import json


class AdminManager:
    """Class to manage the admin data, including adding and removing admins. Filepath is the path to the JSON file, if it didn't exist it will be created automatically."""

    def __init__(self, filepath):
        self.filepath = filepath
        self.data = {}

    def load_data(self):
        """Loads the data from a specifed JSON file path"""
        try:
            with open(self.filepath, "r") as file:
                self.data = json.load(file)
                return self.data
        except FileNotFoundError:
            with open(self.filepath, "x") as file:
                self.data = {
                    "706330866267193344": "xnonxte"
                }  # My user_id and username on discord as the default value for data, change it with yours if you want to use the command yourself
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
