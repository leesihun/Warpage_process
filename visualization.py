#!/usr/bin/env python3
"""
Warpage Analyzer용 시각화 함수들
Visualization functions for Warpage Analyzer
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import base64
import io
# Import Plotly for interactive visualizations
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio
# 고급 통계 함수들 가져오기 / Import advanced statistics functions
try:
    from advanced_statistics import ADVANCED_PLOT_FUNCTIONS
except ImportError:
    ADVANCED_PLOT_FUNCTIONS = {}


def figure_to_base64(fig):
    """
    Convert a matplotlib figure to a base64-encoded string.
    
    Args:
        fig (matplotlib.figure.Figure): The figure to convert
        
    Returns:
        str: Base64-encoded PNG image
    """
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close(fig)  # Clean up the figure to prevent memory leaks
    
    graphic = base64.b64encode(image_png)
    return graphic.decode('utf-8')


def get_readable_x_axis_ticks(x_pos, labels, max_labels=10):
    """
    Get readable x-axis tick positions and labels by selecting a subset when there are too many.
    
    Args:
        x_pos (array): X-axis positions (e.g., np.arange(len(data)))
        labels (list): All labels corresponding to x_pos
        max_labels (int): Maximum number of labels to show
        
    Returns:
        tuple: (selected_x_positions, selected_labels)
    """
    if len(labels) <= max_labels:
        # If we have few enough labels, show them all
        return x_pos, labels
    else:
        # Calculate step size to show approximately max_labels
        step = max(1, len(labels) // max_labels)
        # Select every nth position and label
        selected_indices = range(0, len(labels), step)
        selected_x_pos = x_pos[selected_indices]
        selected_labels = [labels[i] for i in selected_indices]
        return selected_x_pos, selected_labels


def create_comparison_plot(folder_data, figsize=(11.69, 8.27), vmin=None, vmax=None, cmap='jet', colorbar=True):
    """
    Create a comparison plot showing all files in 4x4 grid configuration.
    
    Args:
        folder_data (dict): Dictionary with file_id as key and (data, stats, filename) as value
        figsize (tuple): Figure size (width, height)
        vmin, vmax (float): Color scale limits
        cmap (str): Colormap name
        colorbar (bool): Whether to show colorbar
        
    Returns:
        list: List of matplotlib figures (one or more pages)
    """
    files = list(folder_data.items())
    n_files = len(files)
    files_per_page = 16  # 4x4 format
    
    figures = []
    
    # Find consistent axis limits for all subplots
    all_shapes = [data.shape for _, (data, stats, filename) in files if data is not None]
    if all_shapes:
        max_rows = max(shape[0] for shape in all_shapes)
        max_cols = max(shape[1] for shape in all_shapes)
    else:
        max_rows, max_cols = 100, 100  # Default fallback
    
    # Process files in chunks of 16 (4x4 per page)
    for page_start in range(0, n_files, files_per_page):
        page_end = min(page_start + files_per_page, n_files)
        page_files = files[page_start:page_end]
        n_page_files = len(page_files)
        
        # Create 4x4 subplot layout
        fig, axes = plt.subplots(4, 4, figsize=figsize)
        fig.suptitle('Warpage Data Comparison', fontsize=16, fontweight='bold')
        axes = axes.flatten()  # Flatten for easy indexing
        
        for i, (file_id, (data, stats, filename)) in enumerate(page_files):
            if data is not None:
                ax = axes[i]
                im = ax.imshow(data, cmap=cmap, vmin=vmin, vmax=vmax)
                
                # Simplify file ID to just number
                simple_file_id = file_id.replace('File_', '')
                ax.set_title(f'{simple_file_id}\n{filename}', fontsize=8, fontweight='bold')
                ax.set_aspect('equal')
                
                # Set consistent axis limits
                ax.set_xlim(0, max_cols)
                ax.set_ylim(max_rows, 0)  # Inverted y-axis for image display
                
                # Remove tick labels for cleaner look
                ax.set_xticks([])
                ax.set_yticks([])
                
                # Add statistics text (smaller for 4x4 grid)
                stats_text = f"Min: {stats['min']:.3f}\nMax: {stats['max']:.3f}\nMean: {stats['mean']:.3f}"
                ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=6,
                        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # Hide unused subplots
        for j in range(n_page_files, 16):
            axes[j].set_visible(False)
        
        # Add colorbar if requested (only one for the entire figure)
        if colorbar and n_page_files > 0:
            fig.colorbar(im, ax=[ax for ax in axes[:n_page_files]], shrink=0.6, label='Warpage Value')
        
        plt.tight_layout()
        figures.append(fig)
    
    return figures


def create_comprehensive_advanced_analysis(folder_data, figsize=(8.27, 11.69)):
    """
    종합 고급 분석 보고서 생성 / Create comprehensive advanced analysis report
    
    Args:
        folder_data (dict): 파일 데이터 / File data
        figsize (tuple): 그래프 크기 / Figure size
        
    Returns:
        list: 고급 분석 그래프들의 목록 / List of advanced analysis figures
    """
    figures = []
    
    # 고급 분석 그래프들 생성 (성능을 위해 핵심 분석만 선택) / Generate essential advanced analysis plots for performance
    plot_configs = [
        ('violin_plots', 'Distribution Analysis - Violin Plots'),
        ('percentile_analysis', 'Percentile Analysis'),
        ('gradient_analysis', 'Spatial Gradient Analysis')
    ]
    
    for plot_key, plot_title in plot_configs:
        if plot_key in ADVANCED_PLOT_FUNCTIONS:
            try:
                fig = ADVANCED_PLOT_FUNCTIONS[plot_key](folder_data)
                if fig:
                    figures.append((fig, plot_title))
                    print(f"  OK Generated: {plot_title}")
            except Exception as e:
                print(f"  WARNING: Failed to generate {plot_title}: {e}")
    
    return figures


def create_individual_plot(file_id, data, stats, filename, figsize=(8.27, 11.69), vmin=None, vmax=None, cmap='jet', colorbar=True):
    """
    Create an individual plot for a single file with consistent scaling.
    
    Args:
        file_id (str): File identifier
        data (numpy.ndarray): Data array
        stats (dict): Statistics dictionary
        filename (str): Filename for title
        figsize (tuple): Figure size
        vmin, vmax (float): Color scale limits
        cmap (str): Colormap name
        colorbar (bool): Whether to show colorbar
        
    Returns:
        matplotlib.figure.Figure: The created figure
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Handle NaN values in visualization
    data_for_plot = np.ma.masked_invalid(data)
    im = ax.imshow(data_for_plot, cmap=cmap, vmin=vmin, vmax=vmax)
    # Simplify file ID to just number
    simple_file_id = file_id.replace('File_', '')
    ax.set_title(f'{simple_file_id} - {filename}', fontweight='bold', fontsize=12)
    ax.set_aspect('equal')
    
    # Set consistent axis scaling
    ax.set_xlim(0, data.shape[1])
    ax.set_ylim(data.shape[0], 0)  # Inverted y-axis for image display
    
    # Remove tick labels for cleaner look
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Add colorbar if requested
    if colorbar:
        cbar = fig.colorbar(im, ax=ax, shrink=0.5)  # Make colorbar shorter
        cbar.set_label('Warpage Value', fontsize=10)
        
        # Add statistics text above the colorbar
        stats_text = f"Shape: {stats['shape']}\nMin: {stats['min']:.6f}\nMax: {stats['max']:.6f}\nMean: {stats['mean']:.6f}\nStd: {stats['std']:.6f}"
        cbar.ax.text(0.5, 1.1, stats_text, transform=cbar.ax.transAxes, 
                    verticalalignment='bottom', horizontalalignment='center',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.9), fontsize=9)
    
    plt.tight_layout(pad=0.5)
    return fig


