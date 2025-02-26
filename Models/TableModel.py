#declare table object id, number of seats, order list, status(reserved, free), ( list of products), customer list
#etc.
import json
import os

TABLE_FILE = "database/TableDB.json"

class Table:
    def __init__(self, table_id, number_of_seats, status="free", order_list=None, product_list=None, customer_list=None):
        self.table_id = table_id #identifier for the table.
        self.number_of_seats = number_of_seats #Number of seats available at the table.
        self.status = status  # "reserved" or "free"
        self.order_list = order_list if order_list is not None else [] #List of orders placed at the table.
        self.product_list = product_list if product_list is not None else [] #List of products associated with the table? Is this needed?
        self.customer_list = customer_list if customer_list is not None else [] #List of customers sitting at the table.

#---------------------------------------------------------------------------------------------------------------------
#Do we need to converts a Table object into the dictionary?
    def to_dict(self):
        return {
            "table_id": self.table_id,
            "number_of_seats": self.number_of_seats,
            "status": self.status,
            "order_list": self.order_list,
            "product_list": self.product_list,
            "customer_list": self.customer_list
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            table_id=data["table_id"],
            number_of_seats=data["number_of_seats"],
            status=data.get("status", "free"),
            order_list=data.get("order_list", []),
            product_list=data.get("product_list", []),
            customer_list=data.get("customer_list", [])
        )
#---------------------------------------------------------------------------------------------------------------------
class TableModel:
    def __init__(self):
        self.tables = []
        self.load_tables()

    def get_table_by_id(self, table_id):
        return next((table for table in self.tables if table.table_id == table_id), None)

    def update_table_status(self, table_id, new_status):
        table = self.get_table_by_id(table_id)
        if table:
            table.status = new_status
            self.save_tables()
            return True
        return False

    def add_order_to_table(self, table_id, order):
        table = self.get_table_by_id(table_id)
        if table:
            table.order_list.append(order)
            self.save_tables()
            return True
        return False

#VIP -> pay at the table, for normal customer 
#Button on the table "Go to the bar" -> Log in as a Bartender and "Check Out that table" 
#-> Log in as a customer and you're allowed to pay
#push
