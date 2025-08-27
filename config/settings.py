"""
Configuration settings for Library Management System
"""

import os
from typing import Dict, Any

class Settings:
    """Application settings and configuration"""
    
    # Database Configuration
    DATABASE_NAME: str = "library_management.db"
    DATABASE_PATH: str = os.path.join("data", DATABASE_NAME)
    
    # Application Configuration
    APP_NAME: str = "Library Management System"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Professional Library Management System with Role-based Access"
    
    # GUI Configuration
    DEFAULT_WINDOW_WIDTH: int = 1200
    DEFAULT_WINDOW_HEIGHT: int = 700
    LOGIN_WINDOW_WIDTH: int = 450
    LOGIN_WINDOW_HEIGHT: int = 350
    
    # Authentication Configuration
    DEFAULT_ADMIN_USERNAME: str = "admin"
    DEFAULT_ADMIN_PASSWORD: str = "admin123"
    DEFAULT_LIBRARIAN_USERNAME: str = "librarian"
    DEFAULT_LIBRARIAN_PASSWORD: str = "lib123"
    
    # Business Rules Configuration
    BORROWING_PERIOD_DAYS: int = 14
    DAILY_LATE_FEE: float = 0.50
    
    # Logging Configuration
    LOG_DIRECTORY: str = "logs"
    LOG_FILENAME: str = "library_system.log"
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Export Configuration
    EXPORT_DIRECTORY: str = "exports"
    EXPORT_DATE_FORMAT: str = "%Y%m%d_%H%M%S"
    
    # Color Themes
    THEMES: Dict[str, Dict[str, str]] = {
        'professional': {
            'bg_primary': '#2C3E50',      # Dark blue-gray
            'bg_secondary': '#34495E',     # Lighter blue-gray  
            'bg_accent': '#3498DB',        # Blue
            'fg_primary': '#FFFFFF',       # White
            'fg_secondary': '#BDC3C7',     # Light gray
            'success': '#27AE60',          # Green
            'warning': '#F39C12',          # Orange
            'error': '#E74C3C',           # Red
            'button_bg': '#3498DB',        # Blue
            'button_fg': '#FFFFFF',        # White
            'entry_bg': '#FFFFFF',         # White
            'entry_fg': '#2C3E50'          # Dark blue-gray
        },
        'modern': {
            'bg_primary': '#1A1A2E',       # Dark purple
            'bg_secondary': '#16213E',     # Dark blue
            'bg_accent': '#0F3460',        # Medium blue
            'fg_primary': '#E94560',       # Pink-red
            'fg_secondary': '#F5F5F5',     # Light gray
            'success': '#00D4AA',          # Teal
            'warning': '#FFB830',          # Yellow
            'error': '#FF4757',           # Red
            'button_bg': '#E94560',        # Pink-red
            'button_fg': '#FFFFFF',        # White
            'entry_bg': '#F5F5F5',         # Light gray
            'entry_fg': '#1A1A2E'          # Dark purple
        }
    }
    
    @classmethod
    def get_database_path(cls) -> str:
        """Get the full database path"""
        os.makedirs("data", exist_ok=True)
        return cls.DATABASE_PATH
    
    @classmethod
    def get_log_path(cls) -> str:
        """Get the full log path"""
        os.makedirs(cls.LOG_DIRECTORY, exist_ok=True)
        return os.path.join(cls.LOG_DIRECTORY, cls.LOG_FILENAME)
    
    @classmethod
    def get_export_directory(cls) -> str:
        """Get export directory path"""
        os.makedirs(cls.EXPORT_DIRECTORY, exist_ok=True)
        return cls.EXPORT_DIRECTORY

# Global settings instance
settings = Settings()
