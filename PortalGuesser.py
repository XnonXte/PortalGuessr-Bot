import discord
from discord.ext import commands
import asyncio
from os import environ
from dotenv import load_dotenv
from Modules import components, contents

bot_version = "v0.1-beta"
load_dotenv(".env")
token = environ["TOKEN"]

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"We've logged in as {bot.user}!")


@bot.slash_command(description="Returns a list of available commands.")
async def help(ctx):
    help_message_embed = discord.Embed(
        title="Help & About",
        description="Created with 💖 by XnonXte & Contributions.",
        color=discord.Color.from_rgb(50, 100, 255),
    )
    help_message_embed.add_field(
        name="Available slash commands", value=contents.slash_commands
    )
    help_message_embed.set_footer(
        text=f"PortalGuesser {bot_version} | The bot is currently on its development phase, expect some instability.",
        icon_url="attachment://logo.png",
    )
    help_message_embed.set_thumbnail(url="attachment://logo.png")

    await ctx.respond(
        file=discord.File("local/logo.png", filename="logo.png"),
        embed=help_message_embed,
    )


@bot.slash_command(description="Returns the GitHub page for this bot.")
async def github(ctx):
    await ctx.respond("It's coming soon :)")


@bot.slash_command(description="Starts a Portalguesser game.")
async def guess(
    ctx,
):
    guessr_request = components.guesser()
    guessr_image = guessr_request[0]
    guessr_correct_answer = guessr_request[1]
    guessr_embed = discord.Embed(
        title="Guess the Chamber!",
        description="Difficulty: -",
        color=discord.Color.from_rgb(50, 100, 255),
    )
    guessr_embed.set_image(url="attachment://embed.jpg")
    guessr_embed.set_footer(text="Answer with a Chamber number (e.g. 01, 04, e00).")

    def is_valid_response(message: discord.Message):
        return (
            message.author.id == ctx.author.id
            and message.channel.id == ctx.channel.id
            and message.content.lower() in components.chambers_list
        )

    try:
        await ctx.respond(
            ctx.user.mention,
            file=discord.File(guessr_image, filename="embed.jpg"),
            embed=guessr_embed,
        )
    except:
        # If the bot can't send an interaction response for some reason (e.g. slow internet connection).
        await ctx.send(
            ctx.user.mention,
            file=discord.File(guessr_image, filename="embed.jpg"),
            embed=guessr_embed,
        )

    try:
        response = await bot.wait_for("message", check=is_valid_response, timeout=30)
    except asyncio.TimeoutError:
        await ctx.send("Time is up!")

    if response.content.lower() == guessr_correct_answer:
        await ctx.send("You're correct!")
    else:
        await ctx.send("Oops that was incorrect, good luck next time!")


bot.run(token)
