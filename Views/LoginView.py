import tkinter as tk
from tkinter import Toplevel, Label, Entry, Button, StringVar, messagebox


class MultiStepForm:
    """Handles shared functionalities for Back, Next, Cancel buttons."""

    def __init__(self, root, steps, on_finish):
        self.root = root
        self.steps = steps  # List of steps, each step is a dictionary
        self.on_finish = on_finish
        self.step = 0  # Current step index
        self.input_values = {}  # Store user inputs
        self.top_window = None  # Store reference to the popup window

    def show(self):
        """Displays the popup window and starts the multi-step form."""
        print("show() - Creating top_window")
        self.top_window = Toplevel(self.root)
        self.top_window.title(self.steps[self.step]["title"])
        self.top_window.geometry("300x300")
        self.top_window.resizable(False, False)

        # Create input_var here to ensure it is bound to the correct window
        self.input_var = tk.StringVar(self.top_window)

        # Create label and input field
        self.label = Label(self.top_window, text=self.steps[self.step]["label"])
        self.label.pack(pady=5)

        # Dynamically create input field or dropdown
        if self.steps[self.step]["field"] == "user_type":
            # Use OptionMenu for the "user_type" step
            options = ["customer", "bartender"]
            self.dropdown = tk.OptionMenu(self.top_window, self.input_var, *options)
            self.dropdown.pack(pady=5)
        else:
            # Use Entry for other steps
            self.entry = Entry(self.top_window, textvariable=self.input_var)
            self.entry.pack(pady=5)

        # Button frame
        btn_frame = tk.Frame(self.top_window)
        btn_frame.pack(pady=10)

        # Back button
        self.back_btn = Button(btn_frame, text="← Back", command=self.back_step, state=tk.DISABLED)
        self.back_btn.pack(side=tk.LEFT, padx=5)

        # Next button
        self.next_btn = Button(btn_frame, text="Next", command=self.next_step)
        self.next_btn.pack(side=tk.LEFT, padx=5)

        # Cancel button
        cancel_btn = Button(self.top_window, text="Cancel", command=self.cancel)
        cancel_btn.pack(pady=5)

        # Update Back button's state
        self.update_back_button()

        # Run the window to wait for user input
        self.top_window.grab_set()
        self.top_window.wait_window()
        print("show() - Exiting show() method")

    def next_step(self):
        """Move to the next step."""
        print(f"next_step() - Current step: {self.step}")
        val = self.input_var.get().strip()
        if not val:
            return  # Don't submit if the input is empty

        # Record user input
        self.input_values[self.steps[self.step]["field"]] = val
        self.step += 1
        self.input_var.set("")  # Clear input field

        if self.step < len(self.steps):
            print(f"next_step() - Moving to next step: {self.step}")
            self.label.config(text=self.steps[self.step]["label"])
            self.top_window.title(self.steps[self.step]["title"])

        else:
            self.on_finish(self.input_values)

        self.update_back_button()

    def back_step(self):
        """Go back to the previous step."""
        print(f"back_step() - Current step: {self.step}")
        if self.step > 0:
            self.step -= 1
            self.input_var.set("")  # Clear input field
            self.label.config(text=self.steps[self.step]["label"])
            self.top_window.title(self.steps[self.step]["title"])

        self.update_back_button()

    def cancel(self):
        """Cancel the input and close the window."""
        print("cancel() - Closing the window")
        self.top_window.destroy()

    def update_back_button(self):
        """Update the state of the Back button."""
        if self.step > 0:
            if self.back_btn.winfo_exists():  # Check if the button still exists
                self.back_btn.config(state=tk.NORMAL)
        else:
            if self.back_btn.winfo_exists():  # Check if the button still exists
                self.back_btn.config(state=tk.DISABLED)


class LoginView:
    """Handles the login functionality, including password attempt tracking."""

    def __init__(self, root, controller, on_update_customer_view):
        self.root = root
        self.controller = controller
        self.on_update_customer_view = on_update_customer_view
        self.attempts = 5  # Track remaining attempts
        self.form = None  # Store form instance

    def login(self):
        """Trigger the login process."""
        print(f"login() - Attempts left: {self.attempts}")
        if self.attempts <= 0:
            print("login() - Account locked")
            messagebox.showerror("Account Locked", "Your account is locked due to too many failed attempts.")
            return

        steps = [
            {"title": "Login", "label": "Enter username, email, or phone:", "field": "identifier"},
            {"title": "Login", "label": "Enter password:", "field": "password"},
        ]

        def on_finish(input_values):
            print("on_finish() - Checking credentials")
            result = self.controller.login(input_values["identifier"], input_values["password"])

            if result == "success":
                print("on_finish() - Login successful")
                self.on_update_customer_view()
                messagebox.showinfo("Login Successful!", "Welcome!")
                self.attempts = 5
                self.form.top_window.destroy()
            else:
                print(f"on_finish() - Login failed, attempts remaining: {self.attempts}")
                self.attempts -= 1
                if self.attempts > 0:
                    messagebox.showerror("Login Failed!", f"Password Incorrect! You can try {self.attempts} more times.")
                    self.form.step -= 1  # Go back to password input step
                    self.form.label.config(text=self.form.steps[self.form.step]["label"])
                else:
                    print("on_finish() - Account locked due to too many attempts")
                    messagebox.showerror("Account Locked",
                                         "Your account has been locked due to too many failed attempts.")
                    self.form.top_window.destroy()  # Close the login window after too many attempts

        print("login() - Creating MultiStepForm")
        self.form = MultiStepForm(self.root, steps, on_finish)
        self.form.show()
        print("login() - Exiting login() method")


class RegisterView:
    """Handles the registration functionality."""

    def __init__(self, root, controller):
        self.root = root
        self.controller = controller

    def register(self):
        """Trigger the registration process."""
        steps = [
            {"title": "Register", "label": "Enter username:", "field": "username"},
            {"title": "Register", "label": "Enter password:", "field": "password"},
            {"title": "Register", "label": "Enter user type (customer/bartender):", "field": "user_type"},
            {"title": "Register", "label": "Enter email or phone:", "field": "contact"},
        ]

        def on_finish(input_values):
            self.controller.register(input_values["username"], input_values["password"], input_values["user_type"], input_values["contact"])
            messagebox.showinfo("Registration Success!", "Welcome! ")
            form.top_window.destroy()

        form = MultiStepForm(self.root, steps, on_finish)
        form.show()


class TableChoice:
    """Handles the table selection functionality."""

    def __init__(self, root, on_finish):
        self.root = root
        self.on_finish = on_finish
        self.table_choice = None  # Store the selected table

    def show(self):
        """Display the table selection interface."""
        top_window = tk.Toplevel(self.root)
        top_window.title("Table Choice")
        top_window.geometry("300x500")

        label = tk.Label(top_window, text="Which table are you sitting at?")
        label.pack(pady=20)

        # Create buttons for tables 1-6
        for i in range(1, 7):
            btn = tk.Button(top_window, text=f"Table {i}", command=lambda table=i: self.on_table_selected(table, top_window))
            btn.pack(pady=5)

        # Run the window to wait for user selection
        top_window.grab_set()
        top_window.wait_window()

    def on_table_selected(self, table, top_window):
        """When a table is selected, save the choice and close the window."""
        self.table_choice = table
        self.on_finish(self.table_choice)  # Call the on_finish callback and pass table_choice
        top_window.destroy()  # Close the window
