#!/usr/bin/env python3
"""
PEMTRON Warpage Analysis Tool - Web Server
Provides web interface for warpage data analysis and visualization
"""

import os
import webbrowser
import threading
import time
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import gc  # For garbage collection
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend to prevent figure accumulation
import matplotlib.pyplot as plt

# Import analysis components
from config import DEFAULT_CONFIG, WEB_PORT, get_data_dir
from data_loader import process_folder_data, process_folder_data_parallel, find_data_files
from warpage_statistics import calculate_statistics
import visualization

app = Flask(__name__, 
           template_folder='templates',
           static_folder='templates/static')
CORS(app)

# Global variables for storing analysis results
current_data = None
current_plots = None
current_stats = None

# Import scanning configuration
from config import SCAN_CONFIG

# Cache for directory scan results - prevents repeated expensive filesystem operations
_directory_cache = {}
_cache_ttl = SCAN_CONFIG['cache_ttl_seconds']

def cleanup_matplotlib_figures():
    """
    Clean up matplotlib figures to prevent memory leaks and warnings.

    This function closes all figures and forces garbage collection to prevent
    the "more than 20 figures have been opened" warning.
    """
    plt.close('all')  # Close all matplotlib figures
    gc.collect()      # Force garbage collection to free memory
    print(f"DEBUG: Cleaned up matplotlib figures. Active figures: {len(plt.get_fignums())}")

def _get_directory_cache_key(directory_path):
    """Generate cache key based on directory path and modification time."""
    try:
        stat = os.stat(directory_path)
        return f"{directory_path}:{stat.st_mtime}"
    except (OSError, IOError):
        return None

def _clear_expired_cache():
    """Clear expired cache entries to prevent memory growth."""
    current_time = time.time()
    expired_keys = [key for key, (result, timestamp) in _directory_cache.items()
                   if current_time - timestamp > _cache_ttl]
    for key in expired_keys:
        del _directory_cache[key]

def has_data_files_optimized(directory_path, max_depth=None):
    """
    Optimized check for data files in directory tree with caching and early exit.

    Performance improvements:
    - Single-pass directory traversal
    - Result caching with TTL
    - Early exit on first data file found
    - Combined file pattern matching

    Args:
        directory_path (str): Path to directory to check
        max_depth (int): Maximum depth to recurse (uses config default if None)

    Returns:
        bool: True if data files are found anywhere in the directory tree
    """
    # Use configured default if not specified
    if max_depth is None:
        max_depth = SCAN_CONFIG['max_scan_depth']

    # Clean expired cache entries periodically
    _clear_expired_cache()

    # Check cache first
    cache_key = _get_directory_cache_key(directory_path)
    if cache_key and cache_key in _directory_cache:
        result, _ = _directory_cache[cache_key]
        return result

    try:
        result = _scan_directory_tree(directory_path, max_depth, 0)

        # Cache the result
        if cache_key:
            _directory_cache[cache_key] = (result, time.time())

        return result
    except (OSError, IOError, PermissionError):
        return False

def _scan_directory_tree(directory_path, max_depth, current_depth):
    """
    Internal recursive function for optimized directory scanning.

    Uses single-pass scanning with combined pattern matching for maximum performance.
    """
    if current_depth > max_depth:
        return False

    try:
        # Single directory listing - much faster than multiple os.listdir calls
        items = os.listdir(directory_path)

        # Define all patterns to check in one pass
        from config import FILE_PATTERNS
        original_patterns = FILE_PATTERNS['original']
        original_pkg_patterns = FILE_PATTERNS.get('original_with_package', [])
        akrometrix_patterns = FILE_PATTERNS.get('akrometrix', [])

        subdirectories = []

        # Single pass through directory contents
        for item in items:
            if item.startswith('.'):
                continue

            # Check for data files (any type) - early exit on first match
            if (any(item.endswith(pattern) for pattern in original_patterns) or
                any(item.endswith(pattern) for pattern in original_pkg_patterns) or
                any(item.endswith(pattern) for pattern in akrometrix_patterns) or
                (item.endswith('.txt') and not any(item.endswith(pattern) for pattern in original_patterns + original_pkg_patterns))):
                return True  # Early exit - found data files

            # Collect subdirectories for recursive checking
            item_path = os.path.join(directory_path, item)
            if os.path.isdir(item_path):
                subdirectories.append(item_path)

        # Only recurse if no data files found in current directory
        for subdir in subdirectories:
            if _scan_directory_tree(subdir, max_depth, current_depth + 1):
                return True  # Early exit on first subdirectory with data

        return False

    except (OSError, IOError, PermissionError):
        return False

