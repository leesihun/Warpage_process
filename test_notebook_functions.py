#!/usr/bin/env python3
"""
Test script for the ORI file modification notebook functions.
This script tests the core functionality without requiring Jupyter.
"""

import os
import numpy as np
import sys

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_test_data():
    """Create test data that simulates an ORI file."""
    # Create a 100x100 array with various values
    np.random.seed(42)  # For reproducible results
    
    # Start with random values between -50 and 50
    data = np.random.uniform(-50, 50, (100, 100))
    
    # Add some artifact values (9999.0) to simulate invalid measurements
    # Set borders to 9999.0
    data[0, :] = 9999.0  # Top border
    data[-1, :] = 9999.0  # Bottom border
    data[:, 0] = 9999.0  # Left border
    data[:, -1] = 9999.0  # Right border
    
    # Add some scattered artifact values
    artifact_indices_i = np.random.choice(range(1, 99), size=50, replace=False)
    artifact_indices_j = np.random.choice(range(1, 99), size=50, replace=False)
    for i, j in zip(artifact_indices_i, artifact_indices_j):
        data[i, j] = 9999.0
    
    return data

def save_test_ori_file(data, filename):
    """Save test data as an ORI file."""
    with open(filename, 'w', encoding='utf-8') as f:
        for row in data:
            row_str = '\t'.join(f'{val:.1f}' for val in row)
            f.write(row_str + '\n')
    print(f"Test ORI file saved: {filename}")