def create_3d_surface_plot(folder_data, figsize=(11.69, 8.27)):
    """
    Create 3D surface plots for all files.
    
    Args:
        folder_data (dict): Dictionary with file_id as key and (data, stats, filename) as value
        figsize (tuple): Figure size
        
    Returns:
        matplotlib.figure.Figure: The created figure
    """
    fig = plt.figure(figsize=figsize)
    fig.suptitle('3D Surface Plots - Warpage Data', fontsize=16, fontweight='bold')
    
    # Dynamically calculate plot positions based on number of files
    n_files = len(folder_data)
    n_cols = min(4, n_files)  # Max 4 columns
    n_rows = (n_files + n_cols - 1) // n_cols  # Calculate rows needed
    
    for i, (file_id, (data, stats, filename)) in enumerate(folder_data.items()):
        if data is not None and i < 16:  # Limit to 16 plots to avoid overcrowding
            ax = fig.add_subplot(n_rows, n_cols, i + 1, projection='3d')
            
            # Create coordinate meshes
            rows, cols = data.shape
            x = np.arange(cols)
            y = np.arange(rows)
            X, Y = np.meshgrid(x, y)
            
            # Create surface plot
            surf = ax.plot_surface(X, Y, data, cmap='viridis', alpha=0.8)
            
            # Simplify file ID to just number
            simple_file_id = file_id.replace('File_', '')
            ax.set_title(f'{simple_file_id}\n{filename}', fontweight='bold', fontsize=10)
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Warpage')
            
            # Add colorbar
            fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)
    
    plt.tight_layout()
    return fig


