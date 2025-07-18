#!/usr/bin/env python3
"""
Data loading and processing functions for Warpage Analyzer
"""

import os
import numpy as np
from config import FILE_PATTERNS


def load_data_from_file(file_path):
    """
    Load raw data from a text file, removing all-zero rows and columns by default.
    
    Args:
        file_path (str): Path to the data file
        
    Returns:
        numpy.ndarray: Cleaned data array, or None if error
    """
    try:
        print(f"Opening file: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            data = f.read()
        
        print(f"  File size: {len(data)} characters")
        
        # Convert to numpy array
        data_lines = data.strip().split('\n')
        print(f"  Number of lines: {len(data_lines)}")
        
        data_array = np.array([list(map(float, line.split())) for line in data_lines])
        print(f"  Original array shape: {data_array.shape}")
        
        # Remove all-zero rows
        nonzero_row_mask = ~(np.all(data_array == 0, axis=1))
        data_array = data_array[nonzero_row_mask, :]
        print(f"  After removing zero rows: {data_array.shape}")
        
        # Remove all-zero columns
        nonzero_col_mask = ~(np.all(data_array == 0, axis=0))
        data_array = data_array[:, nonzero_col_mask]
        print(f"  After removing zero columns: {data_array.shape}")
        
        # Nullify -4000 values as artifacts
        artifact_count = np.sum(data_array == -4000)
        data_array = np.where(data_array == -4000, np.nan, data_array)
        if artifact_count > 0:
            print(f"  Nullified {artifact_count} -4000 artifacts")
        
        print(f"  Final array shape: {data_array.shape}")
        return data_array
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None


def extract_center_region(data_array, row_fraction=1, col_fraction=1):
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
    
    # If fractions are 1, return the full data
    if row_fraction == 1 and col_fraction == 1:
        return data_array
    
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


def find_data_files(folder_path, use_original_files=True):
    """
    Find all data files in a given folder (original or corrected).
    
    Args:
        folder_path (str): Path to the folder
        use_original_files (bool): If True, look for original files (@_ORI.txt), 
                                  if False, look for corrected files (.txt but not @_ORI.txt)
        
    Returns:
        list: List of full paths to the data files, or empty list if none found
    """
    try:
        files = os.listdir(folder_path)
        
        if use_original_files:
            # Look for original files
            pattern = FILE_PATTERNS['original']
            target_files = [f for f in files if f.endswith(pattern)]
            file_type = "original"
        else:
            # Look for corrected files (.txt but not @_ORI.txt)
            pattern = FILE_PATTERNS['corrected']
            original_pattern = FILE_PATTERNS['original']
            target_files = [f for f in files if f.endswith(pattern) and not f.endswith(original_pattern)]
            file_type = "corrected"
        
        if target_files:
            # Sort files for consistent ordering
            target_files.sort()
            return [os.path.join(folder_path, f) for f in target_files]
        else:
            print(f"No {file_type} files found in {folder_path}")
            return []
    except Exception as e:
        print(f"Error accessing folder {folder_path}: {e}")
        return []


def process_folder_data(base_path, folder, row_fraction=1, col_fraction=1, use_original_files=True):
    """
    Process data for all files in a single folder.
    
    Args:
        base_path (str): Base path to data folders
        folder (str): Folder name
        row_fraction (float): Fraction of rows to keep in center
        col_fraction (float): Fraction of columns to keep in center
        use_original_files (bool): If True, use original files (@_ORI.txt), 
                                  if False, use corrected files (.txt but not @_ORI.txt)
        
    Returns:
        list: List of tuples (center_data, stats, data_filename) for each file, or empty list if error
    """
    from statistics import calculate_statistics
    
    folder_path = os.path.join(base_path, folder)
    file_paths = find_data_files(folder_path, use_original_files)
    
    if not file_paths:
        print(f"  No files found in {folder}")
        return []
    
    print(f"  Found {len(file_paths)} files to process")
    print(f"  Processing parameters: row_fraction={row_fraction}, col_fraction={col_fraction}")
    print(f"  File type: {'original' if use_original_files else 'corrected'}")
    
    results = []
    successful_files = 0
    failed_files = 0
    
    for i, file_path in enumerate(file_paths):
        filename = os.path.basename(file_path)
        print(f"    Processing file {i+1}/{len(file_paths)}: {filename}")
        
        # Load raw data
        raw_data = load_data_from_file(file_path)
        if raw_data is None:
            print(f"    ⚠ Skipped {filename} (load failed)")
            failed_files += 1
            continue
        
        # Extract center region
        if row_fraction != 1 or col_fraction != 1:
            print(f"    Extracting center region: {row_fraction}x{col_fraction}")
            center_data = extract_center_region(raw_data, row_fraction, col_fraction)
            print(f"    Center region shape: {center_data.shape}")
        else:
            center_data = raw_data
            print(f"    Using full data: {center_data.shape}")
        
        # Calculate statistics
        print(f"    Calculating statistics...")
        stats = calculate_statistics(center_data)
        print(f"    Statistics calculated: min={stats['min']:.6f}, max={stats['max']:.6f}, mean={stats['mean']:.6f}")
        
        # Get filename for display
        data_filename = filename
        
        results.append((center_data, stats, data_filename))
        successful_files += 1
        print(f"    ✓ Processed {filename}: {center_data.shape}")
    
    print(f"  ✓ Completed {folder}: {successful_files} successful, {failed_files} failed")
    return results


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