"""
Login window for user authentication - Clean version without default credentials
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
from views.base_window import BaseWindow
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class LoginWindow(BaseWindow):
    """Clean login window for user authentication"""
    
    def __init__(self, controller, on_login_success: Callable):
        """Initialize login window"""
        super().__init__(
            title="Login",
            width=settings.LOGIN_WINDOW_WIDTH,
            height=settings.LOGIN_WINDOW_HEIGHT,
            resizable=False
        )
        
        self.controller = controller
        self.on_login_success = on_login_success
        
        # Initialize UI components
        self.username_entry: Optional[ttk.Entry] = None
        self.password_entry: Optional[ttk.Entry] = None
        
        self.setup_login_ui()
        logger.info("Clean login window initialized")
    
    def setup_login_ui(self) -> None:
        """Setup clean login user interface"""
        # Create main frame
        main_frame = self.create_main_frame(padding=40, style='Custom.TFrame')
        
        # Create header
        self.create_header(main_frame, settings.APP_NAME, 
                         "Please sign in to continue")
        
        # Create login form
        self.create_login_form(main_frame)
        
        # Focus on username entry
        self.username_entry.focus()
        
        # Bind Enter key to login
        self.root.bind('<Return>', lambda e: self.handle_login())
    
    def create_login_form(self, parent: ttk.Frame) -> None:
        """Create clean login form with username and password fields"""
        # Form container
        form_frame = ttk.Frame(parent, style='Card.TFrame', padding=30)
        form_frame.grid(row=1, column=0, sticky='ew', pady=40)
        form_frame.columnconfigure(1, weight=1)
        
        # Username field
        ttk.Label(form_frame, text="Username:", style='Custom.TLabel').grid(
            row=0, column=0, sticky='w', padx=(0, 15), pady=10
        )
        self.username_entry = ttk.Entry(form_frame, width=25, style='Custom.TEntry', font=('Arial', 12))
        self.username_entry.grid(row=0, column=1, sticky='ew', pady=10, ipady=5)
        
        # Password field
        ttk.Label(form_frame, text="Password:", style='Custom.TLabel').grid(
            row=1, column=0, sticky='w', padx=(0, 15), pady=10
        )
        self.password_entry = ttk.Entry(form_frame, width=25, style='Custom.TEntry', show='*', font=('Arial', 12))
        self.password_entry.grid(row=1, column=1, sticky='ew', pady=10, ipady=5)
        
        # Login button
        login_btn = ttk.Button(
            form_frame, 
            text="🔐 Sign In", 
            command=self.handle_login,
            style='Success.TButton'
        )
        login_btn.grid(row=2, column=0, columnspan=2, pady=30, sticky='ew')
        
        # Professional footer
        footer_text = f"© {settings.APP_NAME} v{settings.APP_VERSION} - Secure Library Management"
        footer_label = ttk.Label(
            parent,
            text=footer_text,
            style='Info.TLabel'
        )
        footer_label.grid(row=2, column=0, pady=20)
    
    def handle_login(self) -> None:
        """Handle login button click"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        # Validate input
        if not username or not password:
            self.show_message(
                "Please enter both username and password.", 
                'error', 
                "Login Required"
            )
            return
        
        # Clear password field for security
        self.password_entry.delete(0, tk.END)
        
        try:
            # Attempt authentication
            if self.controller.login(username, password):
                user = self.controller.current_user
                logger.info(f"Successful login: {user['username']} ({user['role']})")
                
                # Show success message
                self.show_message(
                    f"Welcome, {user['username']}!\\n"
                    f"Role: {user['role'].title()}",
                    'success',
                    "Login Successful"
                )
                
                # Close login window and proceed
                self.root.destroy()
                self.on_login_success()
                
            else:
                # Authentication failed
                logger.warning(f"Failed login attempt: {username}")
                self.show_message(
                    "Invalid username or password.\\n"
                    "Please check your credentials and try again.",
                    'error',
                    "Login Failed"
                )
                
                # Focus back to username for retry
                self.username_entry.focus()
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            self.show_message(
                f"An error occurred during login:\\n{str(e)}",
                'error',
                "Login Error"
            )
    
    def reset_form(self) -> None:
        """Reset login form"""
        try:
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            self.username_entry.focus()
        except (AttributeError, tk.TclError):
            pass
    
    def pre_fill_credentials(self, username: str, password: str = '') -> None:
        """Pre-fill credentials (for testing/demo purposes)"""
        try:
            self.username_entry.delete(0, tk.END)
            self.username_entry.insert(0, username)
            
            if password:
                self.password_entry.delete(0, tk.END)
                self.password_entry.insert(0, password)
                
            # Focus on password if username is filled
            if username and not password:
                self.password_entry.focus()
        except (AttributeError, tk.TclError):
            pass


# Quick access functions for testing (can be removed in production)
def create_admin_login_window(controller, on_success):
    """Create login window pre-filled with admin credentials"""
    window = LoginWindow(controller, on_success)
    window.pre_fill_credentials(settings.DEFAULT_ADMIN_USERNAME)
    return window


def create_librarian_login_window(controller, on_success):
    """Create login window pre-filled with librarian credentials"""
    window = LoginWindow(controller, on_success)
    window.pre_fill_credentials(settings.DEFAULT_LIBRARIAN_USERNAME)
    return window
