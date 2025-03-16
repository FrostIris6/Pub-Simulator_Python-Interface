import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
from datetime import datetime


# 订单卡片组件 view card set (view part start here)
class OrderCard(tk.Frame):
    def __init__(self, parent, order, on_click=None, translation_controller=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.order = order
        self.on_click = on_click
        self.translation_controller = translation_controller  # 存储翻译控制器 / Store translation controller

        # 设置卡片样式
        self.config(relief=tk.RAISED, borderwidth=1, padx=10, pady=10)
        self.bind("<Button-1>", self._on_click)

        # 计算总金额
        total = 0
        for item in order["breakdown"]:
            total += item["price"] * item["amount"]

        # 获取标签文本的翻译 / Get translations for label texts
        table_text = f"Table: {order['table_id']}"
        time_text = f"Time: {order['transaction_time']}"
        status_label_text = "Status: "
        total_text = f"Total: ¥{total:.2f}"

        if self.translation_controller:
            # 获取"Table: X"的翻译 / Get translation for "Table: X"
            table_pattern = self.translation_controller.get_text("views.order_management.table",
                                                                 default="Table: {table_id}")
            table_text = table_pattern.format(table_id=order['table_id'])

            # 获取"Time: X"的翻译 / Get translation for "Time: X"
            time_pattern = self.translation_controller.get_text("views.order_management.time",
                                                                default="Time: {transaction_time}")
            time_text = time_pattern.format(transaction_time=order['transaction_time'])

            # 获取"Status: "的翻译 / Get translation for "Status: "
            status_label_text = self.translation_controller.get_text("views.order_management.status_text",
                                                                     default="Status: ")

            # 获取"Total: ¥X"的翻译 / Get translation for "Total: ¥X"
            total_pattern = self.translation_controller.get_text("views.order_management.total",
                                                                 default="Total: ¥{total}")
            total_text = total_pattern.format(total=f"{total:.2f}")

        # 卡片标题 - 桌号 / Card title - table number
        title_frame = tk.Frame(self)
        title_frame.pack(fill=tk.X, pady=(0, 5))

        self.table_label = tk.Label(title_frame, text=table_text, font=("Arial", 12, "bold"))
        self.table_label.pack(side=tk.LEFT)

        # 订单时间 / Order time
        self.time_label = tk.Label(self, text=time_text, font=("Arial", 10))
        self.time_label.pack(anchor=tk.W)

        # 订单状态 / Order status
        is_completed = True
        for item in order["breakdown"]:
            if not item.get("is_paid", False):
                is_completed = False
                break

        # 获取状态文本的翻译 / Get translation for status text
        status_text = "Completed" if is_completed else "In Progress"
        if self.translation_controller:
            status_key = "completed" if is_completed else "in_progress"
            status_text = self.translation_controller.get_text(f"views.order_management.status.{status_key}",
                                                               default=status_text)

        status_color = "#27ae60" if is_completed else "#e74c3c"  # 绿色表示完成，红色表示进行中 / Green for completed, red for in progress

        status_frame = tk.Frame(self)
        status_frame.pack(fill=tk.X, pady=5)

        self.status_label_text = tk.Label(status_frame, text=status_label_text, font=("Arial", 10))
        self.status_label_text.pack(side=tk.LEFT)

        self.status_label = tk.Label(status_frame, text=status_text, fg=status_color, font=("Arial", 10, "bold"))
        self.status_label.pack(side=tk.LEFT)

        # 总价 / Total price
        self.total_label = tk.Label(self, text=total_text, font=("Arial", 11))
        self.total_label.pack(anchor=tk.E)

    # 处理点击事件 / Handle click event
    def _on_click(self, event):
        if self.on_click:
            self.on_click(self.order["transaction_id"])

    def update_translations(self):
        """更新卡片中的所有翻译文本 / Update all translated text in the card"""
        if not self.translation_controller:
            return

        # 更新桌号标签 / Update table number label
        table_pattern = self.translation_controller.get_text("views.order_management.table",
                                                             default="Table: {table_id}")
        self.table_label.config(text=table_pattern.format(table_id=self.order['table_id']))

        # 更新时间标签 / Update time label
        time_pattern = self.translation_controller.get_text("views.order_management.time",
                                                            default="Time: {transaction_time}")
        self.time_label.config(text=time_pattern.format(transaction_time=self.order['transaction_time']))

        # 更新状态标签文本 / Update status label text
        status_label_text = self.translation_controller.get_text("views.order_management.status_text",
                                                                 default="Status: ")
        self.status_label_text.config(text=status_label_text)

        # 更新状态文本 / Update status text
        is_completed = True
        for item in self.order["breakdown"]:
            if not item.get("is_paid", False):
                is_completed = False
                break

        status_key = "completed" if is_completed else "in_progress"
        status_text = self.translation_controller.get_text(f"views.order_management.status.{status_key}",
                                                           default="Completed" if is_completed else "In Progress")
        self.status_label.config(text=status_text)

        # 更新总价标签 / Update total price label
        total = 0
        for item in self.order["breakdown"]:
            total += item["price"] * item["amount"]

        total_pattern = self.translation_controller.get_text("views.order_management.total", default="Total: ¥{total}")
        self.total_label.config(text=total_pattern.format(total=f"{total:.2f}"))


# 订单列表视图 order list view
class OrderListView(ttk.Frame):
    def __init__(self, parent, controller, main_window, translation_controller=None):
        super().__init__(parent)
        self.controller = controller
        self.main_window = main_window
        self.translation_controller = translation_controller  # 存储翻译控制器 / Store translation controller
        self.create_widgets()
        self.load_orders()

    # 创建界面组件 / Create UI components
    def create_widgets(self):
        # 获取按钮文本的翻译 / Get translations for button texts
        refresh_text = "Refresh"
        history_text = "History"
        current_orders_text = "Current Orders"

        if self.translation_controller:
            refresh_text = self.translation_controller.get_text("views.order_management.refresh", default=refresh_text)
            history_text = self.translation_controller.get_text("views.order_management.history", default=history_text)
            current_orders_text = self.translation_controller.get_text("views.order_management.current_orders",
                                                                       default=current_orders_text)

        # 顶部工具栏 / Top toolbar
        toolbar = tk.Frame(self, bg="#f5f6fa")
        toolbar.pack(fill=tk.X, pady=5)

        self.refresh_button = ttk.Button(toolbar, text=refresh_text, command=self.load_orders)
        self.refresh_button.pack(side=tk.LEFT, padx=5)

        self.history_button = ttk.Button(toolbar, text=history_text, command=self.show_history)
        self.history_button.pack(side=tk.LEFT, padx=5)

        # 标题 / Title
        title_frame = tk.Frame(self, bg="#f5f6fa")
        title_frame.pack(fill=tk.X, pady=10)
        self.title_label = tk.Label(title_frame, text=current_orders_text, font=("Arial", 14, "bold"), bg="#f5f6fa")
        self.title_label.pack(pady=5)

        # 创建滚动区域 / Create scrollable area
        self.canvas = tk.Canvas(self, bg="white")
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # 创建卡片容器 / Create card container
        self.cards_frame = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window((0, 0), window=self.cards_frame, anchor="nw")

        # 绑定调整大小事件 / Bind resize events
        self.cards_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

    # 调整滚动区域 / Adjust scrollable area
    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    # 调整内部框架宽度 / Adjust inner frame width
    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas.find_withtag("all")[0], width=event.width)

    # 加载订单数据 / Load order data
    def load_orders(self):
        # 清除现有卡片 / Clear existing cards
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        orders = self.controller.get_active_orders()

        if not orders:
            # 获取"No active orders"的翻译 / Get translation for "No active orders"
            no_orders_text = "No active orders"
            if self.translation_controller:
                no_orders_text = self.translation_controller.get_text("views.order_management.no_active_orders",
                                                                      default=no_orders_text)

            # 显示无订单信息 / Display no orders message
            tk.Label(self.cards_frame, text=no_orders_text, font=("Arial", 12), bg="white").pack(pady=20)
            return

        # 添加订单卡片 / Add order cards
        for order in orders:
            def on_card_click(tid=order["transaction_id"]):
                self.main_window.show_detail_view(tid)

            card = OrderCard(
                self.cards_frame,
                order,
                on_click=on_card_click,
                translation_controller=self.translation_controller,  # 传递翻译控制器 / Pass translation controller
                bg="white",
                width=350  # 固定宽度 / Fixed width
            )
            card.pack(fill=tk.X, pady=5, padx=10, ipadx=5, ipady=5)

    # 显示历史订单 / Show order history
    def show_history(self):
        self.main_window.show_history_view()

    def update_translations(self):
        """更新视图中的所有翻译文本 / Update all translated text in the view"""
        if not self.translation_controller:
            return

        # 更新按钮文本 / Update button texts
        refresh_text = self.translation_controller.get_text("views.order_management.refresh", default="Refresh")
        history_text = self.translation_controller.get_text("views.order_management.history", default="History")
        self.refresh_button.config(text=refresh_text)
        self.history_button.config(text=history_text)

        # 更新标题文本 / Update title text
        current_orders_text = self.translation_controller.get_text("views.order_management.current_orders",
                                                                   default="Current Orders")
        self.title_label.config(text=current_orders_text)

        # 重新加载订单卡片以更新翻译 / Reload order cards to update translations
        self.load_orders()


