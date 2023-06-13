import os
import random

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


def guesser():
    random_chamber_dir = random.choice(chambers_list)

    image_path = f"images/{random_chamber_dir}"
    image_files = [
        file for file in os.listdir(image_path)
    ]  # Creates a list of images for the random file path.

    random_image_index = random.randint(
        0, len(image_files) - 1
    )  # Gets a random image index.
    random_image_path = os.path.join(
        image_path, image_files[random_image_index]
    )  # Gets the path for the random image.

    return random_image_path, random_chamber_dir
