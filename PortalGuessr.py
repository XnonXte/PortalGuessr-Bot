"""
PortalGussr v0.3-beta Stable Version

Copyright (c) 2023 XnonXte
"""

# todo list is in https://trello.com/b/iQgOc5H1/portalguesser

import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, Literal
import asyncio
import time
import const
import random
from components.guessr import chambers_list
from components.guessr import Guessr, GuessrUsersLeaderboard
from components.buttons import HelpButtonsLink
from components.admin import AdminManager
from os import environ
from dotenv import load_dotenv

load_dotenv(".env")
version = "v0.3-beta"
discord_bot_token = environ.get("BOTTOKEN")
dpy_version = discord.__version__
bot_accent_color = discord.Color.from_rgb(203, 48, 48)
guessr_leaderboard = GuessrUsersLeaderboard(
    "db/leaderboard.json"
)  # If file path doesn't exist it will be created automatically.
admin_manager = AdminManager("db/authorized.json")
is_guessr_running = False

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=";", intents=intents)


@bot.event
async def on_ready():
    # Getting IDs of guild that the bot is in.
    guild_ids = []
    async for guild in bot.fetch_guilds():
        guild_ids.append(guild.id)
    print(
        """
  ___         _        _  ___                
 | _ \___ _ _| |_ __ _| |/ __|_  _ _______ _ 
 |  _/ _ \ '_|  _/ _` | | (_ | || (_-<_-< '_|
 |_| \___/_|  \__\__,_|_|\___|\_,_/__/__/_|  
                                             
"""
    )
    print(f"We have logged in as {bot.user}!")
    print(
        f"The bot is in {len(guild_ids)} guilds | {len(await bot.tree.sync())} application commands have been synced."
    )


@bot.tree.command(description="Shows an overview of the available slash command.")
async def help(interaction: discord.Interaction):
    help_message_embed = discord.Embed(
        title="Help & About",
        description="PortalGuessr is a bot that challenges you to guess a Portal chamber from a random picture taken from various locations, similar to GeoGuessr. Have fun using the bot!",
        color=bot_accent_color,
    )
    help_message_embed.add_field(name="Main Commands", value=const.available_commands)
    help_message_embed.add_field(
        name="Config Commands", value=const.admin_only_commands, inline=False
    )
    help_message_embed.set_footer(
        text=f"PortalGuessr {version} - Developed with 💖 by XnonXte & Contributors.",
        icon_url="attachment://logo.jpg",
    )
    help_message_embed.set_thumbnail(url="attachment://logo.jpg")
    await interaction.response.send_message(
        file=discord.File("logo.jpg", filename="logo.jpg"),
        embed=help_message_embed,
        view=HelpButtonsLink(),
    )


@bot.tree.command(
    description="Returns this bot's latency relative to the user invoking it."
)
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! `{round(bot.latency * 1000)}ms`")


