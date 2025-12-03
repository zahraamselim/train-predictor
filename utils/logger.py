from datetime import datetime

class Logger:
    """Centralized logging utility"""
    
    @staticmethod
    def timestamp():
        return datetime.now().strftime("%H:%M:%S")
    
    @staticmethod
    def log(message, prefix=""):
        if prefix:
            print(f"[{Logger.timestamp()}] {prefix}: {message}")
        else:
            print(f"[{Logger.timestamp()}] {message}")
    
    @staticmethod
    def section(title):
        print(f"\n[{Logger.timestamp()}] {title}")