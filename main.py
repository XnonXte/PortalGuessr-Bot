"""
Root file for PortalGuesser bot.

(C) 2023 - XnonXte & Contributors
"""

import discord
from discord.ext import bridge, commands
import asyncio
from dotenv import load_dotenv
from os import getenv
from PGModules import PGComponents
import random
import const

version = "v0.2-beta"
prefix = ";"
load_dotenv(".env")
token = getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = bridge.Bot(
    command_prefix=commands.when_mentioned_or(prefix),
    debug_guilds=[1103578001318346812],
    intents=intents,
)


@bot.event
async def on_ready():
    print(f"We've logged in as {bot.user}!")


@bot.bridge_command(description="Shows an overview of the available slash command.")
async def support(ctx: bridge.BridgeExtContext):
    """Help & About PortalGuessr."""
    help_message_embed = discord.Embed(
        title="Help & About",
        description=f"A bot about guessing a Portal chamber from a random picture taken from every spots imaginable, much like [GeoGuessr](https://www.geoguessr.com/), thus the name PortalGuessr.\n\nAll of my commands are invoked either by using the built-in slash command or `{prefix}` prefix. Have fun using the bot!",
        color=discord.Color.from_rgb(
            0,
            162,
            255,
        ),
    )
    help_message_embed.add_field(name="Commands", value=const.main_commands)
    help_message_embed.add_field(
        name="Misc Commands", value=const.misc_commands, inline=False
    )
    help_message_embed.set_footer(
        text=f"PortalGuessr {version} - Developed with 💖 by XnonXte & Contributors.",
        icon_url="attachment://logo.jpg",
    )
    help_message_embed.set_thumbnail(url="attachment://logo.jpg")

    await ctx.respond(
        file=discord.File("logo.jpg", filename="logo.jpg"),
        embed=help_message_embed,
        view=PGComponents.HelpComponents(),
    )


@bot.bridge_command(description="Sends the GitHub page for this bot.")
async def github(ctx: bridge.BridgeExtContext):
    await ctx.respond("https://github.com/XnonXte/PortalGuessr")


@bot.bridge_command(
    description="Returns this bot's latency relative to the user invoking it."
)
async def ping(ctx: bridge.BridgeExtContext):
    """Returns the bot's ping relative to the user invoking it."""
    await ctx.respond(f"Pong! My ping is {round(bot.latency * 100, 2)}ms.")


@bot.bridge_command(description="Starts a Portalguesser game.")
async def guess(ctx: bridge.BridgeExtContext):
    """Prompts a randomized image and then waiting for the user to response. Soon to be legacy command."""
    difficulty_choices = ("Easy", "Medium", "Hard")
    difficulty = random.choice(difficulty_choices)

    # Green for easy difficulty, yellow for medium difficulty, and red for hard difficulty.
    if difficulty == "Easy":
        red = 46
        green = 139
        blue = 87
    elif difficulty == "Medium":
        red = 204
        green = 204
        blue = 0
    elif difficulty == "Hard":
        red = 178
        green = 34
        blue = 34

    guessr_request = PGComponents.guesser(difficulty)
    guessr_image = guessr_request[0]
    guessr_correct_answer = guessr_request[1]
    guessr_embed = discord.Embed(
        title="Which chamber is this?",
        description=f"Difficulty: {difficulty}",
        color=discord.Color.from_rgb(r=red, g=green, b=blue),
    )
    guessr_embed.set_image(url="attachment://embed.jpg")
    guessr_embed.set_footer(
        text="Please send your response within the next 30 seconds."
    )

    def is_valid_response(message: discord.Message):
        # This checks for 3 things at once, I won't go into detail since they are pretty obvious.
        return (
            message.author.id == ctx.author.id
            and message.channel.id == ctx.channel.id
            and message.content.lower() in const.chambers_list
        )

    try:
        await ctx.respond(
            f"Make a guess! {ctx.author.mention}",
            file=discord.File(guessr_image, filename="embed.jpg"),
            embed=guessr_embed,
        )
    except:
        # If the bot can't send an interaction response for some reason (e.g. slow internet connection).
        await ctx.send(
            f"Make a guess! {ctx.author.mention}",
            file=discord.File(guessr_image, filename="embed.jpg"),
            embed=guessr_embed,
        )

    try:
        response = await bot.wait_for("message", check=is_valid_response, timeout=30)

        if response.content.lower() == guessr_correct_answer:
            await ctx.send("You're correct!")
        else:
            await ctx.send("Oops that was incorrect, try again.")
    except asyncio.TimeoutError:
        timeout_embed = discord.Embed(
            title="Time is up!", color=discord.Color.from_rgb(237, 237, 237)
        )
        await ctx.send(embed=timeout_embed)
    except Exception as e:
        print(e)


bot.run(token)
