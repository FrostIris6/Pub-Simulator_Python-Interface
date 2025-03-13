#we might not need it if we integrate it in the other views


import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

class OrderViewClass:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        #self.root.title("Order")  # 设置窗口标题
        #self.root.geometry("560x700")  # 设置窗口大小 对于 Arial 字体，12 号字体的字符宽度大约为 7 像素。总共80个字符宽度

        self.total_price = 0

        # 创建 confirm_order 面板
        self.confirm_panel = tk.Frame(root, width=560, height=100, bg="lightgray")
        self.confirm_panel.pack(side="bottom", fill="x", expand=False)  # 固定在底部
        self.init_confirm_order()

        # 创建 order_title 面板
        self.order_title = tk.Frame(root, width=560, height=50, bg="lightgray")
        self.order_title.pack(side="top", fill="x", expand=False)  # 固定在顶部
        self.init_title_order()

        # 创建主 order 面板
        self.order_panel = tk.Frame(root, width=560, height=550, bg="white")
        self.order_panel.pack(side="top", fill="both", expand=True)

        # # 让窗口根据内容自动调整大小
        # self.root.update()  # 更新窗口布局
        # self.root.minsize(self.root.winfo_width(), self.root.winfo_height())  # 设置窗口最小大小

    def init_confirm_order(self):
        # Sum 标签（第一行，居右）
        self.sum_label = tk.Label(self.confirm_panel, text="Sum: " + str(self.total_price), font=("Arial", 16), bg="white")
        self.sum_label.grid(row=0, column=0, padx=10, pady=5)

        # 创建一个 Frame 用于放置按钮（第二行，居中）
        button_frame = tk.Frame(self.confirm_panel, width=560, bg="lightgray")
        button_frame.grid(row=1, column=0, pady=5)

        # 结算按钮
        checkout_button = tk.Button(button_frame, text="Place the order", command=self.checkout_window, width=20, height=2)
        checkout_button.grid(row=0, column=0, padx=10) #不知道为什么pack的side没用，grid的sticky也没用，不管怎么设置都是贴着放的

        # 临时设置桌号按钮
        temp_button = tk.Button(button_frame, text="Table Confirmation", command=self.temp_button, width=20, height=2)
        temp_button.grid(row=0, column=1, padx=10)

    def init_title_order(self):
        # 订单标题
        tk.Label(self.order_title, text="Order Details", font=("Arial", 16), bg="white").pack(pady=10)

    def checkout_window(self):
        # 创建 Toplevel 窗口
        checkout_window = tk.Toplevel(self.root)
        checkout_window.title("Check Out")

        # 设置窗口大小
        checkout_window.geometry("300x200")

        # 设置模态窗口
        checkout_window.grab_set()

        # 在新窗口中添加标签
        label = tk.Label(checkout_window, text="You order amount is " + str(self.total_price), font=("Arial", 14))
        label.pack(pady=20)

        # 在新窗口中添加按钮
        button = tk.Button(checkout_window, text="Pay Now", command=lambda: self.pay_successfully(checkout_window))
        button.pack(pady=10)

    def pay_successfully(self, window):
        window.destroy()
        self.controller.checkout_order()
        self.controller.clear_order()
        self.update_items()

    def update_items(self):
        self.total_price = self.controller.order.total_price()
        self.sum_label.config(text="Sum: " + str(self.total_price))

        # 清空 order_panel
        for widget in self.order_panel.winfo_children():
            widget.destroy()

        # 显示订单项
        for i, item in enumerate(self.controller.order.items):
            # 创建 product 标签
            label = tk.Label(self.order_panel, text=item["product_id"], width=20, bg="white")
            label.grid(row=i + 1, column=0, sticky="w", padx=5, pady=2)

            # 创建 price 标签
            label = tk.Label(self.order_panel, text=item["price"], width=5, height=1, bg="white")
            label.grid(row=i + 1, column=1, sticky="w", padx=5, pady=2)

            # 创建 amount 标签
            label = tk.Label(self.order_panel, text=item["amount"], width=5, height=1, bg="white")
            label.grid(row=i + 1, column=2, sticky="w", padx=5, pady=2)

            # 创建 specification 下拉框
            options = ["can", "bottle"]
            combobox = ttk.Combobox(self.order_panel, values=options, width=10, height=1)
            index = options.index(item["specification"])
            combobox.current(index)  # 设置默认选中项
            combobox.grid(row=i + 1, column=3, sticky="w", padx=5, pady=2)
            combobox.bind("<<ComboboxSelected>>", lambda event, item=item, combobox=combobox: self.controller.pick_spe(item["product_id"], combobox.get()))

            # 创建 notes 按钮
            label = tk.Button(self.order_panel, text="notes", width=5, height=1, bg="lightblue",
                              command=lambda item=item: self.notes_dialog(item["product_id"], item["note"]))
            label.grid(row=i + 1, column=4, sticky="w", padx=5, pady=2)

            # 创建 - 按钮
            button = tk.Button(self.order_panel, text="-", width=5, height=1, bg="lightgray",
                               command=lambda item=item: self.controller.minus1_item(item["product_id"]))
            button.grid(row=i + 1, column=5, sticky="e", padx=5, pady=2)

            # 创建 + 按钮
            button = tk.Button(self.order_panel, text="+", width=5, height=1, bg="lightgray",
                               command=lambda item=item: self.controller.plus1_item(item["product_id"]))
            button.grid(row=i + 1, column=6, sticky="e", padx=5, pady=2)

    def notes_dialog(self, product_id, current_note):
        task = simpledialog.askstring("notes", "Current notes:" + current_note)
        if task:  # 如果用户输入了内容
            self.controller.add_notes(product_id, task)  # 调用 Controller 添加任务
            messagebox.showinfo("Success", "Notes added")

    def temp_button(self):
        # 重要！临时措施，后面这里接入 table，点击 table 确定落座后，创建订单实例
        from Controllers.OrderController import OrderController
        self.controller = OrderController(self, 1, 1)
        self.update_items()