import platform
import time

import discord
from discord.ext import commands
from memory_profiler import memory_usage

from cogs.util import checks


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
        embed.colour = discord.Colour.blue()
        embed.url = self.bot.user.avatar_url
        embed.set_thumbnail(
            url='https://i.imgur.com/HI8kV9c.png')
        embed.add_field(name='Artist', value='SaiDrawing', inline=False)
        await self.bot.say(embed=embed)

    @info.command(name='name', pass_context=True, hidden=True)
    @checks.is_owner()
    async def _name(self, ctx, name: str):
        """Change the bot's username. OWNER ONLY."""
        await self.bot.edit_profile(username=name)
        embed = discord.Embed(title='Success', description='Changed my name to ' + name, colour=discord.Colour.green())
        await self.bot.say(embed=embed)

    @info.command(name='status', pass_context=True, aliases=['uptime', 'up'])
    async def _status(self, ctx: commands.Context):
        """Information about the bot's status."""
        uptime = time.time() - self.bot.uptime
        hours = uptime / 3600
        minutes = (uptime / 60) % 60
        seconds = uptime % 60

        users = 0
        channel = 0
        try:
            commands_chart = sorted(self.bot.counter.items(), key=lambda t: t[1], reverse=False)
            top_command = commands_chart.pop()
            command_info = f'{sum(self.bot.counter.values())} (Top Command: {top_command[0]} [x{top_command[1]}])'
        except IndexError:
            command_info = str(sum(self.bot.counter.values()))

        bot_member = ctx.message.server.get_member(self.bot.user.id)
        for server in self.bot.servers:
            users += len(server.members)
            channel += len(server.channels)
        embed = discord.Embed(colour=bot_member.top_role.colour)
        embed.add_field(name='Bot Creator', value=self.bot.owner.name, inline=False)
        embed.add_field(name='Uptime',
                        value='{0:.0f} Hours, {1:.0f} Minutes, and {2:.0f} Seconds'.format(hours, minutes, seconds),
                        inline=False)
        embed.add_field(name='Total Users', value=users)
        embed.add_field(name='Total Channels', value=channel)
        embed.add_field(name='Total Servers', value=str(len(self.bot.servers)))
        embed.add_field(name='Command Usage', value=command_info)
        embed.add_field(name='Bot Version', value=self.bot.version)
        embed.add_field(name='Discord.py Version', value=discord.__version__)
        embed.add_field(name='Python Version', value=platform.python_version())
        embed.add_field(name='Memory Usage', value='{} MB'.format(round(memory_usage(-1)[0], 3)))
        embed.add_field(name='Operating System',
                        value='{} {} {}'.format(platform.system(), platform.release(), platform.version()),
                        inline=False)
        await self.bot.say(embed=embed)


def setup(bot):
    bot.add_cog(Info(bot))
