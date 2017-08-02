from discord.ext import commands


class Reddit:
    """Reddit related commands. Designed for use by /r/Paragon moderators only!
        Requires an authentication key to be used!
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
