#!/usr/bin/env python3
"""
Library Management System - Main Application Entry Point
A comprehensive, role-based library management application

Usage:
    python src/main.py
    or
    python -m src.main

Requirements:
    - Python 3.6+
    - bcrypt library
"""

import sys
import os
import logging
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    # Import required modules
    import tkinter as tk
    from tkinter import messagebox
    
    from controllers.library_controller import LibraryController
    from views.login_window import LoginWindow
    from views.dashboard import MainDashboard
    from config.settings import settings
    from utils.logger import get_logger
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("📦 Please ensure all required packages are installed:")
    print("   pip install bcrypt")
    sys.exit(1)

# Configure logging
logger = get_logger(__name__)


class LibraryManagementApp:
    """Main application class"""
    
    def __init__(self):
        """Initialize the application"""
        logger.info("=== Library Management System Starting ===")
        
        # Initialize controller
        try:
            self.controller = LibraryController()
            logger.info("Application controller initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize controller: {e}")
            messagebox.showerror("Startup Error", 
                               f"Failed to initialize application:\n{str(e)}")
            sys.exit(1)
    
    def run(self) -> None:
        """Run the main application"""
        try:
            # Show login window
            def on_login_success():
                """Handle successful login"""
                try:
                    # Create and show main dashboard
                    dashboard = MainDashboard(self.controller)
                    dashboard.run()
                    
                except Exception as e:
                    logger.error(f"Dashboard error: {e}")
                    messagebox.showerror("Dashboard Error", 
                                       f"Failed to open dashboard:\n{str(e)}")
            
            # Create and show login window
            login_window = LoginWindow(self.controller, on_login_success)
            login_window.run()
            
        except Exception as e:
            logger.error(f"Application error: {e}")
            messagebox.showerror("Application Error", 
                               f"An unexpected error occurred:\n{str(e)}")
        finally:
            logger.info("=== Library Management System Closed ===")
    
    def validate_dependencies(self) -> bool:
        """Validate all required dependencies"""
        try:
            import bcrypt
            import sqlite3
            import tkinter
            logger.info("All dependencies validated successfully")
            return True
        except ImportError as e:
            logger.error(f"Missing dependency: {e}")
            return False
    
    def show_startup_info(self) -> None:
        """Show startup information"""
        print("🚀 Starting Library Management System...")
        print(f"📚 {settings.APP_NAME} v{settings.APP_VERSION}")
        print(f"📂 Database: {settings.get_database_path()}")
        print(f"📄 Logs: {settings.get_log_path()}")
        print("=" * 60)


def main():
    """Main entry point"""
    try:
        # Create and run application
        app = LibraryManagementApp()
        
        # Show startup info
        app.show_startup_info()
        
        # Validate dependencies
        if not app.validate_dependencies():
            print("❌ Dependency validation failed!")
            print("📦 Please install required packages: pip install bcrypt")
            return 1
        
        # Run application
        app.run()
        
        print("👋 Library Management System closed. Goodbye!")
        return 0
        
    except KeyboardInterrupt:
        print("\n⏹️ Application interrupted by user")
        return 130
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        logger.error(f"Fatal application error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