# 历史订单详情视图 history view
class HistoryDetailView(ttk.Frame):
    def __init__(self, parent, controller, order, main_window, translation_controller=None):
        super().__init__(parent)
        self.controller = controller
        self.order = order
        self.main_window = main_window
        self.translation_controller = translation_controller  # 存储翻译控制器 / Store translation controller
        self.create_widgets()
        self.refresh_display()

    # 创建界面组件 / Create UI components
    def create_widgets(self):
        # 获取按钮文本和标题的翻译 / Get translations for button texts and titles
        back_text = "← Back"
        table_text = f"Table {self.order['table_id']}"
        total_text = "Total: ¥0.00"
        back_button_text = "Back"

        if self.translation_controller:
            back_text = self.translation_controller.get_text("general.back", default=back_text)

            # 获取"Table X"的翻译 / Get translation for "Table X"
            table_pattern = self.translation_controller.get_text(
                "views.order_management.order_details",
                default="Table {table_id}"
            )
            table_text = table_pattern.format(table_id=self.order['table_id'])

            # 获取"Total: ¥X"的翻译 / Get translation for "Total: ¥X"
            total_pattern = self.translation_controller.get_text(
                "views.order_management.total",
                default="Total: ¥{total}"
            )
            total_text = total_pattern.format(total="0.00")

            back_button_text = self.translation_controller.get_text("general.back", default="Back").replace("← ", "")

        # 顶部导航栏 / Top navigation bar
        header = tk.Frame(self, bg="#f5f6fa")
        header.pack(fill=tk.X)

        # 返回按钮 / Back button
        self.back_btn = ttk.Button(header, text=back_text, command=self.return_to_history)
        self.back_btn.pack(side=tk.LEFT, padx=10, pady=10)

        # 桌号标题 / Table number title
        title_frame = tk.Frame(header, bg="#f5f6fa")
        title_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20)

        self.title_label = tk.Label(title_frame, text=table_text,
                                    font=("Arial", 14, "bold"), bg="#f5f6fa")
        self.title_label.pack(side=tk.LEFT)

        # 创建滚动区域 / Create scrollable area
        self.canvas = tk.Canvas(self, bg="white")
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # 创建详情容器 / Create details container
        self.detail_frame = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window((0, 0), window=self.detail_frame, anchor="nw")

        # 绑定调整大小事件 / Bind resize events
        def on_frame_configure(e):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        self.detail_frame.bind("<Configure>", on_frame_configure)

        def on_canvas_configure(e):
            self.canvas.itemconfig(self.canvas.find_withtag("all")[0], width=e.width)

        self.canvas.bind("<Configure>", on_canvas_configure)

        # 底部区域 - 左对齐总额和返回按钮 / Bottom area - left-aligned total and back button
        self.bottom_frame = tk.Frame(self, bg="#f5f6fa")
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # 创建左侧区域 / Create left area
        bottom_left = tk.Frame(self.bottom_frame, bg="#f5f6fa")
        bottom_left.pack(side=tk.LEFT, padx=15, pady=10, fill=tk.Y)

        # 总金额 / Total amount
        self.total_label = tk.Label(bottom_left, text=total_text,
                                    font=("Arial", 14, "bold"), bg="#f5f6fa")
        self.total_label.pack(anchor=tk.W)

        # 返回按钮 / Back button
        self.back_button = ttk.Button(bottom_left, text=back_button_text,
                                      command=self.return_to_history)
        self.back_button.pack(anchor=tk.W, pady=5)

    # 返回历史订单列表 / Return to order history list
    def return_to_history(self):
        self.main_window.show_history_view()

    # 刷新数据 / Refresh data
    def refresh_data(self):
        self.order = self.controller.get_order_by_transaction(self.order["transaction_id"])
        self.refresh_display()

    # 刷新显示 / Refresh display
    def refresh_display(self):
        # 清除现有内容 / Clear existing content
        for widget in self.detail_frame.winfo_children():
            widget.destroy()

        # 按类别组织商品 / Organize products by category
        categories = {}

        # 获取类别名称的翻译 / Get translations for category names
        category_translations = {
            "酒水": "Wine & Spirits",
            "啤酒": "Beer",
            "鸡尾酒": "Cocktail",
            "食品": "Food",
            "玻璃杯": "Glass",
            "瓶装": "Bottle",
            "威士忌": "Whiskey"
        }

        # 如果有翻译控制器，更新翻译字典 / If translation controller exists, update translation dictionary
        if self.translation_controller:
            category_translations = {
                "酒水": self.translation_controller.get_text("views.order_management.categories.wine_spirits",
                                                             default="Wine & Spirits"),
                "啤酒": self.translation_controller.get_text("views.order_management.categories.beer", default="Beer"),
                "鸡尾酒": self.translation_controller.get_text("views.order_management.categories.cocktails",
                                                               default="Cocktail"),
                "食品": self.translation_controller.get_text("views.order_management.categories.food", default="Food"),
                "玻璃杯": self.translation_controller.get_text("products.info.glass", default="Glass"),
                "瓶装": self.translation_controller.get_text("products.info.bottle", default="Bottle"),
                "威士忌": "Whiskey"  # 保持原样或添加特定翻译 / Keep as is or add specific translation
            }

            # 获取默认类别名称的翻译 / Get translations for default category names
            default_drinks = self.translation_controller.get_text("views.order_management.categories.drinks",
                                                                  default="Drinks")
            wine_spirits = self.translation_controller.get_text("views.order_management.categories.wine_spirits",
                                                                default="Wine & Spirits")
            beer = self.translation_controller.get_text("views.order_management.categories.beer", default="Beer")
            cocktails = self.translation_controller.get_text("views.order_management.categories.cocktails",
                                                             default="Cocktails")
            food = self.translation_controller.get_text("views.order_management.categories.food", default="Food")

        for item in self.order["breakdown"]:
            # 默认类别名称 / Default category name
            cat_name = "Drinks"
            if self.translation_controller:
                cat_name = default_drinks

            # 翻译规格 / Translate specifications
            if "specification" in item:
                spec = item["specification"]
                # 检查是否需要翻译 / Check if translation is needed
                for cn, en in category_translations.items():
                    if cn in spec:
                        spec = spec.replace(cn, en)
                # 更新规格 / Update specification
                item["specification"] = spec

                # 按规格分类 / Categorize by specification
                spec_lower = spec.lower()
                if "wine" in spec_lower or "whisky" in spec_lower or "whiskey" in spec_lower:
                    cat_name = "Wine & Spirits" if not self.translation_controller else wine_spirits
                elif "beer" in spec_lower:
                    cat_name = "Beer" if not self.translation_controller else beer
                elif "cocktail" in spec_lower:
                    cat_name = "Cocktails" if not self.translation_controller else cocktails
                elif "food" in spec_lower or "snack" in spec_lower:
                    cat_name = "Food" if not self.translation_controller else food

            if cat_name not in categories:
                categories[cat_name] = []
            categories[cat_name].append(item)

        # 显示每个类别 / Display each category
        for cat_name in categories:
            items = categories[cat_name]
            if items:  # 只显示有商品的类别 / Only show categories with items
                self.create_item_section(cat_name, items)

        # 计算总金额 / Calculate total amount
        total = 0
        for item in self.order["breakdown"]:
            total += item["price"] * item["amount"]

        # 更新总金额显示 / Update total amount display
        total_pattern = "Total: ¥{total:.2f}"
        if self.translation_controller:
            total_pattern = self.translation_controller.get_text("views.order_management.total", default=total_pattern)

        self.total_label.config(text=total_pattern.format(total=total))

    # 创建商品分类部分 / Create product category section
    def create_item_section(self, category, items):
        # 创建类别标题框架 / Create category title frame
        section_frame = tk.Frame(self.detail_frame, bg="white")
        section_frame.pack(fill=tk.X, pady=5)

        # 类别标题 / Category title
        tk.Label(section_frame, text=category,
                 font=("Arial", 12, "bold"), bg="white").pack(anchor=tk.W, padx=10, pady=5)

        # 遍历类别中的商品 / Iterate through items in the category
        for item in items:
            # 获取商品状态文本的翻译 / Get translation for item status text
            status = "Paid" if item.get("is_paid", False) else ""
            if self.translation_controller and item.get("is_paid", False):
                status = self.translation_controller.get_text("views.order_management.status.completed", default="Paid")

            bg_color = "#ebf5eb" if item.get("is_paid", False) else "white"

            # 创建商品框架 / Create item frame
            item_frame = tk.Frame(self.detail_frame, bg=bg_color)
            item_frame.pack(fill=tk.X, padx=5, pady=2)

            # 左侧信息 / Left side information
            left_frame = tk.Frame(item_frame, bg=bg_color)
            left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=8)

            # 商品名称和规格 / Product name and specifications
            product_name = f"Item {item['product_id']}"
            if "specification" in item and item["specification"]:
                product_name = item["specification"]

            tk.Label(left_frame, text=product_name,
                     font=("Arial", 11), bg=bg_color).pack(anchor=tk.W)

            # 显示折扣信息 / Display discount information
            if "discount_percentage" in item:
                # 获取折扣信息的翻译 / Get translation for discount information
                discount_pattern = "Discount {percentage}%"
                if self.translation_controller:
                    discount_pattern = self.translation_controller.get_text(
                        "views.order_management.discount_info",
                        default=discount_pattern
                    )

                discount_info = discount_pattern.format(percentage=item['discount_percentage'])
                tk.Label(left_frame, text=discount_info, fg="#e67e22",
                         font=("Arial", 9), bg=bg_color).pack(anchor=tk.W)

            # 右侧信息 / Right side information
            right_frame = tk.Frame(item_frame, bg=bg_color)
            right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=8)

            # 显示价格 / Display price
            price_text = f"¥ {item['price']:.2f}"
            tk.Label(right_frame, text=price_text,
                     font=("Arial", 11), bg=bg_color).pack(side=tk.RIGHT)

            # 显示数量 / Display quantity
            qty_frame = tk.Frame(right_frame, bg=bg_color)
            qty_frame.pack(side=tk.RIGHT, padx=20)

            # 数量格式保持原样 / Keep quantity format as is
            tk.Label(qty_frame, text=f"× {item['amount']}",
                     font=("Arial", 11), bg=bg_color).pack()

    def update_translations(self):
        """更新视图中的所有翻译文本 / Update all translated text in the view"""
        if not self.translation_controller:
            return

        # 更新返回按钮和标题 / Update back button and title
        back_text = self.translation_controller.get_text("general.back", default="← Back")
        self.back_btn.config(text=back_text)

        back_button_text = self.translation_controller.get_text("general.back", default="Back").replace("← ", "")
        self.back_button.config(text=back_button_text)

        # 更新桌号标题 / Update table number title
        table_pattern = self.translation_controller.get_text(
            "views.order_management.order_details",
            default="Table {table_id}"
        )
        self.title_label.config(text=table_pattern.format(table_id=self.order['table_id']))

        # 刷新显示以更新所有其他文本 / Refresh display to update all other texts
        self.refresh_display()

