"""
Styling and theming for Library Management System GUI
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict
from config.settings import settings


class ColorScheme:
    """Professional color schemes for the application"""
    
    def __init__(self, theme_name: str = 'professional'):
        """Initialize color scheme with specified theme"""
        self.current_theme = settings.THEMES.get(theme_name, settings.THEMES['professional'])
        self.theme_name = theme_name
    
    def get_color(self, color_key: str) -> str:
        """Get color value by key"""
        return self.current_theme.get(color_key, '#000000')
    
    def get_all_colors(self) -> Dict[str, str]:
        """Get all colors in current theme"""
        return self.current_theme.copy()
    
    def switch_theme(self, theme_name: str) -> bool:
        """Switch to different theme"""
        if theme_name in settings.THEMES:
            self.current_theme = settings.THEMES[theme_name]
            self.theme_name = theme_name
            return True
        return False
    
    def get_available_themes(self) -> list:
        """Get list of available theme names"""
        return list(settings.THEMES.keys())


class StyleManager:
    """Manager for TTK styles and GUI theming"""
    
    def __init__(self, root: tk.Tk, color_scheme: ColorScheme):
        """Initialize style manager"""
        self.root = root
        self.colors = color_scheme
        self.style = ttk.Style()
        self.setup_styles()
    
    def setup_styles(self) -> None:
        """Setup custom TTK styles"""
        # Configure root window
        self.root.configure(bg=self.colors.get_color('bg_primary'))
        
        # Button styles
        self._setup_button_styles()
        
        # Entry styles
        self._setup_entry_styles()
        
        # Label styles
        self._setup_label_styles()
        
        # Frame styles
        self._setup_frame_styles()
        
        # Treeview styles
        self._setup_treeview_styles()
        
        # Notebook styles
        self._setup_notebook_styles()
        
        # Progressbar styles
        self._setup_progressbar_styles()
    
    def _setup_button_styles(self) -> None:
        """Setup button styles"""
        # Primary button
        self.style.configure(
            'Custom.TButton',
            background=self.colors.get_color('button_bg'),
            foreground=self.colors.get_color('button_fg'),
            borderwidth=0,
            focuscolor='none',
            padding=(12, 8),
            font=('Arial', 10)
        )
        
        self.style.map(
             'Success.TButton',
            background=[
                ('active', '#229954'),      # Darker green on hover
                ('pressed', '#1E8449')      # Even darker when pressed
            ],
        foreground=[
            ('active', 'white'),        # Keep text white and visible
            ('pressed', 'white')        # Keep text white when pressed
        ]
        )
        # Success button (green)
        self.style.configure(
            'Success.TButton',
            background=self.colors.get_color('success'),
            foreground='white',
            borderwidth=0,
            focuscolor='none',
            padding=(12, 8),
            font=('Arial', 10, 'bold')
        )
        
        # Warning button (orange)
        self.style.configure(
            'Warning.TButton',
            background=self.colors.get_color('warning'),
            foreground='white',
            borderwidth=0,
            focuscolor='none',
            padding=(12, 8),
            font=('Arial', 10, 'bold')
        )
        
        # Error button (red)
        self.style.configure(
            'Error.TButton',
            background=self.colors.get_color('error'),
            foreground='white',
            borderwidth=0,
            focuscolor='none',
            padding=(12, 8),
            font=('Arial', 10, 'bold')
        )
    
    def _setup_entry_styles(self) -> None:
        """Setup entry field styles"""
        self.style.configure(
            'Custom.TEntry',
            fieldbackground=self.colors.get_color('entry_bg'),
            foreground=self.colors.get_color('entry_fg'),
            borderwidth=2,
            insertcolor=self.colors.get_color('entry_fg'),
            font=('Arial', 10)
        )
        
        self.style.map(
            'Custom.TEntry',
            focuscolor=[('focus', self.colors.get_color('bg_accent'))]
        )
        
        # Search entry
        self.style.configure(
            'Search.TEntry',
            fieldbackground=self.colors.get_color('entry_bg'),
            foreground=self.colors.get_color('entry_fg'),
            borderwidth=2,
            insertcolor=self.colors.get_color('entry_fg'),
            font=('Arial', 10, 'italic')
        )
    
    def _setup_label_styles(self) -> None:
        """Setup label styles"""
        # Main heading
        self.style.configure(
            'Heading.TLabel',
            background=self.colors.get_color('bg_primary'),
            foreground=self.colors.get_color('fg_primary'),
            font=('Arial', 18, 'bold')
        )
        
        # Subheading
        self.style.configure(
            'Subheading.TLabel',
            background=self.colors.get_color('bg_primary'),
            foreground=self.colors.get_color('fg_primary'),
            font=('Arial', 14, 'bold')
        )
        
        # Regular label
        self.style.configure(
            'Custom.TLabel',
            background=self.colors.get_color('bg_primary'),
            foreground=self.colors.get_color('fg_secondary'),
            font=('Arial', 10)
        )
        
        # Info label
        self.style.configure(
            'Info.TLabel',
            background=self.colors.get_color('bg_primary'),
            foreground=self.colors.get_color('fg_secondary'),
            font=('Arial', 9, 'italic')
        )
        
        # Status labels
        self.style.configure(
            'Success.TLabel',
            background=self.colors.get_color('bg_primary'),
            foreground=self.colors.get_color('success'),
            font=('Arial', 10, 'bold')
        )
        
        self.style.configure(
            'Warning.TLabel',
            background=self.colors.get_color('bg_primary'),
            foreground=self.colors.get_color('warning'),
            font=('Arial', 10, 'bold')
        )
        
        self.style.configure(
            'Error.TLabel',
            background=self.colors.get_color('bg_primary'),
            foreground=self.colors.get_color('error'),
            font=('Arial', 10, 'bold')
        )
    
    def _setup_frame_styles(self) -> None:
        """Setup frame styles"""
        # Primary frame
        self.style.configure(
            'Custom.TFrame',
            background=self.colors.get_color('bg_secondary'),
            relief='flat',
            borderwidth=0
        )
        
        # Card frame (raised appearance)
        self.style.configure(
            'Card.TFrame',
            background=self.colors.get_color('bg_secondary'),
            relief='raised',
            borderwidth=2
        )
        
        # Sidebar frame
        self.style.configure(
            'Sidebar.TFrame',
            background=self.colors.get_color('bg_primary'),
            relief='flat',
            borderwidth=0
        )
    
    def _setup_treeview_styles(self) -> None:
        """Setup treeview (table) styles"""
        self.style.configure(
            'Custom.Treeview',
            background=self.colors.get_color('entry_bg'),
            foreground=self.colors.get_color('entry_fg'),
            fieldbackground=self.colors.get_color('entry_bg'),
            borderwidth=1,
            font=('Arial', 9)
        )
        
        self.style.configure(
            'Custom.Treeview.Heading',
            background=self.colors.get_color('bg_accent'),
            foreground=self.colors.get_color('fg_primary'),
            borderwidth=1,
            font=('Arial', 10, 'bold')
        )
        
        self.style.map(
            'Custom.Treeview',
            background=[('selected', self.colors.get_color('bg_accent'))],
            foreground=[('selected', self.colors.get_color('fg_primary'))]
        )
    
    def _setup_notebook_styles(self) -> None:
        """Setup notebook (tabbed interface) styles"""
        self.style.configure(
            'Custom.TNotebook',
            background=self.colors.get_color('bg_secondary'),
            borderwidth=0
        )
        
        self.style.configure(
            'Custom.TNotebook.Tab',
            background=self.colors.get_color('bg_primary'),
            foreground=self.colors.get_color('fg_secondary'),
            padding=(12, 8),
            font=('Arial', 10)
        )
        
        self.style.map(
            'Custom.TNotebook.Tab',
            background=[('selected', self.colors.get_color('bg_accent')),
                       ('active', self.colors.get_color('bg_secondary'))],
            foreground=[('selected', self.colors.get_color('fg_primary'))]
        )
    
    def _setup_progressbar_styles(self) -> None:
        """Setup progressbar styles"""
        self.style.configure(
            'Custom.Horizontal.TProgressbar',
            background=self.colors.get_color('bg_accent'),
            troughcolor=self.colors.get_color('bg_secondary'),
            borderwidth=0,
            lightcolor=self.colors.get_color('bg_accent'),
            darkcolor=self.colors.get_color('bg_accent')
        )
    
    def update_theme(self, new_theme: str) -> bool:
        """Update all styles with new theme"""
        if self.colors.switch_theme(new_theme):
            self.setup_styles()
            return True
        return False
    
    def get_font(self, size: int = 10, weight: str = 'normal') -> tuple:
        """Get standardized font tuple"""
        return ('Arial', size, weight)
    
    def get_icon_font(self, size: int = 12) -> tuple:
        """Get font for icons/symbols"""
        return ('Segoe UI Symbol', size)


class UIHelpers:
    """Helper functions for UI creation"""
    
    @staticmethod
    def center_window(window: tk.Toplevel, width: int, height: int) -> None:
        """Center window on screen"""
        window.update_idletasks()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        
        window.geometry(f"{width}x{height}+{x}+{y}")
    
    @staticmethod
    def create_separator(parent: tk.Widget, style: str = 'Custom.TSeparator') -> ttk.Separator:
        """Create horizontal separator"""
        return ttk.Separator(parent, orient='horizontal', style=style)
    
    @staticmethod
    def create_scrollable_frame(parent: tk.Widget, style: str = 'Custom.TFrame') -> tuple:
        """Create scrollable frame with scrollbars"""
        # Canvas for scrolling
        canvas = tk.Canvas(parent)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(parent, orient='vertical', command=canvas.yview)
        h_scrollbar = ttk.Scrollbar(parent, orient='horizontal', command=canvas.xview)
        
        # Scrollable frame
        scrollable_frame = ttk.Frame(canvas, style=style)
        
        # Configure canvas
        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        
        def configure_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox('all'))
        
        scrollable_frame.bind('<Configure>', configure_scroll_region)
        
        # Pack elements
        canvas.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
        return scrollable_frame, canvas, v_scrollbar, h_scrollbar
    
    @staticmethod
    def create_tooltip(widget: tk.Widget, text: str) -> None:
        """Create tooltip for widget"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(tooltip, text=text, background='lightyellow',
                           font=('Arial', 9), relief='solid', borderwidth=1)
            label.pack()
            
            def hide_tooltip():
                tooltip.destroy()
            
            tooltip.after(3000, hide_tooltip)  # Hide after 3 seconds
        
        def hide_tooltip(event):
            pass
        
        widget.bind('<Enter>', show_tooltip)
        widget.bind('<Leave>', hide_tooltip)
    
    @staticmethod
    def validate_numeric_input(char: str) -> bool:
        """Validate numeric input for entry fields"""
        return char.isdigit() or char == ""
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 30) -> str:
        """Truncate text for display"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
