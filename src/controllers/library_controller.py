"""
Main library controller that coordinates between models and views
"""

from typing import Optional, Dict, List, Any
from models.database import DatabaseManager
from models.user import User
from models.book import Book
from models.member import Member
from models.transaction import Transaction
from utils.logger import get_logger
from utils.helpers import ExportHelper
from config.settings import settings

logger = get_logger(__name__)


class LibraryController:
    """Main controller class that coordinates between models and views"""
    
    def __init__(self):
        """Initialize library controller"""
        # Initialize database and models
        self.db_manager = DatabaseManager()
        self.user_model = User(self.db_manager)
        self.book_model = Book(self.db_manager)
        self.member_model = Member(self.db_manager)
        self.transaction_model = Transaction(self.db_manager)
        
        # Current session state
        self.current_user: Optional[Dict] = None
        
        # Initialize system
        self.setup_system()
        
        logger.info("Library controller initialized")
    
    def setup_system(self) -> None:
        """Setup system with default users if needed"""
        try:
            # Check if any users exist
            user_count = self.user_model.get_user_count()
            
            if user_count == 0:
                # Create default users
                self.user_model.create_user(
                    settings.DEFAULT_ADMIN_USERNAME,
                    settings.DEFAULT_ADMIN_PASSWORD,
                    "admin"
                )
                self.user_model.create_user(
                    settings.DEFAULT_LIBRARIAN_USERNAME,
                    settings.DEFAULT_LIBRARIAN_PASSWORD,
                    "librarian"
                )
                logger.info("Default users created")
            
        except Exception as e:
            logger.error(f"System setup error: {e}")
    
    # ==================== Authentication ====================
    
    def login(self, username: str, password: str) -> bool:
        """Authenticate user login"""
        try:
            user = self.user_model.authenticate(username, password)
            if user:
                self.current_user = user
                logger.info(f"User {username} logged in successfully")
                return True
            
            logger.warning(f"Login failed for user {username}")
            return False
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False
    
    def logout(self) -> None:
        """Logout current user"""
        if self.current_user:
            username = self.current_user['username']
            self.current_user = None
            logger.info(f"User {username} logged out")
    
    def is_admin(self) -> bool:
        """Check if current user is admin"""
        return self.current_user and self.current_user['role'] == 'admin'
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.current_user is not None
    
    def get_current_user(self) -> Optional[Dict]:
        """Get current user information"""
        return self.current_user
    
    # ==================== Dashboard Statistics ====================
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get statistics for dashboard"""
        try:
            # Book statistics
            book_stats = self.book_model.get_book_statistics()
            
            # Member statistics
            member_stats = self.member_model.get_member_statistics()
            
            # Transaction statistics
            transaction_stats = self.transaction_model.get_transaction_statistics()
            
            # Combine all statistics
            dashboard_stats = {
                'books': book_stats,
                'members': member_stats,
                'transactions': transaction_stats,
                'system_info': {
                    'current_user': self.current_user,
                    'database_path': self.db_manager.db_path
                }
            }
            
            return dashboard_stats
            
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {e}")
            return {}
    
    # ==================== User Management ====================
    
    def create_user(self, username: str, password: str, role: str) -> bool:
        """Create new user (admin only)"""
        if not self.is_admin():
            logger.warning("Unauthorized user creation attempt")
            return False
        
        return self.user_model.create_user(username, password, role)
    
    def get_all_users(self) -> List[Dict]:
        """Get all users (admin only)"""
        if not self.is_admin():
            return []
        
        return self.user_model.get_all_users()
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user (admin only)"""
        if not self.is_admin():
            return False
        
        # Prevent deletion of current user
        if self.current_user and self.current_user['id'] == user_id:
            logger.warning("Cannot delete current user")
            return False
        
        return self.user_model.delete_user(user_id)
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """Change user password"""
        return self.user_model.change_password(user_id, old_password, new_password)
    
    # ==================== Book Management ====================
    
    def add_book(self, title: str, author: str, category: str, isbn: str) -> bool:
        """Add new book (admin only)"""
        if not self.is_admin():
            return False
        
        return self.book_model.add_book(title, author, category, isbn)
    
    def get_all_books(self) -> List[Dict]:
        """Get all books"""
        return self.book_model.get_all_books()
    
    def search_books(self, search_term: str) -> List[Dict]:
        """Search books"""
        return self.book_model.search_books(search_term)
    
    def get_available_books(self) -> List[Dict]:
        """Get available books"""
        return self.book_model.get_available_books()
    
    def update_book(self, book_id: int, **kwargs) -> bool:
        """Update book (admin only)"""
        if not self.is_admin():
            return False
        
        return self.book_model.update_book(book_id, **kwargs)
    
    def delete_book(self, book_id: int) -> bool:
        """Delete book (admin only)"""
        if not self.is_admin():
            return False
        
        return self.book_model.delete_book(book_id)
    
    def get_book_by_id(self, book_id: int) -> Optional[Dict]:
        """Get book by ID"""
        return self.book_model.get_book_by_id(book_id)
    
    def get_all_categories(self) -> List[str]:
        """Get all book categories"""
        return self.book_model.get_all_categories()
    
    # ==================== Member Management ====================
    
    def add_member(self, name: str, email: str, phone: str) -> bool:
        """Add new member (admin only)"""
        if not self.is_admin():
            return False
        
        return self.member_model.add_member(name, email, phone)
    
    def get_all_members(self) -> List[Dict]:
        """Get all members"""
        return self.member_model.get_all_members()
    
    def search_members(self, search_term: str) -> List[Dict]:
        """Search members"""
        return self.member_model.search_members(search_term)
    
    def update_member(self, member_id: int, **kwargs) -> bool:
        """Update member (admin only)"""
        if not self.is_admin():
            return False
        
        return self.member_model.update_member(member_id, **kwargs)
    
    def delete_member(self, member_id: int) -> bool:
        """Delete member (admin only)"""
        if not self.is_admin():
            return False
        
        return self.member_model.delete_member(member_id)
    
    def get_member_by_id(self, member_id: int) -> Optional[Dict]:
        """Get member by ID"""
        return self.member_model.get_member_by_id(member_id)
    
    def get_member_by_email(self, email: str) -> Optional[Dict]:
        """Get member by email"""
        return self.member_model.get_member_by_email(email)
    
    # ==================== Transaction Management ====================
    
    def issue_book(self, book_id: int, member_id: int) -> bool:
        """Issue book to member"""
        return self.transaction_model.issue_book(book_id, member_id)
    
    def return_book(self, book_id: int, member_id: int) -> tuple:
        """Return book and get late fee"""
        return self.transaction_model.return_book(book_id, member_id)
    
    def get_issued_books(self) -> List[Dict]:
        """Get currently issued books"""
        return self.transaction_model.get_issued_books()
    
    def get_overdue_books(self) -> List[Dict]:
        """Get overdue books"""
        return self.transaction_model.get_overdue_books()
    
    def get_transaction_history(self, limit: int = None) -> List[Dict]:
        """Get transaction history"""
        return self.transaction_model.get_transaction_history(limit)
    
    def get_member_transactions(self, member_id: int) -> List[Dict]:
        """Get transactions for specific member"""
        return self.transaction_model.get_member_transactions(member_id)
    
    def get_book_transactions(self, book_id: int) -> List[Dict]:
        """Get transactions for specific book"""
        return self.transaction_model.get_book_transactions(book_id)
    
    def renew_book(self, transaction_id: int, days: int = None) -> bool:
        """Renew book"""
        return self.transaction_model.renew_book(transaction_id, days)
    
    # ==================== Reporting ====================
    
    def export_report(self, report_type: str, data: List[Dict]) -> str:
        """Export report to CSV"""
        try:
            if report_type == 'books':
                prepared_data = ExportHelper.prepare_books_export(data)
            elif report_type == 'members':
                prepared_data = ExportHelper.prepare_members_export(data)
            elif report_type in ['transactions', 'issued', 'overdue']:
                prepared_data = ExportHelper.prepare_transactions_export(data)
            else:
                prepared_data = data
            
            filename = ExportHelper.export_to_csv(prepared_data, report_type)
            logger.info(f"Report exported: {filename}")
            return f"Report exported successfully to: {filename}"
            
        except Exception as e:
            logger.error(f"Export error: {e}")
            return f"Export failed: {str(e)}"
    
    def get_comprehensive_report(self) -> Dict[str, Any]:
        """Get comprehensive library report"""
        try:
            report = {
                'generated_at': str(__import__('datetime').datetime.now()),
                'generated_by': self.current_user['username'] if self.current_user else 'Unknown',
                'statistics': self.get_dashboard_stats(),
                'books': {
                    'total': self.book_model.get_all_books(),
                    'available': self.book_model.get_available_books(),
                    'categories': self.book_model.get_all_categories()
                },
                'members': {
                    'all': self.member_model.get_all_members(),
                    'statistics': self.member_model.get_member_statistics()
                },
                'transactions': {
                    'issued': self.transaction_model.get_issued_books(),
                    'overdue': self.transaction_model.get_overdue_books(),
                    'recent': self.transaction_model.get_transaction_history(50)
                }
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Comprehensive report error: {e}")
            return {}
    
    # ==================== System Utilities ====================
    
    def backup_database(self, backup_path: str = None) -> bool:
        """Backup database"""
        if not backup_path:
            import os
            timestamp = __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"data/backup_library_{timestamp}.db"
            os.makedirs("data", exist_ok=True)
        
        return self.db_manager.backup_database(backup_path)
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        return {
            'app_name': settings.APP_NAME,
            'app_version': settings.APP_VERSION,
            'database_info': self.db_manager.get_database_info(),
            'current_user': self.current_user,
            'settings': {
                'borrowing_period': settings.BORROWING_PERIOD_DAYS,
                'late_fee': settings.DAILY_LATE_FEE
            }
        }
    
    def validate_system(self) -> Dict[str, bool]:
        """Validate system integrity"""
        try:
            validation_results = {
                'database_connection': False,
                'users_table': False,
                'books_table': False,
                'members_table': False,
                'transactions_table': False,
                'admin_user_exists': False
            }
            
            # Test database connection
            with self.db_manager.get_connection() as conn:
                validation_results['database_connection'] = True
                
                # Test tables
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                for table in ['users', 'books', 'members', 'transactions']:
                    validation_results[f'{table}_table'] = table in tables
                
                # Check for admin user
                cursor = conn.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
                admin_count = cursor.fetchone()[0]
                validation_results['admin_user_exists'] = admin_count > 0
            
            return validation_results
            
        except Exception as e:
            logger.error(f"System validation error: {e}")
            return {'error': str(e)}
