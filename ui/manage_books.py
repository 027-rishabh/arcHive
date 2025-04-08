import tkinter as tk
from tkinter import messagebox
from db_operations import add_book, update_book, delete_book, search_books

# Function to handle adding a book
def add_book_ui():
    title = title_entry.get()
    author = author_entry.get()
    genre = genre_entry.get()
    quantity = quantity_entry.get()
    
    if not title or not author or not genre or not quantity:
        messagebox.showerror("Error", "All fields are required!")
        return
    
    # Add the book to the database
    add_book(title, author, genre, int(quantity))
    messagebox.showinfo("Success", "Book added successfully!")
    clear_form()

# Function to handle updating a book
def update_book_ui():
    book_id = book_id_entry.get()
    title = title_entry.get()
    author = author_entry.get()
    genre = genre_entry.get()
    quantity = quantity_entry.get()
    
    if not book_id or not title or not author or not genre or not quantity:
        messagebox.showerror("Error", "All fields are required!")
        return
    
    # Update the book in the database
    update_book(int(book_id), title, author, genre, int(quantity))
    messagebox.showinfo("Success", "Book updated successfully!")
    clear_form()

# Function to handle deleting a book
def delete_book_ui():
    book_id = book_id_entry.get()
    
    if not book_id:
        messagebox.showerror("Error", "Book ID is required!")
        return
    
    # Delete the book from the database
    delete_book(int(book_id))
    messagebox.showinfo("Success", "Book deleted successfully!")
    clear_form()

# Function to clear form fields
def clear_form():
    book_id_entry.delete(0, tk.END)
    title_entry.delete(0, tk.END)
    author_entry.delete(0, tk.END)
    genre_entry.delete(0, tk.END)
    quantity_entry.delete(0, tk.END)

# Setup the Tkinter window
root = tk.Tk()
root.title("Manage Books")
root.geometry("500x400")

# Add form fields
book_id_label = tk.Label(root, text="Book ID:")
book_id_label.pack(pady=5)
book_id_entry = tk.Entry(root)
book_id_entry.pack(pady=5)

title_label = tk.Label(root, text="Title:")
title_label.pack(pady=5)
title_entry = tk.Entry(root)
title_entry.pack(pady=5)

author_label = tk.Label(root, text="Author:")
author_label.pack(pady=5)
author_entry = tk.Entry(root)
author_entry.pack(pady=5)

genre_label = tk.Label(root, text="Genre:")
genre_label.pack(pady=5)
genre_entry = tk.Entry(root)
genre_entry.pack(pady=5)

quantity_label = tk.Label(root, text="Quantity:")
quantity_label.pack(pady=5)
quantity_entry = tk.Entry(root)
quantity_entry.pack(pady=5)

# Add buttons for actions
add_button = tk.Button(root, text="Add Book", font=("Arial", 12), command=add_book_ui)
add_button.pack(pady=10)

update_button = tk.Button(root, text="Update Book", font=("Arial", 12), command=update_book_ui)
update_button.pack(pady=10)

delete_button = tk.Button(root, text="Delete Book", font=("Arial", 12), command=delete_book_ui)
delete_button.pack(pady=10)

# Run the Tkinter loop
root.mainloop()

