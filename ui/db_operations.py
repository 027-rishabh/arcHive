import sqlite3
from datetime import date

# Connect to the SQLite database
def get_connection():
    return sqlite3.connect('../database/library.db')

# Add a new book to the database
def add_book(title, author, genre, quantity):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO Books (Title, Author, Genre, Quantity, Available)
    VALUES (?, ?, ?, ?, ?)
    ''', (title, author, genre, quantity, quantity))  # Quantity is initially set to Available
    conn.commit()
    conn.close()

# Update an existing book's details
def update_book(book_id, title, author, genre, quantity):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE Books
    SET Title = ?, Author = ?, Genre = ?, Quantity = ?, Available = ?
    WHERE ID = ?
    ''', (title, author, genre, quantity, quantity, book_id))
    conn.commit()
    conn.close()

# Delete a book from the database
def delete_book(book_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Books WHERE ID = ?', (book_id,))
    conn.commit()
    conn.close()

# Search for books by title, author, or genre
def search_books(search_term):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT * FROM Books
    WHERE Title LIKE ? OR Author LIKE ? OR Genre LIKE ?
    ''', ('%' + search_term + '%', '%' + search_term + '%', '%' + search_term + '%'))
    books = cursor.fetchall()
    conn.close()
    return books

# Add a new user to the database
def add_user(name, email, phone, user_type):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO Users (Name, Email, Phone, UserType)
    VALUES (?, ?, ?, ?)
    ''', (name, email, phone, user_type))
    conn.commit()
    conn.close()

# Update an existing user's details
def update_user(user_id, name, email, phone, user_type):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE Users
    SET Name = ?, Email = ?, Phone = ?, UserType = ?
    WHERE ID = ?
    ''', (name, email, phone, user_type, user_id))
    conn.commit()
    conn.close()

# Delete a user from the database
def delete_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Users WHERE ID = ?', (user_id,))
    conn.commit()
    conn.close()


# Borrow a book (Issue a book)
def borrow_book(user_id, book_id):
    conn = get_connection()
    cursor = conn.cursor()

    # Check if the book is available for borrowing
    cursor.execute('SELECT Available FROM Books WHERE ID = ?', (book_id,))
    book = cursor.fetchone()

    if book and book[0] > 0:
        # If available, create a transaction record and decrease available quantity
        cursor.execute('''
        INSERT INTO Transactions (UserID, BookID, IssueDate, ReturnDate)
        VALUES (?, ?, ?, ?)
        ''', (user_id, book_id, date.today().strftime('%Y-%m-%d'), None))

        cursor.execute('''
        UPDATE Books
        SET Available = Available - 1
        WHERE ID = ?
        ''', (book_id,))

        conn.commit()
        conn.close()
        return True  # Borrowing successful
    else:
        conn.close()
        return False  # Book not available for borrowing

# Return a book (Complete the transaction)
def return_book(transaction_id):
    conn = get_connection()
    cursor = conn.cursor()

    # Get the book ID and update available quantity
    cursor.execute('SELECT BookID FROM Transactions WHERE TransactionID = ?', (transaction_id,))
    transaction = cursor.fetchone()

    if transaction:
        book_id = transaction[0]
        cursor.execute('''
        UPDATE Transactions
        SET ReturnDate = ?
        WHERE TransactionID = ?
        ''', (date.today().strftime('%Y-%m-%d'), transaction_id))

        cursor.execute('''
        UPDATE Books
        SET Available = Available + 1
        WHERE ID = ?
        ''', (book_id,))

        conn.commit()
        conn.close()
        return True  # Return successful
    else:
        conn.close()
        return False  # Transaction not found

