import tkinter as tk

class CustomerView(tk.Frame):
    """显示用户信息，并提供登录/注册/登出按钮"""
    def __init__(self, parent, controller, login_view):
        super().__init__(parent, bg="#f0f0f0")  # 继承 Frame
        self.controller = controller
        self.login_view = login_view

        # ** 顶部框架（用户身份 + 按钮） **
        self.top_frame = tk.Frame(self, bg="#f0f0f0")
        self.top_frame.pack(fill="x", padx=10, pady=10)

        # ** 用户身份显示 **
        self.user_label = tk.Label(self.top_frame, text=self.get_user_text(), font=("Arial", 12), anchor="w", bg="#f0f0f0")
        self.user_label.pack(side="left")

        # ** 按钮框架 **
        self.button_frame = tk.Frame(self.top_frame, bg="#f0f0f0")
        self.button_frame.pack(side="right")

        self.login_button = tk.Button(self.button_frame, text="Login", command=self.login)
        self.login_button.pack(side="left", padx=5)

        self.register_button = tk.Button(self.button_frame, text="Register", command=self.register)
        self.register_button.pack(side="left", padx=5)

        self.logout_button = tk.Button(self.button_frame, text="Logout", command=self.logout)
        self.logout_button.pack(side="left", padx=5)
        self.logout_button.pack_forget()  # 先隐藏

        # ** 用户信息框架（登录后才显示） **
        self.info_frame = tk.Frame(self, bg="#f0f0f0")
        self.info_frame.pack(fill="x", padx=10)
        self.info_frame.pack_forget()  # 先隐藏

        self.user_id_label = tk.Label(self.info_frame, font=("Arial", 12), anchor="w", bg="#f0f0f0")
        self.user_id_label.pack(side="left", padx=10)

        self.user_name_label = tk.Label(self.info_frame, font=("Arial", 12), anchor="w", bg="#f0f0f0")
        self.user_name_label.pack(side="left", padx=10)

        self.user_balance_label = tk.Label(self.info_frame, font=("Arial", 12), anchor="w", bg="#f0f0f0")
        self.user_balance_label.pack(side="left", padx=20)

    def get_user_text(self):
        """返回用户信息"""
        return "VIP User" if self.controller.current_user else "Regular Customer"

    def update_ui(self):
        """更新用户信息和按钮显示"""
        if self.controller.current_user:
            self.user_label.config(text="Registered User")
            self.user_id_label.config(text=f"ID: {self.controller.current_user.id}")
            self.user_name_label.config(text=f"Name: {self.controller.current_user.name}")
            self.user_balance_label.config(text=f"Balance: ${self.controller.current_user.balance}")

            self.info_frame.pack(fill="x")  # 显示用户信息框架
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
        """调用 LoginView 进行登录"""
        self.login_view.login()
        self.update_ui()

    def register(self):
        """调用 LoginView 进行注册"""
        self.login_view.register()

    def logout(self):
        """触发登出"""
        self.controller.logout()
        self.update_ui()
