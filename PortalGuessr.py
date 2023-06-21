"""
PortalGussr v0.3.1-beta Stable Version

Copyright (c) 2023 XnonXte
"""

# todo list is in https://trello.com/b/iQgOc5H1/portalguesser

import discord
from discord import app_commands
from discord.ext import commands
from typing import Literal
import random
import asyncio
import time
import const
from components.guessr import Guessr, GuessrUsersStatistics
from components.buttons import HelpButtonsLink
from components.keep_alive import keep_alive
from os import environ
from dotenv import load_dotenv


load_dotenv(".env")
discord_bot_token = environ.get("BOTTOKEN")

portalguessr_version = "v0.3.1-beta"
bot_accent_color = discord.Color.from_rgb(203, 48, 48)
guessr_statistics = GuessrUsersStatistics("db/statistics.json")
is_guessr_running = False

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=";", intents=intents)


@bot.event
async def on_ready():
    print(
        """
  ___         _        _  ___                
 | _ \___ _ _| |_ __ _| |/ __|_  _ _______ _ 
 |  _/ _ \ '_|  _/ _` | | (_ | || (_-<_-< '_|
 |_| \___/_|  \__\__,_|_|\___|\_,_/__/__/_|  
                                             
"""
    )
    print(
        f"We have logged in as {bot.user}! We are in {len(bot.guilds)} guild(s) | discord.py {discord.__version__}"
    )
    try:
        synced = await bot.tree.sync()
        print(f"Successfully synced {len(synced)} command(s).")
    except Exception as e:
        print(e)

    # Set the activity of the bot, showing how many servers the bot is in.
    await bot.change_presence(
        activity=discord.Game(name=f"In {len(bot.guilds)} servers!")
    )


