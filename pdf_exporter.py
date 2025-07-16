# pdf_exporter.py - PDF Export Functions
import os
from matplotlib.backends.backend_pdf import PdfPages
from data_loader import process_resolution_data
from statistics_utils import find_optimal_color_range, collect_resolution_statistics, print_statistics_summary
from visualization import create_comparison_plot, create_individual_plot, create_statistics_plots, create_3d_surface_plot

def export_to_pdf(base_path, resolution_folders, output_filename='warpage_analysis_center_region.pdf', 
                  include_stats=True, include_3d=True, dpi=300):
    """
    Export comprehensive warpage analysis to high-resolution PDF.
    
    Args:
        base_path (str): Base path to data folders
        resolution_folders (list): List of resolution folder names
        output_filename (str): Output PDF filename
        include_stats (bool): Whether to include statistical analysis plots
        include_3d (bool): Whether to include 3D surface plots
        dpi (int): DPI for high-resolution output
        
    Returns:
        str: Path to created PDF file
    """
    print(f"Creating high-resolution PDF: {output_filename}")
    
    # Load all data
    resolution_data = {}
    for resolution in resolution_folders:
        center_data, stats, filename = process_resolution_data(base_path, resolution)
        if center_data is not None:
            resolution_data[resolution] = (center_data, stats, filename)
    
    if not resolution_data:
        print("No data found to export!")
        return None
    
    # Find optimal color range
    data_only = {k: v[0] for k, v in resolution_data.items()}
    vmin, vmax = find_optimal_color_range(data_only)
    
    # Create PDF
    with PdfPages(output_filename) as pdf:
        # Page 1: Comparison plot
        print("Creating comparison plot...")
        comparison_fig = create_comparison_plot(resolution_data, figsize=(20, 5), vmin=vmin, vmax=vmax)
        pdf.savefig(comparison_fig, dpi=dpi, bbox_inches='tight')
        comparison_fig.clear()
        
        # Pages 2-5: Individual plots
        print("Creating individual plots...")
        for resolution, (data, stats, filename) in resolution_data.items():
            individual_fig = create_individual_plot(resolution, data, stats, filename, 
                                                  figsize=(10, 8), vmin=vmin, vmax=vmax)
            pdf.savefig(individual_fig, dpi=dpi, bbox_inches='tight')
            individual_fig.clear()
        
        # Page 6: Statistical analysis (if requested)
        if include_stats and len(resolution_data) > 1:
            print("Creating statistical analysis plots...")
            resolutions, stats_data = collect_resolution_statistics(base_path, resolution_folders)
            if resolutions:
                stats_fig = create_statistics_plots(resolutions, stats_data, figsize=(15, 10))
                pdf.savefig(stats_fig, dpi=dpi, bbox_inches='tight')
                stats_fig.clear()
        
        # Page 7: 3D surface plots (if requested)
        if include_3d and len(resolution_data) > 1:
            print("Creating 3D surface plots...")
            surface_fig = create_3d_surface_plot(resolution_data, figsize=(20, 15))
            pdf.savefig(surface_fig, dpi=dpi, bbox_inches='tight')
            surface_fig.clear()
    
    print(f"PDF created successfully: {output_filename}")
    print_pdf_summary(output_filename, resolution_data, include_stats, include_3d)
    
    return output_filename

def export_single_resolution_pdf(base_path, resolution, output_filename=None, dpi=300):
    """
    Export analysis for a single resolution to PDF.
    
    Args:
        base_path (str): Base path to data folders
        resolution (str): Resolution folder name
        output_filename (str): Output PDF filename (auto-generated if None)
        dpi (int): DPI for high-resolution output
        
    Returns:
        str: Path to created PDF file
    """
    if output_filename is None:
        output_filename = f'warpage_analysis_{resolution}um.pdf'
    
    print(f"Creating PDF for {resolution}μm resolution: {output_filename}")
    
    # Load data
    center_data, stats, filename = process_resolution_data(base_path, resolution)
    if center_data is None:
        print(f"No data found for resolution {resolution}μm!")
        return None
    
    # Create PDF
    with PdfPages(output_filename) as pdf:
        # Individual plot
        individual_fig = create_individual_plot(resolution, center_data, stats, filename, 
                                              figsize=(10, 8))
        pdf.savefig(individual_fig, dpi=dpi, bbox_inches='tight')
        individual_fig.clear()
    
    print(f"PDF created successfully: {output_filename}")
    return output_filename

def print_pdf_summary(filename, resolution_data, include_stats, include_3d):
    """
    Print a summary of the created PDF.
    
    Args:
        filename (str): PDF filename
        resolution_data (dict): Resolution data dictionary
        include_stats (bool): Whether stats were included
        include_3d (bool): Whether 3D plots were included
    """
    print("\n" + "="*60)
    print(f"PDF EXPORT SUMMARY: {filename}")
    print("="*60)
    
    page_count = 1
    print(f"Page {page_count}: Comparison plot (all resolutions)")
    page_count += 1
    
    for resolution in resolution_data.keys():
        print(f"Page {page_count}: Individual plot - {resolution}μm resolution")
        page_count += 1
    
    if include_stats and len(resolution_data) > 1:
        print(f"Page {page_count}: Statistical analysis plots")
        page_count += 1
    
    if include_3d and len(resolution_data) > 1:
        print(f"Page {page_count}: 3D surface plots")
        page_count += 1
    
    print(f"\nTotal pages: {page_count - 1}")
    print(f"Resolutions included: {', '.join([f'{r}μm' for r in resolution_data.keys()])}")
    print(f"File size: {os.path.getsize(filename) / (1024*1024):.2f} MB")
    print("="*60) 