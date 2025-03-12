import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
from datetime import datetime

# Add Controllers directory to system path to be able to import controller module
controllers_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Controllers")
sys.path.append(controllers_path)

# Import controller from Controllers directory
from Order_bar_controller import EnhancedOrderController, initialize_test_data

# 订单卡片组件 view card set (view part start here)
class OrderCard(tk.Frame):
    def __init__(self, parent, order, on_click=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.order = order
        self.on_click = on_click

        # 设置卡片样式
        self.config(relief=tk.RAISED, borderwidth=1, padx=10, pady=10)
        self.bind("<Button-1>", self._on_click)

        # 计算总金额
        total = 0
        for item in order["breakdown"]:
            total += item["price"] * item["amount"]

        # 卡片标题 - 桌号
        title_frame = tk.Frame(self)
        title_frame.pack(fill=tk.X, pady=(0, 5))

        tk.Label(title_frame, text=f"Table: {order['table_id']}",
                 font=("Arial", 12, "bold")).pack(side=tk.LEFT)

        # 订单时间
        tk.Label(self, text=f"Time: {order['transaction_time']}",
                 font=("Arial", 10)).pack(anchor=tk.W)

        # 订单状态
        is_completed = True
        for item in order["breakdown"]:
            if not item.get("is_paid", False):
                is_completed = False
                break

        status = "Completed" if is_completed else "In Progress"
        status_color = "#27ae60" if is_completed else "#e74c3c"  # 绿色表示完成，红色表示进行中

        status_frame = tk.Frame(self)
        status_frame.pack(fill=tk.X, pady=5)

        tk.Label(status_frame, text=f"Status: ",
                 font=("Arial", 10)).pack(side=tk.LEFT)
        tk.Label(status_frame, text=status, fg=status_color,
                 font=("Arial", 10, "bold")).pack(side=tk.LEFT)

        # 总价
        tk.Label(self, text=f"Total: ¥{total:.2f}",
                 font=("Arial", 11)).pack(anchor=tk.E)

    # 处理点击事件
    def _on_click(self, event):
        if self.on_click:
            self.on_click(self.order["transaction_id"])


# 订单列表视图 order list view
class OrderListView(ttk.Frame):
    def __init__(self, parent, controller, main_window):
        super().__init__(parent)
        self.controller = controller
        self.main_window = main_window
        self.create_widgets()
        self.load_orders()

    # 创建界面组件
    def create_widgets(self):
        # 顶部工具栏
        toolbar = tk.Frame(self, bg="#f5f6fa")
        toolbar.pack(fill=tk.X, pady=5)

        ttk.Button(toolbar, text="Refresh", command=self.load_orders).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="History", command=self.show_history).pack(side=tk.LEFT, padx=5)

        # 标题
        title_frame = tk.Frame(self, bg="#f5f6fa")
        title_frame.pack(fill=tk.X, pady=10)
        tk.Label(title_frame, text="Current Orders", font=("Arial", 14, "bold"),
                 bg="#f5f6fa").pack(pady=5)

        # 创建滚动区域
        self.canvas = tk.Canvas(self, bg="white")
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # 创建卡片容器
        self.cards_frame = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window((0, 0), window=self.cards_frame, anchor="nw")

        # 绑定调整大小事件
        self.cards_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

    # 调整滚动区域
    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    # 调整内部框架宽度
    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas.find_withtag("all")[0], width=event.width)

    # 加载订单数据
    def load_orders(self):
        # 清除现有卡片
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        orders = self.controller.get_active_orders()

        if not orders:
            # 显示无订单信息
            tk.Label(self.cards_frame, text="No active orders",
                     font=("Arial", 12), bg="white").pack(pady=20)
            return

        # 添加订单卡片
        for order in orders:
            def on_card_click(tid=order["transaction_id"]):
                self.main_window.show_detail_view(tid)

            card = OrderCard(
                self.cards_frame,
                order,
                on_click=on_card_click,
                bg="white",
                width=350  # 固定宽度
            )
            card.pack(fill=tk.X, pady=5, padx=10, ipadx=5, ipady=5)

    # 显示历史订单
    def show_history(self):
        self.main_window.show_history_view()