# Backward compatibility alias
has_data_files_recursive = has_data_files_optimized

def _scan_directories_parallel(potential_dirs):
    """
    Scan directories in parallel for maximum speed.

    Args:
        potential_dirs (list): List of (item_name, item_path) tuples

    Returns:
        list: List of directory names that contain data files
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import threading

    if not potential_dirs:
        return []

    # Use thread-safe progress tracking
    progress_lock = threading.Lock()
    folders_with_data = []
    processed_count = [0]

    def scan_single_directory(item_tuple):
        """Scan a single directory for data files."""
        item_name, item_path = item_tuple
        try:
            has_data = has_data_files_recursive(item_path)

            # Thread-safe progress update
            with progress_lock:
                processed_count[0] += 1
                status = "HAS DATA" if has_data else "no data"
                print(f"DEBUG: [{processed_count[0]}/{len(potential_dirs)}] {item_name}: {status}")

            return (item_name, has_data)
        except Exception as e:
            with progress_lock:
                processed_count[0] += 1
                print(f"DEBUG: [{processed_count[0]}/{len(potential_dirs)}] {item_name}: ERROR - {e}")
            return (item_name, False)

    # Determine optimal number of threads from config
    max_workers = min(len(potential_dirs), SCAN_CONFIG['max_scan_threads'], 61)
    timeout_per_dir = SCAN_CONFIG['per_directory_timeout']

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all directory scan tasks
        future_to_dir = {executor.submit(scan_single_directory, item_tuple): item_tuple
                        for item_tuple in potential_dirs}

        # Collect results as they complete
        for future in as_completed(future_to_dir):
            try:
                item_name, has_data = future.result(timeout=timeout_per_dir)
                if has_data:
                    folders_with_data.append(item_name)
            except Exception as e:
                item_tuple = future_to_dir[future]
                print(f"DEBUG: Failed to scan {item_tuple[0]}: {e}")

    print(f"DEBUG: Parallel scan used {max_workers} threads for {len(potential_dirs)} directories")
    return sorted(folders_with_data)

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/folders')
def get_folders():
    """Get available data folders - optimized for performance with progress feedback"""
    try:
        data_dir = get_data_dir()
        print(f"DEBUG: Found data directory at: {data_dir}")

        if not os.path.isabs(data_dir):
            data_dir = os.path.join(os.getcwd(), data_dir)

        folders = []
        if os.path.exists(data_dir):
            try:
                # Get list of potential directories first
                all_items = [item for item in os.listdir(data_dir)
                           if not item.startswith('.')]
                potential_dirs = [(item, os.path.join(data_dir, item))
                                for item in all_items
                                if os.path.isdir(os.path.join(data_dir, item))]

                # Apply directory limit from config
                max_dirs = SCAN_CONFIG['max_directories']
                if len(potential_dirs) > max_dirs:
                    print(f"DEBUG: Limiting scan to first {max_dirs} directories (config limit)")
                    potential_dirs = potential_dirs[:max_dirs]

                print(f"DEBUG: Scanning {len(potential_dirs)} directories for data files using parallel processing...")

                # Use parallel scanning for much faster performance
                scan_start_time = time.time()
                folders = _scan_directories_parallel(potential_dirs)
                scan_duration = time.time() - scan_start_time

                print(f"DEBUG: Parallel directory scan completed in {scan_duration:.2f}s. Found {len(folders)} folders with data files.")

            except (OSError, IOError, PermissionError) as e:
                print(f"ERROR: Could not access data directory: {str(e)}")
                return jsonify({'error': f'Could not access data directory: {str(e)}'}), 500

        folders.sort()
        return jsonify({
            'folders': folders,
            'data_directory': data_dir,
            'scan_summary': {
                'total_directories': len(potential_dirs) if 'potential_dirs' in locals() else 0,
                'directories_with_data': len(folders)
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug')
def debug_info():
    """Return minimal diagnostics about server paths."""
    try:
        data_dir = get_data_dir()
        return jsonify({
            'data_directory': data_dir,
            'data_dir_exists': os.path.exists(data_dir),
            'cwd': os.getcwd()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Analyze selected folder - optimized for memory efficiency"""
    global current_data, current_plots, current_stats

    try:
        # Clear previous data and figures to free memory
        current_data = None
        current_plots = None
        current_stats = None
        cleanup_matplotlib_figures()  # Clean up any existing figures

        data = request.get_json()
        folder = data.get('folder')
        file_type = data.get('file_type', 'original')

        # Support both new margin system and legacy row/col fraction system
        # New system: independent margins (left, right, top, bottom)
        margin_left = data.get('margin_left')
        margin_right = data.get('margin_right')
        margin_top = data.get('margin_top')
        margin_bottom = data.get('margin_bottom')

        # Legacy system: centered fractions
        row_fraction = data.get('row_fraction')
        col_fraction = data.get('col_fraction')

        # Determine which system to use and convert if needed
        use_margin_system = any(m is not None for m in [margin_left, margin_right, margin_top, margin_bottom])

        if use_margin_system:
            # New margin system takes precedence
            from data_loader import convert_fraction_to_margins
            margin_left = float(margin_left) if margin_left is not None else 0.0
            margin_right = float(margin_right) if margin_right is not None else 0.0
            margin_top = float(margin_top) if margin_top is not None else 0.0
            margin_bottom = float(margin_bottom) if margin_bottom is not None else 0.0

            # For backward compatibility, also set row_fraction and col_fraction for summary display
            # (These won't be used for processing, but may be needed for display)
            effective_row_fraction = 1.0 - (margin_top + margin_bottom)
            effective_col_fraction = 1.0 - (margin_left + margin_right)
        else:
            # Legacy row/col fraction system - convert to margins
            from data_loader import convert_fraction_to_margins
            row_fraction = float(row_fraction) if row_fraction is not None else 1.0
            col_fraction = float(col_fraction) if col_fraction is not None else 1.0

            margins = convert_fraction_to_margins(row_fraction, col_fraction)
            margin_left = margins['left_margin']
            margin_right = margins['right_margin']
            margin_top = margins['top_margin']
            margin_bottom = margins['bottom_margin']

            effective_row_fraction = row_fraction
            effective_col_fraction = col_fraction

        vmin = data.get('vmin')
        vmax = data.get('vmax')

        if not folder:
            return jsonify({'error': 'No folder selected'}), 400

        # Get performance settings from request
        downsample_factor = int(data.get('downsample_factor', 1))
        parallel_processing = data.get('parallel_processing', True)
        fast_plots = data.get('fast_plots', True)

        # Load data with parallel processing and downsampling using new margin system
        from data_loader import _process_single_file_with_margins, find_data_files
        from concurrent.futures import ProcessPoolExecutor, as_completed
        import multiprocessing

        data_dir = get_data_dir()
        folder_path = os.path.join(data_dir, folder)
        file_paths = find_data_files(folder_path, file_type)

        if not file_paths:
            return jsonify({'error': f'No data files found in folder: {folder}'}), 400

        # Process files with new margin system
        if parallel_processing:
            max_workers = min(len(file_paths), multiprocessing.cpu_count(), 61)
            folder_results = []

            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                future_to_path = {
                    executor.submit(_process_single_file_with_margins, path,
                                  margin_left, margin_right, margin_top, margin_bottom,
                                  downsample_factor): path
                    for path in file_paths
                }

                for future in as_completed(future_to_path):
                    result = future.result()
                    if result is not None:
                        folder_results.append(result)

            # Sort by filename for consistency
            folder_results.sort(key=lambda x: x[2])
        else:
            # Sequential processing
            folder_results = []
            for file_path in file_paths:
                result = _process_single_file_with_margins(
                    file_path, margin_left, margin_right, margin_top, margin_bottom, downsample_factor
                )
                if result is not None:
                    folder_results.append(result)
            folder_results.sort(key=lambda x: x[2])

        if not folder_results:
            return jsonify({'error': f'No data found in folder: {folder}'}), 400

        # Convert to expected format
        current_data = {}
        current_stats = []
        for i, (data_array, stats, filename) in enumerate(folder_results):
            file_id = f"File_{i+1:02d}"
            current_data[file_id] = (data_array, stats, filename)
            current_stats.append(stats)

        # Create plots with maximum speed optimization
        cmap = DEFAULT_CONFIG.get('cmap', 'jet')
        dpi = 100 if fast_plots else 120  # Even lower DPI for maximum speed

        # Use unified landscape figsize for all plots
        landscape_figsize = (11.69, 8.27)  # A4 landscape
        
        if parallel_processing and fast_plots:
            # Use parallel plot generation for maximum speed with unified figsize
            individual_plots = visualization.create_plots_parallel(
                current_data, vmin=vmin, vmax=vmax, cmap=cmap, dpi=dpi, config=DEFAULT_CONFIG,
                figsize=landscape_figsize
            )
        else:
            # Fallback to sequential processing with unified figsize
            individual_plots = []
            for file_id, (data_array, stats, filename) in current_data.items():
                fig = visualization.create_individual_plot(file_id, data_array, stats, filename,
                                                         figsize=landscape_figsize, vmin=vmin, vmax=vmax, cmap=cmap, config=DEFAULT_CONFIG)
                plot_base64 = visualization.figure_to_base64(fig, dpi=dpi)
                individual_plots.append(plot_base64)

        # Create comparison plot with unified figsize
        comparison_plot = ''
        if len(current_data) > 1:
            comparison_figs = visualization.create_comparison_plot(current_data, figsize=landscape_figsize, vmin=vmin, vmax=vmax, cmap=cmap, config=DEFAULT_CONFIG)
            if comparison_figs:
                comparison_plot = visualization.figure_to_base64(comparison_figs[0], dpi=dpi)

        # Create 3D plots if data is available with unified figsize
        three_d_plots = []
        if current_data:
            three_d_plots = visualization.create_3d_surface_plot_web(current_data, figsize=landscape_figsize, config=DEFAULT_CONFIG)

        # Create statistical plots if multiple files are available
        statistical_plots = {}
        if current_data and len(current_data) > 1:
            try:
                # Generate all statistical comparison plots
                stat_plot_functions = {
                    'mean': visualization.create_mean_comparison_plot,
                    'range': visualization.create_range_comparison_plot,
                    'minmax': visualization.create_minmax_comparison_plot,
                    'std': visualization.create_std_comparison_plot,
                    'distribution': visualization.create_warpage_distribution_plot
                }

                for plot_name, plot_function in stat_plot_functions.items():
                    try:
                        fig = plot_function(current_data)
                        statistical_plots[plot_name] = visualization.figure_to_base64(fig, dpi=dpi)
                        print(f"Generated {plot_name} statistical plot")
                    except Exception as e:
                        print(f"Failed to generate {plot_name} plot: {e}")

            except Exception as e:
                print(f"Statistical plots generation failed: {e}")

        # Create advanced statistics if data is available
        advanced_plots = []
        if current_data and len(current_data) > 1:
            try:
                # Import advanced statistics
                from advanced_statistics import create_comprehensive_advanced_analysis

                # Generate advanced analysis plots
                advanced_analysis = create_comprehensive_advanced_analysis(current_data, vmin=vmin, vmax=vmax)
                if advanced_analysis:
                    for fig, title in advanced_analysis:
                        plot_base64 = visualization.figure_to_base64(fig, dpi=dpi)
                        advanced_plots.append({
                            'title': title,
                            'image': plot_base64
                        })
                print(f"Generated {len(advanced_plots)} advanced analysis plots")
            except Exception as e:
                print(f"Advanced analysis generation failed: {e}")

        current_plots = {
            'individual': individual_plots,
            'comparison': comparison_plot,
            '3d': three_d_plots,
            'statistical': statistical_plots,
            'advanced': advanced_plots
        }

        # Clean up any figures created during analysis to prevent memory leaks
        cleanup_matplotlib_figures()

        # Prepare response
        file_list = [filename for _, _, filename in current_data.values()]
        total_data_points = sum(data_array.size for data_array, _, _ in current_data.values() if data_array is not None)

        # Create margin/fraction summary for display
        margin_info = {
            'left_margin': margin_left,
            'right_margin': margin_right,
            'top_margin': margin_top,
            'bottom_margin': margin_bottom,
            'row_fraction': effective_row_fraction,
            'col_fraction': effective_col_fraction,
            'using_margin_system': use_margin_system
        }

        return jsonify({
            'success': True,
            'summary': {
                'folder': folder,
                'file_count': len(current_data),
                'files': file_list,
                'plots_available': list(current_plots.keys()),
                'total_data_points': total_data_points,
                'downsample_factor': downsample_factor,
                'parallel_processing': parallel_processing,
                'processing_time_optimized': True,
                'margins': margin_info
            }
        })

    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/api/plot/<file_id>')
