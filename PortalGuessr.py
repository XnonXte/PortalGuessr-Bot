"""
PortalGussr v0.2.2.1-Beta Stable Version

Copyright (c) 2023 XnonXte
"""

# This bot is currently using py-cord with commands for ease of use.
# todo rewrite the bot to use discord.py, and possibly with hybrid commands.

import discord
from discord.ext import commands
import time
import asyncio
import random
from Components.guessr import chambers_list
from Components.guessr import Guessr, GuessrUsersLeaderboard
from Components.buttons import HelpButtonsLink
from Components.admin import AdminManager
import const
from os import environ
from dotenv import load_dotenv

load_dotenv(".env")

version = "v0.2.2.1-beta"
token = environ["BOTTOKEN"]

py_cord_version = discord.__version__
bot_accent_color = discord.Color.from_rgb(203, 48, 48)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(
    intents=intents, help_command=None
)  # Here we disable the help command because we have our own help command on line 50.

is_guessr_running = False
guessr_leaderboard = GuessrUsersLeaderboard(
    "Database/leaderboard.json"
)  # If filepath doesn't exist, it will create a new one.
admin_manager = AdminManager("Database/authorized.json")


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user} | Running on py-cord {py_cord_version}")


@bot.slash_command(description="Shows an overview of the available slash command.")
async def help(ctx: commands.Context):
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
    await ctx.respond(
        file=discord.File("logo.jpg", filename="logo.jpg"),
        embed=help_message_embed,
        view=HelpButtonsLink(),
    )


@bot.slash_command(
    description="Returns this bot's latency relative to the user invoking it."
)
async def ping(ctx: commands.Context):
    await ctx.respond(f"Pong! `{round(bot.latency * 1000)}ms`")


@bot.slash_command(description="Starts a PortalGuessr game.")
async def guess(
    ctx: commands.Context,
    difficulty: discord.Option(
        choices=["Easy", "Medium", "Hard"],
        description="Choose a difficulty (leave blank for random difficulty).",
        required=False,
    ) = random.choice(["Easy", "Medium", "Hard"]),
):
    global is_guessr_running

    # A check whether the game is already running or not.
    if is_guessr_running:
        await ctx.respond(
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
            message.channel.id == ctx.channel.id
            and message.content.lower() in chambers_list
        )

    try:
        await ctx.respond(
            files=local_files,
            embed=guessr_embed,
        )
    # If the bot can't send an interaction response with the user (e.g. slow internet connection).
    except discord.errors.HTTPException:
        await ctx.send(
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
                await ctx.send(embed=max_guess_embed)
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
        await ctx.send(embed=timeout_embed)
    finally:
        is_guessr_running = False


@bot.slash_command(description="Returns the current leaderboard.")
async def leaderboard(ctx: commands.Context):
    guessr_leaderboard.load_stats()
    leaderboard = (
        guessr_leaderboard.get_sorted_stats()
    )  # Example of dictionary that will be returned: [('<user_id>', {'Easy': 2, 'Medium': 3, 'Hard': 4})].

    leaderboard_message = ""

    # We use enumerate to get the index of every keys in the dictionary, we start at index 1.
    for index, (user_id, stats) in enumerate(leaderboard, start=1):
        user = await bot.get_or_fetch_user(int(user_id))
        leaderboard_message += f"{index}. `{user.display_name or user.name}` has completed "  # use user.name if user.display_name doesn't exist.
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
    await ctx.respond(
        file=discord.File("logo.jpg", filename="logo.jpg"), embed=leaderboard_embed
    )


@bot.slash_command(description="Returns the stats for a spesific user.")
async def stats_for(
    ctx: commands.Context, target_user: discord.SlashCommandOptionType.user
):
    guessr_leaderboard.load_stats()
    leaderboard = guessr_leaderboard.get_sorted_stats()

    found = False
    stats_message = ""
    for user_id, stats in leaderboard:
        if target_user.id == int(user_id):
            user = await bot.get_or_fetch_user(target_user.id)
            stats_message += f"`{user.display_name or user.name}` has completed "
            user_stats_entries = []
            for difficulty in stats:
                count = stats.get(difficulty)
                user_stats_entries.append(f"{count} {difficulty.lower()}")
            stats_message += ", ".join(user_stats_entries)
            stats_message += f" difficulty Guessr.\n"
            found = True

    if not found:
        await ctx.respond(
            f"The stats for {target_user.display_name or target_user.name} doesn't exist!",
            ephemeral=True,
        )
        return

    stats_embed = discord.Embed(
        title=f"Stats for {target_user.display_name}",
        description=stats_message,
        color=bot_accent_color,
    )

    await ctx.respond(embed=stats_embed)


@bot.slash_command(description="Removes a spesific user from the leaderboard.")
async def remove_stats(
    ctx: commands.Context, target_user: discord.SlashCommandOptionType.user
):
    admins_list = admin_manager.load_data()
    if str(ctx.author.id) not in admins_list:
        await ctx.respond(
            "You're not an admin, you can't remove users from the leaderboard.",
            ephemeral=True,
        )
        return

    try:
        guessr_leaderboard.load_stats()
        guessr_leaderboard.delete_user_stats(target_user.id)
        guessr_leaderboard.save_stats()
        await ctx.respond(
            f"{target_user.display_name or target_user.name} has been removed from the leaderboard!"
        )
    except KeyError as e:
        await ctx.respond(e, ephemeral=True)


@bot.slash_command(description="Authorizes a user.")
async def authorize(
    ctx: commands.Context, target_user: discord.SlashCommandOptionType.user
):
    admins_list = admin_manager.load_data()
    if str(ctx.author.id) not in admins_list:
        await ctx.respond(
            "You're not an admin, you can't remove users from the leaderboard.",
            ephemeral=True,
        )
        return

    if ctx.author.id == target_user.id:
        await ctx.respond("You can't add yourself as an admin.", ephemeral=True)
        return

    try:
        # Loading the JSON file, returns a python dictionary.
        admin_manager.load_data()
        admin_manager.add_admin(target_user.name, target_user.id)

        # Dumping the dictionary we've opened earlier to the JSON file we have.
        admin_manager.save_data()
        await ctx.respond(f"{target_user.name} is now an admin!")
    except KeyError as e:
        print(e)
        await ctx.respond(f"{target_user.name} is already an admin!", ephemeral=True)


@bot.slash_command(description="Removes authorization for a user.")
async def deauthorize(
    ctx: commands.Context, target_user: discord.SlashCommandOptionType.user
):
    admins_list = admin_manager.load_data()
    if str(ctx.author.id) not in admins_list:
        await ctx.respond(
            "You're not an admin, you can't remove users from the leaderboard.",
            ephemeral=True,
        )
        return

    if ctx.author.id == target_user.id:
        await ctx.respond("You can't add yourself as an admin.", ephemeral=True)
        return

    try:
        admin_manager.load_data()
        admin_manager.remove_admin(target_user.id)
        admin_manager.save_data()
        await ctx.respond(f"{target_user.name} has been authorized as an admin!")
    except KeyError as e:
        print(e)
        await ctx.respond(f"{target_user.name} is not an admin!", ephemeral=True)


# Running the bot.
bot.run(token)
