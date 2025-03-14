import tkinter as tk
from Models.TableModel import TableModel
from Controllers.TableController import TableController
from Controllers.Order_bar_controller import EnhancedOrderController
from Views.BartenderView import BartenderView
from Views.Order_bar_view import OrderListView

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Combined Bar Management")
    root.geometry("1200x700")

    # Initialize models and controllers
    table_model = TableModel()
    table_controller = TableController(table_model)
    order_controller = EnhancedOrderController()

    # Main frame to hold the two views
    main_frame = tk.Frame(root, bg="#F7F9FC")
    main_frame.pack(fill="both", expand=True)

    # Left side - BartenderView (narrower now)
    bartender_view = BartenderView(main_frame, table_controller)
    bartender_view.pack(side="left", fill="both", expand=True)

    # Right side - Order_bar_view (wider now)
    order_list_view = OrderListView(main_frame, order_controller, main_window=root)
    order_list_view.pack(side="right", fill="both", expand=True)

    # Set proportional widths using grid weights
    main_frame.columnconfigure(0, weight=2)  # BartenderView column (narrower)
    main_frame.columnconfigure(1, weight=3)  # Order_bar_view column (wider)

    root.mainloop()



