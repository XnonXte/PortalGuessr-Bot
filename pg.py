# PortalGuessr v0.2.1-beta - 2023 (c) XnonXte
# Using py-cord v2.4.1

# The todo list is on https://trello.com/b/iQgOc5H1/portalguesser
# todo rewrite the bot to use vannila discord.py using hybrid command.

import discord
from discord.ext import bridge
import random
import asyncio
from components import variables
from components.guessr import Guessr, GuessrLeaderboard
from components.buttons import HelpButtonsLink
from components.admin import AuthManager
from os import environ
from dotenv import load_dotenv

load_dotenv(".env")

version = "v0.2.1-beta"
token = environ["DEVTOKEN"]
py_cord_version = discord.__version__
bot_accent_color = discord.Color.from_rgb(203, 48, 48)

intents = discord.Intents.default()
intents.message_content = True

bot = bridge.Bot(
    command_prefix=";",
    debug_guilds=[1103578001318346812],
    intents=intents,
    help_command=None,
)

is_guessr_running = False
guessr_leaderboard = GuessrLeaderboard("resources/local/leaderboard.json")
auth_manager = AuthManager("resources/local/authorized.json")


@bot.event
async def on_ready():
    print(
        f"We have logged in as {bot.user} (ID: {bot.user.id}) - py-cord {py_cord_version}"
    )


