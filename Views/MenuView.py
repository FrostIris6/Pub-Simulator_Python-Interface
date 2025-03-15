import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk  

class MenuView(tk.Frame):
    def __init__(self, root, menu_controller, user_controller):
        super().__init__(root)
        self.controller = menu_controller
        self.user_controller = user_controller
        
        self.user_role = self.user_controller.get_current_user_role() 

        # Left category panel
        self.left_frame = tk.Frame(self, width=300)
        self.left_frame.grid(row=0, column=0, padx=10, pady=0, sticky="nsw")
        self.left_frame.grid_columnconfigure(0, weight=0)

        # Main display area
        self.right_frame = tk.Frame(self)
        self.right_frame.grid(row=0, column=1, padx=10, pady=0, sticky="nsew")
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(0, weight=1)

        # Scrollable canvas
        self.canvas = tk.Canvas(self.right_frame, width=500, height=550)  
        self.scrollbar = tk.Scrollbar(self.right_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Scrollable frame inside canvas
        self.scrollable_frame = tk.Frame(self.canvas, width=1200, height=750)  # Enlarged frame
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.config(scrollregion=self.canvas.bbox("all")))

        # Category buttons
        self.categories = ['wine', 'beer', 'cocktail', 'food']
        if self.user_role in ['customer', 'bartender']:  # Only show fridge if user is 'customer' or 'bartender'
            self.categories.append('fridge')
            
        self.category_buttons = {}
        for i, category in enumerate(self.categories):
            btn = tk.Button(self.left_frame, text=category.capitalize(), fg="black", font=("Arial", 14), width=25, command=lambda c=category: self.display_category(c))
            btn.grid(row=i, column=0, pady=5)
            self.category_buttons[category] = btn
            
        

        # Product list 
        self.product_label = tk.Label(self.scrollable_frame, text="Products", font=("Arial", 20))
        self.product_label.grid(row=0, column=0, pady=10, sticky="w")

        # Create a frame for the product list
        self.product_frame = tk.Frame(self.scrollable_frame)
        self.product_frame.grid(row=1, column=0, padx=10, pady=10, sticky="w")  # Align left

        self.product_listbox = tk.Listbox(self.product_frame, width=50, height=10, selectmode=tk.SINGLE)  # Half the width
        self.product_listbox.pack()

        self.product_listbox.bind('<<ListboxSelect>>', self.on_product_select)

        # Stock update section
        self.stock_label = tk.Label(self.scrollable_frame, text="Update Stock", font=("Arial", 16, "bold"))
        self.stock_label.grid(row=2, column=0, pady=10, sticky="w")  # Aligned left

        self.stock_name_label = tk.Label(self.scrollable_frame, text="Product Name:")
        self.stock_name_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")  # Aligned left

        self.stock_name = tk.Label(self.scrollable_frame, text="", font=("Arial", 12, "bold"))
        self.stock_name.grid(row=3, column=1, padx=5, pady=5, sticky="w")  # Next to label

        self.stock_input_label = tk.Label(self.scrollable_frame, text="New Stock Quantity:")
        self.stock_input_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")  # Aligned left

        self.stock_input = tk.Entry(self.scrollable_frame, width=10)
        self.stock_input.grid(row=4, column=1, padx=5, pady=5, sticky="w")  # Aligned left

        self.update_stock_button = tk.Button(self.scrollable_frame, text="Update Stock", command=self.update_stock)
        self.update_stock_button.grid(row=5, column=1, columnspan=2, pady=10, sticky="w")  # Left-aligned button
        
        self.stock_price_label = tk.Label(self.scrollable_frame, text="Product Price:")
        self.stock_price_label.grid(row=6, column=0, padx=5, pady=5, sticky="w")  # Aligned left
        
        self.stock_price = tk.Label(self.scrollable_frame, text="", font=("Arial", 12, "bold"))
        self.stock_price.grid(row=6, column=1, padx=5, pady=5, sticky="w")  # Next to label
        
        self.update_stock_ui()
        self.update_categories()

        # Product details
        self.photo_label = tk.Label(self.scrollable_frame, text="Product Photo:")
        self.photo_label.grid(row=7, column=0, pady=10)

        self.photo_display = tk.Label(self.scrollable_frame)  
        self.photo_display.grid(row=8, column=0, pady=10)

        self.description_label = tk.Label(self.scrollable_frame, text="Description:")
        self.description_label.grid(row=9, column=0, pady=10)

        self.description_text = tk.Label(self.scrollable_frame, text="", wraplength=800, justify="left")  # Wider description area
        self.description_text.grid(row=10, column=0, pady=10)

    def display_category(self, category):
        # Reset all category buttons
        for btn in self.category_buttons.values():
            btn.config(bg="SystemButtonFace")

        # Get items in the category
        items = self.controller.get_items_by_category(category)

        # Check if any item is low on stock
        low_stock = any(item.stock < 5 for item in items)

        # If any item is low on stock, mark the button red
        if low_stock and self.user_controller.get_current_user_role() == "bartender":
            self.category_buttons[category].config(bg="red")
        else:
            self.category_buttons[category].config(bg="lightblue")

        # Clear the product listbox
        self.product_listbox.delete(0, tk.END)

        # Populate listbox with products and change color if stock < 5
        for item in items:
            index = self.product_listbox.size()
            if self.user_controller.get_current_user_role() == "bartender": 
                self.product_listbox.insert(tk.END, item.name)
            elif self.user_controller.get_current_user_role() == "customer":
                if item.stock >= 5:
                    self.product_listbox.insert(tk.END, item.name)
            else:
                if item.is_vip == "NO" and item.stock >= 5:
                    self.product_listbox.insert(tk.END, item.name)
            
            # If stock is low, change text color to red
            if item.stock < 5 and self.user_controller.get_current_user_role() == "bartender":
                self.product_listbox.itemconfig(index, {'fg': 'red'})

    def on_product_select(self, event):
        selected_product = self.product_listbox.get(tk.ACTIVE)
        product = next((item for item in self.controller.model.menu if item.name == selected_product), None)

        if product:
            self.stock_name.config(text=product.name)
            self.stock_price.config(text=product.price)
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
            
    def update_categories(self):
        self.user_role = self.user_controller.get_current_user_role()
        self.update_stock_ui()
        
        # Remove old buttons
        for btn in self.category_buttons.values():
            btn.destroy()

        self.categories = ['wine', 'beer', 'cocktail', 'food']
        if self.user_role in ['customer', 'bartender']:  
            self.categories.append('fridge')

        # Create new buttons
        self.category_buttons = {}
        for i, category in enumerate(self.categories):
            btn = tk.Button(self.left_frame, text=category.capitalize(), fg="black", font=("Arial", 14), width=25, command=lambda c=category: self.display_category(c))
            btn.grid(row=i, column=0, pady=5)
            self.category_buttons[category] = btn
            
            
    def temporarily_remove(self):
        """Temporarily remove a product by setting its stock to 0."""
        product_name = self.stock_name.cget("text")

        if not product_name:
            messagebox.showerror("Error", "No product selected.")
            return

        confirm = messagebox.askyesno("Confirm Removal", f"Are you sure you want to temporarily remove '{product_name}'?")
        if not confirm:
            return

        product = next((item for item in self.controller.model.menu if item.name == product_name), None)

        if product:
            if self.controller.update_item_stock(product.id, 0):
                messagebox.showinfo("Success", f"'{product_name}' has been temporarily removed.")
                self.display_category(product.category)
            else:
                messagebox.showerror("Error", "Failed to remove product.")
        else:
            messagebox.showerror("Error", "Product not found.")
            
            
    def update_stock_ui(self):
        """Show stock update section only for bartenders."""
        if self.user_controller.get_current_user_role() == "bartender":
            self.stock_label.grid()
            self.stock_input_label.grid()
            self.stock_input.grid()
            self.update_stock_button.grid()
            
            # Add Temporarily Remove button next to Update Stock
            if not hasattr(self, "remove_button"):
                self.remove_button = tk.Button(self.scrollable_frame, text="Temporarily Remove", command=self.temporarily_remove, fg="white", bg="red")
                self.remove_button.grid(row=5, column=0, columnspan=2, pady=10, sticky="w")
            else:
                self.remove_button.grid()

        else:
            self.stock_label.grid_remove()
            self.stock_input_label.grid_remove()
            self.stock_input.grid_remove()
            self.update_stock_button.grid_remove()

            if hasattr(self, "remove_button"):
                self.remove_button.grid_remove()
            



           
            
    

