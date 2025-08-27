"""
Enhanced Transaction model that integrates with member limits and comprehensive tracking
"""

import sqlite3
import datetime
from typing import Dict, List, Optional, Tuple
from models.database import DatabaseManager
from utils.helpers import DataHelper
from utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)


class Transaction:
    """Enhanced Transaction model class for book issue/return management with member limits"""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize enhanced transaction model"""
        self.db_manager = db_manager
        logger.info("Enhanced Transaction model initialized")
    
    def issue_book(self, book_id: int, member_id: int) -> bool:
        """Issue a book to a member with comprehensive validation"""
        try:
            with self.db_manager.get_connection() as conn:
                # Check if book exists and is available
                cursor = conn.execute(
                    "SELECT availability_status FROM books WHERE book_id = ?", 
                    (book_id,)
                )
                book = cursor.fetchone()
                
                if not book:
                    logger.warning(f"Book ID {book_id} not found")
                    return False
                
                if book[0] != 'available':
                    logger.warning(f"Book ID {book_id} is not available for issue")
                    return False
                
                # Check enhanced member information and limits
                cursor = conn.execute(
                    """SELECT m.member_id, m.first_name, m.last_name, m.is_active,
                              COALESCE(ml.max_books, 3) as max_books,
                              COALESCE(ml.current_issues, 0) as current_issues,
                              COALESCE(ml.member_status, 'active') as member_status
                       FROM members m
                       LEFT JOIN member_limits ml ON m.member_id = ml.member_id
                       WHERE m.member_id = ? AND m.is_active = 1""",
                    (member_id,)
                )
                member_data = cursor.fetchone()
                
                if not member_data:
                    logger.warning(f"Active member ID {member_id} not found")
                    return False
                
                member_id, first_name, last_name, is_active, max_books, current_issues, member_status = member_data
                member_name = f"{first_name} {last_name}"
                
                # Check member status
                if member_status != 'active':
                    logger.warning(f"Member {member_name} is {member_status}")
                    return False
                
                # Check issue limits
                if current_issues >= max_books:
                    logger.warning(f"Member {member_name} has reached maximum book limit ({max_books})")
                    return False
                
                # Check for overdue books
                cursor = conn.execute(
                    f"""SELECT COUNT(*) FROM transactions 
                        WHERE member_id = ? AND status = 'issued' 
                        AND DATE(issue_date, '+{settings.BORROWING_PERIOD_DAYS} days') < DATE('now')""",
                    (member_id,)
                )
                overdue_count = cursor.fetchone()[0]
                
                if overdue_count > 0:
                    logger.warning(f"Member {member_name} has {overdue_count} overdue book(s)")
                    return False
                
                # All checks passed, create transaction
                cursor = conn.execute(
                    "INSERT INTO transactions (book_id, member_id) VALUES (?, ?)",
                    (book_id, member_id)
                )
                transaction_id = cursor.lastrowid
                
                # Update book availability status
                conn.execute(
                    "UPDATE books SET availability_status = 'issued' WHERE book_id = ?",
                    (book_id,)
                )
                
                # Update member limits - ensure record exists first
                conn.execute(
                    """INSERT OR IGNORE INTO member_limits (member_id, max_books) 
                       VALUES (?, ?)""",
                    (member_id, max_books)
                )
                
                # Increment current issues and total issued
                conn.execute(
                    """UPDATE member_limits SET 
                       current_issues = current_issues + 1,
                       total_issued = total_issued + 1,
                       last_visit_date = CURRENT_TIMESTAMP,
                       updated_date = CURRENT_TIMESTAMP
                       WHERE member_id = ?""",
                    (member_id,)
                )
                
                conn.commit()
                logger.info(f"Book ID {book_id} issued to member ID {member_id} (Transaction: {transaction_id})")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Error issuing book: {e}")
            return False
    
    def return_book(self, book_id: int, member_id: int) -> Tuple[bool, float]:
        """Return a book and calculate late fee with member stats update"""
        try:
            with self.db_manager.get_connection() as conn:
                # Find active transaction
                cursor = conn.execute(
                    """SELECT transaction_id, issue_date FROM transactions 
                       WHERE book_id = ? AND member_id = ? AND status = 'issued'""",
                    (book_id, member_id)
                )
                transaction = cursor.fetchone()
                
                if not transaction:
                    logger.warning(f"No active transaction found for book ID {book_id} and member ID {member_id}")
                    return False, 0.0
                
                transaction_id, issue_date = transaction
                
                # Calculate late fee and determine if return was late
                issue_datetime = datetime.datetime.fromisoformat(issue_date)
                late_fee = DataHelper.calculate_late_fee(issue_datetime)
                was_late = late_fee > 0
                
                # Update transaction record
                conn.execute(
                    """UPDATE transactions 
                       SET return_date = CURRENT_TIMESTAMP, status = 'returned', late_fee = ? 
                       WHERE transaction_id = ?""",
                    (late_fee, transaction_id)
                )
                
                # Update book availability status
                conn.execute(
                    "UPDATE books SET availability_status = 'available' WHERE book_id = ?",
                    (book_id,)
                )
                
                # Update member stats - ensure record exists first
                conn.execute(
                    """INSERT OR IGNORE INTO member_limits (member_id, max_books) 
                       VALUES (?, 3)""",
                    (member_id,)
                )
                
                # Update member limits based on return
                if was_late:
                    conn.execute(
                        """UPDATE member_limits SET 
                           current_issues = MAX(0, current_issues - 1),
                           total_returned = total_returned + 1,
                           late_returns = late_returns + 1,
                           fine_balance = fine_balance + ?,
                           last_visit_date = CURRENT_TIMESTAMP,
                           updated_date = CURRENT_TIMESTAMP
                           WHERE member_id = ?""",
                        (late_fee, member_id)
                    )
                else:
                    conn.execute(
                        """UPDATE member_limits SET 
                           current_issues = MAX(0, current_issues - 1),
                           total_returned = total_returned + 1,
                           last_visit_date = CURRENT_TIMESTAMP,
                           updated_date = CURRENT_TIMESTAMP
                           WHERE member_id = ?""",
                        (member_id,)
                    )
                
                conn.commit()
                logger.info(f"Book ID {book_id} returned by member ID {member_id}, late fee: ${late_fee:.2f}")
                return True, late_fee
                
        except sqlite3.Error as e:
            logger.error(f"Error returning book: {e}")
            return False, 0.0
    
    def get_member_transaction_summary(self, member_id: int) -> Dict:
        """Get comprehensive transaction summary for a member"""
        try:
            with self.db_manager.get_connection() as conn:
                # Get member basic info with limits
                cursor = conn.execute(
                    """SELECT m.member_id, m.first_name, m.last_name, m.email, m.phone, m.member_type,
                              COALESCE(ml.max_books, 3) as max_books,
                              COALESCE(ml.current_issues, 0) as current_issues,
                              COALESCE(ml.total_issued, 0) as total_issued,
                              COALESCE(ml.total_returned, 0) as total_returned,
                              COALESCE(ml.late_returns, 0) as late_returns,
                              COALESCE(ml.member_status, 'active') as member_status,
                              COALESCE(ml.fine_balance, 0) as fine_balance
                       FROM members m
                       LEFT JOIN member_limits ml ON m.member_id = ml.member_id
                       WHERE m.member_id = ? AND m.is_active = 1""",
                    (member_id,)
                )
                member_row = cursor.fetchone()
                
                if not member_row:
                    return {}
                
                # Get currently issued books
                cursor = conn.execute(
                    """SELECT t.transaction_id, t.issue_date, b.book_id, b.title, b.author,
                              (julianday('now') - julianday(t.issue_date)) as days_issued
                       FROM transactions t
                       JOIN books b ON t.book_id = b.book_id
                       WHERE t.member_id = ? AND t.status = 'issued'
                       ORDER BY t.issue_date ASC""",
                    (member_id,)
                )
                
                issued_books = []
                overdue_count = 0
                for row in cursor.fetchall():
                    days_issued = int(row[5]) if row[5] else 0
                    is_overdue = days_issued > settings.BORROWING_PERIOD_DAYS
                    if is_overdue:
                        overdue_count += 1
                    
                    issued_books.append({
                        'transaction_id': row[0],
                        'issue_date': row[1],
                        'book_id': row[2],
                        'title': row[3],
                        'author': row[4],
                        'days_issued': days_issued,
                        'is_overdue': is_overdue
                    })
                
                # Get recent transaction history (last 10)
                cursor = conn.execute(
                    """SELECT t.transaction_id, t.issue_date, t.return_date, t.status, t.late_fee,
                              b.title, b.author
                       FROM transactions t
                       JOIN books b ON t.book_id = b.book_id
                       WHERE t.member_id = ?
                       ORDER BY t.issue_date DESC
                       LIMIT 10""",
                    (member_id,)
                )
                
                recent_transactions = []
                for row in cursor.fetchall():
                    recent_transactions.append({
                        'transaction_id': row[0],
                        'issue_date': row[1],
                        'return_date': row[2],
                        'status': row[3],
                        'late_fee': row[4],
                        'book_title': row[5],
                        'book_author': row[6]
                    })
                
                # Calculate availability for new issues
                can_issue_more = (member_row[7] < member_row[6] and 
                                 member_row[11] == 'active' and 
                                 overdue_count == 0)
                
                return {
                    'member_id': member_row[0],
                    'name': f"{member_row[1]} {member_row[2]}",
                    'first_name': member_row[1],
                    'last_name': member_row[2],
                    'email': member_row[3],
                    'phone': member_row[4],
                    'member_type': member_row[5],
                    'max_books': member_row[6],
                    'current_issues': member_row[7],
                    'total_issued': member_row[8],
                    'total_returned': member_row[9],
                    'late_returns': member_row[10],
                    'member_status': member_row[11],
                    'fine_balance': float(member_row[12]),
                    'overdue_count': overdue_count,
                    'can_issue_more': can_issue_more,
                    'available_slots': max(0, member_row[6] - member_row[7]),
                    'issued_books': issued_books,
                    'recent_transactions': recent_transactions
                }
                
        except sqlite3.Error as e:
            logger.error(f"Error getting member transaction summary: {e}")
            return {}
    
    def renew_book(self, transaction_id: int, days: int = None) -> bool:
        """Renew a book (extend borrowing period) with member limit checks"""
        try:
            renewal_days = days or settings.BORROWING_PERIOD_DAYS
            
            with self.db_manager.get_connection() as conn:
                # Get transaction and member details
                cursor = conn.execute(
                    """SELECT t.book_id, t.member_id, t.issue_date,
                              m.first_name, m.last_name, COALESCE(ml.member_status, 'active') as member_status
                       FROM transactions t
                       JOIN members m ON t.member_id = m.member_id
                       LEFT JOIN member_limits ml ON m.member_id = ml.member_id
                       WHERE t.transaction_id = ? AND t.status = 'issued' AND m.is_active = 1""",
                    (transaction_id,)
                )
                
                result = cursor.fetchone()
                if not result:
                    logger.warning(f"No active transaction found with ID {transaction_id}")
                    return False
                
                book_id, member_id, issue_date, first_name, last_name, member_status = result
                member_name = f"{first_name} {last_name}"
                
                # Check if member can renew (must be active)
                if member_status != 'active':
                    logger.warning(f"Cannot renew - member {member_name} is {member_status}")
                    return False
                
                # Check if book is not already overdue by more than grace period
                issue_dt = datetime.datetime.fromisoformat(issue_date)
                days_issued = (datetime.datetime.now() - issue_dt).days
                
                if days_issued > settings.BORROWING_PERIOD_DAYS + 7:  # 7-day grace period
                    logger.warning(f"Cannot renew - book is {days_issued} days overdue (limit: {settings.BORROWING_PERIOD_DAYS + 7})")
                    return False
                
                # Update issue date to extend borrowing period
                new_issue_date = datetime.datetime.now()
                cursor = conn.execute(
                    "UPDATE transactions SET issue_date = ? WHERE transaction_id = ?",
                    (new_issue_date.isoformat(), transaction_id)
                )
                
                if cursor.rowcount > 0:
                    conn.commit()
                    logger.info(f"Transaction {transaction_id} renewed for member {member_name}")
                    return True
                return False
                
        except sqlite3.Error as e:
            logger.error(f"Error renewing transaction: {e}")
            return False
    
    # Keep all original methods for compatibility
    def get_transaction_by_id(self, transaction_id: int) -> Optional[Dict]:
        """Get transaction by ID"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute(
                    """SELECT t.transaction_id, t.book_id, t.member_id, 
                              b.title, b.author, 
                              COALESCE(m.first_name || ' ' || m.last_name, 'Unknown') as member_name, 
                              m.email,
                              t.issue_date, t.return_date, t.status, t.late_fee
                       FROM transactions t
                       JOIN books b ON t.book_id = b.book_id
                       LEFT JOIN members m ON t.member_id = m.member_id
                       WHERE t.transaction_id = ?""",
                    (transaction_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    return self._row_to_dict(row)
                return None
                
        except sqlite3.Error as e:
            logger.error(f"Error fetching transaction {transaction_id}: {e}")
            return None
    
    def get_issued_books(self) -> List[Dict]:
        """Get all currently issued books with enhanced member info"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute(
                    """SELECT t.transaction_id, t.book_id, t.member_id,
                              b.title, b.author, 
                              COALESCE(m.first_name || ' ' || m.last_name, 'Unknown') as member_name, 
                              m.email,
                              t.issue_date, t.return_date, t.status, t.late_fee,
                              COALESCE(ml.member_status, 'active') as member_status
                       FROM transactions t
                       JOIN books b ON t.book_id = b.book_id
                       LEFT JOIN members m ON t.member_id = m.member_id
                       LEFT JOIN member_limits ml ON m.member_id = ml.member_id
                       WHERE t.status = 'issued'
                       ORDER BY t.issue_date"""
                )
                transactions = []
                for row in cursor.fetchall():
                    transaction_dict = self._row_to_dict_enhanced(row)
                    # Add calculated fields
                    issue_date = datetime.datetime.fromisoformat(transaction_dict['issue_date'])
                    transaction_dict['days_issued'] = DataHelper.calculate_days_between(issue_date)
                    transaction_dict['is_overdue'] = transaction_dict['days_issued'] > settings.BORROWING_PERIOD_DAYS
                    transactions.append(transaction_dict)
                return transactions
                
        except sqlite3.Error as e:
            logger.error(f"Error fetching issued books: {e}")
            return []
    
    def get_overdue_books(self) -> List[Dict]:
        """Get overdue books with enhanced member info"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute(
                    f"""SELECT t.transaction_id, t.book_id, t.member_id,
                               b.title, b.author, 
                               COALESCE(m.first_name || ' ' || m.last_name, 'Unknown') as member_name, 
                               m.email,
                               t.issue_date, t.return_date, t.status, t.late_fee,
                               COALESCE(ml.member_status, 'active') as member_status
                        FROM transactions t
                        JOIN books b ON t.book_id = b.book_id
                        LEFT JOIN members m ON t.member_id = m.member_id
                        LEFT JOIN member_limits ml ON m.member_id = ml.member_id
                        WHERE t.status = 'issued' 
                        AND DATE(t.issue_date, '+{settings.BORROWING_PERIOD_DAYS} days') < DATE('now')
                        ORDER BY t.issue_date"""
                )
                overdue = []
                for row in cursor.fetchall():
                    transaction_dict = self._row_to_dict_enhanced(row)
                    # Add calculated fields
                    issue_date = datetime.datetime.fromisoformat(transaction_dict['issue_date'])
                    days_issued = DataHelper.calculate_days_between(issue_date)
                    transaction_dict['days_issued'] = days_issued
                    transaction_dict['days_overdue'] = max(days_issued - settings.BORROWING_PERIOD_DAYS, 0)
                    transaction_dict['calculated_late_fee'] = DataHelper.calculate_late_fee(issue_date)
                    overdue.append(transaction_dict)
                return overdue
                
        except sqlite3.Error as e:
            logger.error(f"Error fetching overdue books: {e}")
            return []
    
    def get_transaction_history(self, limit: int = None) -> List[Dict]:
        """Get complete transaction history"""
        try:
            query = """SELECT t.transaction_id, t.book_id, t.member_id,
                              b.title, b.author, 
                              COALESCE(m.first_name || ' ' || m.last_name, 'Unknown') as member_name, 
                              m.email,
                              t.issue_date, t.return_date, t.status, t.late_fee
                       FROM transactions t
                       JOIN books b ON t.book_id = b.book_id
                       LEFT JOIN members m ON t.member_id = m.member_id
                       ORDER BY t.issue_date DESC"""
            
            if limit:
                query += f" LIMIT {limit}"
            
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute(query)
                transactions = []
                for row in cursor.fetchall():
                    transactions.append(self._row_to_dict(row))
                return transactions
                
        except sqlite3.Error as e:
            logger.error(f"Error fetching transaction history: {e}")
            return []
    
    def get_transaction_statistics(self) -> Dict:
        """Get transaction statistics with member info"""
        try:
            with self.db_manager.get_connection() as conn:
                # Total transactions
                cursor = conn.execute("SELECT COUNT(*) FROM transactions")
                total_transactions = cursor.fetchone()[0]
                
                # Currently issued
                cursor = conn.execute("SELECT COUNT(*) FROM transactions WHERE status = 'issued'")
                currently_issued = cursor.fetchone()[0]
                
                # Total returned
                cursor = conn.execute("SELECT COUNT(*) FROM transactions WHERE status = 'returned'")
                total_returned = cursor.fetchone()[0]
                
                # Overdue transactions
                cursor = conn.execute(
                    f"""SELECT COUNT(*) FROM transactions 
                        WHERE status = 'issued' 
                        AND DATE(issue_date, '+{settings.BORROWING_PERIOD_DAYS} days') < DATE('now')"""
                )
                overdue_count = cursor.fetchone()[0]
                
                # Total late fees collected
                cursor = conn.execute("SELECT COALESCE(SUM(late_fee), 0) FROM transactions WHERE status = 'returned'")
                total_late_fees = cursor.fetchone()[0]
                
                # Average borrowing period
                cursor = conn.execute(
                    """SELECT AVG(julianday(return_date) - julianday(issue_date)) 
                       FROM transactions WHERE status = 'returned' AND return_date IS NOT NULL"""
                )
                avg_borrowing_days = cursor.fetchone()[0] or 0
                
                # Members at book limit
                cursor = conn.execute(
                    """SELECT COUNT(*) FROM member_limits 
                       WHERE current_issues >= max_books AND member_status = 'active'"""
                )
                members_at_limit = cursor.fetchone()[0]
                
                return {
                    'total_transactions': total_transactions,
                    'currently_issued': currently_issued,
                    'total_returned': total_returned,
                    'overdue_count': overdue_count,
                    'total_late_fees': float(total_late_fees),
                    'average_borrowing_days': round(float(avg_borrowing_days), 1),
                    'members_at_limit': members_at_limit
                }
                
        except sqlite3.Error as e:
            logger.error(f"Error getting transaction statistics: {e}")
            return {}
    
    def get_member_transactions(self, member_id: int) -> List[Dict]:
        """Get all transactions for a specific member"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute(
                    """SELECT t.transaction_id, t.book_id, t.member_id,
                              b.title, b.author, 
                              COALESCE(m.first_name || ' ' || m.last_name, 'Unknown') as member_name, 
                              m.email,
                              t.issue_date, t.return_date, t.status, t.late_fee
                       FROM transactions t
                       JOIN books b ON t.book_id = b.book_id
                       LEFT JOIN members m ON t.member_id = m.member_id
                       WHERE t.member_id = ?
                       ORDER BY t.issue_date DESC""",
                    (member_id,)
                )
                transactions = []
                for row in cursor.fetchall():
                    transactions.append(self._row_to_dict(row))
                return transactions
                
        except sqlite3.Error as e:
            logger.error(f"Error fetching member transactions: {e}")
            return []
    
    def get_book_transactions(self, book_id: int) -> List[Dict]:
        """Get all transactions for a specific book"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute(
                    """SELECT t.transaction_id, t.book_id, t.member_id,
                              b.title, b.author, 
                              COALESCE(m.first_name || ' ' || m.last_name, 'Unknown') as member_name, 
                              m.email,
                              t.issue_date, t.return_date, t.status, t.late_fee
                       FROM transactions t
                       JOIN books b ON t.book_id = b.book_id
                       LEFT JOIN members m ON t.member_id = m.member_id
                       WHERE t.book_id = ?
                       ORDER BY t.issue_date DESC""",
                    (book_id,)
                )
                transactions = []
                for row in cursor.fetchall():
                    transactions.append(self._row_to_dict(row))
                return transactions
                
        except sqlite3.Error as e:
            logger.error(f"Error fetching book transactions: {e}")
            return []
    
    def _row_to_dict(self, row) -> Dict:
        """Convert database row to dictionary"""
        return {
            'transaction_id': row[0],
            'book_id': row[1],
            'member_id': row[2],
            'book_title': row[3],
            'book_author': row[4],
            'member_name': row[5],
            'member_email': row[6],
            'issue_date': row[7],
            'return_date': row[8],
            'status': row[9],
            'late_fee': float(row[10]) if row[10] else 0.0
        }
    
    def _row_to_dict_enhanced(self, row) -> Dict:
        """Convert database row to dictionary with enhanced member info"""
        base_dict = self._row_to_dict(row)
        if len(row) > 11:
            base_dict['member_status'] = row[11]
        else:
            base_dict['member_status'] = 'active'
        return base_dict
