#for seeing if there are empty seats or available space in the pub, get order by table
#for seeing if there are empty seats or available space in the pub
from Models.TableModel import TableModel

class TableController:
    """ Handles interactions between the view and the model. """

    def __init__(self, model):
        self.model = model

    def get_tables(self):
        """ Retrieve all tables from the model. """
        return self.model.get_tables()

    def update_table_status(self, table_id, new_status):
        """ Update a table's status via the model. """
        return self.model.update_table_status(table_id, new_status)

    def get_orders_by_table(self, table_id):
        """ Retrieve orders for a specific table. """
        table = self.model.get_table_by_id(table_id)
        return table.order_list if table else []