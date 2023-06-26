"""
Cog for guessr statistics related commands.

Copyright (c) 2023 XnonXte
"""

import discord
from discord import app_commands
from discord.ext import commands
from components import guessing, const
from typing import Optional

guessr_statistics = guessing.GuessrUsersStatistics("db\statistics.json")


class GuessrStatistics(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(description="Returns the current statistics.")
    @app_commands.describe(
        stats_for="Returns the statistics for a spesific user (blank for the whole statistics)."
    )
    async def stats(
        self, interaction: discord.Interaction, stats_for: Optional[discord.Member]
    ):
        guessr_statistics.load_stats()

        if stats_for:
            try:
                user_stats = guessr_statistics.get_user_stats(
                    interaction.guild.id, stats_for.id
                )
            except KeyError:
                await interaction.response.send_message(
                    f"The stats for {stats_for.name} in {interaction.guild.name} not found!",
                    ephemeral=True,
                )
                return
            stats_message = f'`{stats_for.name}` has completed {user_stats["Easy"]} easy, {user_stats["Medium"]} medium, and {user_stats["Hard"]} hard difficulty Guessr.'
            stats_embed = discord.Embed(
                title=f"Statistics for {stats_for.name} in {interaction.guild.name} 📋",
                description=stats_message,
                color=const.BOT_COLOR,
            )
            await interaction.response.send_message(embed=stats_embed)
        else:
            try:
                statistics = guessr_statistics.get_sorted_stats(interaction.guild.id)
            except KeyError:
                await interaction.response.send_message(
                    f"The statistics for {interaction.guild.name} is empty!",
                    ephemeral=True,
                )
                return
            statistics_message = ""
            for index, (user_id, stats) in enumerate(statistics, start=1):
                user = await self.bot.fetch_user(int(user_id))
                statistics_message += f"{index}. `{user.name}` has completed "
                stats_entries = []
                for difficulty in stats:
                    count = stats.get(difficulty)
                    stats_entries.append(f"{count} {difficulty.lower()}")
                statistics_message += ", ".join(stats_entries)
                statistics_message += " difficulty Guessr.\n"
            statistics_embed = discord.Embed(
                title=f"{interaction.guild.name} Statistics 🏆",
                description=statistics_message,
                color=const.BOT_COLOR,
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


async def setup(bot):
    await bot.add_cog(GuessrStatistics(bot))
