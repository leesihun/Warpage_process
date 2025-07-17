# main_analysis.py - Resolution Comparison Analysis
"""
Main script for warpage data resolution comparison analysis.
Provides easy-to-use interface for comparing different resolutions.
"""

from data_loader import process_resolution_data
from statistics_utils import find_optimal_color_range
from visualization import create_comparison_plot
from pdf_exporter import export_to_pdf
from presets import get_preset, list_presets, update_visualization_settings
import matplotlib.pyplot as plt
import os
import sys

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

def compare_resolution(preset_name="resolution_comparison", vmin=None, vmax=None, cmap=None, colorbar=None):
    """
    Compare results with respect to different resolutions.
    
    Args:
        preset_name (str): Name of the analysis preset to use
        vmin (float, optional): Minimum value for color scale. Overrides preset if provided.
        vmax (float, optional): Maximum value for color scale. Overrides preset if provided.
        cmap (str, optional): Colormap name. Overrides preset if provided.
        colorbar (bool, optional): Whether to show colorbar. Overrides preset if provided.
    """
    # Get preset settings
    try:
        preset = get_preset(preset_name)
        
        # Update visualization settings if parameters are provided
        update_visualization_settings(preset_name, vmin, vmax, cmap, colorbar)
        
        # Extract settings from preset
        vis_settings = preset["visualization"]
        vmin = vis_settings["vmin"]
        vmax = vis_settings["vmax"]
        cmap = vis_settings["cmap"]
        colorbar = vis_settings["colorbar"]
        
        # Get analysis settings
        base_path = preset.get("base_path", "./data/단일보드")
        resolution_folders = preset.get("folders", ["30", "60", "90", "120"])
    except ValueError as e:
        print(f"Error: {e}")
        list_presets()
        return
    
    print("="*80)
    print(f"{preset['name']} ANALYSIS")
    print("="*80)
    print(f"Description: {preset['description']}")
    
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
    auto_vmin, auto_vmax = find_optimal_color_range(data_only)
    print(f"   Auto-calculated range: {auto_vmin:.6f} to {auto_vmax:.6f}")
    
    # Use user-specified values if provided
    if vmin is None:
        vmin = auto_vmin
    if vmax is None:
        vmax = auto_vmax
    
    print(f"   Using range: {vmin:.6f} to {vmax:.6f}")
    if vmin != auto_vmin or vmax != auto_vmax:
        print(f"   (User-specified min/max values applied)")
    
    print(f"   Using colormap: {cmap}")
    print(f"   Colorbar: {'enabled' if colorbar else 'disabled'}")
    
    # Create comparison visualization
    print("\n3. Creating comparison visualization...")
    comparison_fig = create_comparison_plot(resolution_data, figsize=(20, 5), vmin=vmin, vmax=vmax, cmap=cmap, colorbar=colorbar)
    
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
    output_filename = f"{preset_name.lower()}_analysis.pdf"
    pdf_filename = export_to_pdf(base_path, resolution_folders, 
                                output_filename=output_filename,
                                include_stats=False, include_3d=False, dpi=300, cmap=cmap, colorbar=colorbar, vmin=vmin, vmax=vmax)
    
    if pdf_filename:
        pdf_size = get_file_size(pdf_filename)
        print(f"   ✓ Analysis PDF: {pdf_filename} ({pdf_size})")
    
    # Visualization created and ready for display
    print("\n7. Visualization created and ready for display...")
    print("   (Use plt.show() to display when ready)")
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE!")
    print("="*80)
    
    return comparison_fig

def main():
    """
    Main function to handle command line arguments and run the analysis.
    """
    # Show presets if no arguments or help requested
    if len(sys.argv) == 1 or sys.argv[1] in ['-h', '--help']:
        print("\nWarpage Analysis Tool")
        print("Usage: python main_analysis.py [preset_name] [options]")
        print("\nOptions:")
        print("  -h, --help     Show this help message")
        print("  --vmin=VALUE   Set minimum value for color scale")
        print("  --vmax=VALUE   Set maximum value for color scale")
        print("  --cmap=NAME    Set colormap name")
        print("  --colorbar     Enable colorbar")
        print("  --no-colorbar  Disable colorbar")
        print("  --show         Show plots after analysis")
        list_presets()
        return
    
    # Parse arguments
    preset_name = "resolution_comparison"
    vmin = None
    vmax = None
    cmap = None
    colorbar = None
    show_plots = False
    
    for arg in sys.argv[1:]:
        if arg.startswith('--vmin='):
            try:
                vmin = float(arg.split('=')[1])
            except (IndexError, ValueError):
                print("Error: Invalid vmin value")
                return
        elif arg.startswith('--vmax='):
            try:
                vmax = float(arg.split('=')[1])
            except (IndexError, ValueError):
                print("Error: Invalid vmax value")
                return
        elif arg.startswith('--cmap='):
            try:
                cmap = arg.split('=')[1]
            except IndexError:
                print("Error: Invalid cmap value")
                return
        elif arg == '--colorbar':
            colorbar = True
        elif arg == '--no-colorbar':
            colorbar = False
        elif arg == '--show':
            show_plots = True
        elif not arg.startswith('-'):
            preset_name = arg
    
    # Run analysis
    fig = compare_resolution(preset_name, vmin, vmax, cmap, colorbar)
    
    # Show plots if requested
    if show_plots and fig is not None:
        plt.show()

if __name__ == "__main__":
    main() 