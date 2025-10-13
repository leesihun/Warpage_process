"""
Logging configuration for data auto transfer system.
Provides structured logging with file rotation and console output.
"""

import logging
import logging.handlers
import os
from datetime import datetime
from typing import Optional


class TransferLogger:
    """Enhanced logger for transfer operations."""
    
    def __init__(self, log_level: str = "INFO", log_file: str = "transfer.log", 
                 max_file_size: int = 10 * 1024 * 1024, backup_count: int = 5):
        """
        Initialize logger with file rotation.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Log file name
            max_file_size: Maximum log file size in bytes (default: 10MB)
            backup_count: Number of backup files to keep
        """
        self.log_file = log_file
        self.logger = logging.getLogger("data_autotransfer")
        self.logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Create file handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=max_file_size, backupCount=backup_count
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
    
    def get_logger(self) -> logging.Logger:
        """Get the configured logger instance."""
        return self.logger
    
    def log_transfer_start(self, source_path: str, target_ip: str, target_path: str, protocol: str):
        """Log transfer operation start."""
        self.logger.info(f"Starting transfer: {source_path} -> {target_ip}:{target_path} ({protocol})")
    
    def log_transfer_success(self, source_path: str, target_ip: str, target_path: str, duration: float):
        """Log successful transfer."""
        self.logger.info(f"Transfer completed successfully in {duration:.2f}s: {source_path} -> {target_ip}:{target_path}")
    
    def log_transfer_failure(self, source_path: str, target_ip: str, target_path: str, error: str):
        """Log failed transfer."""
        self.logger.error(f"Transfer failed: {source_path} -> {target_ip}:{target_path} - {error}")
    
    def log_folder_not_found(self, folder_path: str):
        """Log when yesterday's folder is not found."""
        self.logger.info(f"Yesterday's folder not found, skipping transfer: {folder_path}")
    
    def log_config_loaded(self, config_file: str):
        """Log configuration loading."""
        self.logger.info(f"Configuration loaded from: {config_file}")
    
    def log_scheduler_start(self, schedule_time: str):
        """Log scheduler startup."""
        self.logger.info(f"Scheduler started - transfers scheduled for {schedule_time} daily")
    
    def log_retry_attempt(self, attempt: int, max_attempts: int, delay: int):
        """Log retry attempt."""
        self.logger.warning(f"Retry attempt {attempt}/{max_attempts} in {delay} seconds")
    
    def log_dry_run(self, operation: str):
        """Log dry run operations."""
        self.logger.info(f"DRY RUN: {operation}")
    
    def log_system_info(self, info: dict):
        """Log system information at startup."""
        self.logger.info("=== Data Auto Transfer System Started ===")
        for key, value in info.items():
            self.logger.info(f"{key}: {value}")
        self.logger.info("==========================================")


class OperationLogger:
    """Context manager for logging operations with timing."""
    
    def __init__(self, logger: logging.Logger, operation: str, level: int = logging.INFO):
        self.logger = logger
        self.operation = operation
        self.level = level
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.log(self.level, f"Starting: {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type is None:
            self.logger.log(self.level, f"Completed: {self.operation} (took {duration:.2f}s)")
        else:
            self.logger.error(f"Failed: {self.operation} after {duration:.2f}s - {exc_val}")
        
        return False  # Don't suppress exceptions


def setup_logger(log_level: str = "INFO", log_file: str = "transfer.log") -> logging.Logger:
    """
    Setup and return a configured logger.
    
    Args:
        log_level: Logging level
        log_file: Log file name
        
    Returns:
        Configured logger instance
    """
    transfer_logger = TransferLogger(log_level, log_file)
    return transfer_logger.get_logger()


if __name__ == "__main__":
    # Test logging functionality
    logger = setup_logger("DEBUG", "test_transfer.log")
    
    logger.info("Testing logger functionality")
    logger.debug("Debug message")
    logger.warning("Warning message")
    logger.error("Error message")
    
    # Test operation logger
    with OperationLogger(logger, "Test operation"):
        import time
        time.sleep(1)
        logger.info("Operation in progress")
    
    print("Logger test completed. Check test_transfer.log file.")