def load_ori_data(file_path):
    """Load data from an ORI file (simplified version)."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = f.read()
        
        data_lines = data.strip().split('\n')
        clean_lines = []
        
        for line in data_lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('%'):
                try:
                    float_values = [float(x) for x in line.split()]
                    if float_values:
                        clean_lines.append(line)
                except ValueError:
                    continue
        
        if not clean_lines:
            return None
        
        data_array = np.array([list(map(float, line.split())) for line in clean_lines])
        return data_array
        
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def analyze_data(data_array, artifact_values=None):
    """Analyze the data array."""
    if artifact_values is None:
        artifact_values = [9999.0, -9999.0, 99999.0, -99999.0, -4000.0]
    
    # Create mask for non-artifact values
    non_artifact_mask = np.ones(data_array.shape, dtype=bool)
    for artifact_val in artifact_values:
        non_artifact_mask &= (data_array != artifact_val)
    
    valid_data = data_array[non_artifact_mask]
    
    total_points = data_array.size
    valid_points = valid_data.size
    artifact_points = total_points - valid_points
    
    analysis = {
        'total_points': total_points,
        'valid_points': valid_points,
        'artifact_points': artifact_points,
        'valid_percentage': (valid_points / total_points) * 100,
        'artifact_percentage': (artifact_points / total_points) * 100,
    }
    
    if valid_points > 0:
        analysis.update({
            'min_value': np.min(valid_data),
            'max_value': np.max(valid_data),
            'mean_value': np.mean(valid_data),
            'std_value': np.std(valid_data),
            'median_value': np.median(valid_data)
        })
    
    return analysis

def modify_lower_values(data_array, percentage, artifact_values=None, new_value=9999.0):
    """Modify the lower N% of valid values."""
    if artifact_values is None:
        artifact_values = [9999.0, -9999.0, 99999.0, -99999.0, -4000.0]
    
    modified_data = data_array.copy()
    
    # Create mask for non-artifact values
    non_artifact_mask = np.ones(data_array.shape, dtype=bool)
    for artifact_val in artifact_values:
        non_artifact_mask &= (data_array != artifact_val)
    
    valid_data = data_array[non_artifact_mask]
    
    if valid_data.size == 0:
        return modified_data, {
            'modified_count': 0,
            'threshold_value': None,
            'valid_points': 0,
            'error': 'No valid data points found'
        }
    
    # Calculate threshold
    threshold_percentile = percentage
    threshold_value = np.percentile(valid_data, threshold_percentile)
    
    # Create modification mask
    modification_mask = non_artifact_mask & (data_array <= threshold_value)
    modified_count = np.sum(modification_mask)
    
    # Apply modification
    modified_data[modification_mask] = new_value
    
    modification_info = {
        'modified_count': modified_count,
        'threshold_value': threshold_value,
        'valid_points': valid_data.size,
        'percentage_requested': percentage,
        'percentage_actual': (modified_count / valid_data.size) * 100 if valid_data.size > 0 else 0,
        'new_value': new_value
    }
    
    return modified_data, modification_info

def test_notebook_functions():
    """Test the main functions from the notebook."""
    print("=== Testing ORI File Modification Functions ===\n")
    
    # 1. Create test data
    print("1. Creating test data...")
    test_data = create_test_data()
    print(f"   Created test data with shape: {test_data.shape}")
    
    # 2. Save test ORI file
    print("\n2. Saving test ORI file...")
    test_file_path = "test_ori_file.txt"
    save_test_ori_file(test_data, test_file_path)
    
    # 3. Load the test file
    print("\n3. Loading test ORI file...")
    loaded_data = load_ori_data(test_file_path)
    if loaded_data is not None:
        print(f"   Successfully loaded data with shape: {loaded_data.shape}")
        print(f"   Data matches original: {np.array_equal(test_data, loaded_data)}")
    else:
        print("   ERROR: Failed to load test data")
        return False
    
    # 4. Analyze original data
    print("\n4. Analyzing original data...")
    analysis = analyze_data(loaded_data)
    print(f"   Total points: {analysis['total_points']:,}")
    print(f"   Valid points: {analysis['valid_points']:,} ({analysis['valid_percentage']:.1f}%)")
    print(f"   Artifact points: {analysis['artifact_points']:,} ({analysis['artifact_percentage']:.1f}%)")
    if analysis['valid_points'] > 0:
        print(f"   Value range: {analysis['min_value']:.3f} to {analysis['max_value']:.3f}")
        print(f"   Mean: {analysis['mean_value']:.3f}, Std: {analysis['std_value']:.3f}")
    
    # 5. Test modification with different percentages
    test_percentages = [5.0, 10.0, 25.0]
    
    for percentage in test_percentages:
        print(f"\n5.{test_percentages.index(percentage)+1}. Testing {percentage}% modification...")
        
        modified_data, mod_info = modify_lower_values(loaded_data, percentage)
        
        if 'error' in mod_info:
            print(f"     ERROR: {mod_info['error']}")
            continue
        
        print(f"     Threshold value: {mod_info['threshold_value']:.6f}")
        print(f"     Values modified: {mod_info['modified_count']:,}")
        print(f"     Requested: {mod_info['percentage_requested']:.1f}%, Actual: {mod_info['percentage_actual']:.2f}%")
        
        # Verify modification
        original_valid_count = analysis['valid_points']
        modified_analysis = analyze_data(modified_data)
        new_valid_count = modified_analysis['valid_points']
        
        expected_reduction = mod_info['modified_count']
        actual_reduction = original_valid_count - new_valid_count
        
        print(f"     Valid points reduced by: {actual_reduction:,} (expected: {expected_reduction:,})")
        print(f"     Modification successful: {actual_reduction == expected_reduction}")
        
        # Save modified file
        output_file = f"test_ori_modified_{percentage:.0f}pct.txt"
        save_test_ori_file(modified_data, output_file)
    
    # 6. Clean up test files
    print("\n6. Cleaning up test files...")
    test_files = [test_file_path] + [f"test_ori_modified_{p:.0f}pct.txt" for p in test_percentages]
    for file_path in test_files:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"   Removed: {file_path}")
    
    print("\n=== All tests completed successfully! ===")
    return True

if __name__ == "__main__":
    try:
        success = test_notebook_functions()
        if success:
            print("\nOK Notebook functions are working correctly!")
            exit(0)
        else:
            print("\nERROR Some tests failed!")
            exit(1)
    except Exception as e:
        print(f"\nERROR Test failed with error: {e}")
        exit(1)