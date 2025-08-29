#!/usr/bin/env python3
"""
Test script to debug folder detection issue
"""

import os
import sys
from config import DEFAULT_CONFIG
from data_loader import find_data_files
from web_server import has_data_files_recursive

def test_folder_detection():
    print("=== Folder Detection Test ===")
    
    config = DEFAULT_CONFIG.copy()
    data_dir = config.get('data_dir', './data')
    
    print(f"Config data_dir: {data_dir}")
    print(f"Data directory exists: {os.path.exists(data_dir)}")
    print(f"Current working directory: {os.getcwd()}")
    
    if not os.path.exists(data_dir):
        print("ERROR: Data directory does not exist!")
        return
    
    print(f"\nScanning directory: {data_dir}")
    all_items = os.listdir(data_dir)
    print(f"All items found: {all_items}")
    
    folders = []
    for item in all_items:
        item_path = os.path.join(data_dir, item)
        print(f"\nChecking item: {item}")
        print(f"  Full path: {item_path}")
        print(f"  Is directory: {os.path.isdir(item_path)}")
        print(f"  Starts with dot: {item.startswith('.')}")
        
        if os.path.isdir(item_path) and not item.startswith('.'):
            print(f"  Checking for data files...")
            try:
                # Check both original and corrected files
                original_files = find_data_files(item_path, True)
                corrected_files = find_data_files(item_path, False)
                has_files_recursive = has_data_files_recursive(item_path)
                
                print(f"    Original files found: {len(original_files)}")
                print(f"    Corrected files found: {len(corrected_files)}")
                print(f"    Has files recursive: {has_files_recursive}")
                
                if has_files_recursive:
                    folders.append(item)
                    print(f"    ✓ Added to folders list")
                else:
                    print(f"    ✗ Not added - no data files found")
                    
            except Exception as e:
                print(f"    ERROR checking folder {item}: {e}")
                import traceback
                traceback.print_exc()
    
    print(f"\nFinal folders list: {folders}")
    return folders

if __name__ == "__main__":
    test_folder_detection()