import tkinter as tk
from Models.UserModel import UserModel
from Views.MainView import MainView
from Views.CustomerView import CustomerView
from Controllers.UserController import UserController
from Views.LoginView import LoginView
from Views.LoginView import RegisterView
from Views.LoginView import TableChoice

if __name__ == "__main__":
    root = tk.Tk()
    main_view = MainView(root)

    # Initialize MVC components
    user_model = UserModel()
    controller = UserController(user_model)

    # Create LoginView
    login_view = LoginView(root, controller, lambda: customer_view.update_ui())
    register_view = RegisterView(root, controller)
    table_choice_view = TableChoice(root, None)

    # Create CustomerView and pass login_view as a dependency
    customer_view = CustomerView(main_view.user_area, controller, login_view, register_view, table_choice_view)
    main_view.set_user_view(customer_view)

    root.mainloop()
