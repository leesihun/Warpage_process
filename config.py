#!/usr/bin/env python3
"""
Warpage Analyzer용 설정 구성
Configuration settings for Warpage Analyzer

This module provides centralized configuration management for the PEMTRON Warpage Analysis Tool.
It handles path resolution for both development and PyInstaller executable environments,
and defines all configurable parameters for the application.
"""

import os
import sys

def get_resource_path(relative_path):
    """
    Get absolute path to resource, works for both development and PyInstaller executable modes.
    
    This function automatically detects if the code is running as a PyInstaller executable
    or in development mode and returns the appropriate absolute path to resources.
    
    Args:
        relative_path (str): Relative path to the resource file/directory
        
    Returns:
        str: Absolute path to the resource
        
    Example:
        >>> get_resource_path('templates/index.html')
        '/path/to/app/templates/index.html'  # In development
        # or
        '/temp/pyinstaller_bundle/templates/index.html'  # In executable
    """
    if hasattr(sys, '_MEIPASS'):
        # Running as PyInstaller executable - use temporary extraction directory
        base_path = sys._MEIPASS
    else:
        # Running in development - use script directory
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)

def get_data_dir():
    """
    Get the data directory path, handling both development and executable modes.
    
    This function implements a search strategy to locate the data directory:
    1. In executable mode: searches for 'data' folder in multiple locations
    2. In development mode: uses relative path from script location
    
    Search order for executable mode:
    1. Next to the executable file
    2. In current working directory
    3. Fallback to script directory
    
    Returns:
        str: Absolute path to the data directory
        
    Note:
        If no data directory is found in executable mode, returns the first
        search location and lets the application handle the missing directory.
    """
    if hasattr(sys, '_MEIPASS'):
        # In PyInstaller executable, try multiple possible data folder locations
        exe_dir = os.path.dirname(sys.executable)
        possible_paths = [
            os.path.join(exe_dir, 'data'),  # Next to exe (most common)
            os.path.join(os.getcwd(), 'data'),  # In current working directory
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')  # Fallback to script directory
        ]
        
        # Return the first existing data directory
        for path in possible_paths:
            if os.path.exists(path) and os.path.isdir(path):
                print(f"DEBUG: Found data directory at: {path}")
                return path
        
        # If none found, return the first option (next to exe) and let the app handle the error
        print(f"DEBUG: No data directory found, using default: {possible_paths[0]}")
        return possible_paths[0]
    else:
        # In development, use relative path from script location
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

# 기본 설정 구성 / Default configuration settings
# This dictionary contains all default configuration parameters for the warpage analysis tool
DEFAULT_CONFIG = {
    # === Data Directory Settings ===
    "base_path": get_data_dir(),               # 데이터 폴더 기본 경로 / Base path to data folders
    "data_dir": get_data_dir(),                # 웹서버용 데이터 디렉토리 / Data directory for web server
    "folders": ["20250716"],                   # 분석할 폴더들 / Folders to analyze (list of folder names)
    
    # === Visualization Settings ===
    "vmin": None,                              # 색상 스케일 최솏값 (None = 자동) / Min value for color scale (None = auto-detect)
    "vmax": None,                              # 색상 스케일 최댓값 (None = 자동) / Max value for color scale (None = auto-detect)
    "cmap": "jet",                             # 색상맵 (jet, viridis, plasma 등) / Colormap (jet, viridis, plasma, etc.)
    "colorbar": True,                          # 색상 막대 표시 여부 / Whether to show colorbar in plots
    
    # === Data Processing Settings ===
    "row_fraction": 1,                         # 중앙에서 유지할 행 비율 / Fraction of rows to keep in center (1.0 = keep all)
    "col_fraction": 1,                         # 중앙에서 유지할 열 비율 / Fraction of columns to keep in center (1.0 = keep all)
    
    # === Output Settings ===
    "output_filename": "warpage_analysis.pdf", # 출력 PDF 파일명 / Output PDF filename
    "dpi": 500,                                # PDF 내보낼 용 DPI / DPI for PDF export (higher = better quality, larger file)
    "show_plots": False,                       # 분석 후 그래프 표시 여부 / Show plots after analysis (for interactive mode)
    
    # === Report Content Settings ===
    "include_stats": True,                     # 통계 분석 그래프 포함 여부 / Include statistical analysis plots in report
    "include_3d": True,                        # 3D 표면 그래프 포함 여부 / Include 3D surface plots in report
    "include_advanced": False,                 # 고급 통계 분석 포함 여부 (성능상 기본 비활성화) / Include advanced statistical analysis (disabled by default for performance)
    "optimize_pdf_data": True,                 # PDF 생성시 데이터 리사이징 최적화 / Optimize data resizing for faster PDF generation
    "disable_data_resizing": False,           # 데이터 리사이징 완전 비활성화 / Completely disable data resizing for all visualizations
    
    # === File Processing Settings ===
    "use_original_files": True                 # 원본 파일(@_ORI.txt) vs 보정된 파일(.txt) 사용 / Use original files (@_ORI.txt) vs corrected files (.txt)
}

# === Directory Configuration ===
# Global directory paths used throughout the application
DATA_DIR = get_data_dir()                    # 데이터 디렉토리 / Data directory - where measurement files are stored
REPORT_DIR = get_resource_path('report')     # 보고서 디렉토리 / Report directory - where PDF reports are saved

