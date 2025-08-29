#!/usr/bin/env python3
"""
Debug script to test path resolution in executable vs development
"""

import os
import sys
from config import get_data_dir, DEFAULT_CONFIG

print("=== Path Debug Information ===")
print(f"Python executable: {sys.executable}")
print(f"Current working directory: {os.getcwd()}")
print(f"Script directory: {os.path.dirname(os.path.abspath(__file__))}")
print(f"Has _MEIPASS: {hasattr(sys, '_MEIPASS')}")
if hasattr(sys, '_MEIPASS'):
    print(f"_MEIPASS: {sys._MEIPASS}")

print(f"\nData directory from get_data_dir(): {get_data_dir()}")
print(f"Data directory exists: {os.path.exists(get_data_dir())}")

if os.path.exists(get_data_dir()):
    print(f"Contents of data directory:")
    try:
        for item in os.listdir(get_data_dir()):
            item_path = os.path.join(get_data_dir(), item)
            print(f"  - {item} ({'dir' if os.path.isdir(item_path) else 'file'})")
    except Exception as e:
        print(f"  Error listing directory: {e}")

print(f"\nDEFAULT_CONFIG['data_dir']: {DEFAULT_CONFIG.get('data_dir')}")