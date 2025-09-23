"""
Configuration parser for data auto transfer system.
Reads configuration from config.txt file.
"""

import os
from typing import Dict, Any, List


class ConfigParser:
    """Parse configuration from txt file."""
    
    def __init__(self, config_path: str = "config.txt"):
        self.config_path = config_path
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from txt file."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Parse key=value pairs
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Convert boolean strings
                    if value.lower() in ('true', 'false'):
                        value = value.lower() == 'true'
                    # Convert numeric strings
                    elif value.isdigit():
                        value = int(value)
                    
                    self.config[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        return self.config.get(key, default)
    
    def get_schedule_time(self) -> str:
        """Get scheduled execution time (primary schedule)."""
        return self.get('SCHEDULE_TIME', '06:00')

    def get_schedule_times(self) -> List[str]:
        """Get all scheduled execution times as a list."""
        # Check if SCHEDULE_TIMES is configured
        times_str = self.get('SCHEDULE_TIMES', '')
        if times_str:
            return [time.strip() for time in times_str.split(',') if time.strip()]
        # Fallback to single SCHEDULE_TIME
        return [self.get_schedule_time()]
    
    def get_timezone(self) -> str:
        """Get timezone setting."""
        return self.get('TIMEZONE', 'Asia/Seoul')
    
    def get_source_directory(self) -> str:
        """Get source directory path."""
        return self.get('SOURCE_DIRECTORY', '../data')
    
    def get_folder_pattern(self) -> str:
        """Get folder naming pattern."""
        return self.get('FOLDER_PATTERN', '%Y%m%d')
    
    def get_target_ip(self) -> str:
        """Get target IP address."""
        return self.get('TARGET_IP', '')
    
    def get_target_directory(self) -> str:
        """Get target directory path."""
        return self.get('TARGET_DIRECTORY', '')
    
    def get_protocol(self) -> str:
        """Get transfer protocol."""
        return self.get('PROTOCOL', 'scp')

    def get_port(self) -> int:
        """Get target port number."""
        return self.get('PORT', 22)

    def get_username(self) -> str:
        """Get target username."""
        return self.get('USERNAME', '')
    
    def get_password(self) -> str:
        """Get target password."""
        return self.get('PASSWORD', '')

    def get_password_fallbacks(self) -> List[str]:
        """Get password fallbacks as a list."""
        fallbacks_str = self.get('PASSWORD_FALLBACKS', '')
        if not fallbacks_str:
            return []
        return [pwd.strip() for pwd in fallbacks_str.split(',') if pwd.strip()]

    def get_all_passwords(self) -> List[str]:
        """Get all passwords (primary + fallbacks) as a list."""
        passwords = []
        primary = self.get_password()
        if primary:
            passwords.append(primary)
        passwords.extend(self.get_password_fallbacks())
        return passwords
    
    def get_ssh_key_path(self) -> str:
        """Get SSH key path."""
        return self.get('SSH_KEY_PATH', '')
    
    def is_dry_run(self) -> bool:
        """Check if dry run mode is enabled."""
        return self.get('DRY_RUN', False)
    
    def get_retry_attempts(self) -> int:
        """Get number of retry attempts."""
        return self.get('RETRY_ATTEMPTS', 3)
    
    def get_retry_delay(self) -> int:
        """Get retry delay in seconds."""
        return self.get('RETRY_DELAY', 30)
    
    def should_delete_after_transfer(self) -> bool:
        """Check if source should be deleted after transfer."""
        return self.get('DELETE_AFTER_TRANSFER', False)
    
    def get_log_level(self) -> str:
        """Get logging level."""
        return self.get('LOG_LEVEL', 'INFO')


if __name__ == "__main__":
    # Test configuration parsing
    config = ConfigParser()
    print("Configuration loaded:")
    print(f"Schedule time: {config.get_schedule_time()}")
    print(f"Source directory: {config.get_source_directory()}")
    print(f"Target IP: {config.get_target_ip()}")
    print(f"Protocol: {config.get_protocol()}")
    print(f"Dry run: {config.is_dry_run()}")