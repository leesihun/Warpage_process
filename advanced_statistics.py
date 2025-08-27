#!/usr/bin/env python3
"""
Advanced statistical analysis functions for Warpage Analyzer
고급 통계 분석 함수들
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from datetime import datetime
from scipy.spatial.distance import pdist, squareform
from scipy.ndimage import gaussian_filter, sobel
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import seaborn as sns
from matplotlib.colors import ListedColormap


def calculate_advanced_statistics(data_array):
    """
    고급 통계 지표 계산 / Calculate advanced statistical metrics
    
    Args:
        data_array (numpy.ndarray): 입력 데이터 배열 / Input data array
        
    Returns:
        dict: 고급 통계 지표들 / Advanced statistical measures
    """
    # 유효한 데이터만 사용 / Use only valid data
    valid_data = data_array[~np.isnan(data_array)].flatten()
    
    if len(valid_data) == 0:
        return {}
    
    # 기본 통계 / Basic statistics
    mean_val = np.mean(valid_data)
    std_val = np.std(valid_data)
    
    # 분포 형태 특성 / Distribution shape characteristics
    skewness = stats.skew(valid_data)
    kurtosis_val = stats.kurtosis(valid_data)
    
    # 백분위수 분석 / Percentile analysis
    percentiles = np.percentile(valid_data, [1, 5, 10, 25, 50, 75, 90, 95, 99])
    
    # 공정 능력 지수 (가정: USL=평균+3σ, LSL=평균-3σ) / Process capability indices
    usl = mean_val + 3 * std_val  # Upper Specification Limit
    lsl = mean_val - 3 * std_val  # Lower Specification Limit
    cp = (usl - lsl) / (6 * std_val) if std_val > 0 else 0
    cpk = min((usl - mean_val) / (3 * std_val), (mean_val - lsl) / (3 * std_val)) if std_val > 0 else 0
    
    return {
        'skewness': skewness,
        'kurtosis': kurtosis_val,
        'percentiles': {
            'p1': percentiles[0], 'p5': percentiles[1], 'p10': percentiles[2],
            'p25': percentiles[3], 'p50': percentiles[4], 'p75': percentiles[5],
            'p90': percentiles[6], 'p95': percentiles[7], 'p99': percentiles[8]
        },
        'cp': cp,
        'cpk': cpk,
        'usl': usl,
        'lsl': lsl
    }


def create_violin_plots(folder_data, figsize=(11.69, 8.27)):
    """
    바이올린 플롯으로 분포 시각화 / Violin plots for distribution visualization
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # 데이터 준비 / Prepare data
    data_list = []
    labels = []
    
    for file_id, (data, stats, filename) in folder_data.items():
        valid_data = data[~np.isnan(data)].flatten()
        data_list.append(valid_data)
        labels.append(file_id.replace('File_', ''))
    
    # 바이올린 플롯 생성 / Create violin plot
    parts = ax.violinplot(data_list, positions=range(len(data_list)), showmeans=True, showmedians=True)
    
    # 스타일링 / Styling
    for pc in parts['bodies']:
        pc.set_facecolor('lightblue')
        pc.set_alpha(0.7)
    
    ax.set_xlabel('Files', fontsize=12)
    ax.set_ylabel('Warpage Values', fontsize=12)
    ax.set_title('Warpage Distribution - Violin Plots', fontsize=14, fontweight='bold')
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def create_cdf_plots(folder_data, figsize=(11.69, 8.27)):
    """
    누적분포함수 플롯 - (최대-최소) 워페이지 범위 기준
    Cumulative Distribution Function plots - Based on (max-min) warpage ranges
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Calculate (max-min) range for each file
    range_values = []
    file_labels = []
    
    for file_id, (data, stats, filename) in folder_data.items():
        range_val = stats['max'] - stats['min']
        range_values.append(range_val)
        file_labels.append(file_id.replace('File_', ''))
    
    # Sort ranges for CDF calculation
    sorted_ranges = np.sort(range_values)
    cdf_y = np.arange(1, len(sorted_ranges) + 1) / len(sorted_ranges)
    
    # Plot CDF of ranges
    ax.plot(sorted_ranges, cdf_y, 'o-', linewidth=3, markersize=8, 
            color='blue', label='Warpage Range CDF')
    
    # Add individual points with labels
    for i, (range_val, label) in enumerate(zip(range_values, file_labels)):
        cdf_val = (np.searchsorted(sorted_ranges, range_val) + 1) / len(sorted_ranges)
        ax.plot(range_val, cdf_val, 'ro', markersize=10, alpha=0.7)
        ax.annotate(label, (range_val, cdf_val), 
                   xytext=(5, 5), textcoords='offset points', 
                   fontsize=9, alpha=0.8)
    
    # Add statistics
    mean_range = np.mean(range_values)
    median_range = np.median(range_values)
    ax.axvline(mean_range, color='red', linestyle='--', alpha=0.7, 
               label=f'Mean Range: {mean_range:.2f}')
    ax.axvline(median_range, color='green', linestyle='--', alpha=0.7, 
               label=f'Median Range: {median_range:.2f}')
    
    ax.set_xlabel('(Max - Min) Warpage Value', fontsize=12)
    ax.set_ylabel('Cumulative Probability', fontsize=12)
    ax.set_title('Cumulative Distribution of Warpage Ranges\n(X-axis: Max-Min values across files)', 
                fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    plt.tight_layout()
    return fig




def calculate_spatial_gradients(data_array):
    """
    공간 기울기 계산 / Calculate spatial gradients
    """
    # Sobel 필터로 기울기 계산 / Calculate gradients using Sobel filter
    grad_x = sobel(data_array, axis=1)  # X 방향 기울기 / X-direction gradient
    grad_y = sobel(data_array, axis=0)  # Y 방향 기울기 / Y-direction gradient
    gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
    
    return grad_x, grad_y, gradient_magnitude


def create_gradient_analysis(folder_data, figsize=(11.69, 8.27), vmin=None, vmax=None):
    """
    기울기 크기 분석 시각화 (2x2 형식으로 페이지당 4개 파일)
    Gradient magnitude analysis visualization (2x2 format, 4 files per page)
    """
    files = list(folder_data.items())
    n_files = len(files)
    files_per_page = 4  # 2x2 format
    
    figures = []
    
    # Process files in chunks of 4 (2x2 per page)
    for page_start in range(0, n_files, files_per_page):
        page_end = min(page_start + files_per_page, n_files)
        page_files = files[page_start:page_end]
        n_page_files = len(page_files)
        
        # Create 2x2 subplot layout
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        axes = axes.flatten()  # Flatten for easy indexing
        
        for i, (file_id, (data, stats, filename)) in enumerate(page_files):
            grad_x, grad_y, grad_mag = calculate_spatial_gradients(data)
            
            # Show only gradient magnitude
            ax = axes[i]
            im = ax.imshow(grad_mag, cmap='hot', aspect='equal')
            ax.set_title(f'{file_id.replace("File_", "")} - Gradient Magnitude\n{filename}', 
                        fontsize=10, fontweight='bold')
            
            # Remove ticks for cleaner look
            ax.set_xticks([])
            ax.set_yticks([])
            
            # Add colorbar
            plt.colorbar(im, ax=ax, shrink=0.8)
        
        # Hide unused subplots
        for j in range(n_page_files, 4):
            axes[j].set_visible(False)
        
        plt.tight_layout()
        figures.append(fig)
    
    return figures


def create_contour_plots(folder_data, figsize=(11.69, 8.27)):
    """
    등고선 플롯 생성 (2x2 형식으로 페이지당 4개 파일)
    Create contour plots (2x2 format, 4 files per page)
    """
    files = list(folder_data.items())
    n_files = len(files)
    files_per_page = 4  # 2x2 format
    
    figures = []
    
    # Process files in chunks of 4 (2x2 per page)
    for page_start in range(0, n_files, files_per_page):
        page_end = min(page_start + files_per_page, n_files)
        page_files = files[page_start:page_end]
        n_page_files = len(page_files)
        
        # Create 2x2 subplot layout
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        axes = axes.flatten()  # Flatten for easy indexing
        
        for i, (file_id, (data, stats, filename)) in enumerate(page_files):
            ax = axes[i]
            
            # 등고선 생성 / Create contours
            rows, cols = data.shape
            x = np.arange(cols)
            y = np.arange(rows)
            X, Y = np.meshgrid(x, y)
            
            contour = ax.contour(X, Y, data, levels=15, colors='black', alpha=0.6, linewidths=0.8)
            contourf = ax.contourf(X, Y, data, levels=15, cmap='viridis', alpha=0.8)
            
            ax.set_title(f'{file_id.replace("File_", "")} - Contour\n{filename}', 
                        fontsize=10, fontweight='bold')
            ax.set_aspect('equal')
            
            # Remove ticks for cleaner look
            ax.set_xticks([])
            ax.set_yticks([])
            
            # Add colorbar
            plt.colorbar(contourf, ax=ax, shrink=0.8)
        
        # Hide unused subplots
        for j in range(n_page_files, 4):
            axes[j].set_visible(False)
        
        plt.tight_layout()
        figures.append(fig)
    
    return figures


def create_cross_sectional_profiles(folder_data, figsize=(11.69, 8.27)):
    """
    단면 프로파일 플롯 / Cross-sectional profile plots
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize)
    
    colors = plt.cm.Set1(np.linspace(0, 1, len(folder_data)))
    
    for i, (file_id, (data, stats, filename)) in enumerate(folder_data.items()):
        rows, cols = data.shape
        
        # 중앙 행 프로파일 / Center row profile
        center_row = data[rows // 2, :]
        ax1.plot(center_row, label=file_id.replace('File_', ''), 
                color=colors[i], linewidth=2)
        
        # 중앙 열 프로파일 / Center column profile
        center_col = data[:, cols // 2]
        ax2.plot(center_col, label=file_id.replace('File_', ''), 
                color=colors[i], linewidth=2)
    
    ax1.set_xlabel('X Position', fontsize=12)
    ax1.set_ylabel('Warpage Value', fontsize=12)
    ax1.set_title('Center Row Profile', fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    ax2.set_xlabel('Y Position', fontsize=12)
    ax2.set_ylabel('Warpage Value', fontsize=12)
    ax2.set_title('Center Column Profile', fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    plt.tight_layout()
    return fig


def create_percentile_analysis(folder_data, figsize=(11.69, 8.27)):
    """
    백분위수 분석 시각화 / Percentile analysis visualization
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    file_ids = []
    percentile_data = {
        'p5': [], 'p25': [], 'p50': [], 'p75': [], 'p95': []
    }
    
    for file_id, (data, stats, filename) in folder_data.items():
        valid_data = data[~np.isnan(data)].flatten()
        percentiles = np.percentile(valid_data, [5, 25, 50, 75, 95])
        
        file_ids.append(file_id.replace('File_', ''))
        percentile_data['p5'].append(percentiles[0])
        percentile_data['p25'].append(percentiles[1])
        percentile_data['p50'].append(percentiles[2])
        percentile_data['p75'].append(percentiles[3])
        percentile_data['p95'].append(percentiles[4])
    
    x_pos = np.arange(len(file_ids))
    
    # 백분위수 플롯 / Percentile plots
    ax.plot(x_pos, percentile_data['p5'], 'o-', label='5th percentile', linewidth=2)
    ax.plot(x_pos, percentile_data['p25'], 's-', label='25th percentile', linewidth=2)
    ax.plot(x_pos, percentile_data['p50'], '^-', label='50th percentile (Median)', linewidth=3)
    ax.plot(x_pos, percentile_data['p75'], 'd-', label='75th percentile', linewidth=2)
    ax.plot(x_pos, percentile_data['p95'], 'v-', label='95th percentile', linewidth=2)
    
    ax.fill_between(x_pos, percentile_data['p25'], percentile_data['p75'], alpha=0.3, color='gray', label='IQR')
    
    ax.set_xlabel('Files', fontsize=12)
    ax.set_ylabel('Warpage Value', fontsize=12)
    ax.set_title('Percentile Analysis', fontsize=14, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(file_ids)
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    plt.tight_layout()
    return fig




def create_skewness_kurtosis_analysis(folder_data, figsize=(8.27, 11.69)):
    """
    왜도와 첨도 분석 / Skewness and kurtosis analysis
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize)
    
    file_ids = []
    skewness_values = []
    kurtosis_values = []
    
    for file_id, (data, stats, filename) in folder_data.items():
        advanced_stats = calculate_advanced_statistics(data)
        file_ids.append(file_id.replace('File_', ''))
        skewness_values.append(advanced_stats.get('skewness', 0))
        kurtosis_values.append(advanced_stats.get('kurtosis', 0))
    
    x_pos = np.arange(len(file_ids))
    
    # 왜도 / Skewness
    colors_skew = ['red' if s < 0 else 'blue' if s > 0 else 'gray' for s in skewness_values]
    bars1 = ax1.bar(x_pos, skewness_values, alpha=0.7, color=colors_skew)
    ax1.axhline(y=0, color='black', linestyle='-', alpha=0.5)
    ax1.set_xlabel('Files', fontsize=12)
    ax1.set_ylabel('Skewness', fontsize=12)
    ax1.set_title('Distribution Skewness\n(Negative=Left skewed, Positive=Right skewed)', fontweight='bold')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(file_ids)
    ax1.grid(True, alpha=0.3)
    
    # 첨도 / Kurtosis
    colors_kurt = ['red' if k < 0 else 'blue' if k > 0 else 'gray' for k in kurtosis_values]
    bars2 = ax2.bar(x_pos, kurtosis_values, alpha=0.7, color=colors_kurt)
    ax2.axhline(y=0, color='black', linestyle='-', alpha=0.5)
    ax2.set_xlabel('Files', fontsize=12)
    ax2.set_ylabel('Kurtosis', fontsize=12)
    ax2.set_title('Distribution Kurtosis\n(Negative=Platykurtic, Positive=Leptokurtic)', fontweight='bold')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(file_ids)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def detect_hotspots(data_array, threshold_percentile=95):
    """
    핫스팟 탐지 / Hotspot detection
    """
    threshold = np.percentile(data_array[~np.isnan(data_array)], threshold_percentile)
    hotspots = data_array > threshold
    return hotspots, threshold


def create_hotspot_analysis(folder_data, figsize=(11.69, 8.27), vmin=None, vmax=None):
    """
    Hotspot analysis visualization (2x2 format, 4 files per page)
    Shows hotspots overlay for all files in the dataset
    """
    files = list(folder_data.items())
    n_files = len(files)
    files_per_page = 4  # 2x2 format
    
    figures = []
    
    # Process files in chunks of 4 (2x2 per page)
    for page_start in range(0, n_files, files_per_page):
        page_end = min(page_start + files_per_page, n_files)
        page_files = files[page_start:page_end]
        n_page_files = len(page_files)
        
        # Create 2x2 subplot layout
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        axes = axes.flatten()  # Flatten for easy indexing
        
        for i, (file_id, (data, stats, filename)) in enumerate(page_files):
            # Hotspot overlay
            hotspots, threshold = detect_hotspots(data)
            
            ax = axes[i]
            # Show hotspots over original data
            ax.imshow(data, cmap='viridis', aspect='equal', alpha=0.7, vmin=vmin, vmax=vmax)
            im = ax.imshow(hotspots, cmap='Reds', aspect='equal', alpha=0.5)
            ax.set_title(f'{file_id.replace("File_", "")} - Hotspots (>{threshold:.1f})\n{filename}', 
                        fontsize=10, fontweight='bold')
            
            # Remove ticks for cleaner look
            ax.set_xticks([])
            ax.set_yticks([])
            
            # Add colorbar for hotspots
            plt.colorbar(im, ax=ax, shrink=0.8)
        
        # Hide unused subplots
        for j in range(n_page_files, 4):
            axes[j].set_visible(False)
        
        plt.tight_layout()
        figures.append(fig)
    
    return figures




def create_correlation_analysis(folder_data, figsize=(11.69, 8.27)):
    """
    상관관계 분석 / Correlation analysis
    """
    # 모든 데이터를 플랫화하여 상관관계 매트릭스 생성 / Flatten all data to create correlation matrix
    data_matrix = []
    file_ids = []
    min_samples = float('inf')
    
    # First pass: collect data and find minimum sample size
    temp_data = []
    for file_id, (data, stats, filename) in folder_data.items():
        flattened = data[~np.isnan(data)].flatten()
        temp_data.append(flattened)
        file_ids.append(file_id.replace('File_', ''))
        min_samples = min(min_samples, len(flattened))
    
    # Second pass: ensure all arrays have same length (minimum available)
    target_samples = min(min_samples, 1000)  # Use max 1000 points or minimum available
    
    for flattened in temp_data:
        if len(flattened) >= target_samples:
            # Randomly sample target_samples points
            indices = np.random.choice(len(flattened), target_samples, replace=False)
            sampled_data = flattened[indices]
        else:
            # If somehow we have fewer points, pad with the mean
            sampled_data = np.pad(flattened, (0, target_samples - len(flattened)), 
                                mode='constant', constant_values=np.mean(flattened))
        data_matrix.append(sampled_data)
    
    # 상관관계 매트릭스 계산 / Calculate correlation matrix
    correlation_matrix = np.corrcoef(data_matrix)
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # 히트맵 생성 / Create heatmap
    im = ax.imshow(correlation_matrix, cmap='RdBu', aspect='equal', vmin=-1, vmax=1)
    
    # 축 라벨 / Axis labels
    ax.set_xticks(np.arange(len(file_ids)))
    ax.set_yticks(np.arange(len(file_ids)))
    ax.set_xticklabels(file_ids)
    ax.set_yticklabels(file_ids)
    
    # 상관계수 값 표시 / Display correlation values
    for i in range(len(file_ids)):
        for j in range(len(file_ids)):
            text = ax.text(j, i, f'{correlation_matrix[i, j]:.2f}',
                          ha="center", va="center", color="black" if abs(correlation_matrix[i, j]) < 0.5 else "white")
    
    ax.set_title('Correlation Matrix Between Files', fontsize=14, fontweight='bold')
    
    # Add horizontal colorbar
    cbar = plt.colorbar(im, ax=ax, orientation='horizontal', pad=0.1, shrink=0.8)
    cbar.set_label('Correlation Coefficient', fontsize=12)
    
    plt.tight_layout()
    return fig


def perform_pca_analysis(folder_data):
    """
    주성분 분석 수행 / Perform PCA analysis
    """
    # 데이터 준비 / Prepare data
    data_matrix = []
    file_ids = []
    
    for file_id, (data, stats, filename) in folder_data.items():
        flattened = data[~np.isnan(data)].flatten()
        # 리샘플링 / Resampling
        if len(flattened) > 500:
            indices = np.random.choice(len(flattened), 500, replace=False)
            flattened = flattened[indices]
        data_matrix.append(flattened[:500])
        file_ids.append(file_id.replace('File_', ''))
    
    # 데이터 표준화 / Standardize data
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(data_matrix)
    
    # PCA 수행 / Perform PCA
    pca = PCA()
    pca_result = pca.fit_transform(data_scaled)
    
    return pca, pca_result, file_ids


def create_pca_visualization(folder_data, figsize=(8.27, 11.69)):
    """
    주성분 분석 시각화 / PCA visualization
    """
    pca, pca_result, file_ids = perform_pca_analysis(folder_data)
    
    fig, axes = plt.subplots(3, 1, figsize=figsize)
    
    # 1. 설명된 분산 비율 / Explained variance ratio
    axes[0].bar(range(len(pca.explained_variance_ratio_)), pca.explained_variance_ratio_, alpha=0.7)
    axes[0].set_xlabel('Principal Component')
    axes[0].set_ylabel('Explained Variance Ratio')
    axes[0].set_title('PCA - Explained Variance')
    axes[0].grid(True, alpha=0.3)
    
    # 2. 누적 설명된 분산 / Cumulative explained variance
    cumsum = np.cumsum(pca.explained_variance_ratio_)
    axes[1].plot(range(len(cumsum)), cumsum, 'o-', linewidth=2)
    axes[1].axhline(y=0.95, color='red', linestyle='--', label='95% threshold')
    axes[1].set_xlabel('Principal Component')
    axes[1].set_ylabel('Cumulative Explained Variance')
    axes[1].set_title('Cumulative Explained Variance')
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()
    
    # 3. PC1 vs PC2 스캐터 플롯 / PC1 vs PC2 scatter plot
    colors = plt.cm.Set1(np.linspace(0, 1, len(file_ids)))
    for i, file_id in enumerate(file_ids):
        axes[2].scatter(pca_result[i, 0], pca_result[i, 1], 
                       color=colors[i], s=100, label=file_id)
    axes[2].set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)')
    axes[2].set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)')
    axes[2].set_title('PCA - PC1 vs PC2')
    axes[2].grid(True, alpha=0.3)
    axes[2].legend()
    
    plt.tight_layout()
    return fig


def perform_clustering_analysis(folder_data, n_clusters=3):
    """
    클러스터링 분석 수행 / Perform clustering analysis
    """
    # 데이터 준비 / Prepare data
    features = []
    file_ids = []
    
    for file_id, (data, stats, filename) in folder_data.items():
        # 통계적 특성을 특징으로 사용 / Use statistical features
        advanced_stats = calculate_advanced_statistics(data)
        feature_vector = [
            stats['mean'], stats['std'], stats['min'], stats['max'], stats['range'],
            advanced_stats.get('skewness', 0), advanced_stats.get('kurtosis', 0),
            advanced_stats.get('cp', 0), advanced_stats.get('cpk', 0)
        ]
        features.append(feature_vector)
        file_ids.append(file_id.replace('File_', ''))
    
    # 특징 표준화 / Standardize features
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    # K-means 클러스터링 / K-means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    cluster_labels = kmeans.fit_predict(features_scaled)
    
    return features_scaled, cluster_labels, file_ids, kmeans


def create_clustering_visualization(folder_data, figsize=(8.27, 11.69)):
    """
    클러스터링 시각화 / Clustering visualization
    """
    features_scaled, cluster_labels, file_ids, kmeans = perform_clustering_analysis(folder_data)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize)
    
    # PCA로 2D 시각화 / 2D visualization with PCA
    pca = PCA(n_components=2)
    features_2d = pca.fit_transform(features_scaled)
    
    colors = ['red', 'blue', 'green', 'orange', 'purple']
    
    # 클러스터별 색상으로 표시 / Display with cluster colors
    for i in range(max(cluster_labels) + 1):
        cluster_mask = cluster_labels == i
        ax1.scatter(features_2d[cluster_mask, 0], features_2d[cluster_mask, 1], 
                   color=colors[i % len(colors)], label=f'Cluster {i}', s=100, alpha=0.7)
    
    # 파일 ID 라벨 / File ID labels
    for i, file_id in enumerate(file_ids):
        ax1.annotate(file_id, (features_2d[i, 0], features_2d[i, 1]), 
                    xytext=(5, 5), textcoords='offset points')
    
    ax1.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)')
    ax1.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)')
    ax1.set_title('File Clustering (PCA projection)')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # 클러스터 중심과의 거리 / Distance to cluster centers
    cluster_centers_2d = pca.transform(kmeans.cluster_centers_)
    ax1.scatter(cluster_centers_2d[:, 0], cluster_centers_2d[:, 1], 
               color='black', marker='x', s=200, linewidths=3, label='Centroids')
    
    # 클러스터 분포 / Cluster distribution
    unique, counts = np.unique(cluster_labels, return_counts=True)
    ax2.bar(unique, counts, alpha=0.7, color=[colors[i % len(colors)] for i in unique])
    ax2.set_xlabel('Cluster')
    ax2.set_ylabel('Number of Files')
    ax2.set_title('Cluster Distribution')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def create_stability_metrics(folder_data, figsize=(8.27, 11.69)):
    """
    안정성 메트릭 시각화 / Stability metrics visualization
    """
    fig, axes = plt.subplots(2, 1, figsize=figsize)
    
    file_ids = []
    cv_values = []  # Coefficient of variation
    stability_scores = []
    
    for file_id, (data, stats, filename) in folder_data.items():
        file_ids.append(file_id.replace('File_', ''))
        
        # 변동계수 (CV) / Coefficient of variation
        cv = (stats['std'] / abs(stats['mean'])) * 100 if stats['mean'] != 0 else 0
        cv_values.append(cv)
        
        # 안정성 점수 (작은 CV가 더 안정적) / Stability score
        stability_score = 100 / (1 + cv/10)  # 변동계수가 작을수록 높은 점수
        stability_scores.append(stability_score)
    
    x_pos = np.arange(len(file_ids))
    
    # 변동계수 / Coefficient of variation
    bars1 = axes[0].bar(x_pos, cv_values, alpha=0.7, color='lightcoral')
    axes[0].set_xlabel('Files', fontsize=12)
    axes[0].set_ylabel('Coefficient of Variation (%)', fontsize=12)
    axes[0].set_title('Measurement Variability (CV)', fontweight='bold')
    axes[0].set_xticks(x_pos)
    axes[0].set_xticklabels(file_ids, rotation=45)
    axes[0].grid(True, alpha=0.3)
    
    # 안정성 점수 / Stability scores
    colors_stability = ['green' if s >= 80 else 'orange' if s >= 60 else 'red' for s in stability_scores]
    bars2 = axes[1].bar(x_pos, stability_scores, alpha=0.7, color=colors_stability)
    axes[1].axhline(y=80, color='green', linestyle='--', label='Good (≥80)')
    axes[1].axhline(y=60, color='orange', linestyle='--', label='Fair (≥60)')
    axes[1].set_xlabel('Files', fontsize=12)
    axes[1].set_ylabel('Stability Score', fontsize=12)
    axes[1].set_title('Process Stability Score', fontweight='bold')
    axes[1].set_xticks(x_pos)
    axes[1].set_xticklabels(file_ids, rotation=45)
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()
    
    plt.tight_layout()
    return fig


