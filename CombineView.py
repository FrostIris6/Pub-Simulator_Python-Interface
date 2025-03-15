import tkinter as tk
from tkinter import ttk
import os

# Import models and controllers
from Models.UserModel import UserModel
from Models.MenuModel import MenuModel
from Models.TableModel import TableModel

# Import controllers
from Controllers.UserController import UserController
from Controllers.MenuController import MenuController
from Controllers.TableController import TableController
from Controllers.Order_bar_controller import EnhancedOrderController, initialize_test_data

# Import views
from Views.MainView import MainView
from Views.CustomerView import CustomerView
from Views.BartenderView import BartenderView
from Views.Order_bar_view import OrderListView, OrderDetailView, OrderCard, HistoryDetailView
from Views.LoginView import LoginView, RegisterView, TableChoice


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


# Custom tab class
class CustomTab(tk.Frame):
    def __init__(self, parent, text, command, is_active=False):
        super().__init__(parent, cursor="hand2")
        self.command = command
        self.is_active = is_active

        # Set initial colors
        self.active_bg = "#4a6984"
        self.inactive_bg = "#333333"
        self.active_fg = "white"
        self.inactive_fg = "#cccccc"

        # Configure tab appearance
        self.config(bg=self.active_bg if is_active else self.inactive_bg, padx=15, pady=8)

        # Create tab label
        self.label = tk.Label(
            self,
            text=text,
            font=("Arial", 11),
            bg=self.active_bg if is_active else self.inactive_bg,
            fg=self.active_fg if is_active else self.inactive_fg
        )
        self.label.pack(side="left")

        # Bind click events
        self.bind("<Button-1>", self._on_click)
        self.label.bind("<Button-1>", self._on_click)

    def set_active(self, active):
        self.is_active = active
        bg_color = self.active_bg if active else self.inactive_bg
        fg_color = self.active_fg if active else self.inactive_fg
        self.config(bg=bg_color)
        self.label.config(bg=bg_color, fg=fg_color)

    def _on_click(self, event):
        self.command()


# Application Manager class to handle view switching and user roles
class AppManager:
    def __init__(self, root, user_controller):
        self.root = root
        self.user_controller = user_controller

        # Create main container
        self.main_container = tk.Frame(root)
        self.main_container.pack(fill="both", expand=True)

        # Create tab bar (initially hidden)
        self.tab_bar = tk.Frame(self.main_container, bg="#333")

        # Create content area
        self.content_area = tk.Frame(self.main_container)
        self.content_area.pack(fill="both", expand=True)

        # Create view frames
        self.customer_view_frame = tk.Frame(self.content_area)
        self.staff_view_frame = tk.Frame(self.content_area)

        # View state
        self.current_view = "customer"

        # Tab references
        self.customer_tab = None
        self.staff_tab = None

        # Initialize with tabs hidden (will show based on user role)
        self.update_ui()

    def setup_tabs(self):
        # Clear existing tabs if any
        for widget in self.tab_bar.winfo_children():
            widget.destroy()

        # Create tabs
        self.customer_tab = CustomTab(self.tab_bar, "Product", self.show_customer_view,
                                      is_active=(self.current_view == "customer"))
        self.customer_tab.pack(side="left")

        self.staff_tab = CustomTab(self.tab_bar, "Table", self.show_staff_view,
                                   is_active=(self.current_view == "staff"))
        self.staff_tab.pack(side="left")

    def show_customer_view(self):
        if self.current_view != "customer":
            self.staff_view_frame.pack_forget()
            self.customer_view_frame.pack(fill="both", expand=True)
            if self.customer_tab and self.staff_tab:
                self.customer_tab.set_active(True)
                self.staff_tab.set_active(False)
            self.current_view = "customer"

    def show_staff_view(self):
        if self.current_view != "staff":
            self.customer_view_frame.pack_forget()
            self.staff_view_frame.pack(fill="both", expand=True)
            if self.customer_tab and self.staff_tab:
                self.customer_tab.set_active(False)
                self.staff_tab.set_active(True)
            self.current_view = "staff"

    def update_ui(self):
        """Update UI based on user role"""
        user_role = self.user_controller.get_current_user_role()

        # Show tabs only for bartender role
        if user_role == "bartender":
            # Show the tab bar
            self.tab_bar.pack(fill="x", side="top", before=self.content_area)
            self.setup_tabs()
        else:
            # Hide the tab bar
            self.tab_bar.pack_forget()

            # Make sure we're in customer view
            self.show_customer_view()


if __name__ == "__main__":
    # Initialize test data if needed
    if not os.path.exists("OrderDB.json"):
        initialize_test_data()

    # Create main window
    root = tk.Tk()
    root.title("Restaurant Management System")
    root.geometry("1400x800")
    root.minsize(1200, 700)

    # Initialize models
    user_model = UserModel()
    menu_model = MenuModel()
    table_model = TableModel()

    # Initialize controllers
    user_controller = UserController(user_model)
    menu_controller = MenuController(menu_model)
    table_controller = TableController(table_model)
    order_controller = EnhancedOrderController()

    # Create app manager
    app_manager = AppManager(root, user_controller)

    # Create user view
    # Create login-related views
    login_view = LoginView(root, user_controller, lambda: app_manager.update_ui())
    register_view = RegisterView(root, user_controller)
    table_choice_view = TableChoice(root, login_view, None)

    # Create MainView
    main_view = MainView(root, user_controller, menu_controller)

    # Create CustomerView
    customer_view = CustomerView(main_view.user_area, user_controller, login_view, register_view, table_choice_view)
    main_view.set_user_view(customer_view)

    # Update login callback to refresh UI when user logs in
    login_view.update_callback = lambda: [customer_view.update_ui(), app_manager.update_ui()]

    # Move MainView components from root to customer_view_frame
    for widget in list(root.winfo_children()):
        if widget != app_manager.main_container and not isinstance(widget, tk.Toplevel):
            widget.pack_forget()
            widget.place_forget() if hasattr(widget, 'place_forget') else None
            widget.grid_forget() if hasattr(widget, 'grid_forget') else None
            widget.pack(in_=app_manager.customer_view_frame, fill="both", expand=True)

    # Create staff view
    # Use PanedWindow as split view
    staff_pane = tk.PanedWindow(app_manager.staff_view_frame, orient=tk.HORIZONTAL, sashwidth=5)
    staff_pane.pack(fill="both", expand=True)

    # Create left and right panels
    left_frame = tk.Frame(staff_pane, bg="#F7F9FC")
    right_frame = tk.Frame(staff_pane, bg="#F7F9FC")

    # Add panels to PanedWindow
    staff_pane.add(left_frame, minsize=600, width=800)
    staff_pane.add(right_frame, minsize=400, width=600)

    # Create BartenderView
    bartender_view = BartenderView(left_frame, table_controller)
    bartender_view.pack(fill="both", expand=True, padx=5, pady=5)

    # Create OrderViewManager
    order_view_manager = OrderViewManager(right_frame, order_controller)

    # Initially show customer view
    app_manager.customer_view_frame.pack(fill="both", expand=True)

    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    root.mainloop()