def create_statistical_comparison_plots(folder_data, figsize=(8.27, 11.69)):
    """
    분포 포함 종합 통계 비교 그래프 생성
    Create comprehensive statistical comparison plots including warpage distribution.
    
    Args:
        folder_data (dict): 파일 ID를 키로 하고 (data, stats, filename)를 값으로 하는 딕셔너리
                           Dictionary with file_id as key and (data, stats, filename) as value
        figsize (tuple): 그래프 크기 / Figure size
        
    Returns:
        matplotlib.figure.Figure: 생성된 그래프 / The created figure
    """
    fig = plt.figure(figsize=figsize)
    fig.suptitle('Statistical Comparison - Warpage Analysis', fontsize=16, fontweight='bold', y=0.98)
    
    # 다른 통계 분석을 위한 서브플롯 생성 / Create subplots for different statistical analyses
    gs = fig.add_gridspec(2, 2, hspace=0.35, wspace=0.3, top=0.92, bottom=0.08, left=0.08, right=0.95)
    
    # 파일 ID를 숫자로 단순화 / Simplify file IDs to just numbers
    file_ids = list(folder_data.keys())
    simple_file_ids = [fid.replace('File_', '') for fid in file_ids]
    
    # 데이터 추출 / Extract data
    means = [stats['mean'] for _, (_, stats, _) in folder_data.items()]
    stds = [stats['std'] for _, (_, stats, _) in folder_data.items()]
    ranges = [stats['range'] for _, (_, stats, _) in folder_data.items()]
    mins = [stats['min'] for _, (_, stats, _) in folder_data.items()]
    maxs = [stats['max'] for _, (_, stats, _) in folder_data.items()]
    x_pos = np.arange(len(means))
    
    # 1. Mean Warpage Values with Standard Deviation
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.bar(x_pos, means, yerr=stds, capsize=5, alpha=0.7, color='skyblue', edgecolor='navy', linewidth=0.8)
    ax1.set_xlabel('Files', fontsize=11)
    ax1.set_ylabel('Mean Warpage Value', fontsize=11)
    ax1.set_title('Mean Warpage Values with Std Dev', fontsize=12, fontweight='bold')
    # Use smart x-axis tick selection for readability
    selected_x_pos, selected_labels = get_readable_x_axis_ticks(x_pos, simple_file_ids)
    ax1.set_xticks(selected_x_pos)
    ax1.set_xticklabels(selected_labels, rotation=45, ha='right', fontsize=10)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.tick_params(axis='both', which='major', labelsize=10)
    
    # 2. Range Comparison
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.bar(x_pos, ranges, alpha=0.7, color='orange', edgecolor='darkorange', linewidth=0.8)
    ax2.set_xlabel('Files', fontsize=11)
    ax2.set_ylabel('Warpage Range', fontsize=11)
    ax2.set_title('Warpage Range Comparison', fontsize=12, fontweight='bold')
    # Use smart x-axis tick selection for readability
    selected_x_pos, selected_labels = get_readable_x_axis_ticks(x_pos, simple_file_ids)
    ax2.set_xticks(selected_x_pos)
    ax2.set_xticklabels(selected_labels, rotation=45, ha='right', fontsize=10)
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.tick_params(axis='both', which='major', labelsize=10)
    
    # 3. Min-Max Comparison
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.plot(x_pos, mins, 'o-', label='Min', color='red', alpha=0.8, linewidth=2, markersize=6)
    ax3.plot(x_pos, maxs, 's-', label='Max', color='blue', alpha=0.8, linewidth=2, markersize=6)
    ax3.fill_between(x_pos, mins, maxs, alpha=0.2, color='gray')
    ax3.set_xlabel('Files', fontsize=11)
    ax3.set_ylabel('Warpage Value', fontsize=11)
    ax3.set_title('Min-Max Warpage Values', fontsize=12, fontweight='bold')
    # Use smart x-axis tick selection for readability
    selected_x_pos, selected_labels = get_readable_x_axis_ticks(x_pos, simple_file_ids)
    ax3.set_xticks(selected_x_pos)
    ax3.set_xticklabels(selected_labels, rotation=45, ha='right', fontsize=10)
    ax3.legend(fontsize=10, loc='best')
    ax3.grid(True, alpha=0.3, linestyle='--')
    ax3.tick_params(axis='both', which='major', labelsize=10)
    
    # 4. Standard Deviation Analysis
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.bar(x_pos, stds, alpha=0.7, color='green', edgecolor='darkgreen', linewidth=0.8)
    ax4.set_xlabel('Files', fontsize=11)
    ax4.set_ylabel('Standard Deviation', fontsize=11)
    ax4.set_title('Standard Deviation Comparison', fontsize=12, fontweight='bold')
    # Use smart x-axis tick selection for readability
    selected_x_pos, selected_labels = get_readable_x_axis_ticks(x_pos, simple_file_ids)
    ax4.set_xticks(selected_x_pos)
    ax4.set_xticklabels(selected_labels, rotation=45, ha='right', fontsize=10)
    ax4.grid(True, alpha=0.3, linestyle='--')
    ax4.tick_params(axis='both', which='major', labelsize=10)
    
    # 자동 레이아웃 조정 제거하고 수동 설정 사용
    # Don't use plt.tight_layout() as we've manually set the gridspec
    return fig 


