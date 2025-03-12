import tkinter as tk
from Models.UserModel import UserModel
from Views.MainView import MainView
from Views.CustomerView import CustomerView
from Controllers.UserController import UserController
from Views.LoginView import LoginView

if __name__ == "__main__":
    root = tk.Tk()
    main_view = MainView(root)

    # 初始化 MVC 组件
    user_model = UserModel()
    controller = UserController(user_model)

    # 创建 LoginView
    login_view = LoginView(root, controller, lambda: customer_view.update_ui())

    # 创建 CustomerView，并传递 login_view 作为依赖
    customer_view = CustomerView(main_view.user_area, controller, login_view)
    main_view.set_user_view(customer_view)

    root.mainloop()