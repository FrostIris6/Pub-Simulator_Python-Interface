import tkinter as tk
from tkinter import Toplevel, Label, Entry, Button, StringVar

class LoginView:
    """处理登录、注册时的输入界面"""
    def __init__(self, root, controller, on_update_customer_view):
        self.root = root
        self.controller = controller
        self.on_update_customer_view = on_update_customer_view

    def get_input_with_back(self, prompts):
        """
        自定义窗口，支持多步输入和返回上一步
        :param prompts: 需要输入的字段列表
        :return: 用户输入的字典 (如果取消则返回 None)
        """
        input_values = {}
        step = 0  # 当前步骤索引

        def next_step():
            """进入下一步"""
            nonlocal step
            val = input_var.get().strip()
            if step < len(prompts):
                input_values[prompts[step]] = val
            step += 1

            if step < len(prompts):  # 继续下一步
                label.config(text=prompts[step])
                input_var.set("")
            else:
                top_window.destroy()  # 关闭窗口

        def back_step():
            """返回上一步"""
            nonlocal step
            if step > 0:
                step -= 1
                label.config(text=prompts[step])
                input_var.set(input_values.get(prompts[step], ""))

        def cancel():
            """用户取消输入"""
            nonlocal input_values
            input_values = None  # 标记取消
            top_window.destroy()

        # 创建输入窗口
        top_window = Toplevel(self.root)
        top_window.title("Input")
        top_window.geometry("300x150")
        top_window.resizable(False, False)
        top_window.protocol("WM_DELETE_WINDOW", cancel)  # 处理窗口关闭按钮 (X)

        input_var = StringVar()

        label = Label(top_window, text=prompts[step])
        label.pack(pady=5)

        entry = Entry(top_window, textvariable=input_var)
        entry.pack(pady=5)

        btn_frame = tk.Frame(top_window)
        btn_frame.pack(pady=10)

        back_btn = Button(btn_frame, text="← Back", command=back_step, state=tk.DISABLED)
        back_btn.pack(side=tk.LEFT, padx=5)

        next_btn = Button(btn_frame, text="Next", command=next_step)
        next_btn.pack(side=tk.LEFT, padx=5)

        cancel_btn = Button(top_window, text="Cancel", command=cancel)
        cancel_btn.pack(pady=5)

        def update_back_button():
            """更新 Back 按钮状态"""
            if step > 0:
                back_btn.config(state=tk.NORMAL)
            else:
                back_btn.config(state=tk.DISABLED)

        # 在每次操作后更新 Back 按钮状态
        def wrapped_next_step():
            next_step()
            update_back_button()

        def wrapped_back_step():
            back_step()
            update_back_button()

        next_btn.config(command=wrapped_next_step)
        back_btn.config(command=wrapped_back_step)

        # 运行窗口等待输入完成
        top_window.grab_set()
        top_window.wait_window()

        return input_values  # 返回输入结果（或 None）

    def login(self):
        """触发登录"""
        user_input = self.get_input_with_back(["Enter username, email, or phone:", "Enter password:"])
        if not user_input:
            return  # 用户取消，直接返回
        identifier, password = user_input.values()
        success = self.controller.login(identifier, password)

        if success:
            self.on_update_customer_view()  # 更新 CustomerView 界面

    def register(self):
        """触发注册"""
        user_input = self.get_input_with_back([
            "Enter username:",
            "Enter password:",
            "Enter user type (customer/bartender):",
            "Enter email or phone:"
        ])
        if not user_input:
            return  # 用户取消，直接返回
        name, password, user_type, contact = user_input.values()
        self.controller.register(name, password, user_type, contact)