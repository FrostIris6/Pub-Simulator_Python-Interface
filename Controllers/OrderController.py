#actions for calculate order price per table (the table object empties the food/beverages lists after the table has paid)
#show order items, decrease stock after order, increase stock after barista/waiter orders products
#no need for a database for orders as they are stored locally in the table database
#drag and drop for what you want to pay -> delete them from Table Order List
#methods: 1. in memu page click + to show submenu(pop-up) with 1)"order" to add items 2)"amount" 3)specification(op) 4)notes(op)
# 2. in order page click 1) + to plus 1, 2) - to minus 1, 3) "edit" to show submenu(pop-up) 4)show price at bottom
#logic: controller: 1. get product info from menudb 2. record new order items 3. adjust ordered items info
from Models.Order_Payment_Model import OrderModel, PaymentModel
from Views.OrderViewClass import OrderViewClass
import tkinter as tk
from tkinter import messagebox


class OrderController:

    def __init__(self, view, user_id, table_id):

        self.view = view #call view to receive input from window
        self.user_id = user_id
        self.table_id = table_id
        self.order = OrderModel(user_id, table_id) #call model_layer to deal with data
        self.payment = PaymentModel(self.order)


    def add_item(self, item_id, price, amount=1, specification=None, notes=None): #get new item from menu
        self.order.add_item(item_id, price, amount, specification, notes)
        self.view.update_items()

    def minus1_item(self, item_id):
        if self.order.minus1_item(item_id): self.view.update_items()
        else: self.remove_item(item_id)

    def plus1_item(self, item_id):
        self.order.plus1_item(item_id)
        self.view.update_items()

    def add_notes(self, item_id, notes):
        self.order.add_notes(item_id, notes)

    def pick_spe(self, item_id, spe):
        self.order.pick_spe(item_id, spe)

    def update_items(self, item_id, price, amount=1, specification=None, notes=None): #update details
        self.order.update_items(item_id, price, amount, specification, notes)
        self.view.update_items()

    def remove_item(self, item_id):
        self.order.remove_item(item_id)
        self.view.update_items()

    def current_order(self): #get current all items to display
        return self.order.items

    def confirm_order(self): #please check your order before checkout
        return self.order.checkout_info()

    def checkout_order(self):#enter checkout process, write bill into DB
        self.order.write_order()
        # if customer_status:
        #     if self.payment._check_vip_balance():
        #         self.payment._save_payment_record()
        #         return True
        #     else:
        #         return False
        # else:
        #     self.payment._save_payment_record()
        #     return True

    def clear_order(self): self.order.clear_order()




# root = tk.Tk()
# order_controller = OrderController(None, 1, 1)  # 先创建 OrderController
# app = OrderView(root, order_controller)  # 将 OrderController 传递给 OrderView 刚刚这里出错，导致view那边收不到正常的controller的实例
# order_controller.view = app
# root.mainloop()
# if __name__ == "__main__":
#     root = tk.Tk()
#     app = OrderViewClass(root, None)
#     #order_controller = OrderController(app, 1, 1)
#     root.mainloop()