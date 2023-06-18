# PortalGuessr

PortalGuessr is a Python bot that challenges you to guess a Portal chamber from a random picture taken from various locations, similar to GeoGuessr. Written in Python using py-cord library.

## Contributions

We welcome contributions to enhance the data sets used by the bot. If you would like to contribute, please join our [Discord server](https://discord.gg/hHYfnqa6zS).

## Self-hosting the bot

Hosting the bot is straightforward. Simply modify the token argument inside the `bot.run()` function and launch `launch.bat` for an easy startup. You can download the release version if available.

## Changelogs

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