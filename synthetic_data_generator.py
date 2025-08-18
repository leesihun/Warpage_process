#!/usr/bin/env python3
"""
Synthetic warpage data generator for demonstration purposes
합성 워페이지 데이터 생성기
"""

import numpy as np
import os
from warpage_statistics import calculate_statistics


def generate_realistic_warpage_pattern(rows, cols, pattern_type='mixed'):
    """
    Generate realistic warpage pattern with spatial correlation
    실제적인 공간 상관관계를 가진 워페이지 패턴 생성
    
    Args:
        rows (int): Number of rows
        cols (int): Number of columns  
        pattern_type (str): Type of warpage pattern
        
    Returns:
        numpy.ndarray: Generated warpage data
    """
    # Create coordinate grids
    y, x = np.meshgrid(np.linspace(0, 1, rows), np.linspace(0, 1, cols), indexing='ij')
    
    # Base warpage patterns
    if pattern_type == 'center_bow':
        # Center bowing - common in semiconductor packages
        r_squared = (x - 0.5)**2 + (y - 0.5)**2
        warpage = -2000 * r_squared + np.random.normal(0, 150, (rows, cols))
    
    elif pattern_type == 'edge_curl':
        # Edge curling pattern
        edge_dist = np.minimum(np.minimum(x, 1-x), np.minimum(y, 1-y))
        warpage = -1500 * (1 - 2*edge_dist) + np.random.normal(0, 200, (rows, cols))
    
    elif pattern_type == 'corner_stress':
        # Corner stress concentration
        corner_effects = ((x-0)**2 + (y-0)**2) + ((x-1)**2 + (y-0)**2) + ((x-0)**2 + (y-1)**2) + ((x-1)**2 + (y-1)**2)
        warpage = -800 * corner_effects + np.random.normal(0, 180, (rows, cols))
    
    elif pattern_type == 'thermal_gradient':
        # Thermal gradient effect
        warpage = -1200 * (x + y) + np.random.normal(0, 160, (rows, cols))
    
    elif pattern_type == 'process_variation':
        # Random process variation
        warpage = np.random.normal(-1000, 400, (rows, cols))
        # Add some spatial correlation
        from scipy.ndimage import gaussian_filter
        warpage = gaussian_filter(warpage, sigma=2)
    
    elif pattern_type == 'mixed':
        # Mixed pattern combining multiple effects
        r_squared = (x - 0.5)**2 + (y - 0.5)**2
        edge_dist = np.minimum(np.minimum(x, 1-x), np.minimum(y, 1-y))
        warpage = (-1500 * r_squared + 
                  -800 * (1 - 2*edge_dist) + 
                  -300 * (x + y) + 
                  np.random.normal(0, 200, (rows, cols)))
    
    # Apply some spatial smoothing for realism
    from scipy.ndimage import gaussian_filter
    warpage = gaussian_filter(warpage, sigma=1.5)
    
    # Add some measurement artifacts (-4000 values)
    artifact_mask = np.random.random((rows, cols)) < 0.001  # 0.1% artifacts
    warpage[artifact_mask] = -4000
    
    return warpage


def generate_synthetic_dataset(num_samples=100):
    """
    Generate synthetic warpage dataset with 100 samples
    100개 샘플의 합성 워페이지 데이터셋 생성
    
    Args:
        num_samples (int): Number of samples to generate
        
    Returns:
        dict: Dictionary with file_id as key and (data, stats, filename) as value
    """
    print(f"Generating synthetic warpage dataset with {num_samples} samples...")
    
    # Different sample types and sizes
    sample_configs = [
        {'type': 'large_package', 'rows': 120, 'cols': 160, 'pattern': 'center_bow'},
        {'type': 'medium_package', 'rows': 80, 'cols': 100, 'pattern': 'edge_curl'},
        {'type': 'small_package', 'rows': 50, 'cols': 60, 'pattern': 'corner_stress'},
        {'type': 'flex_pcb', 'rows': 200, 'cols': 300, 'pattern': 'thermal_gradient'},
        {'type': 'standard_pcb', 'rows': 100, 'cols': 120, 'pattern': 'process_variation'},
        {'type': 'complex_pattern', 'rows': 150, 'cols': 180, 'pattern': 'mixed'},
    ]
    
    folder_data = {}
    
    for i in range(num_samples):
        # Select configuration cyclically with some variation
        base_config = sample_configs[i % len(sample_configs)]
        
        # Add some size variation (±20%)
        size_factor = np.random.uniform(0.8, 1.2)
        rows = max(20, int(base_config['rows'] * size_factor))
        cols = max(20, int(base_config['cols'] * size_factor))
        
        # Generate the warpage data
        data = generate_realistic_warpage_pattern(rows, cols, base_config['pattern'])
        
        # Calculate statistics
        stats = calculate_statistics(data)
        
        # Create filename
        filename = f"synthetic_{base_config['type']}_sample_{i+1:03d}.txt"
        
        # Create file ID
        file_id = f"sample_{i+1:03d}"
        
        folder_data[file_id] = (data, stats, filename)
        
        if (i + 1) % 10 == 0:
            print(f"  Generated {i+1}/{num_samples} samples...")
    
    print(f"Successfully generated {num_samples} synthetic warpage samples!")
    
    # Print summary statistics
    print(f"\nDataset Summary:")
    print(f"  Total samples: {len(folder_data)}")
    
    all_means = [stats['mean'] for _, (_, stats, _) in folder_data.items()]
    all_stds = [stats['std'] for _, (_, stats, _) in folder_data.items()]
    all_ranges = [stats['range'] for _, (_, stats, _) in folder_data.items()]
    
    print(f"  Mean warpage: {np.mean(all_means):.2f} ± {np.std(all_means):.2f}")
    print(f"  Std deviation: {np.mean(all_stds):.2f} ± {np.std(all_stds):.2f}")
    print(f"  Range: {np.mean(all_ranges):.2f} ± {np.std(all_ranges):.2f}")
    
    # Sample sizes
    all_sizes = [data.shape for _, (data, _, _) in folder_data.items()]
    total_points = sum(rows * cols for rows, cols in all_sizes)
    print(f"  Total measurement points: {total_points:,}")
    print(f"  Average sample size: {total_points / len(folder_data):,.0f} points")
    
    return folder_data


if __name__ == "__main__":
    # Generate synthetic data for testing
    synthetic_data = generate_synthetic_dataset(100)
    print("Synthetic warpage data generation completed!")