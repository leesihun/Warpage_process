#!/usr/bin/env python3
"""
Warpage Analyzer - A simple tool for analyzing warpage data across different resolutions

This single file contains all the necessary functionality for warpage data analysis:
- Loading and processing data from files
- Statistical analysis
- Visualization with configurable parameters
- PDF export capabilities
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from mpl_toolkits.mplot3d import Axes3D

# -----------------------------------------------------------------------------
# Configuration - Modify these settings as needed
# -----------------------------------------------------------------------------

# Default settings
DEFAULT_CONFIG = {
    "base_path": "./data/단일보드",        # Base path to data folders
    "resolutions": ["30", "60", "90", "120"],  # Resolution folders to analyze
    "vmin": None,                          # Min value for color scale (None = auto)
    "vmax": None,                          # Max value for color scale (None = auto)
    "cmap": "jet",                         # Colormap (jet, viridis, plasma, etc.)
    "colorbar": True,                      # Whether to show colorbar
    "row_fraction": 0.4,                   # Fraction of rows to keep in center
    "col_fraction": 0.5,                   # Fraction of columns to keep in center
    "output_filename": "warpage_analysis.pdf",  # Output PDF filename
    "include_stats": True,                 # Include statistical analysis plots
    "include_3d": False,                   # Include 3D surface plots
    "dpi": 300,                            # DPI for PDF export
    "show_plots": False                    # Show plots after analysis
}

# -----------------------------------------------------------------------------
# Data Loading Functions
# -----------------------------------------------------------------------------

def load_data_from_file(file_path):
    """
    Load raw data from a text file.
    
    Args:
        file_path (str): Path to the data file
        
    Returns:
        numpy.ndarray: Raw data array, or None if error
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = f.read()
        
        # Convert to numpy array
        data_lines = data.strip().split('\n')
        data_array = np.array([list(map(float, line.split())) for line in data_lines])
        
        return data_array
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def extract_center_region(data_array, row_fraction=0.4, col_fraction=0.5):
    """
    Extract center region from data array.
    
    Args:
        data_array (numpy.ndarray): Input data array
        row_fraction (float): Fraction of rows to keep in center
        col_fraction (float): Fraction of columns to keep in center
        
    Returns:
        numpy.ndarray: Center region data
    """
    n_rows, n_cols = data_array.shape
    
    # Calculate center region boundaries
    row_margin = (1 - row_fraction) / 2
    col_margin = (1 - col_fraction) / 2
    
    row_start = int(n_rows * row_margin)
    row_end = int(n_rows * (1 - row_margin))
    col_start = int(n_cols * col_margin)
    col_end = int(n_cols * (1 - col_margin))
    
    # Extract center region
    center_data = data_array[row_start:row_end, col_start:col_end]
    
    return center_data

def find_ori_file(folder_path):
    """
    Find the ORI file in a given folder.
    
    Args:
        folder_path (str): Path to the folder
        
    Returns:
        str: Full path to the ORI file, or None if not found
    """
    try:
        files = os.listdir(folder_path)
        ori_files = [f for f in files if f.endswith('@_ORI.txt')]
        if ori_files:
            return os.path.join(folder_path, ori_files[0])
        else:
            print(f"No ORI file found in {folder_path}")
            return None
    except Exception as e:
        print(f"Error accessing folder {folder_path}: {e}")
        return None

def process_resolution_data(base_path, resolution, row_fraction=0.4, col_fraction=0.5):
    """
    Process data for a single resolution.
    
    Args:
        base_path (str): Base path to data folders
        resolution (str): Resolution folder name
        row_fraction (float): Fraction of rows to keep in center
        col_fraction (float): Fraction of columns to keep in center
        
    Returns:
        tuple: (center_data, stats, ori_filename) or (None, None, None) if error
    """
    folder_path = os.path.join(base_path, resolution)
    file_path = find_ori_file(folder_path)
    
    if file_path is None:
        return None, None, None
    
    # Load raw data
    raw_data = load_data_from_file(file_path)
    if raw_data is None:
        return None, None, None
    
    # Extract center region
    center_data = extract_center_region(raw_data, row_fraction, col_fraction)
    
    # Calculate statistics
    stats = calculate_statistics(center_data)
    
    # Get filename for display
    ori_filename = os.path.basename(file_path)
    
    return center_data, stats, ori_filename

# -----------------------------------------------------------------------------
# Statistical Analysis Functions
# -----------------------------------------------------------------------------

def calculate_statistics(data_array):
    """
    Calculate comprehensive statistics for data array.
    
    Args:
        data_array (numpy.ndarray): Input data array
        
    Returns:
        dict: Dictionary containing statistical measures
    """
    return {
        'min': np.min(data_array),
        'max': np.max(data_array),
        'mean': np.mean(data_array),
        'std': np.std(data_array),
        'shape': data_array.shape,
        'range': np.max(data_array) - np.min(data_array)
    }

