# pdf_exporter.py - PDF Export Functions
import os
from matplotlib.backends.backend_pdf import PdfPages
from data_loader import process_resolution_data
from statistics_utils import find_optimal_color_range, collect_resolution_statistics, print_statistics_summary
from visualization import create_comparison_plot, create_individual_plot, create_statistics_plots, create_3d_surface_plot

def ensure_report_directory():
    """
    Ensure the report directory exists, create if it doesn't.
    
    Returns:
        str: Path to the report directory
    """
    report_dir = 'report'
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
        print(f"Created report directory: {report_dir}")
    return report_dir

def export_to_pdf(base_path, resolution_folders, output_filename='warpage_analysis_center_region.pdf', 
                  include_stats=True, include_3d=True, dpi=300):
    """
    Export comprehensive warpage analysis to high-resolution PDF in report directory.
    
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
    # Ensure report directory exists
    report_dir = ensure_report_directory()
    full_output_path = os.path.join(report_dir, output_filename)
    
    print(f"Creating high-resolution PDF: {full_output_path}")
    
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
    with PdfPages(full_output_path) as pdf:
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
    
    print(f"PDF created successfully: {full_output_path}")
    print_pdf_summary(full_output_path, resolution_data, include_stats, include_3d)
    
    return full_output_path

def export_single_resolution_pdf(base_path, resolution, output_filename=None, dpi=300):
    """
    Export analysis for a single resolution to PDF in report directory.
    
    Args:
        base_path (str): Base path to data folders
        resolution (str): Resolution folder name
        output_filename (str): Output PDF filename (auto-generated if None)
        dpi (int): DPI for high-resolution output
        
    Returns:
        str: Path to created PDF file
    """
    # Ensure report directory exists
    report_dir = ensure_report_directory()
    
    if output_filename is None:
        output_filename = f'warpage_analysis_{resolution}um.pdf'
    
    full_output_path = os.path.join(report_dir, output_filename)
    
    print(f"Creating PDF for {resolution}μm resolution: {full_output_path}")
    
    # Load data
    center_data, stats, filename = process_resolution_data(base_path, resolution)
    if center_data is None:
        print(f"No data found for resolution {resolution}μm!")
        return None
    
    # Create PDF
    with PdfPages(full_output_path) as pdf:
        # Individual plot
        individual_fig = create_individual_plot(resolution, center_data, stats, filename, 
                                              figsize=(10, 8))
        pdf.savefig(individual_fig, dpi=dpi, bbox_inches='tight')
        individual_fig.clear()
    
    print(f"PDF created successfully: {full_output_path}")
    return full_output_path

def print_pdf_summary(filename, resolution_data, include_stats, include_3d):
    """
    Print a summary of the created PDF.
    
    Args:
        filename (str): PDF filename (full path)
        resolution_data (dict): Resolution data dictionary
        include_stats (bool): Whether stats were included
        include_3d (bool): Whether 3D plots were included
    """
    print("\n" + "="*60)
    print(f"PDF EXPORT SUMMARY: {os.path.basename(filename)}")
    print(f"Location: {filename}")
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