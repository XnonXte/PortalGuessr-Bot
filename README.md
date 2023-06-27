# PortalGuessr

PortalGuessr is a Discord bot that challenges you to guess a Portal chamber from a random picture taken from various locations, similar to GeoGuessr. Written in Python with discord.py library.

## Contributions

We welcome contributions to enhance the data sets used by the bot. If you would like to contribute, please join our [Discord server](https://discord.gg/hHYfnqa6zS).

## Self-hosting the bot

Hosting the bot is straightforward. Simply modify the token argument inside the `bot.run()` function and launch `launch.bat` for an easy startup. You can download the release version if available.

### Requirements

The requirements.txt should contain the required libraries that your IDE will depend on to run this bot locally, and they will be installed using:

```shell
pip install -r requirements.txt
```

## Changelogs

- v0.4-beta:

  - Renamed a few commands, mainly reverting statistics to leaderboard.
  - major rework to /guess, mainly how the bot would send the message and response to the user.
  - Added the correct answer to the timeout message due to recent demand for it.

- v0.4-beta-Unstable-Version:

  - Overhauled commands into using cogs for ease of development.
  - Added the /upload command to upload an image directly to the bot.
  - Reworked config commands; added /clear_stats.
  - Several QoL changes and bug fixes.
  - added a lot of emojis.
  - Revamped /help message.
  - Added ;sync to sync slash commands into the tree.

- v0.3.1-beta:

  - Added activity status.
  - Renamed much of leaderboard to statistics.
  - Statistics (previously leaderboard) are now available for every server and they're separate from each other.
  - Removes admin.py in components and instead relies on app_commands.checks.has_permission() for permissions check.

- v0.3-beta:

  - Rewritten using Rapptz's discord.py; this will make future development easier.
  - Same as v0.2.2.1-beta feature-wise except for several QoL improvements and some slight renaming.

- v0.2.2-beta:

  - Fixed the issues with several admin commands not working properly.
  - Fixed the issue with the leaderboard not being able to display usernames and scores as intended.
  - Removed /upload since it prompts some hurdles that I don't want to fix at the moment.
  - The bot is now using discord.ext.commands instead of discord.ext.bridge for a temporary fix to hybrid commands that cannot pass arguments into options.

- v0.2.1-beta-Unstable-Build:

  - Added several new features, including admin commands.
  - Fixed the issue with how the bot listens to responses in /guess.
  - Added /leaderboard command.
  - Restructured PGComponents into smaller components for ease of use.

- v0.2-beta:

  - Added easy, medium, and hard difficulty levels for /guess.
  - Introduced /ping command to check the bot's latency.
  - Implemented several quality-of-life improvements.
  - Added the /bridge command.

- v0.1-beta:

  - Initial commit, representing the most basic version of this bot.
