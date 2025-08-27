"""
Enhanced Main dashboard and management screens for Library Management System
Includes comprehensive member management for librarians
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, List, Dict
import datetime

from views.base_window import BaseWindow, DialogWindow
from config.settings import settings
from utils.logger import get_logger
from utils.helpers import DataHelper, StringHelper

logger = get_logger(__name__)


class MainDashboard(BaseWindow):
    """Enhanced main dashboard window with role-based functionality and member management"""
    
    def __init__(self, controller):
        """Initialize main dashboard"""
        super().__init__(
            title="Dashboard",
            width=settings.DEFAULT_WINDOW_WIDTH,
            height=settings.DEFAULT_WINDOW_HEIGHT
        )
        
        self.controller = controller
        self.current_view = None
        
        # Initialize UI
        self.setup_dashboard()
        logger.info("Enhanced main dashboard initialized")
    
    def setup_dashboard(self) -> None:
        """Setup main dashboard interface"""
        # Create main container with sidebar and content area
        self.main_container = ttk.Frame(self.root, style='Custom.TFrame')
        self.main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create sidebar and content area
        self.create_sidebar()
        self.create_content_area()
        
        # Show welcome screen initially
        self.show_welcome()
        
        # Configure window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_sidebar(self) -> None:
        """Create navigation sidebar"""
        sidebar_frame = ttk.Frame(self.main_container, style='Sidebar.TFrame')
        sidebar_frame.pack(side='left', fill='y', padx=(0, 10))
        
        # User info section
        self.create_user_info_section(sidebar_frame)
        
        # Navigation buttons
        self.create_navigation_buttons(sidebar_frame)
    
    def create_user_info_section(self, parent: ttk.Frame) -> None:
        """Create user information section"""
        user_frame = ttk.Frame(parent, style='Card.TFrame', padding=15)
        user_frame.pack(fill='x', padx=10, pady=10)
        
        user = self.controller.current_user
        
        # Role-specific welcome message
        if user['role'] == 'admin':
            role_icon = "👑"
            role_description = "Full System Access"
        else:
            role_icon = "📚"
            role_description = "Library Operations"
        
        user_info = f"""Welcome!
        
{role_icon} {user['username']}
🔑 {user['role'].title()}
📋 {role_description}

