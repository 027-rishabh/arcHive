"""
Fixed User Model with missing methods that controller expects
"""

import sqlite3
import bcrypt
from typing import Dict, List, Optional
from models.database import DatabaseManager
from utils.helpers import ValidationError, DataHelper
from utils.logger import get_logger

logger = get_logger(__name__)


class User:
    """Fixed User model class with all required methods"""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize user model"""
        self.db_manager = db_manager
        logger.info("User model initialized")
    
    def authenticate(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user data if successful"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute(
                    """SELECT id, username, password_hash, role, first_name, last_name, email, is_active
                       FROM users WHERE username = ? AND is_active = 1""",
                    (username.strip(),)
                )
                user_row = cursor.fetchone()
                
                if not user_row:
                    logger.warning(f"User '{username}' not found or inactive")
                    return None
                
                # Verify password
                stored_hash = user_row[2]
                if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                    user_data = {
                        'id': user_row[0],
                        'username': user_row[1],
                        'role': user_row[3],
                        'first_name': user_row[4] or '',
                        'last_name': user_row[5] or '',
                        'email': user_row[6] or '',
                        'full_name': f"{user_row[4] or ''} {user_row[5] or ''}".strip(),
                        'is_active': user_row[7]
                    }
                    logger.info(f"User '{username}' authenticated successfully (Role: {user_data['role']})")
                    return user_data
                else:
                    logger.warning(f"Invalid password for user '{username}'")
                    return None
                    
        except sqlite3.Error as e:
            logger.error(f"Database error during authentication: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {e}")
            return None
    
    def add_user(self, username: str, password: str, role: str, first_name: str = None, 
                 last_name: str = None, email: str = None) -> bool:
        """Add new user (librarian) - Admin only function"""
        try:
            # Validate inputs
            self._validate_user_data(username, password, role, email)
            
            # Hash password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            with self.db_manager.get_connection() as conn:
                # Check if username already exists
                cursor = conn.execute(
                    "SELECT id FROM users WHERE username = ?", 
                    (username.strip(),)
                )
                if cursor.fetchone():
                    logger.warning(f"Username '{username}' already exists")
                    return False
                
                # Check if email already exists (if provided)
                if email and email.strip():
                    cursor = conn.execute(
                        "SELECT id FROM users WHERE email = ? AND email != ''", 
                        (email.strip(),)
                    )
                    if cursor.fetchone():
                        logger.warning(f"Email '{email}' already exists")
                        return False
                
                # Insert new user
                cursor = conn.execute(
                    """INSERT INTO users (username, password_hash, role, first_name, last_name, email, is_active)
                       VALUES (?, ?, ?, ?, ?, ?, 1)""",
                    (username.strip(), password_hash.decode('utf-8'), role, 
                     first_name.strip() if first_name else None,
                     last_name.strip() if last_name else None,
                     email.strip() if email else None)
                )
                
                user_id = cursor.lastrowid
                conn.commit()
                
                logger.info(f"User '{username}' added successfully (ID: {user_id}, Role: {role})")
                return True
                
        except ValidationError as e:
            logger.warning(f"User validation failed: {e}")
            return False
        except sqlite3.IntegrityError as e:
            logger.warning(f"User creation failed - constraint violation: {e}")
            return False
        except sqlite3.Error as e:
            logger.error(f"Database error adding user: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error adding user: {e}")
            return False
    
    def get_all_users(self) -> List[Dict]:
        """Get all system users"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute(
                    """SELECT id, username, role, first_name, last_name, email, created_date, is_active
                       FROM users ORDER BY role, username"""
                )
                
                users = []
                for row in cursor.fetchall():
                    user_dict = {
                        'id': row[0],
                        'username': row[1],
                        'role': row[2],
                        'first_name': row[3] or '',
                        'last_name': row[4] or '',
                        'full_name': f"{row[3] or ''} {row[4] or ''}".strip(),
                        'email': row[5] or '',
                        'created_date': row[6],
                        'is_active': row[7]
                    }
                    users.append(user_dict)
                
                logger.info(f"Retrieved {len(users)} users")
                return users
                
        except sqlite3.Error as e:
            logger.error(f"Error fetching users: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching users: {e}")
            return []
    
    def get_user_count(self) -> int:
        """Get total number of active users (method that controller expects)"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
                count = cursor.fetchone()[0]
                logger.info(f"Total active users: {count}")
                return count
                
        except sqlite3.Error as e:
            logger.error(f"Error getting user count: {e}")
            return 0
        except Exception as e:
            logger.error(f"Unexpected error getting user count: {e}")
            return 0
    
    def get_librarians_only(self) -> List[Dict]:
        """Get only librarian users (for admin management)"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute(
                    """SELECT id, username, role, first_name, last_name, email, created_date, is_active
                       FROM users WHERE role = 'librarian' ORDER BY username"""
                )
                
                librarians = []
                for row in cursor.fetchall():
                    librarian_dict = {
                        'id': row[0],
                        'username': row[1],
                        'role': row[2],
                        'first_name': row[3] or '',
                        'last_name': row[4] or '',
                        'full_name': f"{row[3] or ''} {row[4] or ''}".strip(),
                        'email': row[5] or '',
                        'created_date': row[6],
                        'is_active': row[7]
                    }
                    librarians.append(librarian_dict)
                
                logger.info(f"Retrieved {len(librarians)} librarians")
                return librarians
                
        except sqlite3.Error as e:
            logger.error(f"Error fetching librarians: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching librarians: {e}")
            return []
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute(
                    """SELECT id, username, role, first_name, last_name, email, created_date, is_active
                       FROM users WHERE id = ?""",
                    (user_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    return {
                        'id': row[0],
                        'username': row[1],
                        'role': row[2],
                        'first_name': row[3] or '',
                        'last_name': row[4] or '',
                        'full_name': f"{row[3] or ''} {row[4] or ''}".strip(),
                        'email': row[5] or '',
                        'created_date': row[6],
                        'is_active': row[7]
                    }
                return None
                
        except sqlite3.Error as e:
            logger.error(f"Error fetching user {user_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching user {user_id}: {e}")
            return None
    
    def update_user(self, user_id: int, user_data: Dict) -> bool:
        """Update user information (excluding password and username)"""
        try:
            updates = []
            params = []
            
            updateable_fields = ['first_name', 'last_name', 'email']
            
            for field in updateable_fields:
                if field in user_data:
                    value = user_data[field]
                    if value is not None:
                        value = value.strip() if isinstance(value, str) else value
                    updates.append(f"{field} = ?")
                    params.append(value)
            
            if not updates:
                logger.warning("No valid updates provided for user update")
                return False
            
            params.append(user_id)
            
            with self.db_manager.get_connection() as conn:
                # Check if user exists and is not the main admin
                cursor = conn.execute(
                    "SELECT username, role FROM users WHERE id = ?", 
                    (user_id,)
                )
                user_info = cursor.fetchone()
                
                if not user_info:
                    logger.warning(f"User ID {user_id} not found for update")
                    return False
                
                # Don't allow updating the main admin user
                if user_info[0] == 'admin' and user_info[1] == 'admin':
                    logger.warning("Cannot update the main admin user")
                    return False
                
                # Check email uniqueness if updating email
                if 'email' in user_data and user_data['email']:
                    cursor = conn.execute(
                        "SELECT id FROM users WHERE email = ? AND id != ? AND email != ''",
                        (user_data['email'].strip(), user_id)
                    )
                    if cursor.fetchone():
                        logger.warning(f"Email {user_data['email']} already exists for another user")
                        return False
                
                # Perform update
                cursor = conn.execute(
                    f"UPDATE users SET {', '.join(updates)} WHERE id = ?",
                    tuple(params)
                )
                
                if cursor.rowcount > 0:
                    conn.commit()
                    logger.info(f"User ID {user_id} updated successfully")
                    return True
                else:
                    logger.warning(f"No rows affected when updating user ID {user_id}")
                    return False
                
        except sqlite3.IntegrityError as e:
            logger.warning(f"User update failed - constraint violation: {e}")
            return False
        except sqlite3.Error as e:
            logger.error(f"Database error updating user {user_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error updating user {user_id}: {e}")
            return False
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user (soft delete by marking as inactive) - Cannot delete main admin"""
        try:
            with self.db_manager.get_connection() as conn:
                # Check if user exists and get user info
                cursor = conn.execute(
                    "SELECT username, role FROM users WHERE id = ?", 
                    (user_id,)
                )
                user_info = cursor.fetchone()
                
                if not user_info:
                    logger.warning(f"User ID {user_id} not found for deletion")
                    return False
                
                # Don't allow deleting the main admin user
                if user_info[0] == 'admin' and user_info[1] == 'admin':
                    logger.warning("Cannot delete the main admin user")
                    return False
                
                # Soft delete - mark as inactive
                cursor = conn.execute(
                    "UPDATE users SET is_active = 0 WHERE id = ?", 
                    (user_id,)
                )
                
                if cursor.rowcount > 0:
                    conn.commit()
                    logger.info(f"User ID {user_id} ({user_info[0]}) deactivated successfully")
                    return True
                else:
                    logger.warning(f"No rows affected when deleting user ID {user_id}")
                    return False
                
        except sqlite3.Error as e:
            logger.error(f"Database error deleting user {user_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting user {user_id}: {e}")
            return False
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """Change user password (user must provide old password)"""
        try:
            # Validate new password
            if not new_password or len(new_password.strip()) < 6:
                logger.warning("New password must be at least 6 characters")
                return False
            
            with self.db_manager.get_connection() as conn:
                # Get current password hash
                cursor = conn.execute(
                    "SELECT password_hash, username FROM users WHERE id = ? AND is_active = 1",
                    (user_id,)
                )
                user_data = cursor.fetchone()
                
                if not user_data:
                    logger.warning(f"User ID {user_id} not found or inactive")
                    return False
                
                # Verify old password
                stored_hash = user_data[0]
                if not bcrypt.checkpw(old_password.encode('utf-8'), stored_hash.encode('utf-8')):
                    logger.warning(f"Incorrect old password for user {user_data[1]}")
                    return False
                
                # Hash new password
                new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                
                # Update password
                cursor = conn.execute(
                    "UPDATE users SET password_hash = ? WHERE id = ?",
                    (new_hash.decode('utf-8'), user_id)
                )
                
                if cursor.rowcount > 0:
                    conn.commit()
                    logger.info(f"Password changed successfully for user {user_data[1]}")
                    return True
                return False
                
        except sqlite3.Error as e:
            logger.error(f"Database error changing password: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error changing password: {e}")
            return False
    
    def reset_password(self, user_id: int, new_password: str) -> bool:
        """Reset user password (Admin function - no old password required)"""
        try:
            # Validate new password
            if not new_password or len(new_password.strip()) < 6:
                logger.warning("New password must be at least 6 characters")
                return False
            
            with self.db_manager.get_connection() as conn:
                # Check if user exists
                cursor = conn.execute(
                    "SELECT username FROM users WHERE id = ? AND is_active = 1",
                    (user_id,)
                )
                user_data = cursor.fetchone()
                
                if not user_data:
                    logger.warning(f"User ID {user_id} not found or inactive")
                    return False
                
                # Hash new password
                new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                
                # Update password
                cursor = conn.execute(
                    "UPDATE users SET password_hash = ? WHERE id = ?",
                    (new_hash.decode('utf-8'), user_id)
                )
                
                if cursor.rowcount > 0:
                    conn.commit()
                    logger.info(f"Password reset successfully for user {user_data[0]} (Admin action)")
                    return True
                return False
                
        except sqlite3.Error as e:
            logger.error(f"Database error resetting password: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error resetting password: {e}")
            return False
    
    def get_user_statistics(self) -> Dict:
        """Get user statistics"""
        try:
            with self.db_manager.get_connection() as conn:
                stats = {}
                
                # Total active users
                cursor = conn.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
                stats['total_users'] = cursor.fetchone()[0]
                
                # Users by role
                cursor = conn.execute(
                    "SELECT role, COUNT(*) FROM users WHERE is_active = 1 GROUP BY role"
                )
                stats['users_by_role'] = dict(cursor.fetchall())
                
                # Recent users (last 30 days)
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM users WHERE created_date >= datetime('now', '-30 days') AND is_active = 1"
                )
                stats['recent_users'] = cursor.fetchone()[0]
                
                # Inactive users
                cursor = conn.execute("SELECT COUNT(*) FROM users WHERE is_active = 0")
                stats['inactive_users'] = cursor.fetchone()[0]
                
                logger.info("User statistics retrieved successfully")
                return stats
                
        except sqlite3.Error as e:
            logger.error(f"Error getting user statistics: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error getting user statistics: {e}")
            return {}
    
    # Additional compatibility methods that controller might expect
    def get_admin_count(self) -> int:
        """Get number of admin users"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM users WHERE role = 'admin' AND is_active = 1")
                return cursor.fetchone()[0]
        except:
            return 0
    
    def get_librarian_count(self) -> int:
        """Get number of librarian users"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM users WHERE role = 'librarian' AND is_active = 1")
                return cursor.fetchone()[0]
        except:
            return 0
    
    def _validate_user_data(self, username: str, password: str, role: str, email: str = None) -> None:
        """Validate user data"""
        errors = []
        
        # Validate username
        if not username or not username.strip():
            errors.append("Username is required")
        elif len(username.strip()) < 3:
            errors.append("Username must be at least 3 characters")
        elif not username.replace('_', '').replace('-', '').isalnum():
            errors.append("Username can only contain letters, numbers, hyphens, and underscores")
        
        # Validate password
        if not password or len(password) < 6:
            errors.append("Password must be at least 6 characters")
        
        # Validate role
        if role not in ['admin', 'librarian']:
            errors.append("Role must be 'admin' or 'librarian'")
        
        # Validate email if provided
        if email and email.strip():
            if not DataHelper.validate_email(email.strip()):
                errors.append("Invalid email format")
        
        if errors:
            raise ValidationError("; ".join(errors))
