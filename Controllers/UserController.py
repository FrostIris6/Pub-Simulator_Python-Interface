from tkinter import messagebox
from Models.UserModel import UserList

class UserController:
    """Manages user login, registration, and logout logic"""
    def __init__(self, user_model):
        self.user_model = user_model
        self.current_user = None  # Stores the currently logged-in user

    def login(self, identifier, password):
        """Handles user login"""
        result = self.user_model.login(identifier, password)

        if isinstance(result, UserList):  # Login successful
            self.current_user = result
            return "success"
        elif result == "locked":  # Account is locked
            return "locked"
        elif result.startswith("wrong_password"):
            return result  # Example: "wrong_password:3"
        else:
            return "not_found"  # User not found

    def register(self, name, password, user_type, contact):
        """Handles user registration"""
        new_user = self.user_model.register(name, password, user_type, contact)
        if new_user:
            messagebox.showinfo("Success", f"Registration successful! Your ID is {new_user.id}")

    def logout(self):
        """Handles user logout"""
        if self.current_user:
            messagebox.showinfo("Logged Out", "You have been logged out successfully.")
            self.current_user = None
