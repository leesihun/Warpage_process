#!/usr/bin/env python3
"""
Warpage Analyzer용 PDF 내보내기 함수들
PDF export functions for Warpage Analyzer
"""

import os
import base64
import io
from matplotlib.backends.backend_pdf import PdfPages
from config import REPORT_DIR
from visualization import (create_individual_plot, create_3d_surface_plot, create_statistical_comparison_plots,
                          create_mean_comparison_plot, create_range_comparison_plot, 
                          create_minmax_comparison_plot, create_std_comparison_plot,
                          create_warpage_distribution_plot, create_mean_range_combined_plot,
                          create_minmax_std_combined_plot)
from advanced_statistics import create_comprehensive_advanced_analysis, create_legend_page, create_cover_page, create_table_of_contents
from data_loader import get_file_size
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import gc  # For garbage collection


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


def base64_to_figure(base64_string, figsize=(8.27, 11.69)):
    """
    Convert base64 image string to matplotlib figure
    
    Args:
        base64_string (str): Base64 encoded image string
        figsize (tuple): Figure size for the plot
        
    Returns:
        matplotlib.figure.Figure: Figure containing the image
    """
    # Decode base64 string to image data
    img_data = base64.b64decode(base64_string)
    img_buffer = io.BytesIO(img_data)
    
    # Create figure and display image
    fig, ax = plt.subplots(figsize=figsize)
    img = mpimg.imread(img_buffer, format='png')
    ax.imshow(img)
    ax.axis('off')  # Remove axes for clean image display
    
    return fig


def export_to_pdf_from_webui_plots(plots_data, folder_data, output_filename='warpage_analysis.pdf', dpi=150):
    """
    Export PDF using pre-generated plots from web UI for maximum efficiency.
    
    Args:
        plots_data (dict): Pre-generated plots from web UI in base64 format
        folder_data (dict): Original folder data for cover page and metadata
        output_filename (str): Output PDF filename
        dpi (int): DPI for PDF export
        
    Returns:
        str: Path to created PDF file
    """
    # Ensure report directory exists
    report_dir = ensure_report_directory()
    full_output_path = os.path.join(report_dir, output_filename)
    
    print(f"Creating efficient PDF from web UI plots: {full_output_path}")
    
    if not plots_data:
        print("No plot data found to export!")
        return None
    
    # A4 page size in inches with reduced margins
    A4_WIDTH = 8.27
    A4_HEIGHT = 11.69
    MARGIN = 0.5
    
    # Create PDF with A4 page size
    with PdfPages(full_output_path) as pdf:
        
        # Page 1: Cover page
        print("Creating cover page...")
        cover_fig = create_cover_page(folder_data, figsize=(A4_WIDTH-MARGIN, A4_HEIGHT-MARGIN))
        pdf.savefig(cover_fig, dpi=dpi, bbox_inches='tight')
        plt.close(cover_fig)
        
        # Page 2: Table of contents
        print("Creating table of contents...")
        toc_fig = create_table_of_contents(folder_data, include_stats=True, include_3d=False, include_advanced=True, figsize=(A4_WIDTH-MARGIN, A4_HEIGHT-MARGIN))
        pdf.savefig(toc_fig, dpi=dpi, bbox_inches='tight')
        plt.close(toc_fig)
        
        # Page 3: Legend and terminology
        print("Creating legend page...")
        legend_fig = create_legend_page(figsize=(A4_WIDTH-MARGIN, A4_HEIGHT-MARGIN))
        pdf.savefig(legend_fig, dpi=dpi, bbox_inches='tight')
        plt.close(legend_fig)
        
        # Pages 4 onwards: Individual plots (from web UI)
        if 'individual' in plots_data:
            print(f"Adding {len(plots_data['individual'])} individual plots from web UI...")
            for i, plot_info in enumerate(plots_data['individual']):
                print(f"  Adding individual plot {i+1}/{len(plots_data['individual'])}: {plot_info['file_id']}")
                fig = base64_to_figure(plot_info['image'], figsize=(A4_WIDTH-MARGIN, A4_HEIGHT-MARGIN))
                pdf.savefig(fig, dpi=dpi, bbox_inches='tight')
                plt.close(fig)
        
        # Statistical comparison pages (from web UI)
        print("Adding statistical analysis plots from web UI...")
        
        # Add statistical comparison plot
        if 'statistics' in plots_data:
            print("  Adding statistical comparison plot...")
            fig = base64_to_figure(plots_data['statistics'], figsize=(A4_WIDTH-MARGIN, A4_HEIGHT-MARGIN))
            pdf.savefig(fig, dpi=dpi, bbox_inches='tight')
            plt.close(fig)
        
        # Add individual statistical plots
        stat_plots = ['mean', 'range', 'minmax', 'std']
        for stat_name in stat_plots:
            if stat_name in plots_data:
                print(f"  Adding {stat_name} comparison plot...")
                fig = base64_to_figure(plots_data[stat_name], figsize=(A4_WIDTH-MARGIN, A4_HEIGHT-MARGIN))
                pdf.savefig(fig, dpi=dpi, bbox_inches='tight')
                plt.close(fig)
        
        # Add distribution plot
        if 'distribution' in plots_data:
            print("  Adding distribution plot...")
            fig = base64_to_figure(plots_data['distribution'], figsize=(A4_WIDTH-MARGIN, A4_HEIGHT-MARGIN))
            pdf.savefig(fig, dpi=dpi, bbox_inches='tight')
            plt.close(fig)
        
        # Add advanced analysis plots (from web UI)
        if 'advanced' in plots_data:
            print(f"Adding {len(plots_data['advanced'])} advanced analysis plots from web UI...")
            for i, advanced_plot in enumerate(plots_data['advanced']):
                print(f"  Adding advanced plot {i+1}/{len(plots_data['advanced'])}: {advanced_plot['title']}")
                fig = base64_to_figure(advanced_plot['image'], figsize=(A4_WIDTH-MARGIN, A4_HEIGHT-MARGIN))
                pdf.savefig(fig, dpi=dpi, bbox_inches='tight')
                plt.close(fig)
        
        # Add comparison plot (side-by-side heatmaps)
        if 'comparison' in plots_data:
            print("Adding comparison plot...")
            fig = base64_to_figure(plots_data['comparison'], figsize=(A4_WIDTH-MARGIN, A4_HEIGHT-MARGIN))
            pdf.savefig(fig, dpi=dpi, bbox_inches='tight')
            plt.close(fig)
        
        # Add 3D plots if available (though disabled by default)
        if '3d' in plots_data:
            print("Adding 3D surface plots...")
            fig = base64_to_figure(plots_data['3d'], figsize=(A4_WIDTH-MARGIN, A4_HEIGHT-MARGIN))
            pdf.savefig(fig, dpi=dpi, bbox_inches='tight')
            plt.close(fig)
    
    # Final cleanup
    plt.close('all')
    gc.collect()
    
    print(f"Efficient PDF created successfully: {full_output_path}")
    print(f"File size: {os.path.getsize(full_output_path) / (1024*1024):.2f} MB")
    
    return full_output_path