@bot.bridge_command(description="Shows an overview of the available slash command.")
async def help(ctx: bridge.BridgeContext):
    """Help & About the bot."""
    help_message_embed = discord.Embed(
        title="Help & About",
        description="A bot about guessing a Portal chamber from a random picture taken from every spots imaginable, much like [GeoGuessr](https://www.geoguessr.com/), thus the name PortalGuessr.\n\nAll of my commands are invoked either by using the built-in slash command or `;` prefix. Have fun using the bot!",
        color=bot_accent_color,
    )
    help_message_embed.add_field(name="Commands", value=variables.available_commands)
    help_message_embed.add_field(
        name="Admin Commands", value=variables.admin_only_commands, inline=False
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


@bot.bridge_command(
    description="Returns this bot's latency relative to the user invoking it."
)
async def ping(ctx: bridge.BridgeContext):
    """Returns the bot's ping relative to the user invoking it."""
    await ctx.respond(f"Pong! `{round(bot.latency * 1000)}ms`")


@bot.bridge_command(description="Starts a Portalguesser game.")
async def guess(ctx: bridge.BridgeContext):
    global is_guessr_running

    # A check whether the game is already running or not.
    if is_guessr_running:
        await ctx.respond(
            "A PortalGuessr game is already running. Please wait for it to finish.",
            ephemeral=True,
        )
        return
    else:
        is_guessr_running = True

    difficulty_choices = ("Easy", "Medium", "Hard")
    difficulty = random.choice(difficulty_choices)

    # Green for easy difficulty, yellow for medium difficulty, and red for hard difficulty.
    difficulty_colors = {
        "Easy": (46, 139, 87),
        "Medium": (204, 204, 0),
        "Hard": (178, 34, 34),
    }

    red, green, blue = difficulty_colors.get(difficulty)
    guessr_request = Guessr(difficulty).get_guess()
    guessr_image = guessr_request[0]
    guessr_correct_answer = guessr_request[1]
    guessr_user_have_answered = []
    guessr_user_count = 0
    guessr_embed = discord.Embed(
        title="Which chamber is this?",
        description=f"Difficulty: {difficulty}",
        color=discord.Color.from_rgb(red, green, blue),
    )
    guessr_embed.set_image(url="attachment://embed.jpg")
    guessr_embed.set_footer(
        text="Answer with a valid chamber number to make a guess! (e.g. 02, 04, e01).",
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
            and message.content.lower() in variables.chambers_list
        )

    try:
        await ctx.respond(
            files=local_files,
            embed=guessr_embed,
        )
    except discord.errors.HTTPException:
        # If the bot can't send an interaction response with the user (e.g. slow internet connection).
        await ctx.send(
            files=local_files,
            embed=guessr_embed,
        )

    try:

        async def guessr_timeout():
            # 30 seconds timeout if anyone hasn't gotten the question right.
            await asyncio.sleep(30)
            timeout_embed = discord.Embed(title="Time's up!", color=bot_accent_color)
            await ctx.send(embed=timeout_embed)

        timeout_task = asyncio.create_task(guessr_timeout())
        guessr_game_running = True

        while guessr_game_running:
            response = await bot.wait_for("message", check=is_valid)
            # A check to see if the user has already answered this guessr.
            if response.author.id not in guessr_user_have_answered:
                guessr_user_have_answered.append(response.author.id)
                guessr_user_count += (
                    1  # Increment guess_count by 1 each time a user guesses.
                )
            elif response.author.id in guessr_user_have_answered:
                await response.reply("You've already answered this guessr!")
            if response.content.lower() == guessr_correct_answer:
                await response.reply(
                    f"You're correct! It was {guessr_correct_answer}, congratulations you earned a point."
                )
                scores = variables.difficulty_scores.get(difficulty)
                guessr_leaderboard.add_score(response.author.id, scores)
                guessr_leaderboard.save()
                timeout_task.cancel()
                guessr_game_running = False
            elif guessr_user_count == 5:
                # If the response has been invoked 5 times, the game is over.
                max_guess_embed = discord.Embed(
                    title="Exceeded the maximum time to guess! Good luck next time.",
                    color=bot_accent_color,
                )
                await ctx.send(embed=max_guess_embed)
                timeout_task.cancel()
                guessr_game_running = False
    except asyncio.CancelledError:
        pass
    finally:
        is_guessr_running = False


@bot.bridge_command(description="Returns the current leaderboard.")
async def leaderboard(ctx: bridge.BridgeContext):
    guessr_leaderboard.load()
    guessr_leaderboard_data = guessr_leaderboard.get_sorted_leaderboard()
    leaderboard = []

    for index, (user_id, score) in enumerate(guessr_leaderboard_data, start=1):
        user = bot.get_user(int(user_id))
        leaderboard.append(f"{index}. {user.name}: {score}")

    leaderboard_message = "\n".join(guessr_leaderboard_data)
    leaderboard_embed = discord.Embed(
        title="Leaderboard",
        description=leaderboard_message,
        color=discord.Color.from_rgb(0, 162, 255),
    )
    leaderboard_embed.set_footer(text=f"{index} users() in the leaderboard.")
    await ctx.respond(embed=leaderboard_embed)


@bot.bridge_command(description="Upload a picture of a chamber.")
async def upload(
    ctx: bridge.BridgeContext,
    attachment: discord.SlashCommandOptionType.attachment,
    difficulty: discord.Option(
        choices=["Easy", "Medium", "Hard"], description="Choose a difficulty."
    ),
    chamber: discord.Option(
        choices=variables.chambers_list, description="Choose a chamber."
    ),
):
    authorized_users = auth_manager.data.get("authorized", [])
    if ctx.author.id not in authorized_users:
        await ctx.respond(
            "You are not authorized to use this command.",
            ephemeral=True,
        )
        return

    if not attachment.filename.lower().endswith(".jpg", ".png", ".jpeg", ".gif"):
        await ctx.respond("Invalid file type.", ephemeral=True)
        return

    image_filename = attachment.filename

    try:
        await attachment.save(
            f"resources/images/{difficulty}/{chamber}/{image_filename}"
        )
        await ctx.respond(f"Image saved as {image_filename}")
    except Exception as e:
        await ctx.respond(
            f"An error occurred while uploading the picture.", e, ephemeral=True
        )


@bot.bridge_command(description="Authorizes a user.")
async def authorize(ctx, user: discord.SlashCommandOptionType.user):
    # For now the user invokes this command must be the bot owner, you can override it if you want to use the command.
    if ctx.author.id != 706330866267193344:
        await ctx.respond("You don't have permission to use this command.")
        return

    # Loading authorized users list.
    authorized_users = auth_manager.data.get("authorized", [])

    # Checking if the user is already authorized.
    for target_user in authorized_users:
        if user in target_user:
            await ctx.respond(f"User '{user}' is already authorized.")
            return

    auth_manager.add_authorized_user(user, user.id)
    auth_manager.save_data()
    await ctx.respond(f"User '{user}' with ID '{user.id}' has been authorized.")


@bot.bridge_command(description="Removes authorization for a user.")
async def deauthorize(ctx, user: discord.SlashCommandOptionType.user):
    if ctx.author.id != 706330866267193344:
        await ctx.respond("You don't have permission to use this command.")
        return

    authorized_users = auth_manager.data.get("authorized", [])
    found = False

    # Same as before but for removing the user from the authorized list.
    for target_user in authorized_users:
        if user in target_user:
            auth_manager.remove_authorized_user(user)
            auth_manager.save_data()
            await ctx.respond(f"Authorization has been removed for user '{user}'.")
            found = True
            break
    # If the user is not found or is not authorized.
    if not found:
        await ctx.respond(f"User '{user}' not found or is not authorized.")


bot.run(token)
