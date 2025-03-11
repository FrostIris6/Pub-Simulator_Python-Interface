#For food or beverage object id, name, price, stock, image(?) etc.
#Robert

import json
import os

MENU_FILE = "database/MenuDB.json"

class MenuItem:
    
    def __init__(self, name, price, stock, description, is_vip, category, image="", item_id=None):
        self.id = item_id  # keep existing ID from database
        self.name = name # do a dictionary for the db
        self.price = price
        self.stock = stock
        self.description = description
        self.is_vip = is_vip
        self.category = category  #Food, Wine, Cocktail etc.
        self.image = image  

    def to_dict(self):
        #Convert object to dictionary for JSON storage
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "stock": self.stock,
            "description": self.description,
            "is_vip": self.is_vip,
            "category": self.category,
            "image": self.image
        }

    @classmethod
    def from_dict(cls, data):
        #Create a MenuItem from a dictionary
        return cls(
            name=data["name"],
            price=data["price"],
            stock=data["stock"],
            description=data["description"],
            is_vip=data["is_vip"],
            category=data["category"],
            image=data.get("image", ""),
            item_id=data["id"]
        )


class MenuModel:
    #Handles loading menu items and updating stock

    def __init__(self):
        self.menu = []
        self.load_menu()

    def load_menu(self):
        #Load menu from a single JSON file
        try:
            if os.path.exists(MENU_FILE):
                with open(MENU_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.menu = [MenuItem.from_dict(item) for item in data]
            else:
                self.menu = []
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading menu: {e}")
            self.menu = []

    def update_stock(self, item_id, new_stock):
        #Update stock of a specific menu item
        for item in self.menu:
            if item.id == item_id:
                item.stock = new_stock
                self.save_menu()
                return True
        return False

    def save_menu(self):
        #Save updated stock values back to the JSON file
        with open(MENU_FILE, "w", encoding="utf-8") as f:
            json.dump([item.to_dict() for item in self.menu], f, indent=4)

    def get_items_by_category(self, category, is_vip):
        #Retrieve all items in a specific category
        return [item for item in self.menu if (item.category.lower() == category.lower() and item.is_vip.lower() == is_vip.lower())]

    def get_item_by_id(self, item_id):
        #Retrieve a single item by its ID
        return next((item for item in self.menu if item.id == item_id), None)
    
    def get_item_by_name(self, name):
        return [item for item in self.menu if name.lower() in item.name.lower()]

    def get_vip_items(self):
        return [item for item in self.menu if item.is_vip.lower() == "yes"]