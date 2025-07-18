#!/usr/bin/env python3
"""
PDF export functions for Warpage Analyzer
"""

import os
from matplotlib.backends.backend_pdf import PdfPages
from config import REPORT_DIR
from visualization import (create_individual_plot, create_3d_surface_plot, create_statistical_comparison_plots,
                          create_mean_comparison_plot, create_range_comparison_plot, 
                          create_minmax_comparison_plot, create_std_comparison_plot,
                          create_warpage_distribution_plot, create_mean_range_combined_plot,
                          create_minmax_std_combined_plot)
from data_loader import get_file_size
import matplotlib.pyplot as plt


def ensure_report_directory():
    """
    Ensure the report directory exists, create if it doesn't.
    
    Returns:
        str: Path to the report directory
    """
    report_dir = REPORT_DIR
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
        print(f"Created report directory: {report_dir}")
    return report_dir


def export_to_pdf(folder_data, output_filename='warpage_analysis.pdf', 
                  include_stats=True, include_3d=True, dpi=600, cmap='jet', colorbar=True, vmin=None, vmax=None):
    """
    Export comprehensive warpage analysis to high-resolution PDF in report directory.
    
    Args:
        folder_data (dict): Dictionary with folder as key and (data, stats, filename) as value
        output_filename (str): Output PDF filename
        include_stats (bool): Whether to include statistical analysis plots
        include_3d (bool): Whether to include 3D surface plots
        dpi (int): DPI for high-resolution output
        cmap (str): Colormap name
        colorbar (bool): Whether to show colorbar
        vmin (float, optional): Minimum value for color scale
        vmax (float, optional): Maximum value for color scale
        
    Returns:
        str: Path to created PDF file
    """
    # Ensure report directory exists
    report_dir = ensure_report_directory()
    full_output_path = os.path.join(report_dir, output_filename)
    
    print(f"Creating high-resolution PDF: {full_output_path}")
    
    if not folder_data:
        print("No data found to export!")
        return None
    
    # A4 page size in inches (8.27 x 11.69 inches)
    A4_WIDTH = 8.27
    A4_HEIGHT = 11.69
    
    # Create PDF with A4 page size
    with PdfPages(full_output_path) as pdf:
        
        # Pages 1-N: Individual plots
        print("Creating individual plots...")
        total_files = len(folder_data)
        for i, (file_id, (data, stats, filename)) in enumerate(folder_data.items()):
            print(f"  Creating plot {i+1}/{total_files}: {file_id}")
            # Create figure sized to fit A4 page with margins
            individual_fig = create_individual_plot(file_id, data, stats, filename, 
                                                  figsize=(A4_WIDTH-1, A4_HEIGHT-1), vmin=vmin, vmax=vmax, cmap=cmap, colorbar=colorbar)
            pdf.savefig(individual_fig, dpi=dpi, bbox_inches='tight')
            individual_fig.clear()
        
        # Statistical comparison pages (two plots per page in up-down configuration)
        if include_stats and len(folder_data) > 0:
            print("Creating statistical comparison pages...")
            
            # 1. Mean and Range combined plot
            print("  Creating mean and range combined plot...")
            mean_range_fig = create_mean_range_combined_plot(folder_data, figsize=(A4_WIDTH-1, A4_HEIGHT-1))
            pdf.savefig(mean_range_fig, dpi=dpi, bbox_inches='tight')
            mean_range_fig.clear()
            
            # 2. Min-Max and Standard Deviation combined plot
            print("  Creating min-max and standard deviation combined plot...")
            minmax_std_fig = create_minmax_std_combined_plot(folder_data, figsize=(A4_WIDTH-1, A4_HEIGHT-1))
            pdf.savefig(minmax_std_fig, dpi=dpi, bbox_inches='tight')
            minmax_std_fig.clear()
            
            # 3. Warpage distribution plot (Histogram)
            print("  Creating warpage distribution plot...")
            dist_fig = create_warpage_distribution_plot(folder_data, figsize=(A4_WIDTH-1, A4_HEIGHT-1))
            pdf.savefig(dist_fig, dpi=dpi, bbox_inches='tight')
            dist_fig.clear()
            
            print("  ✓ Statistical comparison pages created (3 pages with combined plots)")
        
        # Final page: 3D surface plots (if requested)
        if include_3d and len(folder_data) > 0:
            print("Creating 3D surface plots...")
            surface_fig = create_3d_surface_plot(folder_data, figsize=(A4_WIDTH-1, A4_HEIGHT-1))
            pdf.savefig(surface_fig, dpi=dpi, bbox_inches='tight')
            surface_fig.clear()
    
    print(f"PDF created successfully: {full_output_path}")
    print(f"File size: {os.path.getsize(full_output_path) / (1024*1024):.2f} MB")
    
    return full_output_path 