def create_heatmap_overlays(folder_data, figsize=(11.69, 8.27), vmin=None, vmax=None):
    """
    통계적 메트릭 히트맵 오버레이 (2x2 형식으로 페이지당 4개 파일)
    Statistical metrics heatmap overlays (2x2 format, 4 files per page)
    """
    files = list(folder_data.items())
    n_files = len(files)
    files_per_page = 4  # 2x2 format
    
    figures = []
    
    # Process files in chunks of 4 (2x2 per page)
    for page_start in range(0, n_files, files_per_page):
        page_end = min(page_start + files_per_page, n_files)
        page_files = files[page_start:page_end]
        n_page_files = len(page_files)
        
        # Create 2x2 subplot layout
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        axes = axes.flatten()  # Flatten for easy indexing
        
        for i, (file_id, (data, stats, filename)) in enumerate(page_files):
            # 로컬 표준편차 맵 / Local standard deviation map
            local_std = gaussian_filter(data, sigma=2)
            local_var = (data - local_std) ** 2
            
            # Create combined visualization showing both original and local variability
            ax = axes[i]
            
            # Show local variability as the main plot
            im = ax.imshow(local_var, cmap='hot', aspect='equal')
            ax.set_title(f'{file_id.replace("File_", "")} - Local Variability\n{filename}', 
                        fontsize=10, fontweight='bold')
            
            # Remove ticks for cleaner look
            ax.set_xticks([])
            ax.set_yticks([])
            
            # Add colorbar
            plt.colorbar(im, ax=ax, shrink=0.8)
        
        # Hide unused subplots
        for j in range(n_page_files, 4):
            axes[j].set_visible(False)
        
        plt.tight_layout()
        figures.append(fig)
    
    return figures


