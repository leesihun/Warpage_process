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
            # Simplify file ID to just number
            simple_file_id = file_id.replace('File_', '')
            axes[i].set_title(f'{simple_file_id}\n{filename}', fontweight='bold')
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
    gs = fig.add_gridspec(2, 2, hspace=0.4, wspace=0.4)
    
    # Simplify file IDs to just numbers
    file_ids = list(folder_data.keys())
    simple_file_ids = [fid.replace('File_', '') for fid in file_ids]
    
    # 1. Statistical Summary Bar Chart
    ax1 = fig.add_subplot(gs[0, 0])
    means = [stats['mean'] for _, (_, stats, _) in folder_data.items()]
    stds = [stats['std'] for _, (_, stats, _) in folder_data.items()]
    
    x_pos = np.arange(len(means))
    ax1.bar(x_pos, means, yerr=stds, capsize=5, alpha=0.7)
    ax1.set_xlabel('Files', fontsize=10)
    ax1.set_ylabel('Mean Warpage Value', fontsize=10)
    ax1.set_title('Mean Warpage Values with Standard Deviation', fontsize=11)
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(simple_file_ids, rotation=45, ha='right', fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='both', which='major', labelsize=9)
    
    # 2. Range Comparison
    ax2 = fig.add_subplot(gs[0, 1])
    ranges = [stats['range'] for _, (_, stats, _) in folder_data.items()]
    ax2.bar(x_pos, ranges, alpha=0.7, color='orange')
    ax2.set_xlabel('Files', fontsize=10)
    ax2.set_ylabel('Warpage Range', fontsize=10)
    ax2.set_title('Warpage Range Comparison', fontsize=11)
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(simple_file_ids, rotation=45, ha='right', fontsize=9)
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='both', which='major', labelsize=9)
    
    # 3. Min-Max Comparison
    ax3 = fig.add_subplot(gs[1, 0])
    mins = [stats['min'] for _, (_, stats, _) in folder_data.items()]
    maxs = [stats['max'] for _, (_, stats, _) in folder_data.items()]
    
    ax3.plot(x_pos, mins, 'o-', label='Min', color='red', alpha=0.7)
    ax3.plot(x_pos, maxs, 's-', label='Max', color='blue', alpha=0.7)
    ax3.fill_between(x_pos, mins, maxs, alpha=0.2, color='gray')
    ax3.set_xlabel('Files', fontsize=10)
    ax3.set_ylabel('Warpage Value', fontsize=10)
    ax3.set_title('Min-Max Warpage Values', fontsize=11)
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(simple_file_ids, rotation=45, ha='right', fontsize=9)
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.3)
    ax3.tick_params(axis='both', which='major', labelsize=9)
    
    # 4. Standard Deviation Analysis
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.bar(x_pos, stds, alpha=0.7, color='green')
    ax4.set_xlabel('Files', fontsize=10)
    ax4.set_ylabel('Standard Deviation', fontsize=10)
    ax4.set_title('Standard Deviation Comparison', fontsize=11)
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels(simple_file_ids, rotation=45, ha='right', fontsize=9)
    ax4.grid(True, alpha=0.3)
    ax4.tick_params(axis='both', which='major', labelsize=9)
    
    plt.tight_layout()
    return fig 


def create_mean_comparison_plot(folder_data, figsize=(10, 6)):
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
    ax.set_xticks(x_pos)
    ax.set_xticklabels(simple_file_ids, rotation=45, ha='right', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis='both', which='major', labelsize=10)
    
    plt.tight_layout()
    return fig


def create_range_comparison_plot(folder_data, figsize=(10, 6)):
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
    ax.set_xticks(x_pos)
    ax.set_xticklabels(simple_file_ids, rotation=45, ha='right', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis='both', which='major', labelsize=10)
    
    plt.tight_layout()
    return fig


def create_minmax_comparison_plot(folder_data, figsize=(10, 6)):
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
    ax.set_xticks(x_pos)
    ax.set_xticklabels(simple_file_ids, rotation=45, ha='right', fontsize=10)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis='both', which='major', labelsize=10)
    
    plt.tight_layout()
    return fig


def create_std_comparison_plot(folder_data, figsize=(10, 6)):
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
    ax.set_xticks(x_pos)
    ax.set_xticklabels(simple_file_ids, rotation=45, ha='right', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis='both', which='major', labelsize=10)
    
    plt.tight_layout()
    return fig 


def create_warpage_distribution_plot(folder_data, figsize=(10, 6)):
    """
    Create a warpage distribution plot showing histogram of (max-min) values.
    X-axis: (Max - Min) Warpage Value
    Y-axis: Probability/Frequency
    
    Args:
        folder_data (dict): Dictionary with file_id as key and (data, stats, filename) as value
        figsize (tuple): Figure size
        
    Returns:
        matplotlib.figure.Figure: The created figure
    """
    # Keep original page size, but make plot smaller (0.45 height) in upper half
    width, height = figsize
    plot_height = height * 0.45
    
    fig = plt.figure(figsize=figsize)
    fig.suptitle('Warpage Range Distribution', fontsize=16, fontweight='bold')
    
    # Create single plot in the upper half of the page
    ax = plt.subplot(1, 1, 1)
    
    # Position the plot in the upper half, leaving bottom half empty
    # Make it smaller to match the 0.45 height requirement
    ax.set_position([0.1, 0.6, 0.8, 0.3])  # [left, bottom, width, height]
    
    # Calculate (max-min) values for each file
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


