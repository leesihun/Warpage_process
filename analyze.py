#!/usr/bin/env python3
"""
Simple script to demonstrate how to use presets for warpage analysis.
"""

from main_analysis import compare_resolution
from presets import list_presets
import matplotlib.pyplot as plt

def main():
    """
    Demonstrate how to use presets.
    """
    # Show available presets
    list_presets()
    
    # Choose a preset
    preset_name = input("\nEnter preset name (or press Enter for default): ").strip() or "resolution_comparison"
    
    # Run analysis with chosen preset
    fig = compare_resolution(preset_name)
    
    # Show plots
    print("\nDisplaying plots...")
    plt.show()

if __name__ == "__main__":
    main() 