import discord


class HelpButtonsLink(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(
            discord.ui.Button(
                style=discord.ButtonStyle.link,
                label="Discord",
                url="https://discord.gg/hHYfnqa6zS",
            )
        )
        self.add_item(
            discord.ui.Button(
                style=discord.ButtonStyle.link,
                label="GitHub",
                url="https://github.com/XnonXte/PortalGuessr",
            )
        )