@bot.tree.command(description="Starts a PortalGuessr game.")
@app_commands.describe(difficulty="The difficulty of the game.")
async def guess(
    interaction: discord.Interaction,
    difficulty: Optional[Literal["Easy", "Medium", "Hard"]] = random.choice(
        ["Easy", "Medium", "Hard"]
    ),
):
    global is_guessr_running

    # A check whether the game is already running or not.
    if is_guessr_running:
        await interaction.response.send_message(
            "A PortalGuessr game is already running. Please wait for it to finish.",
            ephemeral=True,
        )
        return

    is_guessr_running = True
    guessr_request = Guessr().get_guess(difficulty)
    guessr_image = guessr_request[0]
    guessr_correct_answer = guessr_request[1]

    # Green for easy difficulty, yellow for medium difficulty, red for hard difficulty.
    difficulty_colors = {
        "Easy": discord.Color.from_rgb(46, 139, 87),
        "Medium": discord.Color.from_rgb(204, 204, 0),
        "Hard": discord.Color.from_rgb(178, 34, 34),
    }
    difficulty_color_accent = difficulty_colors.get(difficulty)
    guessr_embed = discord.Embed(
        title="Which chamber is this?",
        description=f"Difficulty: {difficulty}",
        color=difficulty_color_accent,
    )
    guessr_embed.set_image(url="attachment://embed.jpg")
    guessr_embed.set_footer(
        text="Answer with a valid chamber number to make a guess! Please send a response within the next 20 seconds.",
        icon_url="attachment://logo.jpg",
    )
    local_files = [
        discord.File(guessr_image, filename="embed.jpg"),
        discord.File("logo.jpg", filename="logo.jpg"),
    ]

    # This checks for the channel and the chamber the user is in.
    def is_valid(message: discord.Message):
        return (
            message.channel.id == interaction.channel.id
            and message.content.lower() in chambers_list
        )

    await interaction.response.send_message(
        files=local_files,
        embed=guessr_embed,
    )

    guessr_user_have_answered = []
    guessr_user_count = 0

    # Timeout in 20 seconds if the user hasn't answered correctly.
    start_time = time.time()
    timeout_seconds = 20
    elapsed_time = 0

    try:
        while elapsed_time < timeout_seconds:
            response = await asyncio.wait_for(
                bot.wait_for("message", check=is_valid),
                timeout=timeout_seconds - elapsed_time,
            )

            # Check to make sure the user responding wouldn't be able to answer twice.
            if response.author.id not in guessr_user_have_answered:
                guessr_user_have_answered.append(response.author.id)
                guessr_user_count += 1

                if response.content.lower() == guessr_correct_answer:
                    await response.reply(
                        f"You're correct! Congratulations you earned a point for {difficulty.lower()} difficulty."
                    )

                    # Saving the score into leaderboard logic.
                    guessr_leaderboard.load_stats()
                    guessr_leaderboard.add_user_stats(response.author.id, difficulty)
                    guessr_leaderboard.save_stats()
                    break
            elif response.author.id in guessr_user_have_answered:
                await response.reply("You've already answered this guessr!")

            if guessr_user_count == 5:
                max_guess_embed = discord.Embed(
                    title="Game Over!",
                    description="Good luck next time.",
                    color=discord.Color.from_rgb(237, 237, 237),
                )
                await interaction.followup.send(embed=max_guess_embed)
                break

            # Neccessary timeout logic, here we update elapsed_time everytime the loop iterates through.
            elapsed_time = time.time() - start_time

            # Checking if the timeout has been reached, ultimately ending the game.
            if elapsed_time == timeout_seconds:
                raise TimeoutError
    except TimeoutError:
        timeout_embed = discord.Embed(
            title="Time's up!", color=discord.Color.from_rgb(237, 237, 237)
        )
        await interaction.followup.send(embed=timeout_embed)
    finally:
        is_guessr_running = False


@bot.tree.command(description="Returns the current leaderboard.")
async def leaderboard(interaction: discord.Interaction):
    guessr_leaderboard.load_stats()
    leaderboard = (
        guessr_leaderboard.get_sorted_stats()
    )  # Example of dictionary that will be returned: [('<user_id>', {'Easy': 2, 'Medium': 3, 'Hard': 4})].

    leaderboard_message = ""

    # We use enumerate to get the index of every keys in the dictionary, we start at index 1.
    for index, (user_id, stats) in enumerate(leaderboard, start=1):
        user = await bot.fetch_user(int(user_id))
        leaderboard_message += f"{index}. `{user.name}` has completed "
        stats_entries = []
        for difficulty in stats:
            count = stats.get(difficulty)
            stats_entries.append(f"{count} {difficulty.lower()}")
        leaderboard_message += ", ".join(stats_entries)
        leaderboard_message += f" difficulty Guessr.\n"

    leaderboard_embed = discord.Embed(
        title="Leaderboard", description=leaderboard_message, color=bot_accent_color
    )
    leaderboard_embed.set_footer(
        text=f"{len(leaderboard)} users in the leaderboard.",
        icon_url="attachment://logo.jpg",
    )
    await interaction.response.send_message(
        file=discord.File("logo.jpg", filename="logo.jpg"), embed=leaderboard_embed
    )


