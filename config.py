#!/usr/bin/env python3
"""
Warpage Analyzer용 설정 구성
Configuration settings for Warpage Analyzer
"""

# 기본 설정 구성 / Default configuration settings
DEFAULT_CONFIG = {
    "base_path": "./data/",                    # 데이터 폴더 기본 경로 / Base path to data folders
    "folders": ["20250716"],                   # 분석할 폴더들 / Folders to analyze
    "vmin": None,                              # 색상 스케일 최솏값 (None = 자동) / Min value for color scale (None = auto)
    "vmax": None,                              # 색상 스케일 최댓값 (None = 자동) / Max value for color scale (None = auto)
    "cmap": "jet",                             # 색상맵 (jet, viridis, plasma 등) / Colormap (jet, viridis, plasma, etc.)
    "colorbar": True,                          # 색상 막대 표시 여부 / Whether to show colorbar
    "row_fraction": 1,                         # 중앙에서 유지할 행 비율 / Fraction of rows to keep in center
    "col_fraction": 1,                         # 중앙에서 유지할 열 비율 / Fraction of columns to keep in center
    "output_filename": "warpage_analysis.pdf", # 출력 PDF 파일명 / Output PDF filename
    "include_stats": True,                     # 통계 분석 그래프 포함 여부 / Include statistical analysis plots
    "include_3d": True,                        # 3D 표면 그래프 포함 여부 / Include 3D surface plots
    "include_advanced": False,                 # 고급 통계 분석 포함 여부 (성능상 기본 비활성화) / Include advanced statistical analysis (disabled by default for performance)
    "dpi": 150,                                # PDF 내보낼 용 DPI / DPI for PDF export
    "show_plots": False,                       # 분석 후 그래프 표시 여부 / Show plots after analysis
    "use_original_files": True                 # 원본 파일(@_ORI.txt) vs 보정된 파일(.txt) 사용 / Use original files (@_ORI.txt) vs corrected files (.txt)
}

# 디렉토리 설정 / Directory settings
DATA_DIR = './data/'     # 데이터 디렉토리 / Data directory
REPORT_DIR = 'report'    # 보고서 디렉토리 / Report directory

# 웹 GUI 설정 / Web GUI settings
WEB_PORT = 8080          # 웹 서버 포트 / Web server port
WEB_HOST = '0.0.0.0'     # 웹 서버 호스트 / Web server host
WEB_DEBUG = True         # 웹 디버그 모드 / Web debug mode

# 파일 패턴 / File patterns
FILE_PATTERNS = {
    'original': '@_ORI.txt',     # 원본 파일 패턴 / Original files pattern
    'corrected': '@.txt'         # 보정된 파일 패턴 (@_ORI.txt 제외) / Corrected files pattern (excluding @_ORI.txt)
}

# 배치 처리 설정 / Batch processing settings
BATCH_CONFIG = {
    'max_files': 100,              # 최대 배치 파일 수 / Maximum batch file count
    'max_file_size_mb': 50,        # 파일당 최대 크기 (MB) / Maximum file size per file (MB)
    'max_total_size_mb': 500,      # 총 최대 크기 (MB) / Maximum total size (MB)
    'parallel_workers': 4,         # 병렬 처리 워커 수 / Number of parallel workers
    'supported_extensions': ['.txt', '.ptr'],  # 지원되는 파일 확장자 / Supported file extensions
    'temp_dir_prefix': 'warpage_batch_'        # 임시 디렉토리 접두사 / Temporary directory prefix
}

# 인터랙티브 플롯 설정 / Interactive plot settings
PLOTLY_CONFIG = {
    'default_colorscale': 'jet',   # 기본 색상맵 / Default colorscale
    'plot_width': 800,             # 기본 플롯 너비 / Default plot width
    'plot_height': 600,            # 기본 플롯 높이 / Default plot height
    'show_toolbar': True,          # 도구막대 표시 / Show toolbar
    'enable_zoom': True,           # 줌 기능 활성화 / Enable zoom
    'enable_pan': True,            # 팬 기능 활성화 / Enable pan
    'enable_select': True,         # 선택 기능 활성화 / Enable select
    'auto_resize': True,           # 자동 크기 조정 / Auto resize
    'responsive': True             # 반응형 / Responsive
}

# 실시간 업데이트 설정 / Real-time update settings
REALTIME_CONFIG = {
    'update_delay_ms': 300,        # 업데이트 지연 시간 (밀리초) / Update delay (milliseconds)
    'debounce_enabled': True,      # 디바운싱 활성화 / Enable debouncing
    'max_update_frequency': 5,     # 초당 최대 업데이트 횟수 / Maximum updates per second
    'enable_live_preview': True    # 라이브 프리뷰 활성화 / Enable live preview
} 