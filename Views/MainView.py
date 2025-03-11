import tkinter as tk
from tkinter import Frame, Label, Button
from Views.OrderViewClass import OrderViewClass
from Views.MenuView import MenuView

class MainView:
    def __init__(self, root):
        self.root = root
        self.root.title("Main View")
        self.root.geometry("1280x800")  # Approximate resolution for a 10-inch tablet
        self.root.configure(bg="white")

        # Initialize the main layout
        self.create_layout()

    def create_layout(self):
        """Create the basic layout of the interface."""
        # Left sidebar for functional buttons
        self.sidebar = Frame(self.root, bg="#333", width=200, height=800)
        self.sidebar.pack(side="left", fill="y")

        # Buttons
        buttons = ["Wine", "Beer", "Cocktail", "Food", "Fridge"]
        for text in buttons:
            btn = Button(self.sidebar, text=text, bg="#555", fg="white", font=("Arial", 14), width=15)
            btn.pack(pady=10, padx=10)

        # Right-side user information & menu display area
        self.main_content = Frame(self.root, bg="white", width=1080, height=800)
        self.main_content.pack(side="right", fill="both", expand=True)

        # Upper-right section (User info display area)
        self.user_area = Frame(self.main_content, bg="#f0f0f0", height=150)
        self.user_area.pack(fill="x")

        self.user_label = Label(self.user_area, text="User Info Here", font=("Arial", 16), bg="#f0f0f0")
        self.user_label.pack(pady=20)

        # Lower-right section (Menu display area)
        self.menu_area = Frame(self.main_content, bg="white")
        self.menu_area.pack(fill="both", expand=True)

        # put order frame here
        self.order_frame = OrderViewClass(self.menu_area, None)
        # self.menu_label = Label(self.menu_area, text="Menu Content Here", font=("Arial", 16), bg="white")
        # self.menu_label.pack(pady=20)

    def set_user_view(self, view):
        """Set and display the user view."""
        if hasattr(self, "user_view"):
            self.user_view.destroy()  # Destroy the previous view before updating

        self.user_view = view
        self.user_view.pack(fill="both", expand=True)

    def set_menu_view(self, view):
        """Set the menu display area."""
        for widget in self.menu_area.winfo_children():
            widget.destroy()  # Clear old widgets
        view.pack(fill="both", expand=True)

