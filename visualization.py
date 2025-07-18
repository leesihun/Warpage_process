#!/usr/bin/env python3
"""
Visualization functions for Warpage Analyzer
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def create_comparison_plot(folder_data, figsize=(20, 5), vmin=None, vmax=None, cmap='jet', colorbar=True):
    """
    Create a comparison plot showing all files side by side with consistent scaling.
    
    Args:
        folder_data (dict): Dictionary with file_id as key and (data, stats, filename) as value
        figsize (tuple): Figure size (width, height)
        vmin, vmax (float): Color scale limits
        cmap (str): Colormap name
        colorbar (bool): Whether to show colorbar
        
    Returns:
        matplotlib.figure.Figure: The created figure
    """
    fig, axes = plt.subplots(1, len(folder_data), figsize=figsize)
    fig.suptitle('Warpage Data Comparison', fontsize=16, fontweight='bold')
    
    if len(folder_data) == 1:
        axes = [axes]
    
    # Find consistent axis limits for all subplots
    all_shapes = [data[0].shape for data in folder_data.values() if data[0] is not None]
    if all_shapes:
        max_rows = max(shape[0] for shape in all_shapes)
        max_cols = max(shape[1] for shape in all_shapes)
    else:
        max_rows, max_cols = 100, 100  # Default fallback
    
    for i, (file_id, (data, stats, filename)) in enumerate(folder_data.items()):
        if data is not None:
            im = axes[i].imshow(data, cmap=cmap, vmin=vmin, vmax=vmax)
            axes[i].set_title(f'{file_id}\n{filename}', fontweight='bold')
            axes[i].set_aspect('equal')
            
            # Set consistent axis limits
            axes[i].set_xlim(0, max_cols)
            axes[i].set_ylim(max_rows, 0)  # Inverted y-axis for image display
            
            # Remove tick labels for cleaner look
            axes[i].set_xticks([])
            axes[i].set_yticks([])
            
            # Add statistics text
            stats_text = f"Min: {stats['min']:.4f}\nMax: {stats['max']:.4f}\nMean: {stats['mean']:.4f}"
            axes[i].text(0.02, 0.98, stats_text, transform=axes[i].transAxes, 
                        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Add colorbar if requested (only one for the entire figure)
    if colorbar and len(folder_data) > 0:
        fig.colorbar(im, ax=axes, shrink=0.6, label='Warpage Value')
    
    plt.tight_layout()
    return fig


def create_individual_plot(file_id, data, stats, filename, figsize=(8, 6), vmin=None, vmax=None, cmap='jet', colorbar=True):
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
    
    im = ax.imshow(data, cmap=cmap, vmin=vmin, vmax=vmax)
    ax.set_title(f'{file_id} - {filename}', fontweight='bold', fontsize=12)
    ax.set_aspect('equal')
    
    # Set consistent axis scaling
    ax.set_xlim(0, data.shape[1])
    ax.set_ylim(data.shape[0], 0)  # Inverted y-axis for image display
    
    # Remove tick labels for cleaner look
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Add statistics text with smaller font for A4
    stats_text = f"Shape: {stats['shape']}\nMin: {stats['min']:.6f}\nMax: {stats['max']:.6f}\nMean: {stats['mean']:.6f}\nStd: {stats['std']:.6f}"
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.9), fontsize=9)
    
    # Add colorbar if requested
    if colorbar:
        cbar = fig.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label('Warpage Value', fontsize=10)
    
    plt.tight_layout(pad=0.5)
    return fig


def create_3d_surface_plot(folder_data, figsize=(20, 15)):
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
            
            ax.set_title(f'{file_id}\n{filename}', fontweight='bold', fontsize=10)
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Warpage')
            
            # Add colorbar
            fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)
    
    plt.tight_layout()
    return fig 


def create_statistical_comparison_plots(folder_data, figsize=(15, 10)):
    """
    Create comprehensive statistical comparison plots including warpage distribution.
    
    Args:
        folder_data (dict): Dictionary with file_id as key and (data, stats, filename) as value
        figsize (tuple): Figure size
        
    Returns:
        matplotlib.figure.Figure: The created figure
    """
    fig = plt.figure(figsize=figsize)
    fig.suptitle('Statistical Comparison - Warpage Analysis', fontsize=14, fontweight='bold')
    
    # Create subplots for different statistical analyses
    gs = fig.add_gridspec(2, 3, hspace=0.4, wspace=0.4)
    
    # 1. Warpage Distribution Histogram
    ax1 = fig.add_subplot(gs[0, 0])
    all_data = []
    file_labels = []
    for file_id, (data, stats, filename) in folder_data.items():
        all_data.append(data.flatten())
        file_labels.append(file_id)
    
    # Create histogram
    ax1.hist(all_data, bins=50, alpha=0.7, label=file_labels)
    ax1.set_xlabel('Warpage Value', fontsize=10)
    ax1.set_ylabel('Frequency', fontsize=10)
    ax1.set_title('Warpage Distribution Comparison', fontsize=11)
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='both', which='major', labelsize=9)
    
    # 2. Statistical Summary Bar Chart
    ax2 = fig.add_subplot(gs[0, 1])
    means = [stats['mean'] for _, (_, stats, _) in folder_data.items()]
    stds = [stats['std'] for _, (_, stats, _) in folder_data.items()]
    file_ids = list(folder_data.keys())
    
    x_pos = np.arange(len(means))
    ax2.bar(x_pos, means, yerr=stds, capsize=5, alpha=0.7)
    ax2.set_xlabel('Files', fontsize=10)
    ax2.set_ylabel('Mean Warpage Value', fontsize=10)
    ax2.set_title('Mean Warpage Values with Standard Deviation', fontsize=11)
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(file_ids, rotation=45, ha='right', fontsize=9)
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='both', which='major', labelsize=9)
    
    # 3. Range Comparison
    ax3 = fig.add_subplot(gs[0, 2])
    ranges = [stats['range'] for _, (_, stats, _) in folder_data.items()]
    ax3.bar(x_pos, ranges, alpha=0.7, color='orange')
    ax3.set_xlabel('Files', fontsize=10)
    ax3.set_ylabel('Warpage Range', fontsize=10)
    ax3.set_title('Warpage Range Comparison', fontsize=11)
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(file_ids, rotation=45, ha='right', fontsize=9)
    ax3.grid(True, alpha=0.3)
    ax3.tick_params(axis='both', which='major', labelsize=9)
    
    # 4. Min-Max Comparison
    ax4 = fig.add_subplot(gs[1, 0])
    mins = [stats['min'] for _, (_, stats, _) in folder_data.items()]
    maxs = [stats['max'] for _, (_, stats, _) in folder_data.items()]
    
    ax4.plot(x_pos, mins, 'o-', label='Min', color='red', alpha=0.7)
    ax4.plot(x_pos, maxs, 's-', label='Max', color='blue', alpha=0.7)
    ax4.fill_between(x_pos, mins, maxs, alpha=0.2, color='gray')
    ax4.set_xlabel('Files', fontsize=10)
    ax4.set_ylabel('Warpage Value', fontsize=10)
    ax4.set_title('Min-Max Warpage Values', fontsize=11)
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels(file_ids, rotation=45, ha='right', fontsize=9)
    ax4.legend(fontsize=9)
    ax4.grid(True, alpha=0.3)
    ax4.tick_params(axis='both', which='major', labelsize=9)
    
    # 5. Standard Deviation Analysis
    ax5 = fig.add_subplot(gs[1, 1])
    ax5.bar(x_pos, stds, alpha=0.7, color='green')
    ax5.set_xlabel('Files', fontsize=10)
    ax5.set_ylabel('Standard Deviation', fontsize=10)
    ax5.set_title('Standard Deviation Comparison', fontsize=11)
    ax5.set_xticks(x_pos)
    ax5.set_xticklabels(file_ids, rotation=45, ha='right', fontsize=9)
    ax5.grid(True, alpha=0.3)
    ax5.tick_params(axis='both', which='major', labelsize=9)
    
    # 6. Data Shape Comparison
    ax6 = fig.add_subplot(gs[1, 2])
    shapes = [stats['shape'] for _, (_, stats, _) in folder_data.items()]
    areas = [shape[0] * shape[1] for shape in shapes]
    ax6.bar(x_pos, areas, alpha=0.7, color='purple')
    ax6.set_xlabel('Files', fontsize=10)
    ax6.set_ylabel('Data Points (Rows × Columns)', fontsize=10)
    ax6.set_title('Data Size Comparison', fontsize=11)
    ax6.set_xticks(x_pos)
    ax6.set_xticklabels(file_ids, rotation=45, ha='right', fontsize=9)
    ax6.grid(True, alpha=0.3)
    ax6.tick_params(axis='both', which='major', labelsize=9)
    
    plt.tight_layout()
    return fig 