@bot.tree.command(description="Shows an overview of the available slash command.")
async def help(interaction: discord.Interaction):
    help_message_embed = discord.Embed(
        title="Help & About",
        description="PortalGuessr is a bot that challenges you to guess a Portal chamber from a random picture taken from various locations, similar to GeoGuessr. Have fun using the bot!",
        color=bot_accent_color,
    )
    help_message_embed.add_field(name="Main Commands", value=const.main_commands)
    help_message_embed.add_field(
        name="Config Commands", value=const.config_commands, inline=False
    )
    help_message_embed.set_footer(
        text=f"PortalGuessr {portalguessr_version} - Developed with 💖 by XnonXte & Contributors.",
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
@app_commands.describe(
    difficulty="Select the desired difficulty of the game (blank for random)."
)
async def guess(
    interaction: discord.Interaction,
    difficulty: Literal["Easy", "Medium", "Hard", "Random"],
):
    global is_guessr_running

    # A check whether the game is already running or not.
    if is_guessr_running:
        await interaction.response.send_message(
            "A PortalGuessr game is already running. Please wait for it to finish.",
            ephemeral=True,
        )
        return
    else:
        is_guessr_running = True

    if difficulty == "Random":
        difficulty = random.choice(["Easy", "Medium", "Hard"])

    guessr_request = Guessr().get_guess(difficulty)
    guessr_image = guessr_request[0]
    guessr_correct_answer = guessr_request[1]
    guessr_color_accent = guessr_request[2]
    guessr_timeout = guessr_request[3]
    guessr_embed = discord.Embed(
        title="Which chamber is this?",
        description=f"Difficulty: {difficulty}",
        color=guessr_color_accent,
    )
    guessr_embed.set_image(url="attachment://embed.jpg")
    guessr_embed.set_footer(
        text=f"Answer with a valid chamber number to make a guess! Please send a response within the next {guessr_timeout} seconds.",
        icon_url="attachment://logo.jpg",
    )
    local_files = [
        discord.File(guessr_image, filename="embed.jpg"),
        discord.File("logo.jpg", filename="logo.jpg"),
    ]

    # This checks for the same channel and valid chamber for the response message.
    def is_valid(message: discord.Message):
        return (
            message.channel.id == interaction.channel.id
            and message.content.lower() in Guessr.chambers_list
        )

    # We use response.defer() to prevent the bot from returning an unknown interaction since the message needs to be sent in under 3 seconds without deferring.
    # We will see this through the bot.
    await interaction.response.defer(thinking=True)
    await interaction.followup.send(
        files=local_files,
        embed=guessr_embed,
    )

    guessr_user_have_answered = []
    guessr_user_count = 0
    guessr_max_count = 5

    # 20, 25, or 30 seconds timeout if the user hasn't answered correctly.
    start_time = time.time()
    timeout_seconds = guessr_timeout
    elapsed_time = 0

    while elapsed_time < timeout_seconds:
        try:
            response = await bot.wait_for(
                "message", check=is_valid, timeout=timeout_seconds - elapsed_time
            )
        except asyncio.TimeoutError:
            timeout_embed = discord.Embed(
                title="Time's up!", color=discord.Color.from_rgb(237, 237, 237)
            )
            await interaction.followup.send(embed=timeout_embed)
            break

        # Check to make sure the user responding wouldn't be able to answer twice.
        if response.author.id not in guessr_user_have_answered:
            guessr_user_have_answered.append(response.author.id)
            guessr_user_count += 1

            if response.content.lower() == guessr_correct_answer:
                await response.reply(
                    f"You're correct! Congratulations you earned a point for {difficulty.lower()} difficulty."
                )

                # Saving the score into leaderboard logic.
                guessr_statistics.load_stats()
                guessr_statistics.add_user_stats(
                    interaction.guild.id, response.author.id, difficulty
                )
                guessr_statistics.save_stats()
                break
            elif guessr_user_count == guessr_max_count:
                max_guess_embed = discord.Embed(
                    title="Game Over!",
                    color=discord.Color.from_rgb(237, 237, 237),
                )
                await interaction.followup.send(embed=max_guess_embed)
                break
        else:
            await response.reply("You've already answered this guessr!")

        # Update elapsed time everytime the loop iterates through.
        elapsed_time = time.time() - start_time

    # Ending the game.
    is_guessr_running = False


@bot.tree.command(description="Returns the current statistics.")
async def stats(interaction: discord.Interaction):
    guessr_statistics.load_stats()

    try:
        # Example of dictionary that will be returned: [('706330866267193344', {'Easy': 3, 'Medium': 0, 'Hard': 0})]
        statistics = guessr_statistics.get_sorted_stats(interaction.guild.id)
    except KeyError:
        await interaction.response.send_message(
            f"The statistics for {interaction.guild.name} is empty!",
            ephemeral=True,
        )
        return

    statistics_message = ""
    for index, (user_id, stats) in enumerate(statistics, start=1):
        user = await bot.fetch_user(int(user_id))
        statistics_message += f"{index}. `{user.name}` has completed "
        stats_entries = []
        for difficulty in stats:
            count = stats.get(difficulty)
            stats_entries.append(f"{count} {difficulty.lower()}")
        statistics_message += ", ".join(stats_entries)
        statistics_message += f" difficulty Guessr.\n"

    statistics_embed = discord.Embed(
        title=f"{interaction.guild.name} Statistics",
        description=statistics_message,
        color=bot_accent_color,
    )
    statistics_embed.set_footer(
        text=f"{len(statistics)} users in the statistics.",
        icon_url="attachment://logo.jpg",
    )
    await interaction.response.defer()
    await interaction.followup.send(
        file=discord.File("logo.jpg", filename="logo.jpg"),
        embed=statistics_embed,
    )


@bot.tree.command(description="Returns the statistics for a spesific user.")
@app_commands.describe(target_user="The user to get the statistics for.")
async def stats_for(interaction: discord.Interaction, target_user: discord.Member):
    guessr_statistics.load_stats()

    try:
        user_stats = guessr_statistics.get_user_stats(
            interaction.guild.id, target_user.id
        )
    except KeyError:
        await interaction.response.send_message(
            f"The stats for {target_user.name} in {interaction.guild.name} not found!",
            ephemeral=True,
        )
        return

    stats_message = f'`{target_user.name}` has completed {user_stats["Easy"]} easy, {user_stats["Medium"]} medium, and {user_stats["Hard"]} hard difficulty Guessr.'
    stats_embed = discord.Embed(
        title=f"Statistics for {target_user.name} in {interaction.guild.name}",
        description=stats_message,
        color=bot_accent_color,
    )
    await interaction.response.send_message(embed=stats_embed)


@bot.tree.command(description="Removes a spesific user from the statistics.")
@app_commands.describe(target_user="The user to remove from the statistics.")
@app_commands.checks.has_permissions(manage_guild=True)
async def remove_stats(interaction: discord.Interaction, target_user: discord.Member):
    try:
        guessr_statistics.load_stats()
        guessr_statistics.delete_user_stats(interaction.guild.id, target_user.id)
        guessr_statistics.save_stats()
        await interaction.response.send_message(
            f"{target_user.name} has been removed from the statistics!"
        )
    except KeyError:
        await interaction.response.send_message(
            f"{target_user.name} not found in the statistics!", ephemeral=True
        )


# todo make a command to upload an image directly to the bot, possibly using os module.
# todo this should be as simple as possible.

# @bot.tree.command(description="Upload an image directly to the bot.")
# @app_commands.describe(image="The image to upload.")
# async def upload_image(interaction: discord.Interaction, image: discord.File):
#     raise NotImplementedError


@bot.tree.error  # Catch any errors inside bot.tree aka slash commands.
async def on_app_command_error(
    interaction: discord.Interaction, error: discord.app_commands.AppCommandError
):
    if isinstance(error, discord.app_commands.MissingPermissions):
        await interaction.response.send_message(
            f"You don't have permission to use this command!",
            ephemeral=True,
        )
    else:
        raise error


keep_alive()
bot.run(discord_bot_token)
