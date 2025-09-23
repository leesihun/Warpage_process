"""
Main script for data auto transfer system.
Orchestrates daily automated transfers of dated folders to remote systems.
"""

import os
import sys
import time
from datetime import datetime
import argparse

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config_parser import ConfigParser
from date_utils import DateUtils
from transfer_manager import TransferManager
from logger import TransferLogger, OperationLogger
from scheduler import TransferScheduler


class DataAutoTransfer:
    """Main class for data auto transfer system."""
    
    def __init__(self, config_file: str = "config.txt"):
        """
        Initialize the auto transfer system.
        
        Args:
            config_file: Path to configuration file
        """
        # Load configuration
        self.config = ConfigParser(config_file)
        
        # Setup logging
        self.transfer_logger = TransferLogger(
            log_level=self.config.get_log_level(),
            log_file="data_transfer.log"
        )
        self.logger = self.transfer_logger.get_logger()
        
        # Initialize components
        self.transfer_manager = TransferManager(self.logger)
        self.scheduler = TransferScheduler(self.logger)
        
        # Log system startup
        self._log_system_info()
    
    def _log_system_info(self):
        """Log system information at startup."""
        info = {
            "Python Version": sys.version.split()[0],
            "System": os.name,
            "Working Directory": os.getcwd(),
            "Config File": self.config.config_path,
            "Source Directory": self.config.get_source_directory(),
            "Target IP": self.config.get_target_ip(),
            "Protocol": self.config.get_protocol(),
            "Port": self.config.get_port(),
            "Schedule Time": self.config.get_schedule_time(),
            "Dry Run Mode": self.config.is_dry_run()
        }
        self.transfer_logger.log_system_info(info)
    
    def perform_transfer(self):
        """
        Perform a single transfer operation.
        Finds yesterday's folder and transfers it if it exists.
        """
        with OperationLogger(self.logger, "Daily transfer operation"):
            try:
                # Find yesterday's folder
                source_dir = self.config.get_source_directory()
                folder_pattern = self.config.get_folder_pattern()
                
                yesterday_folder = DateUtils.find_yesterday_folder(source_dir, folder_pattern)
                
                if not yesterday_folder:
                    yesterday_name = DateUtils.get_yesterday_date(folder_pattern)
                    self.transfer_logger.log_folder_not_found(f"{source_dir}/{yesterday_name}")
                    return True  # Not an error, just nothing to transfer
                
                # Perform transfer with retry logic
                return self._transfer_with_retry(yesterday_folder)
                
            except Exception as e:
                self.logger.error(f"Transfer operation failed: {e}")
                return False
    
    def _transfer_with_retry(self, source_path: str) -> bool:
        """
        Transfer folder with retry logic.
        
        Args:
            source_path: Path to source folder
            
        Returns:
            True if transfer successful, False otherwise
        """
        max_attempts = self.config.get_retry_attempts()
        retry_delay = self.config.get_retry_delay()
        
        for attempt in range(1, max_attempts + 1):
            try:
                # Log transfer start
                self.transfer_logger.log_transfer_start(
                    source_path,
                    self.config.get_target_ip(),
                    self.config.get_target_directory(),
                    self.config.get_protocol()
                )
                
                start_time = time.time()
                
                # Perform transfer with password fallbacks
                success, message = self.transfer_manager.transfer_folder(
                    source_path=source_path,
                    target_ip=self.config.get_target_ip(),
                    target_path=self.config.get_target_directory(),
                    protocol=self.config.get_protocol(),
                    username=self.config.get_username(),
                    password=self.config.get_password(),
                    ssh_key_path=self.config.get_ssh_key_path(),
                    dry_run=self.config.is_dry_run(),
                    password_fallbacks=self.config.get_password_fallbacks()
                )
                
                duration = time.time() - start_time
                
                if success:
                    # Log success
                    self.transfer_logger.log_transfer_success(
                        source_path,
                        self.config.get_target_ip(),
                        self.config.get_target_directory(),
                        duration
                    )
                    
                    # Delete source if configured
                    if self.config.should_delete_after_transfer() and not self.config.is_dry_run():
                        self._delete_source_folder(source_path)
                    
                    return True
                else:
                    # Log failure
                    self.transfer_logger.log_transfer_failure(
                        source_path,
                        self.config.get_target_ip(),
                        self.config.get_target_directory(),
                        message
                    )
                    
                    # Retry if not last attempt
                    if attempt < max_attempts:
                        self.transfer_logger.log_retry_attempt(attempt, max_attempts, retry_delay)
                        time.sleep(retry_delay)
                    else:
                        return False
                        
            except Exception as e:
                self.logger.error(f"Transfer attempt {attempt} failed: {e}")
                
                if attempt < max_attempts:
                    self.transfer_logger.log_retry_attempt(attempt, max_attempts, retry_delay)
                    time.sleep(retry_delay)
                else:
                    return False
        
        return False
    
    def _delete_source_folder(self, source_path: str):
        """
        Delete source folder after successful transfer.
        
        Args:
            source_path: Path to source folder to delete
        """
        try:
            import shutil
            shutil.rmtree(source_path)
            self.logger.info(f"Source folder deleted: {source_path}")
        except Exception as e:
            self.logger.error(f"Failed to delete source folder {source_path}: {e}")
    
    def test_connection(self) -> bool:
        """
        Test connection to target system.
        
        Returns:
            True if connection successful, False otherwise
        """
        self.logger.info("Testing connection to target system...")
        
        # Test with primary password first
        success, message = self.transfer_manager.test_connection(
            target_ip=self.config.get_target_ip(),
            protocol=self.config.get_protocol(),
            username=self.config.get_username(),
            password=self.config.get_password(),
            ssh_key_path=self.config.get_ssh_key_path()
        )

        # If primary password fails, try fallbacks
        if not success:
            fallback_passwords = self.config.get_password_fallbacks()
            for i, fallback_pwd in enumerate(fallback_passwords):
                self.logger.info(f"Testing connection with password fallback {i+1}")
                success, message = self.transfer_manager.test_connection(
                    target_ip=self.config.get_target_ip(),
                    protocol=self.config.get_protocol(),
                    username=self.config.get_username(),
                    password=fallback_pwd,
                    ssh_key_path=self.config.get_ssh_key_path()
                )
                if success:
                    message += f" (using password fallback {i+1})"
                    break
        
        if success:
            self.logger.info(f"Connection test successful: {message}")
        else:
            self.logger.error(f"Connection test failed: {message}")
        
        return success
    
    def run_scheduled(self):
        """Run the scheduler for daily automated transfers."""
        try:
            # Get schedule times - use multiple times if configured, otherwise single time
            schedule_times = self.config.get_schedule_times()

            if len(schedule_times) == 1:
                # Single schedule time
                schedule_time = schedule_times[0]
                self.scheduler.schedule_daily_transfer(schedule_time, self.perform_transfer)
                self.transfer_logger.log_scheduler_start(schedule_time)
            else:
                # Multiple schedule times
                self.scheduler.schedule_multiple_daily_transfers(schedule_times, self.perform_transfer)
                self.logger.info(f"Scheduled transfers for: {', '.join(schedule_times)}")

            # Display next run time
            next_run = self.scheduler.get_next_run_time()
            if next_run:
                self.logger.info(f"Next transfer scheduled for: {next_run}")

            # Start scheduler (blocking)
            self.logger.info("Starting scheduler... Press Ctrl+C to stop")
            self.scheduler.start(blocking=True)
            
        except KeyboardInterrupt:
            self.logger.info("Interrupted by user")
        except Exception as e:
            self.logger.error(f"Scheduler error: {e}")
        finally:
            self.scheduler.stop()
    
    def run_once(self):
        """Run transfer once immediately."""
        self.logger.info("Running transfer once...")
        success = self.perform_transfer()
        
        if success:
            self.logger.info("Single transfer completed successfully")
        else:
            self.logger.error("Single transfer failed")
        
        return success


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Data Auto Transfer System")
    parser.add_argument("--config", "-c", default="config.txt", 
                       help="Configuration file path (default: config.txt)")
    parser.add_argument("--once", action="store_true", 
                       help="Run transfer once immediately instead of scheduling")
    parser.add_argument("--test", action="store_true", 
                       help="Test connection to target system")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Enable dry run mode (overrides config)")
    
    args = parser.parse_args()
    
    try:
        # Initialize system
        transfer_system = DataAutoTransfer(args.config)
        
        # Override dry run mode if specified
        if args.dry_run:
            transfer_system.config.config['DRY_RUN'] = True
            transfer_system.logger.info("Dry run mode enabled via command line")
        
        # Test connection if requested
        if args.test:
            success = transfer_system.test_connection()
            sys.exit(0 if success else 1)
        
        # Run once or start scheduler
        if args.once:
            success = transfer_system.run_once()
            sys.exit(0 if success else 1)
        else:
            transfer_system.run_scheduled()
    
    except FileNotFoundError as e:
        print(f"Configuration file not found: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"System error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()