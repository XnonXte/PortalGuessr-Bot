"""
Cog for guessr related commands.

Copyright (c) 2023 XnonXte
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import Literal
import random
import asyncio
import time
from collections import Counter
from components import guessing, const


guessr_statistics = guessing.GuessrUsersStatistics("db\statistics.json")
is_guessr_running = False


class Guessr(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(description="Starts a PortalGuessr game.")
    @app_commands.describe(
        difficulty="Select the desired difficulty.",
        session="Have multiple guessing session in a row.",
    )
    async def guess(
        self,
        interaction: discord.Interaction,
        difficulty: Literal["Easy", "Medium", "Hard", "Very Hard", "Random"],
        session: int,
    ):
        """Main command to start PortalGuessr game."""
        global is_guessr_running

        # Check if a PortalGuessr game is already running.
        if is_guessr_running:
            await interaction.response.send_message(
                "A PortalGuessr game is already running, please wait until the game has finished!",
                ephemeral=True,
            )
            return
        elif session <= 0:
            # You can't have it equal or less than 0, can you?
            await interaction.response.send_message(
                "You can't have sessions equal or less than 0!", ephemeral=True
            )
            return

        is_guessr_running = True
        await interaction.response.defer()  # We use defer() to prevent interaction error caused by the bot not being able to response withing 3 seconds window (i.e. slow internet connection).
        correct_guessr = 0
        incorrect_guessr = 0
        guessr_skipped = 0
        users_participated = []
        users_correct = []
        guessr_stopped = False

        def get_most_common(List):
            """Finds the key that has most common occurence inside a list, returns None if the list is empty."""
            try:
                counter_list = Counter(List)
                return counter_list.most_common(1)[0][0]
            except IndexError:
                return None

        def is_valid_channel_and_chambers(message: discord.Message):
            """This checks for the same channel and valid chambers."""
            return (
                message.channel.id == interaction.channel.id
                and message.content.lower()
                in guessing.chambers_list
                + [
                    "skip",
                    "stop",
                ]  # We added the option to skip or stop the current game.
            )

        for game in range(session):
            if difficulty == "Random":
                guessr_difficulty = random.choice(
                    ["Easy", "Medium", "Hard", "Very Hard"]
                )
            else:
                guessr_difficulty = difficulty

            guessr_request = guessing.Guessr().get_guess(guessr_difficulty)
            guessr_image = guessr_request[0]
            guessr_correct_answer = guessr_request[1]
            guessr_color_accent = guessr_request[2]
            guessr_timeout = guessr_request[3]
            guessr_embed = discord.Embed(
                title="Which chamber is this?",
                description=f"🤯 Difficulty: ***{guessr_difficulty}***\n⌛ Time limit: ***{guessr_timeout} seconds***\n\n`skip` to skip the current guessr session.\n`stop` to stop the current guessr game.",
                color=guessr_color_accent,
            )
            guessr_embed.set_image(url="attachment://embed.jpg")
            guessr_embed.set_footer(
                text=f"Answer with a valid chamber number to make a guess!\n",
                icon_url="attachment://logo.jpg",
            )
            load_local_files = [
                discord.File(guessr_image, filename="embed.jpg"),
                discord.File("logo.jpg", filename="logo.jpg"),
            ]
            guessr_user_have_answered = []
            guessr_user_count = 0
            guessr_max_count = 5
            start_time = time.time()
            elapsed_time = 0
            timeout = guessr_timeout

            await interaction.followup.send(
                content=f"Guessr {game + 1} of {session}",
                files=load_local_files,
                embed=guessr_embed,
            )

            while True:
                try:
                    response: discord.Message = await self.bot.wait_for(
                        "message",
                        check=is_valid_channel_and_chambers,
                        timeout=timeout - elapsed_time,
                    )

                    if (
                        response.content.lower() == "skip"
                        or response.content.lower() == "stop"
                    ):
                        # Skip or stop the current session of the game.
                        if response.author.id == interaction.user.id:
                            if response.content.lower() == "skip":
                                title = "Guessr Skipped!"
                            else:
                                title = "Guessr Stopped!"

                            guessr_embed = discord.Embed(
                                title=title, color=const.BOT_COLOR
                            )
                            await interaction.followup.send(embed=guessr_embed)

                            if response.content.lower() == "skip":
                                guessr_skipped += 1
                                break
                            else:
                                guessr_stopped = True
                                break
                        else:
                            guessr_not_authorized_embed = discord.Embed(
                                title="⛔ You're not authorized to use this command!",
                                description="Only the user who started this game is able to skip or stop the current guessr game.",
                                color=const.BOT_COLOR,
                            )
                            guessr_not_authorized_embed.set_footer(
                                text="This message is deleted after 3 seconds.",
                                icon_url="attachment://logo.jpg",
                            )
                            await response.reply(
                                file=discord.File("logo.jpg", filename="logo.jpg"),
                                embed=guessr_not_authorized_embed,
                                delete_after=3,
                                mention_author=False,
                            )

                    # Check to make sure the user responding won't be able to answer twice.
                    if response.author.id not in guessr_user_have_answered:
                        guessr_user_have_answered.append(response.author.id)
                        guessr_user_count += 1

                        if f"`{response.author.name}`" not in users_participated:
                            users_participated.append(f"`{response.author.name}`")

                        if response.content.lower() == guessr_correct_answer:
                            response_reply_embed = discord.Embed(
                                title=f"🎉 Congratulations! You guessed chamber {guessr_correct_answer} correctly!",
                                description=f"You earned a point for {guessr_difficulty.lower()} guessr.",
                                color=const.BOT_COLOR,
                            )
                            response_reply_embed.set_footer(
                                text=f"/stats to open the statistics for {interaction.guild.name}!",
                                icon_url="attachment://logo.jpg",
                            )
                            await response.reply(
                                file=discord.File("logo.jpg", filename="logo.jpg"),
                                embed=response_reply_embed,
                                mention_author=False,
                            )

                            # Saving the score into leaderboard logic.
                            guessr_statistics.load_stats()
                            guessr_statistics.add_user_stats(
                                interaction.guild.id,
                                response.author.id,
                                guessr_difficulty,
                            )
                            guessr_statistics.save_stats()
                            users_correct.append(response.author.name)
                            correct_guessr += 1
                            break
                        elif guessr_user_count >= guessr_max_count:
                            max_guess_embed = discord.Embed(
                                title="Guessr Over!",
                                description="5 or more people have answered.",
                                color=discord.Color.from_rgb(237, 237, 237),
                            )
                            await interaction.followup.send(embed=max_guess_embed)
                            incorrect_guessr += 1
                            break
                    else:
                        response_twice_embed = discord.Embed(
                            title="⛔ You have already answered this guessr!",
                            color=const.BOT_COLOR,
                        )
                        response_twice_embed.set_footer(
                            text="This message is deleted after 3 seconds.",
                            icon_url="attachment://logo.jpg",
                        )
                        await response.reply(
                            file=discord.File("logo.jpg", filename="logo.jpg"),
                            embed=response_twice_embed,
                            mention_author=False,
                            delete_after=3,
                        )
                except asyncio.TimeoutError:
                    timeout_embed = discord.Embed(
                        title="Time's up!", color=discord.Color.from_rgb(237, 237, 237)
                    )
                    await interaction.followup.send(embed=timeout_embed)
                    incorrect_guessr += 1
                    break

                # Update elapsed time everytime the loop iterates through.
                elapsed_time = time.time() - start_time

            if guessr_stopped:
                # Escape out of the for loop.
                break

        # Preparing the endgame message.
        user_mvp = get_most_common(users_correct)
        guessr_game_statistics = (
            f"✅ Correct answer(s): ***{correct_guessr}***\n"
            f"❌ Incorrect answer(s): ***{incorrect_guessr}***\n"
            f"🏳 Guessr(s) skipped: ***{guessr_skipped}***\n\n"
            f"👥 User(s) Participated: {', '.join(users_participated) or 'No one participated :('}"
        )
        guessr_ending_embed = discord.Embed(
            title="Guessr Finished!"
            if not guessr_stopped
            else f"Guessr Stopped at {game + 1}",
            description=f"🔥 MVP: {user_mvp} for the most correct answers."
            if user_mvp
            else "🔥 MVP: No one answered correctly :(",
            color=const.BOT_COLOR,
        )
        guessr_ending_embed.add_field(
            name="Game Statistics", value=guessr_game_statistics
        )
        guessr_ending_embed.set_footer(
            icon_url="attachment://logo.jpg",
            text=f"/stats to open the statistics for {interaction.guild.name}!",
        )
        await interaction.followup.send(
            file=discord.File("logo.jpg", filename="logo.jpg"),
            embed=guessr_ending_embed,
        )

        # Ending the game.
        is_guessr_running = False


async def setup(bot):
    await bot.add_cog(Guessr(bot))
