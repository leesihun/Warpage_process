#!/usr/bin/env python3
"""
Warpage Analysis Tool용 웹 기반 서버
Web-based server for Warpage Analysis Tool
"""

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import os
import json
import tempfile
from werkzeug.utils import secure_filename
import zipfile
import io
import base64
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import webbrowser
import threading
import time

# 분석 모듈들 가져오기 / Import our analysis modules
from config import DATA_DIR, REPORT_DIR, WEB_PORT, WEB_HOST, WEB_DEBUG
from data_loader import process_folder_data
from warpage_statistics import calculate_statistics
from visualization import (create_individual_plot, create_statistical_comparison_plots,
                          create_mean_range_combined_plot, create_minmax_std_combined_plot,
                          create_warpage_distribution_plot, create_web_gui_statistical_plots,
                          create_comparison_plot, create_3d_surface_plot, create_mean_comparison_plot,
                          create_range_comparison_plot, create_minmax_comparison_plot, create_std_comparison_plot,
                          create_comprehensive_advanced_analysis)
from advanced_statistics import create_comprehensive_advanced_analysis
from pdf_exporter import export_to_pdf, export_to_pdf_from_webui_plots, ensure_report_directory

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1000 * 1024 * 1024  # 1GB max file size
app.secret_key = 'warpage_analysis_secret_key'

# 현재 분석 결과를 저장하는 전역 변수 / Global variable to store current analysis results
current_analysis = None

def figure_to_base64(fig, dpi=150):
    """Convert matplotlib figure to base64 string"""
    img_buffer = BytesIO()
    fig.savefig(img_buffer, format='png', dpi=dpi, bbox_inches='tight')
    img_buffer.seek(0)
    img_data = base64.b64encode(img_buffer.getvalue()).decode()
    plt.close(fig)
    return img_data

def generate_all_plots(folder_data, vmin=None, vmax=None):
    """Generate all plots and return as base64 images"""
    plots = {}
    
    print("Generating all plots in background...")
    print(f"  Using color scale: vmin={vmin}, vmax={vmax}")
    
    # 1. Individual plots
    print("  Generating individual plots...")
    individual_plots = []
    for file_id, (data, stats, filename) in folder_data.items():
        fig = create_individual_plot(file_id, data, stats, filename, 
                                   figsize=(8, 6), vmin=vmin, vmax=vmax, 
                                   cmap='jet', colorbar=True)
        img_data = figure_to_base64(fig)
        individual_plots.append({
            'file_id': file_id,
            'filename': filename,
            'image': img_data,
            'stats': stats
        })
    plots['individual'] = individual_plots
    
    # 2. Comparison plot
    print("  Generating comparison plot...")
    fig = create_comparison_plot(folder_data, figsize=(20, 5), vmin=vmin, vmax=vmax)
    plots['comparison'] = figure_to_base64(fig)
    
    # 3. 3D surface plots
    print("  Generating 3D surface plots...")
    fig = create_3d_surface_plot(folder_data, figsize=(20, 15))
    plots['3d'] = figure_to_base64(fig)
    
    # 4. Statistical analysis
    print("  Generating statistical analysis...")
    fig = create_web_gui_statistical_plots(folder_data, figsize=(12, 16))
    plots['statistics'] = figure_to_base64(fig)
    
    # 5. Individual statistical plots
    print("  Generating individual statistical plots...")
    fig = create_mean_comparison_plot(folder_data, figsize=(10, 6))
    plots['mean'] = figure_to_base64(fig)
    
    fig = create_range_comparison_plot(folder_data, figsize=(10, 6))
    plots['range'] = figure_to_base64(fig)
    
    fig = create_minmax_comparison_plot(folder_data, figsize=(10, 6))
    plots['minmax'] = figure_to_base64(fig)
    
    fig = create_std_comparison_plot(folder_data, figsize=(10, 6))
    plots['std'] = figure_to_base64(fig)
    
    # 6. Distribution plot
    print("  Generating distribution plot...")
    fig = create_warpage_distribution_plot(folder_data, figsize=(10, 8))
    plots['distribution'] = figure_to_base64(fig)
    
    # 7. Advanced analysis plots
    print("  Generating advanced analysis plots...")
    advanced_figs = create_comprehensive_advanced_analysis(folder_data, figsize=(12, 16))
    advanced_plots = []
    for i, fig in enumerate(advanced_figs):
        img_data = figure_to_base64(fig)
        advanced_plots.append({
            'title': f'Advanced Analysis - Page {i+1}',
            'image': img_data
        })
    plots['advanced'] = advanced_plots
    
    print(f"  Generated {len(advanced_plots)} advanced analysis plots")
    print("All plots generated successfully!")
    
    return plots

