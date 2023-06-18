import json


class AuthManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = self.load_data()

    def load_data(self):
        try:
            with open(self.file_path, "r") as file:
                data = json.load(file)
            return data
        except FileNotFoundError:
            return {}

    def save_data(self):
        with open(self.file_path, "w") as file:
            json.dump(self.data, file, indent=4)

    def add_authorized_user(self, username, user_id):
        if "authorized" not in self.data:
            self.data["authorized"] = []
        self.data["authorized"].append({username: user_id})

    def remove_authorized_user(self, username):
        if "authorized" in self.data:
            self.data["authorized"] = [
                user for user in self.data["authorized"] if username not in user
            ]
