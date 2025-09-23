"""
Date utilities for data auto transfer system.
Handles date calculations for finding yesterday's folder.
"""

import os
from datetime import datetime, timedelta
from typing import Optional


class DateUtils:
    """Utility class for date operations."""
    
    @staticmethod
    def get_yesterday_date(date_format: str = "%Y%m%d") -> str:
        """
        Get yesterday's date formatted as string.
        
        Args:
            date_format: Date format string (default: %Y%m%d)
            
        Returns:
            Yesterday's date as formatted string
        """
        yesterday = datetime.now() - timedelta(days=1)
        return yesterday.strftime(date_format)
    
    @staticmethod
    def get_specific_date(days_ago: int, date_format: str = "%Y%m%d") -> str:
        """
        Get date from specific number of days ago.
        
        Args:
            days_ago: Number of days in the past
            date_format: Date format string (default: %Y%m%d)
            
        Returns:
            Date as formatted string
        """
        target_date = datetime.now() - timedelta(days=days_ago)
        return target_date.strftime(date_format)
    
    @staticmethod
    def find_yesterday_folder(source_directory: str, folder_pattern: str = "%Y%m%d") -> Optional[str]:
        """
        Find yesterday's folder in the source directory.
        
        Args:
            source_directory: Path to search for folders
            folder_pattern: Folder naming pattern
            
        Returns:
            Full path to yesterday's folder if found, None otherwise
        """
        yesterday_folder_name = DateUtils.get_yesterday_date(folder_pattern)
        folder_path = os.path.join(source_directory, yesterday_folder_name)
        
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            return folder_path
        else:
            return None
    
    @staticmethod
    def list_date_folders(source_directory: str, folder_pattern: str = "%Y%m%d") -> list:
        """
        List all folders matching the date pattern in source directory.
        
        Args:
            source_directory: Path to search for folders
            folder_pattern: Folder naming pattern
            
        Returns:
            List of folder names matching the pattern
        """
        if not os.path.exists(source_directory):
            return []
        
        folders = []
        try:
            for item in os.listdir(source_directory):
                item_path = os.path.join(source_directory, item)
                if os.path.isdir(item_path):
                    # Try to parse the folder name as a date
                    try:
                        datetime.strptime(item, folder_pattern)
                        folders.append(item)
                    except ValueError:
                        # Folder name doesn't match date pattern, skip
                        continue
        except OSError:
            pass
        
        return sorted(folders)
    
    @staticmethod
    def validate_date_format(date_string: str, date_format: str = "%Y%m%d") -> bool:
        """
        Validate if a string matches the expected date format.
        
        Args:
            date_string: String to validate
            date_format: Expected date format
            
        Returns:
            True if valid, False otherwise
        """
        try:
            datetime.strptime(date_string, date_format)
            return True
        except ValueError:
            return False


if __name__ == "__main__":
    # Test date utilities
    print("Date Utils Test:")
    print(f"Yesterday: {DateUtils.get_yesterday_date()}")
    print(f"2 days ago: {DateUtils.get_specific_date(2)}")
    print(f"3 days ago: {DateUtils.get_specific_date(3)}")
    
    # Test folder finding
    source_dir = "../data"
    yesterday_folder = DateUtils.find_yesterday_folder(source_dir)
    if yesterday_folder:
        print(f"Yesterday's folder found: {yesterday_folder}")
    else:
        print("Yesterday's folder not found")
    
    # List all date folders
    date_folders = DateUtils.list_date_folders(source_dir)
    print(f"Date folders found: {date_folders}")