@app.route('/')
def index():
    """분석 폼이 있는 메인 페이지 / Main page with analysis form"""
    return render_template('index.html')

@app.route('/api/folders')
def get_folders():
    """사용 가능한 데이터 폴더들을 가져오는 API 엔드포인트 / API endpoint to get available data folders"""
    try:
        if not os.path.exists(DATA_DIR):
            return jsonify({'folders': [], 'error': 'Data directory not found'})
        
        # Only show top-level folders
        folders = [d for d in os.listdir(DATA_DIR) 
                  if os.path.isdir(os.path.join(DATA_DIR, d))]
        folders.sort()
        return jsonify({'folders': folders})
    except Exception as e:
        return jsonify({'folders': [], 'error': str(e)})

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """분석을 실행하는 API 엔드포인트 / API endpoint to run analysis"""
    global current_analysis
    
    try:
        data = request.get_json()
        folder = data.get('folder')
        use_original = data.get('use_original', True)
        row_fraction = float(data.get('row_fraction', 1.0))
        col_fraction = float(data.get('col_fraction', 1.0))
        vmin = data.get('vmin')
        vmax = data.get('vmax')
        
        if not folder:
            return jsonify({'error': 'No folder selected'})
        
        # Run analysis
        folder_path = os.path.join(DATA_DIR, folder)
        if not os.path.exists(folder_path):
            return jsonify({'error': f'Folder {folder} not found'})
        
        print(f"Starting analysis of folder: {folder}")
        
        # Process folder data and all subdirectories
        results = []
        total_files_processed = 0
        status_messages = []
        
        # Process the main folder
        status_msg = f"Processing main folder: {folder}"
        print(status_msg)
        status_messages.append(status_msg)
        
        main_results = process_folder_data(DATA_DIR, folder, row_fraction, col_fraction, use_original)
        results.extend(main_results)
        total_files_processed += len(main_results)
        
        status_msg = f"OK Main folder processed: {len(main_results)} files"
        print(status_msg)
        status_messages.append(status_msg)
        
        # Process all subdirectories
        subdirs_found = []
        for root, dirs, files in os.walk(folder_path):
            for subdir in dirs:
                subdirs_found.append(subdir)
        
        status_msg = f"Found {len(subdirs_found)} subdirectories to process"
        print(status_msg)
        status_messages.append(status_msg)
        
        for i, subdir in enumerate(subdirs_found):
            subdir_path = os.path.join(folder_path, subdir)
            rel_path = os.path.relpath(subdir_path, DATA_DIR)
            
            status_msg = f"Processing subdirectory {i+1}/{len(subdirs_found)}: {subdir}"
            print(status_msg)
            status_messages.append(status_msg)
            
            sub_results = process_folder_data(DATA_DIR, rel_path, row_fraction, col_fraction, use_original)
            results.extend(sub_results)
            total_files_processed += len(sub_results)
            
            status_msg = f"OK Subdirectory {subdir} processed: {len(sub_results)} files"
            print(status_msg)
            status_messages.append(status_msg)
        
        status_msg = f"Total files processed: {total_files_processed}"
        print(status_msg)
        status_messages.append(status_msg)
        
        if not results:
            return jsonify({'error': f'No data files found in {folder}'})
        
        # Create analysis results
        status_msg = "Creating analysis results..."
        print(status_msg)
        status_messages.append(status_msg)
        
        analysis_results = {}
        for i, (data, stats, filename) in enumerate(results):
            file_id = f"File_{i+1:02d}"
            analysis_results[file_id] = {
                'data': data.tolist(),  # Convert numpy array to list for JSON
                'stats': stats,
                'filename': filename,
                'shape': data.shape
            }
            
            status_msg = f"  Prepared {file_id}: {filename} ({data.shape})"
            print(status_msg)
            status_messages.append(status_msg)
        
        # Generate all plots in background
        status_msg = "Generating all visualization plots..."
        print(status_msg)
        status_messages.append(status_msg)
        
        folder_data = {}
        for file_id, result in analysis_results.items():
            data = np.array(result['data'])
            stats = result['stats']
            filename = result['filename']
            folder_data[file_id] = (data, stats, filename)
        
        all_plots = generate_all_plots(folder_data, vmin, vmax)
        
        current_analysis = {
            'folder': folder,
            'use_original': use_original,
            'row_fraction': row_fraction,
            'col_fraction': col_fraction,
            'vmin': vmin,
            'vmax': vmax,
            'results': analysis_results,
            'plots': all_plots
        }
        
        # Prepare summary for response
        summary = {
            'folder': folder,
            'file_count': len(analysis_results),
            'files': list(analysis_results.keys()),
            'total_data_points': sum(stats['shape'][0] * stats['shape'][1] 
                                   for stats in analysis_results.values())
        }
        
        return jsonify({
            'success': True,
            'summary': summary,
            'analysis_id': id(current_analysis),
            'status_messages': status_messages
        })
        
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'})

