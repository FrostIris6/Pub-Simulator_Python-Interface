#declare user object id, name, email, category(type of user) etc.
# users - id(system),name, password,type_of_user(customer or bartender),balance,method
# function - login; logout; show_balance; register; type_of_user_ident;
# Hao

import json
import os
import time
import random
import re

USER_FILE = os.path.join(os.path.dirname(__file__), "D:/Pycharm/Pub-Simulator_Python-Interface/Database/UsersDB.json")
USER_FILE = os.path.abspath(USER_FILE)  # absolute route

# if os.path.exists(USER_FILE):
#     print(f"✅ UsersDB.json found at: {os.path.abspath(USER_FILE)}")
# else:
#     print("❌ UsersDB.json NOT found! Check the path.")


class UserList:
    def __init__(self, name, password, type_of_user, balance=0.0, method="", user_id=None):
        self.id = user_id  # id given by system
        self.name = name  # username whether customerize or random given
        self.password = password  # password set by customers
        self.type_of_user = type_of_user  #  customer or bartender
        self.balance = balance  # account balance
        self.method = method  # register method（email/phone/bankID）

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "password": self.password,
            "type_of_user": self.type_of_user,
            "balance": self.balance,
            "method": self.method
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            password=data["password"],
            type_of_user=data["type_of_user"],
            balance=data.get("balance", 0.0),
            method=data.get("method", ""),
            user_id=data["id"]
        )


class UserModel:
    def __init__(self):
        self.users = []
        self.load_users()
        self.failed_attempts = {}  # remember times of wrong password

    def load_users(self):
        #print("Loading users from database...")
        if os.path.exists(USER_FILE):
            with open(USER_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                #print("Loaded data from JSON:", data)  # print data from json
                self.users = [UserList.from_dict(user) for user in data]
                #print("Converted users:", [user.to_dict() for user in self.users])  # readble
        else:
            print("User database file not found!")
            self.users = []

    def save_users(self):
        #update user data to database
        with open(USER_FILE, "w", encoding="utf-8") as f:
            json.dump([user.to_dict() for user in self.users], f, indent=4)

    def login(self, identifier, password):
        #login -- fail over 5 times lock the account
        #identifier can be:1.id(set by system) 2.username 3.other login method(mail/phone/bankid)

        if identifier in self.failed_attempts and self.failed_attempts[identifier] >= 5:
            #prevent locked users still trying
            print("Failed over five times, locked account. Please call the bartender.")
            return None

        for user in self.users:
            #print(f"Checking user: {user.to_dict()}")  # user data
            #print(f"Identifier provided: {identifier}")

            if str(user.id) == identifier or user.name == identifier or user.method == identifier:
                print("User matched!")
                if user.password == password:
                    print(f"Login successfully! Welcome {user.name}！")
                    self.failed_attempts[identifier] = 0  # reset fail counter
                    return user
                else:
                    self.failed_attempts[identifier] = self.failed_attempts.get(identifier, 0) + 1
                    print(f"Password wrong, the chance to try again：{5 - self.failed_attempts[identifier]}")
                    if self.failed_attempts[identifier] >= 5:
                        print("Failed over five times, locked account. Please call the bartender.")
                    return None
        print("User doesn't exist ！")
        return None

    def show_balance(self, user):
        #show balance -- in later development can use different way to show
        print(f"your balance：{user.balance} ")

    def register(self, name, password, type_of_user, method):
        #give a button for regular customer to register
        new_id = random.randint(1000, 9999)
        while any(user.id == new_id for user in self.users):
            #make sure id is not an existing one
            new_id = random.randint(1000, 9999)

        # check username format: only letters, numbers,spaces are allowed
        if not name or not re.fullmatch(r"[A-Za-z0-9 ]{3,20}", name):
            print("Invalid username! Using your ID as username.")
            name = str(new_id)  # if not or skipped, use id instead.

        # register method must be mail or phone
        if not method or not re.fullmatch(r"(\w+@\w+\.\w+|\d{10,15})", method):
            print("Invalid method! Using your ID as method.")
            method = str(new_id)  # if not or skipped, use id instead.

        new_user = UserList(name, password, type_of_user, method=method, user_id=new_id)
        self.users.append(new_user)
        self.save_users()
        print(f"Register successfully！Your user ID is {new_id}")
        return new_user

    def type_of_user_ident(self, user):
        # customer and bartender login will go to different related page
        if user.type_of_user.lower() == "customer":
            print("Go to menu page...")
            # if customer, go back to menu page
            self.show_balance(user)
            #show account balance for VIP users
        elif user.type_of_user.lower() == "bartender":
            print("Go to bartender management page...")
            # if bartender, go to management page
        else:
            print("Unknown user type！")

    def logout(self, user):
        #logout function
        print(f"{user.name} Logout successfully! Account balance {user.balance} is storied.")
        self.save_users()
        return None
