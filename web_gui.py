#!/usr/bin/env python3
"""
Web-based GUI for Warpage Analysis Tool
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

# Import our analysis modules
from config import DATA_DIR, REPORT_DIR, WEB_PORT, WEB_HOST, WEB_DEBUG
from data_loader import process_folder_data, find_data_files
from analyzer import analyze_warpage
from statistics import calculate_statistics
from visualization import create_individual_plot, create_statistical_comparison_plots
from pdf_exporter import export_to_pdf, ensure_report_directory

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.secret_key = 'warpage_analysis_secret_key'

# Global variable to store current analysis results
current_analysis = None

@app.route('/')
def index():
    """Main page with analysis form"""
    return render_template('index.html')

@app.route('/api/folders')
def get_folders():
    """API endpoint to get available data folders"""
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
    """API endpoint to run analysis"""
    global current_analysis
    
    try:
        data = request.get_json()
        folder = data.get('folder')
        use_original = data.get('use_original', True)
        row_fraction = float(data.get('row_fraction', 1.0))
        col_fraction = float(data.get('col_fraction', 1.0))
        
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
        
        # Process the main folder
        print(f"Processing main folder: {folder}")
        main_results = process_folder_data(DATA_DIR, folder, row_fraction, col_fraction, use_original)
        results.extend(main_results)
        total_files_processed += len(main_results)
        print(f"✓ Main folder processed: {len(main_results)} files")
        
        # Process all subdirectories
        subdirs_found = []
        for root, dirs, files in os.walk(folder_path):
            for subdir in dirs:
                subdirs_found.append(subdir)
        
        print(f"Found {len(subdirs_found)} subdirectories to process")
        
        for i, subdir in enumerate(subdirs_found):
            subdir_path = os.path.join(folder_path, subdir)
            rel_path = os.path.relpath(subdir_path, DATA_DIR)
            print(f"Processing subdirectory {i+1}/{len(subdirs_found)}: {subdir}")
            sub_results = process_folder_data(DATA_DIR, rel_path, row_fraction, col_fraction, use_original)
            results.extend(sub_results)
            total_files_processed += len(sub_results)
            print(f"✓ Subdirectory {subdir} processed: {len(sub_results)} files")
        
        print(f"Total files processed: {total_files_processed}")
        
        if not results:
            return jsonify({'error': f'No data files found in {folder}'})
        
        # Create analysis results
        analysis_results = {}
        for i, (data, stats, filename) in enumerate(results):
            file_id = f"File_{i+1:02d}"
            analysis_results[file_id] = {
                'data': data.tolist(),  # Convert numpy array to list for JSON
                'stats': stats,
                'filename': filename,
                'shape': data.shape
            }
        
        current_analysis = {
            'folder': folder,
            'use_original': use_original,
            'row_fraction': row_fraction,
            'col_fraction': col_fraction,
            'results': analysis_results
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
            'analysis_id': id(current_analysis)
        })
        
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'})

@app.route('/api/plot/<file_id>')
def get_plot(file_id):
    """API endpoint to get individual plot as base64 image"""
    global current_analysis
    
    if not current_analysis or file_id not in current_analysis['results']:
        return jsonify({'error': 'No analysis data available'})
    
    try:
        result = current_analysis['results'][file_id]
        data = np.array(result['data'])
        stats = result['stats']
        filename = result['filename']
        
        # Create plot
        fig = create_individual_plot(file_id, data, stats, filename, 
                                   figsize=(8, 6), vmin=None, vmax=None, 
                                   cmap='jet', colorbar=True)
        
        # Convert to base64
        img_buffer = BytesIO()
        fig.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        img_data = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close(fig)
        
        return jsonify({
            'success': True,
            'image': img_data,
            'filename': filename,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({'error': f'Plot generation failed: {str(e)}'})

@app.route('/api/stats_plot')
def get_stats_plot():
    """API endpoint to get statistical comparison plot"""
    global current_analysis
    
    if not current_analysis:
        return jsonify({'error': 'No analysis data available'})
    
    try:
        # Prepare data for statistical plots
        folder_data = {}
        for file_id, result in current_analysis['results'].items():
            data = np.array(result['data'])
            stats = result['stats']
            filename = result['filename']
            folder_data[file_id] = (data, stats, filename)
        
        # Create statistical plot
        fig = create_statistical_comparison_plots(folder_data, figsize=(12, 8))
        
        # Convert to base64
        img_buffer = BytesIO()
        fig.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        img_data = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close(fig)
        
        return jsonify({
            'success': True,
            'image': img_data
        })
        
    except Exception as e:
        return jsonify({'error': f'Statistical plot generation failed: {str(e)}'})

@app.route('/api/export_pdf')
def export_pdf():
    """API endpoint to export PDF report"""
    global current_analysis
    
    if not current_analysis:
        return jsonify({'error': 'No analysis data available'})
    
    try:
        print(f"Starting PDF export for folder: {current_analysis['folder']}")
        print(f"Number of files to process: {len(current_analysis['results'])}")
        
        # Prepare data for PDF export
        folder_data = {}
        print(f"Preparing {len(current_analysis['results'])} files for PDF export...")
        for i, (file_id, result) in enumerate(current_analysis['results'].items()):
            data = np.array(result['data'])
            stats = result['stats']
            filename = result['filename']
            folder_data[file_id] = (data, stats, filename)
            print(f"  Prepared {file_id} ({i+1}/{len(current_analysis['results'])}): {data.shape}, {filename}")
        
        # Export PDF
        pdf_path = export_to_pdf(folder_data, 
                                output_filename=f'warpage_analysis_{current_analysis["folder"].replace("/", "_")}.pdf',
                                include_stats=True, include_3d=False)  # Disable 3D plots for now
        
        print(f"PDF export returned path: {pdf_path}")
        
        if pdf_path and os.path.exists(pdf_path):
            print(f"PDF file exists at: {pdf_path}")
            print(f"PDF file size: {os.path.getsize(pdf_path)} bytes")
            return send_file(pdf_path, as_attachment=True, 
                           download_name=os.path.basename(pdf_path))
        else:
            print(f"PDF file does not exist at: {pdf_path}")
            return jsonify({'error': 'PDF generation failed - file not created'})
        
    except Exception as e:
        import traceback
        print(f"PDF export error: {e}")
        print(f"Full traceback: {traceback.format_exc()}")
        return jsonify({'error': f'PDF export failed: {str(e)}'})



def open_browser():
    """Open the web browser after a short delay to ensure server is ready"""
    time.sleep(2.0)  # Wait longer for server to start
    url = f"http://localhost:{WEB_PORT}"
    try:
        webbrowser.open(url)
        print(f"✓ Browser opened successfully to {url}")
    except Exception as e:
        print(f"⚠ Could not open browser automatically: {e}")
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
            print(f"⚠ Port {WEB_PORT} is already in use!")
            print(f"Please try a different port in config.py or close other applications using port {WEB_PORT}")
        else:
            print(f"⚠ Server error: {e}")
    except Exception as e:
        print(f"⚠ Unexpected error: {e}") 