def get_plot(file_id):
    """Get individual plot"""
    global current_plots
    
    try:
        if not current_plots:
            return jsonify({'error': 'No plots available'}), 404
        
        # Handle both integer indices and filename strings
        file_index = None
        
        # Try to parse as integer index first
        try:
            file_index = int(file_id)
        except ValueError:
            # If not an integer, try to find by filename
            if current_data:
                for i, (_, _, filename) in enumerate(current_data.values()):
                    if filename == file_id:
                        file_index = i
                        break
        
        if file_index is None:
            return jsonify({'error': f'File not found: {file_id}'}), 400
            
        try:
            if 'individual' in current_plots and file_index < len(current_plots['individual']):
                plot_base64 = current_plots['individual'][file_index]
                
                # Get file info and stats
                file_keys = list(current_data.keys())
                if file_index < len(file_keys):
                    file_key = file_keys[file_index]
                    _, stats, filename = current_data[file_key]
                    
                    return jsonify({
                        'success': True,
                        'image': plot_base64,
                        'file_index': file_index,
                        'filename': filename,
                        'stats': {
                            'shape': f"{stats['shape'][0]}x{stats['shape'][1]}",
                            'min': stats['min'],
                            'max': stats['max'],
                            'mean': stats['mean'],
                            'range': stats['range']
                        }
                    })
                else:
                    return jsonify({
                        'success': True,
                        'image': plot_base64,
                        'file_index': file_index,
                        'filename': f'File_{file_index+1}',
                        'stats': {'shape': 'Unknown', 'min': 0, 'max': 0, 'mean': 0, 'range': 0}
                    })
        except (IndexError) as e:
            return jsonify({'error': f'Plot not found for index: {file_index}'}), 400
        
        return jsonify({'error': 'Plot not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats_plot')
def get_stats_plot():
    """Get statistical comparison plot"""
    global current_plots
    
    try:
        if not current_plots or 'comparison' not in current_plots:
            return jsonify({'error': 'No comparison plot available'}), 404
        
        return jsonify({
            'success': True,
            'image': current_plots['comparison']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export_pdf', methods=['GET', 'POST'])
def export_pdf_report():
    """Export analysis as PDF"""
    global current_data, current_plots, current_stats
    
    try:
        if not current_data:
            return jsonify({'error': 'No analysis data available'}), 400
        
        # Handle both GET and POST requests - avoid any automatic JSON parsing
        pdf_filename = 'warpage_analysis_report.pdf'  # default

        if request.method == 'POST':
            # For POST, only try JSON if content type is explicitly set
            try:
                content_type = request.content_type or ''
                if 'application/json' in content_type:
                    data = request.get_json(force=False, silent=True) or {}
                    pdf_filename = data.get('filename', pdf_filename)
            except Exception:
                pass  # Use default filename
        else:
            # For GET, use query parameters
            pdf_filename = request.args.get('filename', pdf_filename)

        # Ensure filename has .pdf extension
        if not pdf_filename.endswith('.pdf'):
            pdf_filename += '.pdf'

        # Generate PDF report using web UI plots for consistency
        import pdf_exporter

        # Build comprehensive plots response
        all_plots = {
            'individual': [],
            'comparison': current_plots.get('comparison', ''),
            '3d': current_plots.get('3d', []),
            'advanced': current_plots.get('advanced', [])
        }

        # Add statistical plots for PDF export
        statistical_plots = current_plots.get('statistical', {})
        all_plots.update({
            'mean': statistical_plots.get('mean', ''),
            'range': statistical_plots.get('range', ''),
            'minmax': statistical_plots.get('minmax', ''),
            'std': statistical_plots.get('std', ''),
            'distribution': statistical_plots.get('distribution', '')
        })

        # Add individual plots with file_id information
        if current_plots and 'individual' in current_plots:
            for i, (file_id, (_, _, data_filename)) in enumerate(current_data.items()):
                if i < len(current_plots['individual']):
                    all_plots['individual'].append({
                        'file_id': file_id,
                        'image': current_plots['individual'][i],
                        'filename': data_filename
                    })

        pdf_path = pdf_exporter.export_to_pdf_from_webui_plots(
            all_plots,
            current_data,
            pdf_filename
        )

        # Debug: Print file information
        print(f"DEBUG: Sending PDF file: {pdf_path}")
        print(f"DEBUG: Download name: {pdf_filename}")
        print(f"DEBUG: File exists: {os.path.exists(pdf_path)}")
        if os.path.exists(pdf_path):
            print(f"DEBUG: File size: {os.path.getsize(pdf_path)} bytes")

        # Return the file for download
        return send_file(pdf_path, as_attachment=True, download_name=pdf_filename, mimetype='application/pdf')
            
    except Exception as e:
        return jsonify({'error': f'PDF export error: {str(e)}'}), 500


@app.route('/api/export_stats_json', methods=['GET', 'POST'])
def export_stats_json_route():
    """Export per-file statistics as downloadable JSON"""
    global current_data

    try:
        if not current_data:
            return jsonify({'error': 'No analysis data available'}), 400

        json_filename = 'warpage_analysis_stats.json'

        if request.method == 'POST':
            try:
                content_type = request.content_type or ''
                if 'application/json' in content_type:
                    data = request.get_json(force=False, silent=True) or {}
                    json_filename = data.get('filename', json_filename)
            except Exception:
                pass
        else:
            json_filename = request.args.get('filename', json_filename)

        if not json_filename.endswith('.json'):
            json_filename += '.json'

        import pdf_exporter

        json_path = pdf_exporter.export_statistics_json(current_data, json_filename)
        if not json_path or not os.path.exists(json_path):
            return jsonify({'error': 'Failed to generate statistics JSON'}), 500

        return send_file(
            json_path,
            as_attachment=True,
            download_name=os.path.basename(json_path),
            mimetype='application/json'
        )

    except Exception as e:
        return jsonify({'error': f'Stats JSON export error: {str(e)}'}), 500

@app.route('/api/comparison_plot')
def get_comparison_plot():
    """Get comparison plot - same as stats plot for now"""
    return get_stats_plot()

@app.route('/api/3d_plot')
def get_3d_plot():
    """Get 3D surface plot"""
    global current_data, current_plots
    
    try:
        if not current_data:
            return jsonify({'error': 'No analysis data available'}), 404
        
        # Create 3D surface plot using visualization module
        plot_base64_list = visualization.create_3d_surface_plot_web(current_data, config=DEFAULT_CONFIG)

        return jsonify({
            'success': True,
            'images': plot_base64_list,
            'total_pages': len(plot_base64_list)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mean_plot')
def get_mean_plot():
    """Get mean analysis plot"""
    global current_data
    
    try:
        if not current_data:
            return jsonify({'error': 'No analysis data available'}), 404
        
        # Create mean comparison plot
        plot_base64 = visualization.create_mean_comparison_plot(current_data)
        
        return jsonify({
            'success': True,
            'image': plot_base64
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/range_plot')
def get_range_plot():
    """Get range analysis plot"""
    global current_data
    
    try:
        if not current_data:
            return jsonify({'error': 'No analysis data available'}), 404
        
        # Create range comparison plot
        plot_base64 = visualization.create_range_comparison_plot(current_data)
        
        return jsonify({
            'success': True,
            'image': plot_base64
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/minmax_plot')
def get_minmax_plot():
    """Get min-max analysis plot"""
    global current_data
    
    try:
        if not current_data:
            return jsonify({'error': 'No analysis data available'}), 404
        
        # Create min-max comparison plot
        plot_base64 = visualization.create_minmax_comparison_plot(current_data)
        
        return jsonify({
            'success': True,
            'image': plot_base64
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/std_plot')
def get_std_plot():
    """Get standard deviation analysis plot"""
    global current_data
    
    try:
        if not current_data:
            return jsonify({'error': 'No analysis data available'}), 404
        
        # Create std deviation comparison plot
        plot_base64 = visualization.create_std_comparison_plot(current_data)
        
        return jsonify({
            'success': True,
            'image': plot_base64
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/distribution_plot')
def get_distribution_plot():
    """Get distribution analysis plot"""
    global current_data
    
    try:
        if not current_data:
            return jsonify({'error': 'No analysis data available'}), 404
        
        # Create warpage distribution plot
        plot_base64 = visualization.create_warpage_distribution_plot(current_data)
        
        return jsonify({
            'success': True,
            'image': plot_base64
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/advanced_analysis')
def get_advanced_analysis():
    """Get advanced analysis plots"""
    global current_data

    try:
        if not current_data:
            return jsonify({'error': 'No analysis data available'}), 404

        # Use the advanced statistics module for comprehensive analysis
        from advanced_statistics import create_comprehensive_advanced_analysis
        advanced_analysis = create_comprehensive_advanced_analysis(current_data)

        if advanced_analysis:
            plots = []
            for fig, title in advanced_analysis:
                plot_base64 = visualization.figure_to_base64(fig, dpi=150)
                plots.append({
                    'title': title,
                    'image': plot_base64
                })

            return jsonify({
                'success': True,
                'plots': plots
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No advanced analysis plots generated'
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/all_plots')
def get_all_plots():
    """Get all plots in one response - optimized"""
    global current_data, current_plots, current_stats

    try:
        if not current_data or not current_plots:
            return jsonify({'error': 'No analysis data available'}), 404

        # Build comprehensive plots response
        all_plots = {
            'individual': [],
            'comparison': current_plots.get('comparison', ''),
            'statistics': current_plots.get('comparison', ''),
            '3d': current_plots.get('3d', []),
            'advanced': current_plots.get('advanced', [])
        }

        # Add statistical plots if they were generated during analysis
        statistical_plots = current_plots.get('statistical', {})
        all_plots.update({
            'mean': statistical_plots.get('mean', ''),
            'range': statistical_plots.get('range', ''),
            'minmax': statistical_plots.get('minmax', ''),
            'std': statistical_plots.get('std', ''),
            'distribution': statistical_plots.get('distribution', '')
        })

        # Add individual plots with metadata
        file_keys = list(current_data.keys())
        for i, plot_base64 in enumerate(current_plots.get('individual', [])):
            if i < len(file_keys):
                file_key = file_keys[i]
                _, stats, filename = current_data[file_key]
                all_plots['individual'].append({
                    'file_id': file_key,
                    'filename': filename,
                    'image': plot_base64,
                    'stats': stats
                })

        # Statistical plots are now generated during analysis and cached
        # No need to regenerate them here

        return jsonify({
            'success': True,
            'plots': all_plots
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status')
def get_status():
    """Get server status"""
    global current_data, current_plots
    
    return jsonify({
        'healthy': True,
        'has_data': current_data is not None,
        'has_plots': current_plots is not None,
        'file_count': len(current_data) if current_data else 0
    })

def open_browser():
    """Open browser after server starts"""
    time.sleep(2)  # Wait for server to start
    try:
        webbrowser.open(f'http://localhost:{WEB_PORT}')
        print(f"Browser opened to http://localhost:{WEB_PORT}")
    except Exception as e:
        print(f"Could not open browser: {e}")
        print(f"Please manually open: http://localhost:{WEB_PORT}")

if __name__ == '__main__':
    # Required for multiprocessing in PyInstaller executables
    import multiprocessing
    multiprocessing.freeze_support()

    print("=" * 60)
    print("PEMTRON Warpage Analysis Tool - Web Interface")
    print("=" * 60)
    print()
    print(f"Starting server on http://localhost:{WEB_PORT}")
    print("Press Ctrl+C to stop")
    print()
    
    # Start browser in background
    if DEFAULT_CONFIG.get('auto_open_browser', True):
        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()
    
    try:
        app.run(host='0.0.0.0', port=WEB_PORT, debug=False, use_reloader=False, threaded=True)
    except KeyboardInterrupt:
        print("\nServer stopped")
    except Exception as e:
        print(f"Server error: {e}")