# 历史订单详情视图 history view
class HistoryDetailView(ttk.Frame):
    def __init__(self, parent, controller, order, main_window):
        super().__init__(parent)
        self.controller = controller
        self.order = order
        self.main_window = main_window
        self.create_widgets()
        self.refresh_display()

    # 创建界面组件
    def create_widgets(self):
        # 顶部导航栏
        header = tk.Frame(self, bg="#f5f6fa")
        header.pack(fill=tk.X)

        # 返回按钮
        back_btn = ttk.Button(header, text="← Back", command=self.return_to_history)
        back_btn.pack(side=tk.LEFT, padx=10, pady=10)

        # 桌号标题
        title_frame = tk.Frame(header, bg="#f5f6fa")
        title_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20)

        tk.Label(title_frame, text=f"Table {self.order['table_id']}",
                 font=("Arial", 14, "bold"), bg="#f5f6fa").pack(side=tk.LEFT)

        # 创建滚动区域
        self.canvas = tk.Canvas(self, bg="white")
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # 创建详情容器
        self.detail_frame = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window((0, 0), window=self.detail_frame, anchor="nw")

        # 绑定调整大小事件
        def on_frame_configure(e):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        self.detail_frame.bind("<Configure>", on_frame_configure)

        def on_canvas_configure(e):
            self.canvas.itemconfig(self.canvas.find_withtag("all")[0], width=e.width)

        self.canvas.bind("<Configure>", on_canvas_configure)

        # 底部区域 - 左对齐总额和返回按钮
        self.bottom_frame = tk.Frame(self, bg="#f5f6fa")
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # 创建左侧区域
        bottom_left = tk.Frame(self.bottom_frame, bg="#f5f6fa")
        bottom_left.pack(side=tk.LEFT, padx=15, pady=10, fill=tk.Y)

        # 总金额
        self.total_label = tk.Label(bottom_left, text="Total: ¥0.00",
                                    font=("Arial", 14, "bold"), bg="#f5f6fa")
        self.total_label.pack(anchor=tk.W)

        # 返回按钮
        ttk.Button(bottom_left, text="Back",
                   command=self.return_to_history).pack(anchor=tk.W, pady=5)

    # 返回历史订单列表
    def return_to_history(self):
        self.main_window.show_history_view()

    # 刷新数据
    def refresh_data(self):
        self.order = self.controller.get_order_by_transaction(self.order["transaction_id"])
        self.refresh_display()

    # 刷新显示
    def refresh_display(self):
        # 清除现有内容
        for widget in self.detail_frame.winfo_children():
            widget.destroy()

        # 按类别组织商品
        categories = {}

        # 翻译字典
        translations = {
            "酒水": "Wine & Spirits",
            "啤酒": "Beer",
            "鸡尾酒": "Cocktail",
            "食品": "Food",
            "玻璃杯": "Glass",
            "瓶装": "Bottle",
            "威士忌": "Whiskey"
        }

        for item in self.order["breakdown"]:
            cat_name = "Drinks"  # 默认类别

            # 翻译规格
            if "specification" in item:
                spec = item["specification"]
                # 检查是否需要翻译
                for cn, en in translations.items():
                    if cn in spec:
                        spec = spec.replace(cn, en)
                # 更新规格
                item["specification"] = spec

                # 按规格分类
                spec_lower = spec.lower()
                if "wine" in spec_lower or "whisky" in spec_lower or "whiskey" in spec_lower:
                    cat_name = "Wine & Spirits"
                elif "beer" in spec_lower:
                    cat_name = "Beer"
                elif "cocktail" in spec_lower:
                    cat_name = "Cocktails"
                elif "food" in spec_lower or "snack" in spec_lower:
                    cat_name = "Food"

            if cat_name not in categories:
                categories[cat_name] = []
            categories[cat_name].append(item)

        # 显示每个类别
        for cat_name in categories:
            items = categories[cat_name]
            if items:  # 只显示有商品的类别
                self.create_item_section(cat_name, items)

        # 计算总金额
        total = 0
        for item in self.order["breakdown"]:
            total += item["price"] * item["amount"]
        self.total_label.config(text=f"Total: ¥{total:.2f}")

    # 创建商品分类部分
    def create_item_section(self, category, items):
        # 创建类别标题框架
        section_frame = tk.Frame(self.detail_frame, bg="white")
        section_frame.pack(fill=tk.X, pady=5)

        # 类别标题
        tk.Label(section_frame, text=category,
                 font=("Arial", 12, "bold"), bg="white").pack(anchor=tk.W, padx=10, pady=5)

        # 遍历类别中的商品
        for item in items:
            # 商品状态
            status = "Paid" if item.get("is_paid", False) else ""
            bg_color = "#ebf5eb" if item.get("is_paid", False) else "white"

            # 创建商品框架
            item_frame = tk.Frame(self.detail_frame, bg=bg_color)
            item_frame.pack(fill=tk.X, padx=5, pady=2)

            # 左侧信息
            left_frame = tk.Frame(item_frame, bg=bg_color)
            left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=8)

            # 商品名称和规格
            product_name = f"Item {item['product_id']}"
            if "specification" in item and item["specification"]:
                product_name = item["specification"]

            tk.Label(left_frame, text=product_name,
                     font=("Arial", 11), bg=bg_color).pack(anchor=tk.W)

            # 显示折扣信息
            if "discount_percentage" in item:
                discount_info = f"Discount {item['discount_percentage']}%"
                tk.Label(left_frame, text=discount_info, fg="#e67e22",
                         font=("Arial", 9), bg=bg_color).pack(anchor=tk.W)

            # 右侧信息
            right_frame = tk.Frame(item_frame, bg=bg_color)
            right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=8)

            # 显示价格
            price_text = f"¥ {item['price']:.2f}"
            tk.Label(right_frame, text=price_text,
                     font=("Arial", 11), bg=bg_color).pack(side=tk.RIGHT)

            # 显示数量
            qty_frame = tk.Frame(right_frame, bg=bg_color)
            qty_frame.pack(side=tk.RIGHT, padx=20)

            tk.Label(qty_frame, text=f"× {item['amount']}",
                     font=("Arial", 11), bg=bg_color).pack()


