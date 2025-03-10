from tkinter import messagebox

class UserController:
    """管理用户的登录、注册、登出逻辑"""
    def __init__(self, user_model):
        self.user_model = user_model
        self.current_user = None  # 存储当前登录用户

    def login(self, identifier, password):
        user = self.user_model.login(identifier, password)
        if user:
            self.current_user = user
            return True  # 登录成功
        else:
            messagebox.showerror("Login Failed", "Invalid credentials!")
            return False  # 登录失败

    def register(self, name, password, user_type, contact):
        new_user = self.user_model.register(name, password, user_type, contact)
        if new_user:
            messagebox.showinfo("Success", f"Registration successful! Your ID is {new_user.id}")

    def logout(self):
        """处理登出"""
        if self.current_user:
            messagebox.showinfo("Logged Out", "You have been logged out successfully.")
            self.current_user = None