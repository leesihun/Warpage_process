# main_analysis.py - Resolution Comparison Analysis
"""
Main script for warpage data resolution comparison analysis.
Provides easy-to-use interface for comparing different resolutions.
"""

from data_loader import process_resolution_data
from statistics_utils import find_optimal_color_range
from visualization import create_comparison_plot
from pdf_exporter import export_to_pdf
import matplotlib.pyplot as plt
import os

def get_file_size(file_path):
    """
    Get file size in a human-readable format.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: File size in human-readable format
    """
    if not os.path.exists(file_path):
        return "File not found"
    
    size_bytes = os.path.getsize(file_path)
    
    # Convert to human-readable format
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

def compare_resolution():
    """
    Compare results with respect to different resolutions.
    Displays file sizes and uses consistent scaling.
    """
    base_path = './data/단일보드'
    resolution_folders = ['30', '60', '90', '120']
    
    print("="*80)
    print("RESOLUTION COMPARISON ANALYSIS")
    print("="*80)
    
    # Load all data
    print("\n1. Loading data for all resolutions...")
    resolution_data = {}
    file_info = {}
    
    for resolution in resolution_folders:
        center_data, stats, filename = process_resolution_data(base_path, resolution)
        if center_data is not None:
            resolution_data[resolution] = (center_data, stats, filename)
            
            # Get file information
            file_path = os.path.join(base_path, resolution, filename)
            file_size = get_file_size(file_path)
            file_info[resolution] = {
                'filename': filename,
                'file_size': file_size,
                'data_shape': center_data.shape
            }
            
            print(f"   ✓ {resolution}μm: {filename} ({file_size})")
    
    if not resolution_data:
        print("No data found!")
        return
    
    # Find global color range
    print("\n2. Calculating global color range...")
    data_only = {k: v[0] for k, v in resolution_data.items()}
    vmin, vmax = find_optimal_color_range(data_only)
    print(f"   Global range: {vmin:.6f} to {vmax:.6f}")
    
    # Create comparison visualization
    print("\n3. Creating comparison visualization...")
    comparison_fig = create_comparison_plot(resolution_data, figsize=(20, 5), vmin=vmin, vmax=vmax)
    
    # Display file information table
    print("\n4. File Information Summary:")
    print("="*80)
    print(f"{'Resolution':<12} {'Filename':<30} {'File Size':<12} {'Data Shape':<15}")
    print("-"*80)
    for resolution, info in file_info.items():
        print(f"{resolution}μm{'':<7} {info['filename']:<30} {info['file_size']:<12} {str(info['data_shape']):<15}")
    
    # Display statistical comparison
    print(f"\n5. Statistical Comparison:")
    print("="*80)
    print(f"{'Resolution':<12} {'Mean':<12} {'Std':<12} {'Range':<12} {'Min':<12} {'Max':<12}")
    print("-"*80)
    for resolution, (data, stats, filename) in resolution_data.items():
        print(f"{resolution}μm{'':<7} {stats['mean']:<12.6f} {stats['std']:<12.6f} {stats['range']:<12.6f} {stats['min']:<12.6f} {stats['max']:<12.6f}")
    
    # Export comparison PDF
    print("\n6. Exporting comparison PDF...")
    pdf_filename = export_to_pdf(base_path, resolution_folders, 
                                output_filename='resolution_comparison.pdf',
                                include_stats=False, include_3d=False, dpi=300)
    
    if pdf_filename:
        pdf_size = get_file_size(pdf_filename)
        print(f"   ✓ Comparison PDF: {pdf_filename} ({pdf_size})")
    
    # Visualization created and ready for display
    print("\n7. Visualization created and ready for display...")
    print("   (Use plt.show() to display when ready)")
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE!")
    print("="*80)

if __name__ == "__main__":
    # Run resolution comparison
    compare_resolution() 