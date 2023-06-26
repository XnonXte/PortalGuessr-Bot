"""
Cog for config related commands.

Copyright (c) 2023 XnonXte
"""

import discord
from discord import app_commands
from discord.ext import commands
from components import guessing, const
import requests
from typing import Literal
import asyncio
import datetime
import pytz

timezone = pytz.timezone("Asia/Jakarta")
datetime_now = datetime.datetime.now(timezone)
guessr_statistics = guessing.GuessrUsersStatistics("db\statistics.json")


class Config(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(description="Removes user from the statistics.")
    @app_commands.describe(target_user="The user to remove from the statistics.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def clear_user_stats(
        self, interaction: discord.Interaction, target_user: discord.Member
    ):
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

    @app_commands.command(description="Clear the statistics (destructive command).")
    @app_commands.checks.has_permissions(administrator=True)
    async def clear_stats(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Are you sure to delete the stats for `{interaction.guild.name}`? Please type the server name to continue!"
        )

        def is_valid_user(message: discord.Message):
            return (
                message.channel.id == interaction.channel.id
                and message.author.id == interaction.user.id
            )

        try:
            response = await self.bot.wait_for(
                "message", check=is_valid_user, timeout=30
            )
        except asyncio.TimeoutError:
            await interaction.followup.send(
                "You've exceeded the timeout! Please try the command again."
            )
        else:
            if response.content == interaction.guild.name:
                try:
                    guessr_statistics.load_stats()
                    guessr_statistics.delete_server_stats(interaction.guild.id)
                    guessr_statistics.save_stats()
                    await interaction.followup.send(
                        f"Successfully removed {interaction.guild.name} from the statistics!"
                    )
                except KeyError:
                    await interaction.followup.send(
                        f"{interaction.guild.name} not found in the statistics!"
                    )
            else:
                await interaction.followup.send("Not quite!")

    @app_commands.command(description="Uploads a chamber image directly to the bot.")
    @app_commands.describe(
        image="Image to upload.",
        difficulty="The expected difficulty to guess this image.",
        chamber="Enter the correct chamber.",
    )
    async def upload(
        self,
        interaction: discord.Interaction,
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
            await interaction.response.send_message(
                "Invalid file extension!", ephemeral=True
            )
            return

        image_extension = (
            image_filename[-4:]
            if image_filename.endswith((".jpg", ".png"))
            else image_filename[-5:]
        )
        image_uploaded_filename = f"{difficulty}-{chamber}-{str(datetime_now.strftime('%Y-%m-%d %H.%M.%S'))}{image_extension}"
        get_image = requests.get(image.url)

        try:
            with open(
                f"images/user_uploaded_chambers/{image_uploaded_filename}", "wb"
            ) as f:
                f.write(get_image.content)
        except Exception as e:
            await interaction.response.send_message(f"An error occured: {e}")
        else:
            upload_embed = discord.Embed(
                title=f"Successfully Uploaded {image_filename}!",
                color=const.BOT_COLOR,
            )
            upload_embed.set_image(url=image.url)
            upload_embed.set_footer(
                icon_url="attachment://logo.jpg",
                text="Please wait for your image to be approved by the developer (or not).",
            )
            await interaction.response.send_message(
                file=discord.File("logo.jpg", filename="logo.jpg"), embed=upload_embed
            )

    # Error handler inside this cog.
    @commands.Cog.listener()
    async def on_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                f"You're missing the required permission to run this command - Error: {error}",
                ephemeral=True,
            )
        else:
            raise error


async def setup(bot):
    await bot.add_cog(Config(bot))
