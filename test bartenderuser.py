import tkinter as tk
from Models.UserModel import UserModel
from Models.TableModel import TableModel
from Controllers.UserController import UserController
from Controllers.TableController import TableController
from Views.BartenderView import BartenderView

if __name__ == "__main__":
    root = tk.Tk()

    # Initialize the models
    user_model = UserModel()
    table_model = TableModel()

    # Initialize the controllers
    user_controller = UserController(user_model)
    table_controller = TableController(table_model)

    # Create BartenderView passing the controllers
    bartender_view = BartenderView(table_controller)

    # Here you could set up a specific bartender test-user if needed, for example:
    test_user = {
        "user_id": 2001,
        "name": "Bartender Bob",
        "role": "bartender",
        "balance": 0
    }

    # Optional: print test user information to console for debugging purposes
    print(f"Logged in as {test_user['name']} with role {test_user['role']}")

    bartender_view.mainloop()