def create_mean_range_combined_plot(folder_data, figsize=(10, 12)):
    """
    Create a combined plot showing mean and range comparisons in up-down configuration.
    
    Args:
        folder_data (dict): Dictionary with file_id as key and (data, stats, filename) as value
        figsize (tuple): Figure size
        
    Returns:
        matplotlib.figure.Figure: The created figure
    """
    # Keep original page size, but make plots smaller (0.45 height)
    width, height = figsize
    plot_height = height * 0.45
    
    fig = plt.figure(figsize=figsize)
    fig.suptitle('Statistical Comparison - Mean and Range', fontsize=16, fontweight='bold')
    
    # Create two subplots in the upper half of the page
    ax1 = plt.subplot(2, 1, 1)
    ax2 = plt.subplot(2, 1, 2)
    
    # Adjust the position to use only the upper half with proper spacing
    ax1.set_position([0.1, 0.6, 0.8, 0.3])   # [left, bottom, width, height]
    ax2.set_position([0.1, 0.15, 0.8, 0.3])  # [left, bottom, width, height]
    
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
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(simple_file_ids, rotation=45, ha='right', fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='both', which='major', labelsize=10)
    
    # Bottom plot: Range comparison
    ranges = [stats['range'] for _, (_, stats, _) in folder_data.items()]
    ax2.bar(x_pos, ranges, alpha=0.7, color='orange')
    ax2.set_xlabel('Files', fontsize=12)
    ax2.set_ylabel('Warpage Range', fontsize=12)
    ax2.set_title('Warpage Range Comparison', fontsize=14, fontweight='bold')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(simple_file_ids, rotation=45, ha='right', fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='both', which='major', labelsize=10)
    
    plt.tight_layout()
    return fig


def create_minmax_std_combined_plot(folder_data, figsize=(10, 12)):
    """
    Create a combined plot showing min-max and standard deviation comparisons in up-down configuration.
    
    Args:
        folder_data (dict): Dictionary with file_id as key and (data, stats, filename) as value
        figsize (tuple): Figure size
        
    Returns:
        matplotlib.figure.Figure: The created figure
    """
    # Keep original page size, but make plots smaller (0.45 height)
    width, height = figsize
    plot_height = height * 0.45
    
    fig = plt.figure(figsize=figsize)
    fig.suptitle('Statistical Comparison - Min-Max and Standard Deviation', fontsize=16, fontweight='bold')
    
    # Create two subplots in the upper half of the page
    ax1 = plt.subplot(2, 1, 1)
    ax2 = plt.subplot(2, 1, 2)
    
    # Adjust the position to use only the upper half with proper spacing
    ax1.set_position([0.1, 0.6, 0.8, 0.3])   # [left, bottom, width, height]
    ax2.set_position([0.1, 0.15, 0.8, 0.3])  # [left, bottom, width, height]
    
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
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(simple_file_ids, rotation=45, ha='right', fontsize=10)
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='both', which='major', labelsize=10)
    
    # Bottom plot: Standard deviation comparison
    stds = [stats['std'] for _, (_, stats, _) in folder_data.items()]
    ax2.bar(x_pos, stds, alpha=0.7, color='green')
    ax2.set_xlabel('Files', fontsize=12)
    ax2.set_ylabel('Standard Deviation', fontsize=12)
    ax2.set_title('Standard Deviation Comparison', fontsize=14, fontweight='bold')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(simple_file_ids, rotation=45, ha='right', fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='both', which='major', labelsize=10)
    
    plt.tight_layout()
    return fig 


def create_web_gui_statistical_plots(folder_data, figsize=(12, 16)):
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
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(simple_file_ids, rotation=45, ha='right', fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='both', which='major', labelsize=10)
    
    # 2. Range comparison (middle)
    ax2 = plt.subplot(3, 1, 2)
    ranges = [stats['range'] for _, (_, stats, _) in folder_data.items()]
    ax2.bar(x_pos, ranges, alpha=0.7, color='orange')
    ax2.set_xlabel('Files', fontsize=12)
    ax2.set_ylabel('Warpage Range', fontsize=12)
    ax2.set_title('Warpage Range Comparison', fontsize=14, fontweight='bold')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(simple_file_ids, rotation=45, ha='right', fontsize=10)
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
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(simple_file_ids, rotation=45, ha='right', fontsize=10)
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3)
    ax3.tick_params(axis='both', which='major', labelsize=10)
    
    plt.tight_layout()
    return fig 