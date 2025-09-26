#!/usr/bin/env python3
"""
Warpage Analyzer용 데이터 로딩 및 처리 함수들
Data loading and processing functions for Warpage Analyzer
"""

import os
import numpy as np
from config import FILE_PATTERNS
from functools import lru_cache
import hashlib

# Memory optimization: Global cache for processed files
_file_cache = {}
_cache_max_size = 50  # Maximum cached files

def _get_file_hash(file_path):
    """Generate a hash for file caching based on path and modification time."""
    try:
        stat = os.stat(file_path)
        return hashlib.md5(f"{file_path}:{stat.st_mtime}:{stat.st_size}".encode()).hexdigest()
    except (OSError, IOError):
        return None

def _cache_file_data(file_path, data):
    """Cache processed file data with LRU eviction."""
    global _file_cache
    if len(_file_cache) >= _cache_max_size:
        # Remove oldest entry (simple FIFO for speed)
        oldest_key = next(iter(_file_cache))
        del _file_cache[oldest_key]

    file_hash = _get_file_hash(file_path)
    if file_hash:
        _file_cache[file_hash] = data

def _get_cached_file_data(file_path):
    """Retrieve cached file data if available and valid."""
    file_hash = _get_file_hash(file_path)
    if file_hash and file_hash in _file_cache:
        return _file_cache[file_hash]
    return None


def load_data_from_file(file_path, downsample_factor=1):
    """
    텍스트 또는 AKROMETRIX 파일에서 원시 데이터를 로드하고 모든 0인 행/열을 제거
    Load raw data from a text or AKROMETRIX file, removing all-zero rows and columns by default.

    Args:
        file_path (str): 데이터 파일 경로 / Path to the data file
        downsample_factor (int): 다운샘플링 비율 (1=원본, 2=반, 4=1/4 크기) / Downsampling factor

    Returns:
        numpy.ndarray: 정리된 데이터 배열, 오류시 None / Cleaned data array, or None if error
    """
    try:
        # 파일 타입에 따른 처리 / Process based on file type
        file_ext = os.path.splitext(file_path)[1].lower()
        is_akrometrix = file_ext == '.dat'

        if is_akrometrix:
            # AKROMETRIX 파일은 다양한 인코딩을 시도 / Try various encodings for AKROMETRIX files
            encodings_to_try = ['utf-8', 'latin-1', 'cp1252']
            for encoding in encodings_to_try:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        data = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            else:
                return None
        else:
            # 일반 텍스트 파일 / Regular text file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = f.read()

        # 넘파이 배열로 변환 / Convert to numpy array - optimized approach
        data_lines = [line.strip() for line in data.strip().split('\n') if line.strip() and not line.startswith(('#', '%'))]

        if not data_lines:
            return None

        # 빠른 파싱을 위한 최적화된 접근 / Optimized parsing approach
        try:
            # 첫 번째 줄로 데이터 형식 확인 / Validate format with first line
            first_line = data_lines[0].split()
            [float(x) for x in first_line]  # Test conversion

            # numpy loadtxt가 더 빠름 / numpy loadtxt is faster for large datasets
            from io import StringIO
            clean_data = '\n'.join(data_lines)
            data_array = np.loadtxt(StringIO(clean_data))

            # 1D 배열인 경우 2D로 변환 / Convert 1D to 2D if needed
            if data_array.ndim == 1:
                data_array = data_array.reshape(1, -1)

        except (ValueError, IndexError):
            # 대체 방법 사용 / Use fallback method
            clean_lines = []
            for line in data_lines:
                try:
                    float_values = [float(x) for x in line.split()]
                    if float_values:
                        clean_lines.append(float_values)
                except ValueError:
                    continue

            if not clean_lines:
                return None
            data_array = np.array(clean_lines)

        # 최적화된 전처리 / Optimized preprocessing
        # 모든 값이 0인 행/열 제거 / Remove all-zero rows/columns in one pass
        nonzero_mask = (data_array != 0).any(axis=1)
        if nonzero_mask.any():
            data_array = data_array[nonzero_mask]
            nonzero_mask = (data_array != 0).any(axis=0)
            if nonzero_mask.any():
                data_array = data_array[:, nonzero_mask]

        # 아티팩트 값들을 NaN으로 변환 - 벡터화 연산 / Nullify artifact values - vectorized operation
        invalid_values = np.array([-4000, 9999, -9999, 99999, -99999])
        mask = np.isin(data_array, invalid_values)
        if mask.any():
            data_array = data_array.astype(float)  # Ensure float type for NaN
            data_array[mask] = np.nan

        # 다운샘플링 적용 (요청된 경우) / Apply downsampling if requested
        if downsample_factor > 1:
            data_array = data_array[::downsample_factor, ::downsample_factor]

        return data_array
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None


