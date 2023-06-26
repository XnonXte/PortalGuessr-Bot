import os
import random
import json
import discord


chambers_list = [
    "01",
    "02",
    "03",
    "04",
    "05",
    "06",
    "07",
    "08",
    "09",
    "10",
    "11",
    "12",
    "13",
    "14",
    "15",
    "16",
    "17",
    "18",
    "19",
    "e00",
    "e01",
    "e02",
]


class Guessr:
    def __init__(self):
        self.difficulty_colors = {
            "Easy": discord.Color.from_rgb(46, 139, 87),
            "Medium": discord.Color.from_rgb(204, 204, 0),
            "Hard": discord.Color.from_rgb(178, 34, 34),
            "Very Hard": discord.Color.from_rgb(255, 0, 0),
        }
        self.difficulty_timeouts = {
            "Easy": 20,
            "Medium": 25,
            "Hard": 30,
            "Very Hard": 35,
        }

    def get_guess(self, difficulty):
        """Get a guessr question."""
        random_chamber = random.choice(chambers_list)
        difficulty_color = self.difficulty_colors.get(difficulty)
        difficulty_timeout = self.difficulty_timeouts.get(difficulty)
        image_path = f"images/chambers/{difficulty}/{random_chamber}"
        image_files = os.listdir(image_path)
        random_index = random.randint(0, len(image_files) - 1)
        random_path = os.path.join(
            image_path, image_files[random_index]
        )  # Gets the path for the random image.

        return (
            random_path,
            random_chamber,
            difficulty_color,
            difficulty_timeout,
        )


class GuessrUsersStatistics:
    """Class to handle the users' statistics. If filename doesn't exist, it will create it automatically."""

    def __init__(self, filepath):
        self.filepath = filepath
        self.stats = {}

    def load_stats(self):
        """Load the users' stats from the statistics."""
        try:
            with open(self.filepath, "r") as file:
                self.stats = json.load(file)
                return self.stats
        except FileNotFoundError:
            with open(self.filepath, "x") as file:
                self.stats = {}
                return self.stats

    def save_stats(self):
        """Save the users' stats to the statistics."""
        with open(self.filepath, "w") as file:
            json.dump(self.stats, file)

    def add_user_stats(self, server_id, user_id, difficulty):
        """Add a user's stats to the statistics."""
        server_id = str(server_id)
        user_id = str(user_id)
        if server_id not in self.stats:
            self.stats[server_id] = {}
        if user_id not in self.stats[server_id]:
            self.stats[server_id][user_id] = {
                "Easy": 0,
                "Medium": 0,
                "Hard": 0,
                "Very Hard": 0,
            }
        self.stats[server_id][user_id][difficulty] += 1

    def get_sorted_stats(self, server_id):
        """Returns a sorted list of users' stats in descending order"""
        server_id = str(server_id)
        if server_id not in self.stats:
            raise KeyError("Server not found in statistics.")
        sorted_statistics = sorted(
            self.stats[server_id].items(),
            key=lambda x: sum(x[1].values()),
            reverse=True,
        )
        return sorted_statistics

    def get_user_stats(self, server_id, user_id):
        """Returns a user's stats"""
        server_id = str(server_id)
        user_id = str(user_id)
        if server_id not in self.stats:
            raise KeyError("Server not found in statistics.")
        if user_id not in self.stats[server_id]:
            raise KeyError("User not found in statistics.")
        return self.stats[server_id][user_id]

    def delete_user_stats(self, server_id, user_id):
        """Delete a user's stats from the statistics"""
        server_id = str(server_id)
        user_id = str(user_id)
        if server_id not in self.stats:
            raise KeyError("Server not found in statistics.")
        elif user_id not in self.stats[server_id]:
            raise KeyError("User not found in statistics.")
        del self.stats[server_id][user_id]

    def delete_server_stats(self, server_id):
        server_id = str(server_id)
        if server_id not in self.stats:
            raise KeyError("Server not found in statistics!")
        del self.stats[server_id]
