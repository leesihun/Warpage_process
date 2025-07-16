# main_analysis.py - Main Analysis Script
"""
Main script for warpage data analysis.
Demonstrates usage of all modules and provides easy-to-use interface.
"""

from data_loader import process_resolution_data, load_data_from_file, extract_center_region
from statistics_utils import collect_resolution_statistics, print_statistics_summary
from visualization import create_comparison_plot, create_individual_plot, create_statistics_plots, create_3d_surface_plot
from pdf_exporter import export_to_pdf, export_single_resolution_pdf
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

def main():
    """
    Main function demonstrating comprehensive warpage analysis.
    """
    # Configuration
    base_path = './data/단일보드'
    resolution_folders = ['30', '60', '90', '120']
    
    print("="*80)
    print("WARPAGE DATA ANALYSIS - COMPREHENSIVE REPORT")
    print("="*80)
    
    # 1. Load and process all data
    print("\n1. Loading and processing data...")
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
            
            print(f"   ✓ {resolution}μm resolution loaded successfully")
            print(f"     File: {filename}")
            print(f"     Size: {file_size}")
            print(f"     Data shape: {center_data.shape}")
        else:
            print(f"   ✗ {resolution}μm resolution failed to load")
    
    if not resolution_data:
        print("No data found! Please check your data paths.")
        return
    
    # 2. Find optimal color range for consistent scaling
    print("\n2. Calculating optimal color range for consistent scaling...")
    from statistics_utils import find_optimal_color_range
    data_only = {k: v[0] for k, v in resolution_data.items()}
    vmin, vmax = find_optimal_color_range(data_only)
    print(f"   Global color range: {vmin:.6f} to {vmax:.6f}")
    
    # 3. Create visualizations (store figures, don't show yet)
    print("\n3. Creating visualizations...")
    figures = []
    
    # Comparison plot
    print("   Creating comparison plot...")
    comparison_fig = create_comparison_plot(resolution_data, figsize=(20, 5), vmin=vmin, vmax=vmax)
    figures.append(("Comparison Plot", comparison_fig))
    
    # Individual plots
    print("   Creating individual plots...")
    for resolution, (data, stats, filename) in resolution_data.items():
        individual_fig = create_individual_plot(resolution, data, stats, filename, 
                                              figsize=(10, 8), vmin=vmin, vmax=vmax)
        figures.append((f"Individual Plot - {resolution}μm", individual_fig))
    
    # 4. Export to PDF
    print("\n4. Exporting to PDF...")
    pdf_filename = export_to_pdf(base_path, resolution_folders, 
                                output_filename='warpage_analysis_complete.pdf',
                                include_stats=False, include_3d=False, dpi=300)
    
    if pdf_filename:
        pdf_size = get_file_size(pdf_filename)
        print(f"   ✓ Complete analysis exported to: {pdf_filename}")
        print(f"   ✓ PDF size: {pdf_size}")
    
    # 5. Export individual PDFs (optional)
    print("\n5. Exporting individual resolution PDFs...")
    for resolution in resolution_data.keys():
        individual_pdf = export_single_resolution_pdf(base_path, resolution, dpi=300)
        if individual_pdf:
            individual_pdf_size = get_file_size(individual_pdf)
            print(f"   ✓ {resolution}μm analysis exported to: {individual_pdf}")
            print(f"     PDF size: {individual_pdf_size}")
    
    # 6. Display file information summary
    print("\n6. File Information Summary:")
    print("="*60)
    for resolution, info in file_info.items():
        print(f"{resolution}μm Resolution:")
        print(f"  File: {info['filename']}")
        print(f"  Size: {info['file_size']}")
        print(f"  Data Shape: {info['data_shape']}")
        print()
    
    # 7. Display all figures at the end
    print("\n7. Displaying visualizations...")
    for title, fig in figures:
        print(f"   Showing: {title}")
        plt.figure(fig.number)
        plt.show()
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE!")
    print("="*80)

