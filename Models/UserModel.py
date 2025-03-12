# Declare user object: id, name, email, category (type of user), etc.
# Users - id (system-generated), name, password, type_of_user (customer or bartender), balance, method
# Functions - login; logout; show_balance; register; type_of_user_ident;
# Hao

import json
import os
import time
import random
import re

USER_FILE = os.path.join(os.path.dirname(__file__), "Database", "UsersDB.json")
USER_FILE = os.path.abspath(USER_FILE)  # absolute route

# if os.path.exists(USER_FILE):
#     print(f"✅ UsersDB.json found at: {os.path.abspath(USER_FILE)}")
# else:
#     print("❌ UsersDB.json NOT found! Check the path.")


class UserList:
    def __init__(self, name, password, type_of_user, balance=0.0, method="", user_id=None):
        self.id = user_id  # ID assigned by the system
        self.name = name  # Username, either customized or randomly assigned
        self.password = password  # Password set by the user
        self.type_of_user = type_of_user  # Either customer or bartender
        self.balance = balance  # Account balance
        self.method = method  # Registration method (email/phone/bank ID)

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
        self.failed_attempts = {}  # Track failed password attempts

    def load_users(self):
        # print("Loading users from database...")
        if os.path.exists(USER_FILE):
            with open(USER_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # print("Loaded data from JSON:", data)  # Print data from JSON file
                self.users = [UserList.from_dict(user) for user in data]
                # print("Converted users:", [user.to_dict() for user in self.users])  # Readable output
        else:
            print("User database file not found!")
            self.users = []

    def save_users(self):
        # Update user data to the database
        with open(USER_FILE, "w", encoding="utf-8") as f:
            json.dump([user.to_dict() for user in self.users], f, indent=4)

    def login(self, identifier, password):
        if identifier in self.failed_attempts and self.failed_attempts[identifier] >= 5:
            return "locked"  # Account locked

        for user in self.users:
            if str(user.id) == identifier or user.name == identifier or user.method == identifier:
                if user.password == password:
                    self.failed_attempts[identifier] = 0  # Reset failed attempts on successful login
                    return user  # Return the User object
                else:
                    self.failed_attempts[identifier] = self.failed_attempts.get(identifier, 0) + 1
                    remaining_attempts = 5 - self.failed_attempts[identifier]
                    return f"wrong_password:{remaining_attempts}" if remaining_attempts > 0 else "locked"

        return "not_found"  # Account does not exist

    def show_balance(self, user):
        # Show balance - in future versions, different display methods can be used
        print(f"Your balance: {user.balance} ")

    def register(self, name, password, type_of_user, method):
        # Provide a registration option for regular customers
        new_id = random.randint(1000, 9999)
        while any(user.id == new_id for user in self.users):
            # Ensure the ID is unique
            new_id = random.randint(1000, 9999)

        # Check username format: only letters, numbers, and spaces are allowed
        if not name or not re.fullmatch(r"[A-Za-z0-9 ]{3,20}", name):
            print("Invalid username! Using your ID as the username.")
            name = str(new_id)  # If invalid, use ID instead.

        # Registration method must be email or phone number
        if not method or not re.fullmatch(r"(\w+@\w+\.\w+|\d{10,15})", method):
            print("Invalid method! Using your ID as the method.")
            method = str(new_id)  # If invalid, use ID instead.

        new_user = UserList(name, password, type_of_user, method=method, user_id=new_id)
        self.users.append(new_user)
        self.save_users()
        print(f"Registration successful! Your user ID is {new_id}")
        return new_user

    def type_of_user_ident(self, user):
        # Customers and bartenders will be redirected to different pages upon login
        if user.type_of_user.lower() == "customer":
            print("Redirecting to the menu page...")
            # If the user is a customer, show the menu page
            self.show_balance(user)
            # Display account balance for VIP users
        elif user.type_of_user.lower() == "bartender":
            print("Redirecting to the bartender management page...")
            # If the user is a bartender, redirect to the management page
        else:
            print("Unknown user type!")

    def logout(self, user):
        # Logout function
        print(f"{user.name} logged out successfully! Account balance {user.balance} has been saved.")
        self.save_users()
        return None
