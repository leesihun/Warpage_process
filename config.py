#!/usr/bin/env python3
"""
Configuration settings for Warpage Analyzer
"""

# Default configuration settings
DEFAULT_CONFIG = {
    "base_path": "./data/",                    # Base path to data folders
    "folders": ["20250716"],                   # Resolution folders to analyze
    "vmin": None,                              # Min value for color scale (None = auto)
    "vmax": None,                              # Max value for color scale (None = auto)
    "cmap": "jet",                             # Colormap (jet, viridis, plasma, etc.)
    "colorbar": True,                          # Whether to show colorbar
    "row_fraction": 1,                         # Fraction of rows to keep in center
    "col_fraction": 1,                         # Fraction of columns to keep in center
    "output_filename": "warpage_analysis.pdf", # Output PDF filename
    "include_stats": True,                     # Include statistical analysis plots
    "include_3d": True,                        # Include 3D surface plots
    "dpi": 600,                                # DPI for PDF export
    "show_plots": False,                       # Show plots after analysis
    "use_original_files": True                 # Use original files (@_ORI.txt) vs corrected files (.txt)
}

# Directory settings
DATA_DIR = './data/'
REPORT_DIR = 'report'

# Web GUI settings
WEB_PORT = 9410072
WEB_HOST = '0.0.0.0'
WEB_DEBUG = True

# File patterns
FILE_PATTERNS = {
    'original': '@_ORI.txt',     # Original files pattern
    'corrected': '@.txt'          # Corrected files pattern (excluding @_ORI.txt)
} 