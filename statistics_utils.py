# statistics_utils.py - Statistical Analysis Functions
import numpy as np

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

def collect_resolution_statistics(base_path, resolution_folders):
    """
    Collect statistics for all resolution folders.
    
    Args:
        base_path (str): Base path to data folders
        resolution_folders (list): List of resolution folder names
        
    Returns:
        tuple: (resolutions, stats_data) where stats_data is a dict of lists
    """
    from data_loader import process_resolution_data
    
    resolutions = []
    stats_data = {
        'min': [],
        'max': [],
        'mean': [],
        'std': [],
        'range': []
    }
    
    for resolution in resolution_folders:
        center_data, stats, _ = process_resolution_data(base_path, resolution)
        
        if center_data is not None and stats is not None:
            resolutions.append(int(resolution))
            stats_data['min'].append(stats['min'])
            stats_data['max'].append(stats['max'])
            stats_data['mean'].append(stats['mean'])
            stats_data['std'].append(stats['std'])
            stats_data['range'].append(stats['range'])
    
    return resolutions, stats_data

def print_statistics_summary(resolutions, stats_data):
    """
    Print a formatted summary of statistics.
    
    Args:
        resolutions (list): List of resolution values
        stats_data (dict): Dictionary of statistical data
    """
    print("\n" + "="*80)
    print("WARPAGE DATA ANALYSIS SUMMARY (CENTER REGION)")
    print("="*80)
    
    for i, res in enumerate(resolutions):
        print(f"\nResolution: {res}μm")
        print(f"  Min warpage: {stats_data['min'][i]:.6f}")
        print(f"  Max warpage: {stats_data['max'][i]:.6f}")
        print(f"  Mean warpage: {stats_data['mean'][i]:.6f}")
        print(f"  Std deviation: {stats_data['std'][i]:.6f}")
        print(f"  Range: {stats_data['range'][i]:.6f}")
    
    print("\n" + "="*80)

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