def export_to_pdf(folder_data, output_filename='warpage_analysis.pdf', 
                  include_stats=True, include_3d=True, include_advanced=True, dpi=150, cmap='jet', colorbar=True, vmin=None, vmax=None):
    """
    Export comprehensive warpage analysis to high-resolution PDF in report directory.
    
    Args:
        folder_data (dict): Dictionary with folder as key and (data, stats, filename) as value
        output_filename (str): Output PDF filename
        include_stats (bool): Whether to include statistical analysis plots
        include_3d (bool): Whether to include 3D surface plots
        include_advanced (bool): Whether to include comprehensive advanced statistical analysis
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
    
    print(f"Creating optimized PDF: {full_output_path}")
    
    # Progressive DPI settings for different content types
    dpi_legend = max(100, dpi - 50)     # Lower DPI for legend page
    dpi_individual = dpi                # Standard DPI for main heatmaps
    dpi_stats = max(100, dpi - 50)      # Lower DPI for statistical charts
    dpi_advanced = max(100, dpi - 50)   # Lower DPI for advanced analysis
    dpi_3d = max(100, dpi - 50)         # Lower DPI for 3D plots (memory intensive)
    
    if not folder_data:
        print("No data found to export!")
        return None
    
    # A4 page size in inches with reduced margins for better space utilization
    A4_WIDTH = 8.27
    A4_HEIGHT = 11.69
    MARGIN = 0.5  # Reduced from 1.0 to 0.5 inches
    
    # Create PDF with A4 page size
    with PdfPages(full_output_path) as pdf:
        
        # Page 1: Cover page (표지)
        print("Creating cover page...")
        cover_fig = create_cover_page(folder_data, figsize=(A4_WIDTH-MARGIN, A4_HEIGHT-MARGIN))
        pdf.savefig(cover_fig, dpi=dpi_legend, bbox_inches='tight')
        cover_fig.clear()
        plt.close(cover_fig)
        
        # Page 2: Table of contents (목차)
        print("Creating table of contents...")
        toc_fig = create_table_of_contents(folder_data, include_stats, include_3d, include_advanced, figsize=(A4_WIDTH-MARGIN, A4_HEIGHT-MARGIN))
        pdf.savefig(toc_fig, dpi=dpi_legend, bbox_inches='tight')
        toc_fig.clear()
        plt.close(toc_fig)
        
        # Page 3: Legend and terminology
        print("Creating legend page...")
        legend_fig = create_legend_page(figsize=(A4_WIDTH-MARGIN, A4_HEIGHT-MARGIN))
        pdf.savefig(legend_fig, dpi=dpi_legend, bbox_inches='tight')
        legend_fig.clear()
        plt.close(legend_fig)
        
        # Pages 4 onwards: Individual plots
        print("Creating individual plots...")
        total_files = len(folder_data)
        for i, (file_id, (data, stats, filename)) in enumerate(folder_data.items()):
            print(f"  Creating plot {i+1}/{total_files}: {file_id}")
            # Create figure sized to fit A4 page with margins
            individual_fig = create_individual_plot(file_id, data, stats, filename, 
                                                  figsize=(A4_WIDTH-MARGIN, A4_HEIGHT-MARGIN), vmin=vmin, vmax=vmax, cmap=cmap, colorbar=colorbar)
            pdf.savefig(individual_fig, dpi=dpi_individual, bbox_inches='tight')
            individual_fig.clear()
            plt.close(individual_fig)  # Explicit memory cleanup
        
        # Statistical comparison pages (two plots per page in up-down configuration)
        if include_stats and len(folder_data) > 0:
            print("Creating statistical comparison pages...")
            
            # 1. Mean and Range combined plot
            print("  Creating mean and range combined plot...")
            mean_range_fig = create_mean_range_combined_plot(folder_data, figsize=(A4_WIDTH-MARGIN, A4_HEIGHT-MARGIN))
            pdf.savefig(mean_range_fig, dpi=dpi_stats, bbox_inches='tight')
            mean_range_fig.clear()
            plt.close(mean_range_fig)  # Explicit memory cleanup
            
            # 2. Min-Max and Standard Deviation combined plot
            print("  Creating min-max and standard deviation combined plot...")
            minmax_std_fig = create_minmax_std_combined_plot(folder_data, figsize=(A4_WIDTH-MARGIN, A4_HEIGHT-MARGIN))
            pdf.savefig(minmax_std_fig, dpi=dpi_stats, bbox_inches='tight')
            minmax_std_fig.clear()
            plt.close(minmax_std_fig)  # Explicit memory cleanup
            
            # 3. Warpage distribution plot (Histogram) - Half page size
            print("  Creating warpage distribution plot...")
            half_page_height = (A4_HEIGHT-MARGIN) / 2
            dist_fig = create_warpage_distribution_plot(folder_data, figsize=(A4_WIDTH-MARGIN, half_page_height))
            pdf.savefig(dist_fig, dpi=dpi_stats, bbox_inches='tight')
            dist_fig.clear()
            plt.close(dist_fig)  # Explicit memory cleanup
            
            print("  OK Statistical comparison pages created (3 pages with combined plots)")
        
        # Advanced statistical analysis pages (if requested)
        if include_advanced and len(folder_data) > 0:
            print("Creating comprehensive advanced statistical analysis...")
            advanced_analysis_results = create_comprehensive_advanced_analysis(folder_data, figsize=(A4_WIDTH-MARGIN, A4_HEIGHT-MARGIN), vmin=vmin, vmax=vmax)
            
            total_pages = 0
            for i, result in enumerate(advanced_analysis_results):
                if isinstance(result, list):
                    # Multiple figures returned (e.g., from 2x2 layout functions)
                    for j, fig in enumerate(result):
                        print(f"  Saving advanced analysis page {total_pages+1} (set {i+1}, page {j+1})")
                        pdf.savefig(fig, dpi=dpi_advanced, bbox_inches='tight')
                        plt.close(fig)
                        total_pages += 1
                else:
                    # Single figure returned
                    fig = result
                    print(f"  Saving advanced analysis page {total_pages+1}")
                    pdf.savefig(fig, dpi=dpi_advanced, bbox_inches='tight')
                    plt.close(fig)
                    total_pages += 1
            print(f"  OK Advanced statistical analysis created ({total_pages} pages)")
            
            # Force garbage collection after heavy advanced analysis
            gc.collect()
        
        # Final page: 3D surface plots (if requested)
        if include_3d and len(folder_data) > 0:
            print("Creating 3D surface plots...")
            surface_fig = create_3d_surface_plot(folder_data, figsize=(A4_WIDTH-MARGIN, A4_HEIGHT-MARGIN))
            pdf.savefig(surface_fig, dpi=dpi_3d, bbox_inches='tight')
            surface_fig.clear()
            plt.close(surface_fig)  # Explicit memory cleanup
    
    # Final cleanup
    plt.close('all')
    gc.collect()
    
    print(f"PDF created successfully: {full_output_path}")
    print(f"File size: {os.path.getsize(full_output_path) / (1024*1024):.2f} MB")
    
    return full_output_path 