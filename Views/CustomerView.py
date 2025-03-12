import tkinter as tk

class CustomerView(tk.Frame):
    """Displays user information and provides login/register/logout buttons"""
    def __init__(self, parent, controller, login_view, register_view, table_choice_view):
        super().__init__(parent, bg="#f0f0f0")  # Inherit from Frame
        self.controller = controller
        self.login_view = login_view
        self.register_view = register_view
        self.table_choice_view = table_choice_view

        # ** Top frame (User identity + Buttons) **
        self.top_frame = tk.Frame(self, bg="#f0f0f0")
        self.top_frame.pack(fill="x", padx=10, pady=10)

        # ** User identity display **
        self.user_label = tk.Label(self.top_frame, text=self.get_user_text(), font=("Arial", 12), anchor="w", bg="#f0f0f0")
        self.user_label.pack(side="left")

        # ** Button frame **
        self.button_frame = tk.Frame(self.top_frame, bg="#f0f0f0")
        self.button_frame.pack(side="right")

        self.table_button = tk.Button(self.button_frame, text="Table", command=self.table_choice)
        self.table_button.pack(side="left", padx=5)

        self.login_button = tk.Button(self.button_frame, text="Login", command=self.login)
        self.login_button.pack(side="left", padx=5)

        self.register_button = tk.Button(self.button_frame, text="Register", command=self.register)
        self.register_button.pack(side="left", padx=5)

        self.logout_button = tk.Button(self.button_frame, text="Logout", command=self.logout)
        self.logout_button.pack(side="left", padx=5)
        self.logout_button.pack_forget()  # Initially hidden

        # ** User information frame (only shown after login) **
        self.info_frame = tk.Frame(self, bg="#f0f0f0")
        self.info_frame.pack(fill="x", padx=10)
        self.info_frame.pack_forget()  # Initially hidden

        self.user_id_label = tk.Label(self.info_frame, font=("Arial", 12), anchor="w", bg="#f0f0f0")
        self.user_id_label.pack(side="left", padx=10)

        self.user_name_label = tk.Label(self.info_frame, font=("Arial", 12), anchor="w", bg="#f0f0f0")
        self.user_name_label.pack(side="left", padx=10)

        self.user_balance_label = tk.Label(self.info_frame, font=("Arial", 12), anchor="w", bg="#f0f0f0")
        self.user_balance_label.pack(side="left", padx=20)

    def get_user_text(self):
        """Returns user identity information"""
        return "VIP User" if self.controller.current_user else "Regular Customer"

    def update_ui(self):
        """Updates user information and button display"""
        if self.controller.current_user:
            self.user_label.config(text="Registered User")
            self.user_id_label.config(text=f"ID: {self.controller.current_user.id}")
            self.user_name_label.config(text=f"Name: {self.controller.current_user.name}")
            self.user_balance_label.config(text=f"Balance: ${self.controller.current_user.balance}")

            self.info_frame.pack(fill="x")  # Show user info frame
            self.login_button.pack_forget()
            self.register_button.pack_forget()
            self.logout_button.pack()
        else:
            self.user_label.config(text="Regular Customer")
            self.info_frame.pack_forget()

            self.logout_button.pack_forget()
            self.login_button.pack(side="left", padx=5)
            self.register_button.pack(side="left", padx=5)

    def login(self):
        """Calls LoginView to handle login"""
        self.login_view.login()
        self.update_ui()

    def register(self):
        """Calls RegisterView to handle registration"""
        self.register_view.register()

    def logout(self):
        """Triggers logout process"""
        self.controller.logout()
        self.update_ui()

    def table_choice(self):
        """Opens the table selection window"""
        self.table_choice_view.show()
