import tkinter as tk
from tkinter import Frame, Label, Button, messagebox
from Views.OrderViewClass import OrderViewClass
from Views.MenuView import MenuView

class MainView:
    def __init__(self, root, user_controller, menu_controller):  # Accept both controllers
        self.root = root
        self.user_controller = user_controller
        self.menu_controller = menu_controller
        #self.root.title("Main View")
        #self.root.geometry("1440x800+0+0")  # Approximate resolution for a 10-inch tablet
        #self.root.configure(bg="white")

        # Initialize the main layout
        self.create_layout()

    def create_layout(self):

        # Right-side user information & menu display area
        self.main_content = Frame(self.root, bg="white", width=1440, height=800)
        self.main_content.pack(side="right", fill="both", expand=True)

        # Upper-right section (User info display area)
        self.user_area = Frame(self.main_content, bg="#f0f0f0", height=150)
        self.user_area.pack(fill="x")

        self.user_label = Label(self.user_area, text="Welcome to the BAR !!", font=("Arial", 16), bg="#f0f0f0")
        self.user_label.pack(pady=20)

        # bottom section for menu and order
        self.bottom_aera = Frame(self.main_content, bg="white") #coordinate x=0, y=150
        self.bottom_aera.pack(fill="both", expand=True)

        # Lower-left section (Menu display area)
        self.menu_area = Frame(self.bottom_aera, bg="white")
        self.menu_area.pack(side="left", fill="both", expand=True)

        self.order_area = Frame(self.bottom_aera, bg="white", bd=2, relief="solid")
        self.order_area.pack(side="left", fill="both", expand=True)
        
        self.menu_frame = MenuView(self.menu_area, self.menu_controller, self.user_controller)
        self.menu_frame.pack(fill="both", expand=True)
        # menu and order can't show complete view both, I think reason is from their own codes, not outer frame or pack
        # put order frame here
        self.order_frame = OrderViewClass(self.order_area, None)
        
        self.user_controller.set_menu_view(self.menu_frame)

########drag & drop by Charles###################################
        # 绑定事件
        self.menu_frame.product_listbox.bind("<Button-1>", self.on_drag_start)  # 开始拖拽
        #self.order_frame.order_panel.bind("<Button-1>", lambda e: print("Button-1 clicked on order_area"))
        self.menu_frame.product_listbox.bind("<ButtonRelease-1>", self.on_drop)

    def on_drag_start(self, event):
        """ 记录被拖拽的 Listbox 项目文本 """
        try:
            selected = self.menu_frame.product_listbox.get(self.menu_frame.product_listbox.curselection())  # 获取选中的文本
            self.menu_frame.product_listbox.drag_data = {"text": selected}
            #print(selected)#pick successfully
            # widget = event.widget
            # x = widget.winfo_x()  # correct initial placement do not modify
            # y = widget.winfo_y()  # location to window
            # self.dragging_item = tk.Label(self.root, text=widget["text"], bg="lightblue", padx=10, pady=5)
            # self.dragging_item.place(x=x, y=y)
            # # print(x, y)
            # # 计算鼠标相对组件的偏移量
            # self.offset_x = event.x
            # self.offset_y = event.y
            # print(self.offset_x, self.offset_y)
        except:
            return

    def on_drop(self, event):
        """ 在 Frame 中放置 Label """
        if hasattr(self.menu_frame.product_listbox, "drag_data"):
            text = self.menu_frame.product_listbox.drag_data["text"]
            print(text)
            # label = tk.Label(self.order_frame.order_panel, text=text, bg="lightblue", padx=10, pady=5)
            # label.pack()  # 在鼠标松开的位置放置 Label
            x, y = event.x_root, event.y_root
            order_x1 = self.order_frame.order_panel.winfo_rootx()
            order_y1 = self.order_frame.order_panel.winfo_rooty()
            order_x2 = order_x1 + self.order_frame.order_panel.winfo_width()
            order_y2 = order_y1 + self.order_frame.order_panel.winfo_height()

            if order_x1 < x < order_x2 and order_y1 < y < order_y2:
                # check if in target area
                try:
                    self.order_frame.add_item_from_menu(text)
                except AttributeError:
                    messagebox.showinfo("Warning!", "Please confirm table first")


    ########################################################################

    def set_user_view(self, view):
        """Set and display the user view."""
        if hasattr(self, "user_view"):
            self.user_view.destroy()  # Destroy the previous view before updating

        self.user_view = view
        self.user_view.pack(fill="both", expand=True)

    def set_menu_view(self, view):
        """Set the menu display area."""
        for widget in self.menu_area.winfo_children():
            widget.destroy()  # Clear old widgets
        view.pack(fill="both", expand=True)
        
    

