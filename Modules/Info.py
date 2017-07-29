import discord
from discord.ext import commands


class Info:
    """Information about the bot."""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True)
    async def info(self, ctx):
        """General bot information. See .help info for subcommands."""
        if ctx.invoked_subcommand is None:
            await self.bot.say('No subcommand passed!')

    @info.command(name='avatar', pass_context=True)
    async def _avatar(self, ctx):
        """Returns information about the bot's avatar."""
        embed = discord.Embed()
        embed.title = 'Bot Avatar Information'
        embed.url = 'http://saidrawing.deviantart.com/art/paragon-countess-663256538'
        embed.set_thumbnail(
            url='https://pre09.deviantart.net/d30c/th/pre/i/2017/043/7/b/paragon___countess_by_saidrawing-dayvw0q.png')
        embed.add_field(name='Artist', value='SaiDrawing', inline=False)
        await self.bot.send_message(ctx.message.channel, embed=embed)
