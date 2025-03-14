import tkinter as tk
from tkinter import ttk
import os
import sys
from datetime import datetime

# Import models and controllers
from Models.TableModel import TableModel
from Controllers.TableController import TableController
from Controllers.Order_bar_controller import EnhancedOrderController, initialize_test_data

# Import views
from Views.BartenderView import BartenderView
from Views.Order_bar_view import OrderListView, OrderDetailView, OrderCard, HistoryDetailView


# Create a class to handle the order view navigation
class OrderViewManager:
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.current_view = None
        self.current_frame = None

        # Container for order views
        self.container = tk.Frame(parent, bg="#f5f6fa")
        self.container.pack(fill="both", expand=True)

        # Start with list view
        self.show_list_view()

    def _clear_container(self):
        # Remove current view
        if self.current_frame:
            self.current_frame.pack_forget()

    def show_list_view(self):
        self._clear_container()
        # Create list view
        self.current_frame = OrderListView(self.container, self.controller, self)
        self.current_frame.pack(fill="both", expand=True)
        self.current_view = "list"

    def show_detail_view(self, transaction_id):
        self._clear_container()
        # Get the order and display detail view
        order = self.controller.get_order_by_transaction(transaction_id)
        if order:
            self.current_frame = OrderDetailView(self.container, self.controller, order, self)
            self.current_frame.pack(fill="both", expand=True)
            self.current_view = "detail"
            self.current_transaction_id = transaction_id

    def show_history_view(self):
        self._clear_container()
        # Create a custom history view frame
        history_frame = tk.Frame(self.container)
        history_frame.pack(fill="both", expand=True)

        # Add header with back button
        header = tk.Frame(history_frame, bg="#f5f6fa")
        header.pack(fill="x", pady=5)

        ttk.Button(header, text="← Back", command=self.show_list_view).pack(side="left", padx=10, pady=5)
        tk.Label(header, text="Order History", font=("Arial", 14, "bold"), bg="#f5f6fa").pack(side="left", padx=20,
                                                                                              pady=5)

        # Create scrollable area for order cards
        canvas = tk.Canvas(history_frame, bg="white")
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=canvas.yview)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

        # Create frame for cards
        cards_frame = tk.Frame(canvas, bg="white")
        canvas.create_window((0, 0), window=cards_frame, anchor="nw")

        # Get history orders and add cards
        orders = self.controller.get_history_orders()

        if not orders:
            tk.Label(cards_frame, text="No history orders", font=("Arial", 12), bg="white").pack(pady=20)
        else:
            for order in orders:
                card = OrderCard(
                    cards_frame,
                    order,
                    on_click=lambda tid=order["transaction_id"]: self.show_history_detail_view(tid),
                    bg="white",
                    width=350
                )
                card.pack(fill="x", pady=5, padx=10)

        # Configure canvas scrolling
        def on_frame_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))

        cards_frame.bind("<Configure>", on_frame_configure)

        # Make sure canvas items expand properly
        def on_canvas_configure(e):
            canvas.itemconfig(canvas.find_withtag("all")[0], width=e.width)

        canvas.bind("<Configure>", on_canvas_configure)

        self.current_frame = history_frame
        self.current_view = "history"

    def show_history_detail_view(self, transaction_id):
        self._clear_container()
        # Get the order and display history detail view
        order = self.controller.get_order_by_transaction(transaction_id)
        if order:
            self.current_frame = HistoryDetailView(self.container, self.controller, order, self)
            self.current_frame.pack(fill="both", expand=True)
            self.current_view = "history_detail"


if __name__ == "__main__":
    # Initialize test data if needed
    if not os.path.exists("OrderDB.json"):
        initialize_test_data()

    root = tk.Tk()
    root.title("Combined Bar Management")
    root.geometry("1400x800")  # Increased window size for better viewing
    root.minsize(1200, 700)  # Set minimum size to ensure usability

    # Initialize models and controllers
    table_model = TableModel()
    table_controller = TableController(table_model)
    order_controller = EnhancedOrderController()

    # Create main container with PanedWindow for resizable panels
    main_pane = tk.PanedWindow(root, orient=tk.HORIZONTAL, bg="#F7F9FC", sashwidth=5)
    main_pane.pack(fill="both", expand=True)

    # Left panel - BartenderView
    left_frame = tk.Frame(main_pane, bg="#F7F9FC")

    # Right panel - Order management
    right_frame = tk.Frame(main_pane, bg="#F7F9FC")

    # Add frames to paned window with reversed proportions (left larger, right smaller)
    main_pane.add(left_frame, minsize=600, width=800)  # Larger width for left view
    main_pane.add(right_frame, minsize=400, width=600)  # Smaller width for right view

    # Create BartenderView in left panel
    bartender_view = BartenderView(left_frame, table_controller)
    bartender_view.pack(fill="both", expand=True, padx=5, pady=5)

    # Create OrderViewManager in right panel
    order_view_manager = OrderViewManager(right_frame, order_controller)

    # Center the window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    root.mainloop()