def create_mean_comparison_plot(folder_data, figsize=(11.69, 8.27)):
    """
    Create a single plot showing mean warpage values with standard deviation.
    
    Args:
        folder_data (dict): Dictionary with file_id as key and (data, stats, filename) as value
        figsize (tuple): Figure size
        
    Returns:
        matplotlib.figure.Figure: The created figure
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Simplify file IDs to just numbers
    file_ids = list(folder_data.keys())
    simple_file_ids = [fid.replace('File_', '') for fid in file_ids]
    
    means = [stats['mean'] for _, (_, stats, _) in folder_data.items()]
    stds = [stats['std'] for _, (_, stats, _) in folder_data.items()]
    
    x_pos = np.arange(len(means))
    ax.bar(x_pos, means, yerr=stds, capsize=5, alpha=0.7, color='skyblue')
    ax.set_xlabel('Files', fontsize=12)
    ax.set_ylabel('Mean Warpage Value', fontsize=12)
    ax.set_title('Mean Warpage Values with Standard Deviation', fontsize=14, fontweight='bold')
    # Use smart x-axis tick selection for readability
    selected_x_pos, selected_labels = get_readable_x_axis_ticks(x_pos, simple_file_ids)
    ax.set_xticks(selected_x_pos)
    ax.set_xticklabels(selected_labels, rotation=45, ha='right', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis='both', which='major', labelsize=10)
    
    plt.tight_layout()
    return fig


def create_range_comparison_plot(folder_data, figsize=(11.69, 8.27)):
    """
    Create a single plot showing warpage range comparison.
    
    Args:
        folder_data (dict): Dictionary with file_id as key and (data, stats, filename) as value
        figsize (tuple): Figure size
        
    Returns:
        matplotlib.figure.Figure: The created figure
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Simplify file IDs to just numbers
    file_ids = list(folder_data.keys())
    simple_file_ids = [fid.replace('File_', '') for fid in file_ids]
    
    ranges = [stats['range'] for _, (_, stats, _) in folder_data.items()]
    
    x_pos = np.arange(len(ranges))
    ax.bar(x_pos, ranges, alpha=0.7, color='orange')
    ax.set_xlabel('Files', fontsize=12)
    ax.set_ylabel('Warpage Range', fontsize=12)
    ax.set_title('Warpage Range Comparison', fontsize=14, fontweight='bold')
    # Use smart x-axis tick selection for readability
    selected_x_pos, selected_labels = get_readable_x_axis_ticks(x_pos, simple_file_ids)
    ax.set_xticks(selected_x_pos)
    ax.set_xticklabels(selected_labels, rotation=45, ha='right', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis='both', which='major', labelsize=10)
    
    plt.tight_layout()
    return fig


def create_minmax_comparison_plot(folder_data, figsize=(11.69, 8.27)):
    """
    Create a single plot showing min-max warpage values.
    
    Args:
        folder_data (dict): Dictionary with file_id as key and (data, stats, filename) as value
        figsize (tuple): Figure size
        
    Returns:
        matplotlib.figure.Figure: The created figure
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Simplify file IDs to just numbers
    file_ids = list(folder_data.keys())
    simple_file_ids = [fid.replace('File_', '') for fid in file_ids]
    
    mins = [stats['min'] for _, (_, stats, _) in folder_data.items()]
    maxs = [stats['max'] for _, (_, stats, _) in folder_data.items()]
    
    x_pos = np.arange(len(mins))
    ax.plot(x_pos, mins, 'o-', label='Min', color='red', alpha=0.7, linewidth=2, markersize=8)
    ax.plot(x_pos, maxs, 's-', label='Max', color='blue', alpha=0.7, linewidth=2, markersize=8)
    ax.fill_between(x_pos, mins, maxs, alpha=0.2, color='gray')
    ax.set_xlabel('Files', fontsize=12)
    ax.set_ylabel('Warpage Value', fontsize=12)
    ax.set_title('Min-Max Warpage Values', fontsize=14, fontweight='bold')
    # Use smart x-axis tick selection for readability
    selected_x_pos, selected_labels = get_readable_x_axis_ticks(x_pos, simple_file_ids)
    ax.set_xticks(selected_x_pos)
    ax.set_xticklabels(selected_labels, rotation=45, ha='right', fontsize=10)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis='both', which='major', labelsize=10)
    
    plt.tight_layout()
    return fig


def create_std_comparison_plot(folder_data, figsize=(11.69, 8.27)):
    """
    Create a single plot showing standard deviation comparison.
    
    Args:
        folder_data (dict): Dictionary with file_id as key and (data, stats, filename) as value
        figsize (tuple): Figure size
        
    Returns:
        matplotlib.figure.Figure: The created figure
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Simplify file IDs to just numbers
    file_ids = list(folder_data.keys())
    simple_file_ids = [fid.replace('File_', '') for fid in file_ids]
    
    stds = [stats['std'] for _, (_, stats, _) in folder_data.items()]
    
    x_pos = np.arange(len(stds))
    ax.bar(x_pos, stds, alpha=0.7, color='green')
    ax.set_xlabel('Files', fontsize=12)
    ax.set_ylabel('Standard Deviation', fontsize=12)
    ax.set_title('Standard Deviation Comparison', fontsize=14, fontweight='bold')
    # Use smart x-axis tick selection for readability
    selected_x_pos, selected_labels = get_readable_x_axis_ticks(x_pos, simple_file_ids)
    ax.set_xticks(selected_x_pos)
    ax.set_xticklabels(selected_labels, rotation=45, ha='right', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis='both', which='major', labelsize=10)
    
    plt.tight_layout()
    return fig


