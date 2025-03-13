#declare table object id, number of seats, order list, status(reserved, free), ( list of products), customer list
#etc.
import os

import json

TABLE_FILE = "Database/TablesDB.json"

class Table:
    """ Represents a single table in the pub. """

    def __init__(self, table_id, number_of_seats, status="free", order_list=None, product_list=None, customer_list=None):
        self.table_id = table_id
        self.number_of_seats = number_of_seats
        self.status = status
        self.order_list = order_list if order_list is not None else []
        self.product_list = product_list if product_list is not None else []
        self.customer_list = customer_list if customer_list is not None else []

    def to_dict(self):
        """ Convert table object to dictionary for storage. """
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
        """ Convert dictionary to table object. """
        return cls(
            table_id=data["table_id"],
            number_of_seats=data["number_of_seats"],
            status=data.get("status", "free"),
            order_list=data.get("order_list", []),
            product_list=data.get("product_list", []),
            customer_list=data.get("customer_list", [])
        )

class TableModel:
    """ Manages table data and database operations. """

    def __init__(self):
        self.tables = []
        self.load_tables()

    def load_tables(self):
        """ Load table data from JSON file. """
        try:
            with open(TABLE_FILE, "r") as file:
                data = json.load(file)
                self.tables = [Table.from_dict(table) for table in data]
        except (FileNotFoundError, json.JSONDecodeError):
            print("Error: Table database could not be loaded.")

    def save_tables(self):
        """ Save table data to JSON file. """
        with open(TABLE_FILE, "w") as file:
            json.dump([table.to_dict() for table in self.tables], file, indent=4)

    def get_tables(self):
        """ Return all tables as a list of dictionaries. """
        return [table.to_dict() for table in self.tables]

    def get_table_by_id(self, table_id):
        """ Return a specific table by ID. """
        return next((table for table in self.tables if table.table_id == table_id), None)

    def update_table_status(self, table_id, new_status):
        """ Update the status of a specific table and save changes. """
        table = self.get_table_by_id(table_id)
        if table:
            table.status = new_status
            self.save_tables()
            return True
        return False

#VIP -> pay at the table, for normal customer
#Button on the table "Go to the bar" -> Log in as a Bartender and "Check Out that table"
#-> Log in as a customer and you're allowed to pay