def create_fourier_analysis(folder_data, figsize=(11.69, 8.27), vmin=None, vmax=None):
    """
    푸리에 분석 / Fourier analysis
    """
    n_files = len(folder_data)
    fig, axes = plt.subplots(2, n_files, figsize=figsize)
    if n_files == 1:
        axes = axes.reshape(-1, 1)
    
    for i, (file_id, (data, stats, filename)) in enumerate(folder_data.items()):
        # 2D FFT / 2D FFT
        fft_data = np.fft.fft2(data)
        fft_shifted = np.fft.fftshift(fft_data)
        magnitude_spectrum = np.log(np.abs(fft_shifted) + 1)
        
        # 원본 데이터 / Original data
        im1 = axes[0, i].imshow(data, cmap='viridis', aspect='equal', vmin=vmin, vmax=vmax)
        axes[0, i].set_title(f'{file_id.replace("File_", "")} - Spatial Domain')
        plt.colorbar(im1, ax=axes[0, i])
        
        # 주파수 도메인 / Frequency domain
        im2 = axes[1, i].imshow(magnitude_spectrum, cmap='hot', aspect='equal')
        axes[1, i].set_title(f'{file_id.replace("File_", "")} - Frequency Domain (Log Scale)')
        plt.colorbar(im2, ax=axes[1, i])
    
    plt.tight_layout()
    return fig


