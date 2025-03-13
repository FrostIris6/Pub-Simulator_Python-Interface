#for seeing if there are empty seats or available space in the pub, get order by table
import json
from Models.TableModel import TableModel

class TableController:
    def __init__(self, model: TableModel):
        self.model = model

    def update_table_status(self, table_id):
        """Updates table status automatically based on current table data."""
        table = self.model.get_table_by_id(table_id)
        if not table:
            raise ValueError(f"Table with ID {table_id} does not exist.")

        # Business logic to determine the table status
        if not table.customer_list and not table.product_list:
            table.status = "free"
        elif table.customer_list:
            table.status = "VIP"
        elif not table.customer_list and table.product_list:
            table.status = "occupied"

        # Save changes to the database via model
        self.model.update_table(table)

        # Save updated table status
        self.model.update_table(table)

    def add_customer_to_table(self, table_id, customer_name):
        table = self.model.get_table_by_id(table_id)
        if table:
            table.customer_list.append(customer_name)
            self.update_table_status(table_id)  # här körs statusuppdateringen automatiskt

    def remove_customer_from_table(self, table_id, customer_name):
        table = self.model.get_table_by_id(table_id)
        if table and customer_name in table.customer_list:
            table.customer_list.remove(customer_name)
            self.update_table_status(table_id)

    def add_product_to_table(self, table_id, product_id):
        table = self.model.get_table_by_id(table_id)
        if table:
            table.product_list.append(product_id)
            self.update_table_status(table_id)

    def remove_product_from_table(self, table_id, product_id):
        table = self.model.get_table_by_id(table_id)
        if table and product_id in table.product_list:
            table.product_list.remove(product_id)
            self.update_table_status(table_id)

