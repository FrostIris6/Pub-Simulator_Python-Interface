#for table view + expanding with order when pressing a table
import tkinter as tk
from tkinter import messagebox, ttk
from Controllers.TableController import TableController

# for table view + expanding with order when pressing a table
import tkinter as tk
from tkinter import messagebox, ttk
from Controllers.TableController import TableController


class BartenderView(tk.Frame):
    """MVC View for managing tables and visually displaying their statuses."""

    def __init__(self, parent, controller: TableController, translation_controller=None):
        super().__init__(parent)
        self.controller = controller
        self.translation_controller = translation_controller  # 存储翻译控制器 / Store translation controller
        self.configure(bg="#F7F9FC")

        # Main frame covering the entire view
        self.main_frame = tk.Frame(self, bg="#F7F9FC")
        self.main_frame.pack(fill="both", expand=True)

        # Top fixed frame containing the legend
        self.top_frame = tk.Frame(self.main_frame, bg="#F7F9FC", height=50)
        self.top_frame.pack(fill="x", side="top")

        # Bottom frame that holds the canvas for tables and bar
        self.bottom_frame = tk.Frame(self.main_frame, bg="#FFFFFF")
        self.bottom_frame.pack(fill="both", expand=True)

        # Canvas frame for tables and bar visuals
        self.canvas_frame = tk.Frame(self.bottom_frame, bg="white")
        self.canvas_frame.pack(expand=True, fill="both")

        # Canvas for drawing tables and bar
        self.canvas = tk.Canvas(self.canvas_frame, bg="white")
        self.canvas.pack(expand=True, fill="both")

        # 存储状态标签的引用，用于更新翻译 / Store status label references for translation updates
        self.status_labels = []

        # Initialize the interface components
        self.create_legend()
        self.draw_tables()
        self.draw_bar()

    def create_legend(self):
        """Creates a legend explaining table status colors."""
        legend = tk.Frame(self.top_frame, bg="#F7F9FC")
        legend.pack(pady=10, anchor="w", padx=15)

        statuses = [("free", "#E3F2FD"), ("vip", "#FFD700"), ("occupied", "#90CAF9"), ("bar", "#607D8B")]

        # 清除之前的状态标签 / Clear previous status labels
        self.status_labels.clear()

        for status_key, color in statuses:
            tk.Label(legend, bg=color, width=2, height=1).pack(side="left", padx=5)

            # 初始显示文本，稍后在update_translations中更新 / Initial display text, will be updated in update_translations
            label_text = status_key.capitalize()
            if self.translation_controller:
                label_text = self.translation_controller.get_text(f"views.bartender.table_status.{status_key}",
                                                                  default=label_text)

            label = tk.Label(legend, text=label_text, bg="#F7F9FC")
            label.pack(side="left", padx=10)

            # 存储状态标签和对应的键，用于更新翻译 / Store status labels and their keys for translation updates
            self.status_labels.append((status_key, label))

    def draw_tables(self):
        """Fetches tables from the controller and visually represents them on the canvas."""
        self.canvas.delete("all")
        tables = self.controller.model.tables

        # Define positions for each table visually
        positions = [(150, 120), (350, 120),
                     (150, 280), (350, 280),
                     (150, 440), (350, 440)]

        # Iterate over tables and their positions to draw them
        for table, position in zip(tables, positions):
            # Select color based on table status
            color = "#E3F2FD" if table.status == "free" else "#FFD700" if table.status == "VIP" else "#90CAF9"

            # 获取表状态的翻译 / Get translation for table status
            status_text = table.status
            if self.translation_controller:
                status_key = table.status.lower()
                status_text = self.translation_controller.get_text(f"views.bartender.table_status.{status_key}",
                                                                   default=status_text)

            # 获取"Table"的翻译 / Get translation for "Table"
            table_text = "Table"
            if self.translation_controller:
                table_text = self.translation_controller.get_text("views.bartender.table_text", default=table_text)

            # Draw table rectangle and status
            x, y = position
            rect = self.canvas.create_rectangle(x - 50, y - 30, x + 50, y + 30, fill=color,
                                                tags=f"table_{table.table_id}")
            self.canvas.create_text(x, y, text=f"{table_text} {table.table_id}\n{status_text}")

    def draw_bar(self):
        """Draws a visual representation of the bar area."""
        self.canvas.create_rectangle(650, 100, 750, 600, fill="#607D8B")

        # 获取"BAR"的翻译 / Get translation for "BAR"
        bar_text = "BAR"
        if self.translation_controller:
            bar_text = self.translation_controller.get_text("views.bartender.table_status.bar", default=bar_text)

        self.canvas.create_text(700, 350, text=bar_text, fill="white", font=("Arial", 20, "bold"))

    def show_table_orders(self, table):
        """Opens a popup window to display orders and allow status changes for a specific table."""
        popup = tk.Toplevel(self)

        # 获取"Table X Details"的翻译 / Get translation for "Table X Details"
        title_text = f"Table {table.table_id} Details"
        if self.translation_controller:
            title_pattern = self.translation_controller.get_text("views.bartender.table_details",
                                                                 default="Table {table_id} Details")
            title_text = title_pattern.format(table_id=table.table_id)

        popup.title(title_text)
        popup.geometry("300x200")

        # 获取"Table X Status: Y"的翻译 / Get translation for "Table X Status: Y"
        status_text = f"Table {table.table_id} Status: {table.status}"
        if self.translation_controller:
            status_pattern = self.translation_controller.get_text(
                "views.bartender.table_status_text",
                default="Table {table_id} Status: {status}"
            )

            # 获取状态翻译 / Get translation for status
            status_key = table.status.lower()
            status_translation = self.translation_controller.get_text(
                f"views.bartender.table_status.{status_key}",
                default=table.status
            )

            status_text = status_pattern.format(table_id=table.table_id, status=status_translation)

        tk.Label(popup, text=status_text).pack(pady=10)

        status_var = tk.StringVar(value=table.status)

        # 获取状态选项的翻译 / Get translations for status options
        status_options_keys = ["free", "vip", "occupied"]
        status_options = status_options_keys.copy()

        if self.translation_controller:
            status_options = [
                self.translation_controller.get_text(f"views.bartender.table_status.{key}", default=key)
                for key in status_options_keys
            ]

        status_menu = ttk.Combobox(popup, textvariable=status_var, values=status_options)
        status_menu.pack(pady=10)

        # 获取"Update Status"按钮的翻译 / Get translation for "Update Status" button
        update_button_text = "Update Status"
        if self.translation_controller:
            update_button_text = self.translation_controller.get_text("views.bartender.update_status",
                                                                      default=update_button_text)

        update_button = tk.Button(
            popup,
            text=update_button_text,
            command=lambda: self.update_status(table.table_id, status_var.get(), popup)
        )
        update_button.pack(pady=10)

    def update_status(self, table_id, new_status, popup):
        """Updates the table's status through the controller and refreshes the canvas."""
        table = self.controller.model.get_table_by_id(table_id)

        # 如果选择了翻译后的状态，需要映射回原始值 / If translated status was selected, map back to original value
        if self.translation_controller:
            # 尝试找到对应的原始状态键 / Try to find the corresponding original status key
            status_keys = ["free", "vip", "occupied"]
            for key in status_keys:
                translated = self.translation_controller.get_text(f"views.bartender.table_status.{key}", default=key)
                if translated == new_status:
                    new_status = key
                    break

        table.status = new_status
        self.controller.model.update_table(table)
        self.draw_tables()
        popup.destroy()

        # 获取成功消息的翻译 / Get translation for success message
        message = f"Table {table_id} status updated to {new_status}."
        if self.translation_controller:
            message_pattern = self.translation_controller.get_text(
                "dialogs.table_status_update",
                default="Table {table_id} status updated to {new_status}."
            )

            # 获取状态翻译 / Get translation for status
            status_key = new_status.lower()
            status_translation = self.translation_controller.get_text(
                f"views.bartender.table_status.{status_key}",
                default=new_status
            )

            message = message_pattern.format(table_id=table_id, new_status=status_translation)

        # 获取"Update"对话框标题的翻译 / Get translation for "Update" dialog title
        update_title = "Update"
        if self.translation_controller:
            update_title = self.translation_controller.get_text("dialogs.update", default=update_title)

        messagebox.showinfo(update_title, message)

    def update_translations(self):
        """更新界面中的所有翻译文本 / Update all translated text in the interface"""
        if not self.translation_controller:
            return

        # 更新图例中的状态标签 / Update status labels in the legend
        for status_key, label in self.status_labels:
            translated_text = self.translation_controller.get_text(f"views.bartender.table_status.{status_key}")
            label.config(text=translated_text)

        # 重绘表格和吧台区域以应用新的翻译 / Redraw tables and bar area to apply new translations
        self.draw_tables()
        self.draw_bar()

