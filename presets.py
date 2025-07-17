# presets.py - Analysis Presets for Warpage Analysis
"""
This module contains predefined analysis presets for warpage analysis.
Each preset defines a specific type of analysis to perform.
"""

# Default visualization settings
DEFAULT_VISUALIZATION = {
    "vmin": None,  # Auto-calculated
    "vmax": None,  # Auto-calculated
    "cmap": "jet",
    "colorbar": True,
}

# Dictionary of analysis presets
ANALYSIS_PRESETS = {
    # Default resolution comparison preset
    "resolution_comparison": {
        "name": "Resolution Comparison",
        "description": "Compare warpage data across different resolutions",
        "type": "resolution_comparison",
        "base_path": "./data/단일보드",
        "folders": ["30", "60", "90", "120"],
        "visualization": DEFAULT_VISUALIZATION.copy(),
    },
    
    # Placeholder for future presets
    # These will be implemented in future versions
    
    "date_comparison": {
        "name": "Date Comparison",
        "description": "Compare warpage data across different dates (PLACEHOLDER)",
        "type": "date_comparison",
        "implemented": False,
    },
    
    "batch_comparison": {
        "name": "Batch Comparison",
        "description": "Compare warpage data across different batches (PLACEHOLDER)",
        "type": "batch_comparison",
        "implemented": False,
    },
    
    "defect_analysis": {
        "name": "Defect Analysis",
        "description": "Analyze warpage data for defects (PLACEHOLDER)",
        "type": "defect_analysis",
        "implemented": False,
    },
}

def list_presets():
    """
    Print a list of all available analysis presets with their descriptions.
    """
    print("\nAvailable Analysis Presets:")
    print("=" * 80)
    print(f"{'Name':<20} {'Description':<50} {'Status':<10}")
    print("-" * 80)
    
    for key, preset in ANALYSIS_PRESETS.items():
        status = "Available" if preset.get("implemented", True) else "Coming Soon"
        print(f"{preset['name']:<20} {preset['description']:<50} {status:<10}")
    
    print("=" * 80)

def get_preset(preset_name):
    """
    Get a preset by name.
    
    Args:
        preset_name (str): Name of the preset
        
    Returns:
        dict: Preset dictionary with analysis settings
        
    Raises:
        ValueError: If preset_name is not found or not implemented
    """
    preset_key = preset_name.lower()
    if preset_key in ANALYSIS_PRESETS:
        preset = ANALYSIS_PRESETS[preset_key]
        if preset.get("implemented", True):
            return preset
        else:
            raise ValueError(f"Preset '{preset_name}' is not yet implemented.")
    else:
        available_presets = ", ".join([f"'{key}'" for key in ANALYSIS_PRESETS.keys()])
        raise ValueError(f"Preset '{preset_name}' not found. Available presets: {available_presets}")

def update_visualization_settings(preset_name, vmin=None, vmax=None, cmap=None, colorbar=None):
    """
    Update visualization settings for a preset.
    
    Args:
        preset_name (str): Name of the preset
        vmin (float, optional): Minimum value for color scale
        vmax (float, optional): Maximum value for color scale
        cmap (str, optional): Colormap name
        colorbar (bool, optional): Whether to show colorbar
        
    Returns:
        dict: Updated visualization settings
    """
    preset_key = preset_name.lower()
    if preset_key not in ANALYSIS_PRESETS:
        raise ValueError(f"Preset '{preset_name}' not found.")
    
    preset = ANALYSIS_PRESETS[preset_key]
    
    # Create visualization settings if they don't exist
    if "visualization" not in preset:
        preset["visualization"] = DEFAULT_VISUALIZATION.copy()
    
    # Update visualization settings
    if vmin is not None:
        preset["visualization"]["vmin"] = vmin
    if vmax is not None:
        preset["visualization"]["vmax"] = vmax
    if cmap is not None:
        preset["visualization"]["cmap"] = cmap
    if colorbar is not None:
        preset["visualization"]["colorbar"] = colorbar
    
    return preset["visualization"] 