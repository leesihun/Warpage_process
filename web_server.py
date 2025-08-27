#!/usr/bin/env python3
"""
PEMTRON Warpage Analysis Tool - Web Server
Provides web interface for warpage data analysis and visualization
"""

import os
import json
import tempfile
import webbrowser
import threading
import time
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS

# Import analysis components
from config import DEFAULT_CONFIG
from data_loader import process_folder_data, find_data_files
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

def has_data_files_recursive(directory_path, max_depth=3, current_depth=0):
    """
    Recursively check if a directory or its subdirectories contain data files.
    
    Args:
        directory_path (str): Path to directory to check
        max_depth (int): Maximum depth to recurse (prevent infinite recursion)
        current_depth (int): Current recursion depth
        
    Returns:
        bool: True if data files are found anywhere in the directory tree
    """
    if current_depth > max_depth:
        return False
        
    try:
        # First check the current directory for data files
        if find_data_files(directory_path, True) or find_data_files(directory_path, False):
            return True
            
        # Then check all subdirectories recursively
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            if os.path.isdir(item_path) and not item.startswith('.'):
                if has_data_files_recursive(item_path, max_depth, current_depth + 1):
                    return True
                    
        return False
        
    except (OSError, IOError, PermissionError) as e:
        # Handle permission errors or other file system issues gracefully
        print(f"Warning: Could not access directory {directory_path}: {e}")
        return False

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/folders')
def get_folders():
    """Get available data folders"""
    try:
        config = DEFAULT_CONFIG.copy()
        data_dir = config.get('data_dir', 'data')
        
        # Scan data directory for folders
        folders = []
        if os.path.exists(data_dir):
            for item in os.listdir(data_dir):
                item_path = os.path.join(data_dir, item)
                if os.path.isdir(item_path) and not item.startswith('.'):
                    # Check if folder contains data files (recursively check subdirectories)
                    try:
                        if has_data_files_recursive(item_path):
                            folders.append(item)
                    except Exception as e:
                        # Skip problematic folders but log the issue
                        print(f"Warning: Could not scan folder {item}: {e}")
                        continue
        
        folders.sort()
        return jsonify({
            'folders': folders,
            'data_directory': data_dir
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Analyze selected folder"""
    global current_data, current_plots, current_stats
    
    try:
        data = request.get_json()
        folder = data.get('folder')
        use_original = data.get('use_original', True)
        row_fraction = float(data.get('row_fraction', 1.0))
        col_fraction = float(data.get('col_fraction', 1.0))
        vmin = data.get('vmin')
        vmax = data.get('vmax')
        
        if not folder:
            return jsonify({'error': 'No folder selected'}), 400
        
        # Update config
        config = DEFAULT_CONFIG.copy()
        config['use_original_files'] = use_original
        config['row_fraction'] = row_fraction
        config['col_fraction'] = col_fraction
        if vmin is not None:
            config['vmin'] = vmin
        if vmax is not None:
            config['vmax'] = vmax
        
        # Load data  
        data_dir = config.get('data_dir', 'data')
        folder_results = process_folder_data(data_dir, folder, row_fraction, col_fraction, use_original)
        if not folder_results:
            return jsonify({'error': f'No data found in folder: {folder}'}), 400
        
        # Convert to expected format for other functions
        current_data = {}
        current_stats = []
        for i, (data_array, stats, filename) in enumerate(folder_results):
            file_id = f"File_{i+1:02d}"
            current_data[file_id] = (data_array, stats, filename)
            current_stats.append(stats)
        
        # Create plots
        individual_plots = []
        for file_id, (data_array, stats, filename) in current_data.items():
            fig = visualization.create_individual_plot(file_id, data_array, stats, filename, 
                                               vmin=config.get('vmin'), vmax=config.get('vmax'), 
                                               cmap=config.get('cmap', 'jet'))
            plot_base64 = visualization.figure_to_base64(fig)
            individual_plots.append(plot_base64)
        
        comparison_figs = visualization.create_comparison_plot(current_data, vmin=config.get('vmin'), vmax=config.get('vmax'), cmap=config.get('cmap', 'jet'))
        if comparison_figs and len(comparison_figs) > 0:
            comparison_plot = visualization.figure_to_base64(comparison_figs[0])
        else:
            comparison_plot = ''
        
        current_plots = {
            'individual': individual_plots,
            'comparison': comparison_plot
        }
        
        # Prepare response
        file_list = [filename for _, _, filename in current_data.values()]
        plots_available = list(current_plots.keys()) if current_plots else []
        
        # Calculate total data points
        total_data_points = 0
        for data_array, _, _ in current_data.values():
            if data_array is not None:
                total_data_points += data_array.size
        
        return jsonify({
            'success': True,
            'summary': {
                'folder': folder,
                'file_count': len(current_data),
                'files': file_list,
                'plots_available': plots_available,
                'total_data_points': total_data_points
            }
        })
        
    except Exception as e:
        import traceback
        print(f"Analysis error: {e}")
        traceback.print_exc()
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
    """Get all plots in one response"""
    global current_data, current_plots, current_stats
    
    try:
        if not current_data or not current_plots:
            return jsonify({'error': 'No analysis data available'}), 404
        
        # Build comprehensive plots response
        all_plots = {
            'individual': [],
            'comparison': current_plots.get('comparison', ''),
            '3d': '',
            'statistics': current_plots.get('comparison', ''),  # Use comparison for now
            'mean': '',
            'range': '',
            'minmax': '',
            'std': '',
            'distribution': '',
            'advanced': []
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
        
        # Generate other plot types if needed (with proper base64 conversion)
        try:
            if current_data:
                mean_fig = visualization.create_mean_comparison_plot(current_data)
                all_plots['mean'] = visualization.figure_to_base64(mean_fig)
                
                range_fig = visualization.create_range_comparison_plot(current_data)
                all_plots['range'] = visualization.figure_to_base64(range_fig)
                
                minmax_fig = visualization.create_minmax_comparison_plot(current_data)
                all_plots['minmax'] = visualization.figure_to_base64(minmax_fig)
                
                std_fig = visualization.create_std_comparison_plot(current_data)
                all_plots['std'] = visualization.figure_to_base64(std_fig)
                
                dist_fig = visualization.create_warpage_distribution_plot(current_data)
                all_plots['distribution'] = visualization.figure_to_base64(dist_fig)
        except Exception as e:
            print(f"Warning: Could not generate statistical plots: {e}")
            pass  # Skip if visualization methods don't exist
        
        try:
            if current_data:
                surface_fig = visualization.create_3d_surface_plot(current_data)
                all_plots['3d'] = visualization.figure_to_base64(surface_fig)
        except Exception as e:
            print(f"Warning: Could not generate 3D plot: {e}")
            pass  # Skip if 3D method doesn't exist
        
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
        webbrowser.open('http://localhost:8080')
        print("✓ Browser opened to http://localhost:8080")
    except Exception as e:
        print(f"Could not open browser: {e}")
        print("Please manually open: http://localhost:8080")

if __name__ == '__main__':
    print("=" * 60)
    print("PEMTRON Warpage Analysis Tool - Web Interface")
    print("=" * 60)
    print()
    print("Starting server on http://localhost:8080")
    print("Press Ctrl+C to stop")
    print()
    
    # Start browser in background
    if DEFAULT_CONFIG.get('auto_open_browser', True):
        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()
    
    try:
        app.run(host='0.0.0.0', port=8080, debug=True, use_reloader=False)
    except KeyboardInterrupt:
        print("\n✓ Server stopped")
    except Exception as e:
        print(f"Server error: {e}")