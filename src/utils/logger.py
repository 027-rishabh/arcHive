"""
Logging utilities for Library Management System
"""

import logging
import os
from typing import Optional
from config.settings import settings


class Logger:
    """Centralized logging configuration"""
    
    _instance: Optional['Logger'] = None
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls) -> 'Logger':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup_logger()
        return cls._instance
    
    def _setup_logger(self) -> None:
        """Setup logging configuration"""
        # Create logger
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(getattr(logging, settings.LOG_LEVEL))
        
        # Prevent duplicate handlers
        if self._logger.handlers:
            return
        
        # Create formatter
        formatter = logging.Formatter(settings.LOG_FORMAT)
        
        # File handler
        file_handler = logging.FileHandler(settings.get_log_path())
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)
    
    def get_logger(self) -> logging.Logger:
        """Get the configured logger instance"""
        return self._logger


def get_logger(name: str = __name__) -> logging.Logger:
    """Get a logger instance for the specified module"""
    logger_instance = Logger()
    logger = logging.getLogger(name)
    
    # Use the same configuration as main logger
    if not logger.handlers:
        main_logger = logger_instance.get_logger()
        for handler in main_logger.handlers:
            logger.addHandler(handler)
        logger.setLevel(main_logger.level)
    
    return logger
