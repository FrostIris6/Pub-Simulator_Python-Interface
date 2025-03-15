from tkinter import messagebox

class UserController:
    """Manages user login, registration, and logout logic"""
    def __init__(self, user_model):
        self.user_model = user_model
        self.current_user = None  # Stores the currently logged-in user
        self.menu_view = None  # Add this to store reference to MenuView
        
    def set_menu_view(self, menu_view):
        """Links UserController to MenuView"""
        self.menu_view = menu_view
        
    def get_current_user_role(self):
        if self.current_user is not None:
            return self.current_user.type_of_user
        else:
            return 'none'

    def login(self, identifier, password):
        """Handles user login"""
        result = self.user_model.login(identifier, password)

        if result["status"] == "success":  # Login successful
            self.current_user = result["use_list"]
            self.user_id = result["use_list"].id
            self.type_of_user = result["use_list"].type_of_user
            if hasattr(self, "menu_view"):  # Ensure menu_view exists
                self.menu_view.update_categories()
            return {"status": "success", "user_id": self.user_id, "type_of_user": self.type_of_user}  # return flag and type of user
            # Notify MenuView to update buttons
        elif result["status"] == "wrong_password":
            self.attempts = result["attempts"]
            return {"status": "wrong_password","attempts":self.attempts}  # Example: "wrong_password:3"
        elif result["status"] == "locked":
            return {"status": "locked"}  # User locked
        else:
            return {"status": "not_found"}  # User not found

    def register(self, name, password, user_type, contact):
        """Handles user registration"""
        new_user = self.user_model.register(name, password, user_type, contact)

        if new_user["status"] == "success":
            self.new_id = new_user["new_user"].id
            return {"success": "yes", "user_id": self.new_id }
        elif new_user["status"] == "invalid":
            return {"success": "Invalid"}
        else:
            return {"success": "no", "message": "Registration failed. Please check your input."}

    def logout(self):
        """Handles user logout"""
        if self.current_user:
            messagebox.showinfo("Logged Out", "You have been logged out successfully.")
            self.current_user = None
        if self.menu_view:
                self.menu_view.update_categories()  # Update menu when user logs out
