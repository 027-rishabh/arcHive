"""
Base window class with common functionality for all GUI windows
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable
from views.styles import ColorScheme, StyleManager, UIHelpers
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class BaseWindow:
    """Base window class with common styling and functionality"""
    
    def __init__(self, title: str, width: int = None, height: int = None, 
                 theme: str = 'professional', resizable: bool = True):
        """Initialize base window"""
        self.root = tk.Tk()
        self.title = title
        self.width = width or settings.DEFAULT_WINDOW_WIDTH
        self.height = height or settings.DEFAULT_WINDOW_HEIGHT
        
        # Initialize styling
        self.colors = ColorScheme(theme)
        self.style_manager = StyleManager(self.root, self.colors)
        
        # Configure window
        self.setup_window(resizable)
        
        logger.info(f"BaseWindow '{title}' initialized")
    
    def setup_window(self, resizable: bool = True) -> None:
        """Setup window properties"""
        self.root.title(f"{settings.APP_NAME} - {self.title}")
        self.root.geometry(f"{self.width}x{self.height}")
        self.root.resizable(resizable, resizable)
        
        # Configure window styling
        self.root.configure(bg=self.colors.get_color('bg_primary'))
        
        # Center window on screen
        UIHelpers.center_window(self.root, self.width, self.height)
        
        # Set window icon (if available)
        try:
            self.root.iconname(settings.APP_NAME)
        except tk.TclError:
            pass  # Icon not available, skip
        
        # Configure grid weights for responsive layout
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def create_main_frame(self, padding: int = 20, style: str = 'Custom.TFrame') -> ttk.Frame:
        """Create main content frame"""
        main_frame = ttk.Frame(self.root, style=style, padding=padding)
        main_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        
        # Configure grid weights for responsive behavior
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        return main_frame
    
    def create_header(self, parent: ttk.Frame, title: str, subtitle: str = None) -> ttk.Frame:
        """Create header section with title and optional subtitle"""
        header_frame = ttk.Frame(parent, style='Custom.TFrame')
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, 20))
        header_frame.columnconfigure(0, weight=1)
        
        # Main title
        title_label = ttk.Label(header_frame, text=title, style='Heading.TLabel')
        title_label.grid(row=0, column=0, pady=(0, 5))
        
        # Subtitle (optional)
        if subtitle:
            subtitle_label = ttk.Label(header_frame, text=subtitle, style='Info.TLabel')
            subtitle_label.grid(row=1, column=0)
        
        return header_frame
    
    def create_button_frame(self, parent: ttk.Frame, buttons: list) -> ttk.Frame:
        """Create frame with multiple buttons"""
        button_frame = ttk.Frame(parent, style='Custom.TFrame')
        
        for i, (text, command, style) in enumerate(buttons):
            btn = ttk.Button(button_frame, text=text, command=command, style=style)
            btn.grid(row=0, column=i, padx=5, pady=5, sticky='ew')
            button_frame.columnconfigure(i, weight=1)
        
        return button_frame
    
    def create_form_field(self, parent: ttk.Frame, label_text: str, 
                         entry_width: int = 30, entry_style: str = 'Custom.TEntry',
                         label_style: str = 'Custom.TLabel') -> tuple:
        """Create form field with label and entry"""
        # Container frame
        field_frame = ttk.Frame(parent, style='Custom.TFrame')
        
        # Label
        label = ttk.Label(field_frame, text=label_text, style=label_style)
        label.grid(row=0, column=0, sticky='w', padx=(0, 10))
        
        # Entry
        entry = ttk.Entry(field_frame, width=entry_width, style=entry_style)
        entry.grid(row=0, column=1, sticky='ew')
        
        # Configure grid weights
        field_frame.columnconfigure(1, weight=1)
        
        return field_frame, label, entry
    
    def create_data_table(self, parent: ttk.Frame, columns: list, 
                         show_scrollbars: bool = True) -> tuple:
        """Create data table (Treeview) with optional scrollbars"""
        # Container frame
        table_frame = ttk.Frame(parent, style='Custom.TFrame')
        
        # Treeview
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', 
                           style='Custom.Treeview')
        
        # Configure columns
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, minwidth=80)
        
        if show_scrollbars:
            # Vertical scrollbar
            v_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', 
                                      command=tree.yview)
            tree.configure(yscrollcommand=v_scrollbar.set)
            
            # Horizontal scrollbar
            h_scrollbar = ttk.Scrollbar(table_frame, orient='horizontal', 
                                      command=tree.xview)
            tree.configure(xscrollcommand=h_scrollbar.set)
            
            # Grid layout
            tree.grid(row=0, column=0, sticky='nsew')
            v_scrollbar.grid(row=0, column=1, sticky='ns')
            h_scrollbar.grid(row=1, column=0, sticky='ew')
            
            # Configure grid weights
            table_frame.columnconfigure(0, weight=1)
            table_frame.rowconfigure(0, weight=1)
            
            return table_frame, tree, v_scrollbar, h_scrollbar
        else:
            tree.pack(fill='both', expand=True)
            return table_frame, tree, None, None
    
    def create_search_bar(self, parent: ttk.Frame, placeholder: str = "Search...", 
                         search_command: Callable = None) -> tuple:
        """Create search bar with entry and button"""
        search_frame = ttk.Frame(parent, style='Custom.TFrame')
        
        # Search entry
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var, 
                               width=40, style='Search.TEntry')
        search_entry.grid(row=0, column=0, padx=(0, 10), sticky='ew')
        
        # Placeholder text handling
        def on_focus_in(event):
            if search_entry.get() == placeholder:
                search_entry.delete(0, tk.END)
                search_entry.configure(style='Custom.TEntry')
        
        def on_focus_out(event):
            if not search_entry.get():
                search_entry.insert(0, placeholder)
                search_entry.configure(style='Search.TEntry')
        
        # Set initial placeholder
        search_entry.insert(0, placeholder)
        search_entry.bind('<FocusIn>', on_focus_in)
        search_entry.bind('<FocusOut>', on_focus_out)
        
        # Search button
        if search_command:
            search_btn = ttk.Button(search_frame, text="🔍 Search", 
                                  command=search_command, style='Custom.TButton')
            search_btn.grid(row=0, column=1)
            
            # Bind Enter key to search
            search_entry.bind('<Return>', lambda e: search_command())
        
        # Configure grid weights
        search_frame.columnconfigure(0, weight=1)
        
        return search_frame, search_entry, search_var
    
    def show_message(self, message: str, message_type: str = 'info', title: str = None) -> None:
        """Show message dialog"""
        dialog_title = title or settings.APP_NAME
        
        if message_type == 'error':
            messagebox.showerror(dialog_title, message)
        elif message_type == 'warning':
            messagebox.showwarning(dialog_title, message)
        elif message_type == 'success':
            messagebox.showinfo(dialog_title, message)
        elif message_type == 'question':
            return messagebox.askyesno(dialog_title, message)
        else:
            messagebox.showinfo(dialog_title, message)
    
    def confirm_action(self, message: str, title: str = "Confirm Action") -> bool:
        """Show confirmation dialog"""
        return messagebox.askyesno(title, message)
    
    def create_status_bar(self, parent: ttk.Frame) -> tuple:
        """Create status bar at bottom of window"""
        status_frame = ttk.Frame(parent, style='Custom.TFrame')
        
        # Status text
        status_var = tk.StringVar()
        status_var.set("Ready")
        status_label = ttk.Label(status_frame, textvariable=status_var, 
                               style='Info.TLabel')
        status_label.pack(side='left', padx=10)
        
        # Progress bar (initially hidden)
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(status_frame, variable=progress_var, 
                                     style='Custom.Horizontal.TProgressbar')
        
        return status_frame, status_var, progress_bar, progress_var
    
    def set_status(self, status_var: tk.StringVar, message: str) -> None:
        """Set status bar message"""
        status_var.set(message)
        self.root.update_idletasks()
    
    def show_progress(self, progress_bar: ttk.Progressbar, show: bool = True) -> None:
        """Show or hide progress bar"""
        if show:
            progress_bar.pack(side='right', padx=10, fill='x', expand=True)
        else:
            progress_bar.pack_forget()
    
    def center_on_parent(self, parent_window: tk.Tk) -> None:
        """Center this window on parent window"""
        self.root.update_idletasks()
        
        # Get parent window position and size
        parent_x = parent_window.winfo_rootx()
        parent_y = parent_window.winfo_rooty()
        parent_width = parent_window.winfo_width()
        parent_height = parent_window.winfo_height()
        
        # Calculate center position
        x = parent_x + (parent_width // 2) - (self.width // 2)
        y = parent_y + (parent_height // 2) - (self.height // 2)
        
        self.root.geometry(f"{self.width}x{self.height}+{x}+{y}")
    
    def bind_escape_key(self, callback: Callable = None) -> None:
        """Bind Escape key to close window or custom callback"""
        if callback:
            self.root.bind('<Escape>', lambda e: callback())
        else:
            self.root.bind('<Escape>', lambda e: self.root.destroy())
    
    def set_minimum_size(self, min_width: int = 600, min_height: int = 400) -> None:
        """Set minimum window size"""
        self.root.minsize(min_width, min_height)
    
    def run(self) -> None:
        """Start the window main loop"""
        try:
            self.root.mainloop()
        except Exception as e:
            logger.error(f"Error in window main loop: {e}")
            self.show_message(f"An error occurred: {str(e)}", 'error')
    
    def close(self) -> None:
        """Close the window"""
        try:
            self.root.destroy()
        except Exception as e:
            logger.error(f"Error closing window: {e}")


class DialogWindow(BaseWindow):
    """Dialog window for modal interactions"""
    
    def __init__(self, parent: tk.Tk, title: str, width: int = 400, height: int = 300):
        """Initialize dialog window"""
        # Create Toplevel instead of Tk
        self.parent = parent
        self.root = tk.Toplevel(parent)
        self.title = title
        self.width = width
        self.height = height
        
        # Initialize styling
        self.colors = ColorScheme()
        self.style_manager = StyleManager(self.root, self.colors)
        
        # Configure dialog
        self.setup_dialog()
        
        logger.info(f"DialogWindow '{title}' initialized")
    
    def setup_dialog(self) -> None:
        """Setup dialog properties"""
        self.root.title(self.title)
        self.root.geometry(f"{self.width}x{self.height}")
        self.root.resizable(False, False)
        
        # Make modal
        self.root.transient(self.parent)
        self.root.grab_set()
        
        # Configure styling
        self.root.configure(bg=self.colors.get_color('bg_primary'))
        
        # Center on parent
        self.center_on_parent(self.parent)
        
        # Bind escape key to close
        self.bind_escape_key()
    
    def run_modal(self) -> any:
        """Run dialog as modal and return result"""
        self.result = None
        self.root.wait_window()
        return getattr(self, 'result', None)
