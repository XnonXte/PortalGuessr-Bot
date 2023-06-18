import os
import random
import json
from typing import Any
from components import variables


class Guessr:
    def __init__(self, difficulty):
        self.difficulty = difficulty

    def get_guess(self):
        random_chamber = random.choice(variables.chambers_list)

        image_path = f"resources\images\{self.difficulty}\{random_chamber}"
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


class GuessrLeaderboard:
    def __init__(self, filename):
        self.filename = filename
        self.leaderboard = {}

    def load(self):
        with open(self.filename, "r") as file:
            self.leaderboard = json.load(file)

    def save(self):
        with open(self.filename, "w") as file:
            json.dump(self.leaderboard, file)

    def add_score(self, user_id, score):
        if user_id not in self.leaderboard:
            self.leaderboard[user_id] = score
        else:
            self.leaderboard[user_id] += score

    def get_sorted_leaderboard(self):
        sorted_leaderboard = sorted(
            self.leaderboard.items(), key=lambda x: x[1], reverse=True
        )
        return sorted_leaderboard
