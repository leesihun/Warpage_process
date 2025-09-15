"""
Scheduler for data auto transfer system.
Handles daily scheduled transfers at specified time.
"""

import schedule
import time
import threading
import signal
import sys
from datetime import datetime
from typing import Callable, Optional
import logging


class TransferScheduler:
    """Scheduler for automated daily transfers."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.running = False
        self.scheduler_thread = None
        self.stop_event = threading.Event()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def schedule_daily_transfer(self, time_str: str, transfer_function: Callable):
        """
        Schedule daily transfer at specified time.
        
        Args:
            time_str: Time in HH:MM format (e.g., "06:00")
            transfer_function: Function to call for transfer
        """
        try:
            # Validate time format
            datetime.strptime(time_str, "%H:%M")
            
            # Schedule the job
            schedule.every().day.at(time_str).do(self._safe_transfer_wrapper, transfer_function)
            
            self.logger.info(f"Transfer scheduled for {time_str} daily")
            
        except ValueError as e:
            self.logger.error(f"Invalid time format '{time_str}': {e}")
            raise
    
    def _safe_transfer_wrapper(self, transfer_function: Callable):
        """
        Wrapper for transfer function with error handling.
        
        Args:
            transfer_function: Function to execute
        """
        try:
            self.logger.info("Executing scheduled transfer")
            transfer_function()
            self.logger.info("Scheduled transfer completed")
        except Exception as e:
            self.logger.error(f"Scheduled transfer failed: {e}")
    
    def start(self, blocking: bool = True):
        """
        Start the scheduler.
        
        Args:
            blocking: If True, block current thread. If False, run in background.
        """
        if self.running:
            self.logger.warning("Scheduler is already running")
            return
        
        self.running = True
        self.stop_event.clear()
        
        if blocking:
            self._run_scheduler()
        else:
            self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.scheduler_thread.start()
        
        self.logger.info("Scheduler started")
    
    def stop(self):
        """Stop the scheduler."""
        if not self.running:
            return
        
        self.logger.info("Stopping scheduler...")
        self.running = False
        self.stop_event.set()
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        schedule.clear()
        self.logger.info("Scheduler stopped")
    
    def _run_scheduler(self):
        """Main scheduler loop."""
        self.logger.info("Scheduler loop started")
        
        while self.running and not self.stop_event.is_set():
            try:
                schedule.run_pending()
                
                # Check every 30 seconds
                if self.stop_event.wait(30):
                    break
                    
            except Exception as e:
                self.logger.error(f"Scheduler error: {e}")
                # Continue running even if there's an error
                time.sleep(60)  # Wait a minute before retrying
        
        self.logger.info("Scheduler loop ended")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)
    
    def get_next_run_time(self) -> Optional[datetime]:
        """Get the next scheduled run time."""
        jobs = schedule.get_jobs()
        if jobs:
            next_run = min(job.next_run for job in jobs)
            return next_run
        return None
    
    def list_jobs(self) -> list:
        """List all scheduled jobs."""
        jobs = []
        for job in schedule.get_jobs():
            jobs.append({
                'job': str(job.job_func),
                'next_run': job.next_run,
                'interval': job.interval,
                'unit': job.unit
            })
        return jobs
    
    def run_now(self, transfer_function: Callable):
        """
        Run transfer immediately (for testing).
        
        Args:
            transfer_function: Function to execute
        """
        self.logger.info("Running transfer immediately")
        self._safe_transfer_wrapper(transfer_function)


class OneTimeScheduler:
    """Simple one-time execution scheduler."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
    
    def run_at_time(self, time_str: str, transfer_function: Callable):
        """
        Run transfer function at specified time today.
        
        Args:
            time_str: Time in HH:MM format
            transfer_function: Function to execute
        """
        try:
            target_time = datetime.strptime(time_str, "%H:%M").time()
            now = datetime.now()
            target_datetime = datetime.combine(now.date(), target_time)
            
            # If target time has passed today, schedule for tomorrow
            if target_datetime <= now:
                self.logger.info(f"Target time {time_str} has passed today, will not execute")
                return False
            
            wait_seconds = (target_datetime - now).total_seconds()
            self.logger.info(f"Waiting {wait_seconds:.0f} seconds until {time_str}")
            
            time.sleep(wait_seconds)
            
            self.logger.info("Executing scheduled transfer")
            transfer_function()
            
            return True
            
        except ValueError as e:
            self.logger.error(f"Invalid time format '{time_str}': {e}")
            return False
        except Exception as e:
            self.logger.error(f"Scheduled execution failed: {e}")
            return False


if __name__ == "__main__":
    # Test scheduler functionality
    import logging
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    def test_transfer():
        print("Test transfer function executed!")
        logger.info("Test transfer completed")
    
    # Test immediate execution
    scheduler = TransferScheduler(logger)
    
    print("Testing immediate execution...")
    scheduler.run_now(test_transfer)
    
    # Test scheduling (uncomment to test actual scheduling)
    # print("Testing daily scheduling...")
    # scheduler.schedule_daily_transfer("14:30", test_transfer)
    # 
    # print("Starting scheduler (Ctrl+C to stop)...")
    # try:
    #     scheduler.start(blocking=True)
    # except KeyboardInterrupt:
    #     print("Interrupted by user")
    # finally:
    #     scheduler.stop()
    
    print("Scheduler test completed")