@bot.tree.command(description="Returns the stats for a spesific user.")
@app_commands.describe(target_user="The user to get the stats for.")
async def stats_for(interaction: discord.Interaction, target_user: discord.Member):
    guessr_leaderboard.load_stats()
    leaderboard = guessr_leaderboard.get_sorted_stats()

    found = False
    stats_message = ""
    for user_id, stats in leaderboard:
        if target_user.id == int(user_id):
            user = await bot.fetch_user(target_user.id)
            stats_message += f"`{user.name}` has completed "
            user_stats_entries = []
            for difficulty in stats:
                count = stats.get(difficulty)
                user_stats_entries.append(f"{count} {difficulty.lower()}")
            stats_message += ", ".join(user_stats_entries)
            stats_message += f" difficulty Guessr.\n"
            found = True

    if not found:
        await interaction.response.send_message(
            f"The stats for {target_user.name} doesn't exist!",
            ephemeral=True,
        )
        return

    stats_embed = discord.Embed(
        title=f"Stats for {target_user.name}",
        description=stats_message,
        color=bot_accent_color,
    )
    await interaction.response.send_message(embed=stats_embed)


@bot.tree.command(description="Removes a spesific user from the leaderboard.")
@app_commands.describe(target_user="The user to remove from the leaderboard.")
async def remove_stats(interaction: discord.Interaction, target_user: discord.Member):
    admins_list = admin_manager.load_data()
    if str(interaction.user.id) not in admins_list:
        await interaction.response.send_message(
            "You're not authorized to use this command.",
            ephemeral=True,
        )
        return

    try:
        guessr_leaderboard.load_stats()
        guessr_leaderboard.delete_user_stats(target_user.id)
        guessr_leaderboard.save_stats()
        await interaction.response.send_message(
            f"{target_user.name} has been removed from the leaderboard!"
        )
    except KeyError:
        await interaction.response.send_message(
            f"{target_user.name} not found in the leaderboard!", ephemeral=True
        )


@bot.tree.command(description="Authorizes a user.")
@app_commands.describe(target_user="The user to authorize.")
async def authorize(interaction: discord.Interaction, target_user: discord.Member):
    admins_list = admin_manager.load_data()
    if str(interaction.user.id) not in admins_list:
        await interaction.response.send_message(
            "You're not authorized to use this command.",
            ephemeral=True,
        )
        return

    if interaction.user.id == target_user.id:
        await interaction.response.send_message(
            "You can't add yourself as an admin.", ephemeral=True
        )
        return

    try:
        # Loading the JSON file, returns a python dictionary.
        admin_manager.load_data()
        admin_manager.add_admin(target_user.name, target_user.id)

        # Dumping the dictionary we've opened earlier to the JSON file we have.
        admin_manager.save_data()
        await interaction.response.send_message(f"{target_user.name} is now an admin!")
    except KeyError as e:
        print(e)
        await interaction.response.send_message(
            f"{target_user.name} is already an admin!", ephemeral=True
        )


@bot.tree.command(description="Removes authorization for a user.")
@app_commands.describe(target_user="The user to deauthorize.")
async def deauthorize(interaction: discord.Interaction, target_user: discord.Member):
    admins_list = admin_manager.load_data()
    if str(interaction.user.id) not in admins_list:
        await interaction.response.send_message(
            "You're not authorized to use this command.",
            ephemeral=True,
        )
        return

    if interaction.user.id == target_user.id:
        await interaction.response.send_message(
            "You can't add yourself as an admin.", ephemeral=True
        )
        return

    try:
        admin_manager.load_data()
        admin_manager.remove_admin(target_user.id)
        admin_manager.save_data()
        await interaction.response.send_message(
            f"{target_user.name} has been authorized as an admin!"
        )
    except KeyError as e:
        print(e)
        await interaction.response.send_message(
            f"{target_user.name} is not an admin!", ephemeral=True
        )


bot.run(discord_bot_token)
