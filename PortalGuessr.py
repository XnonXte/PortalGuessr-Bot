"""
Copyright (c) 2023 XnonXte

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

# PortalGuessr v0.4-beta

import discord
from discord.ext import commands
import os
import dotenv
from replit import keep_alive
from typing import Literal, Optional

dotenv.load_dotenv(".env")
token = os.environ["DEVTOKEN"]
prefix = commands.when_mentioned_or(";")
intents = discord.Intents.default()
intents.message_content = True


class PortalGuessr(commands.Bot):
    async def setup_hook(self):
        """Loading cogs into the bot."""
        failed = []
        for cog in os.listdir("cogs"):
            try:
                if cog.endswith(".py"):
                    await self.load_extension(f"cogs.{cog[:-3]}")
            except Exception as e:
                print(e)
                failed.append(cog)
        if failed:
            print(f"The following cog(s) failed to load: {failed}")


bot = PortalGuessr(command_prefix=prefix, intents=intents)


@bot.event
async def on_ready():
    print(
        """
  ___         _        _  ___                    
 | _ \___ _ _| |_ __ _| |/ __|_  _ ___ _______ _ 
 |  _/ _ \ '_|  _/ _` | | (_ | || / -_|_-<_-< '_|
 |_| \___/_|  \__\__,_|_|\___|\_,_\___/__/__/_|  
                                                 
"""
    )
    print(
        f"We have logged in as {bot.user}! Inside {len(bot.guilds)} guilds | discord.py version {discord.__version__}"
    )

    # Set the status to "watching on <number of guilds the bot is in> servers".
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching, name=f"on {len(bot.guilds)} servers"
        )
    )


@bot.command()
@commands.is_owner()
async def sync(ctx: commands.Context, option: Optional[Literal["local", "clear"]]):
    if option == "local":
        synced = await ctx.bot.tree.sync(guild=ctx.guild)
    elif option == "clear":
        ctx.bot.tree.clear_commands(guild=ctx.guild)
        await ctx.bot.tree.sync(guild=ctx.guild)
        synced = []
    else:
        synced = await ctx.bot.tree.sync()
    await ctx.send(
        f"{len(synced)} command(s) synced {'globally' if option is None else f'to {ctx.guild.name}'}."
    )


@sync.error
async def on_command_error(ctx: commands.Context, error: commands.CommandInvokeError):
    if isinstance(error, commands.NotOwner):
        await ctx.send(f"You're not the owner of this bot! Error: {error}")
    elif isinstance(error, commands.BadLiteralArgument):
        await ctx.send(f"Invalid argument(s)! Error: {error}")
    else:
        raise error


# Keeping the bot alive and running the bot.
keep_alive.keep_alive()
bot.run(token)
