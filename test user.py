import tkinter as tk
from Models.UserModel import UserModel
from Models.MenuModel import MenuModel
from Views.MainView import MainView
from Views.CustomerView import CustomerView
from Controllers.UserController import UserController
from Controllers.MenuController import MenuController
from Views.LoginView import LoginView, RegisterView, TableChoice

if __name__ == "__main__":
    root = tk.Tk()

    #Initialize the correct models
    user_model = UserModel()
    menu_model = MenuModel()  #Now using MenuModel, not UserModel!

    #Initialize the controllers
    user_controller = UserController(user_model)
    menu_controller = MenuController(menu_model)  #Pass MenuModel

    #Pass both controllers to MainView
    main_view = MainView(root, user_controller, menu_controller)

    #Create LoginView
    login_view = LoginView(root, user_controller, lambda: customer_view.update_ui())
    register_view = RegisterView(root, user_controller)
    table_choice_view = TableChoice(root, None)

    #Create CustomerView
    customer_view = CustomerView(main_view.user_area, user_controller, login_view, register_view, table_choice_view)
    main_view.set_user_view(customer_view)

    root.mainloop()
