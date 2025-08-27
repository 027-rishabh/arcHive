"""
Fixed Database Manager with proper error handling and debugging
"""

import sqlite3
import os
import bcrypt
from typing import Optional
from utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)


class DatabaseManager:
    """Enhanced Database manager with comprehensive error handling and debugging"""
    
    def __init__(self):
        """Initialize database manager with proper setup"""
        self.db_path = self._get_database_path()
        self.connection = None
        
        # Ensure database directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Initialize database
        self._initialize_database()
        logger.info(f"Database manager initialized: {self.db_path}")
    
    def _get_database_path(self) -> str:
        """Get database file path"""
        db_dir = getattr(settings, 'DATABASE_DIR', 'data')
        db_name = getattr(settings, 'DATABASE_NAME', 'library_management.db')
        return os.path.join(db_dir, db_name)
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with proper configuration"""
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
            conn.execute("PRAGMA journal_mode = WAL")  # Better concurrency
            return conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    def _initialize_database(self) -> None:
        """Initialize database with all required tables"""
        try:
            with self.get_connection() as conn:
                # Users table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        role TEXT NOT NULL CHECK(role IN ('admin', 'librarian')),
                        first_name TEXT,
                        last_name TEXT,
                        email TEXT,
                        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT 1
                    )
                """)
                
                # Books table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS books (
                        book_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        author TEXT NOT NULL,
                        category TEXT NOT NULL,
                        isbn TEXT UNIQUE NOT NULL,
                        availability_status TEXT DEFAULT 'available' 
                            CHECK(availability_status IN ('available', 'issued', 'maintenance')),
                        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Enhanced Members table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS members (
                        member_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        first_name TEXT NOT NULL,
                        last_name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        phone TEXT NOT NULL,
                        date_of_birth DATE,
                        gender TEXT CHECK(gender IN ('Male', 'Female', 'Other', 'Prefer not to say')),
                        address_line1 TEXT,
                        address_line2 TEXT,
                        city TEXT,
                        state TEXT,
                        postal_code TEXT,
                        country TEXT DEFAULT 'India',
                        emergency_contact_name TEXT,
                        emergency_contact_phone TEXT,
                        emergency_contact_relation TEXT,
                        identification_type TEXT CHECK(identification_type IN ('Aadhar', 'PAN', 'Driving License', 'Passport', 'Student ID', 'Employee ID', 'Other')),
                        identification_number TEXT,
                        member_type TEXT DEFAULT 'General' CHECK(member_type IN ('Student', 'Faculty', 'Staff', 'Senior Citizen', 'General', 'Premium')),
                        occupation TEXT,
                        institution_name TEXT,
                        department TEXT,
                        join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        membership_expiry DATE,
                        is_active BOOLEAN DEFAULT 1,
                        notes TEXT,
                        created_by TEXT,
                        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Member limits table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS member_limits (
                        member_id INTEGER PRIMARY KEY,
                        max_books INTEGER DEFAULT 3,
                        current_issues INTEGER DEFAULT 0,
                        total_issued INTEGER DEFAULT 0,
                        total_returned INTEGER DEFAULT 0,
                        late_returns INTEGER DEFAULT 0,
                        member_status TEXT DEFAULT 'active' 
                            CHECK(member_status IN ('active', 'suspended', 'blocked', 'expired')),
                        fine_balance DECIMAL(10,2) DEFAULT 0.00,
                        last_visit_date TIMESTAMP,
                        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (member_id) REFERENCES members (member_id) ON DELETE CASCADE
                    )
                """)
                
                # Transactions table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS transactions (
                        transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        book_id INTEGER NOT NULL,
                        member_id INTEGER NOT NULL,
                        issue_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        return_date TIMESTAMP NULL,
                        status TEXT DEFAULT 'issued' CHECK(status IN ('issued', 'returned', 'renewed')),
                        late_fee DECIMAL(10,2) DEFAULT 0.00,
                        notes TEXT,
                        FOREIGN KEY (book_id) REFERENCES books (book_id),
                        FOREIGN KEY (member_id) REFERENCES members (member_id)
                    )
                """)
                
                # Create indexes
                indexes = [
                    "CREATE INDEX IF NOT EXISTS idx_books_isbn ON books (isbn)",
                    "CREATE INDEX IF NOT EXISTS idx_books_title ON books (title)",
                    "CREATE INDEX IF NOT EXISTS idx_members_email ON members (email)",
                    "CREATE INDEX IF NOT EXISTS idx_members_phone ON members (phone)",
                    "CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions (status)",
                    "CREATE INDEX IF NOT EXISTS idx_transactions_dates ON transactions (issue_date, return_date)"
                ]
                
                for index_sql in indexes:
                    conn.execute(index_sql)
                
                # Create default admin user if not exists
                self._create_default_users(conn)
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
    def _create_default_users(self, conn: sqlite3.Connection) -> None:
        """Create default admin and librarian users"""
        try:
            # Check if admin exists
            cursor = conn.execute("SELECT COUNT(*) FROM users WHERE username = ?", ('admin',))
            if cursor.fetchone()[0] == 0:
                # Create default admin
                admin_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
                conn.execute(
                    """INSERT INTO users (username, password_hash, role, first_name, last_name) 
                       VALUES (?, ?, ?, ?, ?)""",
                    ('admin', admin_password.decode('utf-8'), 'admin', 'System', 'Administrator')
                )
                logger.info("Default admin user created")
            
            # Check if librarian exists
            cursor = conn.execute("SELECT COUNT(*) FROM users WHERE username = ?", ('librarian',))
            if cursor.fetchone()[0] == 0:
                # Create default librarian
                lib_password = bcrypt.hashpw('lib123'.encode('utf-8'), bcrypt.gensalt())
                conn.execute(
                    """INSERT INTO users (username, password_hash, role, first_name, last_name) 
                       VALUES (?, ?, ?, ?, ?)""",
                    ('librarian', lib_password.decode('utf-8'), 'librarian', 'Default', 'Librarian')
                )
                logger.info("Default librarian user created")
                
        except sqlite3.Error as e:
            logger.error(f"Error creating default users: {e}")
    
    def reset_database(self) -> bool:
        """Reset database - DROP ALL TABLES and recreate (USE WITH CAUTION)"""
        try:
            with self.get_connection() as conn:
                # Get all table names
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                
                # Drop all tables
                for table in tables:
                    if table[0] != 'sqlite_sequence':  # Don't drop system table
                        conn.execute(f"DROP TABLE IF EXISTS {table[0]}")
                
                conn.commit()
                logger.info("All tables dropped")
                
                # Reinitialize
                self._initialize_database()
                logger.info("Database reset successfully")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Database reset error: {e}")
            return False
    
    def check_database_integrity(self) -> dict:
        """Check database integrity and return status"""
        try:
            with self.get_connection() as conn:
                # Check if all tables exist
                cursor = conn.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name IN ('users', 'books', 'members', 'member_limits', 'transactions')
                """)
                existing_tables = [row[0] for row in cursor.fetchall()]
                
                # Check record counts
                counts = {}
                for table in existing_tables:
                    cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                    counts[table] = cursor.fetchone()[0]
                
                return {
                    'status': 'healthy',
                    'existing_tables': existing_tables,
                    'record_counts': counts,
                    'database_path': self.db_path
                }
                
        except sqlite3.Error as e:
            logger.error(f"Database integrity check error: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'database_path': self.db_path
            }
    
    def backup_database(self, backup_path: str = None) -> bool:
        """Create database backup"""
        try:
            if not backup_path:
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"{self.db_path}.backup_{timestamp}"
            
            # Simple file copy for SQLite
            import shutil
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Database backed up to: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Database backup error: {e}")
            return False
    
    def close(self) -> None:
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Database connection closed")
