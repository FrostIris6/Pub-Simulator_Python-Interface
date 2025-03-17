import tkinter as tk
from tkinter import ttk, messagebox
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
from Controllers.TranslationController import TranslationController

# Import views
from Views.MainView import MainView
from Views.CustomerView import CustomerView
from Views.BartenderView import BartenderView
from Views.Order_bar_view import OrderListView, OrderDetailView, OrderCard, HistoryDetailView
from Views.LoginView import LoginView, RegisterView, TableChoice


# 创建语言选择窗口 / Create language selection window
def create_language_selector(root, translation_controller, callback=None):
    """
    创建语言选择器对话框
    Create a language selector dialog

    Args:
        root: 父窗口 / Parent window
        translation_controller: 翻译控制器 / Translation controller
        callback: 语言更改后的回调函数 / Callback function after language change
    """
    language_window = tk.Toplevel(root)
    language_window.title("Language / 语言 / Språk")
    language_window.geometry("300x200")
    language_window.resizable(False, False)
    language_window.transient(root)
    language_window.grab_set()

    # 居中窗口 / Center window
    language_window.update_idletasks()
    width = language_window.winfo_width()
    height = language_window.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    language_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    # 标题 / Title
    tk.Label(
        language_window,
        text="Select Language / 选择语言 / Välj Språk",
        font=("Arial", 12, "bold")
    ).pack(pady=15)

    # 获取可用语言 / Get available languages
    languages = translation_controller.get_available_languages()

    # 当前选择的语言 / Currently selected language
    selected_language = tk.StringVar(value=translation_controller.get_current_language())

    # 创建语言选项 / Create language options
    for code, name in languages.items():
        rb = ttk.Radiobutton(
            language_window,
            text=name,
            value=code,
            variable=selected_language
        )
        rb.pack(anchor=tk.W, padx=20, pady=5)

    # 按钮框架 / Button frame
    button_frame = tk.Frame(language_window)
    button_frame.pack(side=tk.BOTTOM, pady=15)

    # 获取按钮文本 / Get button text
    apply_text = "Apply"
    cancel_text = "Cancel"
    if translation_controller:
        apply_text = translation_controller.get_text("dialogs.confirm", default=apply_text)
        cancel_text = translation_controller.get_text("user_interface.cancel", default=cancel_text)

    # 应用按钮 / Apply button
    def apply_language():
        new_lang_code = selected_language.get()
        if translation_controller.set_language(new_lang_code):
            success_text = "Language changed successfully"
            if translation_controller:
                languages = translation_controller.get_available_languages()
                lang_name = languages.get(new_lang_code, new_lang_code)
                success_text = translation_controller.get_text(
                    "dialogs.language_changed",
                    default=f"Language changed to {lang_name}"
                )
            messagebox.showinfo("Success", success_text)
            language_window.destroy()
            if callback:
                callback()

    ttk.Button(
        button_frame,
        text=apply_text,
        command=apply_language
    ).pack(side=tk.LEFT, padx=5)

    # 取消按钮 / Cancel button
    ttk.Button(
        button_frame,
        text=cancel_text,
        command=language_window.destroy
    ).pack(side=tk.LEFT, padx=5)


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

    def update_text(self, text):
        """更新标签文本"""
        self.label.config(text=text)


