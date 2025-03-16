import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk


class MenuView(tk.Frame):
    def __init__(self, root, menu_controller, user_controller, translation_controller=None):
        super().__init__(root)
        self.controller = menu_controller
        self.user_controller = user_controller
        self.translation_controller = translation_controller  # 存储翻译控制器 / Store translation controller

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
            # 获取类别的翻译 / Get translation for category
            category_text = category.capitalize()
            if self.translation_controller:
                category_text = self.translation_controller.get_text(f"categories.{category}", default=category_text)

            btn = tk.Button(self.left_frame, text=category_text, fg="black", font=("Arial", 14), width=25,
                            command=lambda c=category: self.display_category(c))
            btn.grid(row=i, column=0, pady=5)
            self.category_buttons[category] = btn

        # 获取"Products"的翻译 / Get translation for "Products"
        products_text = "Products"
        if self.translation_controller:
            products_text = self.translation_controller.get_text("views.menu.products", default=products_text)

        # Product list
        self.product_label = tk.Label(self.scrollable_frame, text=products_text, font=("Arial", 20))
        self.product_label.grid(row=0, column=0, pady=10, sticky="w")

        # Create a frame for the product list
        self.product_frame = tk.Frame(self.scrollable_frame)
        self.product_frame.grid(row=1, column=0, padx=10, pady=10, sticky="w")  # Align left

        self.product_listbox = tk.Listbox(self.product_frame, width=50, height=10,
                                          selectmode=tk.SINGLE)  # Half the width
        self.product_listbox.pack()

        self.product_listbox.bind('<<ListboxSelect>>', self.on_product_select)

        # 获取"Update Stock"的翻译 / Get translation for "Update Stock"
        update_stock_text = "Update Stock"
        if self.translation_controller:
            update_stock_text = self.translation_controller.get_text("views.menu.update_stock",
                                                                     default=update_stock_text)

        # Stock update section
        self.stock_label = tk.Label(self.scrollable_frame, text=update_stock_text, font=("Arial", 16, "bold"))
        self.stock_label.grid(row=2, column=0, pady=10, sticky="w")  # Aligned left

        # 获取"Product Name:"的翻译 / Get translation for "Product Name:"
        product_name_text = "Product Name:"
        if self.translation_controller:
            product_name_text = self.translation_controller.get_text("views.menu.product_name",
                                                                     default=product_name_text)

        self.stock_name_label = tk.Label(self.scrollable_frame, text=product_name_text)
        self.stock_name_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")  # Aligned left

        self.stock_name = tk.Label(self.scrollable_frame, text="", font=("Arial", 12, "bold"))
        self.stock_name.grid(row=3, column=1, padx=5, pady=5, sticky="w")  # Next to label

        # 获取"New Stock Quantity:"的翻译 / Get translation for "New Stock Quantity:"
        new_stock_text = "New Stock Quantity:"
        if self.translation_controller:
            new_stock_text = self.translation_controller.get_text("views.menu.new_stock_quantity",
                                                                  default=new_stock_text)

        self.stock_input_label = tk.Label(self.scrollable_frame, text=new_stock_text)
        self.stock_input_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")  # Aligned left

        self.stock_input = tk.Entry(self.scrollable_frame, width=10)
        self.stock_input.grid(row=4, column=1, padx=5, pady=5, sticky="w")  # Aligned left

        # 获取"Update Stock"按钮的翻译 / Get translation for "Update Stock" button
        update_stock_button_text = "Update Stock"
        if self.translation_controller:
            update_stock_button_text = self.translation_controller.get_text("views.menu.update_stock_button",
                                                                            default=update_stock_button_text)

        self.update_stock_button = tk.Button(self.scrollable_frame, text=update_stock_button_text,
                                             command=self.update_stock)
        self.update_stock_button.grid(row=5, column=1, columnspan=2, pady=10, sticky="w")  # Left-aligned button

        # 获取"Product Price:"的翻译 / Get translation for "Product Price:"
        product_price_text = "Product Price:"
        if self.translation_controller:
            product_price_text = self.translation_controller.get_text("views.menu.product_price",
                                                                      default=product_price_text)

        self.stock_price_label = tk.Label(self.scrollable_frame, text=product_price_text)
        self.stock_price_label.grid(row=6, column=0, padx=5, pady=5, sticky="w")  # Aligned left

        self.stock_price = tk.Label(self.scrollable_frame, text="", font=("Arial", 12, "bold"))
        self.stock_price.grid(row=6, column=1, padx=5, pady=5, sticky="w")  # Next to label

        self.update_stock_ui()
        self.update_categories()

        # 获取"Product Photo:"的翻译 / Get translation for "Product Photo:"
        photo_text = "Product Photo:"
        if self.translation_controller:
            photo_text = self.translation_controller.get_text("views.menu.product_photo", default=photo_text)

        # Product details
        self.photo_label = tk.Label(self.scrollable_frame, text=photo_text)
        self.photo_label.grid(row=7, column=0, pady=10)

        self.photo_display = tk.Label(self.scrollable_frame)
        self.photo_display.grid(row=8, column=0, pady=10)

        # 获取"Description:"的翻译 / Get translation for "Description:"
        description_text = "Description:"
        if self.translation_controller:
            description_text = self.translation_controller.get_text("views.menu.description", default=description_text)

        self.description_label = tk.Label(self.scrollable_frame, text=description_text)
        self.description_label.grid(row=9, column=0, pady=10)

        self.description_text = tk.Label(self.scrollable_frame, text="", wraplength=800,
                                         justify="left")  # Wider description area
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
                # 获取产品名称的翻译 / Get translation for product name
                product_name = item.name
                if self.translation_controller:
                    product_name = self.translation_controller.get_text(f"products.names.{item.id}", default=item.name)
                self.product_listbox.insert(tk.END, product_name)
            elif self.user_controller.get_current_user_role() == "customer":
                if item.stock >= 5:
                    # 获取产品名称的翻译 / Get translation for product name
                    product_name = item.name
                    if self.translation_controller:
                        product_name = self.translation_controller.get_text(f"products.names.{item.id}",
                                                                            default=item.name)
                    self.product_listbox.insert(tk.END, product_name)
            else:
                if item.is_vip == "NO" and item.stock >= 5:
                    # 获取产品名称的翻译 / Get translation for product name
                    product_name = item.name
                    if self.translation_controller:
                        product_name = self.translation_controller.get_text(f"products.names.{item.id}",
                                                                            default=item.name)
                    self.product_listbox.insert(tk.END, product_name)

            # If stock is low, change text color to red
            if item.stock < 5 and self.user_controller.get_current_user_role() == "bartender":
                self.product_listbox.itemconfig(index, {'fg': 'red'})

    def on_product_select(self, event):
        selected_product = self.product_listbox.get(tk.ACTIVE)

        # 如果产品名已被翻译，需要找到原始产品 / If product name is translated, need to find the original product
        product = None

        # 首先尝试通过名称精确匹配 / First try exact match by name
        product = next((item for item in self.controller.model.menu if item.name == selected_product), None)

        # 如果没找到，可能是翻译后的名称，尝试遍历所有产品 / If not found, it might be a translated name, try all products
        if not product and self.translation_controller:
            for item in self.controller.model.menu:
                translated_name = self.translation_controller.get_text(f"products.names.{item.id}", default=item.name)
                if translated_name == selected_product:
                    product = item
                    break

        if product:
            # 显示产品名称 - 使用原始名称 / Display product name - use original name
            self.stock_name.config(text=product.name)
            self.stock_price.config(text=product.price)
            self.stock_input.delete(0, tk.END)
            self.stock_input.insert(0, str(product.stock))

            # 获取产品描述的翻译 / Get translation for product description
            # 首先尝试从翻译文件获取 / First try to get from translation file
            description = product.description.get('en', "No description available")
            if self.translation_controller:
                # 尝试使用翻译控制器获取描述 / Try to get description from translation controller
                translated_desc = self.translation_controller.get_text(f"products.descriptions.{product.id}",
                                                                       default=None)

                # 如果没有找到翻译，使用产品自带的多语言描述 / If no translation found, use product's multilingual description
                if translated_desc:
                    description = translated_desc
                else:
                    # 获取当前语言代码 / Get current language code
                    current_lang = self.translation_controller.get_current_language()
                    # 映射语言代码到产品描述中的语言代码 / Map language code to product description language code
                    lang_map = {"en": "en", "zh": "zh", "sv": "sv"}
                    desc_lang = lang_map.get(current_lang, "en")
                    # 使用对应语言的描述，如果没有则使用英文 / Use description in corresponding language, or English if not available
                    description = product.description.get(desc_lang,
                                                          product.description.get('en', "No description available"))

            self.description_text.config(text=description)

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
            # 获取错误消息的翻译 / Get translation for error message
            error_title = "Invalid Input"
            error_message = "Please enter a valid stock number."

            if self.translation_controller:
                error_title = self.translation_controller.get_text("dialogs.invalid_input", default=error_title)
                error_message = self.translation_controller.get_text("dialogs.please_enter_valid_stock",
                                                                     default=error_message)

            messagebox.showerror(error_title, error_message)
            return

        new_stock = int(new_stock)
        product = next((item for item in self.controller.model.menu if item.name == product_name), None)

        if product:
            if self.controller.update_item_stock(product.id, new_stock):
                # 获取成功消息的翻译 / Get translation for success message
                success_title = "Success"
                success_pattern = "Stock for {product_name} updated to {new_stock}."

                if self.translation_controller:
                    success_title = self.translation_controller.get_text("dialogs.success", default=success_title)
                    success_pattern = self.translation_controller.get_text(
                        "dialogs.stock_update_success",
                        default=success_pattern
                    )

                success_message = success_pattern.format(product_name=product_name, new_stock=new_stock)
                messagebox.showinfo(success_title, success_message)
                self.display_category(product.category)
            else:
                # 获取错误消息的翻译 / Get translation for error message
                error_title = "Error"
                error_message = "Failed to update stock."

                if self.translation_controller:
                    error_title = self.translation_controller.get_text("dialogs.error", default=error_title)
                    error_message = self.translation_controller.get_text("dialogs.stock_update_error",
                                                                         default=error_message)

                messagebox.showerror(error_title, error_message)
        else:
            # 获取错误消息的翻译 / Get translation for error message
            error_title = "Error"
            error_message = "Product not found."

            if self.translation_controller:
                error_title = self.translation_controller.get_text("dialogs.error", default=error_title)
                error_message = self.translation_controller.get_text("dialogs.product_not_found", default=error_message)

            messagebox.showerror(error_title, error_message)

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
            # 获取类别的翻译 / Get translation for category
            category_text = category.capitalize()
            if self.translation_controller:
                category_text = self.translation_controller.get_text(f"categories.{category}", default=category_text)

            btn = tk.Button(self.left_frame, text=category_text, fg="black", font=("Arial", 14), width=25,
                            command=lambda c=category: self.display_category(c))
            btn.grid(row=i, column=0, pady=5)
            self.category_buttons[category] = btn

    def temporarily_remove(self):
        """Temporarily remove a product by setting its stock to 0."""
        product_name = self.stock_name.cget("text")

        if not product_name:
            # 获取错误消息的翻译 / Get translation for error message
            error_title = "Error"
            error_message = "No product selected."

            if self.translation_controller:
                error_title = self.translation_controller.get_text("dialogs.error", default=error_title)
                error_message = self.translation_controller.get_text("dialogs.no_product_selected",
                                                                     default=error_message)

            messagebox.showerror(error_title, error_message)
            return

        # 获取确认对话框的翻译 / Get translation for confirm dialog
        confirm_title = "Confirm Removal"
        confirm_pattern = "Are you sure you want to temporarily remove '{product_name}'?"

        if self.translation_controller:
            confirm_title = self.translation_controller.get_text("dialogs.confirm_removal", default=confirm_title)
            confirm_pattern = self.translation_controller.get_text(
                "dialogs.removal_question",
                default=confirm_pattern
            )

        confirm_message = confirm_pattern.format(product_name=product_name)
        confirm = messagebox.askyesno(confirm_title, confirm_message)
        if not confirm:
            return

        product = next((item for item in self.controller.model.menu if item.name == product_name), None)

        if product:
            if self.controller.update_item_stock(product.id, 0):
                # 获取成功消息的翻译 / Get translation for success message
                success_title = "Success"
                success_pattern = "'{product_name}' has been temporarily removed."

                if self.translation_controller:
                    success_title = self.translation_controller.get_text("dialogs.success", default=success_title)
                    success_pattern = self.translation_controller.get_text(
                        "dialogs.product_removed_success",
                        default=success_pattern
                    )

                success_message = success_pattern.format(product_name=product_name)
                messagebox.showinfo(success_title, success_message)
                self.display_category(product.category)
            else:
                # 获取错误消息的翻译 / Get translation for error message
                error_title = "Error"
                error_message = "Failed to remove product."

                if self.translation_controller:
                    error_title = self.translation_controller.get_text("dialogs.error", default=error_title)
                    error_message = self.translation_controller.get_text("dialogs.stock_update_error",
                                                                         default=error_message)

                messagebox.showerror(error_title, error_message)
        else:
            # 获取错误消息的翻译 / Get translation for error message
            error_title = "Error"
            error_message = "Product not found."

            if self.translation_controller:
                error_title = self.translation_controller.get_text("dialogs.error", default=error_title)
                error_message = self.translation_controller.get_text("dialogs.product_not_found", default=error_message)

            messagebox.showerror(error_title, error_message)

    def update_stock_ui(self):
        """Show stock update section only for bartenders."""
        if self.user_controller.get_current_user_role() == "bartender":
            self.stock_label.grid()
            self.stock_input_label.grid()
            self.stock_input.grid()
            self.update_stock_button.grid()

            # Add Temporarily Remove button next to Update Stock
            if not hasattr(self, "remove_button"):
                # 获取"Temporarily Remove"按钮的翻译 / Get translation for "Temporarily Remove" button
                remove_text = "Temporarily Remove"
                if self.translation_controller:
                    remove_text = self.translation_controller.get_text("views.menu.temporarily_remove",
                                                                       default=remove_text)

                self.remove_button = tk.Button(self.scrollable_frame, text=remove_text, command=self.temporarily_remove,
                                               fg="white", bg="red")
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

    def update_translations(self):
        """更新界面中的所有翻译文本 / Update all translated text in the interface"""
        if not self.translation_controller:
            return

        # 更新类别按钮文本 / Update category button texts
        for category, btn in self.category_buttons.items():
            category_text = self.translation_controller.get_text(f"categories.{category}",
                                                                 default=category.capitalize())
            btn.config(text=category_text)

        # 更新产品列表标签 / Update product list label
        products_text = self.translation_controller.get_text("views.menu.products", default="Products")
        self.product_label.config(text=products_text)

        # 更新库存更新部分 / Update stock update section
        update_stock_text = self.translation_controller.get_text("views.menu.update_stock", default="Update Stock")
        self.stock_label.config(text=update_stock_text)

        product_name_text = self.translation_controller.get_text("views.menu.product_name", default="Product Name:")
        self.stock_name_label.config(text=product_name_text)

        new_stock_text = self.translation_controller.get_text("views.menu.new_stock_quantity",
                                                              default="New Stock Quantity:")
        self.stock_input_label.config(text=new_stock_text)

        update_stock_button_text = self.translation_controller.get_text("views.menu.update_stock_button",
                                                                        default="Update Stock")
        self.update_stock_button.config(text=update_stock_button_text)

        product_price_text = self.translation_controller.get_text("views.menu.product_price", default="Product Price:")
        self.stock_price_label.config(text=product_price_text)

        # 更新产品详情部分 / Update product details section
        photo_text = self.translation_controller.get_text("views.menu.product_photo", default="Product Photo:")
        self.photo_label.config(text=photo_text)

        description_text = self.translation_controller.get_text("views.menu.description", default="Description:")
        self.description_label.config(text=description_text)

        # 更新临时移除按钮 / Update temporarily remove button
        if hasattr(self, "remove_button"):
            remove_text = self.translation_controller.get_text("views.menu.temporarily_remove",
                                                               default="Temporarily Remove")
            self.remove_button.config(text=remove_text)

        # 刷新显示的产品列表 / Refresh displayed product list
        # 获取当前选中的类别 / Get currently selected category
        current_category = None
        for category, btn in self.category_buttons.items():
            if btn.cget("bg") == "lightblue":
                current_category = category
                break

        if current_category:
            self.display_category(current_category)

        # 刷新选中的产品详情 / Refresh selected product details
        if self.stock_name.cget("text"):  # 如果有选中的产品 / If there's a selected product
            # 触发产品选择事件以刷新描述 / Trigger product selection event to refresh description
            # 注意：这里假设当前选中的产品仍在列表中 / Note: This assumes the currently selected product is still in the list
            try:
                self.product_listbox.event_generate("<<ListboxSelect>>")
            except:
                pass  # 如果失败，忽略错误 / If it fails, ignore the error