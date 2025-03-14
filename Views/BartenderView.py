#for table view + expanding with order when pressing a table
import tkinter as tk
from tkinter import messagebox, ttk
from Controllers.TableController import TableController

class BartenderView(tk.Frame):
    """MVC View for managing tables and visually displaying their statuses."""

    def __init__(self, parent, controller: TableController):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#F7F9FC")

        # Main frame covering the entire view
        self.main_frame = tk.Frame(self, bg="#F7F9FC")
        self.main_frame.pack(fill="both", expand=True)

        # Top fixed frame containing the legend
        self.top_frame = tk.Frame(self.main_frame, bg="#F7F9FC", height=50)
        self.top_frame.pack(fill="x", side="top")

        # Bottom frame that holds the canvas for tables and bar
        self.bottom_frame = tk.Frame(self.main_frame, bg="#FFFFFF")
        self.bottom_frame.pack(fill="both", expand=True)

        # Canvas frame for tables and bar visuals
        self.canvas_frame = tk.Frame(self.bottom_frame, bg="white")
        self.canvas_frame.pack(expand=True, fill="both")

        # Canvas for drawing tables and bar
        self.canvas = tk.Canvas(self.canvas_frame, bg="white")
        self.canvas.pack(expand=True, fill="both")

        # Initialize the interface components
        self.create_legend()
        self.draw_tables()
        self.draw_bar()

    def create_legend(self):
        """Creates a legend explaining table status colors."""
        legend = tk.Frame(self.top_frame, bg="#F7F9FC")
        legend.pack(pady=10, anchor="w", padx=15)

        statuses = [("Free", "#E3F2FD"), ("VIP", "#FFD700"), ("Occupied", "#90CAF9"), ("Bar", "#607D8B")]
        for status, color in statuses:
            tk.Label(legend, bg=color, width=2, height=1).pack(side="left", padx=5)
            tk.Label(legend, text=status, bg="#F7F9FC").pack(side="left", padx=10)

    def draw_tables(self):
        """Fetches tables from the controller and visually represents them on the canvas."""
        self.canvas.delete("all")
        tables = self.controller.model.tables

        # Define positions for each table visually
        positions = [(150, 120), (350, 120),
                     (150, 280), (350, 280),
                     (150, 440), (350, 440)]

        # Iterate over tables and their positions to draw them
        for table, position in zip(tables, positions):
            # Select color based on table status
            color = "#E3F2FD" if table.status == "free" else "#FFD700" if table.status == "VIP" else "#90CAF9"

            # Draw table rectangle and status
            x, y = position
            rect = self.canvas.create_rectangle(x-50, y-30, x+50, y+30, fill=color, tags=f"table_{table.table_id}")
            self.canvas.create_text(x, y, text=f"Table {table.table_id}\n{table.status}")

    def draw_bar(self):
        """Draws a visual representation of the bar area."""
        self.canvas.create_rectangle(650, 100, 750, 600, fill="#607D8B")
        self.canvas.create_text(700, 350, text="BAR", fill="white", font=("Arial", 20, "bold"))

    def show_table_orders(self, table):
        """Opens a popup window to display orders and allow status changes for a specific table."""
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
        """Updates the table's status through the controller and refreshes the canvas."""
        table = self.controller.model.get_table_by_id(table_id)
        table.status = new_status
        self.controller.model.update_table(table)
        self.draw_tables()
        popup.destroy()
        messagebox.showinfo("Update", f"Table {table_id} status updated to {new_status}.")