# 订单详情视图 / Order detail view
class OrderDetailView(ttk.Frame):
    def __init__(self, parent, controller, order, main_window, translation_controller=None):
        super().__init__(parent)
        self.controller = controller
        self.order = order
        self.main_window = main_window
        self.translation_controller = translation_controller  # 存储翻译控制器 / Store translation controller
        self.selected_items = {}  # 用于存储选中的商品 / For storing selected items
        self.create_widgets()
        self.refresh_display()

    # 创建界面组件 / Create UI components
    def create_widgets(self):
        # 获取按钮和标签的翻译 / Get translations for buttons and labels
        back_text = "← Back"
        table_text = f"Table {self.order['table_id']}"
        apply_discount_text = "Apply Discount:"
        rate_text = "Rate (%)"
        apply_discount_btn_text = "Apply Discount"
        clear_selection_text = "Clear Selection"
        partial_checkout_text = "Partial Checkout"
        to_pay_text = "To Pay: ¥0.00"
        checkout_text = "Checkout"
        cancel_text = "Cancel"
        back_btn_text = "Back"

        if self.translation_controller:
            back_text = self.translation_controller.get_text("general.back", default=back_text)

            # 获取"Table X"的翻译 / Get translation for "Table X"
            table_pattern = self.translation_controller.get_text(
                "views.order_management.order_details",
                default="Table {table_id}"
            )
            table_text = table_pattern.format(table_id=self.order['table_id'])

            apply_discount_text = self.translation_controller.get_text(
                "views.order_management.apply_discount",
                default=apply_discount_text
            )

            rate_text = self.translation_controller.get_text(
                "views.order_management.rate",
                default=rate_text
            )

            apply_discount_btn_text = self.translation_controller.get_text(
                "views.order_management.apply_discount_button",
                default=apply_discount_btn_text
            )

            clear_selection_text = self.translation_controller.get_text(
                "views.order_management.clear_selection",
                default=clear_selection_text
            )

            partial_checkout_text = self.translation_controller.get_text(
                "views.order_management.partial_checkout",
                default=partial_checkout_text
            )

            to_pay_pattern = self.translation_controller.get_text(
                "views.order_management.to_pay",
                default="To Pay: ¥{total}"
            )
            to_pay_text = to_pay_pattern.format(total="0.00")

            checkout_text = self.translation_controller.get_text(
                "views.order_management.checkout",
                default=checkout_text
            )

            cancel_text = self.translation_controller.get_text(
                "user_interface.cancel",
                default=cancel_text
            )

            back_btn_text = self.translation_controller.get_text(
                "general.back",
                default=back_btn_text
            ).replace("← ", "")

        # 顶部导航栏 / Top navigation bar
        header = tk.Frame(self, bg="#f5f6fa")
        header.pack(fill=tk.X)

        # 返回按钮 / Back button
        self.back_btn = ttk.Button(header, text=back_text,
                                   command=self.main_window.show_list_view)
        self.back_btn.pack(side=tk.LEFT, padx=10, pady=10)

        # 桌号标题 / Table number title
        title_frame = tk.Frame(header, bg="#f5f6fa")
        title_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20)

        self.title_label = tk.Label(title_frame, text=table_text,
                                    font=("Arial", 14, "bold"), bg="#f5f6fa")
        self.title_label.pack(side=tk.LEFT)

        # 添加和删除按钮 / Add and delete buttons
        btn_frame = tk.Frame(header, bg="#f5f6fa")
        btn_frame.pack(side=tk.RIGHT, padx=10)

        # 添加按钮(+图标) / Add button (+ icon)
        self.add_btn = tk.Button(btn_frame, text="+", font=("Arial", 12, "bold"),
                                 width=2, command=self.show_add_item_dialog,
                                 bg="#2ecc71", fg="white", relief=tk.FLAT)
        self.add_btn.pack(side=tk.RIGHT, padx=5, pady=10)

        # 删除按钮(-图标) / Delete button (- icon)
        self.del_btn = tk.Button(btn_frame, text="−", font=("Arial", 12, "bold"),
                                 width=2, command=self.delete_selected_items,
                                 bg="#e74c3c", fg="white", relief=tk.FLAT)
        self.del_btn.pack(side=tk.RIGHT, padx=5, pady=10)

        # 折扣面板 / Discount panel
        self.discount_panel = tk.Frame(self, bg="#f5f6fa", padx=10, pady=5)
        self.discount_panel.pack(fill=tk.X)

        # 折扣标题 / Discount title
        self.discount_label = tk.Label(self.discount_panel, text=apply_discount_text,
                                       font=("Arial", 11, "bold"), bg="#f5f6fa")
        self.discount_label.pack(side=tk.LEFT, padx=5)

        # 折扣率输入框 / Discount rate input field
        self.rate_label = tk.Label(self.discount_panel, text=rate_text, bg="#f5f6fa")
        self.rate_label.pack(side=tk.LEFT, padx=5)

        self.discount_entry = ttk.Entry(self.discount_panel, width=6)
        self.discount_entry.pack(side=tk.LEFT, padx=2)
        self.discount_entry.insert(0, "10")  # 默认10%折扣 / Default 10% discount

        # 应用折扣按钮 / Apply discount button
        self.apply_discount_btn = ttk.Button(self.discount_panel, text=apply_discount_btn_text,
                                             command=self.apply_selected_discount)
        self.apply_discount_btn.pack(side=tk.LEFT, padx=10)

        # 取消选择按钮 / Clear selection button
        self.clear_selection_btn = ttk.Button(self.discount_panel, text=clear_selection_text,
                                              command=self.clear_item_selection)
        self.clear_selection_btn.pack(side=tk.LEFT, padx=5)

        # 主操作按钮 / Main operation buttons
        self.toolbar = tk.Frame(self)
        self.toolbar.pack(fill=tk.X, pady=5)

        self.partial_checkout_btn = ttk.Button(self.toolbar, text=partial_checkout_text,
                                               command=self.show_checkout_dialog)
        self.partial_checkout_btn.pack(side=tk.LEFT, padx=5)

        # 创建滚动区域 / Create scrollable area
        self.canvas = tk.Canvas(self, bg="white")
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # 创建详情容器 / Create details container
        self.detail_frame = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window((0, 0), window=self.detail_frame, anchor="nw")

        # 绑定调整大小事件 / Bind resize events
        def on_frame_configure(e):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        self.detail_frame.bind("<Configure>", on_frame_configure)

        def on_canvas_configure(e):
            self.canvas.itemconfig(self.canvas.find_withtag("all")[0], width=e.width)

        self.canvas.bind("<Configure>", on_canvas_configure)

        # 底部结账区域 / Bottom checkout area
        self.bottom_frame = tk.Frame(self, bg="#f5f6fa")
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # 创建左侧区域 / Create left area
        bottom_left = tk.Frame(self.bottom_frame, bg="#f5f6fa")
        bottom_left.pack(side=tk.LEFT, padx=15, pady=10, fill=tk.Y)

        # 总金额信息 / Total amount information
        self.total_label = tk.Label(bottom_left, text=to_pay_text,
                                    font=("Arial", 14, "bold"), bg="#f5f6fa")
        self.total_label.pack(anchor=tk.W)

        # 按钮区域 / Button area
        button_frame = tk.Frame(bottom_left, bg="#f5f6fa")
        button_frame.pack(anchor=tk.W, pady=5)

        # 结账按钮 / Checkout button
        self.checkout_btn = ttk.Button(button_frame, text=checkout_text,
                                       command=self.full_checkout)
        self.checkout_btn.pack(side=tk.LEFT, padx=5)

        # 取消按钮 / Cancel button
        self.cancel_btn = ttk.Button(button_frame, text=cancel_text,
                                     command=self.cancel_checkout)
        self.cancel_btn.pack(side=tk.LEFT, padx=5)

        # 返回按钮 / Back button
        self.back_button = ttk.Button(button_frame, text=back_btn_text,
                                      command=self.main_window.show_list_view)
        self.back_button.pack(side=tk.LEFT, padx=5)

    # 创建商品分类部分 / Create product category section
    def create_item_section(self, category, items):
        # 创建类别标题框架 / Create category title frame
        section_frame = tk.Frame(self.detail_frame, bg="white")
        section_frame.pack(fill=tk.X, pady=5)

        # 类别标题 / Category title
        tk.Label(section_frame, text=category,
                 font=("Arial", 12, "bold"), bg="white").pack(anchor=tk.W, padx=10, pady=5)

        # 遍历类别中的商品 / Iterate through items in the category
        for item in items:
            # 商品状态 / Item status
            is_paid = item.get("is_paid", False)

            # 获取状态文本的翻译 / Get translation for status text
            status = "Paid" if is_paid else ""
            if self.translation_controller and is_paid:
                status = self.translation_controller.get_text(
                    "views.order_management.status.completed",
                    default="Paid"
                )

            bg_color = "#ebf5eb" if is_paid else "white"

            # 创建商品框架 / Create item frame
            item_frame = tk.Frame(self.detail_frame, bg=bg_color)
            item_frame.pack(fill=tk.X, padx=5, pady=2)

            # 选择复选框 - 只为未付款商品显示 / Selection checkbox - only for unpaid items
            if not is_paid:
                # 创建选择变量 / Create selection variable
                item_id = str(item["product_id"])
                if item_id not in self.selected_items:
                    self.selected_items[item_id] = tk.BooleanVar(value=False)

                check = ttk.Checkbutton(item_frame, variable=self.selected_items[item_id])
                check.pack(side=tk.LEFT, padx=2)

            # 左侧信息 / Left side information
            left_frame = tk.Frame(item_frame, bg=bg_color)
            left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5 if not is_paid else 10, pady=8)

            # 商品名称和规格 / Product name and specifications
            product_name = f"Item {item['product_id']}"
            if "specification" in item and item["specification"]:
                product_name = item["specification"]

            tk.Label(left_frame, text=product_name,
                     font=("Arial", 11), bg=bg_color).pack(anchor=tk.W)

            # 显示折扣信息 / Display discount information
            if "discount_percentage" in item:
                # 获取折扣信息的翻译 / Get translation for discount information
                discount_pattern = "Discount {percentage}%"
                if self.translation_controller:
                    discount_pattern = self.translation_controller.get_text(
                        "views.order_management.discount_info",
                        default=discount_pattern
                    )

                discount_info = discount_pattern.format(percentage=item['discount_percentage'])
                tk.Label(left_frame, text=discount_info, fg="#e67e22",
                         font=("Arial", 9), bg=bg_color).pack(anchor=tk.W)

            # 右侧信息 / Right side information
            right_frame = tk.Frame(item_frame, bg=bg_color)
            right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=8)

            # 显示价格 / Display price
            price_text = f"¥ {item['price']:.2f}"
            tk.Label(right_frame, text=price_text,
                     font=("Arial", 11), bg=bg_color).pack(side=tk.RIGHT)

            # 显示数量 / Display quantity
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

            # 获取警告和成功消息的翻译
            warning_message = "Please select at least one item to apply discount"
            success_message = f"Discount of {discount_rate * 100:.1f}% applied to {len(selected_ids)} items"
            warning_title = "Warning"
            success_title = "Success"

            if self.translation_controller:
                warning_message = self.translation_controller.get_text(
                    "views.order_management.warnings.select_items_for_discount",
                    default=warning_message
                )
                success_message_pattern = self.translation_controller.get_text(
                    "views.order_management.success.discount_applied",
                    default="Discount of {rate}% applied to {count} items"
                )
                success_message = success_message_pattern.format(
                    rate=f"{discount_rate * 100:.1f}",
                    count=len(selected_ids)
                )
                warning_title = self.translation_controller.get_text(
                    "general.warning",
                    default=warning_title
                )
                success_title = self.translation_controller.get_text(
                    "general.success",
                    default=success_title
                )

            if not selected_ids:
                messagebox.showwarning(warning_title, warning_message)
                return

            # 应用折扣
            self.order = self.controller.apply_discount(self.order, discount_rate, selected_ids)
            self.controller.save_order(self.order)
            self.refresh_display()
            messagebox.showinfo(success_title, success_message)

            # 清除选择
            self.clear_item_selection()

        except ValueError:
            # 错误消息翻译
            error_title = "Error"
            error_message = "Please enter a valid discount rate between 0-100"

            if self.translation_controller:
                error_title = self.translation_controller.get_text(
                    "general.error",
                    default=error_title
                )
                error_message = self.translation_controller.get_text(
                    "views.order_management.errors.invalid_discount_rate",
                    default=error_message
                )

            messagebox.showerror(error_title, error_message)

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

        # 翻译字典 - 如果有翻译控制器，应该从翻译文件获取
        translations = {
            "酒水": "Wine & Spirits",
            "啤酒": "Beer",
            "鸡尾酒": "Cocktail",
            "食品": "Food",
            "玻璃杯": "Glass",
            "瓶装": "Bottle",
            "威士忌": "Whiskey"
        }

        # 如果有翻译控制器，更新翻译字典
        if self.translation_controller:
            for key in translations.keys():
                translations[key] = self.translation_controller.get_text(
                    f"product_categories.{key}",
                    default=translations[key]
                )

        # 获取类别翻译
        default_category = "Drinks"
        wine_spirits_category = "Wine & Spirits"
        beer_category = "Beer"
        cocktails_category = "Cocktails"
        food_category = "Food"
        paid_items_category = "Paid Items"

        if self.translation_controller:
            default_category = self.translation_controller.get_text(
                "product_categories.default",
                default=default_category
            )
            wine_spirits_category = self.translation_controller.get_text(
                "product_categories.wine_spirits",
                default=wine_spirits_category
            )
            beer_category = self.translation_controller.get_text(
                "product_categories.beer",
                default=beer_category
            )
            cocktails_category = self.translation_controller.get_text(
                "product_categories.cocktails",
                default=cocktails_category
            )
            food_category = self.translation_controller.get_text(
                "product_categories.food",
                default=food_category
            )
            paid_items_category = self.translation_controller.get_text(
                "product_categories.paid_items",
                default=paid_items_category
            )

        for item in unpaid_items:
            cat_name = default_category  # 默认类别

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
                    cat_name = wine_spirits_category
                elif "beer" in spec_lower:
                    cat_name = beer_category
                elif "cocktail" in spec_lower:
                    cat_name = cocktails_category
                elif "food" in spec_lower or "snack" in spec_lower:
                    cat_name = food_category

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
            categories[paid_items_category] = checked_out_items

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

        # 获取支付标签翻译
        to_pay_pattern = "To Pay: ¥{total}"
        if self.translation_controller:
            to_pay_pattern = self.translation_controller.get_text(
                "views.order_management.to_pay",
                default=to_pay_pattern
            )

        # 更新总金额显示
        to_pay_text = to_pay_pattern.format(total=f"{total:.2f}")
        self.total_label.config(text=to_pay_text)

        # 全部结账


    def full_checkout(self):
        unpaid_ids = []
        for item in self.order["breakdown"]:
            if not item.get("is_paid", False):
                unpaid_ids.append(str(item["product_id"]))

        # 获取消息翻译
        info_title = "Info"
        all_paid_message = "All items are already paid"
        success_title = "Success"
        checkout_success_pattern = "Successfully checked out ¥{total:.2f}"

        if self.translation_controller:
            info_title = self.translation_controller.get_text(
                "general.info",
                default=info_title
            )
            all_paid_message = self.translation_controller.get_text(
                "views.order_management.info.all_items_paid",
                default=all_paid_message
            )
            success_title = self.translation_controller.get_text(
                "general.success",
                default=success_title
            )
            checkout_success_pattern = self.translation_controller.get_text(
                "views.order_management.success.checkout_completed",
                default=checkout_success_pattern
            )

        if not unpaid_ids:
            messagebox.showinfo(info_title, all_paid_message)
            return

        self.order, total = self.controller.partial_checkout(self.order, unpaid_ids)
        self.controller.save_order(self.order)
        self.refresh_display()
        checkout_success_message = checkout_success_pattern.format(total=total)
        messagebox.showinfo(success_title, checkout_success_message)

        # 显示结账对话框


    def show_checkout_dialog(self):
        # 获取对话框标题和文本的翻译
        dialog_title = "Select Items to Checkout"
        select_items_text = "Select items to checkout:"
        to_pay_pattern = "To Pay: ¥{total}"
        cancel_text = "Cancel"
        confirm_text = "Confirm"
        warning_title = "Warning"
        select_item_warning = "Please select at least one item"
        success_title = "Success"
        checkout_success_pattern = "Successfully checked out ¥{total:.2f}"
        all_paid_text = "All items are already paid"

        if self.translation_controller:
            dialog_title = self.translation_controller.get_text(
                "views.order_management.dialogs.select_items_title",
                default=dialog_title
            )
            select_items_text = self.translation_controller.get_text(
                "views.order_management.dialogs.select_items_instruction",
                default=select_items_text
            )
            to_pay_pattern = self.translation_controller.get_text(
                "views.order_management.to_pay",
                default=to_pay_pattern
            )
            cancel_text = self.translation_controller.get_text(
                "user_interface.cancel",
                default=cancel_text
            )
            confirm_text = self.translation_controller.get_text(
                "user_interface.confirm",
                default=confirm_text
            )
            warning_title = self.translation_controller.get_text(
                "general.warning",
                default=warning_title
            )
            select_item_warning = self.translation_controller.get_text(
                "views.order_management.warnings.select_at_least_one",
                default=select_item_warning
            )
            success_title = self.translation_controller.get_text(
                "general.success",
                default=success_title
            )
            checkout_success_pattern = self.translation_controller.get_text(
                "views.order_management.success.checkout_completed",
                default=checkout_success_pattern
            )
            all_paid_text = self.translation_controller.get_text(
                "views.order_management.info.all_items_paid",
                default=all_paid_text
            )

        dialog = tk.Toplevel(self)
        dialog.title(dialog_title)
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

        # 获取折扣信息的翻译模式
        discount_pattern = "Discount {percentage}%"
        if self.translation_controller:
            discount_pattern = self.translation_controller.get_text(
                "views.order_management.discount_info",
                default=discount_pattern
            )

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

            to_pay_text = to_pay_pattern.format(total=f"{total:.2f}")
            total_label.config(text=to_pay_text)

        if not unpaid_items:
            tk.Label(scroll_frame, text=all_paid_text,
                     font=("Arial", 12)).pack(pady=20)
        else:
            tk.Label(scroll_frame, text=select_items_text,
                     font=("Arial", 11, "bold")).pack(anchor=tk.W, padx=10, pady=10)

            for item in unpaid_items:
                var = tk.BooleanVar(value=True)  # 默认选中

                # 显示折扣信息
                discount_info = ""
                if "discount_percentage" in item:
                    discount_info = f" ({discount_pattern.format(percentage=item['discount_percentage'])})"

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
                messagebox.showwarning(warning_title, select_item_warning)
                return

            self.order, total = self.controller.partial_checkout(self.order, selected_ids)
            self.controller.save_order(self.order)
            self.refresh_display()
            dialog.destroy()
            checkout_success_message = checkout_success_pattern.format(total=total)
            messagebox.showinfo(success_title, checkout_success_message)

        # 底部区域
        bottom_frame = tk.Frame(dialog, bg="#f5f6fa")
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # 结账总金额显示
        initial_to_pay = to_pay_pattern.format(total="0.00")
        total_label = tk.Label(bottom_frame, text=initial_to_pay,
                               font=("Arial", 12, "bold"), bg="#f5f6fa")
        total_label.pack(side=tk.LEFT, padx=15, pady=10)

        # 初始化总金额显示
        if unpaid_items:
            update_total_display()

        # 按钮区域
        button_frame = tk.Frame(bottom_frame, bg="#f5f6fa")
        button_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        ttk.Button(button_frame, text=cancel_text, command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text=confirm_text, command=confirm_checkout).pack(side=tk.LEFT, padx=5)

        # 设置滚动区域
        scroll_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        # 取消结账 - 重置所有商品的付款状态


    def cancel_checkout(self):
        # 获取确认信息和成功信息的翻译
        confirm_title = "Confirm"
        confirm_message = "Are you sure you want to reset all item payment status?"
        success_title = "Success"
        success_message = "All payment status has been reset"

        if self.translation_controller:
            confirm_title = self.translation_controller.get_text(
                "general.confirm",
                default=confirm_title
            )
            confirm_message = self.translation_controller.get_text(
                "views.order_management.confirm.reset_payment_status",
                default=confirm_message
            )
            success_title = self.translation_controller.get_text(
                "general.success",
                default=success_title
            )
            success_message = self.translation_controller.get_text(
                "views.order_management.success.payment_status_reset",
                default=success_message
            )

        if messagebox.askyesno(confirm_title, confirm_message):
            for item in self.order["breakdown"]:
                item["is_paid"] = False
            self.controller.save_order(self.order)
            self.refresh_display()
            messagebox.showinfo(success_title, success_message)

        # 显示添加商品对话框


    def show_add_item_dialog(self):
        # 获取对话框标题和文本的翻译
        dialog_title = "Add New Item"
        dialog_header = "Add New Item"
        field_product_id = "Product ID:"
        field_specification = "Specification:"
        field_price = "Price:"
        field_quantity = "Quantity:"
        cancel_text = "Cancel"
        add_text = "Add"
        error_title = "Error"
        error_message = "Please enter valid values"
        success_title = "Success"
        success_message = "Item added"

        if self.translation_controller:
            dialog_title = self.translation_controller.get_text(
                "views.order_management.dialogs.add_item_title",
                default=dialog_title
            )
            dialog_header = self.translation_controller.get_text(
                "views.order_management.dialogs.add_item_header",
                default=dialog_header
            )
            field_product_id = self.translation_controller.get_text(
                "views.order_management.fields.product_id",
                default=field_product_id
            )
            field_specification = self.translation_controller.get_text(
                "views.order_management.fields.specification",
                default=field_specification
            )
            field_price = self.translation_controller.get_text(
                "views.order_management.fields.price",
                default=field_price
            )
            field_quantity = self.translation_controller.get_text(
                "views.order_management.fields.quantity",
                default=field_quantity
            )
            cancel_text = self.translation_controller.get_text(
                "user_interface.cancel",
                default=cancel_text
            )
            add_text = self.translation_controller.get_text(
                "user_interface.add",
                default=add_text
            )
            error_title = self.translation_controller.get_text(
                "general.error",
                default=error_title
            )
            error_message = self.translation_controller.get_text(
                "views.order_management.errors.invalid_input",
                default=error_message
            )
            success_title = self.translation_controller.get_text(
                "general.success",
                default=success_title
            )
            success_message = self.translation_controller.get_text(
                "views.order_management.success.item_added",
                default=success_message
            )

        dialog = tk.Toplevel(self)
        dialog.title(dialog_title)
        dialog.geometry("300x250")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        # 输入字段
        fields = [
            (field_product_id, "product_id"),
            (field_specification, "specification"),
            (field_price, "price"),
            (field_quantity, "amount")
        ]
        entries = {}

        # 标题
        tk.Label(dialog, text=dialog_header,
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
                messagebox.showerror(error_title, error_message)
                return

            self.order["breakdown"].append(new_item)
            self.controller.save_order(self.order)
            self.refresh_display()
            dialog.destroy()
            messagebox.showinfo(success_title, success_message)

        # 按钮区域
        button_frame = tk.Frame(dialog)
        button_frame.grid(row=len(fields) + 1, column=0, columnspan=2, pady=15)

        ttk.Button(button_frame, text=cancel_text, command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text=add_text, command=add_item).pack(side=tk.LEFT, padx=5)

        # 删除选中的商品


    def delete_selected_items(self):
        # 获取对话框标题和文本的翻译
        information_title = "Information"
        no_unpaid_items_message = "There are no unpaid items to delete. Paid items cannot be deleted."
        dialog_title = "Select Items to Delete"
        select_items_text = "Select unpaid items to delete:"
        note_text_pattern = "Note: {count} paid items are not shown as they cannot be deleted."
        warning_title = "Warning"
        select_items_warning = "Please select items to delete"
        confirm_title = "Confirm"
        confirm_message_pattern = "Are you sure you want to delete {count} selected items?"
        success_title = "Success"
        success_message = "Selected items deleted"
        cancel_text = "Cancel"
        delete_text = "Delete"

        if self.translation_controller:
            information_title = self.translation_controller.get_text(
                "general.information",
                default=information_title
            )
            no_unpaid_items_message = self.translation_controller.get_text(
                "views.order_management.info.no_unpaid_items",
                default=no_unpaid_items_message
            )
            dialog_title = self.translation_controller.get_text(
                "views.order_management.dialogs.delete_items_title",
                default=dialog_title
            )
            select_items_text = self.translation_controller.get_text(
                "views.order_management.dialogs.select_items_to_delete",
                default=select_items_text
            )
            note_text_pattern = self.translation_controller.get_text(
                "views.order_management.info.paid_items_not_shown",
                default=note_text_pattern
            )
            warning_title = self.translation_controller.get_text(
                "general.warning",
                default=warning_title
            )
            select_items_warning = self.translation_controller.get_text(
                "views.order_management.warnings.select_items_to_delete",
                default=select_items_warning
            )
            confirm_title = self.translation_controller.get_text(
                "general.confirm",
                default=confirm_title
            )
            confirm_message_pattern = self.translation_controller.get_text(
                "views.order_management.confirm.delete_items",
                default=confirm_message_pattern
            )
            success_title = self.translation_controller.get_text(
                "general.success",
                default=success_title
            )
            success_message = self.translation_controller.get_text(
                "views.order_management.success.items_deleted",
                default=success_message
            )
            cancel_text = self.translation_controller.get_text(
                "user_interface.cancel",
                default=cancel_text
            )
            delete_text = self.translation_controller.get_text(
                "user_interface.delete",
                default=delete_text
            )

        # 筛选未付款的商品
        unpaid_items = []
        for item in self.order["breakdown"]:
            if not item.get("is_paid", False):
                unpaid_items.append(item)

        if not unpaid_items:
            messagebox.showinfo(information_title, no_unpaid_items_message)
            return

        # 创建删除对话框
        dialog = tk.Toplevel(self)
        dialog.title(dialog_title)
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

        tk.Label(scroll_frame, text=select_items_text,
                 font=("Arial", 11, "bold")).pack(anchor=tk.W, padx=10, pady=10)

        # 显示已付款商品的注释
        paid_items_count = len(self.order["breakdown"]) - len(unpaid_items)
        if paid_items_count > 0:
            note_text = note_text_pattern.format(count=paid_items_count)
            tk.Label(scroll_frame,
                     text=note_text,
                     fg="#e74c3c", font=("Arial", 9)).pack(anchor=tk.W, padx=10, pady=(0, 10))

        # 获取折扣信息的翻译模式
        discount_abbr_pattern = "Disc. {percentage}%"
        if self.translation_controller:
            discount_abbr_pattern = self.translation_controller.get_text(
                "views.order_management.discount_abbr",
                default=discount_abbr_pattern
            )

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
                discount_info = discount_abbr_pattern.format(percentage=item['discount_percentage'])
                price_info += f" ({discount_info})"

            info_text = f"{product_name} - {price_info} × {item['amount']}"
            tk.Label(item_frame, text=info_text).pack(side=tk.LEFT, padx=5)

            check_vars.append((item, var))

        def confirm_delete():
            to_delete = []
            for item, var in check_vars:
                if var.get():
                    to_delete.append(item)

            if not to_delete:
                messagebox.showwarning(warning_title, select_items_warning)
                return

            confirm_message = confirm_message_pattern.format(count=len(to_delete))
            if messagebox.askyesno(confirm_title, confirm_message):
                # 删除选中的商品
                for del_item in to_delete:
                    self.order["breakdown"].remove(del_item)

                self.controller.save_order(self.order)
                self.refresh_display()
                dialog.destroy()
                messagebox.showinfo(success_title, success_message)

        # 底部区域
        bottom_frame = tk.Frame(dialog, bg="#f5f6fa")
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # 按钮区域
        button_frame = tk.Frame(bottom_frame, bg="#f5f6fa")
        button_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        ttk.Button(button_frame, text=cancel_text, command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text=delete_text, command=confirm_delete).pack(side=tk.LEFT, padx=5)

        # 设置滚动区域
        scroll_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))


