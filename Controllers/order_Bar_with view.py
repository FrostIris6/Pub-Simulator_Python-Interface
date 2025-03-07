import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
import copy


# ================== Controller模块 ==================
class EnhancedOrderController:
    def __init__(self):
        self.ORDER_FILE = "OrderDB.json"  # 使用相对路径
        os.makedirs(os.path.dirname(self.ORDER_FILE) if os.path.dirname(self.ORDER_FILE) else ".", exist_ok=True)

    def load_orders(self):
        """Load all order data"""
        try:
            if os.path.exists(self.ORDER_FILE):
                with open(self.ORDER_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # 确保返回的是列表类型
                    if isinstance(data, list):
                        return data
                    else:
                        messagebox.showerror("Data Error", "Order data format is incorrect. Initializing new data.")
                        return []
            return []
        except Exception as e:
            messagebox.showerror("Data Error", f"Failed to read order file: {str(e)}")
            return []

    def get_order_by_transaction(self, transaction_id):
        """Get order by transaction ID"""
        orders = self.load_orders()
        # 确保将transaction_id转换为字符串进行比较
        transaction_id_str = str(transaction_id)
        for order in orders:
            if str(order.get("transaction_id", "")) == transaction_id_str:
                return order
        return None

    def save_order(self, order_data):
        """Save order data"""
        orders = self.load_orders()

        # 确保transaction_id是字符串格式
        order_data["transaction_id"] = str(order_data["transaction_id"])

        # 检查是否存在相同交易ID的订单
        existing_index = -1
        for i, order in enumerate(orders):
            if isinstance(order, dict) and str(order.get("transaction_id", "")) == order_data["transaction_id"]:
                existing_index = i
                break

        if existing_index != -1:
            orders[existing_index] = order_data
        else:
            orders.append(order_data)

        try:
            with open(self.ORDER_FILE, "w", encoding="utf-8") as f:
                json.dump(orders, f, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save order data: {str(e)}")

    def apply_discount(self, order, discount_rate, product_ids=None):
        """Apply discount to items"""
        for item in order["breakdown"]:
            if product_ids is None or str(item["product_id"]) in product_ids:
                # Save original price
                if "original_price" not in item:
                    item["original_price"] = item["price"]

                # Calculate and save discount info
                original_price = item["original_price"]
                new_price = round(original_price * (1 - discount_rate), 2)
                discount_amount = round(original_price - new_price, 2)
                discount_percentage = round(discount_rate * 100, 1)

                item["price"] = new_price
                item["discount_percentage"] = discount_percentage
                item["discount_amount"] = discount_amount
        return order

    def partial_checkout(self, order, selected_ids):
        """Partial checkout for selected items"""
        total_paid = 0
        for item in order["breakdown"]:
            if str(item["product_id"]) in selected_ids and not item.get("is_paid", False):
                item["is_paid"] = True
                total_paid += item["price"] * item["amount"]
        return order, total_paid

    def get_active_orders(self):
        """Get active orders (not fully paid)"""
        orders = self.load_orders()
        return [o for o in orders if isinstance(o, dict) and "breakdown" in o and not all(
            item.get("is_paid", False) for item in o["breakdown"])]

    def get_history_orders(self):
        """Get history orders (fully paid)"""
        orders = self.load_orders()
        return [o for o in orders if
                isinstance(o, dict) and "breakdown" in o and all(item.get("is_paid", False) for item in o["breakdown"])]


# ================== 自定义组件 ==================
class OrderCard(tk.Frame):
    """Order card component"""

    def __init__(self, parent, order, on_click=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.order = order
        self.on_click = on_click

        # Set card style
        self.config(relief=tk.RAISED, borderwidth=1, padx=10, pady=10)
        self.bind("<Button-1>", self._on_click)

        # Calculate total amount
        total = sum(item["price"] * item["amount"] for item in order["breakdown"])

        # Card title - Table number
        title_frame = tk.Frame(self)
        title_frame.pack(fill=tk.X, pady=(0, 5))

        tk.Label(title_frame, text=f"Table: {order['table_id']}",
                 font=("Arial", 12, "bold")).pack(side=tk.LEFT)

        # Order time
        tk.Label(self, text=f"Time: {order['transaction_time']}",
                 font=("Arial", 10)).pack(anchor=tk.W)

        # Order status
        is_completed = all(item.get("is_paid", False) for item in order["breakdown"])
        status = "Completed" if is_completed else "In Progress"
        status_color = "#27ae60" if is_completed else "#e74c3c"  # Green for completed, Red for in progress

        status_frame = tk.Frame(self)
        status_frame.pack(fill=tk.X, pady=5)

        tk.Label(status_frame, text=f"Status: ",
                 font=("Arial", 10)).pack(side=tk.LEFT)
        tk.Label(status_frame, text=status, fg=status_color,
                 font=("Arial", 10, "bold")).pack(side=tk.LEFT)

        # Total price
        tk.Label(self, text=f"Total: ¥{total:.2f}",
                 font=("Arial", 11)).pack(anchor=tk.E)

    def _on_click(self, event):
        """Handle click event"""
        if self.on_click:
            self.on_click(self.order["transaction_id"])


# ================== View模块 ==================
class OrderListView(ttk.Frame):
    def __init__(self, parent, controller, main_window):
        super().__init__(parent)
        self.controller = controller
        self.main_window = main_window
        self.create_widgets()
        self.load_orders()

    def create_widgets(self):
        """Create UI widgets"""
        # Top toolbar
        toolbar = tk.Frame(self, bg="#f5f6fa")
        toolbar.pack(fill=tk.X, pady=5)

        ttk.Button(toolbar, text="Refresh", command=self.load_orders).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="History", command=self.show_history).pack(side=tk.LEFT, padx=5)

        # Title
        title_frame = tk.Frame(self, bg="#f5f6fa")
        title_frame.pack(fill=tk.X, pady=10)
        tk.Label(title_frame, text="Current Orders", font=("Arial", 14, "bold"),
                 bg="#f5f6fa").pack(pady=5)

        # Create scroll container for order cards
        self.canvas = tk.Canvas(self, bg="white")
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # Create Frame container for cards
        self.cards_frame = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window((0, 0), window=self.cards_frame, anchor="nw")

        # Bind resize events
        self.cards_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

    def _on_frame_configure(self, event):
        """Adjust scroll region"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """Adjust internal frame width to fit canvas"""
        self.canvas.itemconfig(self.canvas.find_withtag("all")[0], width=event.width)

    def load_orders(self):
        """Load order data"""
        # Clear existing cards
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        orders = self.controller.get_active_orders()

        if not orders:
            # Show no orders message
            tk.Label(self.cards_frame, text="No active orders",
                     font=("Arial", 12), bg="white").pack(pady=20)
            return

        # Add order cards
        for order in orders:
            card = OrderCard(
                self.cards_frame,
                order,
                on_click=self.main_window.show_detail_view,
                bg="white",
                width=350  # Fixed width
            )
            card.pack(fill=tk.X, pady=5, padx=10, ipadx=5, ipady=5)

    def show_history(self):
        """Show history orders"""
        # Notify main window to show history view
        self.main_window.show_history_view()


class HistoryDetailView(ttk.Frame):
    """History order detail view"""

    def __init__(self, parent, controller, order, main_window):
        super().__init__(parent)
        self.controller = controller
        self.order = order
        self.main_window = main_window  # Reference to main window instance
        self.create_widgets()
        self.refresh_display()

    def create_widgets(self):
        """Create UI widgets"""
        # Top navigation bar
        header = tk.Frame(self, bg="#f5f6fa")
        header.pack(fill=tk.X)

        # Back button
        back_btn = ttk.Button(header, text="← Back", command=self.return_to_history)
        back_btn.pack(side=tk.LEFT, padx=10, pady=10)

        # Table number title
        title_frame = tk.Frame(header, bg="#f5f6fa")
        title_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20)

        tk.Label(title_frame, text=f"Table {self.order['table_id']}",
                 font=("Arial", 14, "bold"), bg="#f5f6fa").pack(side=tk.LEFT)

        # Create scroll container
        self.canvas = tk.Canvas(self, bg="white")
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # Create Frame container for order details
        self.detail_frame = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window((0, 0), window=self.detail_frame, anchor="nw")

        # Bind resize events
        self.detail_frame.bind("<Configure>",
                               lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>",
                         lambda e: self.canvas.itemconfig(self.canvas.find_withtag("all")[0], width=e.width))

        # Bottom area - left aligned total and back button
        self.bottom_frame = tk.Frame(self, bg="#f5f6fa")
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Create left side for total and back button
        bottom_left = tk.Frame(self.bottom_frame, bg="#f5f6fa")
        bottom_left.pack(side=tk.LEFT, padx=15, pady=10, fill=tk.Y)

        # Total amount
        self.total_label = tk.Label(bottom_left, text="Total: ¥0.00",
                                    font=("Arial", 14, "bold"), bg="#f5f6fa")
        self.total_label.pack(anchor=tk.W)

        # Back button
        ttk.Button(bottom_left, text="Back",
                   command=self.return_to_history).pack(anchor=tk.W, pady=5)

    def return_to_history(self):
        """Return to history order list"""
        self.main_window.show_history_view()

    def refresh_data(self):
        """Refresh data"""
        self.order = self.controller.get_order_by_transaction(self.order["transaction_id"])
        self.refresh_display()

    def refresh_display(self):
        """Refresh display"""
        # Clear existing content
        for widget in self.detail_frame.winfo_children():
            widget.destroy()

        # Organize items by category
        categories = {}

        # Translation dictionary for product specifications
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
            cat_name = "Drinks"  # Default category

            # Translate specification if in Chinese
            if "specification" in item:
                spec = item["specification"]
                # Check if we need to translate the specification
                for cn, en in translations.items():
                    if cn in spec:
                        spec = spec.replace(cn, en)
                # Update the specification with English version
                item["specification"] = spec

                # Categorize based on specification
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

        # Display each category
        for cat_name, items in categories.items():
            if items:  # Only show categories with items
                self.create_item_section(cat_name, items)

        # Calculate total amount
        total = sum(item["price"] * item["amount"] for item in self.order["breakdown"])
        self.total_label.config(text=f"Total: ¥{total:.2f}")

    def create_item_section(self, category, items):
        """Create category item section"""
        # Create category title Frame
        section_frame = tk.Frame(self.detail_frame, bg="white")
        section_frame.pack(fill=tk.X, pady=5)

        # Category title
        tk.Label(section_frame, text=category,
                 font=("Arial", 12, "bold"), bg="white").pack(anchor=tk.W, padx=10, pady=5)

        # Iterate through items in category
        for item in items:
            # Item status
            status = "Paid" if item.get("is_paid", False) else ""
            bg_color = "#ebf5eb" if item.get("is_paid", False) else "white"

            # Create item Frame
            item_frame = tk.Frame(self.detail_frame, bg=bg_color)
            item_frame.pack(fill=tk.X, padx=5, pady=2)

            # Left side info
            left_frame = tk.Frame(item_frame, bg=bg_color)
            left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=8)

            # Product name and specification
            product_name = f"Item {item['product_id']}"
            if "specification" in item and item["specification"]:
                product_name = item["specification"]

            tk.Label(left_frame, text=product_name,
                     font=("Arial", 11), bg=bg_color).pack(anchor=tk.W)

            # Display discount info
            if "discount_percentage" in item:
                discount_info = f"Discount {item['discount_percentage']}%"
                tk.Label(left_frame, text=discount_info, fg="#e67e22",
                         font=("Arial", 9), bg=bg_color).pack(anchor=tk.W)

            # Right side info
            right_frame = tk.Frame(item_frame, bg=bg_color)
            right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=8)

            # Display price
            price_text = f"¥ {item['price']:.2f}"
            if "original_price" in item and item["original_price"] != item["price"]:
                price_text = f"¥ {item['price']:.2f}"  # Actual price

            tk.Label(right_frame, text=price_text,
                     font=("Arial", 11), bg=bg_color).pack(side=tk.RIGHT)

            # Display quantity
            qty_frame = tk.Frame(right_frame, bg=bg_color)
            qty_frame.pack(side=tk.RIGHT, padx=20)

            tk.Label(qty_frame, text=f"× {item['amount']}",
                     font=("Arial", 11), bg=bg_color).pack()


class OrderDetailView(ttk.Frame):
    def __init__(self, parent, controller, order, main_window):
        super().__init__(parent)
        self.controller = controller
        self.order = order
        self.main_window = main_window
        self.selected_items = {}  # 用于存储选中的商品
        self.create_widgets()
        self.refresh_display()

    def create_widgets(self):
        """Create UI widgets"""
        # Top navigation bar
        header = tk.Frame(self, bg="#f5f6fa")
        header.pack(fill=tk.X)

        # Back button
        back_btn = ttk.Button(header, text="← Back",
                              command=self.main_window.show_list_view)
        back_btn.pack(side=tk.LEFT, padx=10, pady=10)

        # Table number title
        title_frame = tk.Frame(header, bg="#f5f6fa")
        title_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20)

        tk.Label(title_frame, text=f"Table {self.order['table_id']}",
                 font=("Arial", 14, "bold"), bg="#f5f6fa").pack(side=tk.LEFT)

        # Add and delete buttons on the right
        btn_frame = tk.Frame(header, bg="#f5f6fa")
        btn_frame.pack(side=tk.RIGHT, padx=10)

        # Add item button (+ icon)
        add_btn = tk.Button(btn_frame, text="+", font=("Arial", 12, "bold"),
                            width=2, command=self.show_add_item_dialog,
                            bg="#2ecc71", fg="white", relief=tk.FLAT)
        add_btn.pack(side=tk.RIGHT, padx=5, pady=10)

        # Delete item button (- icon)
        del_btn = tk.Button(btn_frame, text="−", font=("Arial", 12, "bold"),
                            width=2, command=self.delete_selected_items,
                            bg="#e74c3c", fg="white", relief=tk.FLAT)
        del_btn.pack(side=tk.RIGHT, padx=5, pady=10)

        # 折扣面板 - 添加到主窗口
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

        # Main operation buttons - compact icon buttons
        self.toolbar = tk.Frame(self)
        self.toolbar.pack(fill=tk.X, pady=5)

        ttk.Button(self.toolbar, text="Partial Checkout", command=self.show_checkout_dialog).pack(side=tk.LEFT, padx=5)

        # Create scroll container
        self.canvas = tk.Canvas(self, bg="white")
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # Create Frame container for order details
        self.detail_frame = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window((0, 0), window=self.detail_frame, anchor="nw")

        # Bind resize events
        self.detail_frame.bind("<Configure>",
                               lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>",
                         lambda e: self.canvas.itemconfig(self.canvas.find_withtag("all")[0], width=e.width))

        # Bottom checkout area
        self.bottom_frame = tk.Frame(self, bg="#f5f6fa")
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Create left side for total and buttons
        bottom_left = tk.Frame(self.bottom_frame, bg="#f5f6fa")
        bottom_left.pack(side=tk.LEFT, padx=15, pady=10, fill=tk.Y)

        # Total info
        self.total_label = tk.Label(bottom_left, text="To Pay: ¥0.00",
                                    font=("Arial", 14, "bold"), bg="#f5f6fa")
        self.total_label.pack(anchor=tk.W)

        # Button area
        button_frame = tk.Frame(bottom_left, bg="#f5f6fa")
        button_frame.pack(anchor=tk.W, pady=5)

        # Checkout button
        self.checkout_btn = ttk.Button(button_frame, text="Checkout",
                                       command=self.full_checkout)
        self.checkout_btn.pack(side=tk.LEFT, padx=5)

        # Cancel button - call cancel checkout function
        self.cancel_btn = ttk.Button(button_frame, text="Cancel",
                                     command=self.cancel_checkout)
        self.cancel_btn.pack(side=tk.LEFT, padx=5)

        # Back button
        ttk.Button(button_frame, text="Back",
                   command=self.main_window.show_list_view).pack(side=tk.LEFT, padx=5)

    def create_item_section(self, category, items):
        """Create category item section"""
        # Create category title Frame
        section_frame = tk.Frame(self.detail_frame, bg="white")
        section_frame.pack(fill=tk.X, pady=5)

        # Category title
        tk.Label(section_frame, text=category,
                 font=("Arial", 12, "bold"), bg="white").pack(anchor=tk.W, padx=10, pady=5)

        # Iterate through items in category
        for item in items:
            # Item status
            is_paid = item.get("is_paid", False)
            status = "Paid" if is_paid else ""
            bg_color = "#ebf5eb" if is_paid else "white"

            # Create item Frame
            item_frame = tk.Frame(self.detail_frame, bg=bg_color)
            item_frame.pack(fill=tk.X, padx=5, pady=2)

            # Selection checkbox - only show for unpaid items
            if not is_paid:
                # 创建选择变量
                item_id = str(item["product_id"])
                if item_id not in self.selected_items:
                    self.selected_items[item_id] = tk.BooleanVar(value=False)

                check = ttk.Checkbutton(item_frame, variable=self.selected_items[item_id])
                check.pack(side=tk.LEFT, padx=2)

            # Left side info
            left_frame = tk.Frame(item_frame, bg=bg_color)
            left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5 if not is_paid else 10, pady=8)

            # Product name and specification
            product_name = f"Item {item['product_id']}"
            if "specification" in item and item["specification"]:
                product_name = item["specification"]

            tk.Label(left_frame, text=product_name,
                     font=("Arial", 11), bg=bg_color).pack(anchor=tk.W)

            # Display discount info
            if "discount_percentage" in item:
                discount_info = f"Discount {item['discount_percentage']}%"
                tk.Label(left_frame, text=discount_info, fg="#e67e22",
                         font=("Arial", 9), bg=bg_color).pack(anchor=tk.W)

            # Right side info
            right_frame = tk.Frame(item_frame, bg=bg_color)
            right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=8)

            # Display price
            price_text = f"¥ {item['price']:.2f}"
            if "original_price" in item and item["original_price"] != item["price"]:
                price_text = f"¥ {item['price']:.2f}"  # Actual price

            tk.Label(right_frame, text=price_text,
                     font=("Arial", 11), bg=bg_color).pack(side=tk.RIGHT)

            # Display quantity
            qty_frame = tk.Frame(right_frame, bg=bg_color)
            qty_frame.pack(side=tk.RIGHT, padx=20)

            tk.Label(qty_frame, text=f"× {item['amount']}",
                     font=("Arial", 11), bg=bg_color).pack()

    def apply_selected_discount(self):
        """应用选定的折扣"""
        try:
            # 获取折扣率
            discount_rate = float(self.discount_entry.get()) / 100
            if not 0 <= discount_rate <= 1:
                raise ValueError

            # 收集选中的商品ID
            selected_ids = [pid for pid, var in self.selected_items.items() if var.get()]

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

    def clear_item_selection(self):
        """清除所有项目的选择"""
        for var in self.selected_items.values():
            var.set(False)

    def refresh_data(self):
        """Refresh data"""
        self.order = self.controller.get_order_by_transaction(self.order["transaction_id"])
        self.refresh_display()

    def refresh_display(self):
        """Refresh display"""
        # 保存当前选择状态
        current_selection = {pid: var.get() for pid, var in self.selected_items.items()}

        # Clear existing content
        for widget in self.detail_frame.winfo_children():
            widget.destroy()

        # 重置选择状态字典
        self.selected_items = {}
        for pid, selected in current_selection.items():
            self.selected_items[pid] = tk.BooleanVar(value=selected)

        # Organize items by category
        categories = {}
        # Filter unpaid items
        unpaid_items = [item for item in self.order["breakdown"] if not item.get("is_paid", False)]

        # Translation dictionary for product specifications
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
            cat_name = "Drinks"  # Default category

            # Translate specification if in Chinese
            if "specification" in item:
                spec = item["specification"]
                # Check if we need to translate the specification
                for cn, en in translations.items():
                    if cn in spec:
                        spec = spec.replace(cn, en)
                # Update the specification with English version
                item["specification"] = spec

                # Categorize based on specification
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

        # Already paid items
        checked_out_items = [item for item in self.order["breakdown"] if item.get("is_paid", False)]
        if checked_out_items:
            # Also translate paid items
            for item in checked_out_items:
                if "specification" in item:
                    spec = item["specification"]
                    for cn, en in translations.items():
                        if cn in spec:
                            spec = spec.replace(cn, en)
                    item["specification"] = spec
            categories["Paid Items"] = checked_out_items

        # Display each category
        for cat_name, items in categories.items():
            if items:  # Only show categories with items
                self.create_item_section(cat_name, items)

        # Calculate total amount
        total = sum(item["price"] * item["amount"]
                    for item in self.order["breakdown"]
                    if not item.get("is_paid", False))

        # Update total amount display
        self.total_label.config(text=f"To Pay: ¥{total:.2f}")

    def full_checkout(self):
        """Full checkout"""
        unpaid_ids = [str(item["product_id"])
                      for item in self.order["breakdown"]
                      if not item.get("is_paid", False)]

        if not unpaid_ids:
            messagebox.showinfo("Info", "All items are already paid")
            return

        self.order, total = self.controller.partial_checkout(self.order, unpaid_ids)
        self.controller.save_order(self.order)
        self.refresh_display()
        messagebox.showinfo("Success", f"Successfully checked out ¥{total:.2f}")

    def show_checkout_dialog(self):
        """Show checkout dialog"""
        dialog = tk.Toplevel(self)
        dialog.title("Select Items to Checkout")
        dialog.geometry("350x400")
        dialog.transient(self)  # Set as temporary window of parent
        dialog.grab_set()  # Modal dialog
        dialog.resizable(False, False)  # Prevent resizing

        # Scrollable area
        main_frame = tk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

        # Load checkable items
        check_vars = []
        unpaid_items = [item for item in self.order["breakdown"] if not item.get("is_paid", False)]

        # Update total amount display
        def update_total_display():
            selected_ids = [pid for pid, var in check_vars if var.get()]
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
                var = tk.BooleanVar(value=True)  # Default selected

                # Show discount info (if any)
                discount_info = ""
                if "discount_percentage" in item:
                    discount_info = f" (Discount {item['discount_percentage']}%)"

                item_frame = tk.Frame(scroll_frame)
                item_frame.pack(fill=tk.X, padx=10, pady=2)

                cb = ttk.Checkbutton(item_frame, variable=var,
                                     command=update_total_display)  # Add command callback
                cb.pack(side=tk.LEFT)

                # Item info
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

            selected_ids = [pid for pid, var in check_vars if var.get()]
            if not selected_ids:
                messagebox.showwarning("Warning", "Please select at least one item")
                return

            self.order, total = self.controller.partial_checkout(self.order, selected_ids)
            self.controller.save_order(self.order)
            self.refresh_display()
            dialog.destroy()
            messagebox.showinfo("Success", f"Successfully checked out ¥{total:.2f}")

        # Bottom area
        bottom_frame = tk.Frame(dialog, bg="#f5f6fa")
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Checkout total amount display
        total_label = tk.Label(bottom_frame, text="To Pay: ¥0.00",
                               font=("Arial", 12, "bold"), bg="#f5f6fa")
        total_label.pack(side=tk.LEFT, padx=15, pady=10)

        # Initialize total amount display
        if unpaid_items:
            update_total_display()

        # Button area
        button_frame = tk.Frame(bottom_frame, bg="#f5f6fa")
        button_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Confirm", command=confirm_checkout).pack(side=tk.LEFT, padx=5)

        # Set scrollable area
        scroll_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def cancel_checkout(self):
        """Cancel checkout - reset all items to unpaid status"""
        if messagebox.askyesno("Confirm", "Are you sure you want to reset all item payment status?"):
            for item in self.order["breakdown"]:
                item["is_paid"] = False
            self.controller.save_order(self.order)
            self.refresh_display()
            messagebox.showinfo("Success", "All payment status has been reset")

    def show_add_item_dialog(self):
        """Show add item dialog"""
        dialog = tk.Toplevel(self)
        dialog.title("Add New Item")
        dialog.geometry("300x250")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        # Input fields
        fields = [
            ("Product ID:", "product_id"),
            ("Specification:", "specification"),
            ("Price:", "price"),
            ("Quantity:", "amount")
        ]
        entries = {}

        # Title
        tk.Label(dialog, text="Add New Item",
                 font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        for i, (label, field) in enumerate(fields, 1):
            tk.Label(dialog, text=label).grid(row=i, column=0, padx=15, pady=8, sticky=tk.W)
            entry = ttk.Entry(dialog, width=25)
            entry.grid(row=i, column=1, padx=5, pady=8, sticky=tk.W)
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

        # Button area
        button_frame = tk.Frame(dialog)
        button_frame.grid(row=len(fields) + 1, column=0, columnspan=2, pady=15)

        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Add", command=add_item).pack(side=tk.LEFT, padx=5)

    def delete_selected_items(self):
        """Delete selected items"""
        # 筛选未付款的商品
        unpaid_items = [item for item in self.order["breakdown"] if not item.get("is_paid", False)]

        if not unpaid_items:
            messagebox.showinfo("Information", "There are no unpaid items to delete. Paid items cannot be deleted.")
            return

        # Need a dialog to select items
        dialog = tk.Toplevel(self)
        dialog.title("Select Items to Delete")
        dialog.geometry("350x400")
        dialog.transient(self)
        dialog.grab_set()

        # Main frame
        main_frame = tk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Scrollable area
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

        # Load deletable items
        check_vars = []

        tk.Label(scroll_frame, text="Select unpaid items to delete:",
                 font=("Arial", 11, "bold")).pack(anchor=tk.W, padx=10, pady=10)

        # 显示已付款商品的注释
        paid_items_count = len(self.order["breakdown"]) - len(unpaid_items)
        if paid_items_count > 0:
            tk.Label(scroll_frame,
                     text=f"Note: {paid_items_count} paid items are not shown as they cannot be deleted.",
                     fg="#e74c3c", font=("Arial", 9)).pack(anchor=tk.W, padx=10, pady=(0, 10))

        for item in unpaid_items:
            var = tk.BooleanVar(value=False)

            item_frame = tk.Frame(scroll_frame)
            item_frame.pack(fill=tk.X, padx=10, pady=2)

            cb = ttk.Checkbutton(item_frame, variable=var)
            cb.pack(side=tk.LEFT)

            # Item info
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
            to_delete = [item for item, var in check_vars if var.get()]

            if not to_delete:
                messagebox.showwarning("Warning", "Please select items to delete")
                return

            if messagebox.askyesno("Confirm", f"Are you sure you want to delete {len(to_delete)} selected items?"):
                # Delete selected items
                for del_item in to_delete:
                    self.order["breakdown"].remove(del_item)

                self.controller.save_order(self.order)
                self.refresh_display()
                dialog.destroy()
                messagebox.showinfo("Success", "Selected items deleted")

        # Bottom area with fixed button bar
        bottom_frame = tk.Frame(dialog, bg="#f5f6fa")
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Button area
        button_frame = tk.Frame(bottom_frame, bg="#f5f6fa")
        button_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", command=confirm_delete).pack(side=tk.LEFT, padx=5)

        # Set scrollable area
        scroll_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))


class EnhancedBartenderView(tk.Tk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("Bar Management System")
        self.geometry("400x700")  # Set to rectangle, like a sidebar

        # Set overall style
        self.configure(bg="#f5f6fa")
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 10))
        self.style.configure("TLabel", font=("Arial", 10))
        self.style.configure("Total.TLabel", font=("Arial", 14, "bold"), foreground="#27ae60")

        # Top title bar
        title_bar = tk.Frame(self, bg="#f5f6fa")
        title_bar.pack(fill=tk.X, pady=5)

        tk.Label(title_bar, text="Bar Management System", font=("Arial", 14, "bold"),
                 bg="#f5f6fa").pack(pady=5)

        # Main container
        self.container = tk.Frame(self, bg="#f5f6fa")
        self.container.pack(fill=tk.BOTH, expand=True)

        # Current view can be "current_list", "history_list", "detail", "history_detail"
        self.current_view = None
        self.current_transaction_id = None

        self.show_list_view()

    def clear_container(self):
        """Clear main container"""
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_list_view(self):
        """Show current order list view"""
        self.clear_container()
        self.title("Bar Management System - Current Orders")
        self.current_list = OrderListView(self.container, self.controller, self)
        self.current_list.pack(fill=tk.BOTH, expand=True)
        self.current_view = "current_list"

    def show_history_view(self):
        """Show history order list view"""
        self.clear_container()
        self.title("Bar Management System - Order History")

        # Create history order list view
        history_view = tk.Frame(self.container, bg="#f5f6fa")
        history_view.pack(fill=tk.BOTH, expand=True)

        # Title bar and back button
        header = tk.Frame(history_view, bg="#f5f6fa")
        header.pack(fill=tk.X, pady=5)

        ttk.Button(header, text="← Back",
                   command=self.show_list_view).pack(side=tk.LEFT, padx=10, pady=5)

        tk.Label(header, text="Order History",
                 font=("Arial", 14, "bold"), bg="#f5f6fa").pack(side=tk.LEFT, padx=20, pady=5)

        # Create scroll container
        canvas = tk.Canvas(history_view, bg="white")
        scrollbar = ttk.Scrollbar(history_view, orient="vertical", command=canvas.yview)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # Create Frame container for cards
        history_frame = tk.Frame(canvas, bg="white")
        canvas.create_window((0, 0), window=history_frame, anchor="nw")

        orders = self.controller.get_history_orders()

        if not orders:
            tk.Label(history_frame, text="No history orders",
                     font=("Arial", 12), bg="white").pack(pady=20)
        else:
            # Add history order cards
            for order in orders:
                card = OrderCard(
                    history_frame,
                    order,
                    on_click=lambda tid=order["transaction_id"]: self.show_history_detail_view(tid),
                    bg="white",
                    width=350
                )
                card.pack(fill=tk.X, pady=5, padx=10)

        # Bind resize events
        history_frame.bind("<Configure>",
                           lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(canvas.find_withtag("all")[0], width=e.width))

        self.current_view = "history_list"

    def show_history_detail_view(self, transaction_id):
        """Show history order detail view"""
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

    def show_detail_view(self, transaction_id):
        """Show current order detail view"""
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


# ================== Initialize test data ==================
def initialize_test_data():
    controller = EnhancedOrderController()

    test_orders = [
        {
            "transaction_id": "1001",
            "table_id": "A2",
            "transaction_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "breakdown": [
                {"product_id": 101, "price": 32.0, "amount": 1, "specification": "Wine - Glass"},
                {"product_id": 102, "price": 20.0, "amount": 1, "specification": "Beer - Bottle"},
                {"product_id": 103, "price": 45.0, "amount": 1, "specification": "Cocktail"},
                {"product_id": 104, "price": 145.0, "amount": 1, "specification": "Food"}
            ]
        },
        {
            "transaction_id": "1002",
            "table_id": "B3",
            "transaction_time": "2024-01-01 18:00:00",
            "breakdown": [
                {"product_id": 201, "price": 60.0, "amount": 3, "is_paid": True, "specification": "Beer"},
                {"product_id": 301, "price": 120.0, "amount": 1, "is_paid": True, "specification": "Whiskey"}
            ]
        }
    ]

    # 添加您之前提供的测试数据作为第三个订单
    wine_sample = {
        "transaction_id": "1003",
        "table_id": "C5",
        "transaction_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "breakdown": [
            {"product_id": 201, "price": 68.0, "amount": 1, "specification": "红酒 - Wine - Glass", "is_paid": False},
            {"product_id": 202, "price": 98.0, "amount": 1, "specification": "威士忌 - Whiskey", "is_paid": False},
            {"product_id": 203, "price": 38.0, "amount": 2, "specification": "啤酒 - Beer - Bottle", "is_paid": False},
            {"product_id": 301, "price": 58.0, "amount": 1, "specification": "鸡尾酒 - Mojito", "is_paid": False},
            {"product_id": 302, "price": 62.0, "amount": 1, "specification": "鸡尾酒 - Margarita", "is_paid": False},
            {"product_id": 401, "price": 88.0, "amount": 1, "specification": "食品 - Snack Platter", "is_paid": False},
            {"product_id": 402, "price": 35.0, "amount": 2, "specification": "食品 - French Fries", "is_paid": False}
        ]
    }

    test_orders.append(wine_sample)

    for order in test_orders:
        controller.save_order(order)
    print("Test data initialized")


if __name__ == "__main__":
    if not os.path.exists("OrderDB.json"):
        initialize_test_data()

    controller = EnhancedOrderController()
    app = EnhancedBartenderView(controller)
    app.mainloop()