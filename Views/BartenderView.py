#for table view + expanding with order when pressing a table
import tkinter as tk
from tkinter import messagebox, ttk
from Controllers.TableController import TableController
from Models.TableModel import TableModel

class BartenderView(tk.Tk):
    """ MVC View for managing tables and displaying orders visually. """

    def __init__(self, controller: TableController):
        super().__init__()
        self.controller = controller
        self.title("Bartender View")
        self.geometry("1000x700")
        self.configure(bg="#F7F9FC")

        # Create legend for table statuses
        self.create_legend()

        # Create canvas to draw tables
        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(expand=True, fill="both")

        # Draw initial tables and bar
        self.draw_tables()
        self.draw_bar()

    def create_legend(self):
        """ Creates a legend to explain colors representing table statuses. """
        legend = tk.Frame(self, bg="#F7F9FC")
        legend.pack(pady=10)

        statuses = [("Free", "#E3F2FD"), ("VIP", "#FFD700"), ("Occupied", "#90CAF9"), ("Bar", "#607D8B")]
        for status, color in statuses:
            tk.Label(legend, bg=color, width=2, height=1).pack(side="left", padx=5)
            tk.Label(legend, text=status, bg="#F7F9FC").pack(side="left", padx=10)

    def draw_tables(self):
        """ Fetch tables from controller and visually represent them. """
        self.canvas.delete("all")
        tables = self.controller.model.tables

        positions = [(150, 150), (350, 150), (550, 150), (150, 350), (350, 350), (550, 350)]

        for table, position in zip(tables, positions):
            color = "#E3F2FD" if table.status == "free" else "#FFD700" if table.status == "VIP" else "#90CAF9"

            # Draw each table as a rectangle
            x, y = position
            rect = self.canvas.create_rectangle(x-50, y-30, x+50, y+30, fill=color, tags=f"table_{table.table_id}")
            self.canvas.create_text(x, y, text=f"Table {table.table_id}\n{table.status}")

            # Bind click event to open details popup
            self.canvas.tag_bind(rect, "<Button-1>", lambda e, t=table: self.show_table_orders(t))

    def draw_bar(self):
        """ Draws a visual representation of the bar area. """
        self.canvas.create_rectangle(750, 100, 950, 600, fill="#607D8B")
        self.canvas.create_text(850, 350, text="BAR", fill="white", font=("Arial", 20, "bold"))

    def show_table_orders(self, table):
        """ Opens a popup to display table details without manual status change. """
        popup = tk.Toplevel(self)
        popup.title(f"Table {table.table_id} Details")
        popup.geometry("300x150")

        tk.Label(popup, text=f"Table {table.table_id} Status: {table.status}",
                 font=("Arial", 14, "bold")).pack(pady=10)

        # Visa kunder
        customers = ", ".join(table.customer_list) if table.customer_list else "No customers"
        tk.Label(popup, text=f"Customers: {customers}").pack(pady=5)

        # Visa produkter
        products = ", ".join(str(p) for p in table.product_list) if table.product_list else "No products"
        tk.Label(popup, text=f"Products: {products}").pack(pady=5)

    def update_status(self, table_id, new_status, popup):
        """ Updates table status via controller and refreshes the view. """
        table = self.controller.model.get_table_by_id(table_id)
        table.status = new_status
        self.controller.model.update_table(table)
        self.draw_tables()
        popup.destroy()
        messagebox.showinfo("Update", f"Table {table_id} status updated to {new_status}.")

if __name__ == '__main__':
    model = TableModel()
    controller = TableController(model)
    app = BartenderView(controller)
    app.mainloop()
