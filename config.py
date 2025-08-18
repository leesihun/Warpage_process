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