📚 Library System
v{settings.APP_VERSION}"""
        
        user_label = ttk.Label(
            user_frame, 
            text=user_info, 
            style='Custom.TLabel',
            justify='left'
        )
        user_label.pack()
    
    def create_navigation_buttons(self, parent: ttk.Frame) -> None:
        """Create navigation buttons based on user role"""
        nav_frame = ttk.Frame(parent, style='Custom.TFrame', padding=10)
        nav_frame.pack(fill='x', padx=10, pady=10)
        
        # Common buttons for all users
        buttons = [
            ("📊 Dashboard", self.show_welcome, 'Custom.TButton'),
            ("📚 Books", self.show_books, 'Custom.TButton'),
            ("👥 Members", self.show_members, 'Custom.TButton'),  # Now available to librarians!
            ("📋 Transactions", self.show_transactions, 'Custom.TButton'),
        ]
        
        # Admin-only buttons
        if self.controller.is_admin():
            admin_buttons = [
                ("👤 Users", self.show_users, 'Custom.TButton'),
                ("📊 Reports", self.show_reports, 'Custom.TButton'),
            ]
            buttons.extend(admin_buttons)
        
        # Logout button
        buttons.append(("🚪 Logout", self.logout, 'Error.TButton'))
        
        # Create buttons
        for text, command, style in buttons:
            btn = ttk.Button(nav_frame, text=text, command=command, style=style)
            btn.pack(fill='x', pady=2)
    
    def create_content_area(self) -> None:
        """Create main content area"""
        self.content_frame = ttk.Frame(self.main_container, style='Custom.TFrame')
        self.content_frame.pack(side='right', fill='both', expand=True)
    
    def clear_content(self) -> None:
        """Clear current content area"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_welcome(self) -> None:
        """Show welcome/dashboard screen with enhanced statistics"""
        self.clear_content()
        self.current_view = "dashboard"
        
        # Create main welcome frame
        welcome_frame = ttk.Frame(self.content_frame, style='Custom.TFrame', padding=30)
        welcome_frame.pack(fill='both', expand=True)
        
        # Header
        self.create_header(welcome_frame, "📚 Library Management Dashboard", 
                          "Welcome to your enhanced library management system")
        
        # Statistics section
        self.create_enhanced_statistics_section(welcome_frame)
    
    def create_enhanced_statistics_section(self, parent: ttk.Frame) -> None:
        """Create enhanced statistics display section"""
        try:
            stats = self.controller.get_dashboard_stats()
            
            # Stats container
            stats_frame = ttk.LabelFrame(parent, text="📊 Library Statistics", padding=20)
            stats_frame.grid(row=1, column=0, sticky='nsew', pady=20)
            parent.rowconfigure(1, weight=1)
            parent.columnconfigure(0, weight=1)
            
            # Statistics text with enhanced member information
            book_stats = stats.get('books', {})
            member_stats = stats.get('members', {})
            transaction_stats = stats.get('transactions', {})
            
            # Role-specific statistics
            user_role = self.controller.current_user['role']
            
            if user_role == 'admin':
                stats_text = f"""
📚 BOOK STATISTICS:
   • Total Books: {book_stats.get('total_books', 0)}
   • Available: {book_stats.get('available_books', 0)}
   • Currently Issued: {book_stats.get('issued_books', 0)}

👥 MEMBER STATISTICS:
   • Total Members: {member_stats.get('total_members', 0)}
   • Active Borrowers: {member_stats.get('active_members', 0)}
   • Overdue Members: {member_stats.get('overdue_members', 0)}
   • New This Month: {member_stats.get('recent_members', 0)}

📋 TRANSACTION STATISTICS:
   • Total Transactions: {transaction_stats.get('total_transactions', 0)}
   • Currently Issued: {transaction_stats.get('currently_issued', 0)}
   • Overdue Books: {transaction_stats.get('overdue_count', 0)}
   • Total Late Fees: ${transaction_stats.get('total_late_fees', 0):.2f}

🎯 ADMIN FEATURES:
   • Full system administration
   • User and member management
   • Complete reporting and analytics
   • System configuration and backup
   • Data export and import capabilities

📈 SYSTEM STATUS: ✅ Online
👤 Current User: {self.controller.current_user['username']} (Administrator)
"""
            else:  # Librarian view
                stats_text = f"""
📚 BOOK OPERATIONS:
   • Total Books: {book_stats.get('total_books', 0)}
   • Available for Issue: {book_stats.get('available_books', 0)}
   • Currently Issued: {book_stats.get('issued_books', 0)}

👥 MEMBER OPERATIONS:
   • Total Library Members: {member_stats.get('total_members', 0)}
   • Active Borrowers: {member_stats.get('active_members', 0)}
   • Members with Overdue Books: {member_stats.get('overdue_members', 0)}
   • Members at Book Limit: {member_stats.get('members_at_limit', 0)}

📋 TODAY'S TRANSACTIONS:
   • Books Currently Issued: {transaction_stats.get('currently_issued', 0)}
   • Overdue Books Requiring Attention: {transaction_stats.get('overdue_count', 0)}
   • Late Fees Collected: ${transaction_stats.get('total_late_fees', 0):.2f}

🎯 LIBRARIAN TOOLS:
   • Issue and return books quickly
   • Manage member accounts and limits
   • Handle overdue books and renewals
   • Track borrowing statistics
   • Process late fees and payments

📋 QUICK ACTIONS:
   • Use "👥 Members" to manage member accounts
   • Use "📚 Books" to search and manage inventory
   • Use "📋 Transactions" for issue/return operations
   • Right-click members for quick actions

📈 SYSTEM STATUS: ✅ Online
👤 Current User: {self.controller.current_user['username']} (Librarian)
"""
            
            # Categories breakdown (for both roles)
            categories = book_stats.get('categories', {})
            if categories:
                stats_text += "\\n📖 BOOK CATEGORIES:\\n"
                for category, count in sorted(categories.items()):
                    stats_text += f"   • {category}: {count} books\\n"
            
            # Create text widget for stats
            text_widget = tk.Text(
                stats_frame, 
                wrap=tk.WORD, 
                height=28,
                bg=self.colors.get_color('entry_bg'),
                fg=self.colors.get_color('entry_fg'),
                font=('Courier New', 11),
                relief='flat',
                padx=20,
                pady=20
            )
            text_widget.pack(fill='both', expand=True)
            text_widget.insert('1.0', stats_text)
            text_widget.config(state='disabled')
            
        except Exception as e:
            logger.error(f"Error creating enhanced statistics section: {e}")
            error_label = ttk.Label(parent, text=f"Error loading statistics: {str(e)}", 
                                  style='Error.TLabel')
            error_label.grid(row=1, column=0, pady=20)
    
    def show_books(self) -> None:
        """Show books management"""
        self.clear_content()
        self.current_view = "books"
        
        books_frame = ttk.Frame(self.content_frame, style='Custom.TFrame', padding=20)
        books_frame.pack(fill='both', expand=True)
        
        # Header
        self.create_header(books_frame, "📚 Books Management", 
                          "Manage your library's book collection")
        
        # Add book form (Admin only)
        if self.controller.is_admin():
            self.create_book_form(books_frame)
        
        # Books list
        self.create_books_list(books_frame)
    
    def create_book_form(self, parent: ttk.Frame) -> None:
        """Create book addition form"""
        form_frame = ttk.LabelFrame(parent, text="➕ Add New Book", padding=15)
        form_frame.grid(row=1, column=0, sticky='ew', pady=(0, 20))
        parent.columnconfigure(0, weight=1)
        
        # Form fields
        self.book_entries = {}
        fields = [
            ('Title', 'title'),
            ('Author', 'author'),
            ('Category', 'category'),
            ('ISBN', 'isbn')
        ]
        
        for i, (label_text, field_key) in enumerate(fields):
            field_frame, label, entry = self.create_form_field(
                form_frame, f"{label_text}:", 30
            )
            field_frame.grid(row=i//2, column=(i%2)*2, columnspan=2, 
                           sticky='ew', padx=5, pady=5)
            self.book_entries[field_key] = entry
        
        # Add book button
        add_btn = ttk.Button(
            form_frame, 
            text="📚 Add Book", 
            command=self.add_book,
            style='Success.TButton'
        )
        add_btn.grid(row=2, column=0, columnspan=4, pady=15)
    
    def create_books_list(self, parent: ttk.Frame) -> None:
        """Create books list view"""
        list_frame = ttk.LabelFrame(parent, text="📖 Books Collection", padding=15)
        list_frame.grid(row=2, column=0, sticky='nsew', pady=10)
        parent.rowconfigure(2, weight=1)
        
        # Search bar
        search_frame, self.book_search_entry, self.book_search_var = self.create_search_bar(
            list_frame, "Search books by title, author, or ISBN...", self.search_books
        )
        search_frame.grid(row=0, column=0, sticky='ew', pady=(0, 15))
        list_frame.columnconfigure(0, weight=1)
        
        # Books table
        columns = ['ID', 'Title', 'Author', 'Category', 'ISBN', 'Status']
        table_frame, self.books_tree, v_scroll, h_scroll = self.create_data_table(
            list_frame, columns
        )
        table_frame.grid(row=1, column=0, sticky='nsew')
        list_frame.rowconfigure(1, weight=1)
        
        # Load books data
        self.refresh_books()
    
    def add_book(self) -> None:
        """Add new book"""
        try:
            # Get form data
            title = self.book_entries['title'].get().strip()
            author = self.book_entries['author'].get().strip()
            category = self.book_entries['category'].get().strip()
            isbn = self.book_entries['isbn'].get().strip()
            
            # Validate
            if not all([title, author, category, isbn]):
                self.show_message("Please fill all fields", 'error')
                return
            
            # Add book
            if self.controller.add_book(title, author, category, isbn):
                self.show_message("Book added successfully!", 'success')
                
                # Clear form
                for entry in self.book_entries.values():
                    entry.delete(0, tk.END)
                
                # Refresh list
                self.refresh_books()
            else:
                self.show_message("Failed to add book. ISBN may already exist.", 'error')
                
        except Exception as e:
            logger.error(f"Error adding book: {e}")
            self.show_message(f"Error adding book: {str(e)}", 'error')
    
    def search_books(self) -> None:
        """Search books"""
        self.refresh_books()
    
    def refresh_books(self) -> None:
        """Refresh books list"""
        try:
            # Clear existing items
            for item in self.books_tree.get_children():
                self.books_tree.delete(item)
            
            # Get search term
            search_term = self.book_search_var.get().strip()
            if search_term and search_term != "Search books by title, author, or ISBN...":
                books = self.controller.search_books(search_term)
            else:
                books = self.controller.get_all_books()
            
            # Populate tree
            for book in books:
                status_icon = "✅" if book['availability_status'] == 'available' else "📖"
                self.books_tree.insert('', 'end', values=(
                    book['book_id'],
                    StringHelper.truncate_string(book['title'], 30),
                    StringHelper.truncate_string(book['author'], 25),
                    book['category'],
                    book['isbn'],
                    f"{status_icon} {book['availability_status'].title()}"
                ))
                
        except Exception as e:
            logger.error(f"Error refreshing books: {e}")
    
    def show_members(self) -> None:
        """Show enhanced member management (available to both admin and librarian)"""
        self.clear_content()
        self.current_view = "members"
        
        try:
            # Import member management view
            from views.member_management import MemberManagementView
            
            # Create member management interface
            member_mgmt = MemberManagementView(
                self.content_frame, 
                self.controller, 
                self.refresh_transactions
            )
            logger.info("Member management view loaded successfully")
            
        except ImportError as e:
            logger.error(f"Member management view not found: {e}")
            # Fallback to basic member view
            self.show_basic_members_view()
        except Exception as e:
            logger.error(f"Error loading member management: {e}")
            # Show error message
            error_frame = ttk.Frame(self.content_frame, style='Custom.TFrame', padding=50)
            error_frame.pack(fill='both', expand=True)
            
            error_label = ttk.Label(
                error_frame, 
                text=f"Error loading member management:\\n{str(e)}\\n\\nPlease check the system configuration.",
                style='Error.TLabel',
                justify='center'
            )
            error_label.pack(pady=50)
    
    def show_basic_members_view(self) -> None:
        """Show basic member view as fallback"""
        members_frame = ttk.Frame(self.content_frame, style='Custom.TFrame', padding=20)
        members_frame.pack(fill='both', expand=True)
        
        # Header
        self.create_header(members_frame, "👥 Members Management", 
                          "Library member information and management")
        
        if self.controller.is_admin():
            # Admin can add members
            info_text = """
Member management interface is being enhanced.

Current capabilities:
• View all library members
• Search members by name, email, or phone
• Track member borrowing statistics
• Manage member accounts

Enhanced member management with issue limits and 
comprehensive tracking will be available soon.

For now, you can use the Books and Transactions 
sections to manage book issues and returns.
            """
        else:
            # Librarian view
            info_text = """
Welcome to Member Management!

As a librarian, you can:
• View all library members and their current status
• Track which books are issued to each member
• Handle book issues and returns
• Manage member borrowing limits
• Process overdue books and late fees

Enhanced member management interface is loading...
Please use the Transactions section for book operations.
            """
        
        info_label = ttk.Label(
            members_frame, 
            text=info_text.strip(),
            style='Info.TLabel', 
            justify='left'
        )
        info_label.grid(row=1, column=0, pady=50, padx=20, sticky='w')
    
    def show_transactions(self) -> None:
        """Show transaction management"""
        self.clear_content()
        self.current_view = "transactions"
        
        trans_frame = ttk.Frame(self.content_frame, style='Custom.TFrame', padding=20)
        trans_frame.pack(fill='both', expand=True)
        
        # Header
        self.create_header(trans_frame, "📋 Transaction Management", 
                          "Issue and return books, manage borrowing")
        
        # Quick actions
        self.create_transaction_actions(trans_frame)
        
        # Transactions list
        self.create_transactions_list(trans_frame)
    
    def create_transaction_actions(self, parent: ttk.Frame) -> None:
        """Create transaction action buttons"""
        actions_frame = ttk.Frame(parent, style='Custom.TFrame')
        actions_frame.grid(row=1, column=0, sticky='ew', pady=(0, 20))
        
        buttons = [
            ("📖 Issue Book", self.show_issue_dialog, 'Success.TButton'),
            ("📚 Return Book", self.show_return_dialog, 'Warning.TButton'),
            ("⏰ Overdue Books", self.show_overdue_books, 'Error.TButton'),
            ("🔄 Refresh", self.refresh_transactions, 'Custom.TButton')
        ]
        
        for i, (text, command, style) in enumerate(buttons):
            btn = ttk.Button(actions_frame, text=text, command=command, style=style)
            btn.grid(row=0, column=i, padx=5, sticky='ew')
            actions_frame.columnconfigure(i, weight=1)
    
    def create_transactions_list(self, parent: ttk.Frame) -> None:
        """Create transactions list view"""
        list_frame = ttk.LabelFrame(parent, text="📋 Currently Issued Books", padding=15)
        list_frame.grid(row=2, column=0, sticky='nsew', pady=10)
        parent.rowconfigure(2, weight=1)
        parent.columnconfigure(0, weight=1)
        
        # Transactions table
        columns = ['Transaction ID', 'Book Title', 'Member', 'Issue Date', 'Days', 'Status']
        table_frame, self.transactions_tree, v_scroll, h_scroll = self.create_data_table(
            list_frame, columns
        )
        table_frame.pack(fill='both', expand=True)
        
        # Load transactions data
        self.refresh_transactions()
    
    def refresh_transactions(self) -> None:
        """Refresh transactions list"""
        try:
            # Clear existing items
            for item in self.transactions_tree.get_children():
                self.transactions_tree.delete(item)
            
            # Get issued books
            issued_books = self.controller.get_issued_books()
            
            for trans in issued_books:
                # Calculate days and status
                issue_date = datetime.datetime.fromisoformat(trans['issue_date'])
                days_issued = (datetime.datetime.now() - issue_date).days
                
                status_icon = "⚠️" if days_issued > settings.BORROWING_PERIOD_DAYS else "📖"
                status_text = "Overdue" if days_issued > settings.BORROWING_PERIOD_DAYS else "Issued"
                
                self.transactions_tree.insert('', 'end', values=(
                    trans['transaction_id'],
                    StringHelper.truncate_string(trans['book_title'], 35),
                    StringHelper.truncate_string(trans['member_name'], 25),
                    trans['issue_date'][:10],
                    days_issued,
                    f"{status_icon} {status_text}"
                ))
                
        except Exception as e:
            logger.error(f"Error refreshing transactions: {e}")
    
    def show_overdue_books(self) -> None:
        """Show overdue books in a separate dialog"""
        try:
            OverdueBooksDialog(self.root, self.controller, self.refresh_transactions)
        except Exception as e:
            logger.error(f"Error showing overdue books: {e}")
            self.show_message(f"Error loading overdue books: {str(e)}", 'error')
    
    def show_issue_dialog(self) -> None:
        """Show book issue dialog"""
        IssueBookDialog(self.root, self.controller, self.refresh_transactions)
    
    def show_return_dialog(self) -> None:
        """Show book return dialog"""
        ReturnBookDialog(self.root, self.controller, self.refresh_transactions)
    
    def show_users(self) -> None:
        """Show users management (Admin only)"""
        if not self.controller.is_admin():
            self.show_message("Access denied", 'error')
            return
        
        self.clear_content()
        self.current_view = "users"
        
        users_frame = ttk.Frame(self.content_frame, style='Custom.TFrame', padding=20)
        users_frame.pack(fill='both', expand=True)
        
        self.create_header(users_frame, "👤 Users Management", 
                          "Manage system users and permissions")
        
        # User management interface (basic implementation)
        self.create_users_list(users_frame)
    
    def create_users_list(self, parent: ttk.Frame) -> None:
        """Create users list view"""
        try:
            users = self.controller.get_all_users()
            
            # Users table
            list_frame = ttk.LabelFrame(parent, text="System Users", padding=15)
            list_frame.grid(row=1, column=0, sticky='nsew', pady=20)
            parent.rowconfigure(1, weight=1)
            parent.columnconfigure(0, weight=1)
            
            columns = ['ID', 'Username', 'Role', 'Created Date']
            table_frame, users_tree, v_scroll, h_scroll = self.create_data_table(
                list_frame, columns
            )
            table_frame.pack(fill='both', expand=True)
            
            # Populate users
            for user in users:
                users_tree.insert('', 'end', values=(
                    user['id'],
                    user['username'],
                    user['role'].title(),
                    user['created_date'][:10] if user['created_date'] else 'Unknown'
                ))
            
            # Info label
            info_text = f"Total system users: {len(users)}"
            info_label = ttk.Label(parent, text=info_text, style='Info.TLabel')
            info_label.grid(row=2, column=0, pady=10)
            
        except Exception as e:
            logger.error(f"Error creating users list: {e}")
            error_label = ttk.Label(parent, text=f"Error loading users: {str(e)}", 
                                  style='Error.TLabel')
            error_label.grid(row=1, column=0, pady=50)
    
    def show_reports(self) -> None:
        """Show reports (Admin only)"""
        if not self.controller.is_admin():
            self.show_message("Access denied", 'error')
            return
        
        self.clear_content()
        self.current_view = "reports"
        
        reports_frame = ttk.Frame(self.content_frame, style='Custom.TFrame', padding=20)
        reports_frame.pack(fill='both', expand=True)
        
        self.create_header(reports_frame, "📊 Reports & Analytics", 
                          "Generate and export comprehensive reports")
        
        # Export buttons
        self.create_export_buttons(reports_frame)
    
    def create_export_buttons(self, parent: ttk.Frame) -> None:
        """Create export report buttons"""
        export_frame = ttk.LabelFrame(parent, text="📤 Export Reports", padding=15)
        export_frame.grid(row=1, column=0, sticky='ew', pady=20)
        
        buttons = [
            ("📚 Export Books", lambda: self.export_data('books')),
            ("👥 Export Members", lambda: self.export_data('members')),
            ("📋 Export Transactions", lambda: self.export_data('transactions')),
            ("⚠️ Export Overdue", lambda: self.export_data('overdue')),
        ]
        
        for i, (text, command) in enumerate(buttons):
            btn = ttk.Button(export_frame, text=text, command=command, 
                           style='Custom.TButton')
            btn.grid(row=0, column=i, padx=10, sticky='ew')
            export_frame.columnconfigure(i, weight=1)
    
    def export_data(self, data_type: str) -> None:
        """Export data to CSV"""
        try:
            if data_type == 'books':
                data = self.controller.get_all_books()
            elif data_type == 'members':
                data = self.controller.get_all_members()
            elif data_type == 'transactions':
                data = self.controller.get_issued_books()
            elif data_type == 'overdue':
                data = self.controller.get_overdue_books()
            else:
                self.show_message("Unknown export type", 'error')
                return
            
            if data:
                result = self.controller.export_report(data_type, data)
                self.show_message(result, 'success')
            else:
                self.show_message(f"No {data_type} data found to export", 'warning')
                
        except Exception as e:
            logger.error(f"Export error: {e}")
            self.show_message(f"Export failed: {str(e)}", 'error')
    
    def logout(self) -> None:
        """Handle user logout"""
        if self.confirm_action("Are you sure you want to logout?", "Confirm Logout"):
            try:
                self.controller.logout()
                self.root.destroy()
                
                # Restart the application with login screen
                from main import LibraryManagementApp
                app = LibraryManagementApp()
                app.run()
                
            except Exception as e:
                logger.error(f"Logout error: {e}")
                self.root.destroy()
    
    def on_closing(self) -> None:
        """Handle window closing"""
        if self.confirm_action("Are you sure you want to exit?", "Confirm Exit"):
            try:
                self.controller.logout()
                self.root.destroy()
            except Exception as e:
                logger.error(f"Closing error: {e}")
                self.root.destroy()


