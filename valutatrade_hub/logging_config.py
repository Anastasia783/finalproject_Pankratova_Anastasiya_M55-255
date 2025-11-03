import logging
import logging.handlers
import os
from typing import Optional
from valutatrade_hub.infra.settings import settings


def setup_logging():
    """Setup logging configuration"""
    log_dir = settings.get("log_dir", "logs")
    log_level = settings.get("log_level", "INFO").upper()
    log_format = settings.get("log_format", "string")
    
    # Ensure log directory exists
    os.makedirs(log_dir, exist_ok=True)
    
    # Create formatter
    if log_format == "json":
        formatter = logging.Formatter(
            '{"time": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "message": "%(message)s", "data": %(data)s}',
            datefmt="%Y-%m-%dT%H:%M:%S"
        )
    else:
        formatter = logging.Formatter(
            '%(levelname)s %(asctime)s %(name)s %(message)s',
            datefmt="%Y-%m-%dT%H:%M:%S"
        )
    
    # Create file handler with rotation
    log_file = os.path.join(log_dir, "actions.log")
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add our handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get logger with given name"""
    return logging.getLogger(name)


# Initialize logging when module is imported
setup_logging()