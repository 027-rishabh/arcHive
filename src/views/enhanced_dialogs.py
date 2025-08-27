"""
Enhanced Book Management UI with Custom ID Support
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Callable

from views.base_window import DialogWindow
from utils.helpers import DataHelper
from utils.logger import get_logger

logger = get_logger(__name__)


class EnhancedAddBookDialog(DialogWindow):
    """Enhanced dialog for adding books with custom ID support"""
    
    def __init__(self, parent, controller, refresh_callback: Callable = None):
        super().__init__(parent, "Add New Book", 450, 450)
        self.controller = controller
        self.refresh_callback = refresh_callback
        
        self.book_entries = {}
        self.id_mode_var = None
        self.suggested_id_label = None
        
        self.setup_enhanced_book_ui()
        self.update_suggested_id()
    
    def setup_enhanced_book_ui(self) -> None:
        """Setup enhanced book addition interface with ID control"""
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Header
        header_label = ttk.Label(main_frame, text="📚 Add New Book", style='Subheading.TLabel')
        header_label.pack(pady=(0, 20))
        
        # ID Control Section
        id_frame = ttk.LabelFrame(main_frame, text="📋 ID Assignment", padding=10)
        id_frame.pack(fill='x', pady=(0, 15))
        
        # ID Mode Selection
        self.id_mode_var = tk.StringVar(value="auto")
        
        auto_radio = ttk.Radiobutton(
            id_frame, 
            text="🤖 Auto-generate ID", 
            variable=self.id_mode_var, 
            value="auto",
            command=self.on_id_mode_change
        )
        auto_radio.pack(anchor='w', pady=2)
        
        custom_radio = ttk.Radiobutton(
            id_frame, 
            text="✏️ Custom ID", 
            variable=self.id_mode_var, 
            value="custom",
            command=self.on_id_mode_change
        )
        custom_radio.pack(anchor='w', pady=2)
        
        # ID Input Frame
        id_input_frame = ttk.Frame(id_frame)
        id_input_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Label(id_input_frame, text="Book ID:", style='Custom.TLabel').pack(side='left', padx=(0, 10))
        
        # ID Entry
        self.book_entries['book_id'] = ttk.Entry(id_input_frame, style='Custom.TEntry', width=10)
        self.book_entries['book_id'].pack(side='left', padx=(0, 10))
        
        # ID Status/Suggestion
        self.suggested_id_label = ttk.Label(
            id_input_frame, 
            text="Next: 1", 
            style='Info.TLabel'
        )
        self.suggested_id_label.pack(side='left', padx=(10, 0))
        
        # Check ID Button
        check_id_btn = ttk.Button(
            id_input_frame,
            text="🔍 Check",
            command=self.check_id_availability,
            width=8
        )
        check_id_btn.pack(side='right')
        
        # Book Information Section
        info_frame = ttk.LabelFrame(main_frame, text="📖 Book Information", padding=10)
        info_frame.pack(fill='x', pady=(0, 15))
        
        # Title
        title_frame = ttk.Frame(info_frame)
        title_frame.pack(fill='x', pady=5)
        ttk.Label(title_frame, text="Title *:", style='Custom.TLabel').pack(side='left', padx=(0, 10))
        self.book_entries['title'] = ttk.Entry(title_frame, style='Custom.TEntry')
        self.book_entries['title'].pack(side='left', fill='x', expand=True)
        
        # Author
        author_frame = ttk.Frame(info_frame)
        author_frame.pack(fill='x', pady=5)
        ttk.Label(author_frame, text="Author *:", style='Custom.TLabel').pack(side='left', padx=(0, 10))
        self.book_entries['author'] = ttk.Entry(author_frame, style='Custom.TEntry')
        self.book_entries['author'].pack(side='left', fill='x', expand=True)
        
        # Category
        category_frame = ttk.Frame(info_frame)
        category_frame.pack(fill='x', pady=5)
        ttk.Label(category_frame, text="Category *:", style='Custom.TLabel').pack(side='left', padx=(0, 10))
        self.book_entries['category'] = ttk.Combobox(
            category_frame, 
            style='Custom.TCombobox',
            values=["Fiction", "Non-Fiction", "Science", "History", "Biography", "Technology", "Arts", "Other"]
        )
        self.book_entries['category'].pack(side='left', fill='x', expand=True)
        
        # ISBN
        isbn_frame = ttk.Frame(info_frame)
        isbn_frame.pack(fill='x', pady=5)
        ttk.Label(isbn_frame, text="ISBN *:", style='Custom.TLabel').pack(side='left', padx=(0, 10))
        self.book_entries['isbn'] = ttk.Entry(isbn_frame, style='Custom.TEntry')
        self.book_entries['isbn'].pack(side='left', fill='x', expand=True)
        
        # ISBN Validation Button
        validate_isbn_btn = ttk.Button(
            isbn_frame,
            text="✓ Validate",
            command=self.validate_isbn,
            width=10
        )
        validate_isbn_btn.pack(side='right', padx=(5, 0))
        
        # Info Section
        info_text = ("💡 * Required fields\\n"
                    "• Auto-generate: System assigns next available ID\\n"
                    "• Custom ID: You choose the book ID (must be unique)")
        info_label = ttk.Label(main_frame, text=info_text, style='Info.TLabel', justify='left')
        info_label.pack(pady=15)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=20)
        
        ttk.Button(
            button_frame,
            text="💾 Add Book",
            command=self.save_book,
            style='Success.TButton'
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            button_frame,
            text="🔄 Reset Form",
            command=self.reset_form,
            style='Custom.TButton'
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            button_frame,
            text="❌ Cancel",
            command=self.root.destroy,
            style='Error.TButton'
        ).pack(side='right')
        
        # Initialize form state
        self.on_id_mode_change()
        
        # Focus on title field
        self.book_entries['title'].focus()
    
    def on_id_mode_change(self) -> None:
        """Handle ID mode change"""
        try:
            mode = self.id_mode_var.get()
            
            if mode == "auto":
                # Disable ID entry and show suggested ID
                self.book_entries['book_id'].configure(state='disabled')
                self.book_entries['book_id'].delete(0, tk.END)
                self.update_suggested_id()
            else:
                # Enable ID entry and clear suggestion
                self.book_entries['book_id'].configure(state='normal')
                self.suggested_id_label.configure(text="Enter custom ID")
                
        except Exception as e:
            logger.error(f"Error handling ID mode change: {e}")
    
    def update_suggested_id(self) -> None:
        """Update suggested ID display"""
        try:
            next_id = self.controller.book_model.get_next_available_id()
            self.suggested_id_label.configure(text=f"Next: {next_id}")
        except Exception as e:
            logger.error(f"Error updating suggested ID: {e}")
            self.suggested_id_label.configure(text="Next: 1")
    
    def check_id_availability(self) -> None:
        """Check if entered ID is available"""
        try:
            id_text = self.book_entries['book_id'].get().strip()
            
            if not id_text:
                self.show_message("Please enter an ID to check", 'warning')
                return
            
            try:
                book_id = int(id_text)
                if book_id <= 0:
                    raise ValueError("ID must be positive")
            except ValueError:
                self.show_message("ID must be a positive number", 'error')
                return
            
            if self.controller.book_model.is_id_available(book_id):
                self.suggested_id_label.configure(text="✅ Available")
                self.show_message(f"Book ID {book_id} is available!", 'success')
            else:
                self.suggested_id_label.configure(text="❌ Taken")
                self.show_message(f"Book ID {book_id} is already taken", 'error')
                
        except Exception as e:
            logger.error(f"Error checking ID availability: {e}")
            self.show_message(f"Error checking ID: {str(e)}", 'error')
    
    def validate_isbn(self) -> None:
        """Validate ISBN format"""
        try:
            isbn = self.book_entries['isbn'].get().strip()
            
            if not isbn:
                self.show_message("Please enter an ISBN to validate", 'warning')
                return
            
            if DataHelper.validate_isbn(isbn):
                self.show_message("✅ ISBN format is valid", 'success')
            else:
                self.show_message("❌ Invalid ISBN format", 'error')
                
        except Exception as e:
            logger.error(f"Error validating ISBN: {e}")
            self.show_message("Error validating ISBN", 'error')
    
    def reset_form(self) -> None:
        """Reset form to default state"""
        try:
            # Clear all entries
            for key, widget in self.book_entries.items():
                if key != 'book_id':  # Don't clear book_id, let mode handle it
                    if hasattr(widget, 'delete'):
                        widget.delete(0, tk.END)
                    elif hasattr(widget, 'set'):
                        widget.set('')
            
            # Reset ID mode to auto
            self.id_mode_var.set("auto")
            self.on_id_mode_change()
            
            # Focus on title
            self.book_entries['title'].focus()
            
        except Exception as e:
            logger.error(f"Error resetting form: {e}")
    
    def save_book(self) -> None:
        """Save new book"""
        try:
            # Collect form data
            book_data = {}
            for key, widget in self.book_entries.items():
                if key == 'book_id':
                    continue  # Handle separately
                    
                if hasattr(widget, 'get'):
                    value = widget.get().strip()
                    if value:
                        book_data[key] = value
            
            # Validate required fields
            required_fields = ['title', 'author', 'category', 'isbn']
            missing_fields = [field for field in required_fields if not book_data.get(field)]
            
            if missing_fields:
                self.show_message(f"Please fill in required fields: {', '.join(missing_fields)}", 'error')
                return
            
            # Handle ID based on mode
            book_id = None
            if self.id_mode_var.get() == "custom":
                id_text = self.book_entries['book_id'].get().strip()
                if not id_text:
                    self.show_message("Please enter a custom ID or switch to auto-generate", 'error')
                    return
                
                try:
                    book_id = int(id_text)
                    if book_id <= 0:
                        raise ValueError("ID must be positive")
                except ValueError:
                    self.show_message("Book ID must be a positive number", 'error')
                    return
                
                # Check availability one more time
                if not self.controller.book_model.is_id_available(book_id):
                    self.show_message(f"Book ID {book_id} is no longer available", 'error')
                    return
            
            # Attempt to save
            success = self.controller.book_model.add_book(
                title=book_data['title'],
                author=book_data['author'],
                category=book_data['category'],
                isbn=book_data['isbn'],
                book_id=book_id
            )
            
            if success:
                actual_id = book_id if book_id else self.controller.book_model.get_next_available_id() - 1
                self.show_message(f"Book '{book_data['title']}' added successfully!\\nAssigned ID: {actual_id}", 'success')
                
                if self.refresh_callback:
                    self.refresh_callback()
                
                # Ask if user wants to add another book
                if messagebox.askyesno("Add Another", "Book added successfully! Add another book?"):
                    self.reset_form()
                else:
                    self.root.destroy()
            else:
                self.show_message("Failed to add book. ISBN may already exist.", 'error')
                
        except Exception as e:
            logger.error(f"Error saving book: {e}")
            self.show_message(f"Error saving book: {str(e)}", 'error')


class EnhancedAddMemberDialog(DialogWindow):
    """Enhanced dialog for adding members with custom ID support"""
    
    def __init__(self, parent, controller, refresh_callback: Callable = None):
        super().__init__(parent, "Add New Member", 600, 700)
        self.controller = controller
        self.refresh_callback = refresh_callback
        
        self.member_entries = {}
        self.id_mode_var = None
        self.suggested_id_label = None
        
        self.setup_enhanced_member_ui()
        self.update_suggested_id()
    
    def setup_enhanced_member_ui(self) -> None:
        """Setup enhanced member addition interface with ID control"""
        # Create main scrollable frame
        canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y")
        
        main_frame = scrollable_frame
        
        # Header
        header_label = ttk.Label(main_frame, text="👤 Add New Member", style='Subheading.TLabel')
        header_label.pack(pady=(0, 20))
        
        # ID Control Section
        id_frame = ttk.LabelFrame(main_frame, text="🆔 ID Assignment", padding=10)
        id_frame.pack(fill='x', pady=(0, 15))
        
        # ID Mode Selection
        self.id_mode_var = tk.StringVar(value="auto")
        
        auto_radio = ttk.Radiobutton(
            id_frame, 
            text="🤖 Auto-generate ID", 
            variable=self.id_mode_var, 
            value="auto",
            command=self.on_id_mode_change
        )
        auto_radio.pack(anchor='w', pady=2)
        
        custom_radio = ttk.Radiobutton(
            id_frame, 
            text="✏️ Custom ID", 
            variable=self.id_mode_var, 
            value="custom",
            command=self.on_id_mode_change
        )
        custom_radio.pack(anchor='w', pady=2)
        
        # ID Input Frame
        id_input_frame = ttk.Frame(id_frame)
        id_input_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Label(id_input_frame, text="Member ID:", style='Custom.TLabel').pack(side='left', padx=(0, 10))
        
        self.member_entries['member_id'] = ttk.Entry(id_input_frame, style='Custom.TEntry', width=10)
        self.member_entries['member_id'].pack(side='left', padx=(0, 10))
        
        self.suggested_id_label = ttk.Label(
            id_input_frame, 
            text="Next: 1", 
            style='Info.TLabel'
        )
        self.suggested_id_label.pack(side='left', padx=(10, 0))
        
        check_id_btn = ttk.Button(
            id_input_frame,
            text="🔍 Check",
            command=self.check_id_availability,
            width=8
        )
        check_id_btn.pack(side='right')
        
        # Basic Information Section
        basic_frame = ttk.LabelFrame(main_frame, text="👤 Basic Information", padding=10)
        basic_frame.pack(fill='x', pady=(0, 15))
        
        # Create form fields
        basic_fields = [
            ('first_name', 'First Name *', 'entry'),
            ('last_name', 'Last Name *', 'entry'),
            ('email', 'Email *', 'entry'),
            ('phone', 'Phone *', 'entry'),
            ('date_of_birth', 'Date of Birth (YYYY-MM-DD)', 'entry'),
            ('gender', 'Gender', 'combobox', ['Male', 'Female', 'Other', 'Prefer not to say'])
        ]
        
        for field_info in basic_fields:
            field_name = field_info[0]
            label_text = field_info[1]
            widget_type = field_info[2]
            
            field_frame = ttk.Frame(basic_frame)
            field_frame.pack(fill='x', pady=3)
            
            ttk.Label(field_frame, text=label_text, style='Custom.TLabel', width=20).pack(side='left', padx=(0, 10))
            
            if widget_type == 'entry':
                self.member_entries[field_name] = ttk.Entry(field_frame, style='Custom.TEntry')
            elif widget_type == 'combobox':
                values = field_info[3] if len(field_info) > 3 else []
                self.member_entries[field_name] = ttk.Combobox(field_frame, style='Custom.TCombobox', values=values)
            
            self.member_entries[field_name].pack(side='left', fill='x', expand=True)
        
        # Member Type Section
        type_frame = ttk.LabelFrame(main_frame, text="📋 Membership Details", padding=10)
        type_frame.pack(fill='x', pady=(0, 15))
        
        # Member Type
        mtype_frame = ttk.Frame(type_frame)
        mtype_frame.pack(fill='x', pady=3)
        ttk.Label(mtype_frame, text="Member Type:", style='Custom.TLabel', width=20).pack(side='left', padx=(0, 10))
        self.member_entries['member_type'] = ttk.Combobox(
            mtype_frame, 
            style='Custom.TCombobox',
            values=['Student', 'Faculty', 'Staff', 'Senior Citizen', 'General', 'Premium']
        )
        self.member_entries['member_type'].pack(side='left', fill='x', expand=True)
        self.member_entries['member_type'].set('General')  # Default value
        
        # Address Section (collapsed by default)
        address_frame = ttk.LabelFrame(main_frame, text="🏠 Address (Optional)", padding=10)
        address_frame.pack(fill='x', pady=(0, 15))
        
        address_fields = [
            ('address_line1', 'Address Line 1'),
            ('city', 'City'),
            ('state', 'State'),
            ('postal_code', 'Postal Code')
        ]
        
        for field_name, label_text in address_fields:
            field_frame = ttk.Frame(address_frame)
            field_frame.pack(fill='x', pady=3)
            
            ttk.Label(field_frame, text=label_text, style='Custom.TLabel', width=20).pack(side='left', padx=(0, 10))
            self.member_entries[field_name] = ttk.Entry(field_frame, style='Custom.TEntry')
            self.member_entries[field_name].pack(side='left', fill='x', expand=True)
        
        # Info Section
        info_text = ("💡 * Required fields\\n"
                    "• Member types have different book limits\\n"
                    "• Auto-generate: System assigns next available ID\\n"
                    "• Custom ID: You choose the member ID (must be unique)")
        info_label = ttk.Label(main_frame, text=info_text, style='Info.TLabel', justify='left')
        info_label.pack(pady=15)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=20)
        
        ttk.Button(
            button_frame,
            text="💾 Add Member",
            command=self.save_member,
            style='Success.TButton'
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            button_frame,
            text="🔄 Reset Form",
            command=self.reset_form,
            style='Custom.TButton'
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            button_frame,
            text="❌ Cancel",
            command=self.root.destroy,
            style='Error.TButton'
        ).pack(side='right')
        
        # Initialize form state
        self.on_id_mode_change()
        
        # Focus on first name field
        self.member_entries['first_name'].focus()
    
    def on_id_mode_change(self) -> None:
        """Handle ID mode change"""
        try:
            mode = self.id_mode_var.get()
            
            if mode == "auto":
                self.member_entries['member_id'].configure(state='disabled')
                self.member_entries['member_id'].delete(0, tk.END)
                self.update_suggested_id()
            else:
                self.member_entries['member_id'].configure(state='normal')
                self.suggested_id_label.configure(text="Enter custom ID")
                
        except Exception as e:
            logger.error(f"Error handling ID mode change: {e}")
    
    def update_suggested_id(self) -> None:
        """Update suggested ID display"""
        try:
            next_id = self.controller.member_model.get_next_available_id()
            self.suggested_id_label.configure(text=f"Next: {next_id}")
        except Exception as e:
            logger.error(f"Error updating suggested ID: {e}")
            self.suggested_id_label.configure(text="Next: 1")
    
    def check_id_availability(self) -> None:
        """Check if entered ID is available"""
        try:
            id_text = self.member_entries['member_id'].get().strip()
            
            if not id_text:
                self.show_message("Please enter an ID to check", 'warning')
                return
            
            try:
                member_id = int(id_text)
                if member_id <= 0:
                    raise ValueError("ID must be positive")
            except ValueError:
                self.show_message("ID must be a positive number", 'error')
                return
            
            if self.controller.member_model.is_id_available(member_id):
                self.suggested_id_label.configure(text="✅ Available")
                self.show_message(f"Member ID {member_id} is available!", 'success')
            else:
                self.suggested_id_label.configure(text="❌ Taken")
                self.show_message(f"Member ID {member_id} is already taken", 'error')
                
        except Exception as e:
            logger.error(f"Error checking ID availability: {e}")
            self.show_message(f"Error checking ID: {str(e)}", 'error')
    
    def reset_form(self) -> None:
        """Reset form to default state"""
        try:
            # Clear all entries except member_id (handled by mode)
            for key, widget in self.member_entries.items():
                if key != 'member_id':
                    if hasattr(widget, 'delete'):
                        widget.delete(0, tk.END)
                    elif hasattr(widget, 'set'):
                        widget.set('')
            
            # Reset defaults
            self.member_entries['member_type'].set('General')
            
            # Reset ID mode
            self.id_mode_var.set("auto")
            self.on_id_mode_change()
            
            # Focus on first name
            self.member_entries['first_name'].focus()
            
        except Exception as e:
            logger.error(f"Error resetting form: {e}")
    
    def save_member(self) -> None:
        """Save new member"""
        try:
            # Collect form data
            member_data = {}
            for key, widget in self.member_entries.items():
                if key == 'member_id':
                    continue  # Handle separately
                    
                if hasattr(widget, 'get'):
                    value = widget.get().strip()
                    if value:
                        member_data[key] = value
            
            # Validate required fields
            required_fields = ['first_name', 'last_name', 'email', 'phone']
            missing_fields = [field for field in required_fields if not member_data.get(field)]
            
            if missing_fields:
                self.show_message(f"Please fill in required fields: {', '.join(missing_fields)}", 'error')
                return
            
            # Handle ID based on mode
            member_id = None
            if self.id_mode_var.get() == "custom":
                id_text = self.member_entries['member_id'].get().strip()
                if not id_text:
                    self.show_message("Please enter a custom ID or switch to auto-generate", 'error')
                    return
                
                try:
                    member_id = int(id_text)
                    if member_id <= 0:
                        raise ValueError("ID must be positive")
                except ValueError:
                    self.show_message("Member ID must be a positive number", 'error')
                    return
                
                # Check availability
                if not self.controller.member_model.is_id_available(member_id):
                    self.show_message(f"Member ID {member_id} is no longer available", 'error')
                    return
            
            # Add created_by field
            member_data['created_by'] = self.controller.current_user.get('username', 'Unknown') if self.controller.current_user else 'System'
            
            # Attempt to save
            success = self.controller.member_model.add_member(member_data, member_id)
            
            if success:
                actual_id = member_id if member_id else self.controller.member_model.get_next_available_id() - 1
                self.show_message(f"Member '{member_data['first_name']} {member_data['last_name']}' added successfully!\\nAssigned ID: {actual_id}", 'success')
                
                if self.refresh_callback:
                    self.refresh_callback()
                
                # Ask if user wants to add another member
                if messagebox.askyesno("Add Another", "Member added successfully! Add another member?"):
                    self.reset_form()
                else:
                    self.root.destroy()
            else:
                self.show_message("Failed to add member. Email may already exist.", 'error')
                
        except Exception as e:
            logger.error(f"Error saving member: {e}")
            self.show_message(f"Error saving member: {str(e)}", 'error')
