import tkinter as tk
from tkinter import Toplevel, Label, Entry, Button, StringVar, messagebox


class MultiStepForm:
    """Handles shared functionalities for Back, Next, Cancel buttons."""

    def __init__(self, root, steps, on_finish, translation_controller=None):
        self.root = root
        self.steps = steps  # List of steps, each step is a dictionary
        self.on_finish = on_finish
        self.translation_controller = translation_controller  # 存储翻译控制器 / Store translation controller
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

        # 如果提供了翻译控制器，翻译步骤标题和标签 / If translation controller is provided, translate step titles and labels
        if self.translation_controller:
            self.translate_steps()

    def translate_steps(self):
        """翻译步骤中的标题和标签 / Translate titles and labels in steps"""
        for step in self.steps:
            # 获取标题和标签的翻译 / Get translations for title and label
            if "title_key" in step:
                step["title"] = self.translation_controller.get_text(step["title_key"], default=step["title"])
            if "label_key" in step:
                step["label"] = self.translation_controller.get_text(step["label_key"], default=step["label"])

    def show(self):
        """Displays the popup window and starts the multi-step form."""
        print("show() - Creating top_window")
        self.top_window = Toplevel(self.root)
        self.top_window.title(self.steps[self.step]["title"])
        self.top_window.geometry("300x150")
        self.top_window.resizable(False, False)

        # Create label
        self.label = Label(self.top_window, text=self.steps[self.step]["label"])
        self.label.place(x=150, y=self.y_offset - 10, anchor="center")  # Fixed position for label

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

        # 获取按钮文本的翻译 / Get translations for button texts
        back_text = "⬅ Back"
        next_text = "Next ➡"
        cancel_text = "Cancel"

        if self.translation_controller:
            back_text = self.translation_controller.get_text("user_interface.back_button", default=back_text)
            next_text = self.translation_controller.get_text("user_interface.next_button", default=next_text)
            cancel_text = self.translation_controller.get_text("user_interface.cancel", default=cancel_text)

        # Back button
        self.back_btn = Button(self.top_window, text=back_text, command=self.back_step, state=tk.DISABLED)
        self.back_btn.place(x=100, y=button_y_offset, anchor="center")

        # Next button
        self.next_btn = Button(self.top_window, text=next_text, command=self.next_step)
        self.next_btn.place(x=200, y=button_y_offset, anchor="center")

        # Cancel button
        self.cancel_btn = Button(self.top_window, text=cancel_text, command=self.cancel)
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
            # 获取用户类型选项的翻译 / Get translations for user type options
            customer_text = "customer"
            bartender_text = "bartender"

            if self.translation_controller:
                customer_text = self.translation_controller.get_text("user_interface.customer_role",
                                                                     default=customer_text)
                bartender_text = self.translation_controller.get_text("user_interface.bartender_role",
                                                                      default=bartender_text)

            # 显示的选项是翻译后的文本，但内部值保持不变 / Display translated options but keep internal values unchanged
            options_display = [customer_text, bartender_text]
            options_values = ["customer", "bartender"]

            # 创建下拉菜单变量 / Create dropdown menu variable
            self.option_var = StringVar(self.top_window)
            self.option_var.set(options_display[0])  # Default selection

            self.dropdown = tk.OptionMenu(self.top_window, self.option_var, *options_display)
            self.dropdown.place(x=150, y=input_y_offset, anchor="center")  # Fixed position

            # 确保正确映射选择的显示值到内部值 / Ensure correct mapping from display value to internal value
            def update_input_var(*args):
                index = options_display.index(self.option_var.get())
                self.input_var.set(options_values[index])

            self.option_var.trace("w", update_input_var)
            self.input_var.set(options_values[0])  # Set default value
        else:
            # Use Entry for other steps
            self.entry = Entry(self.top_window, textvariable=self.input_var)
            self.entry.place(x=150, y=input_y_offset, anchor="center")  # Fixed position

    def next_step(self):
        """Move to the next step."""
        # print(f"next_step() - Current step: {self.step}")
        val = self.input_var.get().strip()
        if not val:
            if self.steps[self.step]["field"] == "method":
                val = "empty"
            else:
                # 获取错误消息的翻译 / Get translation for error message
                error_title = "Error"
                error_message = "Please enter a value"
                if self.translation_controller:
                    error_title = self.translation_controller.get_text("dialogs.error", default=error_title)
                    error_message = self.translation_controller.get_text("dialogs.empty_value", default=error_message)

                messagebox.showerror(error_title, error_message)
                return  # Don't submit if the input is empty

        # Record user input
        self.input_values[self.steps[self.step]["field"]] = val
        self.step += 1
        self.input_var.set("")  # Clear input field

        if self.step < len(self.steps):
            # print(f"next_step() - Moving to next step: {self.step}")
            self.label.config(text=self.steps[self.step]["label"])
            self.top_window.title(self.steps[self.step]["title"])

            # Dynamically update the input field
            self.create_input_field()
            # Dynamically update the buttons
            self.create_buttons()
            if self.steps[self.step]["field"] == "method":
                self.info_button()  # show info button

        else:
            self.on_finish(self.input_values)

        self.update_back_button()

    def back_step(self):
        """Go back to the previous step."""
        # print(f"back_step() - Current step: {self.step}")
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
        canvas.place(x=250, y=self.y_offset - 10, anchor="center")

    def info(self):
        # 获取提示消息的翻译 / Get translation for info message
        info_title = "Attention"
        info_message = "If you don't want to use email or phone information, you can keep it empty and system will use user id instead."

        if self.translation_controller:
            info_title = self.translation_controller.get_text("dialogs.info", default=info_title)
            info_message = self.translation_controller.get_text("dialogs.email_phone_info", default=info_message)

        messagebox.showinfo(info_title, info_message)


