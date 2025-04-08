import tkinter as tk
from tkinter import messagebox

# Function to handle login
def login():
    user_type = user_type_var.get()
    if user_type == "Admin":
        messagebox.showinfo("Login Successful", "Welcome Admin!")
        # Proceed to the main dashboard for Admin
        main_dashboard('Admin')
    elif user_type == "User":
        messagebox.showinfo("Login Successful", "Welcome User!")
        # Proceed to the main dashboard for User
        main_dashboard('User')
    else:
        messagebox.showerror("Login Failed", "Please select a valid user type.")

# Function to switch to the main dashboard
def main_dashboard(user_type):
    login_frame.pack_forget()  # Hide login screen
    dashboard_frame.pack(fill="both", expand=True)  # Show main dashboard
    
    welcome_label.config(text=f"Welcome, {user_type}!")

# Setup the main Tkinter window
root = tk.Tk()
root.title("Library Management System")
root.geometry("500x400")

# Create login screen frame
login_frame = tk.Frame(root)
login_frame.pack(fill="both", expand=True)

# Add label and user type selection
label = tk.Label(login_frame, text="Select User Type", font=("Arial", 14))
label.pack(pady=20)

user_type_var = tk.StringVar(value="")  # Default is empty
admin_radio = tk.Radiobutton(login_frame, text="Admin", variable=user_type_var, value="Admin", font=("Arial", 12))
admin_radio.pack(pady=5)
user_radio = tk.Radiobutton(login_frame, text="User", variable=user_type_var, value="User", font=("Arial", 12))
user_radio.pack(pady=5)

# Login button
login_button = tk.Button(login_frame, text="Login", font=("Arial", 14), command=login)
login_button.pack(pady=20)

# Main dashboard frame (hidden initially)
dashboard_frame = tk.Frame(root)

# Add a welcome label to the dashboard
welcome_label = tk.Label(dashboard_frame, text="", font=("Arial", 18))
welcome_label.pack(pady=30)

# Add options for managing books and users
manage_books_button = tk.Button(dashboard_frame, text="Manage Books", font=("Arial", 14))
manage_books_button.pack(pady=10)

manage_users_button = tk.Button(dashboard_frame, text="Manage Users", font=("Arial", 14))
manage_users_button.pack(pady=10)

manage_transactions_button = tk.Button(dashboard_frame, text="Manage Transactions", font=("Arial", 14))
manage_transactions_button.pack(pady=10)
# Add functionality to open the Manage Users, Manage Books, and Manage Transactions screens
def open_manage_books():
    import manage_books  # Open the Manage Books screen

def open_manage_users():
    import manage_users  # Open the Manage Users screen

def open_manage_transactions():
    import manage_transactions  # Open the Manage Transactions screen

# Update buttons in the dashboard to open respective screens
manage_books_button.config(command=open_manage_books)
manage_users_button.config(command=open_manage_users)
manage_transactions_button.config(command=open_manage_transactions)

# Run the main Tkinter loop
root.mainloop()

