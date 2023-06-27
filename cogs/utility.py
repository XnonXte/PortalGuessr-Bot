"""
Cog for utility related commands.

Copyright (c) 2023 XnonXte
"""

import discord
from discord import app_commands
from discord.ext import commands
from components import const


class Utility(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(description="Returns the bot's latency.")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Pong! `{round(self.bot.latency * 1000)}` ms"
        )

    @app_commands.command(
        description="Shows an overview of the available slash commands."
    )
    async def help(self, interaction: discord.Interaction):
        help_message_embed = discord.Embed(
            title="About PortalGuessr",
            description="PortalGuessr is a bot that challenges you to guess a Portal chamber from a random picture taken from various locations, similar to GeoGuessr, thus the name PortalGuessr.\n\nIntrested on contributing? Join our [discord server](https://discord.gg/hHYfnqa6zS).",
            color=const.BOT_COLOR,
            url="https://github.com/XnonXte/PortalGuessr",
        )
        help_message_embed.add_field(name="Commands", value=const.MAIN_COMMANDS)
        help_message_embed.add_field(
            name="Config Commands", value=const.CONFIG_COMMANDS, inline=False
        )
        help_message_embed.set_footer(
            text=f"PortalGuessr {const.BOT_VERSION} | Created with 💖 by XnonXte.",
            icon_url="attachment://logo.jpg",
        )
        help_message_embed.set_thumbnail(url="attachment://logo.jpg")
        await interaction.response.send_message(
            file=discord.File("logo.jpg", filename="logo.jpg"),
            embed=help_message_embed,
        )


async def setup(bot):
    await bot.add_cog(Utility(bot))
