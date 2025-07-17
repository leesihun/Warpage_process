# visualization.py - Visualization Functions
import matplotlib.pyplot as plt
import numpy as np

def create_comparison_plot(resolution_data, figsize=(20, 5), vmin=None, vmax=None, cmap='jet', colorbar=True):
    """
    Create a comparison plot showing all resolutions side by side with consistent scaling.
    
    Args:
        resolution_data (dict): Dictionary with resolution as key and (data, stats, filename) as value
        figsize (tuple): Figure size (width, height)
        vmin, vmax (float): Color scale limits
        cmap (str): Colormap name
        colorbar (bool): Whether to show colorbar
        
    Returns:
        matplotlib.figure.Figure: The created figure
    """
    fig, axes = plt.subplots(1, len(resolution_data), figsize=figsize)
    fig.suptitle('Warpage Data Comparison - Center Region Only', fontsize=16, fontweight='bold')
    
    if len(resolution_data) == 1:
        axes = [axes]
    
    # Find consistent axis limits for all subplots
    all_shapes = [data[0].shape for data in resolution_data.values() if data[0] is not None]
    if all_shapes:
        max_rows = max(shape[0] for shape in all_shapes)
        max_cols = max(shape[1] for shape in all_shapes)
    else:
        max_rows, max_cols = 100, 100  # Default fallback
    
    for i, (resolution, (data, stats, filename)) in enumerate(resolution_data.items()):
        if data is not None:
            im = axes[i].imshow(data, cmap=cmap, vmin=vmin, vmax=vmax)
            axes[i].set_title(f'{resolution}μm Resolution\\n{filename}', fontweight='bold')
            axes[i].set_aspect('equal')
            
            # Set consistent axis limits
            axes[i].set_xlim(0, max_cols)
            axes[i].set_ylim(max_rows, 0)  # Inverted y-axis for image display
            
            # Remove tick labels for cleaner look
            axes[i].set_xticks([])
            axes[i].set_yticks([])
            
            # Add statistics text
            stats_text = f"Min: {stats['min']:.4f}\\nMax: {stats['max']:.4f}\\nMean: {stats['mean']:.4f}"
            axes[i].text(0.02, 0.98, stats_text, transform=axes[i].transAxes, 
                        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Note: No colorbar for comparison plot to keep it clean
    # Individual plots will have colorbars when enabled
    
    plt.tight_layout()
    return fig

def create_individual_plot(resolution, data, stats, filename, figsize=(8, 6), vmin=None, vmax=None, cmap='jet', colorbar=True):
    """
    Create an individual plot for a single resolution with consistent scaling.
    
    Args:
        resolution (str): Resolution value
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
    ax.set_title(f'{resolution}μm Resolution - Center Region\\n{filename}', fontweight='bold', fontsize=14)
    ax.set_aspect('equal')
    
    # Set consistent axis scaling
    ax.set_xlim(0, data.shape[1])
    ax.set_ylim(data.shape[0], 0)  # Inverted y-axis for image display
    
    # Remove tick labels for cleaner look
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Add statistics text
    stats_text = f"Shape: {stats['shape']}\\nMin: {stats['min']:.6f}\\nMax: {stats['max']:.6f}\\nMean: {stats['mean']:.6f}\\nStd: {stats['std']:.6f}"
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
    
    # Add colorbar if requested
    if colorbar:
        cbar = fig.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label('Warpage Value', fontsize=12)
    
    plt.tight_layout()
    return fig

def create_statistics_plots(resolutions, stats_data, figsize=(15, 10)):
    """
    Create comprehensive statistics comparison plots.
    NOTE: This function is kept for future use when comparing same resolutions.
    
    Args:
        resolutions (list): List of resolution values
        stats_data (dict): Dictionary of statistical data
        figsize (tuple): Figure size
        
    Returns:
        matplotlib.figure.Figure: The created figure
    """
    fig, axes = plt.subplots(2, 3, figsize=figsize)
    fig.suptitle('Statistical Analysis - Resolution Comparison', fontsize=16, fontweight='bold')
    
    # Plot 1: Min/Max
    axes[0, 0].plot(resolutions, stats_data['min'], 'b-o', label='Min', linewidth=2, markersize=8)
    axes[0, 0].plot(resolutions, stats_data['max'], 'r-o', label='Max', linewidth=2, markersize=8)
    axes[0, 0].set_xlabel('Resolution (μm)')
    axes[0, 0].set_ylabel('Warpage Value')
    axes[0, 0].set_title('Min/Max Warpage vs Resolution')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Plot 2: Mean
    axes[0, 1].plot(resolutions, stats_data['mean'], 'g-o', linewidth=2, markersize=8)
    axes[0, 1].set_xlabel('Resolution (μm)')
    axes[0, 1].set_ylabel('Mean Warpage')
    axes[0, 1].set_title('Mean Warpage vs Resolution')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Plot 3: Standard Deviation
    axes[0, 2].plot(resolutions, stats_data['std'], 'm-o', linewidth=2, markersize=8)
    axes[0, 2].set_xlabel('Resolution (μm)')
    axes[0, 2].set_ylabel('Standard Deviation')
    axes[0, 2].set_title('Std Deviation vs Resolution')
    axes[0, 2].grid(True, alpha=0.3)
    
    # Plot 4: Range
    axes[1, 0].plot(resolutions, stats_data['range'], 'c-o', linewidth=2, markersize=8)
    axes[1, 0].set_xlabel('Resolution (μm)')
    axes[1, 0].set_ylabel('Range (Max - Min)')
    axes[1, 0].set_title('Range vs Resolution')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Plot 5: Bar chart comparison
    x_pos = np.arange(len(resolutions))
    axes[1, 1].bar(x_pos, stats_data['mean'], alpha=0.7, color='skyblue', edgecolor='navy')
    axes[1, 1].set_xlabel('Resolution (μm)')
    axes[1, 1].set_ylabel('Mean Warpage')
    axes[1, 1].set_title('Mean Warpage Comparison')
    axes[1, 1].set_xticks(x_pos)
    axes[1, 1].set_xticklabels([f'{r}μm' for r in resolutions])
    axes[1, 1].grid(True, alpha=0.3, axis='y')
    
    # Plot 6: Combined metrics
    axes[1, 2].plot(resolutions, np.array(stats_data['mean']) + np.array(stats_data['std']), 
                    'r--', label='Mean + Std', alpha=0.7)
    axes[1, 2].plot(resolutions, stats_data['mean'], 'b-o', label='Mean', linewidth=2)
    axes[1, 2].plot(resolutions, np.array(stats_data['mean']) - np.array(stats_data['std']), 
                    'r--', label='Mean - Std', alpha=0.7)
    axes[1, 2].fill_between(resolutions, 
                           np.array(stats_data['mean']) - np.array(stats_data['std']),
                           np.array(stats_data['mean']) + np.array(stats_data['std']),
                           alpha=0.2, color='red')
    axes[1, 2].set_xlabel('Resolution (μm)')
    axes[1, 2].set_ylabel('Warpage Value')
    axes[1, 2].set_title('Mean ± Standard Deviation')
    axes[1, 2].legend()
    axes[1, 2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def create_3d_surface_plot(resolution_data, figsize=(20, 15)):
    """
    Create 3D surface plots for all resolutions.
    NOTE: This function is kept for future use when 3D visualization is needed.
    
    Args:
        resolution_data (dict): Dictionary with resolution as key and (data, stats, filename) as value
        figsize (tuple): Figure size
        
    Returns:
        matplotlib.figure.Figure: The created figure
    """
    from mpl_toolkits.mplot3d import Axes3D
    
    fig = plt.figure(figsize=figsize)
    fig.suptitle('3D Surface Plots - Warpage Data by Resolution', fontsize=16, fontweight='bold')
    
    plot_positions = [(2, 2, 1), (2, 2, 2), (2, 2, 3), (2, 2, 4)]
    
    for i, (resolution, (data, stats, filename)) in enumerate(resolution_data.items()):
        if data is not None and i < len(plot_positions):
            ax = fig.add_subplot(*plot_positions[i], projection='3d')
            
            # Create coordinate meshes
            x = np.arange(data.shape[1])
            y = np.arange(data.shape[0])
            X, Y = np.meshgrid(x, y)
            
            # Create surface plot
            surf = ax.plot_surface(X, Y, data, cmap='jet', alpha=0.8)
            
            ax.set_title(f'{resolution}μm Resolution\\n{filename}', fontweight='bold')
            ax.set_xlabel('X Position')
            ax.set_ylabel('Y Position')
            ax.set_zlabel('Warpage Value')
            
            # Add colorbar
            fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)
    
    plt.tight_layout()
    return fig

def create_same_resolution_comparison(data_dict, resolution, figsize=(20, 5), vmin=None, vmax=None, cmap='jet', colorbar=True):
    """
    Create comparison plot for multiple datasets of the same resolution.
    This function is designed for future use when comparing same resolutions.
    
    Args:
        data_dict (dict): Dictionary with dataset name as key and (data, stats, filename) as value
        resolution (str): Resolution value for all datasets
        figsize (tuple): Figure size (width, height)
        vmin, vmax (float): Color scale limits
        cmap (str): Colormap name
        colorbar (bool): Whether to show colorbar
        
    Returns:
        matplotlib.figure.Figure: The created figure
    """
    fig, axes = plt.subplots(1, len(data_dict), figsize=figsize)
    fig.suptitle(f'Same Resolution Comparison - {resolution}μm', fontsize=16, fontweight='bold')
    
    if len(data_dict) == 1:
        axes = [axes]
    
    # Find consistent axis limits for all subplots
    all_shapes = [data[0].shape for data in data_dict.values() if data[0] is not None]
    if all_shapes:
        max_rows = max(shape[0] for shape in all_shapes)
        max_cols = max(shape[1] for shape in all_shapes)
    else:
        max_rows, max_cols = 100, 100  # Default fallback
    
    for i, (dataset_name, (data, stats, filename)) in enumerate(data_dict.items()):
        if data is not None:
            im = axes[i].imshow(data, cmap=cmap, vmin=vmin, vmax=vmax)
            axes[i].set_title(f'{dataset_name}\\n{filename}', fontweight='bold')
            axes[i].set_aspect('equal')
            
            # Set consistent axis limits
            axes[i].set_xlim(0, max_cols)
            axes[i].set_ylim(max_rows, 0)  # Inverted y-axis for image display
            
            # Remove tick labels for cleaner look
            axes[i].set_xticks([])
            axes[i].set_yticks([])
            
            # Add statistics text
            stats_text = f"Min: {stats['min']:.4f}\\nMax: {stats['max']:.4f}\\nMean: {stats['mean']:.4f}"
            axes[i].text(0.02, 0.98, stats_text, transform=axes[i].transAxes, 
                        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Add colorbar if requested
    if colorbar and len(data_dict) > 0:
        # Create colorbar for the last image (they all have the same scale)
        last_im = im  # im from the last iteration
        cbar = fig.colorbar(last_im, ax=axes, orientation='horizontal', pad=0.1, shrink=0.8)
        cbar.set_label('Warpage Value', fontsize=12)
    
    plt.tight_layout()
    return fig 