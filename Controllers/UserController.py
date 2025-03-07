from Models.UserModel import UserModel

class UserController:
    def __init__(self, UserModel, CustomerView):
        self.UserModel = UserModel  # Model layer
        self.CustomerView = CustomerView  # View layer

    def login(self):
        """Handles user login (maximum of 5 attempts)."""
        attempts = 5  # Allows 5 attempts

        while attempts > 0:
            identifier = self.CustomerView.get_input("Enter your username, email, or phone: ")
            password = self.CustomerView.get_input("Enter your password: ")

            user = self.UserModel.login(identifier, password)

            if user:
                self.CustomerView.display_message(f"Welcome {user.name}! 🎉")
                self.UserModel.type_of_user_ident(user)  # Identify user type and navigate to the corresponding interface
                return  # Exit the method upon successful login

            attempts -= 1  # Decrease attempts on failure

            if attempts > 0:
                self.CustomerView.display_message(f"Login failed! You have {attempts} attempts left.")
            else:
                self.CustomerView.display_message("Too many failed attempts. Login locked! 🔒")
                return  # Completely exit the login process

    def register(self):
        """Handles user registration."""
        name = self.CustomerView.get_input("Enter username (or leave empty to use ID): ")
        password = self.CustomerView.get_input("Enter password: ")
        type_of_user = self.CustomerView.get_input("Enter user type (customer/bartender): ")
        method = self.CustomerView.get_input("Enter email or phone number (or leave empty to use ID): ")

        new_user = self.UserModel.register(name, password, type_of_user, method)

        if new_user:
            self.CustomerView.display_message(f"Registration successful! Your ID is {new_user.id}")

    def show_balance(self, user):
        """Displays the user's balance."""
        self.CustomerView.display_message(f"Your balance: {user.balance}")

    def logout(self, user):
        """Handles user logout."""
        self.UserModel.logout(user)
        self.CustomerView.display_message(f"{user.name}, you have been logged out.")

    def button_clicked(self, button_name):
        """Executes when a button is clicked."""
        if button_name in ["bacon", "beer", "wine"]:
            print(f"{button_name} button clicked. Redirecting to menu_function...")
            self.menu_function()
        else:
            print(f"{button_name} button clicked. No action assigned.")

    def menu_function(self):
        """Menu functionality (example)."""
        print("Entering Menu... 🍽️")
