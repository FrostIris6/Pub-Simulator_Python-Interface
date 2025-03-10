import tkinter as tk

class CustomerView:
    """显示用户信息，并提供登录/注册/登出按钮"""
    def __init__(self, root, controller, login_view):
        self.root = root
        self.controller = controller
        self.login_view = login_view
        self.root.title("Customer View")
        root.geometry("960x600")

        # ** 创建顶部框架（放置用户身份和按钮） **
        self.top_frame = tk.Frame(root)
        self.top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.top_frame.grid_columnconfigure(0, weight=1)  # 让左侧内容（用户身份）占满

        # ** 用户身份显示 **
        self.user_label = tk.Label(self.top_frame, text=self.get_user_text(), font=("Arial", 12), anchor="w")
        self.user_label.grid(row=0, column=0, sticky="w")

        # ** 创建按钮框架 **
        self.button_frame = tk.Frame(self.top_frame)
        self.button_frame.grid(row=0, column=1, sticky="e")

        self.login_button = tk.Button(self.button_frame, text="Login", command=self.login)
        self.login_button.grid(row=0, column=0, padx=5)

        self.register_button = tk.Button(self.button_frame, text="Register", command=self.register)
        self.register_button.grid(row=0, column=1, padx=5)

        self.logout_button = tk.Button(self.button_frame, text="Logout", command=self.logout)
        self.logout_button.grid(row=0, column=2, padx=5)
        self.logout_button.grid_remove()  # 先隐藏

        # ** 创建用户信息框架（登录后才显示） **
        self.info_frame = tk.Frame(root)
        self.info_frame.grid(row=1, column=0, sticky="w", padx=10)
        self.info_frame.grid_remove()  # 先隐藏

        self.user_id_label = tk.Label(self.info_frame, font=("Arial", 12), anchor="w")
        self.user_id_label.grid(row=0, column=0, sticky="w")

        self.user_name_label = tk.Label(self.info_frame, font=("Arial", 12), anchor="w")
        self.user_name_label.grid(row=1, column=0, sticky="w")

        self.user_balance_label = tk.Label(self.info_frame, font=("Arial", 12), anchor="w")
        self.user_balance_label.grid(row=0, column=1, padx=20, sticky="w")

    def get_user_text(self):
        """返回用户信息"""
        return "VIP User" if self.controller.current_user else "Regular Customer"

    def update_ui(self):
        """更新用户信息和按钮显示"""
        if self.controller.current_user:
            # 用户已登录，更新信息
            self.user_label.config(text="Registered User")
            self.user_id_label.config(text=f"ID: {self.controller.current_user.id}")
            self.user_name_label.config(text=f"Name: {self.controller.current_user.name}")
            self.user_balance_label.config(text=f"Balance: ${self.controller.current_user.balance}")

            # 显示用户信息框架
            self.info_frame.grid()

            # 隐藏登录/注册按钮，显示登出按钮
            self.login_button.grid_remove()
            self.register_button.grid_remove()
            self.logout_button.grid()
        else:
            # 恢复默认状态
            self.user_label.config(text="Regular Customer")
            self.info_frame.grid_remove()

            # 显示登录/注册按钮，隐藏登出按钮
            self.logout_button.grid_remove()
            self.login_button.grid()
            self.register_button.grid()

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