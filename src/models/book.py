"""
Enhanced Book Model with Custom ID Support
"""

import sqlite3
from typing import Dict, List, Optional
from models.database import DatabaseManager
from utils.helpers import ValidationError, DataHelper
from utils.logger import get_logger

logger = get_logger(__name__)


class Book:
    """Enhanced Book model with custom ID support"""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize book model"""
        self.db_manager = db_manager
        logger.info("Enhanced Book model with custom ID support initialized")
    
    def add_book(self, title: str, author: str, category: str, isbn: str, book_id: int = None) -> bool:
        """Add new book with optional custom ID"""
        try:
            # Validate inputs
            self._validate_book_data(title, author, category, isbn, book_id)
            
            with self.db_manager.get_connection() as conn:
                # Check if ISBN already exists
                cursor = conn.execute("SELECT book_id FROM books WHERE isbn = ?", (isbn.strip(),))
                existing_book = cursor.fetchone()
                
                if existing_book:
                    logger.warning(f"Book with ISBN {isbn} already exists (ID: {existing_book[0]})")
                    return False
                
                # Check if custom book_id already exists
                if book_id is not None:
                    cursor = conn.execute("SELECT book_id FROM books WHERE book_id = ?", (book_id,))
                    existing_id = cursor.fetchone()
                    
                    if existing_id:
                        logger.warning(f"Book ID {book_id} already exists")
                        return False
                
                # Insert new book with or without custom ID
                if book_id is not None:
                    cursor = conn.execute(
                        """INSERT INTO books (book_id, title, author, category, isbn, availability_status) 
                           VALUES (?, ?, ?, ?, ?, 'available')""",
                        (book_id, title.strip(), author.strip(), category.strip(), isbn.strip())
                    )
                    actual_book_id = book_id
                else:
                    cursor = conn.execute(
                        """INSERT INTO books (title, author, category, isbn, availability_status) 
                           VALUES (?, ?, ?, ?, 'available')""",
                        (title.strip(), author.strip(), category.strip(), isbn.strip())
                    )
                    actual_book_id = cursor.lastrowid
                
                conn.commit()
                
                logger.info(f"Book added successfully: ID {actual_book_id}, Title: '{title}', ISBN: {isbn}")
                return True
                
        except ValidationError as e:
            logger.warning(f"Book validation failed: {e}")
            return False
        except sqlite3.IntegrityError as e:
            logger.warning(f"Book with ISBN {isbn} or ID {book_id} already exists: {e}")
            return False
        except sqlite3.Error as e:
            logger.error(f"Database error adding book: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error adding book: {e}")
            return False
    
    def get_next_available_id(self) -> int:
        """Get the next available book ID"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute("SELECT COALESCE(MAX(book_id), 0) + 1 FROM books")
                next_id = cursor.fetchone()[0]
                logger.info(f"Next available book ID: {next_id}")
                return next_id
                
        except sqlite3.Error as e:
            logger.error(f"Error getting next book ID: {e}")
            return 1
        except Exception as e:
            logger.error(f"Unexpected error getting next book ID: {e}")
            return 1
    
    def is_id_available(self, book_id: int) -> bool:
        """Check if a book ID is available"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM books WHERE book_id = ?", (book_id,))
                count = cursor.fetchone()[0]
                return count == 0
                
        except sqlite3.Error as e:
            logger.error(f"Error checking book ID availability: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking book ID availability: {e}")
            return False
    
    def get_book_by_id(self, book_id: int) -> Optional[Dict]:
        """Get book by ID"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT book_id, title, author, category, isbn, availability_status, created_date FROM books WHERE book_id = ?",
                    (book_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    return self._row_to_dict(row)
                return None
                
        except sqlite3.Error as e:
            logger.error(f"Error fetching book {book_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching book {book_id}: {e}")
            return None
    
    def get_all_books(self) -> List[Dict]:
        """Get all books"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute(
                    """SELECT book_id, title, author, category, isbn, availability_status, created_date 
                       FROM books ORDER BY book_id"""
                )
                
                books = []
                for row in cursor.fetchall():
                    books.append(self._row_to_dict(row))
                
                logger.info(f"Retrieved {len(books)} books")
                return books
                
        except sqlite3.Error as e:
            logger.error(f"Error fetching all books: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching books: {e}")
            return []
    
    def get_available_books(self) -> List[Dict]:
        """Get all available books"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute(
                    """SELECT book_id, title, author, category, isbn, availability_status, created_date 
                       FROM books WHERE availability_status = 'available' ORDER BY book_id"""
                )
                
                books = []
                for row in cursor.fetchall():
                    books.append(self._row_to_dict(row))
                
                logger.info(f"Retrieved {len(books)} available books")
                return books
                
        except sqlite3.Error as e:
            logger.error(f"Error fetching available books: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching available books: {e}")
            return []
    
    def search_books(self, search_term: str) -> List[Dict]:
        """Search books by title, author, category, or ISBN"""
        try:
            search_pattern = f'%{search_term.strip()}%'
            
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute(
                    """SELECT book_id, title, author, category, isbn, availability_status, created_date 
                       FROM books 
                       WHERE title LIKE ? OR author LIKE ? OR category LIKE ? OR isbn LIKE ? OR CAST(book_id AS TEXT) LIKE ?
                       ORDER BY book_id""",
                    (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern)
                )
                
                books = []
                for row in cursor.fetchall():
                    books.append(self._row_to_dict(row))
                
                logger.info(f"Search '{search_term}' returned {len(books)} books")
                return books
                
        except sqlite3.Error as e:
            logger.error(f"Error searching books: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error searching books: {e}")
            return []
    
    def update_book(self, book_id: int, title: str = None, author: str = None, 
                   category: str = None, isbn: str = None) -> bool:
        """Update book information"""
        try:
            updates = []
            params = []
            
            if title:
                if not title.strip():
                    raise ValidationError("Title cannot be empty")
                updates.append("title = ?")
                params.append(title.strip())
            
            if author:
                if not author.strip():
                    raise ValidationError("Author cannot be empty")
                updates.append("author = ?")
                params.append(author.strip())
            
            if category:
                if not category.strip():
                    raise ValidationError("Category cannot be empty")
                updates.append("category = ?")
                params.append(category.strip())
            
            if isbn:
                if not DataHelper.validate_isbn(isbn.strip()):
                    raise ValidationError("Invalid ISBN format")
                updates.append("isbn = ?")
                params.append(isbn.strip())
            
            if not updates:
                logger.warning("No valid updates provided for book update")
                return False
            
            params.append(book_id)
            
            with self.db_manager.get_connection() as conn:
                # Check if book exists
                cursor = conn.execute("SELECT book_id FROM books WHERE book_id = ?", (book_id,))
                if not cursor.fetchone():
                    logger.warning(f"Book ID {book_id} not found for update")
                    return False
                
                # Check ISBN uniqueness if updating ISBN
                if isbn:
                    cursor = conn.execute(
                        "SELECT book_id FROM books WHERE isbn = ? AND book_id != ?", 
                        (isbn.strip(), book_id)
                    )
                    if cursor.fetchone():
                        logger.warning(f"ISBN {isbn} already exists for another book")
                        return False
                
                # Perform update
                cursor = conn.execute(
                    f"UPDATE books SET {', '.join(updates)} WHERE book_id = ?",
                    tuple(params)
                )
                
                if cursor.rowcount > 0:
                    conn.commit()
                    logger.info(f"Book ID {book_id} updated successfully")
                    return True
                else:
                    logger.warning(f"No rows affected when updating book ID {book_id}")
                    return False
                
        except ValidationError as e:
            logger.warning(f"Book update validation failed: {e}")
            return False
        except sqlite3.IntegrityError as e:
            logger.warning(f"Book update failed - constraint violation: {e}")
            return False
        except sqlite3.Error as e:
            logger.error(f"Database error updating book {book_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error updating book {book_id}: {e}")
            return False
    
    def delete_book(self, book_id: int) -> bool:
        """Delete book (only if not currently issued)"""
        try:
            with self.db_manager.get_connection() as conn:
                # Check if book is currently issued
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM transactions WHERE book_id = ? AND status = 'issued'",
                    (book_id,)
                )
                
                if cursor.fetchone()[0] > 0:
                    logger.warning(f"Cannot delete book ID {book_id} - currently issued")
                    return False
                
                # Delete the book
                cursor = conn.execute("DELETE FROM books WHERE book_id = ?", (book_id,))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    logger.info(f"Book ID {book_id} deleted successfully")
                    return True
                else:
                    logger.warning(f"Book ID {book_id} not found for deletion")
                    return False
                
        except sqlite3.Error as e:
            logger.error(f"Database error deleting book {book_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting book {book_id}: {e}")
            return False
    
    def update_availability(self, book_id: int, status: str) -> bool:
        """Update book availability status"""
        try:
            valid_statuses = ['available', 'issued', 'maintenance']
            if status not in valid_statuses:
                logger.warning(f"Invalid availability status: {status}")
                return False
            
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute(
                    "UPDATE books SET availability_status = ? WHERE book_id = ?",
                    (status, book_id)
                )
                
                if cursor.rowcount > 0:
                    conn.commit()
                    logger.info(f"Book ID {book_id} availability updated to '{status}'")
                    return True
                else:
                    logger.warning(f"Book ID {book_id} not found for availability update")
                    return False
                
        except sqlite3.Error as e:
            logger.error(f"Database error updating book availability: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error updating book availability: {e}")
            return False
    
    def get_book_statistics(self) -> Dict:
        """Get book statistics"""
        try:
            with self.db_manager.get_connection() as conn:
                stats = {}
                
                # Total books
                cursor = conn.execute("SELECT COUNT(*) FROM books")
                stats['total_books'] = cursor.fetchone()[0]
                
                # Available books
                cursor = conn.execute("SELECT COUNT(*) FROM books WHERE availability_status = 'available'")
                stats['available_books'] = cursor.fetchone()[0]
                
                # Issued books
                cursor = conn.execute("SELECT COUNT(*) FROM books WHERE availability_status = 'issued'")
                stats['issued_books'] = cursor.fetchone()[0]
                
                # Books in maintenance
                cursor = conn.execute("SELECT COUNT(*) FROM books WHERE availability_status = 'maintenance'")
                stats['maintenance_books'] = cursor.fetchone()[0]
                
                # Books by category
                cursor = conn.execute(
                    "SELECT category, COUNT(*) FROM books GROUP BY category ORDER BY COUNT(*) DESC"
                )
                stats['categories'] = dict(cursor.fetchall())
                
                # Recent additions (last 30 days)
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM books WHERE created_date >= datetime('now', '-30 days')"
                )
                stats['recent_additions'] = cursor.fetchone()[0]
                
                # ID ranges
                cursor = conn.execute("SELECT MIN(book_id), MAX(book_id) FROM books")
                id_range = cursor.fetchone()
                stats['id_range'] = {'min': id_range[0] or 0, 'max': id_range[1] or 0}
                
                logger.info("Book statistics retrieved successfully")
                return stats
                
        except sqlite3.Error as e:
            logger.error(f"Error getting book statistics: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error getting book statistics: {e}")
            return {}
    
    def get_books_by_category(self, category: str) -> List[Dict]:
        """Get books by specific category"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute(
                    """SELECT book_id, title, author, category, isbn, availability_status, created_date 
                       FROM books WHERE category = ? ORDER BY book_id""",
                    (category,)
                )
                
                books = []
                for row in cursor.fetchall():
                    books.append(self._row_to_dict(row))
                
                logger.info(f"Retrieved {len(books)} books in category '{category}'")
                return books
                
        except sqlite3.Error as e:
            logger.error(f"Error fetching books by category: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching books by category: {e}")
            return []
    
    def _validate_book_data(self, title: str, author: str, category: str, isbn: str, book_id: int = None) -> None:
        """Validate book data before adding/updating"""
        errors = []
        
        if not title or not title.strip():
            errors.append("Title is required")
        elif len(title.strip()) < 2:
            errors.append("Title must be at least 2 characters")
        
        if not author or not author.strip():
            errors.append("Author is required")
        elif len(author.strip()) < 2:
            errors.append("Author must be at least 2 characters")
        
        if not category or not category.strip():
            errors.append("Category is required")
        elif len(category.strip()) < 2:
            errors.append("Category must be at least 2 characters")
        
        if not isbn or not isbn.strip():
            errors.append("ISBN is required")
        elif not DataHelper.validate_isbn(isbn.strip()):
            errors.append("Invalid ISBN format")
        
        # Validate custom book_id if provided
        if book_id is not None:
            if not isinstance(book_id, int) or book_id <= 0:
                errors.append("Book ID must be a positive integer")
        
        if errors:
            raise ValidationError("; ".join(errors))
    
    def _row_to_dict(self, row) -> Dict:
        """Convert database row to dictionary"""
        return {
            'book_id': row[0],
            'title': row[1],
            'author': row[2],
            'category': row[3],
            'isbn': row[4],
            'availability_status': row[5],
            'created_date': row[6]
        }