@lru_cache(maxsize=32)
def _calculate_region_bounds(n_rows, n_cols, row_fraction, col_fraction):
    """Cached calculation of region boundaries for speed."""
    row_margin = (1 - row_fraction) / 2
    col_margin = (1 - col_fraction) / 2

    row_start = int(n_rows * row_margin)
    row_end = int(n_rows * (1 - row_margin))
    col_start = int(n_cols * col_margin)
    col_end = int(n_cols * (1 - col_margin))

    return row_start, row_end, col_start, col_end

def extract_center_region(data_array, row_fraction=1, col_fraction=1):
    """
    데이터 배열에서 중앙 영역 추출 - 성능 최적화
    Extract center region from data array - performance optimized.

    Args:
        data_array (numpy.ndarray): 입력 데이터 배열 / Input data array
        row_fraction (float): 중앙에서 유지할 행의 비율 / Fraction of rows to keep in center
        col_fraction (float): 중앙에서 유지할 열의 비율 / Fraction of columns to keep in center

    Returns:
        numpy.ndarray: 중앙 영역 데이터 / Center region data
    """
    # Fast path for full data
    if row_fraction == 1 and col_fraction == 1:
        return data_array

    n_rows, n_cols = data_array.shape

    # Use cached boundary calculation
    row_start, row_end, col_start, col_end = _calculate_region_bounds(n_rows, n_cols, row_fraction, col_fraction)

    # Efficient slice extraction
    return data_array[row_start:row_end, col_start:col_end]


def find_data_files(folder_path, use_original_files=True):
    """
    지정된 폴더에서 모든 데이터 파일 찾기 (원본, 보정된 파일, 또는 AKROMETRIX 파일)
    Find all data files in a given folder (original, corrected, or AKROMETRIX files).

    Args:
        folder_path (str): 폴더 경로 / Path to the folder
        use_original_files (bool): True면 원본 파일들 우선, False면 보정된 파일 우선
                                  If True, prioritize original files, if False, prioritize corrected files

    Returns:
        list: 데이터 파일들의 전체 경로 목록, 없으면 빈 목록 / List of full paths to the data files, or empty list if none found
    """
    try:
        files = os.listdir(folder_path)

        # 최적화된 패턴 매칭 / Optimized pattern matching
        original_patterns = FILE_PATTERNS['original']
        original_pkg_patterns = FILE_PATTERNS.get('original_with_package', [])
        akrometrix_patterns = FILE_PATTERNS.get('akrometrix', [])

        # 파일별로 타입 분류 - 한 번의 순회로 처리 / Classify files by type in single pass
        original_files = []
        original_pkg_files = []
        corrected_files = []
        akrometrix_files = []

        for f in files:
            # 원본 패턴 확인 / Check original patterns
            if any(f.endswith(pattern) for pattern in original_patterns):
                original_files.append(f)
            # 원본 패키지 패턴 확인 / Check original package patterns
            elif any(f.endswith(pattern) for pattern in original_pkg_patterns):
                original_pkg_files.append(f)
            # AKROMETRIX 패턴 확인 / Check AKROMETRIX patterns
            elif any(f.endswith(pattern) for pattern in akrometrix_patterns):
                akrometrix_files.append(f)
            # 보정된 파일 (.txt이지만 원본이 아닌) / Corrected files (.txt but not originals)
            elif f.endswith('.txt'):
                corrected_files.append(f)

        # 우선순위에 따른 파일 선택 / Select files based on priority
        if use_original_files:
            search_order = [original_files, original_pkg_files, corrected_files, akrometrix_files]
        else:
            search_order = [corrected_files, original_files, original_pkg_files, akrometrix_files]

        for file_list in search_order:
            if file_list:
                file_list.sort()  # 일관된 순서
                return [os.path.join(folder_path, f) for f in file_list]

        return []
    except Exception:
        return []


