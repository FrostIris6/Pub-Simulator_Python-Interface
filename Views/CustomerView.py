# This section designs the user information view, incorporating user details and buttons.
# For regular users, shows "table""login""register" buttons
# For registered users(VIP customers and bartenders), shows "table""logout" buttons
#   In user info part, shows users' id, name, account balance
#   If the user is a bartender, the view will be combined with bartender-specific features, granting more privileges
#     such as managing stock，managing orders, handling payments, and viewing the current table status.

import tkinter as tk


class CustomerView(tk.Frame):
    """Displays user information and provides login/register/logout buttons"""

    def __init__(self, parent, controller, login_view, register_view, table_choice_view, translation_controller=None):
        super().__init__(parent, bg="#f0f0f0")  # Inherit from Frame
        self.controller = controller
        self.login_view = login_view
        self.register_view = register_view
        self.table_choice_view = table_choice_view
        self.translation_controller = translation_controller  # 存储翻译控制器 / Store translation controller

        # ** Top frame (User identity + Buttons) **
        self.top_frame = tk.Frame(self, bg="#f0f0f0")
        self.top_frame.pack(fill="x", padx=10, pady=10)

        # ** User identity display **
        self.user_label = tk.Label(self.top_frame, text=self.get_user_text(), font=("Arial", 12), anchor="w",
                                   bg="#f0f0f0")
        self.user_label.pack(side="left")

        # ** Button frame **
        self.button_frame = tk.Frame(self.top_frame, bg="#f0f0f0")
        self.button_frame.pack(side="right")

        # 创建各种按钮，文本稍后在update_translations中更新 / Create buttons, texts will be updated in update_translations
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

        # 如果有翻译控制器，更新文本 / If translation controller exists, update texts
        if self.translation_controller:
            self.update_translations()

    def get_user_text(self):
        """Returns user identity information"""
        if not self.controller.current_user:
            # 获取"Regular Customer"的翻译 / Get translation for "Regular Customer"
            text = "Regular Customer"
            if self.translation_controller:
                text = self.translation_controller.get_text("user_interface.regular_customer", default=text)
            return text
        else:
            # 获取"Registered User"的翻译 / Get translation for "Registered User"
            text = "VIP User"
            if self.translation_controller:
                text = self.translation_controller.get_text("user_interface.vip_user", default=text)
            return text

    def update_ui(self):
        """Updates user information and button display"""
        if self.controller.current_user:
            # 获取"Registered User"的翻译 / Get translation for "Registered User"
            user_text = "Registered User"
            if self.translation_controller:
                user_text = self.translation_controller.get_text("user_interface.registered_user", default=user_text)
            self.user_label.config(text=user_text)

            # 获取ID、Name和Balance的翻译 / Get translations for ID, Name and Balance
            id_text = "ID"
            name_text = "Name"
            balance_text = "Balance"
            if self.translation_controller:
                id_text = self.translation_controller.get_text("user_interface.id", default=id_text)
                name_text = self.translation_controller.get_text("user_interface.name", default=name_text)
                balance_text = self.translation_controller.get_text("user_interface.balance", default=balance_text)

            self.user_id_label.config(text=f"{id_text}: {self.controller.current_user.id}")
            self.user_name_label.config(text=f"{name_text}: {self.controller.current_user.name}")
            self.user_balance_label.config(text=f"{balance_text}: ${self.controller.current_user.balance}")

            self.info_frame.pack(fill="x")  # Show user info frame
            self.login_button.pack_forget()
            self.register_button.pack_forget()
            self.logout_button.pack()
        else:
            # 获取"Regular Customer"的翻译 / Get translation for "Regular Customer"
            user_text = "Regular Customer"
            if self.translation_controller:
                user_text = self.translation_controller.get_text("user_interface.regular_customer", default=user_text)
            self.user_label.config(text=user_text)

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

    def update_translations(self):
        """更新视图中的所有翻译文本 / Update all translated text in the interface"""
        if not self.translation_controller:
            return

        # 更新按钮文本 / Update button texts
        table_text = self.translation_controller.get_text("user_interface.table", default="Table")
        login_text = self.translation_controller.get_text("user_interface.login", default="Login")
        register_text = self.translation_controller.get_text("user_interface.register", default="Register")
        logout_text = self.translation_controller.get_text("user_interface.logout", default="Logout")

        self.table_button.config(text=table_text)
        self.login_button.config(text=login_text)
        self.register_button.config(text=register_text)
        self.logout_button.config(text=logout_text)

        # 更新用户信息 / Update user information
        self.update_ui()