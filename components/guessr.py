import os
import random
import json

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
    def get_guess(self, difficulty):
        """Get a guessr question."""
        random_chamber = random.choice(chambers_list)

        image_path = f"resources/images/{difficulty}/{random_chamber}"
        image_files = [
            file for file in os.listdir(image_path)
        ]  # Creates a list of images for the random file path.

        random_image_index = random.randint(
            0, len(image_files) - 1
        )  # Gets a random image index.
        random_image_path = os.path.join(
            image_path, image_files[random_image_index]
        )  # Gets the path for the random image.

        return random_image_path, random_chamber


class GuessrUsersLeaderboard:
    """Class to handle the users' leaderboard. If filename doesn't exist, it will create it automatically."""

    def __init__(self, filepath):
        self.filepath = filepath
        self.stats = {}

    def load_stats(self):
        """Load the users' stats from the leaderboard."""
        try:
            with open(self.filepath, "r") as file:
                self.stats = json.load(file)
                return self.stats
        except FileNotFoundError:
            with open(self.filepath, "x") as file:
                self.stats = {}
                return self.stats

    def save_stats(self):
        """Save the users' stats to the leaderboard."""
        with open(self.filepath, "w") as file:
            json.dump(self.stats, file)

    def add_user_stats(self, user_id, difficulty):
        """Add a user's stats to the leaderboard."""
        if str(user_id) not in self.stats:
            self.stats[str(user_id)] = {"Easy": 0, "Medium": 0, "Hard": 0}

        self.stats[str(user_id)][difficulty] += 1

    def get_sorted_stats(self):
        """Returns a sorted list of users' stats in descending order"""
        return sorted(
            self.stats.items(), key=lambda x: sum(x[1].values()), reverse=True
        )

    def delete_user_stats(self, user_id):
        """Delete a user's stats from the leaderboard"""
        key_to_remove = None
        for key in self.stats:
            if str(user_id) == key:
                key_to_remove = key

        if key_to_remove:
            del self.stats[key_to_remove]
        else:
            raise KeyError("User not found in leaderboard.")
