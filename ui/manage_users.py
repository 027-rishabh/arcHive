import tkinter as tk
from tkinter import messagebox
from db_operations import add_user, update_user, delete_user

# Function to handle adding a user
def add_user_ui():
    name = name_entry.get()
    email = email_entry.get()
    phone = phone_entry.get()
    user_type = user_type_var.get()
    
    if not name or not email or not phone or not user_type:
        messagebox.showerror("Error", "All fields are required!")
        return
    
    # Add the user to the database
    add_user(name, email, phone, user_type)
    messagebox.showinfo("Success", "User added successfully!")
    clear_form()

# Function to handle updating a user
def update_user_ui():
    user_id = user_id_entry.get()
    name = name_entry.get()
    email = email_entry.get()
    phone = phone_entry.get()
    user_type = user_type_var.get()
    
    if not user_id or not name or not email or not phone or not user_type:
        messagebox.showerror("Error", "All fields are required!")
        return
    
    # Update the user in the database
    update_user(int(user_id), name, email, phone, user_type)
    messagebox.showinfo("Success", "User updated successfully!")
    clear_form()

# Function to handle deleting a user
def delete_user_ui():
    user_id = user_id_entry.get()
    
    if not user_id:
        messagebox.showerror("Error", "User ID is required!")
        return
    
    # Delete the user from the database
    delete_user(int(user_id))
    messagebox.showinfo("Success", "User deleted successfully!")
    clear_form()

# Function to clear form fields
def clear_form():
    user_id_entry.delete(0, tk.END)
    name_entry.delete(0, tk.END)
    email_entry.delete(0, tk.END)
    phone_entry.delete(0, tk.END)

# Setup the Tkinter window
root = tk.Tk()
root.title("Manage Users")
root.geometry("500x400")

# Add form fields
user_id_label = tk.Label(root, text="User ID:")
user_id_label.pack(pady=5)
user_id_entry = tk.Entry(root)
user_id_entry.pack(pady=5)

name_label = tk.Label(root, text="Name:")
name_label.pack(pady=5)
name_entry = tk.Entry(root)
name_entry.pack(pady=5)

email_label = tk.Label(root, text="Email:")
email_label.pack(pady=5)
email_entry = tk.Entry(root)
email_entry.pack(pady=5)

phone_label = tk.Label(root, text="Phone:")
phone_label.pack(pady=5)
phone_entry = tk.Entry(root)
phone_entry.pack(pady=5)

user_type_label = tk.Label(root, text="User Type:")
user_type_label.pack(pady=5)
user_type_var = tk.StringVar(value="User")  # Default is User
user_type_menu = tk.OptionMenu(root, user_type_var, "User", "Admin")
user_type_menu.pack(pady=5)

# Add buttons for actions
add_button = tk.Button(root, text="Add User", font=("Arial", 12), command=add_user_ui)
add_button.pack(pady=10)

update_button = tk.Button(root, text="Update User", font=("Arial", 12), command=update_user_ui)
update_button.pack(pady=10)

delete_button = tk.Button(root, text="Delete User", font=("Arial", 12), command=delete_user_ui)
delete_button.pack(pady=10)

# Run the Tkinter loop
root.mainloop()