class IssueBookDialog(DialogWindow):
    """Enhanced dialog for issuing books with member validation"""
    
    def __init__(self, parent, controller, refresh_callback):
        super().__init__(parent, "Issue Book", 500, 350)
        self.controller = controller
        self.refresh_callback = refresh_callback
        self.setup_issue_ui()
    
    def setup_issue_ui(self):
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="📖 Issue Book to Member", style='Subheading.TLabel').pack(pady=(0, 20))
        
        # Book ID
        book_frame, _, self.book_entry = self.create_form_field(frame, "Book ID:", 20)
        book_frame.pack(fill='x', pady=5)
        
        # Member ID
        member_frame, _, self.member_entry = self.create_form_field(frame, "Member ID:", 20)
        member_frame.pack(fill='x', pady=5)
        
        # Info section
        info_text = """💡 Tips:
• Member must be active and not have overdue books
• Member must not exceed their book limit
• Book must be available for issue"""
        
        info_label = ttk.Label(frame, text=info_text, style='Info.TLabel', justify='left')
        info_label.pack(pady=15)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="📖 Issue Book", command=self.issue_book, 
                  style='Success.TButton').pack(side='left', padx=5)
        ttk.Button(btn_frame, text="❌ Cancel", command=self.root.destroy, 
                  style='Custom.TButton').pack(side='left', padx=5)
    
    def issue_book(self):
        try:
            book_id = int(self.book_entry.get())
            member_id = int(self.member_entry.get())
            
            if self.controller.issue_book(book_id, member_id):
                self.show_message("Book issued successfully!", 'success')
                self.refresh_callback()
                self.root.destroy()
            else:
                self.show_message("Failed to issue book. Please check:\\n• Member limits and status\\n• Book availability\\n• Overdue books", 'error')
        except ValueError:
            self.show_message("Please enter valid numeric IDs", 'error')
        except Exception as e:
            logger.error(f"Error issuing book: {e}")
            self.show_message(f"Error issuing book: {str(e)}", 'error')


