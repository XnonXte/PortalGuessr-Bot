import discord

BOT_COLOR = discord.Color.from_rgb(203, 48, 48)
BOT_VERSION = "0.4-beta"
MAIN_COMMANDS = """
`help` - Shows an overview of the available slash command.
`ping` - Returns the bot's latency.
`guess` - Starts a Portalguesser game.
`leaderboard` - Returns the current leaderboard.
"""
CONFIG_COMMANDS = """
`clear` - Clear the server leaderboard.
`remove` - Removes a spesific user from the leaderboard.
`upload` - Uploads a chamber image directly to the bot.
"""
