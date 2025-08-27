"""
Helper functions and utilities for Library Management System
"""

import datetime
import csv
import os
from typing import Dict, List, Any, Optional
from config.settings import settings


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class DataHelper:
    """Helper class for data operations"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        return '@' in email and '.' in email.split('@')[-1]
    
    @staticmethod
    def validate_isbn(isbn: str) -> bool:
        """Validate ISBN format (simplified)"""
        # Remove hyphens and spaces
        clean_isbn = isbn.replace('-', '').replace(' ', '')
        
        # Check if it's 10 or 13 digits
        return (len(clean_isbn) == 10 or len(clean_isbn) == 13) and clean_isbn.isdigit()
    
    @staticmethod
    def calculate_days_between(start_date: datetime.datetime, 
                             end_date: Optional[datetime.datetime] = None) -> int:
        """Calculate days between two dates"""
        if end_date is None:
            end_date = datetime.datetime.now()
        return (end_date - start_date).days
    
    @staticmethod
    def calculate_late_fee(issue_date: datetime.datetime, 
                          return_date: Optional[datetime.datetime] = None) -> float:
        """Calculate late fee based on issue date"""
        if return_date is None:
            return_date = datetime.datetime.now()
        
        days_issued = DataHelper.calculate_days_between(issue_date, return_date)
        
        if days_issued > settings.BORROWING_PERIOD_DAYS:
            late_days = days_issued - settings.BORROWING_PERIOD_DAYS
            return late_days * settings.DAILY_LATE_FEE
        
        return 0.0
    
    @staticmethod
    def format_currency(amount: float) -> str:
        """Format amount as currency"""
        return f"${amount:.2f}"
    
    @staticmethod
    def format_date(date: datetime.datetime, format_str: str = "%Y-%m-%d") -> str:
        """Format date as string"""
        return date.strftime(format_str)


class ExportHelper:
    """Helper class for data export operations"""
    
    @staticmethod
    def export_to_csv(data: List[Dict[str, Any]], filename: str) -> str:
        """Export data to CSV file"""
        if not data:
            raise ValueError("No data to export")
        
        # Create full file path
        timestamp = datetime.datetime.now().strftime(settings.EXPORT_DATE_FORMAT)
        full_filename = f"{filename}_{timestamp}.csv"
        file_path = os.path.join(settings.get_export_directory(), full_filename)
        
        # Write CSV file
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        return file_path
    
    @staticmethod
    def prepare_books_export(books: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare books data for export"""
        export_data = []
        for book in books:
            export_data.append({
                'Book ID': book.get('book_id', ''),
                'Title': book.get('title', ''),
                'Author': book.get('author', ''),
                'Category': book.get('category', ''),
                'ISBN': book.get('isbn', ''),
                'Status': book.get('availability_status', '').title(),
                'Created Date': book.get('created_date', '')[:10] if book.get('created_date') else ''
            })
        return export_data
    
    @staticmethod
    def prepare_members_export(members: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare members data for export"""
        export_data = []
        for member in members:
            export_data.append({
                'Member ID': member.get('member_id', ''),
                'Name': member.get('name', ''),
                'Email': member.get('email', ''),
                'Phone': member.get('phone', ''),
                'Join Date': member.get('join_date', '')[:10] if member.get('join_date') else ''
            })
        return export_data
    
    @staticmethod
    def prepare_transactions_export(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare transactions data for export"""
        export_data = []
        for trans in transactions:
            export_data.append({
                'Transaction ID': trans.get('transaction_id', ''),
                'Book Title': trans.get('book_title', ''),
                'Book Author': trans.get('book_author', ''),
                'Member Name': trans.get('member_name', ''),
                'Member Email': trans.get('member_email', ''),
                'Issue Date': trans.get('issue_date', '')[:10] if trans.get('issue_date') else '',
                'Return Date': trans.get('return_date', '')[:10] if trans.get('return_date') else 'Not Returned',
                'Status': trans.get('status', '').title(),
                'Late Fee': DataHelper.format_currency(trans.get('late_fee', 0.0))
            })
        return export_data


class StringHelper:
    """Helper class for string operations"""
    
    @staticmethod
    def truncate_string(text: str, max_length: int = 50) -> str:
        """Truncate string to specified length"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    @staticmethod
    def capitalize_words(text: str) -> str:
        """Capitalize each word in text"""
        return ' '.join(word.capitalize() for word in text.split())
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe file system usage"""
        invalid_chars = '<>:"/\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename.strip()