class ReturnBookDialog(DialogWindow):
    """Enhanced dialog for returning books with late fee calculation"""
    
    def __init__(self, parent, controller, refresh_callback):
        super().__init__(parent, "Return Book", 500, 350)
        self.controller = controller
        self.refresh_callback = refresh_callback
        self.setup_return_ui()
    
    def setup_return_ui(self):
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="📚 Return Book", style='Subheading.TLabel').pack(pady=(0, 20))
        
        # Book ID
        book_frame, _, self.book_entry = self.create_form_field(frame, "Book ID:", 20)
        book_frame.pack(fill='x', pady=5)
        
        # Member ID
        member_frame, _, self.member_entry = self.create_form_field(frame, "Member ID:", 20)
        member_frame.pack(fill='x', pady=5)
        
        # Info section
        info_text = f"""💡 Return Information:
• Late fee: ${settings.DAILY_LATE_FEE}/day after {settings.BORROWING_PERIOD_DAYS} days
• System will automatically calculate any late fees
• Member statistics will be updated"""
        
        info_label = ttk.Label(frame, text=info_text, style='Info.TLabel', justify='left')
        info_label.pack(pady=15)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="📚 Return Book", command=self.return_book, 
                  style='Warning.TButton').pack(side='left', padx=5)
        ttk.Button(btn_frame, text="❌ Cancel", command=self.root.destroy, 
                  style='Custom.TButton').pack(side='left', padx=5)
    
    def return_book(self):
        try:
            book_id = int(self.book_entry.get())
            member_id = int(self.member_entry.get())
            
            success, late_fee = self.controller.return_book(book_id, member_id)
            
            if success:
                msg = "Book returned successfully!"
                if late_fee > 0:
                    msg += f"\\nLate fee: ${late_fee:.2f}"
                self.show_message(msg, 'success')
                self.refresh_callback()
                self.root.destroy()
            else:
                self.show_message("Failed to return book. Please check:\\n• Book and member IDs\\n• Active transaction status", 'error')
        except ValueError:
            self.show_message("Please enter valid numeric IDs", 'error')
        except Exception as e:
            logger.error(f"Error returning book: {e}")
            self.show_message(f"Error returning book: {str(e)}", 'error')


