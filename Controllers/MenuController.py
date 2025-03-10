#actions for filtering by Cocktail, Food, Snack, Beer etc. when pressing the button -- also conditions for user
#show by category, update stock, notification for low stock, fridge category, remove product from menu, see availability,

class MenuController:
    def __init__(self, model):
        self.model = model

    def update_item_stock(self, item_id, new_stock):
        success = self.model.update_stock(item_id, new_stock)
        return success

    def search_items_by_name(self, name):
        return self.model.get_item_by_name(name)

    def get_items_by_category(self, category):
        # Show all items in the selected category without filtering by VIP status
        return [item for item in self.model.menu if item.category.lower() == category.lower()]


    def get_vip_items(self):
        return self.model.get_vip_items()

    def get_item_by_id(self, item_id):
        return self.model.get_item_by_id(item_id)