# 订单详情视图
class OrderDetailView(ttk.Frame):
    def __init__(self, parent, controller, order, main_window):
        super().__init__(parent)
        self.controller = controller
        self.order = order
        self.main_window = main_window
        self.selected_items = {}  # 用于存储选中的商品
        self.create_widgets()
        self.refresh_display()

    # 创建界面组件
    def create_widgets(self):
        # 顶部导航栏
        header = tk.Frame(self, bg="#f5f6fa")
        header.pack(fill=tk.X)

        # 返回按钮
        back_btn = ttk.Button(header, text="← Back",
                              command=self.main_window.show_list_view)
        back_btn.pack(side=tk.LEFT, padx=10, pady=10)

        # 桌号标题
        title_frame = tk.Frame(header, bg="#f5f6fa")
        title_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20)

        tk.Label(title_frame, text=f"Table {self.order['table_id']}",
                 font=("Arial", 14, "bold"), bg="#f5f6fa").pack(side=tk.LEFT)

        # 添加和删除按钮
        btn_frame = tk.Frame(header, bg="#f5f6fa")
        btn_frame.pack(side=tk.RIGHT, padx=10)

        # 添加按钮(+图标)
        add_btn = tk.Button(btn_frame, text="+", font=("Arial", 12, "bold"),
                            width=2, command=self.show_add_item_dialog,
                            bg="#2ecc71", fg="white", relief=tk.FLAT)
        add_btn.pack(side=tk.RIGHT, padx=5, pady=10)

        # 删除按钮(-图标)
        del_btn = tk.Button(btn_frame, text="−", font=("Arial", 12, "bold"),
                            width=2, command=self.delete_selected_items,
                            bg="#e74c3c", fg="white", relief=tk.FLAT)
        del_btn.pack(side=tk.RIGHT, padx=5, pady=10)

        # 折扣面板
        self.discount_panel = tk.Frame(self, bg="#f5f6fa", padx=10, pady=5)
        self.discount_panel.pack(fill=tk.X)

        # 折扣标题
        tk.Label(self.discount_panel, text="Apply Discount:",
                 font=("Arial", 11, "bold"), bg="#f5f6fa").pack(side=tk.LEFT, padx=5)

        # 折扣率输入框
        tk.Label(self.discount_panel, text="Rate (%)", bg="#f5f6fa").pack(side=tk.LEFT, padx=5)
        self.discount_entry = ttk.Entry(self.discount_panel, width=6)
        self.discount_entry.pack(side=tk.LEFT, padx=2)
        self.discount_entry.insert(0, "10")  # 默认10%折扣

        # 应用折扣按钮
        self.apply_discount_btn = ttk.Button(self.discount_panel, text="Apply Discount",
                                             command=self.apply_selected_discount)
        self.apply_discount_btn.pack(side=tk.LEFT, padx=10)

        # 取消选择按钮
        self.clear_selection_btn = ttk.Button(self.discount_panel, text="Clear Selection",
                                              command=self.clear_item_selection)
        self.clear_selection_btn.pack(side=tk.LEFT, padx=5)

        # 主操作按钮
        self.toolbar = tk.Frame(self)
        self.toolbar.pack(fill=tk.X, pady=5)

        ttk.Button(self.toolbar, text="Partial Checkout", command=self.show_checkout_dialog).pack(side=tk.LEFT, padx=5)

        # 创建滚动区域
        self.canvas = tk.Canvas(self, bg="white")
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # 创建详情容器
        self.detail_frame = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window((0, 0), window=self.detail_frame, anchor="nw")

        # 绑定调整大小事件
        def on_frame_configure(e):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        self.detail_frame.bind("<Configure>", on_frame_configure)

        def on_canvas_configure(e):
            self.canvas.itemconfig(self.canvas.find_withtag("all")[0], width=e.width)

        self.canvas.bind("<Configure>", on_canvas_configure)

        # 底部结账区域
        self.bottom_frame = tk.Frame(self, bg="#f5f6fa")
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # 创建左侧区域
        bottom_left = tk.Frame(self.bottom_frame, bg="#f5f6fa")
        bottom_left.pack(side=tk.LEFT, padx=15, pady=10, fill=tk.Y)

        # 总金额信息
        self.total_label = tk.Label(bottom_left, text="To Pay: ¥0.00",
                                    font=("Arial", 14, "bold"), bg="#f5f6fa")
        self.total_label.pack(anchor=tk.W)

        # 按钮区域
        button_frame = tk.Frame(bottom_left, bg="#f5f6fa")
        button_frame.pack(anchor=tk.W, pady=5)

        # 结账按钮
        self.checkout_btn = ttk.Button(button_frame, text="Checkout",
                                       command=self.full_checkout)
        self.checkout_btn.pack(side=tk.LEFT, padx=5)

        # 取消按钮
        self.cancel_btn = ttk.Button(button_frame, text="Cancel",
                                     command=self.cancel_checkout)
        self.cancel_btn.pack(side=tk.LEFT, padx=5)

        # 返回按钮
        ttk.Button(button_frame, text="Back",
                   command=self.main_window.show_list_view).pack(side=tk.LEFT, padx=5)

    # 创建商品分类部分
    def create_item_section(self, category, items):
        # 创建类别标题框架
        section_frame = tk.Frame(self.detail_frame, bg="white")
        section_frame.pack(fill=tk.X, pady=5)

        # 类别标题
        tk.Label(section_frame, text=category,
                 font=("Arial", 12, "bold"), bg="white").pack(anchor=tk.W, padx=10, pady=5)

        # 遍历类别中的商品
        for item in items:
            # 商品状态
            is_paid = item.get("is_paid", False)
            status = "Paid" if is_paid else ""
            bg_color = "#ebf5eb" if is_paid else "white"

            # 创建商品框架
            item_frame = tk.Frame(self.detail_frame, bg=bg_color)
            item_frame.pack(fill=tk.X, padx=5, pady=2)

            # 选择复选框 - 只为未付款商品显示
            if not is_paid:
                # 创建选择变量
                item_id = str(item["product_id"])
                if item_id not in self.selected_items:
                    self.selected_items[item_id] = tk.BooleanVar(value=False)

                check = ttk.Checkbutton(item_frame, variable=self.selected_items[item_id])
                check.pack(side=tk.LEFT, padx=2)

            # 左侧信息
            left_frame = tk.Frame(item_frame, bg=bg_color)
            left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5 if not is_paid else 10, pady=8)

            # 商品名称和规格
            product_name = f"Item {item['product_id']}"
            if "specification" in item and item["specification"]:
                product_name = item["specification"]

            tk.Label(left_frame, text=product_name,
                     font=("Arial", 11), bg=bg_color).pack(anchor=tk.W)

            # 显示折扣信息
            if "discount_percentage" in item:
                discount_info = f"Discount {item['discount_percentage']}%"
                tk.Label(left_frame, text=discount_info, fg="#e67e22",
                         font=("Arial", 9), bg=bg_color).pack(anchor=tk.W)

            # 右侧信息
            right_frame = tk.Frame(item_frame, bg=bg_color)
            right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=8)

            # 显示价格
            price_text = f"¥ {item['price']:.2f}"
            tk.Label(right_frame, text=price_text,
                     font=("Arial", 11), bg=bg_color).pack(side=tk.RIGHT)

            # 显示数量
            qty_frame = tk.Frame(right_frame, bg=bg_color)
            qty_frame.pack(side=tk.RIGHT, padx=20)

            tk.Label(qty_frame, text=f"× {item['amount']}",
                     font=("Arial", 11), bg=bg_color).pack()

    # 应用选定的折扣
    def apply_selected_discount(self):
        try:
            # 获取折扣率
            discount_rate = float(self.discount_entry.get()) / 100
            if discount_rate < 0 or discount_rate > 1:
                raise ValueError

            # 收集选中的商品ID
            selected_ids = []
            for pid, var in self.selected_items.items():
                if var.get():
                    selected_ids.append(pid)

            if not selected_ids:
                messagebox.showwarning("Warning", "Please select at least one item to apply discount")
                return

            # 应用折扣
            self.order = self.controller.apply_discount(self.order, discount_rate, selected_ids)
            self.controller.save_order(self.order)
            self.refresh_display()
            messagebox.showinfo("Success",
                                f"Discount of {discount_rate * 100:.1f}% applied to {len(selected_ids)} items")

            # 清除选择
            self.clear_item_selection()

        except ValueError:
            messagebox.showerror("Error", "Please enter a valid discount rate between 0-100")

    # 清除所有项目的选择
    def clear_item_selection(self):
        for pid in self.selected_items:
            var = self.selected_items[pid]
            var.set(False)

    # 刷新数据
    def refresh_data(self):
        self.order = self.controller.get_order_by_transaction(self.order["transaction_id"])
        self.refresh_display()

    # 刷新显示
    def refresh_display(self):
        # 保存当前选择状态
        current_selection = {}
        for pid in self.selected_items:
            var = self.selected_items[pid]
            current_selection[pid] = var.get()

        # 清除现有内容
        for widget in self.detail_frame.winfo_children():
            widget.destroy()

        # 重置选择状态字典
        self.selected_items = {}
        for pid in current_selection:
            selected = current_selection[pid]
            self.selected_items[pid] = tk.BooleanVar(value=selected)

        # 按类别组织商品
        categories = {}

        # 筛选未付款商品
        unpaid_items = []
        for item in self.order["breakdown"]:
            if not item.get("is_paid", False):
                unpaid_items.append(item)

        # 翻译字典
        translations = {
            "酒水": "Wine & Spirits",
            "啤酒": "Beer",
            "鸡尾酒": "Cocktail",
            "食品": "Food",
            "玻璃杯": "Glass",
            "瓶装": "Bottle",
            "威士忌": "Whiskey"
        }

        for item in unpaid_items:
            cat_name = "Drinks"  # 默认类别

            # 翻译规格
            if "specification" in item:
                spec = item["specification"]
                # 检查是否需要翻译
                for cn, en in translations.items():
                    if cn in spec:
                        spec = spec.replace(cn, en)
                # 更新规格
                item["specification"] = spec

                # 按规格分类
                spec_lower = spec.lower()
                if "wine" in spec_lower or "whisky" in spec_lower or "whiskey" in spec_lower:
                    cat_name = "Wine & Spirits"
                elif "beer" in spec_lower:
                    cat_name = "Beer"
                elif "cocktail" in spec_lower:
                    cat_name = "Cocktails"
                elif "food" in spec_lower or "snack" in spec_lower:
                    cat_name = "Food"

            if cat_name not in categories:
                categories[cat_name] = []
            categories[cat_name].append(item)

        # 已付款商品
        checked_out_items = []
        for item in self.order["breakdown"]:
            if item.get("is_paid", False):
                checked_out_items.append(item)

        if checked_out_items:
            # 翻译已付款商品
            for item in checked_out_items:
                if "specification" in item:
                    spec = item["specification"]
                    for cn, en in translations.items():
                        if cn in spec:
                            spec = spec.replace(cn, en)
                    item["specification"] = spec
            categories["Paid Items"] = checked_out_items

        # 显示每个类别
        for cat_name in categories:
            items = categories[cat_name]
            if items:  # 只显示有商品的类别
                self.create_item_section(cat_name, items)

        # 计算总金额
        total = 0
        for item in self.order["breakdown"]:
            if not item.get("is_paid", False):
                total += item["price"] * item["amount"]

        # 更新总金额显示
        self.total_label.config(text=f"To Pay: ¥{total:.2f}")

    # 全部结账
    def full_checkout(self):
        unpaid_ids = []
        for item in self.order["breakdown"]:
            if not item.get("is_paid", False):
                unpaid_ids.append(str(item["product_id"]))

        if not unpaid_ids:
            messagebox.showinfo("Info", "All items are already paid")
            return

        self.order, total = self.controller.partial_checkout(self.order, unpaid_ids)
        self.controller.save_order(self.order)
        self.refresh_display()
        messagebox.showinfo("Success", f"Successfully checked out ¥{total:.2f}")

    # 显示结账对话框
    def show_checkout_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Select Items to Checkout")
        dialog.geometry("350x400")
        dialog.transient(self)  # 设为父窗口的临时窗口
        dialog.grab_set()  # 模态对话框
        dialog.resizable(False, False)  # 禁止调整大小

        # 滚动区域
        main_frame = tk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

        # 加载可选商品
        check_vars = []
        unpaid_items = []
        for item in self.order["breakdown"]:
            if not item.get("is_paid", False):
                unpaid_items.append(item)

        # 更新总金额显示
        def update_total_display():
            selected_ids = []
            for pid, var in check_vars:
                if var.get():
                    selected_ids.append(pid)

            total = 0
            for item in unpaid_items:
                if str(item["product_id"]) in selected_ids:
                    total += item["price"] * item["amount"]
            total_label.config(text=f"To Pay: ¥{total:.2f}")

        if not unpaid_items:
            tk.Label(scroll_frame, text="All items are already paid",
                     font=("Arial", 12)).pack(pady=20)
        else:
            tk.Label(scroll_frame, text="Select items to checkout:",
                     font=("Arial", 11, "bold")).pack(anchor=tk.W, padx=10, pady=10)

            for item in unpaid_items:
                var = tk.BooleanVar(value=True)  # 默认选中

                # 显示折扣信息
                discount_info = ""
                if "discount_percentage" in item:
                    discount_info = f" (Discount {item['discount_percentage']}%)"

                item_frame = tk.Frame(scroll_frame)
                item_frame.pack(fill=tk.X, padx=10, pady=2)

                cb = ttk.Checkbutton(item_frame, variable=var, command=update_total_display)
                cb.pack(side=tk.LEFT)

                # 商品信息
                product_name = f"Item {item['product_id']}"
                if "specification" in item and item["specification"]:
                    product_name = item["specification"]

                info_text = f"{product_name} - ¥{item['price']} × {item['amount']}{discount_info}"
                tk.Label(item_frame, text=info_text).pack(side=tk.LEFT, padx=5)

                check_vars.append((str(item["product_id"]), var))

        def confirm_checkout():
            if not check_vars:
                dialog.destroy()
                return

            selected_ids = []
            for pid, var in check_vars:
                if var.get():
                    selected_ids.append(pid)

            if not selected_ids:
                messagebox.showwarning("Warning", "Please select at least one item")
                return

            self.order, total = self.controller.partial_checkout(self.order, selected_ids)
            self.controller.save_order(self.order)
            self.refresh_display()
            dialog.destroy()
            messagebox.showinfo("Success", f"Successfully checked out ¥{total:.2f}")

        # 底部区域
        bottom_frame = tk.Frame(dialog, bg="#f5f6fa")
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # 结账总金额显示
        total_label = tk.Label(bottom_frame, text="To Pay: ¥0.00",
                               font=("Arial", 12, "bold"), bg="#f5f6fa")
        total_label.pack(side=tk.LEFT, padx=15, pady=10)

        # 初始化总金额显示
        if unpaid_items:
            update_total_display()

        # 按钮区域
        button_frame = tk.Frame(bottom_frame, bg="#f5f6fa")
        button_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Confirm", command=confirm_checkout).pack(side=tk.LEFT, padx=5)

        # 设置滚动区域
        scroll_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    # 取消结账 - 重置所有商品的付款状态
    def cancel_checkout(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to reset all item payment status?"):
            for item in self.order["breakdown"]:
                item["is_paid"] = False
            self.controller.save_order(self.order)
            self.refresh_display()
            messagebox.showinfo("Success", "All payment status has been reset")

    # 显示添加商品对话框
    def show_add_item_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Add New Item")
        dialog.geometry("300x250")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        # 输入字段
        fields = [
            ("Product ID:", "product_id"),
            ("Specification:", "specification"),
            ("Price:", "price"),
            ("Quantity:", "amount")
        ]
        entries = {}

        # 标题
        tk.Label(dialog, text="Add New Item",
                 font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        # 创建输入框
        for i in range(len(fields)):
            label, field = fields[i]
            tk.Label(dialog, text=label).grid(row=i + 1, column=0, padx=15, pady=8, sticky=tk.W)
            entry = ttk.Entry(dialog, width=25)
            entry.grid(row=i + 1, column=1, padx=5, pady=8, sticky=tk.W)
            entries[field] = entry

        def add_item():
            try:
                new_item = {
                    "product_id": int(entries["product_id"].get()),
                    "specification": entries["specification"].get(),
                    "price": float(entries["price"].get()),
                    "amount": int(entries["amount"].get()),
                    "is_paid": False
                }
            except ValueError:
                messagebox.showerror("Error", "Please enter valid values")
                return

            self.order["breakdown"].append(new_item)
            self.controller.save_order(self.order)
            self.refresh_display()
            dialog.destroy()
            messagebox.showinfo("Success", "Item added")

        # 按钮区域
        button_frame = tk.Frame(dialog)
        button_frame.grid(row=len(fields) + 1, column=0, columnspan=2, pady=15)

        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Add", command=add_item).pack(side=tk.LEFT, padx=5)

    # 删除选中的商品
    def delete_selected_items(self):
        # 筛选未付款的商品
        unpaid_items = []
        for item in self.order["breakdown"]:
            if not item.get("is_paid", False):
                unpaid_items.append(item)

        if not unpaid_items:
            messagebox.showinfo("Information", "There are no unpaid items to delete. Paid items cannot be deleted.")
            return

        # 创建删除对话框
        dialog = tk.Toplevel(self)
        dialog.title("Select Items to Delete")
        dialog.geometry("350x400")
        dialog.transient(self)
        dialog.grab_set()

        # 主框架
        main_frame = tk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 滚动区域
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

        # 加载可删除商品
        check_vars = []

        tk.Label(scroll_frame, text="Select unpaid items to delete:",
                 font=("Arial", 11, "bold")).pack(anchor=tk.W, padx=10, pady=10)

        # 显示已付款商品的注释
        paid_items_count = len(self.order["breakdown"]) - len(unpaid_items)
        if paid_items_count > 0:
            tk.Label(scroll_frame,
                     text=f"Note: {paid_items_count} paid items are not shown as they cannot be deleted.",
                     fg="#e74c3c", font=("Arial", 9)).pack(anchor=tk.W, padx=10, pady=(0, 10))

        # 添加可删除商品
        for item in unpaid_items:
            var = tk.BooleanVar(value=False)

            item_frame = tk.Frame(scroll_frame)
            item_frame.pack(fill=tk.X, padx=10, pady=2)

            cb = ttk.Checkbutton(item_frame, variable=var)
            cb.pack(side=tk.LEFT)

            # 商品信息
            product_name = f"Item {item['product_id']}"
            if "specification" in item and item["specification"]:
                product_name = item["specification"]

            # 显示价格和折扣信息
            price_info = f"¥{item['price']}"
            if "discount_percentage" in item:
                price_info += f" (Disc. {item['discount_percentage']}%)"

            info_text = f"{product_name} - {price_info} × {item['amount']}"
            tk.Label(item_frame, text=info_text).pack(side=tk.LEFT, padx=5)

            check_vars.append((item, var))

        def confirm_delete():
            to_delete = []
            for item, var in check_vars:
                if var.get():
                    to_delete.append(item)

            if not to_delete:
                messagebox.showwarning("Warning", "Please select items to delete")
                return

            if messagebox.askyesno("Confirm", f"Are you sure you want to delete {len(to_delete)} selected items?"):
                # 删除选中的商品
                for del_item in to_delete:
                    self.order["breakdown"].remove(del_item)

                self.controller.save_order(self.order)
                self.refresh_display()
                dialog.destroy()
                messagebox.showinfo("Success", "Selected items deleted")

        # 底部区域
        bottom_frame = tk.Frame(dialog, bg="#f5f6fa")
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # 按钮区域
        button_frame = tk.Frame(bottom_frame, bg="#f5f6fa")
        button_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", command=confirm_delete).pack(side=tk.LEFT, padx=5)

        # 设置滚动区域
        scroll_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))