# === Web GUI Configuration ===
# Settings for the Flask web server interface
WEB_PORT = 5001       # 웹 서버 포트 / Web server port (unique port for PEMTRON_warpage as per user rules)
WEB_HOST = '0.0.0.0'     # 웹 서버 호스트 / Web server host (0.0.0.0 = listen on all interfaces)
WEB_DEBUG = False        # 웹 디버그 모드 / Web debug mode (disabled for production builds)

# === File Pattern Configuration ===
# Defines which file types and naming patterns the system recognizes
FILE_PATTERNS = {
    # Original measurement files (raw data from equipment)
    'original': ['_ORI.txt', '@_ORI.txt'],     # 원본 파일 패턴들 / Original files patterns (multiple variations)
    'original_with_package': ['_ORI_A.txt', '@_ORI_A.txt'],  # Original files with additional package info
    
    # Processed/corrected measurement files
    'corrected': '.txt',         # 보정된 파일 패턴 (원본 파일들 제외) / Corrected files pattern (excluding original files)
    
    # Equipment-specific file formats
    'akrometrix': ['.dat', '.DAT'],  # AKROMETRIX 파일 패턴들 / AKROMETRIX measurement equipment file patterns
}

# === Batch Processing Configuration ===
# Settings for processing multiple files simultaneously
BATCH_CONFIG = {
    'max_files': 1000,              # 최대 배치 파일 수 / Maximum batch file count (prevents memory overload)
    'max_file_size_mb': 500,        # 파일당 최대 크기 (MB) / Maximum file size per file (MB)
    'max_total_size_mb': 500000,      # 총 최대 크기 (MB) / Maximum total size (MB) for entire batch
    'parallel_workers': 16,         # 병렬 처리 워커 수 / Number of parallel workers (CPU cores to use)
    'supported_extensions': ['.txt', '.ptr', '.dat', '.DAT'],  # 지원되는 파일 확장자 / Supported file extensions
    'temp_dir_prefix': 'warpage_batch_'        # 임시 디렉토리 접두사 / Temporary directory prefix for batch operations
}

# === Interactive Plot Configuration ===
# Settings for web-based interactive visualizations using Plotly
PLOTLY_CONFIG = {
    'default_colorscale': 'jet',   # 기본 색상맵 / Default colorscale (matches matplotlib colormap)
    'plot_width': 800,             # 기본 플롯 너비 / Default plot width in pixels
    'plot_height': 600,            # 기본 플롯 높이 / Default plot height in pixels
    'show_toolbar': True,          # 도구막대 표시 / Show plotly toolbar (zoom, pan, download controls)
    'enable_zoom': True,           # 줌 기능 활성화 / Enable zoom functionality
    'enable_pan': True,            # 팬 기능 활성화 / Enable pan functionality
    'enable_select': True,         # 선택 기능 활성화 / Enable select/lasso tools
    'auto_resize': True,           # 자동 크기 조정 / Auto resize plots to container
    'responsive': True             # 반응형 / Responsive design for mobile devices
}

# === Real-time Update Configuration ===
# Settings for live updates in the web interface
REALTIME_CONFIG = {
    'update_delay_ms': 300,        # 업데이트 지연 시간 (밀리초) / Update delay (milliseconds) - prevents too frequent updates
    'debounce_enabled': True,      # 디바운싱 활성화 / Enable debouncing (wait for user to stop interacting before updating)
    'max_update_frequency': 5,     # 초당 최대 업데이트 횟수 / Maximum updates per second (rate limiting)
    'enable_live_preview': True    # 라이브 프리뷰 활성화 / Enable live preview of changes as user adjusts parameters
}

# === Directory Scanning Configuration ===
# Settings for optimizing directory scanning performance
SCAN_CONFIG = {
    'max_scan_depth': 2,           # 최대 스캔 깊이 / Maximum directory scan depth (reduces deep recursion)
    'cache_ttl_seconds': 300,       # 캐시 유지 시간 (초) / Cache time-to-live in seconds (prevents repeated scans)
    'max_directories': 5000,         # 최대 스캔 디렉토리 수 / Maximum number of directories to scan (prevents memory overload)
    'scan_timeout_seconds': 100,    # 스캔 타임아웃 (초) / Scan timeout in seconds (prevents hanging)
    'enable_progress_logging': True, # 진행 상황 로깅 활성화 / Enable progress logging for scan operations
    'skip_hidden_dirs': True,      # 숨김 디렉토리 건너뛰기 / Skip hidden directories (names starting with .)
    'early_exit_enabled': True,    # 조기 종료 활성화 / Enable early exit optimization (stop on first data file found)
    'parallel_scanning': True,     # 병렬 스캔 활성화 / Enable parallel directory scanning for faster performance
    'max_scan_threads': 64,         # 최대 스캔 스레드 수 / Maximum number of threads for parallel scanning
    'per_directory_timeout': 5     # 디렉토리당 타임아웃 (초) / Timeout per directory in seconds
}

# === Streaming Data Loading Configuration ===
# Settings for memory-efficient data loading using streaming line processing
STREAMING_CONFIG = {
    'enable_streaming_loading': True,    # 스트리밍 데이터 로딩 활성화 / Enable streaming data loading (reads Nth row/column only)
    'default_downsample_factor': 4,      # 기본 다운샘플링 비율 / Default downsampling factor (1=no downsampling, 2=half, 4=quarter)
}