def find_optimal_color_range(resolution_data):
    """
    Find optimal color range for consistent visualization across resolutions.
    
    Args:
        resolution_data (dict): Dictionary with resolution as key and data as value
        
    Returns:
        tuple: (vmin, vmax) for color scaling
    """
    all_mins = []
    all_maxs = []
    
    for data in resolution_data.values():
        if data is not None:
            all_mins.append(np.min(data))
            all_maxs.append(np.max(data))
    
    if all_mins and all_maxs:
        return min(all_mins), max(all_maxs)
    else:
        return 0, 1  # Default range

# -----------------------------------------------------------------------------
# Visualization Functions
# -----------------------------------------------------------------------------

def create_comparison_plot(resolution_data, figsize=(20, 5), vmin=None, vmax=None, cmap='jet', colorbar=True):
    """
    Create a comparison plot showing all resolutions side by side with consistent scaling.
    
    Args:
        resolution_data (dict): Dictionary with resolution as key and (data, stats, filename) as value
        figsize (tuple): Figure size (width, height)
        vmin, vmax (float): Color scale limits
        cmap (str): Colormap name
        colorbar (bool): Whether to show colorbar
        
    Returns:
        matplotlib.figure.Figure: The created figure
    """
    fig, axes = plt.subplots(1, len(resolution_data), figsize=figsize)
    fig.suptitle('Warpage Data Comparison - Center Region Only', fontsize=16, fontweight='bold')
    
    if len(resolution_data) == 1:
        axes = [axes]
    
    # Find consistent axis limits for all subplots
    all_shapes = [data[0].shape for data in resolution_data.values() if data[0] is not None]
    if all_shapes:
        max_rows = max(shape[0] for shape in all_shapes)
        max_cols = max(shape[1] for shape in all_shapes)
    else:
        max_rows, max_cols = 100, 100  # Default fallback
    
    for i, (resolution, (data, stats, filename)) in enumerate(resolution_data.items()):
        if data is not None:
            im = axes[i].imshow(data, cmap=cmap, vmin=vmin, vmax=vmax)
            axes[i].set_title(f'{resolution}μm Resolution\n{filename}', fontweight='bold')
            axes[i].set_aspect('equal')
            
            # Set consistent axis limits
            axes[i].set_xlim(0, max_cols)
            axes[i].set_ylim(max_rows, 0)  # Inverted y-axis for image display
            
            # Remove tick labels for cleaner look
            axes[i].set_xticks([])
            axes[i].set_yticks([])
            
            # Add statistics text
            stats_text = f"Min: {stats['min']:.4f}\nMax: {stats['max']:.4f}\nMean: {stats['mean']:.4f}"
            axes[i].text(0.02, 0.98, stats_text, transform=axes[i].transAxes, 
                        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Add colorbar if requested (only one for the entire figure)
    if colorbar and len(resolution_data) > 0:
        fig.colorbar(im, ax=axes, shrink=0.6, label='Warpage Value')
    
    plt.tight_layout()
    return fig

def create_individual_plot(resolution, data, stats, filename, figsize=(8, 6), vmin=None, vmax=None, cmap='jet', colorbar=True):
    """
    Create an individual plot for a single resolution with consistent scaling.
    
    Args:
        resolution (str): Resolution value
        data (numpy.ndarray): Data array
        stats (dict): Statistics dictionary
        filename (str): Filename for title
        figsize (tuple): Figure size
        vmin, vmax (float): Color scale limits
        cmap (str): Colormap name
        colorbar (bool): Whether to show colorbar
        
    Returns:
        matplotlib.figure.Figure: The created figure
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    im = ax.imshow(data, cmap=cmap, vmin=vmin, vmax=vmax)
    ax.set_title(f'{resolution}μm Resolution - Center Region\n{filename}', fontweight='bold', fontsize=14)
    ax.set_aspect('equal')
    
    # Set consistent axis scaling
    ax.set_xlim(0, data.shape[1])
    ax.set_ylim(data.shape[0], 0)  # Inverted y-axis for image display
    
    # Remove tick labels for cleaner look
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Add statistics text
    stats_text = f"Shape: {stats['shape']}\nMin: {stats['min']:.6f}\nMax: {stats['max']:.6f}\nMean: {stats['mean']:.6f}\nStd: {stats['std']:.6f}"
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
    
    # Add colorbar if requested
    if colorbar:
        cbar = fig.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label('Warpage Value', fontsize=12)
    
    plt.tight_layout()
    return fig

# -----------------------------------------------------------------------------
# PDF Export Functions
# -----------------------------------------------------------------------------

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

def export_to_pdf(resolution_data, output_filename='warpage_analysis.pdf', 
                  include_stats=True, include_3d=False, dpi=300, cmap='jet', colorbar=True, vmin=None, vmax=None):
    """
    Export comprehensive warpage analysis to high-resolution PDF in report directory.
    
    Args:
        resolution_data (dict): Dictionary with resolution as key and (data, stats, filename) as value
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
    
    if not resolution_data:
        print("No data found to export!")
        return None
    
    # Create PDF
    with PdfPages(full_output_path) as pdf:
        # Page 1: Comparison plot
        print("Creating comparison plot...")
        comparison_fig = create_comparison_plot(resolution_data, figsize=(20, 5), vmin=vmin, vmax=vmax, cmap=cmap, colorbar=colorbar)
        pdf.savefig(comparison_fig, dpi=dpi, bbox_inches='tight')
        comparison_fig.clear()
        
        # Pages 2-5: Individual plots
        print("Creating individual plots...")
        for resolution, (data, stats, filename) in resolution_data.items():
            individual_fig = create_individual_plot(resolution, data, stats, filename, 
                                                  figsize=(10, 8), vmin=vmin, vmax=vmax, cmap=cmap, colorbar=colorbar)
            pdf.savefig(individual_fig, dpi=dpi, bbox_inches='tight')
            individual_fig.clear()
    
    print(f"PDF created successfully: {full_output_path}")
    print(f"File size: {os.path.getsize(full_output_path) / (1024*1024):.2f} MB")
    
    return full_output_path

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

# -----------------------------------------------------------------------------
# Main Analysis Function
# -----------------------------------------------------------------------------

def analyze_warpage(config=None):
    """
    Main function to analyze warpage data with configurable parameters.
    
    Args:
        config (dict, optional): Configuration dictionary with analysis parameters
        
    Returns:
        tuple: (comparison_fig, resolution_data) - The comparison figure and processed data
    """
    # Use default config if none provided
    if config is None:
        config = DEFAULT_CONFIG.copy()
    
    # Extract configuration parameters
    base_path = config.get('base_path', DEFAULT_CONFIG['base_path'])
    resolutions = config.get('resolutions', DEFAULT_CONFIG['resolutions'])
    vmin = config.get('vmin', DEFAULT_CONFIG['vmin'])
    vmax = config.get('vmax', DEFAULT_CONFIG['vmax'])
    cmap = config.get('cmap', DEFAULT_CONFIG['cmap'])
    colorbar = config.get('colorbar', DEFAULT_CONFIG['colorbar'])
    row_fraction = config.get('row_fraction', DEFAULT_CONFIG['row_fraction'])
    col_fraction = config.get('col_fraction', DEFAULT_CONFIG['col_fraction'])
    output_filename = config.get('output_filename', DEFAULT_CONFIG['output_filename'])
    include_stats = config.get('include_stats', DEFAULT_CONFIG['include_stats'])
    include_3d = config.get('include_3d', DEFAULT_CONFIG['include_3d'])
    dpi = config.get('dpi', DEFAULT_CONFIG['dpi'])
    show_plots = config.get('show_plots', DEFAULT_CONFIG['show_plots'])
    
    print("="*80)
    print("WARPAGE DATA ANALYSIS")
    print("="*80)
    
    # Load all data
    print("\n1. Loading data for all resolutions...")
    resolution_data = {}
    file_info = {}
    
    for resolution in resolutions:
        center_data, stats, filename = process_resolution_data(base_path, resolution, row_fraction, col_fraction)
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
        return None, None
    
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
    pdf_filename = export_to_pdf(resolution_data, output_filename=output_filename,
                               include_stats=include_stats, include_3d=include_3d, 
                               dpi=dpi, cmap=cmap, colorbar=colorbar, vmin=vmin, vmax=vmax)
    
    if pdf_filename:
        pdf_size = get_file_size(pdf_filename)
        print(f"   ✓ Analysis PDF: {pdf_filename} ({pdf_size})")
    
    # Show plots if requested
    if show_plots:
        print("\nDisplaying plots...")
        plt.show()
    else:
        print("\nPlots created but not displayed. Use plt.show() to display them.")
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE!")
    print("="*80)
    
    return comparison_fig, resolution_data

# -----------------------------------------------------------------------------
# Command Line Interface
# -----------------------------------------------------------------------------

def parse_command_line_args():
    """
    Parse command line arguments and return a configuration dictionary.
    
    Returns:
        dict: Configuration dictionary with analysis parameters
    """
    config = DEFAULT_CONFIG.copy()
    
    # Show help if requested
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("\nWarpage Analysis Tool")
        print("Usage: python warpage_analyzer.py [options]")
        print("\nOptions:")
        print("  -h, --help           Show this help message")
        print("  --base=PATH          Set base path to data folders")
        print("  --res=RES1,RES2,...  Set resolutions to analyze (comma-separated)")
        print("  --vmin=VALUE         Set minimum value for color scale")
        print("  --vmax=VALUE         Set maximum value for color scale")
        print("  --cmap=NAME          Set colormap name (jet, viridis, plasma, etc.)")
        print("  --colorbar           Enable colorbar")
        print("  --no-colorbar        Disable colorbar")
        print("  --output=FILENAME    Set output PDF filename")
        print("  --stats              Include statistical analysis")
        print("  --no-stats           Exclude statistical analysis")
        print("  --3d                 Include 3D surface plots")
        print("  --no-3d              Exclude 3D surface plots")
        print("  --dpi=VALUE          Set DPI for PDF export")
        print("  --show               Show plots after analysis")
        print("\nExample:")
        print("  python warpage_analyzer.py --cmap=plasma --vmin=-1500 --vmax=-800 --show")
        sys.exit(0)
    
    # Parse arguments
    for arg in sys.argv[1:]:
        if arg.startswith('--base='):
            config['base_path'] = arg.split('=')[1]
        elif arg.startswith('--res='):
            config['resolutions'] = arg.split('=')[1].split(',')
        elif arg.startswith('--vmin='):
            try:
                config['vmin'] = float(arg.split('=')[1])
            except ValueError:
                print("Error: Invalid vmin value")
        elif arg.startswith('--vmax='):
            try:
                config['vmax'] = float(arg.split('=')[1])
            except ValueError:
                print("Error: Invalid vmax value")
        elif arg.startswith('--cmap='):
            config['cmap'] = arg.split('=')[1]
        elif arg == '--colorbar':
            config['colorbar'] = True
        elif arg == '--no-colorbar':
            config['colorbar'] = False
        elif arg.startswith('--output='):
            config['output_filename'] = arg.split('=')[1]
        elif arg == '--stats':
            config['include_stats'] = True
        elif arg == '--no-stats':
            config['include_stats'] = False
        elif arg == '--3d':
            config['include_3d'] = True
        elif arg == '--no-3d':
            config['include_3d'] = False
        elif arg.startswith('--dpi='):
            try:
                config['dpi'] = int(arg.split('=')[1])
            except ValueError:
                print("Error: Invalid DPI value")
        elif arg == '--show':
            config['show_plots'] = True
    
    return config

# -----------------------------------------------------------------------------
# Interactive Mode
# -----------------------------------------------------------------------------

def interactive_mode():
    """
    Run the analysis in interactive mode, prompting the user for configuration.
    
    Returns:
        dict: User-specified configuration
    """
    config = DEFAULT_CONFIG.copy()
    
    print("\nWarpage Analysis Tool - Interactive Mode")
    print("=" * 60)
    
    # Base path
    base_path = input(f"Base path to data folders [{config['base_path']}]: ").strip()
    if base_path:
        config['base_path'] = base_path
    
    # Resolutions
    default_res = ",".join(config['resolutions'])
    res_input = input(f"Resolutions to analyze (comma-separated) [{default_res}]: ").strip()
    if res_input:
        config['resolutions'] = res_input.split(',')
    
    # Colormap
    cmap = input(f"Colormap (jet, viridis, plasma, etc.) [{config['cmap']}]: ").strip()
    if cmap:
        config['cmap'] = cmap
    
    # Color range
    vmin_input = input("Minimum value for color scale [auto]: ").strip()
    if vmin_input:
        try:
            config['vmin'] = float(vmin_input)
        except ValueError:
            print("Invalid value, using auto calculation")
    
    vmax_input = input("Maximum value for color scale [auto]: ").strip()
    if vmax_input:
        try:
            config['vmax'] = float(vmax_input)
        except ValueError:
            print("Invalid value, using auto calculation")
    
    # Colorbar
    colorbar_input = input(f"Show colorbar (y/n) [{'y' if config['colorbar'] else 'n'}]: ").strip().lower()
    if colorbar_input in ['y', 'yes']:
        config['colorbar'] = True
    elif colorbar_input in ['n', 'no']:
        config['colorbar'] = False
    
    # Output filename
    output_filename = input(f"Output PDF filename [{config['output_filename']}]: ").strip()
    if output_filename:
        config['output_filename'] = output_filename
    
    # Show plots
    show_plots_input = input(f"Show plots after analysis (y/n) [{'y' if config['show_plots'] else 'n'}]: ").strip().lower()
    if show_plots_input in ['y', 'yes']:
        config['show_plots'] = True
    elif show_plots_input in ['n', 'no']:
        config['show_plots'] = False
    
    return config

# -----------------------------------------------------------------------------
# Main Entry Point
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    # Check for interactive mode flag
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        config = interactive_mode()
    else:
        # Parse command line arguments
        config = parse_command_line_args()
    
    # Run analysis
    analyze_warpage(config) 