# 모든 고급 시각화 함수들을 하나의 함수로 통합 / Integrate all advanced visualization functions
ADVANCED_PLOT_FUNCTIONS = {
    'violin_plots': create_violin_plots,
    'cdf_plots': create_cdf_plots,
    'gradient_analysis': create_gradient_analysis,
    'contour_plots': create_contour_plots,
    'cross_sectional_profiles': create_cross_sectional_profiles,
    'percentile_analysis': create_percentile_analysis,
    'hotspot_analysis': create_hotspot_analysis,
    'correlation_analysis': create_correlation_analysis,
    'pca_visualization': create_pca_visualization,
    'clustering_visualization': create_clustering_visualization,
    'stability_metrics': create_stability_metrics,
    'heatmap_overlays': create_heatmap_overlays,
    'fourier_analysis': create_fourier_analysis
}


def create_cover_page(folder_data, figsize=(8.27, 11.69)):
    """
    PDF 보고서용 표지 페이지 생성 / Create cover page for PDF report
    """
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111)
    ax.axis('off')  # Hide axes
    
    # Get current date
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Extract folder information
    folder_names = set()
    file_count = len(folder_data)
    
    # Extract folder names from filenames if available
    for file_id, (data, stats, filename) in folder_data.items():
        if '/' in filename or '\\' in filename:
            # Extract parent folder name
            parts = filename.replace('\\', '/').split('/')
            if len(parts) > 1:
                folder_names.add(parts[-2])  # Parent folder
    
    if not folder_names:
        folder_names = {'Analysis Data'}
    
    folder_display = ', '.join(sorted(folder_names))
    
    # Title and main content
    title_text = "PBA Array Warpage Analysis Report"
    
    # Create cover content
    cover_content = f"""
{title_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Analysis Folder: {folder_display}

Number of Files: {file_count}

Date: {current_datetime}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


PBA Warpage analysis


Main Analysis Contents:
• Individual PBA array heatmap analysis
• Statistical comparison analysis across arrays
• 3D surface visualization of warpage patterns
• Advanced statistical analysis


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Generated by Warpage Analysis Tool v2.0
CAE Group, MX division, s.hun.lee@samsung.com
Samsung Electronics Co., Ltd.
"""
    
    # Add cover content to the plot
    ax.text(0.5, 0.5, cover_content, transform=ax.transAxes, fontsize=12,
            verticalalignment='center', horizontalalignment='center',
            bbox=dict(boxstyle='round,pad=1.5', facecolor='lightblue', alpha=0.1),
            family='monospace')
    
    plt.tight_layout()
    return fig


