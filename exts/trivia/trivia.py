"""
Cog for guessr related commands.

Copyright (c) 2023 XnonXte
"""

"""
To avoid some confusion, variables with trivia- (previously guessr-) prefix are related to the guessr game.
"""

# TODO: Fix the issue with the bot not able to start a different guessr when one is prompted somewhere else.

import asyncio
import time
import random
from typing import Literal, Optional
from collections import Counter

import discord
from discord import app_commands
from discord.ext import commands

from modules import const, trivia


trivia_leaderboard = trivia.TriviaLeaderboard("database/leaderboard.json")
running_channel_list = []


def get_most_common(List):
    """Finds the key that has most common occurence inside a list, returns None if the list is empty."""
    try:
        counter_list = Counter(List)
        return counter_list.most_common(1)[0][0]
    except IndexError:
        return None


class TriviaCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(description="Starts a PortalGuessr game")
    @app_commands.describe(
        difficulty="The desired difficulty",
        rounds="Session rounds",
    )
    async def guess(
        self,
        ctx: commands.Context,
        difficulty: Literal["Random", "Easy", "Medium", "Hard", "Very Hard"],
        rounds: Optional[int] = 10,
    ):
        """Main command to start PortalGuessr game."""
        global running_channel_list

        def is_valid_guild_channel_chambers(message: discord.Message):
            """This checks for the same channel and valid chambers."""
            # Added the option to skip or stop the current game.
            return (
                message.guild.id == ctx.guild.id
                and message.channel.id == ctx.channel.id
                and message.content.lower() in trivia.chambers_list + ["skip", "stop"]
            )

        # Check if a PortalGuessr game is already running in the specified channel.
        if rounds <= 0:
            # You can't have 0 or less rounds.
            await ctx.send(
                "You can't have sessions equal or less than 0!", ephemeral=True
            )
            return

        if ctx.channel.id in running_channel_list:
            await ctx.send(
                f"A PortalGuessr game is already running in {ctx.channel.id}, please wait until the game has finished or start another one on different channel!",
                ephemeral=True,
            )
            return

        running_channel_list.append(ctx.channel.id)

        # We use defer() to prevent interaction error caused by the bot not being able to response withing 3 seconds window (i.e. slow internet connection).
        await ctx.defer()

        trivia_correct = 0
        trivia_incorrect = 0
        trivia_skipped = 0
        trivia_participated = []
        trivia_users_correct = []
        trivia_stopped = False

        for round in range(rounds):
            if difficulty == "Random":
                trivia_difficulty = random.choice(
                    ["Easy", "Medium", "Hard", "Very Hard"]
                )
            else:
                trivia_difficulty = difficulty

            trivia_data_request = trivia.TriviaGame().get_guess(trivia_difficulty)
            trivia_image = trivia_data_request[0]
            trivia_correct_answer = trivia_data_request[1]
            trivia_color_accent = trivia_data_request[2]
            trivia_timeout = trivia_data_request[3]
            trivia_stop_skip_embed = discord.Embed(
                title=f"Round {round + 1} of {rounds}",
                description=f"Which chamber is this?\n\nDifficulty: ***{trivia_difficulty}***\nTime limit: ***{trivia_timeout} seconds***\n\n`skip` to skip the current guessr session.\n`stop` to stop the current guessr game.",
                color=trivia_color_accent,
            )
            trivia_stop_skip_embed.set_image(url="attachment://embed.jpg")
            trivia_stop_skip_embed.set_footer(
                text=f"Answer with a valid chamber number to make a guess!",
                icon_url="attachment://logo.jpg",
            )
            image_and_logo = [
                discord.File(trivia_image, filename="embed.jpg"),
                discord.File("logo.jpg", filename="logo.jpg"),
            ]
            trivia_users_have_answered = []
            trivia_user_count = 0
            trivia_max_count = 5
            trivia_start_time = time.time()
            trivia_elapsed_time = 0
            trivia_timeout = trivia_timeout

            if round == 0:
                await ctx.send(
                    files=image_and_logo,
                    embed=trivia_stop_skip_embed,
                )
            else:
                await ctx.channel.send(
                    files=image_and_logo,
                    embed=trivia_stop_skip_embed,
                )

            while True:
                try:
                    response: discord.Message = await self.bot.wait_for(
                        "message",
                        check=is_valid_guild_channel_chambers,
                        timeout=trivia_timeout - trivia_elapsed_time,
                    )

                    if (
                        response.content.lower() == "skip"
                        or response.content.lower() == "stop"
                    ):
                        # Skip or stop the current session of the game.
                        if response.author.id == ctx.author.id:
                            if response.content.lower() == "skip":
                                title = "Guessr Skipped!"
                            else:
                                title = "Guessr Stopped!"

                            trivia_stop_skip_embed = discord.Embed(
                                title=title, color=const.BOT_COLOR
                            )
                            await ctx.channel.send(embed=trivia_stop_skip_embed)

                            if response.content.lower() == "skip":
                                trivia_skipped += 1
                                break
                            else:
                                trivia_stopped = True
                                break
                        else:
                            trivia_not_authorized_embed = discord.Embed(
                                title="You're not authorized to use this command!",
                                description="Only the user who started this game is able to skip or stop the current guessr game.",
                                color=const.BOT_COLOR,
                            )
                            trivia_not_authorized_embed.set_footer(
                                text="This message is deleted after 3 seconds.",
                                icon_url="attachment://logo.jpg",
                            )
                            trivia_not_authorized_embed.set_thumbnail(
                                url="attachment://no_entry.png"
                            )
                            files = [
                                discord.File(
                                    "images/local/no_entry.png", filename="no_entry.png"
                                ),
                                discord.File("logo.jpg", filename="logo.jpg"),
                            ]

                            await response.reply(
                                files=files,
                                embed=trivia_not_authorized_embed,
                                delete_after=3,
                                mention_author=False,
                            )

                            # Continue so we don't ignore the user's response later on.
                            continue

                    # Check to make sure the user responding won't be able to answer twice.
                    if response.author.id not in trivia_users_have_answered:
                        trivia_users_have_answered.append(response.author.id)
                        trivia_user_count += 1

                        if f"`{response.author.name}`" not in trivia_participated:
                            trivia_participated.append(f"`{response.author.name}`")

                        if response.content.lower() == trivia_correct_answer:
                            await response.add_reaction("✅")

                            # Saving the score into leaderboard logic.
                            trivia_leaderboard.load_leaderboard()
                            trivia_leaderboard.add_user_leaderboard(
                                ctx.guild.id,
                                response.author.id,
                                trivia_difficulty,
                            )
                            trivia_leaderboard.save_leaderboard()
                            trivia_users_correct.append(response.author.name)
                            trivia_correct += 1
                            break
                        else:
                            await response.add_reaction("❌")

                        if trivia_user_count >= trivia_max_count:
                            max_guess_embed = discord.Embed(
                                title="Round over!",
                                description="5 or more people have answered.",
                                color=discord.Color.from_rgb(237, 237, 237),
                            )
                            await ctx.channel.send(embed=max_guess_embed)
                            trivia_incorrect += 1
                            break
                    else:
                        response_twice_embed = discord.Embed(
                            title="You've already answered this guessr!",
                            description="This message is deleted after 3 seconds.",
                            color=const.BOT_COLOR,
                        )
                        response_twice_embed.set_thumbnail(
                            url="attachment://no_entry.png"
                        )
                        await response.reply(
                            file=discord.File(
                                "images/local/no_entry.png", filename="no_entry.png"
                            ),
                            embed=response_twice_embed,
                            mention_author=False,
                            delete_after=3,
                        )
                except asyncio.TimeoutError:
                    timeout_embed = discord.Embed(
                        title="Time's up!",
                        description=f"The correct answer was **{trivia_correct_answer}**.",
                        color=discord.Color.from_rgb(237, 237, 237),
                    )
                    await ctx.channel.send(embed=timeout_embed)
                    trivia_incorrect += 1
                    break

                # Update elapsed time everytime the loop iterates through.
                trivia_elapsed_time = time.time() - trivia_start_time

            if trivia_stopped:
                # Escape out of the for loop.
                break

        # Preparing the endgame message.
        user_mvp = get_most_common(trivia_users_correct)
        trivia_game_statistics = (
            f"Correct answer(s): ***{trivia_correct}***\n"
            f"Incorrect answer(s): ***{trivia_incorrect}***\n"
            f"Guessr(s) skipped: ***{trivia_skipped}***\n\n"
            f"User(s) Participated: {', '.join(trivia_participated) or 'None'}"
        )
        trivia_ending_embed = discord.Embed(
            title="Game finished, well done!"
            if not trivia_stopped
            else f"Game stopped at round {round + 1} :(",
            description=f"MVP: {user_mvp} for the most correct answers."
            if user_mvp
            else "MVP: None",
            color=const.BOT_COLOR,
        )
        trivia_ending_embed.add_field(
            name="Game Statistics", value=trivia_game_statistics
        )
        trivia_ending_embed.set_thumbnail(url="attachment://game_over.png")
        trivia_ending_embed.set_footer(
            icon_url="attachment://logo.jpg",
            text=f"/leaderboard to open the statistics for {ctx.guild.name}!",
        )
        files = [
            discord.File("logo.jpg", filename="logo.jpg"),
            discord.File("images/local/game_over.png", filename="game_over.png"),
        ]
        await ctx.send(
            files=files,
            embed=trivia_ending_embed,
        )

        # Ending the game instance.
        running_channel_list.remove(ctx.channel.id)


async def setup(bot):
    await bot.add_cog(TriviaCommands(bot))
