#!/usr/bin/env python3
"""
Warpage Analyzer - Main Entry Point

A modular tool for analyzing warpage data across different resolutions
Refactored from single-file architecture to modular design for better maintainability.

Usage:
    python main.py [options]                  # Command line mode
    python main.py --interactive              # Interactive mode
    python main.py --help                     # Show help
    
Example:
    python main.py --cmap=plasma --vmin=-1500 --vmax=-800 --show
"""

import sys
from cli import parse_command_line_args, interactive_mode
from analyzer import analyze_warpage


def main():
    """
    Main entry point for the Warpage Analyzer application.
    
    Handles command line arguments and runs the analysis.
    """
    # Check for interactive mode flag
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        config = interactive_mode()
    else:
        # Parse command line arguments
        config = parse_command_line_args()
    
    # Run analysis
    analyze_warpage(config)


if __name__ == "__main__":
    main() 