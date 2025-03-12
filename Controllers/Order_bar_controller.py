import json
import os
from tkinter import messagebox
from datetime import datetime


# Order controller class
class EnhancedOrderController:
    def __init__(self):
        # Use absolute path to point to the data file in the project root directory
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.ORDER_FILE = os.path.join(root_dir, "OrderDB.json")

        # Make sure directory exists
        if not os.path.exists(os.path.dirname(self.ORDER_FILE)):
            os.makedirs(os.path.dirname(self.ORDER_FILE), exist_ok=True)

    # Load all order data from file
    def load_orders(self):
        try:
            if os.path.exists(self.ORDER_FILE):
                file = open(self.ORDER_FILE, "r", encoding="utf-8")
                data = json.load(file)
                file.close()

                # Ensure return value is a list
                if isinstance(data, list):
                    return data
                else:
                    messagebox.showerror("Data Error", "Order data format incorrect, initializing new data")
                    return []
            return []
        except Exception as e:
            messagebox.showerror("Data Error", f"Failed to read order file: {str(e)}")
            return []

    # Get order by transaction ID
    def get_order_by_transaction(self, transaction_id):
        orders = self.load_orders()
        transaction_id_str = str(transaction_id)

        # Search for matching transaction
        for order in orders:
            if str(order.get("transaction_id", "")) == transaction_id_str:
                return order
        return None

    # Save order data to file
    def save_order(self, order_data):
        orders = self.load_orders()

        # Ensure ID is in string format
        order_data["transaction_id"] = str(order_data["transaction_id"])

        # Search for existing order with the same ID
        existing_index = -1
        for i in range(len(orders)):
            order = orders[i]
            if isinstance(order, dict):
                if str(order.get("transaction_id", "")) == order_data["transaction_id"]:
                    existing_index = i
                    break

        # Update or add order
        if existing_index != -1:
            orders[existing_index] = order_data
        else:
            orders.append(order_data)

        # Save to file
        try:
            file = open(self.ORDER_FILE, "w", encoding="utf-8")
            json.dump(orders, file, indent=4, ensure_ascii=False)
            file.close()
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save order data: {str(e)}")

    # Apply discount to items
    def apply_discount(self, order, discount_rate, product_ids=None):
        for item in order["breakdown"]:
            # Check if this item should have discount applied
            if product_ids is None or str(item["product_id"]) in product_ids:
                # Save original price
                if "original_price" not in item:
                    item["original_price"] = item["price"]

                # Calculate discount
                original_price = item["original_price"]
                new_price = round(original_price * (1 - discount_rate), 2)
                discount_amount = round(original_price - new_price, 2)
                discount_percentage = round(discount_rate * 100, 1)

                # Update item information
                item["price"] = new_price
                item["discount_percentage"] = discount_percentage
                item["discount_amount"] = discount_amount
        return order

    # Process partial checkout for selected items
    def partial_checkout(self, order, selected_ids):
        total_paid = 0
        # Process selected items
        for item in order["breakdown"]:
            if str(item["product_id"]) in selected_ids and not item.get("is_paid", False):
                item["is_paid"] = True
                total_paid += item["price"] * item["amount"]
        return order, total_paid

    # Get active orders (not fully paid)
    def get_active_orders(self):
        orders = self.load_orders()
        active_orders = []

        # Filter for orders that are not fully paid
        for o in orders:
            if isinstance(o, dict) and "breakdown" in o:
                all_paid = True
                for item in o["breakdown"]:
                    if not item.get("is_paid", False):
                        all_paid = False
                        break
                if not all_paid:
                    active_orders.append(o)

        return active_orders

    # Get history orders (fully paid)
    def get_history_orders(self):
        orders = self.load_orders()
        history_orders = []

        # Filter for orders that are fully paid
        for o in orders:
            if isinstance(o, dict) and "breakdown" in o:
                all_paid = True
                for item in o["breakdown"]:
                    if not item.get("is_paid", False):
                        all_paid = False
                        break
                if all_paid:
                    history_orders.append(o)

        return history_orders


# Initialize test data
def initialize_test_data():
    controller = EnhancedOrderController()

    # Basic test orders
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

    # Add detailed test data
    wine_sample = {
        "transaction_id": "1003",
        "table_id": "C5",
        "transaction_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "breakdown": [
            {"product_id": 201, "price": 68.0, "amount": 1, "specification": "Wine - Glass", "is_paid": False},
            {"product_id": 202, "price": 98.0, "amount": 1, "specification": "Whiskey", "is_paid": False},
            {"product_id": 203, "price": 38.0, "amount": 2, "specification": "Beer - Bottle", "is_paid": False},
            {"product_id": 301, "price": 58.0, "amount": 1, "specification": "Cocktail - Mojito", "is_paid": False},
            {"product_id": 302, "price": 62.0, "amount": 1, "specification": "Cocktail - Margarita", "is_paid": False},
            {"product_id": 401, "price": 88.0, "amount": 1, "specification": "Food - Snack Platter", "is_paid": False},
            {"product_id": 402, "price": 35.0, "amount": 2, "specification": "Food - French Fries", "is_paid": False}
        ]
    }

    test_orders.append(wine_sample)

    # Save test data
    for order in test_orders:
        controller.save_order(order)
    print("Test data initialized")


# If running this file directly, only initialize test data
if __name__ == "__main__":
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(root_dir, "OrderDB.json")
    if not os.path.exists(db_path):
        initialize_test_data()
        print("Test data initialization complete, please run the main program to start the application.")