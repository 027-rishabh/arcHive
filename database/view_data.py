import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('library.db')
cursor = conn.cursor()

# Fetch and display all books
cursor.execute('SELECT * FROM Books')
print("Books Table:")
for row in cursor.fetchall():
    print(row)

# Fetch and display all users
cursor.execute('SELECT * FROM Users')
print("\nUsers Table:")
for row in cursor.fetchall():
    print(row)

# Fetch and display all transactions
cursor.execute('SELECT * FROM Transactions')
print("\nTransactions Table:")
for row in cursor.fetchall():
    print(row)

# Close the connection
conn.close()

