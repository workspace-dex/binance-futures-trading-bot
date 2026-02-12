"""
Logging Configuration
Sets up logging for the trading bot
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path


def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "logs",
    log_to_console: bool = True,
    log_to_file: bool = True
) -> logging.Logger:
    """
    Setup logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_dir: Directory for log files
        log_to_console: Whether to log to console
        log_to_file: Whether to log to file
        
    Returns:
        Root logger instance
    """
    # Create logs directory
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers = []
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # File handler
    if log_to_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = log_path / f"trading_bot_{timestamp}.log"
        
        file_handler = logging.FileHandler(log_file, mode='a')
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
