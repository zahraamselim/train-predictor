from datetime import datetime


class Logger:
    """Simple logger for simulation output"""
    
    verbose = True
    
    @staticmethod
    def log(message):
        """Log a standard message"""
        if Logger.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {message}")
    
    @staticmethod
    def section(title):
        """Log a section header"""
        if Logger.verbose:
            print("\n" + "=" * 80)
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {title}")
            print("=" * 80)
    
    @staticmethod
    def set_verbose(verbose):
        """Enable or disable verbose logging"""
        Logger.verbose = verbose