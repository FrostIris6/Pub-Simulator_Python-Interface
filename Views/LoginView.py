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
        self.input_var = tk.StringVar(self.root)  # Declare input_var for dynamic input fields
        self.label = None
        self.entry = None
        self.dropdown = None
        self.back_btn = None
        self.next_btn = None
        self.cancel_btn = None
        self.y_offset = 30  # Vertical offset for input field and buttons

    def show(self):
        """Displays the popup window and starts the multi-step form."""
        print("show() - Creating top_window")
        self.top_window = Toplevel(self.root)
        self.top_window.title(self.steps[self.step]["title"])
        self.top_window.geometry("300x150")
        self.top_window.resizable(False, False)

        # Create label
        self.label = Label(self.top_window, text=self.steps[self.step]["label"])
        self.label.place(x=150, y=self.y_offset-10, anchor="center")  # Fixed position for label

        # Create input field for current step
        self.create_input_field()

        # Create buttons dynamically
        self.create_buttons()

        # Run the window to wait for user input
        self.top_window.grab_set()
        self.top_window.wait_window()
        print("show() - Exiting show() method")

    def create_buttons(self):
        """Creates Back, Next, and Cancel buttons."""
        # Destroy previous buttons if they exist
        if self.back_btn is not None:
            self.back_btn.destroy()
        if self.next_btn is not None:
            self.next_btn.destroy()
        if self.cancel_btn is not None:
            self.cancel_btn.destroy()

        # Buttons will be placed in fixed position below the input field
        button_y_offset = self.y_offset + 60  # Fixed Y position for buttons

        # Back button
        self.back_btn = Button(self.top_window, text="⬅ Back", command=self.back_step, state=tk.DISABLED)
        self.back_btn.place(x=100, y=button_y_offset, anchor="center")

        # Next button
        self.next_btn = Button(self.top_window, text="Next ➡", command=self.next_step)
        self.next_btn.place(x=200, y=button_y_offset, anchor="center")

        # Cancel button
        self.cancel_btn = Button(self.top_window, text="Cancel", command=self.cancel)
        self.cancel_btn.place(x=150, y=button_y_offset + 35, anchor="center")

    def create_input_field(self):
        """Create the input field dynamically for each step."""
        # Clear previous input field before creating the new one
        if self.entry is not None:
            self.entry.destroy()
        if self.dropdown is not None:
            self.dropdown.destroy()

        # Set y_offset for input fields based on the label position
        input_y_offset = self.y_offset + 20  # Adjust this value for spacing between label and input

        if self.steps[self.step]["field"] == "user_type":
            # Use OptionMenu for the "user_type" step
            options = ["customer", "bartender"]
            self.input_var.set(options[0])  # Default value
            self.dropdown = tk.OptionMenu(self.top_window, self.input_var, *options)
            self.dropdown.place(x=150, y=input_y_offset, anchor="center")  # Fixed position
        else:
            # Use Entry for other steps
            self.entry = Entry(self.top_window, textvariable=self.input_var)
            self.entry.place(x=150, y=input_y_offset, anchor="center")  # Fixed position

    def next_step(self):
        """Move to the next step."""
        #print(f"next_step() - Current step: {self.step}")
        val = self.input_var.get().strip()
        if not val:
            if self.steps[self.step]["field"] == "method":
                val = "empty"
            else:
                messagebox.showerror("error", "Please enter a value")
                return  # Don't submit if the input is empty

        # Record user input
        self.input_values[self.steps[self.step]["field"]] = val
        self.step += 1
        self.input_var.set("")  # Clear input field

        if self.step < len(self.steps):
            #print(f"next_step() - Moving to next step: {self.step}")
            self.label.config(text=self.steps[self.step]["label"])
            self.top_window.title(self.steps[self.step]["title"])

            # Dynamically update the input field
            self.create_input_field()
            # Dynamically update the buttons
            self.create_buttons()
            if self.steps[self.step]["field"] == "method":
                self.info_button() #show info button

        else:
            self.on_finish(self.input_values)

        self.update_back_button()

    def back_step(self):
        """Go back to the previous step."""
        #print(f"back_step() - Current step: {self.step}")
        if self.step > 0:
            self.step -= 1
            self.input_var.set(self.input_values.get(self.steps[self.step]["field"], ""))  # Restore previous value
            self.label.config(text=self.steps[self.step]["label"])
            self.top_window.title(self.steps[self.step]["title"])

            # Dynamically update the input field
            self.create_input_field()
            # Dynamically update the buttons
            self.create_buttons()

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

    def info_button(self):
        """ make a round information button"""
        radius = 10
        canvas = tk.Canvas(self.top_window, width=2 * radius, height=2 * radius)
        canvas.create_oval(0, 0, 2 * radius, 2 * radius, fill="blue", outline="black")
        canvas.create_text(radius, radius, text="i", font=("Arial", 12, "bold"), fill="white")
        canvas.bind("<Button-1>", lambda e: self.info())
        canvas.place(x=250, y=self.y_offset-10, anchor="center")

    def info(self):
        messagebox.showinfo("Attention", "If you don't want to use email or phone information, you can keep it empty and system will use user id instead.")


