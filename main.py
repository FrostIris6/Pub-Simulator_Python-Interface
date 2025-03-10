#for the main logic of the project

from Models.MenuModel import MenuModel, MenuItem
from Controllers.MenuController import MenuController
from Views.MenuView import MenuView

if __name__ == "__main__":
    model = MenuModel()
    controller = MenuController(model)
    view = MenuView(controller)
    view.mainloop()
