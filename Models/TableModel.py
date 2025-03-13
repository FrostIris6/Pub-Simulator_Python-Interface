#declare table object id, number of seats, order list, status(reserved, free), ( list of products), customer list
#etc.
import json
import os

# Hitta alltid rätt mapp oavsett var du startar programmet ifrån
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLE_FILE = os.path.join(BASE_DIR, "Database", "TablesDB.json")

class Table:
    def __init__(self, table_id, number_of_seats, status="free", order_list=None, product_list=None, customer_list=None):
        self.table_id = table_id
        self.number_of_seats = number_of_seats
        self.status = status
        self.order_list = order_list if order_list is not None else []
        self.product_list = product_list if product_list else []
        self.customer_list = customer_list if customer_list else []

    def to_dict(self):
        """Returns table data as a dictionary."""
        return {
            "table_id": self.table_id,
            "number_of_seats": self.number_of_seats,
            "status": self.status,
            "order_list": self.order_list,
            "product_list": self.product_list,
            "customer_list": self.customer_list
        }


class TableModel:
    def __init__(self, database_path=TABLE_FILE):
        self.database_path = database_path
        self.tables = self.load_tables()

    def load_tables(self):
        """Loads tables from JSON database file and updates their status."""
        try:
            with open(self.database_path, "r") as file:
                data = json.load(file)
                tables = []
                for table_data in data:
                    table = Table(**table_data)

                    # Set table status based on business logic
                    if not table.customer_list and not table.product_list:
                        table.status = "free"
                    elif table.customer_list:
                        table.status = "VIP"
                    elif table.product_list:
                        table.status = "occupied"

                    tables.append(table)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print("Error loading tables:", e)
            return []

        return tables

    def save_tables(self):
        """Saves current table data to JSON database file."""
        with open(self.database_path, "w") as file:
            json.dump([table.to_dict() for table in self.tables], file, indent=4)

    def get_table_by_id(self, table_id):
        """Returns a table object by its ID."""
        for table in self.tables:
            if table.table_id == table_id:
                return table
        return None

    def update_table(self, table: Table):
        """Updates table data."""
        for i, t in enumerate(self.tables):
            if t.table_id == table.table_id:
                self.tables[i] = table
                self.save_tables()
                return True
        return False


#VIP -> pay at the table, for normal customer
#Button on the table "Go to the bar" -> Log in as a Bartender and "Check Out that table"
#-> Log in as a customer and you're allowed to pay