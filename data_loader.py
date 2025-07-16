# data_loader.py - Data Loading and Processing Functions
import os
import numpy as np

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
        row_fraction (float): Fraction of rows to keep in center (default: 0.4)
        col_fraction (float): Fraction of columns to keep in center (default: 0.5)
        
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

def find_all_data_files(folder_path, pattern='@_ORI.txt'):
    """
    Find all data files matching a pattern in a given folder.
    This function is designed for future use when comparing multiple files of same resolution.
    
    Args:
        folder_path (str): Path to the folder
        pattern (str): File pattern to match (default: '@_ORI.txt')
        
    Returns:
        list: List of full paths to matching files
    """
    try:
        files = os.listdir(folder_path)
        matching_files = [os.path.join(folder_path, f) for f in files if pattern in f]
        return matching_files
    except Exception as e:
        print(f"Error accessing folder {folder_path}: {e}")
        return []

def process_resolution_data(base_path, resolution):
    """
    Process data for a single resolution.
    
    Args:
        base_path (str): Base path to data folders
        resolution (str): Resolution folder name
        
    Returns:
        tuple: (center_data, stats, ori_filename) or (None, None, None) if error
    """
    from statistics_utils import calculate_statistics
    
    folder_path = os.path.join(base_path, resolution)
    file_path = find_ori_file(folder_path)
    
    if file_path is None:
        return None, None, None
    
    # Load raw data
    raw_data = load_data_from_file(file_path)
    if raw_data is None:
        return None, None, None
    
    # Extract center region
    center_data = extract_center_region(raw_data)
    
    # Calculate statistics
    stats = calculate_statistics(center_data)
    
    # Get filename for display
    ori_filename = os.path.basename(file_path)
    
    return center_data, stats, ori_filename

def process_multiple_files_same_resolution(base_path, resolution, file_pattern='@_ORI.txt'):
    """
    Process multiple files for the same resolution.
    This function is designed for future use when comparing multiple datasets of same resolution.
    
    Args:
        base_path (str): Base path to data folders
        resolution (str): Resolution folder name
        file_pattern (str): Pattern to match files (default: '@_ORI.txt')
        
    Returns:
        dict: Dictionary with filename as key and (center_data, stats, filename) as value
    """
    from statistics_utils import calculate_statistics
    
    folder_path = os.path.join(base_path, resolution)
    file_paths = find_all_data_files(folder_path, file_pattern)
    
    results = {}
    
    for file_path in file_paths:
        # Load raw data
        raw_data = load_data_from_file(file_path)
        if raw_data is None:
            continue
        
        # Extract center region
        center_data = extract_center_region(raw_data)
        
        # Calculate statistics
        stats = calculate_statistics(center_data)
        
        # Get filename for display
        filename = os.path.basename(file_path)
        dataset_name = filename.replace('@_ORI.txt', '').replace('@.txt', '')
        
        results[dataset_name] = (center_data, stats, filename)
    
    return results

def get_available_resolutions(base_path='./data/단일보드'):
    """
    Get list of available resolution folders.
    
    Args:
        base_path (str): Base path to data folders
        
    Returns:
        list: List of available resolution folder names
    """
    try:
        if not os.path.exists(base_path):
            print(f"Base path does not exist: {base_path}")
            return []
        
        folders = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]
        # Filter to only numeric folder names (resolutions)
        resolution_folders = [f for f in folders if f.isdigit()]
        return sorted(resolution_folders, key=int)
    except Exception as e:
        print(f"Error accessing base path {base_path}: {e}")
        return [] 