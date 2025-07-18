#!/usr/bin/env python3
"""
Command Line Interface functions for Warpage Analyzer
"""

import sys
from config import DEFAULT_CONFIG


def parse_command_line_args():
    """
    Parse command line arguments and return a configuration dictionary.
    
    Returns:
        dict: Configuration dictionary with analysis parameters
    """
    config = DEFAULT_CONFIG.copy()
    
    # Show help if requested
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print_help()
        sys.exit(0)
    
    # Parse arguments
    for arg in sys.argv[1:]:
        if arg.startswith('--base='):
            config['base_path'] = arg.split('=')[1]
        elif arg.startswith('--folders='):
            config['folders'] = arg.split('=')[1].split(',')
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
        elif arg == '--original':
            config['use_original_files'] = True
        elif arg == '--corrected':
            config['use_original_files'] = False
    
    return config


def print_help():
    """
    Print help message for command line usage.
    """
    print("\nWarpage Analysis Tool")
    print("Usage: python main.py [options]")
    print("\nOptions:")
    print("  -h, --help           Show this help message")
    print("  --base=PATH          Set base path to data folders")
    print("  --folders=F1,F2,...  Set folders to analyze (comma-separated)")
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
    print("  --original           Use original files (@_ORI.txt) [default]")
    print("  --corrected          Use corrected files (.txt, excluding @_ORI.txt)")
    print("\nExample:")
    print("  python main.py --cmap=plasma --vmin=-1500 --vmax=-800 --show")


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
    
    # Folders
    default_folders = ",".join(config['folders'])
    folders_input = input(f"Folders to analyze (comma-separated) [{default_folders}]: ").strip()
    if folders_input:
        config['folders'] = folders_input.split(',')
    
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
    
    # File type selection
    file_type_input = input(f"Use original files (@_ORI.txt) or corrected files (.txt) (original/corrected) [{'original' if config['use_original_files'] else 'corrected'}]: ").strip().lower()
    if file_type_input in ['original', 'o']:
        config['use_original_files'] = True
    elif file_type_input in ['corrected', 'c']:
        config['use_original_files'] = False
    
    return config 