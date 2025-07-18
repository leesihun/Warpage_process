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

# Import our analysis modules
from config import DATA_DIR, REPORT_DIR, WEB_PORT, WEB_HOST, WEB_DEBUG
from data_loader import process_folder_data, find_data_files
from analyzer import analyze_data
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
        
        # Process folder data
        results = process_folder_data(DATA_DIR, folder, row_fraction, col_fraction, use_original)
        
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
        # Prepare data for PDF export
        folder_data = {}
        for file_id, result in current_analysis['results'].items():
            data = np.array(result['data'])
            stats = result['stats']
            filename = result['filename']
            folder_data[file_id] = (data, stats, filename)
        
        # Export PDF
        pdf_path = export_to_pdf(folder_data, 
                                output_filename=f'warpage_analysis_{current_analysis["folder"]}.pdf',
                                include_stats=True, include_3d=True)
        
        if pdf_path and os.path.exists(pdf_path):
            return send_file(pdf_path, as_attachment=True, 
                           download_name=os.path.basename(pdf_path))
        else:
            return jsonify({'error': 'PDF generation failed'})
        
    except Exception as e:
        return jsonify({'error': f'PDF export failed: {str(e)}'})

@app.route('/api/download_data')
def download_data():
    """API endpoint to download analysis data as JSON"""
    global current_analysis
    
    if not current_analysis:
        return jsonify({'error': 'No analysis data available'})
    
    try:
        # Create JSON data (without the large data arrays)
        export_data = {
            'folder': current_analysis['folder'],
            'use_original': current_analysis['use_original'],
            'row_fraction': current_analysis['row_fraction'],
            'col_fraction': current_analysis['col_fraction'],
            'results': {}
        }
        
        for file_id, result in current_analysis['results'].items():
            export_data['results'][file_id] = {
                'stats': result['stats'],
                'filename': result['filename'],
                'shape': result['shape']
            }
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(export_data, f, indent=2)
            temp_path = f.name
        
        return send_file(temp_path, as_attachment=True, 
                       download_name=f'warpage_analysis_{current_analysis["folder"]}.json')
        
    except Exception as e:
        return jsonify({'error': f'Data export failed: {str(e)}'})

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    print("Starting Warpage Analysis Web GUI...")
    print(f"Open your browser and go to: http://localhost:{WEB_PORT}")
    app.run(debug=WEB_DEBUG, host=WEB_HOST, port=WEB_PORT) 