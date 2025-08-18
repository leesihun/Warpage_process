#!/usr/bin/env python3
"""
Warpage Analyzer용 메인 분석 함수들
Main analysis functions for Warpage Analyzer
"""

import os
import matplotlib.pyplot as plt
from config import DEFAULT_CONFIG
from data_loader import process_folder_data, get_file_size
from warpage_statistics import find_optimal_color_range, print_statistical_comparison, print_file_information
from visualization import create_comparison_plot
from pdf_exporter import export_to_pdf


def analyze_warpage(config=None):
    """
    설정 가능한 매개변수로 워페이지 데이터를 분석하는 메인 함수
    Main function to analyze warpage data with configurable parameters.
    
    Args:
        config (dict, optional): 분석 매개변수들을 포함한 설정 딕셔너리 / Configuration dictionary with analysis parameters
        
    Returns:
        tuple: (comparison_fig, folder_data) - 비교 그래프와 처리된 데이터 / The comparison figure and processed data
    """
    # Use default config if none provided
    if config is None:
        config = DEFAULT_CONFIG.copy()
    
    # Extract configuration parameters
    base_path = config.get('base_path', DEFAULT_CONFIG['base_path'])
    folders = config.get('folders', DEFAULT_CONFIG['folders'])
    vmin = config.get('vmin', DEFAULT_CONFIG['vmin'])
    vmax = config.get('vmax', DEFAULT_CONFIG['vmax'])
    cmap = config.get('cmap', DEFAULT_CONFIG['cmap'])
    colorbar = config.get('colorbar', DEFAULT_CONFIG['colorbar'])
    row_fraction = config.get('row_fraction', DEFAULT_CONFIG['row_fraction'])
    col_fraction = config.get('col_fraction', DEFAULT_CONFIG['col_fraction'])
    output_filename = config.get('output_filename', DEFAULT_CONFIG['output_filename'])
    include_stats = config.get('include_stats', DEFAULT_CONFIG['include_stats'])
    include_3d = config.get('include_3d', DEFAULT_CONFIG['include_3d'])
    include_advanced = config.get('include_advanced', DEFAULT_CONFIG['include_advanced'])
    dpi = config.get('dpi', DEFAULT_CONFIG['dpi'])
    show_plots = config.get('show_plots', DEFAULT_CONFIG['show_plots'])
    use_original_files = config.get('use_original_files', DEFAULT_CONFIG['use_original_files'])
    
    print("="*80)
    print("WARPAGE DATA ANALYSIS")
    print("="*80)
    
    # 모든 데이터 로드 / Load all data
    print("\n1. Loading data for all folders...")
    folder_data = {}
    file_info = {}
    
    for folder in folders:
        file_results = process_folder_data(base_path, folder, row_fraction, col_fraction, use_original_files)
        if file_results:
            for i, (center_data, stats, filename) in enumerate(file_results, 1):
                # Create simple numeric identifier for each file
                file_id = f"File_{i:02d}"
                folder_data[file_id] = (center_data, stats, filename)
                
                # Get file information
                file_path = os.path.join(base_path, folder, filename)
                file_size = get_file_size(file_path)
                file_info[file_id] = {
                    'folder': folder,
                    'filename': filename,
                    'file_size': file_size,
                    'data_shape': center_data.shape,
                    'display_name': file_id
                }
                
                print(f"   OK {file_id}: {filename} ({file_size})")
        else:
            print(f"   ✗ {folder}: No matching files found")
    
    if not folder_data:
        print("No data found!")
        return None, None
    
    # 전역 색상 범위 찾기 / Find global color range
    print("\n2. Calculating global color range...")
    data_only = {k: v[0] for k, v in folder_data.items()}
    auto_vmin, auto_vmax = find_optimal_color_range(data_only)
    print(f"   Auto-calculated range: {auto_vmin:.6f} to {auto_vmax:.6f}")
    
    # Use user-specified values if provided
    if vmin is None:
        vmin = auto_vmin
    if vmax is None:
        vmax = auto_vmax
    
    print(f"   Using range: {vmin:.6f} to {vmax:.6f}")
    if vmin != auto_vmin or vmax != auto_vmax:
        print(f"   (User-specified min/max values applied)")
    
    print(f"   Using colormap: {cmap}")
    print(f"   Colorbar: {'enabled' if colorbar else 'disabled'}")
    
    # 비교 시각화 생성 / Create comparison visualization
    print("\n3. Creating comparison visualization...")
    comparison_fig = create_comparison_plot(folder_data, figsize=(20, 5), vmin=vmin, vmax=vmax, cmap=cmap, colorbar=colorbar)
    
    # Display file information table
    print_file_information(file_info)
    
    # Display statistical comparison
    print_statistical_comparison(folder_data)
    
    # 비교 PDF 내보내기 / Export comparison PDF
    print("\n6. Exporting comparison PDF...")
    pdf_filename = export_to_pdf(folder_data, output_filename=output_filename,
                               include_stats=include_stats, include_3d=include_3d, include_advanced=include_advanced,
                               dpi=dpi, cmap=cmap, colorbar=colorbar, vmin=vmin, vmax=vmax)
    
    if pdf_filename:
        pdf_size = get_file_size(pdf_filename)
        print(f"   OK Analysis PDF: {pdf_filename} ({pdf_size})")
    
    # Show plots if requested
    if show_plots:
        print("\nDisplaying plots...")
        plt.show()
    else:
        print("\nPlots created but not displayed. Use plt.show() to display them.")
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE!")
    print("="*80)
    
    return comparison_fig, folder_data 