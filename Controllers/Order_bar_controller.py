import json
import os
from tkinter import messagebox
from datetime import datetime

# 导入BarModel从Models目录
import sys

models_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Models")
if models_path not in sys.path:
    sys.path.append(models_path)
from Models.BarModel import BarModel


# Order controller class
class EnhancedOrderController:
    def __init__(self):
        # 使用绝对路径指向项目根目录中的数据文件
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.ORDER_FILE = os.path.join(root_dir, "OrderDB.json")

        # 确保目录存在
        if not os.path.exists(os.path.dirname(self.ORDER_FILE)):
            os.makedirs(os.path.dirname(self.ORDER_FILE), exist_ok=True)

        # 初始化并运行数据库合并
        try:
            # 创建BarModel实例进行数据库合并
            self.model = BarModel(
                source_path=os.path.join(root_dir, "Database", "OrderDB.json"),
                target_path=self.ORDER_FILE
            )
            # 自动合并在BarModel初始化时已执行
        except Exception as e:
            messagebox.showwarning("数据库合并警告", f"数据库合并过程中发生错误: {str(e)}\n应用程序将继续使用现有数据。")

    # 加载所有订单数据
    def load_orders(self):
        try:
            if os.path.exists(self.ORDER_FILE):
                file = open(self.ORDER_FILE, "r", encoding="utf-8")
                data = json.load(file)
                file.close()

                # 确保返回值是列表
                if isinstance(data, list):
                    return data
                else:
                    messagebox.showerror("数据错误", "订单数据格式不正确，初始化新数据")
                    return []
            return []
        except Exception as e:
            messagebox.showerror("数据错误", f"读取订单文件失败: {str(e)}")
            return []

    # 根据交易ID获取订单
    def get_order_by_transaction(self, transaction_id):
        orders = self.load_orders()
        transaction_id_str = str(transaction_id)

        # 搜索匹配的交易
        for order in orders:
            if str(order.get("transaction_id", "")) == transaction_id_str:
                return order
        return None

    # 将订单数据保存到文件
    def save_order(self, order_data):
        orders = self.load_orders()

        # 确保ID是字符串格式
        order_data["transaction_id"] = str(order_data["transaction_id"])

        # 搜索具有相同ID的现有订单
        existing_index = -1
        for i in range(len(orders)):
            order = orders[i]
            if isinstance(order, dict):
                if str(order.get("transaction_id", "")) == order_data["transaction_id"]:
                    existing_index = i
                    break

        # 更新或添加订单
        if existing_index != -1:
            orders[existing_index] = order_data
        else:
            orders.append(order_data)

        # 保存到文件
        try:
            file = open(self.ORDER_FILE, "w", encoding="utf-8")
            json.dump(orders, file, indent=4, ensure_ascii=False)
            file.close()
        except Exception as e:
            messagebox.showerror("保存错误", f"保存订单数据失败: {str(e)}")

    # 应用折扣到商品
    def apply_discount(self, order, discount_rate, product_ids=None):
        for item in order["breakdown"]:
            # 检查此商品是否应该应用折扣
            if product_ids is None or str(item["product_id"]) in product_ids:
                # 保存原始价格
                if "original_price" not in item:
                    item["original_price"] = item["price"]

                # 计算折扣
                original_price = item["original_price"]
                new_price = round(original_price * (1 - discount_rate), 2)
                discount_amount = round(original_price - new_price, 2)
                discount_percentage = round(discount_rate * 100, 1)

                # 更新商品信息
                item["price"] = new_price
                item["discount_percentage"] = discount_percentage
                item["discount_amount"] = discount_amount
        return order

    # 处理部分结账
    def partial_checkout(self, order, selected_ids):
        total_paid = 0
        # 处理选中的商品
        for item in order["breakdown"]:
            if str(item["product_id"]) in selected_ids and not item.get("is_paid", False):
                item["is_paid"] = True
                total_paid += item["price"] * item["amount"]
        return order, total_paid

    # 获取活跃订单（未完全付款）
    def get_active_orders(self):
        orders = self.load_orders()
        active_orders = []

        # 筛选未完全付款的订单
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

    # 获取历史订单（已完全付款）
    def get_history_orders(self):
        orders = self.load_orders()
        history_orders = []

        # 筛选已完全付款的订单
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


# 初始化测试数据
def initialize_test_data():
    controller = EnhancedOrderController()

    # 基本测试订单
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

    # 添加详细测试数据
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

    # 保存测试数据
    for order in test_orders:
        controller.save_order(order)
    print("测试数据初始化完成")


# 如果直接运行此文件，只初始化测试数据
if __name__ == "__main__":
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(root_dir, "OrderDB.json")
    if not os.path.exists(db_path):
        initialize_test_data()
        print("测试数据初始化完成，请运行主程序启动应用程序。")