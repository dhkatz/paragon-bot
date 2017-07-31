from discord.ext import commands


class Tournament:
    """Create and run tournaments on your Discord server."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group()
    async def tournament(self):
        """Tournament commands related to this server."""
        await self.bot.reply('Please see ' + self.bot.command_prefix + 'help tournament for command usage.')

    @tournament.command(name='create', pass_context=True)
    async def _create(self, ctx, name: str, ):
        """Create a new tournament on this server."""