def create_table_of_contents(folder_data, include_stats=True, include_3d=True, include_advanced=False, figsize=(8.27, 11.69)):
    """
    PDF 보고서용 목차 페이지 생성 / Create table of contents page for PDF report
    """
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111)
    ax.axis('off')  # Hide axes
    
    # Title
    fig.suptitle('Table of Contents', fontsize=20, fontweight='bold', y=0.95)
    
    # Calculate page numbers (starting from cover page)
    page_num = 1
    
    # Build table of contents
    toc_items = []
    
    # Cover and TOC
    toc_items.append(f"Cover Page ......................................................... 1")
    page_num += 1
    toc_items.append(f"Table of Contents ............................................... {page_num}")
    page_num += 1
    toc_items.append(f"Legend & Terminology .............................. {page_num}")
    page_num += 1
    toc_items.append("")
    
    # Individual analysis pages
    file_count = len(folder_data)
    if file_count > 0:
        toc_items.append("Individual File Analysis")
        for i, file_id in enumerate(sorted(folder_data.keys())):
            simple_id = file_id.replace('File_', '')
            # toc_items.append(f"  • File {simple_id} Analysis ................................................ {page_num}")
            page_num += 1
        toc_items.append("")
    
    # Statistical comparison
    if include_stats:
        toc_items.append("Statistical Comparison Analysis")
        toc_items.append(f"  • Mean & Range Comparison ........................ {page_num}")
        page_num += 1
        toc_items.append(f"  • Min-Max & Standard Deviation ..................... {page_num}")
        page_num += 1
        toc_items.append(f"  • Warpage Distribution ....................... {page_num}")
        page_num += 1
        toc_items.append("")
    
    # Advanced analysis
    if include_advanced:
        toc_items.append("Advanced Statistical Analysis")
        advanced_analyses = [
            "Distribution Analysis - Violin Plots",
            "Percentile Analysis", 
            "Process Capability Analysis",
            "Spatial Gradient Analysis",
            "Statistical Process Control"
        ]
        
        for analysis in advanced_analyses:
            toc_items.append(f"  • {analysis} ............................... {page_num}")
            page_num += 1
        toc_items.append("")
    
    # 3D visualization
    if include_3d:
        toc_items.append("3D Surface Visualization")
        toc_items.append(f"  • 3D Surface Plots ...................................... {page_num}")
        page_num += 1
    
    # Join all TOC items
    toc_text = "\n".join(toc_items)
    
    # Add table of contents to the plot
    ax.text(0.05, 0.85, toc_text, transform=ax.transAxes, fontsize=11,
            verticalalignment='top', horizontalalignment='left',
            bbox=dict(boxstyle='round,pad=1', facecolor='white', alpha=0.9),
            family='monospace')
    
    # Add page count summary
    total_pages = page_num
    summary_text = f"\n\nTotal Pages: {total_pages} pages"
    
    ax.text(0.05, 0.15, summary_text, transform=ax.transAxes, fontsize=12,
            verticalalignment='top', horizontalalignment='left',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgray', alpha=0.3),
            fontweight='bold')
    
    plt.tight_layout()
    return fig


