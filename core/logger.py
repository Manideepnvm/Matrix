# core/logger.py

import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Optional
import traceback
import json


# Configuration
LOG_DIR = "logs"
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
BACKUP_COUNT = 5
LOG_LEVEL = logging.INFO


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record):
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        
        # Format the message
        result = super().format(record)
        
        # Reset levelname for other handlers
        record.levelname = levelname
        
        return result


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'extra_data'):
            log_data['extra'] = record.extra_data
        
        return json.dumps(log_data)


class MatrixLogger:
    """Enhanced logger with multiple outputs and rotation"""
    
    def __init__(self, name: str = "Matrix", log_dir: str = LOG_DIR):
        self.name = name
        self.log_dir = Path(log_dir)
        self.logger = logging.getLogger(name)
        self.logger.setLevel(LOG_LEVEL)
        
        # Create log directory
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Setup handlers
        self._setup_file_handler()
        self._setup_console_handler()
        self._setup_error_handler()
        self._setup_json_handler()
        
        self.logger.info(f"Logger '{name}' initialized")
    
    def _setup_file_handler(self):
        """Setup rotating file handler for general logs"""
        log_file = self.log_dir / f"matrix_{datetime.now().strftime('%Y-%m-%d')}.log"
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=MAX_LOG_SIZE,
            backupCount=BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(module)s.%(funcName)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
    
    def _setup_console_handler(self):
        """Setup colored console handler"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        formatter = ColoredFormatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
    
    def _setup_error_handler(self):
        """Setup separate handler for errors"""
        error_file = self.log_dir / f"errors_{datetime.now().strftime('%Y-%m')}.log"
        
        error_handler = RotatingFileHandler(
            error_file,
            maxBytes=MAX_LOG_SIZE,
            backupCount=BACKUP_COUNT,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(module)s.%(funcName)s:%(lineno)d]\n'
            'Message: %(message)s\n'
            '%(exc_info)s\n' + '-' * 80,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        error_handler.setFormatter(formatter)
        
        self.logger.addHandler(error_handler)
    
    def _setup_json_handler(self):
        """Setup JSON handler for structured logging"""
        json_file = self.log_dir / f"matrix_{datetime.now().strftime('%Y-%m-%d')}.json"
        
        json_handler = RotatingFileHandler(
            json_file,
            maxBytes=MAX_LOG_SIZE,
            backupCount=BACKUP_COUNT,
            encoding='utf-8'
        )
        json_handler.setLevel(logging.DEBUG)
        json_handler.setFormatter(JSONFormatter())
        
        self.logger.addHandler(json_handler)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message, extra={'extra_data': kwargs} if kwargs else None)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, extra={'extra_data': kwargs} if kwargs else None)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, extra={'extra_data': kwargs} if kwargs else None)
    
    def error(self, message: str, exc_info: bool = True, **kwargs):
        """Log error message"""
        self.logger.error(message, exc_info=exc_info, extra={'extra_data': kwargs} if kwargs else None)
    
    def critical(self, message: str, exc_info: bool = True, **kwargs):
        """Log critical message"""
        self.logger.critical(message, exc_info=exc_info, extra={'extra_data': kwargs} if kwargs else None)
    
    def exception(self, message: str, **kwargs):
        """Log exception with traceback"""
        self.logger.exception(message, extra={'extra_data': kwargs} if kwargs else None)


# Global logger instance
_global_logger: Optional[MatrixLogger] = None


def get_logger(name: str = "Matrix") -> MatrixLogger:
    """Get or create global logger instance"""
    global _global_logger
    if _global_logger is None:
        _global_logger = MatrixLogger(name)
    return _global_logger


# Convenience functions for backward compatibility
def log_debug(message: str, **kwargs):
    """Log debug message"""
    logger = get_logger()
    logger.debug(message, **kwargs)


def log_info(message: str, **kwargs):
    """Log info message"""
    logger = get_logger()
    logger.info(message, **kwargs)


def log_warning(message: str, **kwargs):
    """Log warning message"""
    logger = get_logger()
    logger.warning(message, **kwargs)


def log_error(message: str, exc_info: bool = False, **kwargs):
    """Log error message"""
    logger = get_logger()
    if exc_info:
        logger.exception(message, **kwargs)
    else:
        logger.error(message, exc_info=False, **kwargs)


def log_critical(message: str, **kwargs):
    """Log critical message"""
    logger = get_logger()
    logger.critical(message, **kwargs)


def log_exception(message: str, **kwargs):
    """Log exception with full traceback"""
    logger = get_logger()
    logger.exception(message, **kwargs)


# Context manager for logging execution time
class LogExecutionTime:
    """Context manager to log execution time of code blocks"""
    
    def __init__(self, operation_name: str, logger: Optional[MatrixLogger] = None):
        self.operation_name = operation_name
        self.logger = logger or get_logger()
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.debug(f"Started: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type is None:
            self.logger.info(f"Completed: {self.operation_name} (took {duration:.2f}s)")
        else:
            self.logger.error(
                f"Failed: {self.operation_name} (took {duration:.2f}s) - {exc_type.__name__}: {exc_val}"
            )
        
        return False  # Don't suppress exceptions


# Decorator for logging function calls
def log_function_call(func):
    """Decorator to log function calls with parameters and return values"""
    def wrapper(*args, **kwargs):
        logger = get_logger()
        func_name = func.__name__
        
        logger.debug(f"Calling {func_name} with args={args}, kwargs={kwargs}")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func_name} returned: {result}")
            return result
        except Exception as e:
            logger.error(f"{func_name} raised exception: {e}", exc_info=True)
            raise
    
    return wrapper


# Function to clean old log files
def clean_old_logs(days_to_keep: int = 30):
    """Remove log files older than specified days"""
    logger = get_logger()
    log_dir = Path(LOG_DIR)
    
    if not log_dir.exists():
        return
    
    cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
    removed_count = 0
    
    for log_file in log_dir.glob("*.log*"):
        if log_file.stat().st_mtime < cutoff_date:
            try:
                log_file.unlink()
                removed_count += 1
            except Exception as e:
                logger.warning(f"Failed to remove old log file {log_file}: {e}")
    
    if removed_count > 0:
        logger.info(f"Cleaned up {removed_count} old log files")


# Initialize default logger
def initialize_logging(log_level: str = "INFO", log_dir: str = LOG_DIR):
    """Initialize logging system with custom settings"""
    global LOG_LEVEL, LOG_DIR
    
    LOG_LEVEL = getattr(logging, log_level.upper(), logging.INFO)
    LOG_DIR = log_dir
    
    # Create log directory
    Path(LOG_DIR).mkdir(parents=True, exist_ok=True)
    
    # Get or create logger
    logger = get_logger()
    logger.logger.setLevel(LOG_LEVEL)
    
    log_info(f"Logging initialized - Level: {log_level}, Directory: {log_dir}")
    
    return logger


# Auto-initialize on import
if __name__ != "__main__":
    get_logger()