class OverdueBooksDialog(DialogWindow):
    """Dialog showing all overdue books with member information"""
    
    def __init__(self, parent, controller, refresh_callback):
        super().__init__(parent, "Overdue Books", 800, 500)
        self.controller = controller
        self.refresh_callback = refresh_callback
        self.setup_overdue_ui()
    
    def setup_overdue_ui(self):
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Header
        header_label = ttk.Label(main_frame, text="⚠️ Overdue Books Report", style='Subheading.TLabel')
        header_label.pack(pady=(0, 20))
        
        try:
            # Get overdue books
            overdue_books = self.controller.get_overdue_books()
            
            if not overdue_books:
                no_overdue_label = ttk.Label(main_frame, text="🎉 No overdue books! All members are current.", 
                                           style='Success.TLabel')
                no_overdue_label.pack(pady=50)
                
                ttk.Button(main_frame, text="✅ Close", command=self.root.destroy, 
                          style='Custom.TButton').pack()
                return
            
            # Overdue books table
            list_frame = ttk.LabelFrame(main_frame, text=f"Overdue Books ({len(overdue_books)})", padding=10)
            list_frame.pack(fill='both', expand=True, pady=(0, 15))
            
            columns = ['Book', 'Author', 'Member', 'Email', 'Issue Date', 'Days Overdue', 'Late Fee']
            
            self.overdue_tree = ttk.Treeview(list_frame, columns=columns, show='headings', style='Custom.Treeview')
            
            # Configure columns
            column_configs = {
                'Book': {'width': 120, 'anchor': 'w'},
                'Author': {'width': 100, 'anchor': 'w'},
                'Member': {'width': 120, 'anchor': 'w'},
                'Email': {'width': 150, 'anchor': 'w'},
                'Issue Date': {'width': 80, 'anchor': 'center'},
                'Days Overdue': {'width': 80, 'anchor': 'center'},
                'Late Fee': {'width': 80, 'anchor': 'center'}
            }
            
            for col in columns:
                config = column_configs.get(col, {'width': 100, 'anchor': 'w'})
                self.overdue_tree.heading(col, text=col)
                self.overdue_tree.column(col, width=config['width'], anchor=config['anchor'])
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.overdue_tree.yview)
            self.overdue_tree.configure(yscrollcommand=scrollbar.set)
            
            self.overdue_tree.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
            
            # Populate overdue books
            total_late_fees = 0
            for book in overdue_books:
                days_overdue = max(0, book.get('days_overdue', 0))
                late_fee = book.get('calculated_late_fee', 0)
                total_late_fees += late_fee
                
                self.overdue_tree.insert('', 'end', values=(
                    StringHelper.truncate_string(book.get('book_title', 'Unknown'), 15),
                    StringHelper.truncate_string(book.get('book_author', 'Unknown'), 12),
                    StringHelper.truncate_string(book.get('member_name', 'Unknown'), 15),
                    StringHelper.truncate_string(book.get('member_email', 'Unknown'), 20),
                    book.get('issue_date', 'Unknown')[:10],
                    days_overdue,
                    f"${late_fee:.2f}"
                ))
            
            # Summary
            summary_text = f"Total overdue books: {len(overdue_books)} | Total late fees: ${total_late_fees:.2f}"
            summary_label = ttk.Label(main_frame, text=summary_text, style='Warning.TLabel')
            summary_label.pack(pady=10)
            
            # Close button
            ttk.Button(main_frame, text="❌ Close", command=self.root.destroy, 
                      style='Custom.TButton').pack()
                      
        except Exception as e:
            logger.error(f"Error loading overdue books: {e}")
            error_label = ttk.Label(main_frame, text=f"Error loading overdue books: {str(e)}", 
                                  style='Error.TLabel')
            error_label.pack(pady=50)
