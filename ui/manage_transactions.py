import tkinter as tk
from tkinter import messagebox
from db_operations import borrow_book, return_book

# Function to handle borrowing a book
def borrow_book_ui():
    user_id = user_id_entry.get()
    book_id = book_id_entry.get()
    
    if not user_id or not book_id:
        messagebox.showerror("Error", "Both User ID and Book ID are required!")
        return
    
    # Borrow the book
    if borrow_book(int(user_id), int(book_id)):
        messagebox.showinfo("Success", "Book borrowed successfully!")
    else:
        messagebox.showerror("Error", "Book not available for borrowing!")
    clear_form()

# Function to handle returning a book
def return_book_ui():
    transaction_id = transaction_id_entry.get()
    
    if not transaction_id:
        messagebox.showerror("Error", "Transaction ID is required!")
        return
    
    # Return the book
    if return_book(int(transaction_id)):
        messagebox.showinfo("Success", "Book returned successfully!")
    else:
        messagebox.showerror("Error", "Transaction not found!")
    clear_form()

# Function to clear form fields
def clear_form():
    user_id_entry.delete(0, tk.END)
    book_id_entry.delete(0, tk.END)
    transaction_id_entry.delete(0, tk.END)

# Setup the Tkinter window
root = tk.Tk()
root.title("Manage Transactions")
root.geometry("500x400")

# Add form fields for borrowing and returning
transaction_id_label = tk.Label(root, text="Transaction ID:")
transaction_id_label.pack(pady=5)
transaction_id_entry = tk.Entry(root)
transaction_id_entry.pack(pady=5)

user_id_label = tk.Label(root, text="User ID:")
user_id_label.pack(pady=5)
user_id_entry = tk.Entry(root)
user_id_entry.pack(pady=5)

book_id_label = tk.Label(root, text="Book ID:")
book_id_label.pack(pady=5)
book_id_entry = tk.Entry(root)
book_id_entry.pack(pady=5)

# Add buttons for borrowing and returning books
borrow_button = tk.Button(root, text="Borrow Book", font=("Arial", 12), command=borrow_book_ui)
borrow_button.pack(pady=10)

return_button = tk.Button(root, text="Return Book", font=("Arial", 12), command=return_book_ui)
return_button.pack(pady=10)

# Run the Tkinter loop
root.mainloop()