def create_legend_page(figsize=(8.27, 11.69)):
    """
    PDF 보고서용 범례 페이지 생성 / Create legend page for PDF report
    """
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111)
    ax.axis('off')  # Hide axes
    
    # Title
    fig.suptitle('Legend & Terminology', 
                 fontsize=20, fontweight='bold', y=0.95)
    
    # Create text content
    legend_text = """
STATISTICAL METRICS

Basic Statistics:
• Mean: Average warpage value across all measurement points on PBA array
• Standard Deviation (Std): Measure of data spread around the mean
• Range: Difference between maximum and minimum warpage values (Max - Min)
• Min/Max: Minimum and maximum warpage values in the PBA array dataset

Advanced Analysis:
• Hotspots: Areas on PBA array where warpage exceeds 95th percentile threshold
• Local Variability: Spatial variation in warpage across the PBA surface
• Gradient Magnitude: Rate of change in warpage values across the array
• Contour Plots: Lines connecting points of equal warpage values
• CDF Plot: Cumulative distribution of (Max-Min) ranges across PBA arrays
• Correlation Matrix: Shows relationships between different PBA arrays


Distribution Analysis:
• Violin Plots: Extension of box plots showing probability 
  density of data distribution
• Percentile Analysis: Analysis of percentile distribution in data

Generated by Warpage Analysis Tool v2.0
CAE Group, SiHun Lee
Samsung Electronics Co., Ltd.
"""
    
    # Add text to the plot
    ax.text(0.05, 0.95, legend_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', horizontalalignment='left',
            bbox=dict(boxstyle='round,pad=1', facecolor='white', alpha=0.9),
            family='monospace')
    
    plt.tight_layout()
    return fig


