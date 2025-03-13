#for table view + expanding with order when pressing a table
import tkinter as tk
from tkinter import messagebox, ttk
from Controllers.TableController import TableController
from Models.TableModel import TableModel

class BartenderView(tk.Tk):
    """ Modernized GUI for managing tables and bar representation. """

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("Bartender View - Modern Table Management")
        self.geometry("1000x700")
        self.configure(bg="#F7F9FC")  # Light background

        # Legend for Table Status
        self.create_legend()

        # Canvas for Tables
        self.canvas = tk.Canvas(self, width=900, height=600, bg="white", highlightthickness=0)
        self.canvas.pack(pady=10, fill="both", expand=True)

        self.draw_tables()
        self.draw_bar()

    def create_legend(self):
        """ Creates a legend to explain table colors. """
        legend_frame = tk.Frame(self, bg="#F7F9FC")
        legend_frame.pack(pady=5, fill="x", padx=20)

        legends = [
            ("Empty", "#E3F2FD"),
            ("Reserved", "#3E5C76"),  # Lighter blue for better text contrast
            ("Occupied", "#90CAF9"),
            ("Bar", "#607D8B")
        ]

        for text, color in legends:
            tk.Label(legend_frame, text="  ", bg=color, width=2, height=1, relief="solid").pack(side="left", padx=5)
            tk.Label(legend_frame, text=text, font=("Arial", 12), bg="#F7F9FC").pack(side="left", padx=10)

    def draw_tables(self):
        """ Draw tables on the canvas. """
        self.canvas.delete("all")
        tables = self.controller.get_tables()

        if not tables:
            self.canvas.create_text(450, 300, text="No tables available", font=("Arial", 16))
            return

        row_positions = [150, 300, 450]  # Three row positions
        col_start = 120
        col_spacing = 200

        for index, table in enumerate(tables):
            row = index % 3  # Distribute tables into 3 rows
            x = col_start + (index // 3) * col_spacing
            y = row_positions[row]

            color = "#E3F2FD" if table["status"] == "free" else "#3E5C76" if table["status"] == "reserved" else "#90CAF9"

            # Table size based on seats
            width = 80 + (table["number_of_seats"] * 5)
            height = 50 + (table["number_of_seats"] * 3)

            # Draw rectangle tables
            self.canvas.create_rectangle(x - width//2, y - height//2, x + width//2, y + height//2,
                                         fill=color, outline="#B0BEC5", tags=f"table_{table['table_id']}")

            self.canvas.create_text(x, y, text=f"Table {table['table_id']}\n{table['status'].capitalize()}",
                                    font=("Arial", 12, "bold"), fill="white", tags=f"table_{table['table_id']}")

            self.canvas.tag_bind(f"table_{table['table_id']}", "<Button-1>", lambda event, t=table: self.open_status_popup(t))

    def draw_bar(self):
        """ Draws the bar section as a fixed rectangle on the right side. """
        bar_x, bar_y, bar_width, bar_height = 780, 100, 120, 500  # Bar dimensions
        self.canvas.create_rectangle(bar_x, bar_y, bar_x + bar_width, bar_y + bar_height,
                                     fill="#607D8B", outline="black", tags="bar")
        self.canvas.create_text(bar_x + bar_width / 2, bar_y + bar_height / 2,
                                text="BAR", font=("Arial", 14, "bold"), fill="white", tags="bar")

    def open_status_popup(self, table):
        """ Open a popup window to change table status. """
        popup = tk.Toplevel(self)
        popup.title(f"Change Status - Table {table['table_id']}")
        popup.geometry("300x150")

        tk.Label(popup, text=f"Change status for Table {table['table_id']}", font=("Arial", 12, "bold")).pack(pady=10)
        status_var = tk.StringVar(value=table["status"])
        status_dropdown = ttk.Combobox(popup, textvariable=status_var, values=["free", "reserved", "occupied"])
        status_dropdown.pack(pady=5)

        tk.Button(popup, text="Update Status", command=lambda: self.update_status(table, status_var.get(), popup)).pack(pady=10)

    def update_status(self, table, new_status, popup):
        """ Send update request to controller. """
        self.controller.update_table_status(table["table_id"], new_status)
        self.draw_tables()
        popup.destroy()
        messagebox.showinfo("Status Updated", f"Table {table['table_id']} is now {new_status}")

if __name__ == "__main__":
    model = TableModel()
    controller = TableController(model)
    app = BartenderView(controller)
    app.mainloop