def create_warpage_distribution_plot(folder_data, figsize=(11.69, 8.27)):
    """
    워페이지 매개변수 분포 그래프 생성 (max-min 값들의 히스토그램)
    Create a warpage distribution plot showing histogram of (max-min) values.
    X축: (Max - Min) 워페이지 값 / X-axis: (Max - Min) Warpage Value
    Y축: 확률/빈도 / Y-axis: Probability/Frequency
    
    Args:
        folder_data (dict): 파일 ID를 키로 하고 (data, stats, filename)를 값으로 하는 딕셔너리
                           Dictionary with file_id as key and (data, stats, filename) as value
        figsize (tuple): 그래프 크기 / Figure size
        
    Returns:
        matplotlib.figure.Figure: 생성된 그래프 / The created figure
    """
    fig, ax = plt.subplots(figsize=figsize)
    fig.suptitle('Warpage Range Distribution', fontsize=16, fontweight='bold')
    
    # 각 파일에 대해 (max-min) 값 계산 / Calculate (max-min) values for each file
    max_min_values = []
    for file_id, (data, stats, filename) in folder_data.items():
        max_min_diff = stats['max'] - stats['min']
        max_min_values.append(max_min_diff)
    
    if max_min_values:
        # Create histogram of (max-min) values
        ax.hist(max_min_values, bins=min(10, len(max_min_values)), alpha=0.7, 
               color='purple', edgecolor='black', linewidth=1, density=True)
        
        # Add mean line
        mean_value = np.mean(max_min_values)
        ax.axvline(mean_value, color='red', linestyle='--', linewidth=2, 
                  label=f'Mean: {mean_value:.1f}')
        
        # Add statistics text
        std_value = np.std(max_min_values)
        min_value = np.min(max_min_values)
        max_value = np.max(max_min_values)
        
        stats_text = f'Mean: {mean_value:.1f}\nStd: {std_value:.1f}\nMin: {min_value:.1f}\nMax: {max_value:.1f}'
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.legend(fontsize=10)
    
    ax.set_xlabel('(Max - Min) Warpage Value', fontsize=12)
    ax.set_ylabel('Probability Density', fontsize=12)
    ax.set_title('Warpage Range Distribution', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis='both', which='major', labelsize=10)
    
    plt.tight_layout()
    return fig


def create_mean_range_combined_plot(folder_data, figsize=(8.27, 11.69)):
    """
    평균 및 범위 비교를 위아래 구성으로 보여주는 결합 그래프 생성
    Create a combined plot showing mean and range comparisons in up-down configuration.
    
    Args:
        folder_data (dict): 파일 ID를 키로 하고 (data, stats, filename)를 값으로 하는 딕셔너리
                           Dictionary with file_id as key and (data, stats, filename) as value
        figsize (tuple): 그래프 크기 / Figure size
        
    Returns:
        matplotlib.figure.Figure: 생성된 그래프 / The created figure
    """
    fig = plt.figure(figsize=figsize)
    fig.suptitle('Statistical Comparison - Mean and Range', fontsize=16, fontweight='bold')
    
    # 두 개의 서브플롯 생성 / Create two subplots
    ax1 = plt.subplot(2, 1, 1)
    ax2 = plt.subplot(2, 1, 2)
    
    # Simplify file IDs to just numbers
    file_ids = list(folder_data.keys())
    simple_file_ids = [fid.replace('File_', '') for fid in file_ids]
    
    x_pos = np.arange(len(file_ids))
    
    # Top plot: Mean comparison
    means = [stats['mean'] for _, (_, stats, _) in folder_data.items()]
    stds = [stats['std'] for _, (_, stats, _) in folder_data.items()]
    
    ax1.bar(x_pos, means, yerr=stds, capsize=5, alpha=0.7, color='skyblue')
    ax1.set_xlabel('Files', fontsize=12)
    ax1.set_ylabel('Mean Warpage Value', fontsize=12)
    ax1.set_title('Mean Warpage Values with Standard Deviation', fontsize=14, fontweight='bold')
    # Use smart x-axis tick selection for readability
    selected_x_pos, selected_labels = get_readable_x_axis_ticks(x_pos, simple_file_ids)
    ax1.set_xticks(selected_x_pos)
    ax1.set_xticklabels(selected_labels, rotation=45, ha='right', fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='both', which='major', labelsize=10)
    
    # Bottom plot: Range comparison
    ranges = [stats['range'] for _, (_, stats, _) in folder_data.items()]
    ax2.bar(x_pos, ranges, alpha=0.7, color='orange')
    ax2.set_xlabel('Files', fontsize=12)
    ax2.set_ylabel('Warpage Range', fontsize=12)
    ax2.set_title('Warpage Range Comparison', fontsize=14, fontweight='bold')
    # Use smart x-axis tick selection for readability
    selected_x_pos, selected_labels = get_readable_x_axis_ticks(x_pos, simple_file_ids)
    ax2.set_xticks(selected_x_pos)
    ax2.set_xticklabels(selected_labels, rotation=45, ha='right', fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='both', which='major', labelsize=10)
    
    plt.tight_layout()
    return fig