# 主应用视图
class EnhancedBartenderView(tk.Tk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("Bar Management System")
        self.geometry("400x700")  # 设置为矩形，像侧边栏

        # 设置整体样式
        self.configure(bg="#f5f6fa")
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 10))
        self.style.configure("TLabel", font=("Arial", 10))
        self.style.configure("Total.TLabel", font=("Arial", 14, "bold"), foreground="#27ae60")

        # 顶部标题栏
        title_bar = tk.Frame(self, bg="#f5f6fa")
        title_bar.pack(fill=tk.X, pady=5)

        tk.Label(title_bar, text="Bar Management System", font=("Arial", 14, "bold"),
                 bg="#f5f6fa").pack(pady=5)

        # 主容器
        self.container = tk.Frame(self, bg="#f5f6fa")
        self.container.pack(fill=tk.BOTH, expand=True)

        # 当前视图可以是"current_list", "history_list", "detail", "history_detail"
        self.current_view = None
        self.current_transaction_id = None

        self.show_list_view()

    # 清除主容器
    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # 显示当前订单列表视图
    def show_list_view(self):
        self.clear_container()
        self.title("Bar Management System - Current Orders")
        self.current_list = OrderListView(self.container, self.controller, self)
        self.current_list.pack(fill=tk.BOTH, expand=True)
        self.current_view = "current_list"

    # 显示历史订单列表视图
    def show_history_view(self):
        self.clear_container()
        self.title("Bar Management System - Order History")

        # 创建历史订单列表视图
        history_view = tk.Frame(self.container, bg="#f5f6fa")
        history_view.pack(fill=tk.BOTH, expand=True)

        # 标题栏和返回按钮
        header = tk.Frame(history_view, bg="#f5f6fa")
        header.pack(fill=tk.X, pady=5)

        ttk.Button(header, text="← Back",
                   command=self.show_list_view).pack(side=tk.LEFT, padx=10, pady=5)

        tk.Label(header, text="Order History",
                 font=("Arial", 14, "bold"), bg="#f5f6fa").pack(side=tk.LEFT, padx=20, pady=5)

        # 创建滚动区域
        canvas = tk.Canvas(history_view, bg="white")
        scrollbar = ttk.Scrollbar(history_view, orient="vertical", command=canvas.yview)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # 创建卡片容器
        history_frame = tk.Frame(canvas, bg="white")
        canvas.create_window((0, 0), window=history_frame, anchor="nw")

        orders = self.controller.get_history_orders()

        if not orders:
            tk.Label(history_frame, text="No history orders",
                     font=("Arial", 12), bg="white").pack(pady=20)
        else:
            # 添加历史订单卡片
            for order in orders:
                # 创建点击处理函数
                def make_click_handler(transaction_id):
                    def handler():
                        self.show_history_detail_view(transaction_id)

                    return handler

                card = OrderCard(
                    history_frame,
                    order,
                    on_click=make_click_handler(order["transaction_id"]),
                    bg="white",
                    width=350
                )
                card.pack(fill=tk.X, pady=5, padx=10)

        # 绑定调整大小事件
        def on_frame_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))

        history_frame.bind("<Configure>", on_frame_configure)

        def on_canvas_configure(e):
            canvas.itemconfig(canvas.find_withtag("all")[0], width=e.width)

        canvas.bind("<Configure>", on_canvas_configure)

        self.current_view = "history_list"

    # 显示历史订单详情视图
    def show_history_detail_view(self, transaction_id):
        self.clear_container()

        order = self.controller.get_order_by_transaction(transaction_id)
        if order:
            self.title(f"Bar Management System - Order History (Table {order['table_id']})")
            detail_view = HistoryDetailView(self.container, self.controller, order, self)
            detail_view.pack(fill=tk.BOTH, expand=True)
            self.current_view = "history_detail"
            self.current_transaction_id = transaction_id
        else:
            messagebox.showerror("Error", "Order not found")
            self.show_history_view()

    # 显示当前订单详情视图
    def show_detail_view(self, transaction_id):
        self.clear_container()

        order = self.controller.get_order_by_transaction(transaction_id)
        if order:
            self.title(f"Bar Management System - Order Details (Table {order['table_id']})")
            self.current_detail = OrderDetailView(self.container, self.controller, order, self)
            self.current_detail.pack(fill=tk.BOTH, expand=True)
            self.current_view = "detail"
            self.current_transaction_id = transaction_id
        else:
            messagebox.showerror("Error", "Order not found")
            self.show_list_view()


# 主程序入口
if __name__ == "__main__":
    if not os.path.exists("OrderDB.json"):
        initialize_test_data()

    controller = EnhancedOrderController()
    app = EnhancedBartenderView(controller)
    app.mainloop()