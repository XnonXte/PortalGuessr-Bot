import json


class AdminManager:
    def __init__(self, filepath):
        self.filepath = filepath
        self.data = {}

    def load_data(self):
        """Loads the data from a specifed JSON file path"""
        with open(self.filepath, "r") as file:
            self.data = json.load(file)
            return self.data

    def save_data(self):
        """Saves the data to a specifed JSON file path"""
        with open(self.filepath, "w") as file:
            json.dump(self.data, file, indent=4)

    def add_admin(self, username, user_id):
        """Adds an admin to the data"""
        for key in self.data:
            if str(user_id) == key:
                raise KeyError(f"There's already a key with the name {username}")

        self.data[str(user_id)] = username

    def remove_admin(self, user_id):
        """Removes an admin from the data"""
        found = False
        for key in self.data:
            if str(user_id) == key:
                del self.data[key]
                found = True
                break
        if not found:
            raise KeyError(f"Key was not found with the name {user_id}")
