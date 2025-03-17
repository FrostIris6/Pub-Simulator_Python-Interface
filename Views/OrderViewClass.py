# we might not need it if we integrate it in the other views

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox


class OrderViewClass:
    def __init__(self, root, controller, translation_controller=None):
        self.root = root
        self.controller = controller
        self.translation_controller = translation_controller  # 存储翻译控制器 / Store translation controller
        # self.root.title("Order")  # 设置窗口标题
        # self.root.geometry("560x700")  # 设置窗口大小 对于 Arial 字体，12 号字体的字符宽度大约为 7 像素。总共80个字符宽度

        self.total_price = 0

        # 创建 confirm_order 面板 / Create confirm_order panel
        self.confirm_panel = tk.Frame(root, width=560, height=100, bg="lightgray")
        self.confirm_panel.pack(side="bottom", fill="x", expand=False)  # 固定在底部 / Fixed at bottom
        self.init_confirm_order()

        # 创建 order_title 面板 / Create order_title panel
        self.order_title = tk.Frame(root, width=560, height=50, bg="lightgray")  # coordinate is supposed to be x=
        self.order_title.pack(side="top", fill="x", expand=False)  # 固定在顶部 / Fixed at top
        self.init_title_order()

        # 创建主 order 面板 / Create main order panel
        self.order_panel = tk.Frame(root, width=560, height=550, bg="white")
        self.order_panel.pack(side="top", fill="both", expand=True)

        # 如果提供了翻译控制器，更新文本 / If translation controller is provided, update texts
        if self.translation_controller:
            self.update_translations()

    def init_confirm_order(self):
        """创建确认订单面板和按钮"""
        # 清除现有内容
        for widget in self.confirm_panel.winfo_children():
            widget.destroy()

        # 获取"Sum"的翻译
        sum_text = "Sum: "
        if self.translation_controller:
            sum_text = self.translation_controller.get_text("views.order.sum", default=sum_text)

        # Sum 标签
        self.sum_label = tk.Label(self.confirm_panel, text=sum_text + str(self.total_price), font=("Arial", 16),
                                  bg="white")
        self.sum_label.grid(row=0, column=0, padx=10, pady=5)

        # 创建一个 Frame 用于放置按钮
        button_frame = tk.Frame(self.confirm_panel, width=560, bg="lightgray")
        button_frame.grid(row=1, column=0, pady=5)

        # 获取按钮文本的翻译
        place_order_text = "Place the order"
        table_confirm_text = "Table Confirmation"
        check_out_text = "Check Out"

        if self.translation_controller:
            place_order_text = self.translation_controller.get_text("views.order.place_order", default=place_order_text)
            table_confirm_text = self.translation_controller.get_text("views.order.table_confirmation",
                                                                      default=table_confirm_text)
            check_out_text = self.translation_controller.get_text("views.order.check_out", default=check_out_text)

        # 创建所有按钮
        checkout_button = tk.Button(button_frame, text=place_order_text, command=self.place_order, width=20, height=2)
        checkout_button.grid(row=0, column=0, padx=10)

        temp_button = tk.Button(button_frame, text=table_confirm_text, command=self.temp_button, width=20, height=2)
        temp_button.grid(row=0, column=1, padx=10)

        self.checkout_button = tk.Button(button_frame, text=check_out_text, command=self.checkout_window, width=20,
                                         height=2)
        self.checkout_button.grid(row=0, column=2, padx=10)

    def place_order(self):
        self.controller.place_order()

        # 获取订单确认消息的翻译 / Get translation for order confirmation message
        confirm_title = "Order Confirmation"
        confirm_message = "You have placed the order successfully"

        if self.translation_controller:
            confirm_title = self.translation_controller.get_text("dialogs.success", default=confirm_title)
            confirm_message = self.translation_controller.get_text("views.order.order_success", default=confirm_message)

        messagebox.showinfo(confirm_title, confirm_message)

    def init_title_order(self):
        # 获取"Order Details"的翻译 / Get translation for "Order Details"
        order_details_text = "Order Details"
        if self.translation_controller:
            order_details_text = self.translation_controller.get_text("views.order.order_details",
                                                                      default=order_details_text)

        # 订单标题 / Order title
        self.title_label = tk.Label(self.order_title, text=order_details_text, font=("Arial", 16), bg="white")
        self.title_label.pack(pady=10)

    def checkout_window(self):
        # 创建 Toplevel 窗口 / Create Toplevel window
        checkout_window = tk.Toplevel(self.root)

        # 获取"Check Out"的翻译 / Get translation for "Check Out"
        check_out_title = "Check Out"
        if self.translation_controller:
            check_out_title = self.translation_controller.get_text("views.order.check_out", default=check_out_title)

        checkout_window.title(check_out_title)

        # 设置窗口大小 / Set window size
        checkout_window.geometry("300x200")

        # 设置模态窗口 / Set modal window
        checkout_window.grab_set()

        # 获取订单金额消息的翻译 / Get translation for order amount message
        order_amount_text = "You order amount is "
        if self.translation_controller:
            order_amount_text = self.translation_controller.get_text("views.order.order_amount",
                                                                     default=order_amount_text)

        # 在新窗口中添加标签 / Add label to the new window
        label = tk.Label(checkout_window, text=order_amount_text + str(self.total_price), font=("Arial", 14))
        label.pack(pady=20)

        # 获取"Pay Now"的翻译 / Get translation for "Pay Now"
        pay_now_text = "Pay Now"
        if self.translation_controller:
            pay_now_text = self.translation_controller.get_text("views.order.pay_now", default=pay_now_text)

        # 在新窗口中添加按钮 / Add button to the new window
        button = tk.Button(checkout_window, text=pay_now_text, command=lambda: self.pay_successfully(checkout_window))
        button.pack(pady=10)

    def pay_successfully(self, window):
        window.destroy()
        # self.controller.checkout_order()
        self.controller.clear_order()
        self.update_items()

    def update_items(self):
        # 更新总价 / Update total price
        self.total_price = self.controller.order.total_price()

        # 获取"Sum"的翻译 / Get translation for "Sum"
        sum_text = "Sum: "
        if self.translation_controller:
            sum_text = self.translation_controller.get_text("views.order.sum", default=sum_text)

        self.sum_label.config(text=sum_text + str(self.total_price))

        print(self.order_panel.winfo_geometry())
        # 清空 order_panel / Clear order_panel
        for widget in self.order_panel.winfo_children():
            widget.destroy()

        # 显示订单项 / Display order items
        for i, item in enumerate(self.controller.order.items):
            # 创建 product 标签 / Create product label
            label = tk.Label(self.order_panel, text=item["product_id"], width=20, bg="white")
            label.grid(row=i + 1, column=0, sticky="w", padx=5, pady=2)

            # 创建 price 标签 / Create price label
            label = tk.Label(self.order_panel, text=item["price"], width=5, height=1, bg="white")
            label.grid(row=i + 1, column=1, sticky="w", padx=5, pady=2)

            # 创建 amount 标签 / Create amount label
            label = tk.Label(self.order_panel, text=item["amount"], width=5, height=1, bg="white")
            label.grid(row=i + 1, column=2, sticky="w", padx=5, pady=2)

            # 获取"notes"的翻译 / Get translation for "notes"
            notes_text = "notes"
            if self.translation_controller:
                notes_text = self.translation_controller.get_text("views.order.notes", default=notes_text)

            # 创建 notes 按钮 / Create notes button
            label = tk.Button(self.order_panel, text=notes_text, width=5, height=1, bg="lightblue",
                              command=lambda item=item: self.notes_dialog(item["product_id"], item["notes"]))
            label.grid(row=i + 1, column=4, sticky="w", padx=5, pady=2)

            # 创建 - 按钮 / Create - button
            button = tk.Button(self.order_panel, text="-", width=5, height=1, bg="lightgray",
                               command=lambda item=item: self.controller.minus1_item(item["product_id"]))
            button.grid(row=i + 1, column=5, sticky="e", padx=5, pady=2)

            # 创建 + 按钮 / Create + button
            button = tk.Button(self.order_panel, text="+", width=5, height=1, bg="lightgray",
                               command=lambda item=item: self.controller.plus1_item(item["product_id"]))
            button.grid(row=i + 1, column=6, sticky="e", padx=5, pady=2)

    def notes_dialog(self, product_id, current_note):
        # 获取"Current notes:"的翻译 / Get translation for "Current notes:"
        notes_title = "notes"
        current_notes_text = "Current notes:"

        if self.translation_controller:
            notes_title = self.translation_controller.get_text("views.order.notes", default=notes_title)
            current_notes_text = self.translation_controller.get_text("views.order.current_notes",
                                                                      default=current_notes_text)

        task = simpledialog.askstring(notes_title, current_notes_text + current_note)
        if task:  # 如果用户输入了内容 / If user enters content
            self.controller.add_notes(product_id, task)  # 调用 Controller 添加任务 / Call Controller to add task

            # 获取成功消息的翻译 / Get translation for success message
            success_title = "Success"
            success_message = "Notes added"

            if self.translation_controller:
                success_title = self.translation_controller.get_text("dialogs.success", default=success_title)
                success_message = self.translation_controller.get_text("views.order.notes_added",
                                                                       default=success_message)

            messagebox.showinfo(success_title, success_message)

    def temp_button(self):
        # 重要！临时措施，后面这里接入 table，点击 table 确定落座后，创建订单实例
        # Important! Temporary measure, later connect to table, create order instance after confirming table
        from Controllers.OrderController import OrderController
        self.controller = OrderController(self, 1, 1)

        # 获取确认消息的翻译 / Get translation for confirmation message
        notice_title = "Notice!"
        confirm_message = "You have confirm table successfully"

        if self.translation_controller:
            notice_title = self.translation_controller.get_text("dialogs.notice", default=notice_title)
            confirm_message = self.translation_controller.get_text("views.order.table_confirm_success",
                                                                   default=confirm_message)

        messagebox.showinfo(notice_title, confirm_message)
        self.update_items()

    def add_item_from_menu(self, product_index):
        self.controller.add_item(product_index)

    def update_translations(self):
        """更新界面中的所有翻译文本"""
        if not self.translation_controller:
            return

        # 重新创建所有按钮，而不是更新文本
        self.init_confirm_order()

        # 更新订单标题
        order_details_text = self.translation_controller.get_text("views.order.order_details", default="Order Details")
        self.title_label.config(text=order_details_text)

        # 刷新订单项
        if hasattr(self.controller, "order") and self.controller.order:
            self.update_items()