def create_minmax_std_combined_plot(folder_data, figsize=(8.27, 11.69)):
    """
    최소-최대 및 표준편차 비교를 위아래 구성으로 보여주는 결합 그래프 생성
    Create a combined plot showing min-max and standard deviation comparisons in up-down configuration.
    
    Args:
        folder_data (dict): 파일 ID를 키로 하고 (data, stats, filename)를 값으로 하는 딕셔너리
                           Dictionary with file_id as key and (data, stats, filename) as value
        figsize (tuple): 그래프 크기 / Figure size
        
    Returns:
        matplotlib.figure.Figure: 생성된 그래프 / The created figure
    """
    fig = plt.figure(figsize=figsize)
    fig.suptitle('Statistical Comparison - Min-Max and Standard Deviation', fontsize=16, fontweight='bold')
    
    # 두 개의 서브플롯 생성 / Create two subplots
    ax1 = plt.subplot(2, 1, 1)
    ax2 = plt.subplot(2, 1, 2)
    
    # Simplify file IDs to just numbers
    file_ids = list(folder_data.keys())
    simple_file_ids = [fid.replace('File_', '') for fid in file_ids]
    
    x_pos = np.arange(len(file_ids))
    
    # Top plot: Min-Max comparison
    mins = [stats['min'] for _, (_, stats, _) in folder_data.items()]
    maxs = [stats['max'] for _, (_, stats, _) in folder_data.items()]
    
    ax1.plot(x_pos, mins, 'o-', label='Min', color='red', alpha=0.7, linewidth=2, markersize=8)
    ax1.plot(x_pos, maxs, 's-', label='Max', color='blue', alpha=0.7, linewidth=2, markersize=8)
    ax1.fill_between(x_pos, mins, maxs, alpha=0.2, color='gray')
    ax1.set_xlabel('Files', fontsize=12)
    ax1.set_ylabel('Warpage Value', fontsize=12)
    ax1.set_title('Min-Max Warpage Values', fontsize=14, fontweight='bold')
    # Use smart x-axis tick selection for readability
    selected_x_pos, selected_labels = get_readable_x_axis_ticks(x_pos, simple_file_ids)
    ax1.set_xticks(selected_x_pos)
    ax1.set_xticklabels(selected_labels, rotation=45, ha='right', fontsize=10)
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='both', which='major', labelsize=10)
    
    # Bottom plot: Standard deviation comparison
    stds = [stats['std'] for _, (_, stats, _) in folder_data.items()]
    ax2.bar(x_pos, stds, alpha=0.7, color='green')
    ax2.set_xlabel('Files', fontsize=12)
    ax2.set_ylabel('Standard Deviation', fontsize=12)
    ax2.set_title('Standard Deviation Comparison', fontsize=14, fontweight='bold')
    # Use smart x-axis tick selection for readability
    selected_x_pos, selected_labels = get_readable_x_axis_ticks(x_pos, simple_file_ids)
    ax2.set_xticks(selected_x_pos)
    ax2.set_xticklabels(selected_labels, rotation=45, ha='right', fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='both', which='major', labelsize=10)
    
    plt.tight_layout()
    return fig


def create_web_gui_statistical_plots(folder_data, figsize=(8.27, 11.69)):
    """
    Create statistical plots for web GUI that match the PDF export layout.
    Shows all statistical analyses in a single figure with 3 sections.
    
    Args:
        folder_data (dict): Dictionary with file_id as key and (data, stats, filename) as value
        figsize (tuple): Figure size
        
    Returns:
        matplotlib.figure.Figure: The created figure
    """
    fig = plt.figure(figsize=figsize)
    fig.suptitle('Statistical Analysis - Warpage Comparison', fontsize=16, fontweight='bold')
    
    # Simplify file IDs to just numbers
    file_ids = list(folder_data.keys())
    simple_file_ids = [fid.replace('File_', '') for fid in file_ids]
    
    x_pos = np.arange(len(file_ids))
    
    # 1. Mean comparison (top)
    ax1 = plt.subplot(3, 1, 1)
    means = [stats['mean'] for _, (_, stats, _) in folder_data.items()]
    stds = [stats['std'] for _, (_, stats, _) in folder_data.items()]
    
    ax1.bar(x_pos, means, yerr=stds, capsize=5, alpha=0.7, color='skyblue')
    ax1.set_xlabel('Files', fontsize=12)
    ax1.set_ylabel('Mean Warpage Value', fontsize=12)
    ax1.set_title('Mean Warpage Values with Standard Deviation', fontsize=14, fontweight='bold')
    # Use smart x-axis tick selection for readability
    selected_x_pos, selected_labels = get_readable_x_axis_ticks(x_pos, simple_file_ids)
    ax1.set_xticks(selected_x_pos)
    ax1.set_xticklabels(selected_labels, rotation=45, ha='right', fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='both', which='major', labelsize=10)
    
    # 2. Range comparison (middle)
    ax2 = plt.subplot(3, 1, 2)
    ranges = [stats['range'] for _, (_, stats, _) in folder_data.items()]
    ax2.bar(x_pos, ranges, alpha=0.7, color='orange')
    ax2.set_xlabel('Files', fontsize=12)
    ax2.set_ylabel('Warpage Range', fontsize=12)
    ax2.set_title('Warpage Range Comparison', fontsize=14, fontweight='bold')
    # Use smart x-axis tick selection for readability
    selected_x_pos, selected_labels = get_readable_x_axis_ticks(x_pos, simple_file_ids)
    ax2.set_xticks(selected_x_pos)
    ax2.set_xticklabels(selected_labels, rotation=45, ha='right', fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='both', which='major', labelsize=10)
    
    # 3. Min-Max comparison (bottom)
    ax3 = plt.subplot(3, 1, 3)
    mins = [stats['min'] for _, (_, stats, _) in folder_data.items()]
    maxs = [stats['max'] for _, (_, stats, _) in folder_data.items()]
    
    ax3.plot(x_pos, mins, 'o-', label='Min', color='red', alpha=0.7, linewidth=2, markersize=8)
    ax3.plot(x_pos, maxs, 's-', label='Max', color='blue', alpha=0.7, linewidth=2, markersize=8)
    ax3.fill_between(x_pos, mins, maxs, alpha=0.2, color='gray')
    ax3.set_xlabel('Files', fontsize=12)
    ax3.set_ylabel('Warpage Value', fontsize=12)
    ax3.set_title('Min-Max Warpage Values', fontsize=14, fontweight='bold')
    # Use smart x-axis tick selection for readability
    selected_x_pos, selected_labels = get_readable_x_axis_ticks(x_pos, simple_file_ids)
    ax3.set_xticks(selected_x_pos)
    ax3.set_xticklabels(selected_labels, rotation=45, ha='right', fontsize=10)
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3)
    ax3.tick_params(axis='both', which='major', labelsize=10)
    
    plt.tight_layout()
    return fig