@app.route('/api/all_plots')
def get_all_plots():
    """API endpoint to get all plots at once"""
    global current_analysis
    
    if not current_analysis or 'plots' not in current_analysis:
        return jsonify({'error': 'No analysis data available'})
    
    try:
        return jsonify({
            'success': True,
            'plots': current_analysis['plots'],
            'summary': {
                'folder': current_analysis['folder'],
                'file_count': len(current_analysis['results']),
                'files': list(current_analysis['results'].keys())
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get plots: {str(e)}'})

@app.route('/api/plot/<file_id>')
def get_plot(file_id):
    """API endpoint to get individual plot as base64 image"""
    global current_analysis
    
    if not current_analysis or 'plots' not in current_analysis:
        return jsonify({'error': 'No analysis data available'})
    
    try:
        # Find the individual plot (already generated with vmin/vmax in generate_all_plots)
        individual_plots = current_analysis['plots']['individual']
        for plot in individual_plots:
            if plot['file_id'] == file_id:
                return jsonify({
                    'success': True,
                    'image': plot['image'],
                    'filename': plot['filename'],
                    'stats': plot['stats']
                })
        
        return jsonify({'error': f'Plot for {file_id} not found'})
        
    except Exception as e:
        return jsonify({'error': f'Plot retrieval failed: {str(e)}'})

@app.route('/api/stats_plot')
def get_stats_plot():
    """API endpoint to get statistical comparison plot"""
    global current_analysis
    
    if not current_analysis or 'plots' not in current_analysis:
        return jsonify({'error': 'No analysis data available'})
    
    try:
        return jsonify({
            'success': True,
            'image': current_analysis['plots']['statistics']
        })
        
    except Exception as e:
        return jsonify({'error': f'Statistical plot retrieval failed: {str(e)}'})

@app.route('/api/comparison_plot')
def get_comparison_plot():
    """API endpoint to get side-by-side comparison plot"""
    global current_analysis
    
    if not current_analysis or 'plots' not in current_analysis:
        return jsonify({'error': 'No analysis data available'})
    
    try:
        return jsonify({
            'success': True,
            'image': current_analysis['plots']['comparison']
        })
        
    except Exception as e:
        return jsonify({'error': f'Comparison plot retrieval failed: {str(e)}'})

@app.route('/api/3d_plot')
def get_3d_plot():
    """API endpoint to get 3D surface plots"""
    global current_analysis
    
    if not current_analysis or 'plots' not in current_analysis:
        return jsonify({'error': 'No analysis data available'})
    
    try:
        return jsonify({
            'success': True,
            'image': current_analysis['plots']['3d']
        })
        
    except Exception as e:
        return jsonify({'error': f'3D plot retrieval failed: {str(e)}'})

@app.route('/api/mean_plot')
def get_mean_plot():
    """API endpoint to get mean comparison plot"""
    global current_analysis
    
    if not current_analysis or 'plots' not in current_analysis:
        return jsonify({'error': 'No analysis data available'})
    
    try:
        return jsonify({
            'success': True,
            'image': current_analysis['plots']['mean']
        })
        
    except Exception as e:
        return jsonify({'error': f'Mean plot retrieval failed: {str(e)}'})

@app.route('/api/range_plot')
def get_range_plot():
    """API endpoint to get range comparison plot"""
    global current_analysis
    
    if not current_analysis or 'plots' not in current_analysis:
        return jsonify({'error': 'No analysis data available'})
    
    try:
        return jsonify({
            'success': True,
            'image': current_analysis['plots']['range']
        })
        
    except Exception as e:
        return jsonify({'error': f'Range plot retrieval failed: {str(e)}'})

@app.route('/api/minmax_plot')
def get_minmax_plot():
    """API endpoint to get min-max comparison plot"""
    global current_analysis
    
    if not current_analysis or 'plots' not in current_analysis:
        return jsonify({'error': 'No analysis data available'})
    
    try:
        return jsonify({
            'success': True,
            'image': current_analysis['plots']['minmax']
        })
        
    except Exception as e:
        return jsonify({'error': f'Min-Max plot retrieval failed: {str(e)}'})

@app.route('/api/std_plot')
def get_std_plot():
    """API endpoint to get standard deviation comparison plot"""
    global current_analysis
    
    if not current_analysis or 'plots' not in current_analysis:
        return jsonify({'error': 'No analysis data available'})
    
    try:
        return jsonify({
            'success': True,
            'image': current_analysis['plots']['std']
        })
        
    except Exception as e:
        return jsonify({'error': f'Std plot retrieval failed: {str(e)}'})

@app.route('/api/distribution_plot')
def get_distribution_plot():
    """API endpoint to get warpage distribution plot"""
    global current_analysis
    
    if not current_analysis or 'plots' not in current_analysis:
        return jsonify({'error': 'No analysis data available'})
    
    try:
        return jsonify({
            'success': True,
            'image': current_analysis['plots']['distribution']
        })
        
    except Exception as e:
        return jsonify({'error': f'Distribution plot retrieval failed: {str(e)}'})

@app.route('/api/advanced_analysis')
def get_advanced_analysis():
    """API endpoint to get advanced analysis plots"""
    global current_analysis
    
    if not current_analysis or 'plots' not in current_analysis:
        return jsonify({'error': 'No analysis data available'})
    
    try:
        return jsonify({
            'success': True,
            'plots': current_analysis['plots']['advanced']
        })
        
    except Exception as e:
        return jsonify({'error': f'Advanced analysis retrieval failed: {str(e)}'})

@app.route('/api/export_pdf')
def export_pdf():
    """API endpoint to export PDF report"""
    global current_analysis
    
    if not current_analysis:
        return jsonify({'error': 'No analysis data available'})
    
    try:
        status_messages = []
        
        status_msg = f"Starting PDF export for folder: {current_analysis['folder']}"
        print(status_msg)
        status_messages.append(status_msg)
        
        status_msg = f"Number of files to process: {len(current_analysis['results'])}"
        print(status_msg)
        status_messages.append(status_msg)
        
        # Use the efficient PDF export method with pre-generated plots
        status_msg = "Creating efficient PDF report from web UI plots..."
        print(status_msg)
        status_messages.append(status_msg)
        
        # Prepare folder_data for cover page and metadata (only basic structure needed)
        folder_data = {}
        for file_id, result in current_analysis['results'].items():
            data = np.array(result['data'])
            stats = result['stats']
            filename = result['filename']
            folder_data[file_id] = (data, stats, filename)
        
        # Export PDF using pre-generated plots from web UI
        pdf_path = export_to_pdf_from_webui_plots(
            plots_data=current_analysis['plots'],
            folder_data=folder_data,
            output_filename=f'warpage_analysis_{current_analysis["folder"].replace("/", "_")}.pdf'
        )
        
        status_msg = f"PDF export returned path: {pdf_path}"
        print(status_msg)
        status_messages.append(status_msg)
        
        if pdf_path and os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            status_msg = f"PDF file exists at: {pdf_path}"
            print(status_msg)
            status_messages.append(status_msg)
            
            status_msg = f"PDF file size: {file_size} bytes"
            print(status_msg)
            status_messages.append(status_msg)
            
            status_msg = "PDF export completed successfully!"
            print(status_msg)
            status_messages.append(status_msg)
            
            return send_file(pdf_path, as_attachment=True, 
                           download_name=os.path.basename(pdf_path))
        else:
            status_msg = f"PDF file does not exist at: {pdf_path}"
            print(status_msg)
            status_messages.append(status_msg)
            return jsonify({'error': 'PDF generation failed - file not created'})
        
    except Exception as e:
        import traceback
        error_msg = f"PDF export error: {e}"
        print(error_msg)
        print(f"Full traceback: {traceback.format_exc()}")
        return jsonify({'error': f'PDF export failed: {str(e)}'})



def open_browser():
    """Open the web browser after a short delay to ensure server is ready"""
    time.sleep(2.0)  # Wait longer for server to start
    url = f"http://localhost:{WEB_PORT}"
    try:
        webbrowser.open(url)
        print(f"OK Browser opened successfully to {url}")
    except Exception as e:
        print(f"WARNING Could not open browser automatically: {e}")
        print(f"Please manually open: {url}")

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    print("Starting Warpage Analysis Web GUI...")
    print(f"Server will start on: http://localhost:{WEB_PORT}")
    
    # Start browser in a separate thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        app.run(debug=WEB_DEBUG, host=WEB_HOST, port=WEB_PORT)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"WARNING Port {WEB_PORT} is already in use!")
            print(f"Please try a different port in config.py or close other applications using port {WEB_PORT}")
        else:
            print(f"WARNING Server error: {e}")
    except Exception as e:
        print(f"WARNING Unexpected error: {e}") 