class LoginView:
    """Handles the login functionality, including password attempt tracking."""

    def __init__(self, root, controller, on_update_customer_view, translation_controller=None):
        self.root = root
        self.controller = controller
        self.on_update_customer_view = on_update_customer_view
        self.translation_controller = translation_controller  # 存储翻译控制器 / Store translation controller
        self.attempts = 0  # Track remaining attempts
        self.form = None  # Store form instance

    def login(self):
        """Trigger the login process."""
        # 准备步骤数据，包含翻译键 / Prepare step data with translation keys
        steps = [
            {
                "title": "Login", "title_key": "user_interface.login",
                "label": "Enter username, email, or phone:", "label_key": "login_view.enter_identifier",
                "field": "identifier"
            },
            {
                "title": "Login", "title_key": "user_interface.login",
                "label": "Enter password:", "label_key": "login_view.enter_password",
                "field": "password"
            },
        ]

        def on_finish(input_values):
            # print("on_finish() - Checking credentials")
            result = self.controller.login(input_values["identifier"], input_values["password"])

            if result["status"] == "success":
                self.user_id = result["user_id"]  # store user_id
                self.user_type = result["type_of_user"]  # store type of user
                self.on_update_customer_view()

                # 获取成功消息的翻译 / Get translation for success message
                success_title = "Login Successful!"
                success_message = "Welcome!"

                if self.translation_controller:
                    success_title = self.translation_controller.get_text("login_view.success_title",
                                                                         default=success_title)
                    success_message = self.translation_controller.get_text("login_view.welcome_message",
                                                                           default=success_message)

                messagebox.showinfo(success_title, success_message)
                self.form.top_window.destroy()
            elif result["status"] == "wrong_password":
                self.attempts = result["attempts"]
                # print(f"on_finish() - Login failed, attempts remaining: {self.attempts}")

                # 获取密码错误消息的翻译 / Get translation for wrong password message
                error_title = "Login Failed!"
                error_message = f"Password Incorrect! You can try {self.attempts} more times."

                if self.translation_controller:
                    error_title = self.translation_controller.get_text("login_view.failure_title", default=error_title)
                    error_pattern = self.translation_controller.get_text(
                        "login_view.wrong_password_message",
                        default="Password Incorrect! You can try {attempts} more times."
                    )
                    error_message = error_pattern.format(attempts=self.attempts)

                messagebox.showerror(error_title, error_message)
                self.form.step -= 1  # Go back to password input step
                self.form.label.config(text=self.form.steps[self.form.step]["label"])
            elif result["status"] == "locked":
                # 获取账户锁定消息的翻译 / Get translation for account locked message
                locked_title = "Account Locked"
                locked_message = "Your account has been locked due to too many failed attempts. Please contact the bartender!"

                if self.translation_controller:
                    locked_title = self.translation_controller.get_text("login_view.locked_title", default=locked_title)
                    locked_message = self.translation_controller.get_text("login_view.locked_message",
                                                                          default=locked_message)

                messagebox.showerror(locked_title, locked_message)
                self.form.top_window.destroy()  # Close the login window after too many attempts

            else:
                # 获取用户未找到消息的翻译 / Get translation for user not found message
                not_found_title = "Login Failed"
                not_found_message = "User not found."

                if self.translation_controller:
                    not_found_title = self.translation_controller.get_text("login_view.failure_title",
                                                                           default=not_found_title)
                    not_found_message = self.translation_controller.get_text("login_view.user_not_found",
                                                                             default=not_found_message)

                messagebox.showerror(not_found_title, not_found_message)
                self.form.top_window.destroy()

        # print("login() - Creating MultiStepForm")
        self.form = MultiStepForm(self.root, steps, on_finish, self.translation_controller)
        self.form.show()
        # print("login() - Exiting login() method")


