import discord
import os
import random
import const


def guesser(difficulty):
    random_chamber = random.choice(const.chambers_list)

    image_path = f"Resources\images\{difficulty}\{random_chamber}"
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


class HelpComponents(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(
            discord.ui.Button(
                style=discord.ButtonStyle.link,
                label="Discord",
                url="https://discord.gg/hHYfnqa6zS",
            )
        )
        self.add_item(
            discord.ui.Button(
                style=discord.ButtonStyle.link,
                label="GitHub",
                url="https://github.com/XnonXte/PortalGuessr",
            )
        )
