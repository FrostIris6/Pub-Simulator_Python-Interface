import json
import os
import uuid
from datetime import datetime
from enum import Enum

ORDER_FILE = "../Database/OrderDB.json"
PAYMENT_FILE = "../Database/PaymentDB.json"
#transaction_count = 0 #begin with 0 every day,once an order created, plus 1

class OrderModel:

    def __init__(self, user_id, table_id):

        self.user_id = user_id
        self.table_id = table_id
        self.items = [{"product_id": "Burger", "price": 15, "amount": 2, "specification": "can", "note": "cold"},{"product_id": "beef", "price": 25, "amount": 12, "specification": "can", "note": "cold"}] #all items that have ordered
        self.order_info = {} # order_info for this order without detailed items info
        self.transaction_id = str(uuid.uuid4())


    def add_item(self, product_id, price, amount=1, specification=None, notes=None):
        # add new items
        item = dict(product_id=product_id, price=price, amount=amount, specification=specification, notes=notes)
        self.items.append(item)

    def minus1_item(self, product_id):
        # amount - 1
        for item in self.items:
            if item["product_id"] == product_id:
                if item["amount"] <= 1:
                    return False
                else: item["amount"]-=1
                return True

    def plus1_item(self, product_id):
        # amount + 1
        for item in self.items:
            if item["product_id"] == product_id:
                item["amount"] += 1

    def update_items(self, product_id, price, amount=1, specification=None, notes=None):
        #refresh data of existed items
        for item in self.items:
            if item["product_id"] == product_id:
                item["price"] = price
                item["amount"] = amount
                item["specification"] = specification
                item["notes"] = notes

    def remove_item(self, product_id):
        #delete an item
        self.items = [item for item in self.items if item["product_id"] != product_id]

    def add_notes(self, product_id, notes):
        for item in self.items:
            if item["product_id"] == product_id:
                item["note"] = notes

    def pick_spe(self, product_id, spe):
        for item in self.items:
            if item["product_id"] == product_id:
                item["specification"] = spe

    def get_order_info(self, transaction_id, user_id, table_id, total_price, transaction_time, items):
        self.order_info = {
            "transaction_id": transaction_id,
            "user_id": user_id,
            "table_id": table_id,
            "money": total_price,
            "transaction_time": transaction_time,
            "breakdown": items,
        }

    def total_price(self):
        total_price = 0
        for item in self.items:
            total_price += item["price"] * item["amount"]
        return total_price

    def checkout_info(self):
        transaction_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total_price = self.total_price()
        self.get_order_info(self.transaction_id,self.user_id,self.table_id,total_price,transaction_time,self.items)
        return self.order_info

    def read_order(self):
        #read exsited orders from db
        if os.path.exists(ORDER_FILE):
            with open(ORDER_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                transaction_id = data["transaction_id"]
                user_id = data["user_id"]
                table_id = data["table_id"]
                total_price = data["money"]
                transaction_time = data["transaction_time"]
                items = data["breakdown"]
            self.get_order_info(transaction_id, user_id, table_id, total_price, transaction_time, items)
            return self.order_info
        else:
            return "File not found"

    def write_order(self):
        #if an order created, data will be written into OrderDB.json
        if os.path.exists(ORDER_FILE):
            with open(ORDER_FILE, "w", encoding="utf-8") as f:
                json.dump(self.checkout_info(), f, ensure_ascii=False, indent=4)
        else:
            return "File not found."

    def clear_order(self):
        self.items = []


#test demos
# order = OrderModel(1,1)
# order.add_item(1,2,3,"can","no spicy")
# # order.refresh_items(1,12,13,"bottle","spicy")
# # order.remove_item(1)
# order.write_order()
# order.read_order()


# payment status
class PaymentStatus(Enum):
    UNPAID = "unpaid"
    PENDING = "pending_bar"
    PAID = "paid"


# payment methods
class PaymentMethod(Enum):
    VIP_BALANCE = "vip_balance"
    CASH = "cash"
    CREDIT_CARD = "credit_card"


class PaymentModel:
    def __init__(self, order_model):
        """
        初始化支付模块
        """
        self.order = order_model
        self.PAYMENT_FILE = "../Database/PaymentDB.json"

        # paid status
        for item in self.order.items:
            if "is_paid" not in item:
                item["is_paid"] = False

    def _save_payment_record(self, payment_data):
        """save the record to file"""
        try:
            # read existing record
            if os.path.exists(self.PAYMENT_FILE):
                with open(self.PAYMENT_FILE, "r", encoding="utf-8") as f:
                    all_payments = json.load(f)
            else:
                all_payments = []

            # add new record
            all_payments.append(payment_data)

            # add payment record to file
            with open(self.PAYMENT_FILE, "w", encoding="utf-8") as f:
                json.dump(all_payments, f, ensure_ascii=False, indent=4)
        except Exception as e:
            raise IOError(f"fail to save record: {str(e)}")

    def _calculate_selected_total(self, selected_ids):
        """calculate the price"""
        total = 0
        for item in self.order.items:
            if item["product_id"] in selected_ids and not item["is_paid"]:
                total += item["price"] * item["amount"]
        return total

    def split_payment(self, selected_ids: list, payer_id: str, is_vip: bool, payment_method: str,
                      amount_paid: float = 0):
        """
        payment split
        :param selected_ids: item has been selected
        :param payer_id: payer id (not sure if we need)
        :param is_vip: Vip or not
        :param payment_method: payment method
        :param amount_paid: actual payment amount (used when use cash)
        """
        # error status
        if not selected_ids:
            raise ValueError("please select a product")

        # read selected item
        selected_items = [item for item in self.order.items
                          if str(item["product_id"]) in selected_ids
                          and not item["is_paid"]]

        if not selected_items:
            raise ValueError("no item can be paid")

        # calculate the price
        total_due = self._calculate_selected_total(selected_ids)

        # VIP payment
        if is_vip:
            if payment_method != PaymentMethod.VIP_BALANCE.value:
                raise ValueError("VIP use account balance")

            # check the account balance
            vip_balance_sufficient = self._check_vip_balance(payer_id, total_due)

            if not vip_balance_sufficient:
                raise ValueError("VIP account balance not enough")

            # payment status
            payment_status = PaymentStatus.PAID.value

        # regular customer payment
        else:
            if payment_method == PaymentMethod.VIP_BALANCE.value:
                raise ValueError("regular customer don't use account balance")

            if amount_paid < total_due:
                raise ValueError("payment not enough")

            payment_status = PaymentStatus.PAID.value if payment_method == PaymentMethod.CASH.value else PaymentStatus.PENDING.value

        # create payment record
        payment_data = {
            "payment_id": str(uuid.uuid4()),
            "transaction_id": self.order.transaction_id,
            "table_id": self.order.table_id,
            "payer_id": payer_id,
            "total_amount": total_due,
            "amount_paid": amount_paid,
            "payment_method": payment_method,
            "payment_status": payment_status,
            "payment_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "items": [
                {
                    "product_id": item["product_id"],
                    "price": item["price"],
                    "amount": item["amount"],
                    "specification": item.get("specification"),
                    "notes": item.get("notes")
                } for item in selected_items
            ]
        }

        # move item to paid
        for item in self.order.items:
            if str(item["product_id"]) in selected_ids:
                item["is_paid"] = True

        # refresh the order
        self.order.write_order()

        # save payment record
        self._save_payment_record(payment_data)

        return payment_data

    def _check_vip_balance(self, required: float, vip_id: str = None) -> bool:
        """check account balance"""
        # if it's true then it's enough balance for payment
        # if customer["vip_id"] >= required:
        #     return True
        # else:
        #     return False
        return True

    def get_unpaid_items(self):
        """get products unpaid"""
        return [item for item in self.order.items if not item["is_paid"]]

    def get_payment_history(self):
        """get the payment record for this payment"""
        if os.path.exists(self.PAYMENT_FILE):
            with open(self.PAYMENT_FILE, "r", encoding="utf-8") as f:
                all_payments = json.load(f)
            return [p for p in all_payments if p["transaction_id"] == self.order.transaction_id]
        return []