# Create a class to handle the order view navigation
class OrderViewManager:
    def __init__(self, parent, controller, translation_controller=None):
        self.parent = parent
        self.controller = controller
        self.translation_controller = translation_controller
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
        self.current_frame = OrderListView(
            self.container,
            self.controller,
            self,
            translation_controller=self.translation_controller
        )
        self.current_frame.pack(fill="both", expand=True)
        self.current_view = "list"

    def show_detail_view(self, transaction_id):
        self._clear_container()
        # Get the order and display detail view
        order = self.controller.get_order_by_transaction(transaction_id)
        if order:
            self.current_frame = OrderDetailView(
                self.container,
                self.controller,
                order,
                self,
                translation_controller=self.translation_controller
            )
            self.current_frame.pack(fill="both", expand=True)
            self.current_view = "detail"
            self.current_transaction_id = transaction_id

    def show_history_view(self):
        self._clear_container()
        # Create a custom history view frame
        history_frame = tk.Frame(self.container)
        history_frame.pack(fill="both", expand=True)

        # 获取翻译文本 / Get translated texts
        back_text = "← Back"
        order_history_text = "Order History"
        no_history_orders_text = "No history orders"

        if self.translation_controller:
            back_text = self.translation_controller.get_text(
                "general.back",
                default=back_text
            )
            order_history_text = self.translation_controller.get_text(
                "views.order_management.order_history",
                default=order_history_text
            )
            no_history_orders_text = self.translation_controller.get_text(
                "views.order_management.no_history_orders",
                default=no_history_orders_text
            )

        # Add header with back button
        header = tk.Frame(history_frame, bg="#f5f6fa")
        header.pack(fill="x", pady=5)

        ttk.Button(header, text=back_text, command=self.show_list_view).pack(side="left", padx=10, pady=5)
        tk.Label(header, text=order_history_text, font=("Arial", 14, "bold"), bg="#f5f6fa").pack(side="left", padx=20,
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
            tk.Label(cards_frame, text=no_history_orders_text, font=("Arial", 12), bg="white").pack(pady=20)
        else:
            for order in orders:
                card = OrderCard(
                    cards_frame,
                    order,
                    on_click=lambda tid=order["transaction_id"]: self.show_history_detail_view(tid),
                    bg="white",
                    width=350,
                    translation_controller=self.translation_controller
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
            self.current_frame = HistoryDetailView(
                self.container,
                self.controller,
                order,
                self,
                translation_controller=self.translation_controller
            )
            self.current_frame.pack(fill="both", expand=True)
            self.current_view = "history_detail"
        else:
            # 获取错误消息的翻译
            error_title = "Error"
            error_message = "Order not found"

            if self.translation_controller:
                error_title = self.translation_controller.get_text(
                    "dialogs.error",
                    default=error_title
                )
                error_message = self.translation_controller.get_text(
                    "dialogs.product_not_found",
                    default=error_message
                ).replace("Product", "Order")

            messagebox.showerror(error_title, error_message)
            self.show_history_view()

    def update_translations(self):
        """更新订单视图管理器中的所有翻译"""
        # 如果当前有活动视图，更新其翻译
        if self.current_frame and hasattr(self.current_frame, 'update_translations'):
            self.current_frame.update_translations()

        # 如果当前视图是列表视图，强制刷新以更新翻译
        if self.current_view == "list":
            self.show_list_view()
        # 如果当前视图是历史视图，强制刷新以更新翻译
        elif self.current_view == "history":
            self.show_history_view()


# Application Manager class to handle view switching and user roles
class AppManager:
    def __init__(self, root, user_controller, translation_controller=None):
        self.root = root
        self.user_controller = user_controller
        self.translation_controller = translation_controller

        # 创建语言切换按钮
        self.create_language_button()

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

    def update_language_button(self):
        """更新语言按钮文本"""
        language_text = "Language"
        if self.translation_controller:
            language_text = self.translation_controller.get_text(
                "general.language",
                default=language_text
            )

        # 查找并更新语言按钮文本
        for widget in self.toolbar.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.configure(text=language_text)
                break

    def create_language_button(self):
        """创建语言切换按钮"""
        # 创建顶部工具栏
        self.toolbar = tk.Frame(self.root, bg="#f0f0f0", height=30)  # 保存为实例变量
        self.toolbar.pack(side="top", fill="x")

        # 获取语言按钮文本
        language_text = "Language"
        if self.translation_controller:
            language_text = self.translation_controller.get_text(
                "general.language",
                default=language_text
            )

        # 创建语言按钮
        language_btn = ttk.Button(
            self.toolbar,
            text=language_text,
            command=self.show_language_selector
        )
        language_btn.pack(side="right", padx=10, pady=2)

    # 将这段代码替换到CombineView.py文件中对应的地方

    # 修复AppManager类中的方法
    def show_language_selector(self):
        """显示语言选择器"""
        if self.translation_controller:
            # 直接使用内联定义的语言选择器对话框
            language_window = tk.Toplevel(self.root)
            language_window.title("Language / 语言 / Språk")
            language_window.geometry("400x250")  # 显著增加窗口宽度
            language_window.resizable(True, True)  # 允许调整大小
            language_window.transient(self.root)
            language_window.grab_set()

            # 居中窗口
            language_window.update_idletasks()
            width = language_window.winfo_width()
            height = language_window.winfo_height()
            x = (self.root.winfo_screenwidth() // 2) - (width // 2)
            y = (self.root.winfo_screenheight() // 2) - (height // 2)
            language_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

            # 标题
            tk.Label(
                language_window,
                text="Select Language / 选择语言 / Välj Språk",
                font=("Arial", 12, "bold")
            ).pack(pady=15)

            # 获取可用语言
            languages = self.translation_controller.get_available_languages()

            # 当前选择的语言
            selected_language = tk.StringVar(value=self.translation_controller.get_current_language())

            # 创建语言选项
            for code, name in languages.items():
                rb = ttk.Radiobutton(
                    language_window,
                    text=name,
                    value=code,
                    variable=selected_language
                )
                rb.pack(anchor=tk.W, padx=20, pady=5)

            # 按钮框架
            button_frame = tk.Frame(language_window)
            button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

            # 确保按钮框架中的列有合适的权重
            button_frame.columnconfigure(0, weight=1)
            button_frame.columnconfigure(1, weight=1)

            # 获取按钮文本
            apply_text = "Apply"
            cancel_text = "Cancel"
            if self.translation_controller:
                apply_text = self.translation_controller.get_text("dialogs.confirm", default=apply_text)
                cancel_text = self.translation_controller.get_text("user_interface.cancel", default=cancel_text)

            # 使用grid布局管理器，确保按钮有足够的空间
            cancel_btn = ttk.Button(
                button_frame,
                text=cancel_text,
                command=language_window.destroy,
                width=15  # 固定宽度
            )
            cancel_btn.grid(row=0, column=0, padx=20, pady=5, sticky="ew")

            # 应用按钮回调
            def apply_language():
                new_lang_code = selected_language.get()
                if self.translation_controller.set_language(new_lang_code):
                    success_text = "Language changed successfully"
                    if self.translation_controller:
                        languages = self.translation_controller.get_available_languages()
                        lang_name = languages.get(new_lang_code, new_lang_code)
                        success_text = self.translation_controller.get_text(
                            "dialogs.language_changed",
                            default=f"Language changed to {lang_name}"
                        )
                    messagebox.showinfo("Success", success_text)
                    language_window.destroy()
                    self.update_language()

            apply_btn = ttk.Button(
                button_frame,
                text=apply_text,
                command=apply_language,
                width=15  # 固定宽度
            )
            apply_btn.grid(row=0, column=1, padx=20, pady=5, sticky="ew")

            # 设置最小窗口尺寸
            language_window.update_idletasks()
            language_window.minsize(400, 250)

    def update_all_translations(self):
        """递归更新所有视图的翻译"""
        # 更新语言按钮文本
        self.update_language_button()

        # 更新标签页标题
        if self.current_view == "customer":
            self.show_customer_view(force_update=True)
        else:
            self.show_staff_view(force_update=True)

        # 更新主视图及其子视图
        if 'main_view' in globals() and hasattr(main_view, 'update_translations'):
            main_view.update_translations()

            # 直接更新主视图中的订单框架
            if hasattr(main_view, 'order_frame') and main_view.order_frame:
                if hasattr(main_view.order_frame, 'update_translations'):
                    main_view.order_frame.update_translations()

        # 更新客户视图
        if hasattr(customer_view, 'update_translations'):
            customer_view.update_translations()

        # 更新服务员视图
        if hasattr(bartender_view, 'update_translations'):
            bartender_view.update_translations()

        # 更新订单视图
        if hasattr(order_view_manager, 'update_translations'):
            order_view_manager.update_translations()

    def update_language(self):
        """更新语言后的回调"""
        # 更新窗口标题
        app_title = "Restaurant Management System"
        if self.translation_controller:
            app_title = self.translation_controller.get_text(
                "general.app_title",
                default=app_title
            )
        self.root.title(app_title)

        # 更新所有翻译
        self.update_all_translations()

        # 设置延迟任务来执行第二次更新
        self.root.after(100, self.delayed_update)

        # 通知用户
        language_changed_text = "Interface language has been changed."
        success_title = "Success"


        if self.translation_controller:
            languages = self.translation_controller.get_available_languages()
            current_lang = self.translation_controller.get_current_language()
            lang_name = languages.get(current_lang, current_lang)

            language_changed_text = self.translation_controller.get_text(
                "dialogs.language_changed_notice",
                default=f"Interface language has been changed to {lang_name}."
            )

            success_title = self.translation_controller.get_text(
                "dialogs.success",
                default=success_title
            )

        messagebox.showinfo(success_title, language_changed_text)

    def delayed_update(self):
        """延迟执行的更新，确保捕获所有动态加载的组件"""
        # 再次更新订单框架
        if 'main_view' in globals() and hasattr(main_view, 'order_frame') and main_view.order_frame:
            if hasattr(main_view.order_frame, 'update_translations'):
                main_view.order_frame.update_translations()

    def setup_tabs(self):
        # Clear existing tabs if any
        for widget in self.tab_bar.winfo_children():
            widget.destroy()

        # 获取标签文本翻译
        product_tab_text = "Product"
        table_tab_text = "Table"

        if self.translation_controller:
            product_tab_text = self.translation_controller.get_text(
                "views.menu.products",
                default=product_tab_text
            )
            table_tab_text = self.translation_controller.get_text(
                "views.bartender.table_status.bar",
                default=table_tab_text
            )

        # Create tabs
        self.customer_tab = CustomTab(self.tab_bar, product_tab_text, self.show_customer_view,
                                      is_active=(self.current_view == "customer"))
        self.customer_tab.pack(side="left")

        self.staff_tab = CustomTab(self.tab_bar, table_tab_text, self.show_staff_view,
                                   is_active=(self.current_view == "staff"))
        self.staff_tab.pack(side="left")

    def show_customer_view(self, force_update=False):
        if self.current_view != "customer" or force_update:
            if self.current_view != "customer":
                self.staff_view_frame.pack_forget()
                self.customer_view_frame.pack(fill="both", expand=True)

            # 更新标签文本
            if self.customer_tab and self.staff_tab:
                product_tab_text = "Product"
                if self.translation_controller:
                    product_tab_text = self.translation_controller.get_text(
                        "views.menu.products",
                        default=product_tab_text
                    )
                self.customer_tab.label.config(text=product_tab_text)
                self.customer_tab.set_active(True)
                self.staff_tab.set_active(False)

            self.current_view = "customer"

    def show_staff_view(self, force_update=False):
        if self.current_view != "staff" or force_update:
            if self.current_view != "staff":
                self.customer_view_frame.pack_forget()
                self.staff_view_frame.pack(fill="both", expand=True)

            # 更新标签文本
            if self.customer_tab and self.staff_tab:
                table_tab_text = "Table"
                if self.translation_controller:
                    table_tab_text = self.translation_controller.get_text(
                        "views.bartender.table_status.bar",
                        default=table_tab_text
                    )
                self.staff_tab.label.config(text=table_tab_text)
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

    # 初始化翻译控制器
    translation_controller = TranslationController()  # 使用您现有的实现

    # 获取并设置应用标题
    app_title = translation_controller.get_text("general.app_title", default="Restaurant Management System")
    root.title(app_title)

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

    # Create app manager with translation controller
    app_manager = AppManager(root, user_controller, translation_controller)

    # Create login-related views
    login_view = LoginView(root, user_controller, lambda: app_manager.update_ui(), translation_controller)
    register_view = RegisterView(root, user_controller, translation_controller)
    table_choice_view = TableChoice(root, login_view, None, translation_controller)

    # Create MainView with translation controller
    main_view = MainView(root, user_controller, menu_controller, translation_controller)

    # Create CustomerView with translation controller
    customer_view = CustomerView(main_view.user_area, user_controller, login_view, register_view, table_choice_view,
                                 translation_controller)
    main_view.set_user_view(customer_view)

    # Update login callback to refresh UI when user logs in
    login_view.update_callback = lambda: [customer_view.update_ui(), app_manager.update_ui()]

    # Move MainView components from root to customer_view_frame
    for widget in list(root.winfo_children()):
        if widget != app_manager.main_container and not isinstance(widget,
                                                                   tk.Toplevel) and widget != app_manager.toolbar:
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

    # Create BartenderView with translation controller
    bartender_view = BartenderView(left_frame, table_controller, translation_controller=translation_controller)
    bartender_view.pack(fill="both", expand=True, padx=5, pady=5)

    # Create OrderViewManager with translation controller
    order_view_manager = OrderViewManager(right_frame, order_controller, translation_controller=translation_controller)

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