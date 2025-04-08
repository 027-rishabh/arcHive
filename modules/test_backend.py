from db_operations import add_book, borrow_book, return_book, search_books

# Add a new book to the library
add_book('Harry Potter and the Philosopher\'s Stone', 'J.K. Rowling', 'Fantasy', 10)

# Borrow a book (user ID 1 borrows book ID 1)
if borrow_book(1, 1):
    print("Book borrowed successfully!")
else:
    print("Failed to borrow the book.")

# Search for a book by title
books = search_books('Harry Potter')
print("Search Results:", books)

# Return the book (assuming transaction ID 1)
if return_book(1):
    print("Book returned successfully!")
else:
    print("Failed to return the book.")

