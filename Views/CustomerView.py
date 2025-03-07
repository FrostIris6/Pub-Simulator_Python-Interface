import tkinter as tk
from tkinter import messagebox, simpledialog

class CustomerView:
    def __init__(self, master, controller):
        self.master = master
        self.controller = controller
        self.master.title("Pub Simulator")
        self.master.geometry("300x250")

        self.create_widgets()

    def create_widgets(self):
        """Create buttons."""
        self.login_button = tk.Button(self.master, text="Login", command=self.login)
        self.login_button.pack(pady=10)

        self.register_button = tk.Button(self.master, text="Register", command=self.register)
        self.register_button.pack(pady=10)

        self.bacon_button = tk.Button(self.master, text="Bacon", command=lambda: self.button_clicked("bacon"))
        self.bacon_button.pack(pady=10)

        self.beer_button = tk.Button(self.master, text="Beer", command=lambda: self.button_clicked("beer"))
        self.beer_button.pack(pady=10)

        self.wine_button = tk.Button(self.master, text="Wine", command=lambda: self.button_clicked("wine"))
        self.wine_button.pack(pady=10)

    def get_input(self, prompt):
        """Get user input."""
        user_input = simpledialog.askstring("Input", prompt)
        return user_input

    def display_message(self, message):
        """Display an information dialog box."""
        messagebox.showinfo("Information", message)

    def login(self):
        """Trigger login controller."""
        self.controller.login()

    def register(self):
        """Trigger register controller."""
        self.controller.register()

    def button_clicked(self, button_name):
        """Trigger an action when a button is clicked."""
        self.controller.button_clicked(button_name)


