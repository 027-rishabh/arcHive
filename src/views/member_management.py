"""
Complete Member Management Interface with Add/Edit/Delete functionality for Admins
Enhanced views for comprehensive member management
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from typing import Optional, List, Dict, Callable
import datetime

from views.base_window import BaseWindow, DialogWindow
from config.settings import settings
from utils.logger import get_logger
from utils.helpers import DataHelper, StringHelper

logger = get_logger(__name__)


class MemberManagementView:
    """Complete member management interface for admins and librarians"""
    
    def __init__(self, parent_frame: ttk.Frame, controller, refresh_callback: Callable = None):
        """Initialize member management view"""
        self.parent_frame = parent_frame
        self.controller = controller
        self.refresh_callback = refresh_callback
        
        # UI components
        self.member_search_var = None
        self.members_tree = None
        self.filter_var = None
        
        self.setup_member_management()
        logger.info("Complete member management view initialized")
    
    def setup_member_management(self) -> None:
        """Setup comprehensive member management interface"""
        # Clear parent frame
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
        
        # Main container
        main_container = ttk.Frame(self.parent_frame, style='Custom.TFrame')
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header with actions
        self.create_header_with_actions(main_container)
        
        # Search and filters
        self.create_search_and_filters(main_container)
        
        # Members list
        self.create_members_list(main_container)
        
        # Action buttons
        self.create_action_buttons(main_container)
        
        # Load initial data
        self.refresh_members()
    
    def create_header_with_actions(self, parent: ttk.Frame) -> None:
        """Create header section with member actions"""
        header_frame = ttk.Frame(parent, style='Custom.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Title
        title_label = ttk.Label(
            header_frame,
            text="👥 Member Management",
            style='Heading.TLabel'
        )
        title_label.pack(side='left')
        
        # Admin actions
        if self.controller.is_admin():
            actions_frame = ttk.Frame(header_frame)
            actions_frame.pack(side='right')
            
            ttk.Button(
                actions_frame,
                text="➕ Add Member",
                command=self.add_member_dialog,
                style='Success.TButton'
            ).pack(side='left', padx=5)
        
        # Quick stats
        self.stats_label = ttk.Label(
            header_frame,
            text="Loading member statistics...",
            style='Info.TLabel'
        )
        self.stats_label.pack(side='bottom', anchor='w', pady=(10, 0))
        
        # Update stats
        self.update_member_stats()
    
    def update_member_stats(self) -> None:
        """Update member statistics display"""
        try:
            stats = self.controller.member_model.get_member_statistics()
            stats_text = (f"👥 Total: {stats.get('total_members', 0)} | "
                         f"📚 Active: {stats.get('active_borrowers', 0)} | "
                         f"⚠️ Overdue: {stats.get('overdue_members', 0)} | "
                         f"💰 Fines: ${stats.get('total_fines', 0):.2f}")
            self.stats_label.configure(text=stats_text)
        except Exception as e:
            logger.error(f"Error updating member stats: {e}")
    
    def create_search_and_filters(self, parent: ttk.Frame) -> None:
        """Create search bar and filters"""
        search_frame = ttk.Frame(parent, style='Custom.TFrame')
        search_frame.pack(fill='x', pady=(0, 15))
        
        # Search entry
        search_container = ttk.Frame(search_frame)
        search_container.pack(side='left', fill='x', expand=True)
        
        ttk.Label(search_container, text="🔍 Search:", style='Custom.TLabel').pack(side='left', padx=(0, 5))
        
        self.member_search_var = tk.StringVar()
        search_entry = ttk.Entry(
            search_container,
            textvariable=self.member_search_var,
            width=30,
            style='Custom.TEntry'
        )
        search_entry.pack(side='left', padx=(0, 10))
        search_entry.bind('<KeyRelease>', lambda e: self.on_search_change())
        
        # Filter dropdown
        filter_container = ttk.Frame(search_frame)
        filter_container.pack(side='right')
        
        ttk.Label(filter_container, text="Filter:", style='Custom.TLabel').pack(side='left', padx=(0, 5))
        
        self.filter_var = tk.StringVar(value="All Members")
        filter_combo = ttk.Combobox(
            filter_container,
            textvariable=self.filter_var,
            values=["All Members", "Active Borrowers", "Overdue Members", "Students", "Faculty", "Staff"],
            width=15,
            state='readonly'
        )
        filter_combo.pack(side='left')
        filter_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_members())
    
    def create_members_list(self, parent: ttk.Frame) -> None:
        """Create comprehensive members list table"""
        list_frame = ttk.LabelFrame(parent, text="📋 Library Members", padding=10)
        list_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        # Members table
        columns = ['ID', 'Name', 'Email', 'Phone', 'Type', 'Status', 'Issues', 'Fine']
        
        self.members_tree = ttk.Treeview(list_frame, columns=columns, show='headings', style='Custom.Treeview')
        
        # Configure columns
        column_configs = {
            'ID': {'width': 50, 'anchor': 'center'},
            'Name': {'width': 150, 'anchor': 'w'},
            'Email': {'width': 180, 'anchor': 'w'},
            'Phone': {'width': 100, 'anchor': 'w'},
            'Type': {'width': 80, 'anchor': 'center'},
            'Status': {'width': 80, 'anchor': 'center'},
            'Issues': {'width': 60, 'anchor': 'center'},
            'Fine': {'width': 70, 'anchor': 'center'}
        }
        
        for col in columns:
            config = column_configs.get(col, {'width': 100, 'anchor': 'w'})
            self.members_tree.heading(col, text=col)
            self.members_tree.column(col, width=config['width'], anchor=config['anchor'], minwidth=50)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.members_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient='horizontal', command=self.members_tree.xview)
        self.members_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.members_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Double-click to view member details
        self.members_tree.bind('<Double-1>', self.on_member_double_click)
        
        # Right-click context menu
        self.create_context_menu()
    
    def create_context_menu(self) -> None:
        """Create right-click context menu"""
        self.context_menu = tk.Menu(self.parent_frame, tearoff=0)
        self.context_menu.add_command(label="👁️ View Details", command=self.view_member_details)
        self.context_menu.add_command(label="📚 Issue Book", command=self.quick_issue_book)
        self.context_menu.add_command(label="📖 Return Book", command=self.quick_return_book)
        self.context_menu.add_separator()
        
        if self.controller.is_admin():
            self.context_menu.add_command(label="✏️ Edit Member", command=self.edit_member_dialog)
            self.context_menu.add_command(label="🗑️ Delete Member", command=self.delete_member)
            self.context_menu.add_separator()
        
        self.context_menu.add_command(label="🔄 Refresh", command=self.refresh_members)
        
        self.members_tree.bind('<Button-3>', self.show_context_menu)
    
    def show_context_menu(self, event) -> None:
        """Show context menu on right-click"""
        try:
            item = self.members_tree.identify_row(event.y)
            if item:
                self.members_tree.selection_set(item)
                self.context_menu.post(event.x_root, event.y_root)
        except Exception as e:
            logger.error(f"Error showing context menu: {e}")
    
    def create_action_buttons(self, parent: ttk.Frame) -> None:
        """Create action buttons"""
        button_frame = ttk.Frame(parent, style='Custom.TFrame')
        button_frame.pack(fill='x')
        
        buttons = []
        
        # Common buttons
        buttons.extend([
            ("👁️ View Details", self.view_member_details, 'Custom.TButton'),
            ("📚 Quick Issue", self.quick_issue_book, 'Success.TButton'),
            ("📖 Quick Return", self.quick_return_book, 'Warning.TButton')
        ])
        
        # Admin buttons
        if self.controller.is_admin():
            buttons.extend([
                ("➕ Add Member", self.add_member_dialog, 'Success.TButton'),
                ("✏️ Edit Member", self.edit_member_dialog, 'Custom.TButton'),
                ("🗑️ Delete Member", self.delete_member, 'Error.TButton')
            ])
        
        buttons.append(("🔄 Refresh", self.refresh_members, 'Custom.TButton'))
        
        for i, (text, command, style) in enumerate(buttons):
            btn = ttk.Button(button_frame, text=text, command=command, style=style)
            btn.pack(side='left', padx=5, fill='x', expand=True)
    
    def on_search_change(self) -> None:
        """Handle search input change"""
        # Small delay to avoid too frequent searches
        if hasattr(self, '_search_timer'):
            self.parent_frame.after_cancel(self._search_timer)
        self._search_timer = self.parent_frame.after(500, self.refresh_members)
    
    def refresh_members(self) -> None:
        """Refresh members list"""
        try:
            # Clear existing items
            for item in self.members_tree.get_children():
                self.members_tree.delete(item)
            
            # Get search term and filter
            search_term = self.member_search_var.get().strip() if self.member_search_var else ""
            filter_type = self.filter_var.get() if self.filter_var else "All Members"
            
            # Get members based on search and filter
            if search_term:
                members = self.controller.member_model.search_members(search_term)
            else:
                members = self.controller.member_model.get_all_members()
            
            # Apply filters
            filtered_members = self.apply_member_filters(members, filter_type)
            
            # Populate tree
            for member in filtered_members:
                self.insert_member_row(member)
            
            # Update stats
            self.update_member_stats()
            
        except Exception as e:
            logger.error(f"Error refreshing members: {e}")
    
    def apply_member_filters(self, members: List[Dict], filter_type: str) -> List[Dict]:
        """Apply filters to member list"""
        if filter_type == "All Members":
            return members
        elif filter_type == "Active Borrowers":
            return [m for m in members if m.get('current_issues', 0) > 0]
        elif filter_type == "Overdue Members":
            # This would need additional logic to check for overdue books
            return [m for m in members if m.get('member_status') == 'overdue']
        elif filter_type in ["Students", "Faculty", "Staff"]:
            return [m for m in members if m.get('member_type') == filter_type.rstrip('s')]
        else:
            return members
    
    def insert_member_row(self, member: Dict) -> None:
        """Insert member row into tree"""
        try:
            member_id = member['member_id']
            name = member.get('full_name', f"{member.get('first_name', '')} {member.get('last_name', '')}").strip()
            email = StringHelper.truncate_string(member['email'], 25)
            phone = member['phone'][:10] + '...' if len(member['phone']) > 10 else member['phone']
            member_type = member.get('member_type', 'General')
            
            # Status with icon
            status = member.get('member_status', 'active')
            if status == 'active':
                status_display = "✅ Active"
            elif status == 'suspended':
                status_display = "⚠️ Suspended"
            elif status == 'blocked':
                status_display = "🚫 Blocked"
            else:
                status_display = "❓ Unknown"
            
            # Current issues
            current_issues = member.get('current_issues', 0)
            max_books = member.get('max_books', 3)
            issues_display = f"{current_issues}/{max_books}"
            
            # Fine balance
            fine_balance = member.get('fine_balance', 0)
            fine_display = f"${fine_balance:.2f}" if fine_balance > 0 else "-"
            
            # Insert row
            self.members_tree.insert('', 'end', values=(
                member_id,
                StringHelper.truncate_string(name, 20),
                email,
                phone,
                member_type,
                status_display,
                issues_display,
                fine_display
            ))
                
        except Exception as e:
            logger.error(f"Error inserting member row: {e}")
    
    def get_selected_member_id(self) -> Optional[int]:
        """Get selected member ID"""
        selection = self.members_tree.selection()
        if not selection:
            return None
        
        try:
            item = selection[0]
            values = self.members_tree.item(item, 'values')
            return int(values[0]) if values else None
        except (IndexError, ValueError):
            return None
    
    def on_member_double_click(self, event) -> None:
        """Handle double-click on member"""
        self.view_member_details()
    
    def add_member_dialog(self) -> None:
        """Open add member dialog (Admin only)"""
        if not self.controller.is_admin():
            self.show_message("Access denied. Only administrators can add members.", 'error')
            return
        
        try:
            AddMemberDialog(self.parent_frame.winfo_toplevel(), self.controller, self.refresh_members)
        except Exception as e:
            logger.error(f"Error opening add member dialog: {e}")
            self.show_message(f"Error opening add member dialog: {str(e)}", 'error')
    
    def edit_member_dialog(self) -> None:
        """Open edit member dialog (Admin only)"""
        if not self.controller.is_admin():
            self.show_message("Access denied. Only administrators can edit members.", 'error')
            return
        
        member_id = self.get_selected_member_id()
        if not member_id:
            self.show_message("Please select a member to edit", 'warning')
            return
        
        try:
            EditMemberDialog(self.parent_frame.winfo_toplevel(), self.controller, member_id, self.refresh_members)
        except Exception as e:
            logger.error(f"Error opening edit member dialog: {e}")
            self.show_message(f"Error opening edit dialog: {str(e)}", 'error')
    
    def delete_member(self) -> None:
        """Delete selected member (Admin only)"""
        if not self.controller.is_admin():
            self.show_message("Access denied. Only administrators can delete members.", 'error')
            return
        
        member_id = self.get_selected_member_id()
        if not member_id:
            self.show_message("Please select a member to delete", 'warning')
            return
        
        try:
            # Get member details for confirmation
            member = self.controller.member_model.get_member_by_id(member_id)
            if not member:
                self.show_message("Member not found", 'error')
                return
            
            member_name = member.get('full_name', f"Member {member_id}")
            
            # Confirm deletion
            if messagebox.askyesno(
                "Confirm Deletion", 
                f"Are you sure you want to delete member '{member_name}'?\\n\\n"
                "This will deactivate the member account. "
                "Members with active book issues cannot be deleted."
            ):
                if self.controller.member_model.delete_member(member_id):
                    self.show_message(f"Member '{member_name}' has been deactivated successfully.", 'success')
                    self.refresh_members()
                else:
                    self.show_message(
                        "Failed to delete member. "
                        "Please ensure the member has no active book issues.",
                        'error'
                    )
                    
        except Exception as e:
            logger.error(f"Error deleting member: {e}")
            self.show_message(f"Error deleting member: {str(e)}", 'error')
    
    def view_member_details(self) -> None:
        """Open member details dialog"""
        member_id = self.get_selected_member_id()
        if not member_id:
            self.show_message("Please select a member", 'warning')
            return
        
        try:
            MemberDetailDialog(self.parent_frame.winfo_toplevel(), self.controller, member_id, self.refresh_members)
        except Exception as e:
            logger.error(f"Error opening member details: {e}")
            self.show_message(f"Error opening member details: {str(e)}", 'error')
    
    def quick_issue_book(self) -> None:
        """Quick issue book dialog"""
        member_id = self.get_selected_member_id()
        if not member_id:
            self.show_message("Please select a member", 'warning')
            return
        
        try:
            QuickIssueDialog(self.parent_frame.winfo_toplevel(), self.controller, member_id, self.refresh_members)
        except Exception as e:
            logger.error(f"Error opening quick issue dialog: {e}")
            self.show_message(f"Error opening quick issue: {str(e)}", 'error')
    
    def quick_return_book(self) -> None:
        """Quick return book dialog"""
        member_id = self.get_selected_member_id()
        if not member_id:
            self.show_message("Please select a member", 'warning')
            return
        
        try:
            QuickReturnDialog(self.parent_frame.winfo_toplevel(), self.controller, member_id, self.refresh_members)
        except Exception as e:
            logger.error(f"Error opening quick return dialog: {e}")
            self.show_message(f"Error opening quick return: {str(e)}", 'error')
    
    def show_message(self, message: str, msg_type: str = 'info') -> None:
        """Show message dialog"""
        if msg_type == 'error':
            messagebox.showerror("Member Management", message)
        elif msg_type == 'warning':
            messagebox.showwarning("Member Management", message)
        elif msg_type == 'success':
            messagebox.showinfo("Member Management", message)
        else:
            messagebox.showinfo("Member Management", message)


class AddMemberDialog(DialogWindow):
    """Comprehensive dialog for adding new members"""
    
    def __init__(self, parent, controller, refresh_callback: Callable = None):
        super().__init__(parent, "Add New Member", 600, 700)
        self.controller = controller
        self.refresh_callback = refresh_callback
        
        self.member_entries = {}
        self.setup_add_member_ui()
    
    def setup_add_member_ui(self) -> None:
        """Setup comprehensive add member interface"""
        # Create scrollable frame
        canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Main form frame
        main_frame = ttk.Frame(scrollable_frame, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Header
        header_label = ttk.Label(main_frame, text="➕ Add New Library Member", style='Subheading.TLabel')
        header_label.pack(pady=(0, 20))
        
        # Personal Information Section
        self.create_personal_info_section(main_frame)
        
        # Contact Information Section
        self.create_contact_info_section(main_frame)
        
        # Address Information Section
        self.create_address_info_section(main_frame)
        
        # Emergency Contact Section
        self.create_emergency_contact_section(main_frame)
        
        # Additional Information Section
        self.create_additional_info_section(main_frame)
        
        # Buttons
        self.create_form_buttons(main_frame)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Focus on first field
        if 'first_name' in self.member_entries:
            self.member_entries['first_name'].focus()
    
    def create_personal_info_section(self, parent: ttk.Frame) -> None:
        """Create personal information section"""
        personal_frame = ttk.LabelFrame(parent, text="👤 Personal Information", padding=15)
        personal_frame.pack(fill='x', pady=(0, 15))
        
        # First Name and Last Name
        name_frame = ttk.Frame(personal_frame)
        name_frame.pack(fill='x', pady=5)
        
        # First Name
        ttk.Label(name_frame, text="First Name *:", style='Custom.TLabel').grid(row=0, column=0, sticky='w', padx=(0, 10))
        self.member_entries['first_name'] = ttk.Entry(name_frame, width=20, style='Custom.TEntry')
        self.member_entries['first_name'].grid(row=0, column=1, sticky='ew', padx=(0, 20))
        
        # Last Name
        ttk.Label(name_frame, text="Last Name *:", style='Custom.TLabel').grid(row=0, column=2, sticky='w', padx=(0, 10))
        self.member_entries['last_name'] = ttk.Entry(name_frame, width=20, style='Custom.TEntry')
        self.member_entries['last_name'].grid(row=0, column=3, sticky='ew')
        
        name_frame.columnconfigure(1, weight=1)
        name_frame.columnconfigure(3, weight=1)
        
        # Date of Birth and Gender
        dob_frame = ttk.Frame(personal_frame)
        dob_frame.pack(fill='x', pady=5)
        
        # Date of Birth
        ttk.Label(dob_frame, text="Date of Birth:", style='Custom.TLabel').grid(row=0, column=0, sticky='w', padx=(0, 10))
        self.member_entries['date_of_birth'] = ttk.Entry(dob_frame, width=15, style='Custom.TEntry')
        self.member_entries['date_of_birth'].grid(row=0, column=1, sticky='ew', padx=(0, 20))
        
        # Gender
        ttk.Label(dob_frame, text="Gender:", style='Custom.TLabel').grid(row=0, column=2, sticky='w', padx=(0, 10))
        self.member_entries['gender'] = ttk.Combobox(dob_frame, width=15, values=['Male', 'Female', 'Other', 'Prefer not to say'], state='readonly')
        self.member_entries['gender'].grid(row=0, column=3, sticky='ew')
        
        dob_frame.columnconfigure(1, weight=1)
        dob_frame.columnconfigure(3, weight=1)
        
        # Add placeholder text for date
        self.member_entries['date_of_birth'].insert(0, "YYYY-MM-DD (optional)")
        self.member_entries['date_of_birth'].bind('<FocusIn>', lambda e: self._clear_placeholder(e, "YYYY-MM-DD (optional)"))
    
    def create_contact_info_section(self, parent: ttk.Frame) -> None:
        """Create contact information section"""
        contact_frame = ttk.LabelFrame(parent, text="📞 Contact Information", padding=15)
        contact_frame.pack(fill='x', pady=(0, 15))
        
        # Email
        email_frame = ttk.Frame(contact_frame)
        email_frame.pack(fill='x', pady=5)
        ttk.Label(email_frame, text="Email Address *:", style='Custom.TLabel').pack(side='left', padx=(0, 10))
        self.member_entries['email'] = ttk.Entry(email_frame, style='Custom.TEntry')
        self.member_entries['email'].pack(side='left', fill='x', expand=True)
        
        # Phone
        phone_frame = ttk.Frame(contact_frame)
        phone_frame.pack(fill='x', pady=5)
        ttk.Label(phone_frame, text="Phone Number *:", style='Custom.TLabel').pack(side='left', padx=(0, 10))
        self.member_entries['phone'] = ttk.Entry(phone_frame, style='Custom.TEntry')
        self.member_entries['phone'].pack(side='left', fill='x', expand=True)
    
    def create_address_info_section(self, parent: ttk.Frame) -> None:
        """Create address information section"""
        address_frame = ttk.LabelFrame(parent, text="🏠 Address Information", padding=15)
        address_frame.pack(fill='x', pady=(0, 15))
        
        # Address Line 1
        addr1_frame = ttk.Frame(address_frame)
        addr1_frame.pack(fill='x', pady=3)
        ttk.Label(addr1_frame, text="Address Line 1:", style='Custom.TLabel').pack(side='left', padx=(0, 10))
        self.member_entries['address_line1'] = ttk.Entry(addr1_frame, style='Custom.TEntry')
        self.member_entries['address_line1'].pack(side='left', fill='x', expand=True)
        
        # Address Line 2
        addr2_frame = ttk.Frame(address_frame)
        addr2_frame.pack(fill='x', pady=3)
        ttk.Label(addr2_frame, text="Address Line 2:", style='Custom.TLabel').pack(side='left', padx=(0, 10))
        self.member_entries['address_line2'] = ttk.Entry(addr2_frame, style='Custom.TEntry')
        self.member_entries['address_line2'].pack(side='left', fill='x', expand=True)
        
        # City, State, Postal Code
        location_frame = ttk.Frame(address_frame)
        location_frame.pack(fill='x', pady=3)
        
        ttk.Label(location_frame, text="City:", style='Custom.TLabel').grid(row=0, column=0, sticky='w', padx=(0, 5))
        self.member_entries['city'] = ttk.Entry(location_frame, width=15, style='Custom.TEntry')
        self.member_entries['city'].grid(row=0, column=1, sticky='ew', padx=(0, 10))
        
        ttk.Label(location_frame, text="State:", style='Custom.TLabel').grid(row=0, column=2, sticky='w', padx=(0, 5))
        self.member_entries['state'] = ttk.Entry(location_frame, width=15, style='Custom.TEntry')
        self.member_entries['state'].grid(row=0, column=3, sticky='ew', padx=(0, 10))
        
        ttk.Label(location_frame, text="Postal Code:", style='Custom.TLabel').grid(row=0, column=4, sticky='w', padx=(0, 5))
        self.member_entries['postal_code'] = ttk.Entry(location_frame, width=10, style='Custom.TEntry')
        self.member_entries['postal_code'].grid(row=0, column=5, sticky='ew')
        
        location_frame.columnconfigure(1, weight=2)
        location_frame.columnconfigure(3, weight=2)
        location_frame.columnconfigure(5, weight=1)
    
    def create_emergency_contact_section(self, parent: ttk.Frame) -> None:
        """Create emergency contact section"""
        emergency_frame = ttk.LabelFrame(parent, text="🚨 Emergency Contact", padding=15)
        emergency_frame.pack(fill='x', pady=(0, 15))
        
        # Emergency Contact Name
        name_frame = ttk.Frame(emergency_frame)
        name_frame.pack(fill='x', pady=3)
        ttk.Label(name_frame, text="Contact Name:", style='Custom.TLabel').pack(side='left', padx=(0, 10))
        self.member_entries['emergency_contact_name'] = ttk.Entry(name_frame, style='Custom.TEntry')
        self.member_entries['emergency_contact_name'].pack(side='left', fill='x', expand=True)
        
        # Emergency Contact Phone and Relation
        contact_frame = ttk.Frame(emergency_frame)
        contact_frame.pack(fill='x', pady=3)
        
        ttk.Label(contact_frame, text="Phone:", style='Custom.TLabel').grid(row=0, column=0, sticky='w', padx=(0, 5))
        self.member_entries['emergency_contact_phone'] = ttk.Entry(contact_frame, width=15, style='Custom.TEntry')
        self.member_entries['emergency_contact_phone'].grid(row=0, column=1, sticky='ew', padx=(0, 20))
        
        ttk.Label(contact_frame, text="Relation:", style='Custom.TLabel').grid(row=0, column=2, sticky='w', padx=(0, 5))
        self.member_entries['emergency_contact_relation'] = ttk.Entry(contact_frame, width=15, style='Custom.TEntry')
        self.member_entries['emergency_contact_relation'].grid(row=0, column=3, sticky='ew')
        
        contact_frame.columnconfigure(1, weight=1)
        contact_frame.columnconfigure(3, weight=1)
    
    def create_additional_info_section(self, parent: ttk.Frame) -> None:
        """Create additional information section"""
        additional_frame = ttk.LabelFrame(parent, text="📋 Additional Information", padding=15)
        additional_frame.pack(fill='x', pady=(0, 15))
        
        # Member Type and Identification
        type_frame = ttk.Frame(additional_frame)
        type_frame.pack(fill='x', pady=3)
        
        ttk.Label(type_frame, text="Member Type:", style='Custom.TLabel').grid(row=0, column=0, sticky='w', padx=(0, 5))
        self.member_entries['member_type'] = ttk.Combobox(
            type_frame, 
            width=15, 
            values=self.controller.member_model.get_member_types(),
            state='readonly'
        )
        self.member_entries['member_type'].set('General')
        self.member_entries['member_type'].grid(row=0, column=1, sticky='ew', padx=(0, 20))
        
        ttk.Label(type_frame, text="ID Type:", style='Custom.TLabel').grid(row=0, column=2, sticky='w', padx=(0, 5))
        self.member_entries['identification_type'] = ttk.Combobox(
            type_frame,
            width=15,
            values=self.controller.member_model.get_identification_types(),
            state='readonly'
        )
        self.member_entries['identification_type'].grid(row=0, column=3, sticky='ew')
        
        type_frame.columnconfigure(1, weight=1)
        type_frame.columnconfigure(3, weight=1)
        
        # Identification Number
        id_frame = ttk.Frame(additional_frame)
        id_frame.pack(fill='x', pady=3)
        ttk.Label(id_frame, text="ID Number:", style='Custom.TLabel').pack(side='left', padx=(0, 10))
        self.member_entries['identification_number'] = ttk.Entry(id_frame, style='Custom.TEntry')
        self.member_entries['identification_number'].pack(side='left', fill='x', expand=True)
        
        # Occupation and Institution
        work_frame = ttk.Frame(additional_frame)
        work_frame.pack(fill='x', pady=3)
        
        ttk.Label(work_frame, text="Occupation:", style='Custom.TLabel').grid(row=0, column=0, sticky='w', padx=(0, 5))
        self.member_entries['occupation'] = ttk.Entry(work_frame, width=15, style='Custom.TEntry')
        self.member_entries['occupation'].grid(row=0, column=1, sticky='ew', padx=(0, 20))
        
        ttk.Label(work_frame, text="Institution:", style='Custom.TLabel').grid(row=0, column=2, sticky='w', padx=(0, 5))
        self.member_entries['institution_name'] = ttk.Entry(work_frame, width=15, style='Custom.TEntry')
        self.member_entries['institution_name'].grid(row=0, column=3, sticky='ew')
        
        work_frame.columnconfigure(1, weight=1)
        work_frame.columnconfigure(3, weight=1)
        
        # Notes
        notes_frame = ttk.Frame(additional_frame)
        notes_frame.pack(fill='x', pady=3)
        ttk.Label(notes_frame, text="Notes:", style='Custom.TLabel').pack(side='left', padx=(0, 10), anchor='n')
        self.member_entries['notes'] = tk.Text(notes_frame, height=3, width=40)
        self.member_entries['notes'].pack(side='left', fill='x', expand=True)
    
    def create_form_buttons(self, parent: ttk.Frame) -> None:
        """Create form action buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x', pady=20)
        
        ttk.Button(
            button_frame,
            text="💾 Add Member",
            command=self.save_member,
            style='Success.TButton'
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            button_frame,
            text="🔄 Clear Form",
            command=self.clear_form,
            style='Custom.TButton'
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            button_frame,
            text="❌ Cancel",
            command=self.root.destroy,
            style='Error.TButton'
        ).pack(side='right')
    
    def _clear_placeholder(self, event, placeholder_text: str) -> None:
        """Clear placeholder text on focus"""
        if event.widget.get() == placeholder_text:
            event.widget.delete(0, tk.END)
    
    def clear_form(self) -> None:
        """Clear all form fields"""
        for key, widget in self.member_entries.items():
            if isinstance(widget, tk.Text):
                widget.delete(1.0, tk.END)
            elif isinstance(widget, ttk.Combobox):
                widget.set('')
            else:
                widget.delete(0, tk.END)
        
        # Reset defaults
        if 'member_type' in self.member_entries:
            self.member_entries['member_type'].set('General')
        
        # Focus on first field
        if 'first_name' in self.member_entries:
            self.member_entries['first_name'].focus()
    
    def save_member(self) -> None:
        """Save new member"""
        try:
            # Collect form data
            member_data = {}
            
            for key, widget in self.member_entries.items():
                if isinstance(widget, tk.Text):
                    value = widget.get(1.0, tk.END).strip()
                else:
                    value = widget.get().strip()
                
                # Skip empty values and placeholders
                if value and not value.startswith("YYYY-MM-DD"):
                    member_data[key] = value
            
            # Add created_by
            member_data['created_by'] = self.controller.current_user['username']
            
            # Validate required fields
            required_fields = ['first_name', 'last_name', 'email', 'phone']
            missing_fields = [field for field in required_fields if not member_data.get(field)]
            
            if missing_fields:
                self.show_message(f"Please fill in required fields: {', '.join(missing_fields)}", 'error')
                return
            
            # Attempt to save
            if self.controller.member_model.add_member(member_data):
                self.show_message(
                    f"Member '{member_data['first_name']} {member_data['last_name']}' added successfully!",
                    'success'
                )
                
                if self.refresh_callback:
                    self.refresh_callback()
                
                self.root.destroy()
            else:
                self.show_message(
                    "Failed to add member. Please check if email already exists or verify all information.",
                    'error'
                )
                
        except Exception as e:
            logger.error(f"Error saving member: {e}")
            self.show_message(f"Error saving member: {str(e)}", 'error')


