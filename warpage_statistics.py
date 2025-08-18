#!/usr/bin/env python3
"""
Warpage Analyzer용 통계 분석 함수들
Statistical analysis functions for Warpage Analyzer
"""

import numpy as np


def calculate_statistics(data_array):
    """
    데이터 배열에 대한 종합 통계 계산
    Calculate comprehensive statistics for data array.
    
    Args:
        data_array (numpy.ndarray): 입력 데이터 배열 / Input data array
        
    Returns:
        dict: 통계 측정값들을 포함하는 딕셔너리 / Dictionary containing statistical measures
    """
    # NaN 값들을 안전하게 처리하는 함수 사용 / Handle NaN values by using nan-safe functions
    valid_data = data_array[~np.isnan(data_array)]
    
    if len(valid_data) == 0:
        return {
            'min': np.nan,
            'max': np.nan,
            'mean': np.nan,
            'std': np.nan,
            'shape': data_array.shape,
            'range': np.nan
        }
    
    return {
        'min': np.nanmin(data_array),
        'max': np.nanmax(data_array),
        'mean': np.nanmean(data_array),
        'std': np.nanstd(data_array),
        'shape': data_array.shape,
        'range': np.nanmax(data_array) - np.nanmin(data_array)
    }


def find_optimal_color_range(folder_data):
    """
    Find optimal color range for consistent visualization across folders.
    
    Args:
        folder_data (dict): Dictionary with folder as key and data as value
        
    Returns:
        tuple: (vmin, vmax) for color scaling
    """
    all_mins = []
    all_maxs = []
    
    for data in folder_data.values():
        if data is not None:
            # Use nan-safe functions
            valid_data = data[~np.isnan(data)]
            if len(valid_data) > 0:
                all_mins.append(np.nanmin(data))
                all_maxs.append(np.nanmax(data))
    
    if all_mins and all_maxs:
        return min(all_mins), max(all_maxs)
    else:
        return 0, 1  # Default range


def print_statistical_comparison(folder_data):
    """
    Print a formatted table of statistical comparison for all files.
    
    Args:
        folder_data (dict): Dictionary with file_id as key and (data, stats, filename) as value
    """
    print(f"\n5. Statistical Comparison:")
    print("="*80)
    print(f"{'File ID':<10} {'Mean':<12} {'Std':<12} {'Range':<12} {'Min':<12} {'Max':<12}")
    print("-"*80)
    for file_id, (data, stats, filename) in folder_data.items():
        print(f"{file_id:<10} {stats['mean']:<12.6f} {stats['std']:<12.6f} {stats['range']:<12.6f} {stats['min']:<12.6f} {stats['max']:<12.6f}")


def print_file_information(file_info):
    """
    Print a formatted table of file information.
    
    Args:
        file_info (dict): Dictionary with file_id as key and file info as value
    """
    print("\n4. File Information Summary:")
    print("="*80)
    print(f"{'File ID':<10} {'Original Filename':<30} {'File Size':<12} {'Data Shape':<15}")
    print("-"*80)
    for file_id, info in file_info.items():
        print(f"{file_id:<10} {info['filename']:<30} {info['file_size']:<12} {str(info['data_shape']):<15}") 