def process_folder_data_parallel(base_path, folder, row_fraction=1, col_fraction=1, use_original_files=True, downsample_factor=1, max_workers=None):
    """
    병렬 처리로 단일 폴더의 모든 파일 데이터 처리 - 최대 속도
    Parallel process data for all files in a single folder - maximum speed.

    Args:
        base_path (str): 데이터 폴더들의 기본 경로 / Base path to data folders
        folder (str): 폴더 이름 / Folder name
        row_fraction (float): 중앙에서 유지할 행의 비율 / Fraction of rows to keep in center
        col_fraction (float): 중앙에서 유지할 열의 비율 / Fraction of columns to keep in center
        use_original_files (bool): 원본 vs 보정 파일 / Original vs corrected files
        downsample_factor (int): 데이터 다운샘플링 비율 / Data downsampling factor (1=no downsampling, 2=half, 4=quarter, etc.)
        max_workers (int): 최대 워커 수 / Maximum worker threads (None=auto)

    Returns:
        list: 각 파일에 대한 튜플 목록 (center_data, stats, data_filename)
              List of tuples (center_data, stats, data_filename) for each file
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from warpage_statistics import calculate_statistics
    import multiprocessing

    folder_path = os.path.join(base_path, folder)
    file_paths = find_data_files(folder_path, use_original_files)

    if not file_paths:
        return []

    # 자동 워커 수 설정 - CPU 코어 수 기반 / Auto worker count based on CPU cores
    if max_workers is None:
        max_workers = min(len(file_paths), multiprocessing.cpu_count() * 2)  # Aggressive threading

    def process_single_file_fast(file_path):
        """Fast single file processing with caching and memory optimization"""
        try:
            filename = os.path.basename(file_path)
            # Use caching and pass downsample_factor directly to load function
            raw_data = load_data_from_file(file_path, downsample_factor)
            if raw_data is None:
                return None

            # 중앙 영역 추출 / Extract center region
            center_region_needed = row_fraction != 1 or col_fraction != 1
            center_data = extract_center_region(raw_data, row_fraction, col_fraction) if center_region_needed else raw_data

            # 통계 계산 / Calculate statistics
            stats = calculate_statistics(center_data)

            return (center_data, stats, filename)
        except Exception:
            return None

    # 병렬 처리 실행 / Execute parallel processing
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 모든 파일을 병렬로 제출 / Submit all files in parallel
        future_to_path = {executor.submit(process_single_file_fast, path): path for path in file_paths}

        # 결과 수집 / Collect results
        for future in as_completed(future_to_path):
            result = future.result()
            if result is not None:
                results.append(result)

    # 파일명 순서로 정렬 / Sort by filename for consistency
    results.sort(key=lambda x: x[2])
    return results

def process_folder_data(base_path, folder, row_fraction=1, col_fraction=1, use_original_files=True, downsample_factor=1):
    """
    Backward compatible wrapper - uses parallel processing by default for maximum speed
    """
    return process_folder_data_parallel(base_path, folder, row_fraction, col_fraction, use_original_files, downsample_factor)


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


# ===========================================
# BATCH PROCESSING FUNCTIONS
# ===========================================

def process_batch_files(file_paths, row_fraction=1.0, col_fraction=1.0):
    """
    Process multiple files in batch with parallel processing support.
    
    Args:
        file_paths (list): List of file paths to process
        row_fraction (float): Fraction of rows to keep in center region
        col_fraction (float): Fraction of columns to keep in center region
        
    Returns:
        dict: Processed data with file_id as key and (data, stats, filename) as value
    """
    from warpage_statistics import calculate_statistics
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import threading
    
    print(f"Starting batch processing of {len(file_paths)} files...")
    
    # Thread-safe progress tracking
    progress_lock = threading.Lock()
    processed_count = [0]  # Use list for mutable reference
    
    def process_single_file(file_path):
        """Process a single file and return results"""
        try:
            filename = os.path.basename(file_path)
            
            # Load raw data
            raw_data = load_data_from_file(file_path)
            if raw_data is None:
                print(f"    ⚠ Skipped {filename} (load failed)")
                return None
            
            # Extract center region if needed
            if row_fraction != 1 or col_fraction != 1:
                center_data = extract_center_region(raw_data, row_fraction, col_fraction)
            else:
                center_data = raw_data
            
            # Calculate statistics
            stats = calculate_statistics(center_data)
            
            # Update progress
            with progress_lock:
                processed_count[0] += 1
                print(f"    Progress: {processed_count[0]}/{len(file_paths)} - Processed {filename}")
            
            return (filename, center_data, stats)
            
        except Exception as e:
            print(f"    ERROR processing {os.path.basename(file_path)}: {e}")
            return None
    
    # Process files in parallel
    folder_data = {}
    with ThreadPoolExecutor(max_workers=4) as executor:
        # Submit all tasks
        future_to_path = {executor.submit(process_single_file, path): path for path in file_paths}
        
        # Collect results as they complete
        for future in as_completed(future_to_path):
            result = future.result()
            if result:
                filename, data, stats = result
                # Create unique file ID
                file_id = f"File_{len(folder_data) + 1:02d}"
                folder_data[file_id] = (data, stats, filename)
    
    print(f"Batch processing completed: {len(folder_data)} files successfully processed")
    return folder_data


def validate_batch_files(file_paths):
    """
    Validate batch files before processing.
    
    Args:
        file_paths (list): List of file paths to validate
        
    Returns:
        dict: Validation results with valid/invalid file lists
    """
    valid_files = []
    invalid_files = []
    
    print(f"Validating {len(file_paths)} files...")
    
    for file_path in file_paths:
        filename = os.path.basename(file_path)
        
        # Check file existence
        if not os.path.exists(file_path):
            invalid_files.append({'path': file_path, 'reason': 'File not found'})
            continue
        
        # Check file extension
        if not filename.endswith(('.txt', '.ptr')):
            invalid_files.append({'path': file_path, 'reason': 'Invalid file extension'})
            continue
        
        # Check file size (skip empty files)
        if os.path.getsize(file_path) == 0:
            invalid_files.append({'path': file_path, 'reason': 'Empty file'})
            continue
        
        # Try to read a few lines to check format
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                sample_lines = [f.readline().strip() for _ in range(3)]
                
            # Basic format validation
            for line in sample_lines:
                if line:  # Skip empty lines
                    try:
                        # Try to parse numbers
                        list(map(float, line.split()))
                    except ValueError:
                        raise ValueError("Invalid number format")
                        
            valid_files.append(file_path)
            
        except Exception as e:
            invalid_files.append({'path': file_path, 'reason': f'Format error: {str(e)}'})
    
    print(f"Validation completed: {len(valid_files)} valid, {len(invalid_files)} invalid")
    
    return {
        'valid_files': valid_files,
        'invalid_files': invalid_files,
        'total_files': len(file_paths),
        'valid_count': len(valid_files),
        'invalid_count': len(invalid_files)
    }


def create_batch_summary(folder_data):
    """
    Create a summary of batch processing results.
    
    Args:
        folder_data (dict): Processed batch data
        
    Returns:
        dict: Summary statistics and information
    """
    if not folder_data:
        return {'error': 'No data to summarize'}
    
    # Extract all data for global statistics
    all_means = []
    all_stds = []
    all_ranges = []
    all_mins = []
    all_maxs = []
    total_data_points = 0
    
    file_details = []
    
    for file_id, (data, stats, filename) in folder_data.items():
        all_means.append(stats['mean'])
        all_stds.append(stats['std'])
        all_ranges.append(stats['range'])
        all_mins.append(stats['min'])
        all_maxs.append(stats['max'])
        total_data_points += np.prod(data.shape)
        
        file_details.append({
            'file_id': file_id,
            'filename': filename,
            'shape': stats['shape'],
            'data_points': np.prod(data.shape),
            'mean': stats['mean'],
            'std': stats['std'],
            'min': stats['min'],
            'max': stats['max'],
            'range': stats['range']
        })
    
    # Calculate global statistics
    summary = {
        'file_count': len(folder_data),
        'total_data_points': total_data_points,
        'global_stats': {
            'mean_of_means': np.mean(all_means),
            'std_of_means': np.std(all_means),
            'overall_min': np.min(all_mins),
            'overall_max': np.max(all_maxs),
            'mean_range': np.mean(all_ranges),
            'max_range': np.max(all_ranges)
        },
        'file_details': file_details
    }
    
    return summary 