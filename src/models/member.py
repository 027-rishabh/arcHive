"""
Enhanced Member Model with Custom ID Support
"""

import sqlite3
from typing import Dict, List, Optional
from models.database import DatabaseManager
from utils.helpers import ValidationError, DataHelper, StringHelper
from utils.logger import get_logger
from config.settings import settings
import datetime

logger = get_logger(__name__)


class Member:
    """Enhanced Member model with custom ID support"""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize enhanced member model with custom ID support"""
        self.db_manager = db_manager
        self._ensure_enhanced_member_tables()
        logger.info("Enhanced Member model with custom ID support initialized")
    
    def _ensure_enhanced_member_tables(self):
        """Create enhanced member tables with comprehensive information"""
        try:
            with self.db_manager.get_connection() as conn:
                # Check if member_limits table exists, if not create it
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM sqlite_master 
                    WHERE type='table' AND name='member_limits'
                """)
                
                if cursor.fetchone()[0] == 0:
                    # Create member limits table
                    conn.execute("""
                        CREATE TABLE member_limits (
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
                    logger.info("Member limits table created")
                
                # Create indexes
                indexes = [
                    "CREATE INDEX IF NOT EXISTS idx_members_email ON members (email)",
                    "CREATE INDEX IF NOT EXISTS idx_members_phone ON members (phone)",
                    "CREATE INDEX IF NOT EXISTS idx_members_type ON members (member_type)",
                    "CREATE INDEX IF NOT EXISTS idx_members_active ON members (is_active)",
                    "CREATE INDEX IF NOT EXISTS idx_member_limits_status ON member_limits (member_status)",
                ]
                
                for index_sql in indexes:
                    conn.execute(index_sql)
                
                conn.commit()
                logger.info("Member tables and indexes ensured")
                
        except sqlite3.Error as e:
            logger.error(f"Error ensuring member tables: {e}")
    
    def add_member(self, member_data: Dict, member_id: int = None) -> bool:
        """Add new member with optional custom ID and comprehensive information"""
        try:
            # Validate required fields
            self._validate_member_data(member_data, member_id)
            
            with self.db_manager.get_connection() as conn:
                # Check if email already exists
                cursor = conn.execute(
                    "SELECT member_id FROM members WHERE email = ? AND is_active = 1", 
                    (member_data['email'].strip(),)
                )
                existing_member = cursor.fetchone()
                
                if existing_member:
                    logger.warning(f"Member with email {member_data['email']} already exists (ID: {existing_member[0]})")
                    return False
                
                # Check if custom member_id already exists
                if member_id is not None:
                    cursor = conn.execute("SELECT member_id FROM members WHERE member_id = ?", (member_id,))
                    existing_id = cursor.fetchone()
                    
                    if existing_id:
                        logger.warning(f"Member ID {member_id} already exists")
                        return False
                
                # Prepare member data for insertion
                fields = [
                    'first_name', 'last_name', 'email', 'phone', 'date_of_birth', 'gender',
                    'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country',
                    'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relation',
                    'identification_type', 'identification_number', 'member_type',
                    'occupation', 'institution_name', 'department', 'membership_expiry',
                    'notes', 'created_by'
                ]
                
                # Build dynamic insert query
                field_values = []
                placeholders = []
                insert_fields = []
                
                # Add member_id if provided
                if member_id is not None:
                    insert_fields.append('member_id')
                    field_values.append(member_id)
                    placeholders.append('?')
                
                for field in fields:
                    value = member_data.get(field, '').strip() if member_data.get(field) else None
                    if value:  # Only include non-empty values
                        insert_fields.append(field)
                        field_values.append(value)
                        placeholders.append('?')
                
                if not insert_fields or len([f for f in insert_fields if f in ['first_name', 'last_name', 'email', 'phone']]) < 4:
                    logger.error("Missing required fields for member")
                    return False
                
                # Insert member
                query = f"INSERT INTO members ({', '.join(insert_fields)}) VALUES ({', '.join(placeholders)})"
                cursor = conn.execute(query, field_values)
                actual_member_id = member_id if member_id is not None else cursor.lastrowid
                
                # Set default book limits based on member type
                max_books = self._get_default_book_limit(member_data.get('member_type', 'General'))
                
                # Add member limits
                conn.execute(
                    """INSERT INTO member_limits (member_id, max_books) VALUES (?, ?)""",
                    (actual_member_id, max_books)
                )
                
                conn.commit()
                logger.info(f"Member '{member_data.get('first_name', '')} {member_data.get('last_name', '')}' added successfully (ID: {actual_member_id})")
                return True
                
        except ValidationError as e:
            logger.warning(f"Member validation failed: {e}")
            return False
        except sqlite3.IntegrityError as e:
            logger.warning(f"Member with email {member_data.get('email', '')} or ID {member_id} already exists: {e}")
            return False
        except sqlite3.Error as e:
            logger.error(f"Database error adding member: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error adding member: {e}")
            return False
    
    def get_next_available_id(self) -> int:
        """Get the next available member ID"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute("SELECT COALESCE(MAX(member_id), 0) + 1 FROM members")
                next_id = cursor.fetchone()[0]
                logger.info(f"Next available member ID: {next_id}")
                return next_id
                
        except sqlite3.Error as e:
            logger.error(f"Error getting next member ID: {e}")
            return 1
        except Exception as e:
            logger.error(f"Unexpected error getting next member ID: {e}")
            return 1
    
    def is_id_available(self, member_id: int) -> bool:
        """Check if a member ID is available"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM members WHERE member_id = ?", (member_id,))
                count = cursor.fetchone()[0]
                return count == 0
                
        except sqlite3.Error as e:
            logger.error(f"Error checking member ID availability: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking member ID availability: {e}")
            return False
    
    def get_member_by_id(self, member_id: int) -> Optional[Dict]:
        """Get comprehensive member information by ID"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute(
                    """SELECT m.*, 
                              COALESCE(ml.max_books, 3) as max_books,
                              COALESCE(ml.current_issues, 0) as current_issues,
                              COALESCE(ml.total_issued, 0) as total_issued,
                              COALESCE(ml.total_returned, 0) as total_returned,
                              COALESCE(ml.late_returns, 0) as late_returns,
                              COALESCE(ml.member_status, 'active') as member_status,
                              COALESCE(ml.fine_balance, 0) as fine_balance,
                              ml.last_visit_date
                       FROM members m
                       LEFT JOIN member_limits ml ON m.member_id = ml.member_id
                       WHERE m.member_id = ? AND m.is_active = 1""",
                    (member_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    return self._row_to_dict_enhanced(row, cursor.description)
                return None
                
        except sqlite3.Error as e:
            logger.error(f"Error fetching member {member_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching member {member_id}: {e}")
            return None
    
    def get_all_members(self) -> List[Dict]:
        """Get all active members with enhanced information"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute(
                    """SELECT m.member_id, m.first_name, m.last_name, m.email, m.phone, 
                              m.member_type, m.join_date, m.is_active,
                              COALESCE(ml.max_books, 3) as max_books,
                              COALESCE(ml.current_issues, 0) as current_issues,
                              COALESCE(ml.member_status, 'active') as member_status,
                              COALESCE(ml.fine_balance, 0) as fine_balance
                       FROM members m
                       LEFT JOIN member_limits ml ON m.member_id = ml.member_id
                       WHERE m.is_active = 1
                       ORDER BY m.member_id"""
                )
                members = []
                for row in cursor.fetchall():
                    member_dict = {
                        'member_id': row[0],
                        'first_name': row[1] or '',
                        'last_name': row[2] or '',
                        'full_name': f"{row[1] or ''} {row[2] or ''}".strip(),
                        'name': f"{row[1] or ''} {row[2] or ''}".strip(),  # Compatibility
                        'email': row[3] or '',
                        'phone': row[4] or '',
                        'member_type': row[5] or 'General',
                        'join_date': row[6],
                        'is_active': row[7],
                        'max_books': row[8],
                        'current_issues': row[9],
                        'member_status': row[10],
                        'fine_balance': float(row[11])
                    }
                    members.append(member_dict)
                
                logger.info(f"Retrieved {len(members)} active members")
                return members
                
        except sqlite3.Error as e:
            logger.error(f"Error fetching members: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching members: {e}")
            return []
    
    def update_member(self, member_id: int, member_data: Dict) -> bool:
        """Update member information with proper validation"""
        try:
            # Build dynamic update query
            updates = []
            params = []
            
            updateable_fields = [
                'first_name', 'last_name', 'email', 'phone', 'date_of_birth', 'gender',
                'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country',
                'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relation',
                'identification_type', 'identification_number', 'member_type',
                'occupation', 'institution_name', 'department', 'membership_expiry', 'notes'
            ]
            
            for field in updateable_fields:
                if field in member_data:
                    value = member_data[field]
                    if value is not None:  # Allow empty strings
                        value = value.strip() if isinstance(value, str) else value
                    updates.append(f"{field} = ?")
                    params.append(value)
            
            if not updates:
                logger.warning("No valid updates provided for member update")
                return False
            
            # Add updated_date
            updates.append("updated_date = CURRENT_TIMESTAMP")
            params.append(member_id)
            
            with self.db_manager.get_connection() as conn:
                # Check if member exists
                cursor = conn.execute(
                    "SELECT member_id FROM members WHERE member_id = ? AND is_active = 1", 
                    (member_id,)
                )
                if not cursor.fetchone():
                    logger.warning(f"Active member ID {member_id} not found for update")
                    return False
                
                # Check email uniqueness if updating email
                if 'email' in member_data and member_data['email']:
                    cursor = conn.execute(
                        "SELECT member_id FROM members WHERE email = ? AND member_id != ? AND is_active = 1",
                        (member_data['email'].strip(), member_id)
                    )
                    if cursor.fetchone():
                        logger.warning(f"Email {member_data['email']} already exists for another member")
                        return False
                
                # Perform update
                cursor = conn.execute(
                    f"UPDATE members SET {', '.join(updates)} WHERE member_id = ?",
                    tuple(params)
                )
                
                if cursor.rowcount > 0:
                    conn.commit()
                    logger.info(f"Member ID {member_id} updated successfully")
                    return True
                else:
                    logger.warning(f"No rows affected when updating member ID {member_id}")
                    return False
                
        except sqlite3.IntegrityError as e:
            logger.warning(f"Member update failed - constraint violation: {e}")
            return False
        except sqlite3.Error as e:
            logger.error(f"Database error updating member {member_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error updating member {member_id}: {e}")
            return False
    
    def delete_member(self, member_id: int) -> bool:
        """Delete member (soft delete by marking as inactive)"""
        try:
            # Check if member has active transactions
            if not self._can_delete_member(member_id):
                logger.warning(f"Cannot delete member {member_id} - has active transactions")
                return False
            
            with self.db_manager.get_connection() as conn:
                # Soft delete - mark as inactive
                cursor = conn.execute(
                    "UPDATE members SET is_active = 0, updated_date = CURRENT_TIMESTAMP WHERE member_id = ?", 
                    (member_id,)
                )
                
                if cursor.rowcount > 0:
                    conn.commit()
                    logger.info(f"Member ID {member_id} deactivated successfully")
                    return True
                else:
                    logger.warning(f"Member ID {member_id} not found for deletion")
                    return False
                
        except sqlite3.Error as e:
            logger.error(f"Database error deleting member {member_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting member {member_id}: {e}")
            return False
    
    def search_members(self, search_term: str) -> List[Dict]:
        """Search members by name, email, phone, or member ID"""
        try:
            search_pattern = f'%{search_term.strip()}%'
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute(
                    """SELECT m.member_id, m.first_name, m.last_name, m.email, m.phone, 
                              m.member_type, m.join_date, m.is_active,
                              COALESCE(ml.max_books, 3) as max_books,
                              COALESCE(ml.current_issues, 0) as current_issues,
                              COALESCE(ml.member_status, 'active') as member_status,
                              COALESCE(ml.fine_balance, 0) as fine_balance
                       FROM members m
                       LEFT JOIN member_limits ml ON m.member_id = ml.member_id
                       WHERE (m.first_name LIKE ? OR m.last_name LIKE ? OR m.email LIKE ? 
                              OR m.phone LIKE ? OR CAST(m.member_id AS TEXT) LIKE ?)
                       AND m.is_active = 1
                       ORDER BY m.member_id""",
                    (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern)
                )
                members = []
                for row in cursor.fetchall():
                    member_dict = {
                        'member_id': row[0],
                        'first_name': row[1] or '',
                        'last_name': row[2] or '',
                        'full_name': f"{row[1] or ''} {row[2] or ''}".strip(),
                        'name': f"{row[1] or ''} {row[2] or ''}".strip(),  # Compatibility
                        'email': row[3] or '',
                        'phone': row[4] or '',
                        'member_type': row[5] or 'General',
                        'join_date': row[6],
                        'is_active': row[7],
                        'max_books': row[8],
                        'current_issues': row[9],
                        'member_status': row[10],
                        'fine_balance': float(row[11])
                    }
                    members.append(member_dict)
                
                logger.info(f"Search '{search_term}' returned {len(members)} members")
                return members
                
        except sqlite3.Error as e:
            logger.error(f"Error searching members: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error searching members: {e}")
            return []
    
    def get_member_statistics(self) -> Dict:
        """Get comprehensive member statistics"""
        try:
            with self.db_manager.get_connection() as conn:
                stats = {}
                
                # Total active members
                cursor = conn.execute("SELECT COUNT(*) FROM members WHERE is_active = 1")
                stats['total_members'] = cursor.fetchone()[0]
                
                # Members by type
                cursor = conn.execute(
                    "SELECT COALESCE(member_type, 'General'), COUNT(*) FROM members WHERE is_active = 1 GROUP BY member_type"
                )
                stats['members_by_type'] = dict(cursor.fetchall())
                
                # Active borrowers
                cursor = conn.execute(
                    """SELECT COUNT(DISTINCT member_id) FROM member_limits 
                       WHERE current_issues > 0 AND member_status = 'active'"""
                )
                stats['active_borrowers'] = cursor.fetchone()[0] or 0
                
                # Recent members (last 30 days)
                cursor = conn.execute(
                    """SELECT COUNT(*) FROM members 
                       WHERE join_date >= datetime('now', '-30 days') AND is_active = 1"""
                )
                stats['recent_members'] = cursor.fetchone()[0]
                
                # Overdue members
                cursor = conn.execute(
                    f"""SELECT COUNT(DISTINCT m.member_id) FROM members m
                        JOIN transactions t ON m.member_id = t.member_id
                        WHERE t.status = 'issued' 
                        AND DATE(t.issue_date, '+{settings.BORROWING_PERIOD_DAYS} days') < DATE('now')
                        AND m.is_active = 1"""
                )
                stats['overdue_members'] = cursor.fetchone()[0] or 0
                
                # Members with fines
                cursor = conn.execute(
                    """SELECT COUNT(*), COALESCE(SUM(fine_balance), 0) FROM member_limits 
                       WHERE fine_balance > 0"""
                )
                fine_data = cursor.fetchone()
                stats['members_with_fines'] = fine_data[0] or 0
                stats['total_fines'] = float(fine_data[1]) if fine_data[1] else 0.0
                
                # Members at limit
                cursor = conn.execute(
                    """SELECT COUNT(*) FROM member_limits 
                       WHERE current_issues >= max_books AND member_status = 'active'"""
                )
                stats['members_at_limit'] = cursor.fetchone()[0] or 0
                
                # ID ranges
                cursor = conn.execute("SELECT MIN(member_id), MAX(member_id) FROM members WHERE is_active = 1")
                id_range = cursor.fetchone()
                stats['id_range'] = {'min': id_range[0] or 0, 'max': id_range[1] or 0}
                
                logger.info("Member statistics retrieved successfully")
                return stats
                
        except sqlite3.Error as e:
            logger.error(f"Error getting member statistics: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error getting member statistics: {e}")
            return {}
    
    def get_member_types(self) -> List[str]:
        """Get available member types"""
        return ['Student', 'Faculty', 'Staff', 'Senior Citizen', 'General', 'Premium']
    
    def get_identification_types(self) -> List[str]:
        """Get available identification types"""
        return ['Aadhar', 'PAN', 'Driving License', 'Passport', 'Student ID', 'Employee ID', 'Other']
    
    def _validate_member_data(self, member_data: Dict, member_id: int = None) -> None:
        """Validate member data"""
        required_fields = ['first_name', 'last_name', 'email', 'phone']
        errors = []
        
        for field in required_fields:
            value = member_data.get(field, '').strip() if member_data.get(field) else ''
            if not value:
                errors.append(f"{field.replace('_', ' ').title()} is required")
        
        # Validate email format
        email = member_data.get('email', '').strip()
        if email and not DataHelper.validate_email(email):
            errors.append("Invalid email format")
        
        # Validate phone (basic check)
        phone = member_data.get('phone', '').strip()
        if phone and len(phone) < 10:
            errors.append("Phone number must be at least 10 digits")
        
        # Validate custom member_id if provided
        if member_id is not None:
            if not isinstance(member_id, int) or member_id <= 0:
                errors.append("Member ID must be a positive integer")
        
        if errors:
            raise ValidationError("; ".join(errors))
    
    def _get_default_book_limit(self, member_type: str) -> int:
        """Get default book limit based on member type"""
        limits = {
            'Student': 3,
            'Faculty': 10,
            'Staff': 5,
            'Senior Citizen': 5,
            'General': 3,
            'Premium': 15
        }
        return limits.get(member_type, 3)
    
    def _can_delete_member(self, member_id: int) -> bool:
        """Check if member can be deleted (no active transactions)"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM transactions WHERE member_id = ? AND status = 'issued'",
                    (member_id,)
                )
                return cursor.fetchone()[0] == 0
        except sqlite3.Error:
            return False
    
    def _row_to_dict_enhanced(self, row, description) -> Dict:
        """Convert database row to dictionary with all fields"""
        member_dict = {}
        for i, col in enumerate(description):
            member_dict[col[0]] = row[i]
        
        # Add computed fields
        first_name = member_dict.get('first_name', '') or ''
        last_name = member_dict.get('last_name', '') or ''
        member_dict['full_name'] = f"{first_name} {last_name}".strip()
        member_dict['name'] = member_dict['full_name']  # Compatibility
        
        return member_dict
    
    # Keep legacy compatibility methods
    def get_member_by_email(self, email: str) -> Optional[Dict]:
        """Get member by email address"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute(
                    """SELECT m.*, 
                              COALESCE(ml.max_books, 3) as max_books,
                              COALESCE(ml.current_issues, 0) as current_issues,
                              COALESCE(ml.member_status, 'active') as member_status
                       FROM members m
                       LEFT JOIN member_limits ml ON m.member_id = ml.member_id
                       WHERE m.email = ? AND m.is_active = 1""",
                    (email,)
                )
                row = cursor.fetchone()
                
                if row:
                    return self._row_to_dict_enhanced(row, cursor.description)
                return None
                
        except sqlite3.Error as e:
            logger.error(f"Error fetching member by email: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching member by email: {e}")
            return None