# ===========================================
# PLOTLY-BASED INTERACTIVE VISUALIZATIONS
# ===========================================

def create_plotly_individual_plot(file_id, data, stats, filename, vmin=None, vmax=None, cmap='jet'):
    """
    Create an interactive individual plot using Plotly.
    
    Args:
        file_id (str): File identifier
        data (numpy.ndarray): Data array
        stats (dict): Statistics dictionary
        filename (str): Filename for title
        vmin, vmax (float): Color scale limits
        cmap (str): Colormap name
        
    Returns:
        plotly.graph_objects.Figure: The created interactive figure
    """
    # Handle NaN values
    data_clean = np.ma.masked_invalid(data)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=data_clean,
        colorscale=cmap,
        zmin=vmin,
        zmax=vmax,
        colorbar=dict(
            title="Warpage Value",
            titleside="right"
        ),
        hoverongaps=False,
        hovertemplate='X: %{x}<br>Y: %{y}<br>Value: %{z:.6f}<extra></extra>'
    ))
    
    simple_file_id = file_id.replace('File_', '')
    fig.update_layout(
        title=f'{simple_file_id} - {filename}',
        xaxis_title='X Position',
        yaxis_title='Y Position',
        width=800,
        height=600,
        font=dict(size=12)
    )
    
    # Add statistics annotation
    stats_text = f"Shape: {stats['shape']}<br>Min: {stats['min']:.6f}<br>Max: {stats['max']:.6f}<br>Mean: {stats['mean']:.6f}<br>Std: {stats['std']:.6f}"
    fig.add_annotation(
        text=stats_text,
        xref="paper", yref="paper",
        x=1.02, y=1,
        showarrow=False,
        align="left",
        bgcolor="white",
        bordercolor="black",
        borderwidth=1
    )
    
    return fig


def create_plotly_comparison_plot(folder_data, vmin=None, vmax=None, cmap='jet'):
    """
    Create an interactive comparison plot using Plotly subplots.
    
    Args:
        folder_data (dict): Dictionary with file_id as key and (data, stats, filename) as value
        vmin, vmax (float): Color scale limits
        cmap (str): Colormap name
        
    Returns:
        plotly.graph_objects.Figure: The created interactive figure
    """
    n_files = len(folder_data)
    if n_files == 0:
        return go.Figure()
    
    # Create subplots
    cols = min(4, n_files)
    rows = (n_files + cols - 1) // cols
    
    subplot_titles = []
    for file_id, (_, _, filename) in folder_data.items():
        simple_file_id = file_id.replace('File_', '')
        subplot_titles.append(f'{simple_file_id}<br>{filename}')
    
    fig = make_subplots(
        rows=rows, cols=cols,
        subplot_titles=subplot_titles,
        shared_xaxes=False,
        shared_yaxes=False,
        horizontal_spacing=0.1,
        vertical_spacing=0.15
    )
    
    for i, (file_id, (data, stats, filename)) in enumerate(folder_data.items()):
        row = i // cols + 1
        col = i % cols + 1
        
        if data is not None:
            data_clean = np.ma.masked_invalid(data)
            
            heatmap = go.Heatmap(
                z=data_clean,
                colorscale=cmap,
                zmin=vmin,
                zmax=vmax,
                showscale=(i == 0),  # Only show colorbar for first plot
                colorbar=dict(
                    title="Warpage Value",
                    x=1.02,
                    len=0.8
                ) if i == 0 else None,
                hoverongaps=False,
                hovertemplate='X: %{x}<br>Y: %{y}<br>Value: %{z:.6f}<extra></extra>'
            )
            
            fig.add_trace(heatmap, row=row, col=col)
    
    fig.update_layout(
        title="Warpage Data Comparison",
        showlegend=False,
        width=1200,
        height=400 * rows,
        font=dict(size=10)
    )
    
    return fig


def create_plotly_3d_surface(folder_data, cmap='viridis'):
    """
    Create interactive 3D surface plots using Plotly.
    
    Args:
        folder_data (dict): Dictionary with file_id as key and (data, stats, filename) as value
        cmap (str): Colormap name
        
    Returns:
        plotly.graph_objects.Figure: The created interactive figure
    """
    n_files = len(folder_data)
    if n_files == 0:
        return go.Figure()
    
    # Create subplots for 3D
    cols = min(2, n_files)
    rows = (n_files + cols - 1) // cols
    
    subplot_titles = []
    for file_id, (_, _, filename) in folder_data.items():
        simple_file_id = file_id.replace('File_', '')
        subplot_titles.append(f'{simple_file_id} - {filename}')
    
    specs = [[{"type": "surface"} for _ in range(cols)] for _ in range(rows)]
    
    fig = make_subplots(
        rows=rows, cols=cols,
        specs=specs,
        subplot_titles=subplot_titles,
        horizontal_spacing=0.05,
        vertical_spacing=0.1
    )
    
    for i, (file_id, (data, stats, filename)) in enumerate(folder_data.items()):
        if i >= 8:  # Limit to 8 plots for performance
            break
            
        row = i // cols + 1
        col = i % cols + 1
        
        if data is not None:
            rows_data, cols_data = data.shape
            x = np.arange(cols_data)
            y = np.arange(rows_data)
            
            surface = go.Surface(
                z=data,
                x=x,
                y=y,
                colorscale=cmap,
                showscale=(i == 0),
                hovertemplate='X: %{x}<br>Y: %{y}<br>Z: %{z:.6f}<extra></extra>'
            )
            
            fig.add_trace(surface, row=row, col=col)
    
    fig.update_layout(
        title="3D Surface Plots - Warpage Data",
        width=1200,
        height=600 * rows,
        font=dict(size=10)
    )
    
    return fig


