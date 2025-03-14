#for table view + expanding with order when pressing a table
import tkinter as tk
from tkinter import messagebox, ttk
from Controllers.TableController import TableController

class BartenderView(tk.Tk):
    """ MVC View for managing tables and displaying orders visually. """

    def __init__(self, controller: TableController):
        super().__init__()
        self.controller = controller
        self.title("Bartender View")
        self.geometry("1000x700")
        self.configure(bg="#F7F9FC")

        # Huvudram som täcker hela fönstret
        self.main_frame = tk.Frame(self, bg="#F7F9FC")
        self.main_frame.pack(fill="both", expand=True)

        # Övre panel (fast element)
        self.top_frame = tk.Frame(self.main_frame, bg="#F7F9FC", height=50)
        self.top_frame.pack(fill="x", side="top")

        # Nedre ram (delar upp canvas och högerpanel)
        self.bottom_frame = tk.Frame(self.main_frame, bg="#FFFFFF")
        self.bottom_frame.pack(fill="both", expand=True)

        # Canvas-område (2/3 av skärmen)
        self.canvas_frame = tk.Frame(self.bottom_frame, bg="white", width=600)
        self.canvas_frame.pack(side="left", expand=True, fill="both")

        self.canvas = tk.Canvas(self.canvas_frame, bg="white")
        self.canvas.pack(expand=True, fill="both")

        # NY HÖGERPANEL (grå, tar upp 1/3 av skärmen)
        self.right_panel = tk.Frame(self.bottom_frame, bg="#E0E0E0", width=400)
        self.right_panel.pack(side="right", fill="y")

        # Rita befintliga komponenter
        self.create_legend()
        self.draw_tables()
        self.draw_bar()

    def create_legend(self):
        """ Creates a legend to explain colors representing table statuses. """
        # Placera legenden inuti top_frame och vänsterjustera den tydligt.
        legend = tk.Frame(self.top_frame, bg="#F7F9FC")
        legend.pack(pady=10, anchor="w", padx=15)

        statuses = [("Free", "#E3F2FD"), ("VIP", "#FFD700"), ("Occupied", "#90CAF9"), ("Bar", "#607D8B")]
        for status, color in statuses:
            tk.Label(legend, bg=color, width=2, height=1).pack(side="left", padx=5)
            tk.Label(legend, text=status, bg="#F7F9FC").pack(side="left", padx=10)

    def draw_tables(self):
        """ Fetch tables from controller and visually represent them. """
        self.canvas.delete("all")
        tables = self.controller.model.tables

        positions = [(150, 120), (350, 120),
                     (150, 280), (350, 280),
                     (150, 440), (350, 440)]

        for table, position in zip(tables, positions):
            color = "#E3F2FD" if table.status == "free" else "#FFD700" if table.status == "VIP" else "#90CAF9"

            # Draw each table as a rectangle
            x, y = position
            rect = self.canvas.create_rectangle(x-50, y-30, x+50, y+30, fill=color, tags=f"table_{table.table_id}")
            self.canvas.create_text(x, y, text=f"Table {table.table_id}\n{table.status}")


    def draw_bar(self):
        """ Draws a visual representation of the bar area. """
        self.canvas.create_rectangle(650, 100, 750, 600, fill="#607D8B")
        self.canvas.create_text(700, 350, text="BAR", fill="white", font=("Arial", 20, "bold"))

    def show_table_orders(self, table):
        """ Opens a popup to show orders and allows changing table status. """
        popup = tk.Toplevel(self)
        popup.title(f"Table {table.table_id} Details")
        popup.geometry("300x200")

        tk.Label(popup, text=f"Table {table.table_id} Status: {table.status}").pack(pady=10)

        status_var = tk.StringVar(value=table.status)
        status_options = ["free", "VIP", "occupied"]
        status_menu = ttk.Combobox(popup, textvariable=status_var, values=status_options)
        status_menu.pack(pady=10)

        update_button = tk.Button(popup, text="Update Status",
                                  command=lambda: self.update_status(table.table_id, status_var.get(), popup))
        update_button.pack(pady=10)

    def update_status(self, table_id, new_status, popup):
        """ Updates table status via controller and refreshes the view. """
        table = self.controller.model.get_table_by_id(table_id)
        table.status = new_status
        self.controller.model.update_table(table)
        self.draw_tables()
        popup.destroy()
        messagebox.showinfo("Update", f"Table {table_id} status updated to {new_status}.")