class LoginView:
    """Handles the login functionality, including password attempt tracking."""

    def __init__(self, root, controller, on_update_customer_view):
        self.root = root
        self.controller = controller
        self.on_update_customer_view = on_update_customer_view
        self.attempts = 0  # Track remaining attempts
        self.form = None  # Store form instance

    def login(self):
        """Trigger the login process."""
        steps = [
            {"title": "Login", "label": "Enter username, email, or phone:", "field": "identifier"},
            {"title": "Login", "label": "Enter password:", "field": "password"},
        ]

        def on_finish(input_values):
            #print("on_finish() - Checking credentials")
            result = self.controller.login(input_values["identifier"], input_values["password"])

            if result["status"] == "success":
                self.user_id = result["user_id"]  # store user_id
                self.user_type = result["type_of_user"]  # store type of user
                self.on_update_customer_view()
                messagebox.showinfo("Login Successful!", "Welcome!")
                self.form.top_window.destroy()
            elif result["status"] == "wrong_password":
                self.attempts = result["attempts"]
                #print(f"on_finish() - Login failed, attempts remaining: {self.attempts}")
                messagebox.showerror("Login Failed!", f"Password Incorrect! You can try {self.attempts} more times.")
                self.form.step -= 1  # Go back to password input step
                self.form.label.config(text=self.form.steps[self.form.step]["label"])
            elif result["status"] == "locked":
                messagebox.showerror("Account Locked","Your account has been locked due to too many failed attempts. Please contact the bartender!")
                self.form.top_window.destroy()  # Close the login window after too many attempts

            else:
                messagebox.showerror("Login Failed", "User not found.")
                self.form.top_window.destroy()

        #print("login() - Creating MultiStepForm")
        self.form = MultiStepForm(self.root, steps, on_finish)
        self.form.show()
        #print("login() - Exiting login() method")


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
            {"title": "Register", "label": "Enter email or phone:", "field": "method"},
        ]

        def on_finish(input_values):
            # Call the controller to register
            result = self.controller.register(input_values["username"], input_values["password"], input_values["user_type"], input_values["method"])

            if result["success"] == "yes":
                messagebox.showinfo("Registration Success!", f"Welcome! Your ID is {result['user_id']}")
                form.top_window.destroy()  # Close the form on success
            elif result["success"] == "Invalid":
                messagebox.showerror("Method Invalid!", "Keep it empty and system will use user id instead.")
                form.step -= 1  # Go back to password input step
                form.label.config(text=form.steps[form.step]["label"])
            else:
                # Show error message if registration failed
                messagebox.showerror("Registration Failed", result["message"])
                form.top_window.destroy()

        form = MultiStepForm(self.root, steps, on_finish)
        form.show()


class TableChoice:
    """Handles the table selection functionality."""

    def __init__(self, root, login_view, on_finish):
        self.root = root
        self.login_view = login_view  # Load LoginView to get user_id
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
            btn = tk.Button(top_window, text=f"Table {i}",
                            command=lambda table=i: self.on_table_selected(table, top_window))
            btn.pack(pady=5)

        # Keep the window in the foreground, waiting for user selection
        top_window.grab_set()
        top_window.wait_window()

    def on_table_selected(self, table, top_window):
        """When the user selects a table, store the choice and close the window."""
        self.table_choice = table
        user_id = self.login_view.user_id if self.login_view.user_id else "default"  # Get user_id directly from LoginView

        result = {"table_choice": self.table_choice, "user_id": user_id}
        self.on_finish(result)  # Callback function to return the selected data

        top_window.destroy()  # Close the window


