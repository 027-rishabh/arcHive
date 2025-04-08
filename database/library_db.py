import sqlite3

# Connect to SQLite database (this will create the database file if it doesn't exist)
conn = sqlite3.connect('library.db')
cursor = conn.cursor()

# Create Books Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Books (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Title TEXT NOT NULL,
    Author TEXT NOT NULL,
    Genre TEXT NOT NULL,
    Quantity INTEGER NOT NULL,
    Available INTEGER NOT NULL
)
''')

# Create Users Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Users (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Email TEXT NOT NULL,
    Phone TEXT NOT NULL,
    UserType TEXT NOT NULL
)
''')

# Create Transactions Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Transactions (
    TransactionID INTEGER PRIMARY KEY AUTOINCREMENT,
    UserID INTEGER NOT NULL,
    BookID INTEGER NOT NULL,
    IssueDate TEXT NOT NULL,
    ReturnDate TEXT,
    FOREIGN KEY (UserID) REFERENCES Users(ID),
    FOREIGN KEY (BookID) REFERENCES Books(ID)
)
''')

# Commit and close the connection
conn.commit()
conn.close()

print("Database and tables created successfully!")