def quick_analysis(resolution):
    """
    Quick analysis for a single resolution.
    
    Args:
        resolution (str): Resolution folder name (e.g., '30', '60', '90', '120')
    """
    base_path = './data/단일보드'
    
    print(f"Quick analysis for {resolution}μm resolution...")
    
    # Load data
    center_data, stats, filename = process_resolution_data(base_path, resolution)
    
    if center_data is None:
        print(f"No data found for {resolution}μm resolution!")
        return
    
    # Get file information
    file_path = os.path.join(base_path, resolution, filename)
    file_size = get_file_size(file_path)
    
    # Print statistics
    print(f"\nFile Information for {resolution}μm resolution:")
    print(f"  File: {filename}")
    print(f"  Size: {file_size}")
    print(f"  Data shape: {center_data.shape}")
    print(f"  Min: {stats['min']:.6f}")
    print(f"  Max: {stats['max']:.6f}")
    print(f"  Mean: {stats['mean']:.6f}")
    print(f"  Std: {stats['std']:.6f}")
    print(f"  Range: {stats['range']:.6f}")
    
    # Create plot (don't show yet)
    fig = create_individual_plot(resolution, center_data, stats, filename, figsize=(10, 8))
    
    # Export to PDF
    pdf_filename = export_single_resolution_pdf(base_path, resolution)
    if pdf_filename:
        pdf_size = get_file_size(pdf_filename)
        print(f"Analysis exported to: {pdf_filename}")
        print(f"PDF size: {pdf_size}")
    
    # Show plot at the end
    print(f"\nDisplaying plot for {resolution}μm resolution...")
    plt.show()

def compare_resolutions(resolution1, resolution2):
    """
    Compare two specific resolutions.
    
    Args:
        resolution1 (str): First resolution to compare
        resolution2 (str): Second resolution to compare
    """
    base_path = './data/단일보드'
    
    print(f"Comparing {resolution1}μm vs {resolution2}μm resolutions...")
    
    # Load data for both resolutions
    resolution_data = {}
    file_info = {}
    
    for res in [resolution1, resolution2]:
        center_data, stats, filename = process_resolution_data(base_path, res)
        if center_data is not None:
            resolution_data[res] = (center_data, stats, filename)
            
            # Get file information
            file_path = os.path.join(base_path, res, filename)
            file_size = get_file_size(file_path)
            file_info[res] = {
                'filename': filename,
                'file_size': file_size,
                'data_shape': center_data.shape
            }
    
    if len(resolution_data) != 2:
        print("Could not load data for both resolutions!")
        return
    
    # Find optimal color range for consistent scaling
    from statistics_utils import find_optimal_color_range
    data_only = {k: v[0] for k, v in resolution_data.items()}
    vmin, vmax = find_optimal_color_range(data_only)
    
    print(f"Global color range: {vmin:.6f} to {vmax:.6f}")
    
    # Create comparison plot (don't show yet)
    comparison_fig = create_comparison_plot(resolution_data, figsize=(12, 5), vmin=vmin, vmax=vmax)
    
    # Print file information
    print(f"\nFile Information Comparison:")
    print("="*50)
    for res, info in file_info.items():
        print(f"{res}μm Resolution:")
        print(f"  File: {info['filename']}")
        print(f"  Size: {info['file_size']}")
        print(f"  Data Shape: {info['data_shape']}")
        print()
    
    # Print comparison statistics
    print(f"Statistical Comparison:")
    print("="*50)
    for res, (data, stats, filename) in resolution_data.items():
        print(f"{res}μm Resolution:")
        print(f"  Mean: {stats['mean']:.6f}")
        print(f"  Std: {stats['std']:.6f}")
        print(f"  Range: {stats['range']:.6f}")
        print()
    
    # Calculate differences
    res1_stats = resolution_data[resolution1][1]
    res2_stats = resolution_data[resolution2][1]
    
    print(f"Differences ({resolution1}μm - {resolution2}μm):")
    print(f"  Mean difference: {res1_stats['mean'] - res2_stats['mean']:.6f}")
    print(f"  Std difference: {res1_stats['std'] - res2_stats['std']:.6f}")
    print(f"  Range difference: {res1_stats['range'] - res2_stats['range']:.6f}")
    
    # Show plot at the end
    print(f"\nDisplaying comparison plot...")
    plt.show()

def routine_resolution_comparison():
    """
    Routine for comparing results with respect to different resolutions.
    Displays file sizes and uses consistent scaling.
    """
    base_path = './data/단일보드'
    resolution_folders = ['30', '60', '90', '120']
    
    print("="*80)
    print("ROUTINE: RESOLUTION COMPARISON ANALYSIS")
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
    from statistics_utils import find_optimal_color_range
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
                                output_filename='routine_resolution_comparison.pdf',
                                include_stats=False, include_3d=False, dpi=300)
    
    if pdf_filename:
        pdf_size = get_file_size(pdf_filename)
        print(f"   ✓ Comparison PDF: {pdf_filename} ({pdf_size})")
    
    # Display visualization at the end
    print("\n7. Displaying comparison visualization...")
    plt.show()
    
    print("\n" + "="*80)
    print("ROUTINE COMPLETE!")
    print("="*80)

if __name__ == "__main__":
    # Run routine resolution comparison
    routine_resolution_comparison()
    
    # Uncomment below for other analyses:
    # main()
    # quick_analysis('30')
    # compare_resolutions('30', '120') 