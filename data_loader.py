#!/usr/bin/env python3
"""
Warpage Analyzer용 데이터 로딩 및 처리 함수들
Data loading and processing functions for Warpage Analyzer
"""

import os
import numpy as np
from config import FILE_PATTERNS


def load_data_from_file(file_path):
    """
    텍스트 파일에서 원시 데이터를 로드하고 모든 0인 행/열을 제거
    Load raw data from a text file, removing all-zero rows and columns by default.
    
    Args:
        file_path (str): 데이터 파일 경로 / Path to the data file
        
    Returns:
        numpy.ndarray: 정리된 데이터 배열, 오류시 None / Cleaned data array, or None if error
    """
    try:
        print(f"Opening file: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            data = f.read()
        
        print(f"  File size: {len(data)} characters")
        
        # 넘파이 배열로 변환 / Convert to numpy array
        data_lines = data.strip().split('\n')
        print(f"  Number of lines: {len(data_lines)}")
        
        data_array = np.array([list(map(float, line.split())) for line in data_lines])
        print(f"  Original array shape: {data_array.shape}")
        
        # 모든 값이 0인 행 제거 / Remove all-zero rows
        nonzero_row_mask = ~(np.all(data_array == 0, axis=1))
        data_array = data_array[nonzero_row_mask, :]
        print(f"  After removing zero rows: {data_array.shape}")
        
        # 모든 값이 0인 열 제거 / Remove all-zero columns
        nonzero_col_mask = ~(np.all(data_array == 0, axis=0))
        data_array = data_array[:, nonzero_col_mask]
        print(f"  After removing zero columns: {data_array.shape}")
        
        # -4000 값을 아티팩트로 간주하여 NaN으로 변환 / Nullify -4000 values as artifacts
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
    데이터 배열에서 중앙 영역 추출
    Extract center region from data array.
    
    Args:
        data_array (numpy.ndarray): 입력 데이터 배열 / Input data array
        row_fraction (float): 중앙에서 유지할 행의 비율 / Fraction of rows to keep in center
        col_fraction (float): 중앙에서 유지할 열의 비율 / Fraction of columns to keep in center
        
    Returns:
        numpy.ndarray: 중앙 영역 데이터 / Center region data
    """
    n_rows, n_cols = data_array.shape
    
    # 비율이 1이면 전체 데이터 반환 / If fractions are 1, return the full data
    if row_fraction == 1 and col_fraction == 1:
        return data_array
    
    # 중앙 영역 경계 계산 / Calculate center region boundaries
    row_margin = (1 - row_fraction) / 2
    col_margin = (1 - col_fraction) / 2
    
    row_start = int(n_rows * row_margin)
    row_end = int(n_rows * (1 - row_margin))
    col_start = int(n_cols * col_margin)
    col_end = int(n_cols * (1 - col_margin))
    
    # 중앙 영역 추출 / Extract center region
    center_data = data_array[row_start:row_end, col_start:col_end]
    
    return center_data


def find_data_files(folder_path, use_original_files=True):
    """
    지정된 폴더에서 모든 데이터 파일 찾기 (원본 또는 보정된 파일)
    Find all data files in a given folder (original or corrected).
    
    Args:
        folder_path (str): 폴더 경로 / Path to the folder
        use_original_files (bool): True면 원본 파일(@_ORI.txt) 찾기, False면 보정된 파일(.txt, @_ORI.txt 제외) 찾기
                                  If True, look for original files (@_ORI.txt), if False, look for corrected files (.txt but not @_ORI.txt)
        
    Returns:
        list: 데이터 파일들의 전체 경로 목록, 없으면 빈 목록 / List of full paths to the data files, or empty list if none found
    """
    try:
        files = os.listdir(folder_path)
        
        if use_original_files:
            # 원본 파일 찾기 / Look for original files
            pattern = FILE_PATTERNS['original']
            target_files = [f for f in files if f.endswith(pattern)]
            file_type = "original"
        else:
            # 보정된 파일 찾기 (.txt이지만 @_ORI.txt는 제외) / Look for corrected files (.txt but not @_ORI.txt)
            pattern = FILE_PATTERNS['corrected']
            original_pattern = FILE_PATTERNS['original']
            target_files = [f for f in files if f.endswith(pattern) and not f.endswith(original_pattern)]
            file_type = "corrected"
        
        if target_files:
            # 일관된 순서를 위해 파일 정렬 / Sort files for consistent ordering
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
    단일 폴더의 모든 파일에 대해 데이터 처리
    Process data for all files in a single folder.
    
    Args:
        base_path (str): 데이터 폴더들의 기본 경로 / Base path to data folders
        folder (str): 폴더 이름 / Folder name
        row_fraction (float): 중앙에서 유지할 행의 비율 / Fraction of rows to keep in center
        col_fraction (float): 중앙에서 유지할 열의 비율 / Fraction of columns to keep in center
        use_original_files (bool): True면 원본 파일(@_ORI.txt) 사용, False면 보정된 파일(.txt, @_ORI.txt 제외) 사용
                                  If True, use original files (@_ORI.txt), if False, use corrected files (.txt but not @_ORI.txt)
        
    Returns:
        list: 각 파일에 대한 튜플 목록 (center_data, stats, data_filename), 오류시 빈 목록
              List of tuples (center_data, stats, data_filename) for each file, or empty list if error
    """
    from warpage_statistics import calculate_statistics
    
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
        
        # 원시 데이터 로드 / Load raw data
        raw_data = load_data_from_file(file_path)
        if raw_data is None:
            print(f"    ⚠ Skipped {filename} (load failed)")
            failed_files += 1
            continue
        
        # 중앙 영역 추출 / Extract center region
        if row_fraction != 1 or col_fraction != 1:
            print(f"    Extracting center region: {row_fraction}x{col_fraction}")
            center_data = extract_center_region(raw_data, row_fraction, col_fraction)
            print(f"    Center region shape: {center_data.shape}")
        else:
            center_data = raw_data
            print(f"    Using full data: {center_data.shape}")
        
        # 통계 계산 / Calculate statistics
        print(f"    Calculating statistics...")
        stats = calculate_statistics(center_data)
        print(f"    Statistics calculated: min={stats['min']:.6f}, max={stats['max']:.6f}, mean={stats['mean']:.6f}")
        
        # 표시용 파일명 가져오기 / Get filename for display
        data_filename = filename
        
        results.append((center_data, stats, data_filename))
        successful_files += 1
        print(f"    OK Processed {filename}: {center_data.shape}")
    
    print(f"  OK Completed {folder}: {successful_files} successful, {failed_files} failed")
    return results


def get_file_size(file_path):
    """
    사람이 읽기 쉬운 형태로 파일 크기 가져오기
    Get file size in a human-readable format.
    
    Args:
        file_path (str): 파일 경로 / Path to the file
        
    Returns:
        str: 사람이 읽기 쉬운 형태의 파일 크기 / File size in human-readable format
    """
    if not os.path.exists(file_path):
        return "File not found"
    
    size_bytes = os.path.getsize(file_path)
    
    # 사람이 읽기 쉬운 형태로 변환 / Convert to human-readable format
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB" 