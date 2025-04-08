import sqlite3
from datetime import date

# Connect to the SQLite database
conn = sqlite3.connect('library.db')
cursor = conn.cursor()

# Insert sample books
cursor.execute('''
INSERT INTO Books (Title, Author, Genre, Quantity, Available)
VALUES
    ('The Great Gatsby', 'F. Scott Fitzgerald', 'Fiction', 5, 5),
    ('1984', 'George Orwell', 'Dystopian', 3, 3),
    ('To Kill a Mockingbird', 'Harper Lee', 'Fiction', 4, 4)
''')

# Insert sample users
cursor.execute('''
INSERT INTO Users (Name, Email, Phone, UserType)
VALUES
    ('Alice Smith', 'alice@example.com', '123-456-7890', 'User'),
    ('Bob Johnson', 'bob@example.com', '987-654-3210', 'Admin')
''')

# Insert sample transactions (a user borrows a book)
cursor.execute('''
INSERT INTO Transactions (UserID, BookID, IssueDate, ReturnDate)
VALUES
    (1, 1, ?, NULL),  -- Alice borrows 'The Great Gatsby'
    (1, 2, ?, NULL)   -- Alice borrows '1984'
''', (date.today().strftime('%Y-%m-%d'), date.today().strftime('%Y-%m-%d')))

# Commit and close the connection
conn.commit()
conn.close()

print("Sample data inserted successfully!")

