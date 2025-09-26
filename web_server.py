#!/usr/bin/env python3
"""
PEMTRON Warpage Analysis Tool - Web Server
Provides web interface for warpage data analysis and visualization
"""

import os
import tempfile
import webbrowser
import threading
import time
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import gc  # For garbage collection

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

def has_data_files_recursive(directory_path, max_depth=2, current_depth=0):
    """
    Recursively check if a directory or its subdirectories contain data files.

    Args:
        directory_path (str): Path to directory to check
        max_depth (int): Maximum depth to recurse (reduced for performance)
        current_depth (int): Current recursion depth

    Returns:
        bool: True if data files are found anywhere in the directory tree
    """
    if current_depth > max_depth:
        return False

    try:
        # Quick check: look for data files in current directory
        if find_data_files(directory_path, True) or find_data_files(directory_path, False):
            return True

        # Check subdirectories
        try:
            for item in os.listdir(directory_path):
                if item.startswith('.'):
                    continue
                item_path = os.path.join(directory_path, item)
                if os.path.isdir(item_path):
                    if has_data_files_recursive(item_path, max_depth, current_depth + 1):
                        return True
        except (OSError, IOError, PermissionError):
            pass

        return False

    except (OSError, IOError, PermissionError):
        return False

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/folders')
def get_folders():
    """Get available data folders - optimized for performance"""
    try:
        data_dir = get_data_dir()

        if not os.path.isabs(data_dir):
            data_dir = os.path.join(os.getcwd(), data_dir)

        folders = []
        if os.path.exists(data_dir):
            try:
                for item in os.listdir(data_dir):
                    if item.startswith('.'):
                        continue
                    item_path = os.path.join(data_dir, item)
                    if os.path.isdir(item_path) and has_data_files_recursive(item_path):
                        folders.append(item)
            except (OSError, IOError, PermissionError) as e:
                return jsonify({'error': f'Could not access data directory: {str(e)}'}), 500

        folders.sort()
        return jsonify({
            'folders': folders,
            'data_directory': data_dir
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
        # Clear previous data to free memory
        current_data = None
        current_plots = None
        current_stats = None
        gc.collect()  # Force garbage collection

        data = request.get_json()
        folder = data.get('folder')
        file_type = data.get('file_type', 'original')
        row_fraction = float(data.get('row_fraction', 1.0))
        col_fraction = float(data.get('col_fraction', 1.0))
        vmin = data.get('vmin')
        vmax = data.get('vmax')

        if not folder:
            return jsonify({'error': 'No folder selected'}), 400

        # Determine use_original based on file_type
        use_original = file_type in ['original', 'original_with_package']

        # Get performance settings from request
        downsample_factor = int(data.get('downsample_factor', 1))
        parallel_processing = data.get('parallel_processing', True)
        fast_plots = data.get('fast_plots', True)

        # Load data with parallel processing and downsampling
        data_dir = get_data_dir()
        if parallel_processing:
            folder_results = process_folder_data_parallel(
                data_dir, folder, row_fraction, col_fraction, use_original, downsample_factor
            )
        else:
            folder_results = process_folder_data(data_dir, folder, row_fraction, col_fraction, use_original, downsample_factor)

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

        if parallel_processing and fast_plots:
            # Use parallel plot generation for maximum speed
            individual_plots = visualization.create_plots_parallel(
                current_data, vmin=vmin, vmax=vmax, cmap=cmap, dpi=dpi
            )
        else:
            # Fallback to sequential processing
            individual_plots = []
            for file_id, (data_array, stats, filename) in current_data.items():
                fig = visualization.create_individual_plot(file_id, data_array, stats, filename,
                                                         vmin=vmin, vmax=vmax, cmap=cmap)
                plot_base64 = visualization.figure_to_base64(fig, dpi=dpi)
                individual_plots.append(plot_base64)

        # Create comparison plot
        comparison_plot = ''
        if len(current_data) > 1:
            comparison_figs = visualization.create_comparison_plot(current_data, vmin=vmin, vmax=vmax, cmap=cmap)
            if comparison_figs:
                comparison_plot = visualization.figure_to_base64(comparison_figs[0], dpi=dpi)

        current_plots = {
            'individual': individual_plots,
            'comparison': comparison_plot
        }

        # Prepare response
        file_list = [filename for _, _, filename in current_data.values()]
        total_data_points = sum(data_array.size for data_array, _, _ in current_data.values() if data_array is not None)

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
                'processing_time_optimized': True
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
        filename = 'warpage_analysis_report.pdf'  # default
        
        if request.method == 'POST':
            # For POST, only try JSON if content type is explicitly set
            try:
                content_type = request.content_type or ''
                if 'application/json' in content_type:
                    data = request.get_json(force=False, silent=True) or {}
                    filename = data.get('filename', filename)
            except Exception:
                pass  # Use default filename
        else:
            # For GET, use query parameters
            filename = request.args.get('filename', filename)
        
        # Create temporary file
        temp_dir = Path(tempfile.gettempdir())
        output_path = temp_dir / filename
        
        # Generate PDF report
        import pdf_exporter
        pdf_path = pdf_exporter.export_to_pdf(
            current_data, 
            str(output_path),
            include_stats=True,
            include_3d=True,
            include_advanced=True
        )
        
        # Return the file for download
        return send_file(pdf_path, as_attachment=True, download_name=filename)
            
    except Exception as e:
        return jsonify({'error': f'PDF export error: {str(e)}'}), 500

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
        plot_base64 = visualization.create_3d_surface_plot(current_data)
        
        return jsonify({
            'success': True,
            'image': plot_base64
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
        
        # Create comprehensive advanced analysis
        plot_base64 = visualization.create_comprehensive_advanced_analysis(current_data)
        
        return jsonify({
            'success': True,
            'plots': [{
                'title': 'Advanced Statistical Analysis',
                'image': plot_base64
            }]
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
            'mean': '',
            'range': '',
            'minmax': '',
            'std': '',
            'distribution': ''
        }

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

        # Generate statistical plots in parallel for maximum speed
        try:
            if current_data and len(current_data) > 1:
                from concurrent.futures import ThreadPoolExecutor, as_completed
                import multiprocessing

                # Ultra-low DPI for maximum speed
                dpi = 80
                max_workers = min(5, multiprocessing.cpu_count())

                def create_stat_plot(plot_type):
                    """Create statistical plots in parallel"""
                    try:
                        if plot_type == 'mean':
                            fig = visualization.create_mean_comparison_plot(current_data)
                        elif plot_type == 'range':
                            fig = visualization.create_range_comparison_plot(current_data)
                        elif plot_type == 'minmax':
                            fig = visualization.create_minmax_comparison_plot(current_data)
                        elif plot_type == 'std':
                            fig = visualization.create_std_comparison_plot(current_data)
                        elif plot_type == 'distribution':
                            fig = visualization.create_warpage_distribution_plot(current_data)
                        else:
                            return None, None
                        return plot_type, visualization.figure_to_base64(fig, dpi=dpi)
                    except Exception:
                        return None, None

                # Generate all statistical plots in parallel
                plot_types = ['mean', 'range', 'minmax', 'std', 'distribution']
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = {executor.submit(create_stat_plot, plot_type): plot_type for plot_type in plot_types}
                    for future in as_completed(futures):
                        plot_type, plot_base64 = future.result()
                        if plot_type and plot_base64:
                            all_plots[plot_type] = plot_base64

        except Exception:
            pass  # Skip failed plots

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
        print(f"✓ Browser opened to http://localhost:{WEB_PORT}")
    except Exception as e:
        print(f"Could not open browser: {e}")
        print(f"Please manually open: http://localhost:{WEB_PORT}")

if __name__ == '__main__':
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
        app.run(host='127.0.0.1', port=WEB_PORT, debug=False, use_reloader=False, threaded=True)
    except KeyboardInterrupt:
        print("\n✓ Server stopped")
    except Exception as e:
        print(f"Server error: {e}")