"""
Cog for guessr leaderboard related commands.

Copyright (c) 2023 XnonXte
"""

from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from modules import const, trivia

trivia_leaderboard = trivia.TriviaLeaderboard("database/leaderboard.json")


class TriviaLeaderboardCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(description="Returns the current leaderboard")
    @app_commands.describe(limit="Sets a limit for the leaderboard")
    @app_commands.describe(stats_for="Returns the stats from a specific user instead")
    async def leaderboard(
        self,
        ctx: commands.Context,
        limit: Optional[int] = None,
        stats_for: Optional[discord.Member] = None,
    ):
        await ctx.defer()
        trivia_leaderboard.load_leaderboard()

        if stats_for:
            try:
                user_stats = trivia_leaderboard.get_user_leaderboard(
                    ctx.guild.id, stats_for.id
                )
                full_leaderboard = trivia_leaderboard.get_sorted_leaderboard(
                    ctx.guild.id, None
                )
            except KeyError:
                await ctx.send(
                    f"The stats for {stats_for.name} in {ctx.guild.name} not found!",
                    ephemeral=True,
                )
                return

            leaderboard_message = f"`{stats_for.name}` has completed {user_stats['Easy']} easy, {user_stats['Medium']} medium, {user_stats['Hard']} hard, and {user_stats['Very Hard']} very hard difficulty Guessr."
            leaderboard_embed = discord.Embed(
                title=f"leaderboard for {stats_for.name} in {ctx.guild.name}",
                description=leaderboard_message,
                color=const.BOT_COLOR,
            )
            leaderboard_embed.set_thumbnail(url="attachment://placement.png")
            leaderboard_embed.set_footer(
                text=f"{len(full_leaderboard) or '0'} user(s) in the leaderboard!",
                icon_url="attachment://logo.jpg",
            )
            files = [
                discord.File("images/local/placement.png", filename="placement.png"),
                discord.File("logo.jpg", filename="logo.jpg"),
            ]
            return
        try:
            leaderboard = trivia_leaderboard.get_sorted_leaderboard(ctx.guild.id, limit)
            full_leaderboard = trivia_leaderboard.get_sorted_leaderboard(
                ctx.guild.id, None
            )
        except KeyError:
            await ctx.send(
                f"The leaderboard for {ctx.guild.name} is empty!",
                ephemeral=True,
            )
            return

        leaderboard_message = ""
        for index, (user_id, stats) in enumerate(leaderboard, start=1):
            user = await self.bot.fetch_user(int(user_id))
            stats_entries = [
                f"{count} {difficulty.lower()}" for difficulty, count in stats.items()
            ]
            stats_string = ", ".join(stats_entries)
            leaderboard_message += f"{index}. `{user.name}` has completed {stats_string} difficulty Guessr.\n"

        leaderboard_embed = discord.Embed(
            title=f"{ctx.guild.name} leaderboard",
            description=leaderboard_message,
            color=const.BOT_COLOR,
        )
        leaderboard_embed.set_footer(
            text=f"{len(full_leaderboard) or '0'} user(s) in the leaderboard!",
            icon_url="attachment://logo.jpg",
        )
        leaderboard_embed.set_thumbnail(url="attachment://placement.png")
        files = [
            discord.File("logo.jpg", filename="logo.jpg"),
            discord.File("images/local/placement.png", filename="placement.png"),
        ]

        await ctx.send(
            files=files,
            embed=leaderboard_embed,
        )


async def setup(bot):
    await bot.add_cog(TriviaLeaderboardCommands(bot))