class EditMemberDialog(AddMemberDialog):
    """Dialog for editing existing members (inherits from AddMemberDialog)"""
    
    def __init__(self, parent, controller, member_id: int, refresh_callback: Callable = None):
        self.member_id = member_id
        self.member_data = None
        
        # Initialize parent but override title
        super().__init__(parent, controller, refresh_callback)
        self.root.title("Edit Member")
        
        # Load and populate existing data
        self.load_member_data()
    
    def load_member_data(self) -> None:
        """Load existing member data and populate form"""
        try:
            self.member_data = self.controller.member_model.get_member_by_id(self.member_id)
            
            if not self.member_data:
                self.show_message("Member not found", 'error')
                self.root.destroy()
                return
            
            # Populate form fields
            for key, widget in self.member_entries.items():
                value = self.member_data.get(key, '')
                
                if isinstance(widget, tk.Text):
                    widget.delete(1.0, tk.END)
                    if value:
                        widget.insert(1.0, str(value))
                elif isinstance(widget, (ttk.Combobox, ttk.Entry)):
                    widget.delete(0, tk.END)
                    if value:
                        widget.insert(0, str(value))
            
            # Update header
            header_name = self.member_data.get('full_name', f"Member {self.member_id}")
            # Find and update header label - this is a simplified approach
            
        except Exception as e:
            logger.error(f"Error loading member data: {e}")
            self.show_message(f"Error loading member data: {str(e)}", 'error')
    
    def save_member(self) -> None:
        """Update existing member"""
        try:
            # Collect form data
            member_data = {}
            
            for key, widget in self.member_entries.items():
                if isinstance(widget, tk.Text):
                    value = widget.get(1.0, tk.END).strip()
                else:
                    value = widget.get().strip()
                
                # Include all values (empty ones will be handled by the model)
                member_data[key] = value if value and not value.startswith("YYYY-MM-DD") else None
            
            # Validate required fields
            required_fields = ['first_name', 'last_name', 'email', 'phone']
            missing_fields = [field for field in required_fields if not member_data.get(field)]
            
            if missing_fields:
                self.show_message(f"Please fill in required fields: {', '.join(missing_fields)}", 'error')
                return
            
            # Attempt to update
            if self.controller.member_model.update_member(self.member_id, member_data):
                self.show_message(
                    f"Member '{member_data['first_name']} {member_data['last_name']}' updated successfully!",
                    'success'
                )
                
                if self.refresh_callback:
                    self.refresh_callback()
                
                self.root.destroy()
            else:
                self.show_message(
                    "Failed to update member. Please check if email already exists or verify all information.",
                    'error'
                )
                
        except Exception as e:
            logger.error(f"Error updating member: {e}")
            self.show_message(f"Error updating member: {str(e)}", 'error')


# Include the existing classes (MemberDetailDialog, QuickIssueDialog, QuickReturnDialog) from the previous implementation
# These classes remain the same as in the previous member management views
