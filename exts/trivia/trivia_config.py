"""
Cog for config related commands.

Copyright (c) 2023 XnonXte
"""

import asyncio
import requests
import datetime
from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands

from modules import const, trivia

trivia_leaderboard = trivia.TriviaLeaderboard("database/leaderboard.json")


class Config(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(description="Removes a spesific user from the leaderboard")
    @commands.has_permissions(manage_guild=True)
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.describe(target_user="The user to remove from the leaderboard")
    async def remove(self, ctx: commands.Context, target_user: discord.Member):
        try:
            trivia_leaderboard.load_leaderboard()
            trivia_leaderboard.delete_user_leaderboard(ctx.guild.id, target_user.id)
            trivia_leaderboard.save_leaderboard()
            await ctx.send(f"{target_user.name} has been removed from the leaderboard!")
        except KeyError:
            await ctx.send(
                f"{target_user.name} not found in the leaderboard!", ephemeral=True
            )

    @commands.hybrid_command(description="Clear the server leaderboard.")
    @commands.has_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def clear(self, ctx: commands.Context):
        await ctx.send(
            f"Are you sure to delete the stats for `{ctx.guild.name}`? Please type the server name to continue!"
        )

        def is_valid_user(message: discord.Message):
            return (
                message.channel.id == ctx.channel.id
                and message.author.id == ctx.user.id
            )

        try:
            response = await self.bot.wait_for(
                "message", check=is_valid_user, timeout=30
            )
        except asyncio.TimeoutError:
            await ctx.send("You've exceeded the timeout! Please try the command again.")
        else:
            if response.content == ctx.guild.name:
                try:
                    trivia_leaderboard.load_leaderboard()
                    trivia_leaderboard.delete_server_leaderboard(ctx.guild.id)
                    trivia_leaderboard.save_leaderboard()
                    await ctx.send(
                        f"Successfully removed {ctx.guild.name} from the leaderboard!"
                    )
                except KeyError:
                    await ctx.send(f"{ctx.guild.name} not found in the leaderboard!")
            else:
                await ctx.send("Not quite!")

    @commands.hybrid_command(description="Uploads a chamber image directly to the bot")
    @app_commands.describe(
        image="Image to upload",
        difficulty="The expected difficulty to guess this image",
        chamber="Enter the correct chamber",
    )
    async def submit(
        self,
        ctx: commands.Context,
        image: discord.Attachment,
        difficulty: Literal["Easy", "Medium", "Hard", "Very Hard"],
        chamber: Literal[
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
        ],
    ):
        image_filename = image.filename

        if not image_filename.endswith((".jpg", "jpeg", "png")):
            await ctx.send("Invalid file extension!", ephemeral=True)
            return

        file_extension = (
            image_filename[-4:]
            if image_filename.endswith((".jpg", ".png"))
            else image_filename[-5:]
        )
        image_uploaded_filename = f"{difficulty}-{chamber}-{str(datetime.datetime.now().strftime('%Y-%m-%d %H.%M.%S'))}{file_extension}"
        get_image = requests.get(image.url)

        try:
            with open(f"images/user_chambers/{image_uploaded_filename}", "wb") as f:
                f.write(get_image.content)
        except Exception as e:
            await ctx.send(f"An error occured: {e}")
        else:
            upload_embed = discord.Embed(
                title=f"Successfully submitted {image_filename}!",
                color=const.BOT_COLOR,
            )
            upload_embed.set_image(url=image.url)
            upload_embed.set_footer(
                icon_url="attachment://logo.jpg",
                text="Your image needs to be reviewed by the developer before it gets added into the database.",
            )
            await ctx.send(
                file=discord.File("logo.jpg", filename="logo.jpg"), embed=upload_embed
            )


async def setup(bot):
    await bot.add_cog(Config(bot))