def create_plotly_statistical_plots(folder_data):
    """
    Create interactive statistical comparison plots using Plotly.
    
    Args:
        folder_data (dict): Dictionary with file_id as key and (data, stats, filename) as value
        
    Returns:
        plotly.graph_objects.Figure: The created interactive figure
    """
    if not folder_data:
        return go.Figure()
    
    # Extract data
    file_ids = list(folder_data.keys())
    simple_file_ids = [fid.replace('File_', '') for fid in file_ids]
    
    means = [stats['mean'] for _, (_, stats, _) in folder_data.items()]
    stds = [stats['std'] for _, (_, stats, _) in folder_data.items()]
    ranges = [stats['range'] for _, (_, stats, _) in folder_data.items()]
    mins = [stats['min'] for _, (_, stats, _) in folder_data.items()]
    maxs = [stats['max'] for _, (_, stats, _) in folder_data.items()]
    
    # Create subplots
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=('Mean Warpage Values with Std Dev', 'Warpage Range Comparison', 'Min-Max Warpage Values'),
        vertical_spacing=0.1
    )
    
    # Mean with error bars
    fig.add_trace(
        go.Bar(
            x=simple_file_ids,
            y=means,
            error_y=dict(type='data', array=stds, visible=True),
            name='Mean ± Std',
            marker_color='skyblue',
            hovertemplate='File: %{x}<br>Mean: %{y:.6f}<br>Std: %{error_y.array:.6f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Range comparison
    fig.add_trace(
        go.Bar(
            x=simple_file_ids,
            y=ranges,
            name='Range',
            marker_color='orange',
            hovertemplate='File: %{x}<br>Range: %{y:.6f}<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Min-Max comparison
    fig.add_trace(
        go.Scatter(
            x=simple_file_ids,
            y=mins,
            mode='lines+markers',
            name='Min',
            line=dict(color='red', width=2),
            marker=dict(size=8),
            hovertemplate='File: %{x}<br>Min: %{y:.6f}<extra></extra>'
        ),
        row=3, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=simple_file_ids,
            y=maxs,
            mode='lines+markers',
            name='Max',
            line=dict(color='blue', width=2),
            marker=dict(size=8, symbol='square'),
            hovertemplate='File: %{x}<br>Max: %{y:.6f}<extra></extra>'
        ),
        row=3, col=1
    )
    
    # Fill between min and max
    fig.add_trace(
        go.Scatter(
            x=simple_file_ids + simple_file_ids[::-1],
            y=mins + maxs[::-1],
            fill='toself',
            fillcolor='rgba(128,128,128,0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            showlegend=False,
            hoverinfo='skip'
        ),
        row=3, col=1
    )
    
    fig.update_layout(
        title="Statistical Analysis - Warpage Comparison",
        width=1000,
        height=1200,
        showlegend=True
    )
    
    # Update axes
    fig.update_xaxes(title_text="Files", row=3, col=1)
    fig.update_yaxes(title_text="Mean Warpage Value", row=1, col=1)
    fig.update_yaxes(title_text="Warpage Range", row=2, col=1)
    fig.update_yaxes(title_text="Warpage Value", row=3, col=1)
    
    return fig


def plotly_to_static_image(fig, width=None, height=None, format='png'):
    """
    Convert Plotly figure to static image for PDF export.
    
    Args:
        fig (plotly.graph_objects.Figure): Plotly figure
        width (int): Image width
        height (int): Image height
        format (str): Image format ('png', 'jpeg', 'svg')
        
    Returns:
        bytes: Image data
    """
    return pio.to_image(fig, format=format, width=width, height=height, engine="kaleido")


def create_plotly_figure_for_pdf(folder_data, plot_type, **kwargs):
    """
    Create Plotly figures optimized for PDF export (static versions).
    
    Args:
        folder_data (dict): Data for plotting
        plot_type (str): Type of plot ('individual', 'comparison', '3d', 'statistics')
        **kwargs: Additional arguments for specific plot types
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure optimized for PDF
    """
    if plot_type == 'individual':
        return create_plotly_individual_plot(folder_data, **kwargs)
    elif plot_type == 'comparison':
        return create_plotly_comparison_plot(folder_data, **kwargs)
    elif plot_type == '3d':
        return create_plotly_3d_surface(folder_data, **kwargs)
    elif plot_type == 'statistics':
        return create_plotly_statistical_plots(folder_data)
    else:
        raise ValueError(f"Unknown plot type: {plot_type}")