# 主应用视图
class EnhancedBartenderView(tk.Tk):
    def __init__(self, controller, translation_controller=None):
        super().__init__()
        self.controller = controller
        self.translation_controller = translation_controller  # 存储翻译控制器

        # 获取应用标题的翻译
        app_title = "Bar Management System"
        if self.translation_controller:
            app_title = self.translation_controller.get_text(
                "general.app_title",
                default=app_title
            )

        self.title(app_title)
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

        tk.Label(title_bar, text=app_title, font=("Arial", 14, "bold"),
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

        # 获取窗口标题的翻译
        app_title = "Bar Management System"
        current_orders_text = "Current Orders"
        window_title = f"{app_title} - {current_orders_text}"

        if self.translation_controller:
            app_title = self.translation_controller.get_text(
                "general.app_title",
                default=app_title
            )
            current_orders_text = self.translation_controller.get_text(
                "views.order_management.current_orders",
                default=current_orders_text
            )
            window_title = f"{app_title} - {current_orders_text}"

        self.title(window_title)
        self.current_list = OrderListView(
            self.container,
            self.controller,
            self,
            translation_controller=self.translation_controller  # 传递翻译控制器
        )
        self.current_list.pack(fill=tk.BOTH, expand=True)
        self.current_view = "current_list"

    # 显示历史订单列表视图
    def show_history_view(self):
        self.clear_container()

        # 获取窗口标题和其他文本的翻译
        app_title = "Bar Management System"
        order_history_text = "Order History"
        back_text = "← Back"
        no_history_orders_text = "No history orders"
        window_title = f"{app_title} - {order_history_text}"

        if self.translation_controller:
            app_title = self.translation_controller.get_text(
                "general.app_title",
                default=app_title
            )
            order_history_text = self.translation_controller.get_text(
                "views.order_management.order_history",
                default=order_history_text
            )
            back_text = self.translation_controller.get_text(
                "general.back",
                default=back_text
            )
            no_history_orders_text = self.translation_controller.get_text(
                "views.order_management.no_history_orders",
                default=no_history_orders_text
            )
            window_title = f"{app_title} - {order_history_text}"

        self.title(window_title)

        # 创建历史订单列表视图
        history_view = tk.Frame(self.container, bg="#f5f6fa")
        history_view.pack(fill=tk.BOTH, expand=True)

        # 标题栏和返回按钮
        header = tk.Frame(history_view, bg="#f5f6fa")
        header.pack(fill=tk.X, pady=5)

        ttk.Button(header, text=back_text,
                   command=self.show_list_view).pack(side=tk.LEFT, padx=10, pady=5)

        tk.Label(header, text=order_history_text,
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
            tk.Label(history_frame, text=no_history_orders_text,
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
                    width=350,
                    translation_controller=self.translation_controller  # 传递翻译控制器
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
            # 获取窗口标题的翻译
            app_title = "Bar Management System"
            order_history_text = "Order History"

            if self.translation_controller:
                app_title = self.translation_controller.get_text(
                    "general.app_title",
                    default=app_title
                )
                order_history_text = self.translation_controller.get_text(
                    "views.order_management.order_history",
                    default=order_history_text
                )

                # 获取"Table X"的翻译模式
                table_pattern = self.translation_controller.get_text(
                    "views.order_management.table",
                    default="Table: {table_id}"
                )
                # 从模式中提取出表号部分
                table_text = table_pattern.format(table_id=order['table_id']).replace("Table: ", "Table ")
                window_title = f"{app_title} - {order_history_text} ({table_text})"
            else:
                window_title = f"{app_title} - {order_history_text} (Table {order['table_id']})"

            self.title(window_title)
            detail_view = HistoryDetailView(
                self.container,
                self.controller,
                order,
                self,
                translation_controller=self.translation_controller  # 传递翻译控制器
            )
            detail_view.pack(fill=tk.BOTH, expand=True)
            self.current_view = "history_detail"
            self.current_transaction_id = transaction_id
        else:
            # 获取错误消息的翻译
            error_title = "Error"
            order_not_found_text = "Order not found"

            if self.translation_controller:
                error_title = self.translation_controller.get_text(
                    "dialogs.error",
                    default=error_title
                )
                order_not_found_text = self.translation_controller.get_text(
                    "dialogs.product_not_found",
                    default=order_not_found_text
                ).replace("Product", "Order")

            messagebox.showerror(error_title, order_not_found_text)
            self.show_history_view()

    # 显示当前订单详情视图
    def show_detail_view(self, transaction_id):
        self.clear_container()

        order = self.controller.get_order_by_transaction(transaction_id)
        if order:
            # 获取窗口标题的翻译
            app_title = "Bar Management System"
            order_details_text = "Order Details"

            if self.translation_controller:
                app_title = self.translation_controller.get_text(
                    "general.app_title",
                    default=app_title
                )
                order_details_text = self.translation_controller.get_text(
                    "views.order_management.order_details",
                    default=order_details_text
                )

                # 获取"Table X"的翻译模式
                table_pattern = self.translation_controller.get_text(
                    "views.order_management.table",
                    default="Table: {table_id}"
                )
                # 从模式中提取出表号部分
                table_text = table_pattern.format(table_id=order['table_id']).replace("Table: ", "Table ")
                window_title = f"{app_title} - {order_details_text} ({table_text})"
            else:
                window_title = f"{app_title} - {order_details_text} (Table {order['table_id']})"

            self.title(window_title)
            self.current_detail = OrderDetailView(
                self.container,
                self.controller,
                order,
                self,
                translation_controller=self.translation_controller  # 传递翻译控制器
            )
            self.current_detail.pack(fill=tk.BOTH, expand=True)
            self.current_view = "detail"
            self.current_transaction_id = transaction_id
        else:
            # 获取错误消息的翻译
            error_title = "Error"
            order_not_found_text = "Order not found"

            if self.translation_controller:
                error_title = self.translation_controller.get_text(
                    "dialogs.error",
                    default=error_title
                )
                order_not_found_text = self.translation_controller.get_text(
                    "dialogs.product_not_found",
                    default=order_not_found_text
                ).replace("Product", "Order")

            messagebox.showerror(error_title, order_not_found_text)
            self.show_list_view()