class RegisterView:
    """Handles the registration functionality."""

    def __init__(self, root, controller, translation_controller=None):
        self.root = root
        self.controller = controller
        self.translation_controller = translation_controller  # 存储翻译控制器 / Store translation controller

    def register(self):
        """Trigger the registration process."""
        # 准备步骤数据，包含翻译键 / Prepare step data with translation keys
        steps = [
            {
                "title": "Register", "title_key": "user_interface.register",
                "label": "Enter username:", "label_key": "register_view.enter_username",
                "field": "username"
            },
            {
                "title": "Register", "title_key": "user_interface.register",
                "label": "Enter password:", "label_key": "register_view.enter_password",
                "field": "password"
            },
            {
                "title": "Register", "title_key": "user_interface.register",
                "label": "Enter user type (customer/bartender):", "label_key": "register_view.enter_user_type",
                "field": "user_type"
            },
            {
                "title": "Register", "title_key": "user_interface.register",
                "label": "Enter email or phone:", "label_key": "register_view.enter_contact",
                "field": "method"
            },
        ]

        def on_finish(input_values):
            # Call the controller to register
            result = self.controller.register(input_values["username"], input_values["password"],
                                              input_values["user_type"], input_values["method"])

            if result["success"] == "yes":
                # 获取注册成功消息的翻译 / Get translation for registration success message
                success_title = "Registration Success!"
                success_pattern = "Welcome! Your ID is {user_id}"

                if self.translation_controller:
                    success_title = self.translation_controller.get_text("register_view.success_title",
                                                                         default=success_title)
                    success_pattern = self.translation_controller.get_text(
                        "register_view.success_message",
                        default="Welcome! Your ID is {user_id}"
                    )

                success_message = success_pattern.format(user_id=result['user_id'])
                messagebox.showinfo(success_title, success_message)
                form.top_window.destroy()  # Close the form on success
            elif result["success"] == "Invalid":
                # 获取无效方法消息的翻译 / Get translation for invalid method message
                invalid_title = "Method Invalid!"
                invalid_message = "Keep it empty and system will use user id instead."

                if self.translation_controller:
                    invalid_title = self.translation_controller.get_text("register_view.invalid_method_title",
                                                                         default=invalid_title)
                    invalid_message = self.translation_controller.get_text("register_view.invalid_method_message",
                                                                           default=invalid_message)

                messagebox.showerror(invalid_title, invalid_message)
                form.step -= 1  # Go back to password input step
                form.label.config(text=form.steps[form.step]["label"])
            else:
                # 获取注册失败消息的翻译 / Get translation for registration failure message
                failure_title = "Registration Failed"

                if self.translation_controller:
                    failure_title = self.translation_controller.get_text("register_view.failure_title",
                                                                         default=failure_title)

                # Show error message if registration failed
                messagebox.showerror(failure_title, result["message"])
                form.top_window.destroy()

        form = MultiStepForm(self.root, steps, on_finish, self.translation_controller)
        form.show()


class TableChoice:
    """Handles the table selection functionality."""

    def __init__(self, root, login_view, on_finish, translation_controller=None):
        self.root = root
        self.login_view = login_view  # Load LoginView to get user_id
        self.on_finish = on_finish
        self.translation_controller = translation_controller  # 存储翻译控制器 / Store translation controller
        self.table_choice = None  # Store the selected table

    def show(self):
        """Display the table selection interface."""
        top_window = tk.Toplevel(self.root)

        # 获取窗口标题的翻译 / Get translation for window title
        title_text = "Table Choice"
        if self.translation_controller:
            title_text = self.translation_controller.get_text("table_choice.title", default=title_text)

        top_window.title(title_text)
        top_window.geometry("300x500")

        # 获取标签文本的翻译 / Get translation for label text
        label_text = "Which table are you sitting at?"
        if self.translation_controller:
            label_text = self.translation_controller.get_text("table_choice.prompt", default=label_text)

        label = tk.Label(top_window, text=label_text)
        label.pack(pady=20)

        # 获取"Table"的翻译 / Get translation for "Table"
        table_text = "Table"
        if self.translation_controller:
            table_text = self.translation_controller.get_text("views.bartender.table_text", default=table_text)

        # Create buttons for tables 1-6
        for i in range(1, 7):
            btn = tk.Button(top_window, text=f"{table_text} {i}",
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