def create_comprehensive_advanced_analysis(folder_data, figsize=(8.27, 11.69), vmin=None, vmax=None):
    """
    모든 고급 통계 분석 생성 / Create comprehensive advanced statistical analysis
    
    Args:
        folder_data (dict): Dictionary with file_id as key and (data, stats, filename) as value
        figsize (tuple): Figure size for each plot
        vmin (float, optional): Minimum value for color scale
        vmax (float, optional): Maximum value for color scale
        
    Returns:
        list: List of matplotlib figures for advanced analysis
    """
    if not folder_data:
        print("No data found for advanced analysis!")
        return []
    
    # 사용할 분석 함수들 (사용자가 요청하지 않은 것들 제외)
    # Analysis functions to use (excluding user-specified exclusions)
    excluded_analyses = ['box_plots', 'signal_to_noise', 'moving_averages', 
                        'correlation_between_points', 'stability_between_measurements', 'fourier_analysis']
    
    # 생성할 분석들 / Analyses to create
    analyses_to_create = []
    for name, func in ADVANCED_PLOT_FUNCTIONS.items():
        if name not in excluded_analyses:
            analyses_to_create.append((name, func))
    
    print(f"Creating {len(analyses_to_create)} advanced statistical analyses...")
    
    # Functions that should use landscape orientation (use their own defaults)
    landscape_functions = [
        'violin_plots', 'cdf_plots', 'gradient_analysis', 'contour_plots',
        'cross_sectional_profiles', 'percentile_analysis', 'hotspot_analysis', 'heatmap_overlays'
    ]
    
    # Title mapping for each analysis
    analysis_titles = {
        'violin_plots': 'Distribution Analysis - Violin Plots',
        'cdf_plots': 'Cumulative Distribution Function',
        'gradient_analysis': 'Gradient Magnitude Analysis', 
        'contour_plots': 'Contour Analysis',
        'cross_sectional_profiles': 'Center Row/Column Profile',
        'percentile_analysis': 'Percentile Analysis',
        'hotspot_analysis': 'Hotspot Analysis',
        'heatmap_overlays': 'Local Variability',
        'correlation_analysis': 'Correlation Analysis',
        'pca_visualization': 'PCA Visualization',
        'clustering_visualization': 'Clustering Visualization',
        'stability_metrics': 'Stability Metrics'
    }
    
    all_results = []
    for i, (analysis_name, analysis_func) in enumerate(analyses_to_create):
        try:
            print(f"  Creating {analysis_name} ({i+1}/{len(analyses_to_create)})...")
            # Functions that need vmin/vmax for original data visualization
            functions_needing_vmin_vmax = ['gradient_analysis', 'hotspot_analysis', 'heatmap_overlays', 'fourier_analysis']
            
            # Let landscape functions use their own defaults, others use provided figsize
            if analysis_name in landscape_functions:
                # Use function's default figsize (which is landscape)
                if analysis_name in functions_needing_vmin_vmax:
                    result = analysis_func(folder_data, vmin=vmin, vmax=vmax)
                else:
                    result = analysis_func(folder_data)
            else:
                # Use provided figsize for portrait functions
                if analysis_name in functions_needing_vmin_vmax:
                    result = analysis_func(folder_data, figsize=figsize, vmin=vmin, vmax=vmax)
                else:
                    result = analysis_func(folder_data, figsize=figsize)
            
            if result is not None:
                title = analysis_titles.get(analysis_name, f"Advanced Analysis - {analysis_name}")
                
                # Check if result is a list of figures (from 2x2 layout functions) or single figure
                if isinstance(result, list):
                    for j, fig in enumerate(result):
                        page_title = f"{title} - Page {j+1}" if len(result) > 1 else title
                        all_results.append((fig, page_title))
                    print(f"    Added {len(result)} pages for {analysis_name}")
                else:
                    all_results.append((result, title))  # Add tuple of (figure, title)
                    print(f"    Added 1 page for {analysis_name}")
            else:
                print(f"    Warning: {analysis_name} returned None")
        except Exception as e:
            print(f"    Error creating {analysis_name}: {str(e)}")
            continue
    
    print(f"Successfully created {len(all_results)} advanced analysis figures with titles")
    return all_results