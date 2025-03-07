#we might not need it if we integrate it in the other views
import tkinter as tk
from tkinter import simpledialog,messagebox,ttk
#from Controllers.OrderController import OrderController

class OrderView:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.root.title("Order") #initial window
        self.root.geometry("1000x700")
        self.root.pack_propagate(False)  # 禁止 Frame 根据子组件调整大小

        self.order_status = 0

        # 创建confirm_order按钮面板
        self.confirm_panel = tk.Frame(root, width=100, height=10, bg="lightgray") #create window frame
        self.confirm_panel.pack(side="bottom",fill="both",  expand=True) #put it in outer window
        self.confirm_panel.pack_propagate(False)
        # 初始化confirm面板
        self.init_confirm_order()

        # 创建order_title面板
        self.order_title = tk.Frame(root, width=100, height=10, bg="lightgray")  # create window frame
        self.order_title.pack(side="top", fill="both", expand=True)  # put it in outer window
        self.order_title.pack_propagate(False)
        # 初始化confirm面板
        self.init_title_order()

        # 创建主order面板
        self.order_panel = tk.Frame(root, width=100, height=50, bg="white")
        self.order_panel.pack(side="top", fill="both", expand=True)
        self.order_panel.pack_propagate(False)
        # 初始化订单面板

    def init_confirm_order(self):
        #结算按钮
        checkout_button = tk.Button(self.confirm_panel, text="Check Out", command=self.checkout, width=30, height=3)
        checkout_button.pack(side="bottom", expand=True)

    def init_title_order(self):
        # 订单标题
        tk.Label(self.order_title, text="Order Details", font=("Arial", 16), bg="white").grid(sticky="we", padx=5, pady=5)


    def order_start(self):
        if self.order_status == 1:
            self.update_items()

    def update_items(self):
        # show items and buttons
        for widget in self.order_panel.winfo_children():
            widget.destroy()

        for i, item in enumerate(self.controller.order.items):
            print(item)
            # 创建product标签
            label = tk.Label(self.order_panel, text=item["product_id"], width=30, height=1, bg="white")
            label.grid(row=i + 1, column=0, sticky="w", padx=5, pady=2)

            # 创建price标签
            label = tk.Label(self.order_panel, text=item["price"], width=20, height=1, bg="white")
            label.grid(row=i + 1, column=1, sticky="w", padx=5, pady=2)

            # 创建amount标签
            label = tk.Label(self.order_panel, text=item["amount"], width=20, height=1, bg="white")
            label.grid(row=i + 1, column=2, sticky="w", padx=5, pady=2)

            # 创建specification按钮
            options = ["can", "bottle"]
            combobox = ttk.Combobox(self.order_panel, values=options, width=20, height=1)
            index = options.index(item["specification"])
            combobox.current(index)  # 设置默认选中项（索引从 0 开始）
            combobox.grid(row=i + 1, column=3, sticky="w", padx=5, pady=2)
            combobox.bind("<<ComboboxSelected>>",
                          lambda event, item=item, combobox=combobox: self.controller.pick_spe(item["product_id"],
                                                                                               combobox.get()))
            # 这里的问题是，lambda 会捕获循环变量 item 的引用，而不是它的值。由于 lambda 是延迟执行的（只有在按钮点击时才会执行），当按钮被点击时，item 的值已经是循环结束后的最终值，而不是每次迭代时的值。

            # 创建notes按钮
            label = tk.Button(self.order_panel, text="notes", width=10, height=1, bg="lightblue",
                              command=lambda item=item: self.notes_dialog(item["product_id"], item["note"]))
            label.grid(row=i + 1, column=4, sticky="w", padx=5, pady=2)

            # 创建-按钮
            button = tk.Button(self.order_panel, text="-", width=5, height=1, bg="lightgray",
                               command=lambda item=item: self.controller.minus1_item(item["product_id"]))
            button.grid(row=i + 1, column=5, sticky="e", padx=5, pady=2)

            # 创建+按钮
            button = tk.Button(self.order_panel, text="+", width=5, height=1, bg="lightgray",
                               command=lambda item=item: self.controller.plus1_item(item["product_id"]))
            button.grid(row=i + 1, column=6, sticky="e", padx=5, pady=2)

    def notes_dialog(self, product_id, current_note):
        task = simpledialog.askstring("notes", "Current notes:"+ current_note)
        if task:  # 如果用户输入了内容
            self.controller.add_notes(product_id, task)  # 调用 Controller 添加任务
            messagebox.showinfo("Success", "Notes added")

    def checkout(self):
        from Controllers.OrderController import OrderController
        self.controller = OrderController(self, 1, 1)
        self.update_items()


# if __name__ == "__main__":
#     root = tk.Tk()
#     app = OrderView(root, None)
#     Order_test =OrderController(app,1,1)
#     app.some_method()
#     root.mainloop()