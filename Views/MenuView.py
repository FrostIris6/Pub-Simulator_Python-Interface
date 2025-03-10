import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk  

class MenuView(tk.Tk):
    def __init__(self, controller):
        super().__init__()
        
        self.controller = controller
        
        # Window setup
        self.title("Menu Management")
        self.geometry("1800x900")  # Enlarged window size

        # Left category panel
        self.left_frame = tk.Frame(self, width=300)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsw")
        self.left_frame.grid_columnconfigure(0, weight=0)

        # Main display area
        self.right_frame = tk.Frame(self)
        self.right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(0, weight=1)

        # Scrollable canvas
        self.canvas = tk.Canvas(self.right_frame, width=1200, height=750)  # Made it much larger
        self.scrollbar = tk.Scrollbar(self.right_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Scrollable frame inside canvas
        self.scrollable_frame = tk.Frame(self.canvas, width=1200, height=750)  # Enlarged frame
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.config(scrollregion=self.canvas.bbox("all")))

        # Category buttons
        self.categories = ['wine', 'beer', 'cocktail', 'food', 'fridge']
        self.category_buttons = {}
        for i, category in enumerate(self.categories):
            btn = tk.Button(self.left_frame, text=category.capitalize(), width=25, command=lambda c=category: self.display_category(c))
            btn.grid(row=i, column=0, pady=5)
            self.category_buttons[category] = btn

        # Product list
        self.product_label = tk.Label(self.scrollable_frame, text="Products", font=("Arial", 20))
        self.product_label.grid(row=0, column=0, pady=10)

        self.product_listbox = tk.Listbox(self.scrollable_frame, width=100, height=10, selectmode=tk.SINGLE)  # Much bigger listbox
        self.product_listbox.grid(row=1, column=0, padx=10, pady=10)
        self.product_listbox.bind('<<ListboxSelect>>', self.on_product_select)

        # Stock update form
        self.stock_label = tk.Label(self.scrollable_frame, text="Update Stock", font=("Arial", 16, "bold"))
        self.stock_label.grid(row=2, column=0, pady=10)

        self.stock_name_label = tk.Label(self.scrollable_frame, text="Product Name:")
        self.stock_name_label.grid(row=3, column=0, padx=5, pady=5)

        self.stock_name = tk.Label(self.scrollable_frame, text="", font=("Arial", 12, "bold"))
        self.stock_name.grid(row=3, column=1, padx=5, pady=5)

        self.stock_input_label = tk.Label(self.scrollable_frame, text="New Stock Quantity:")
        self.stock_input_label.grid(row=4, column=0, padx=5, pady=5)

        self.stock_input = tk.Entry(self.scrollable_frame, width=15)
        self.stock_input.grid(row=4, column=1, padx=5, pady=5)

        self.update_stock_button = tk.Button(self.scrollable_frame, text="Update Stock", command=self.update_stock)
        self.update_stock_button.grid(row=5, column=0, columnspan=2, pady=10)

        # Product details
        self.photo_label = tk.Label(self.scrollable_frame, text="Product Photo:")
        self.photo_label.grid(row=6, column=0, pady=10)

        self.photo_display = tk.Label(self.scrollable_frame)  
        self.photo_display.grid(row=7, column=0, pady=10)

        self.description_label = tk.Label(self.scrollable_frame, text="Description:")
        self.description_label.grid(row=8, column=0, pady=10)

        self.description_text = tk.Label(self.scrollable_frame, text="", wraplength=800, justify="left")  # Wider description area
        self.description_text.grid(row=9, column=0, pady=10)

    def display_category(self, category):
    # Reset all category buttons
        for btn in self.category_buttons.values():
            btn.config(bg="SystemButtonFace")

        # Get items in the category
        items = self.controller.get_items_by_category(category)

        # Check if any item is low on stock
        low_stock = any(item.stock < 5 for item in items)

        # If any item is low on stock, mark the button red
        if low_stock:
            self.category_buttons[category].config(bg="red")
        else:
            self.category_buttons[category].config(bg="lightblue")

        # Clear the product listbox
        self.product_listbox.delete(0, tk.END)

        # Populate listbox with products and change color if stock < 5
        for item in items:
            index = self.product_listbox.size()
            self.product_listbox.insert(tk.END, item.name)
            
            # If stock is low, change text color to red
            if item.stock < 5:
                self.product_listbox.itemconfig(index, {'fg': 'red'})


    def on_product_select(self, event):
        selected_product = self.product_listbox.get(tk.ACTIVE)
        product = next((item for item in self.controller.model.menu if item.name == selected_product), None)

        if product:
            self.stock_name.config(text=product.name)
            self.stock_input.delete(0, tk.END)
            self.stock_input.insert(0, str(product.stock))

            self.description_text.config(text=product.description.get('en', "No description available"))

            if product.image:
                self.show_image(product.image)
            else:
                self.photo_display.config(image="")

    def show_image(self, image_path):
        try:
            img = Image.open(image_path)
            img = img.resize((200, 200), Image.Resampling.LANCZOS)  
            img = ImageTk.PhotoImage(img)
            self.photo_display.config(image=img)
            self.photo_display.image = img  
        except Exception as e:
            print(f"Error loading image: {e}")
            self.photo_display.config(image="")

    def update_stock(self):
        product_name = self.stock_name.cget("text")
        new_stock = self.stock_input.get()

        if not new_stock.isdigit():
            messagebox.showerror("Invalid Input", "Please enter a valid stock number.")
            return

        new_stock = int(new_stock)
        product = next((item for item in self.controller.model.menu if item.name == product_name), None)

        if product:
            if self.controller.update_item_stock(product.id, new_stock):
                messagebox.showinfo("Success", f"Stock for {product_name} updated to {new_stock}.")
                self.display_category(product.category)
            else:
                messagebox.showerror("Error", "Failed to update stock.")
        else:
            messagebox.showerror("Error", "Product not found.")
