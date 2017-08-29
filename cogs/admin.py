import asyncio
import os
import sys

import aiohttp
import discord
from discord.ext import commands

from cogs.util import checks


class Admin():
    """Commands executable only by the bot owner."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def embed_notify(self, ctx: commands.Context, error: int, title: str, message: str):
        """Create and reply Discord embeds in one line."""
        embed = discord.Embed()
        embed.title = title
        embed.colour = discord.Colour.dark_red() if error == 1 else discord.Colour.green() if error == 0 else discord.Colour.blue()
        embed.description = message
        await self.bot.say(embed=embed)

    @commands.command(pass_context=True, aliases=['quit'], hidden=True)
    @checks.is_owner()
    async def shutdown(self, ctx):
        """Shutdown the bot. (Bot owner only)"""
        await self.bot.say('**:ok:** Goodbye!')
        self.bot.logout()
        sys.exit(0)

    @commands.command(pass_context=True, hidden=True)
    @checks.is_owner()
    async def restart(self, ctx):
        """Restart the bot program. (Bot owner only)"""
        await self.bot.say('**:ok:** Be back soon!')
        self.bot.logout()
        sys.exit(6)

    @commands.command(pass_context=True, hidden=True)
    @checks.is_owner()
    async def avatar(self, ctx, url: str):
        """Set the bot's avatar image. (Bot owner only)"""
        temp_avatar = 'temp_avatar.png'
        async with aiohttp.get(''.join(url)) as img:
            with open(temp_avatar, 'wb') as f:
                f.write(await img.read())
        with open(temp_avatar, 'rb') as f:
            await self.bot.edit_profile(avatar=f.read())
        os.remove(temp_avatar)
        await asyncio.sleep(2)
        embed = discord.Embed(title='Success', description='Changed my avatar!', colour=discord.Colour.green())
        await self.bot.say(embed=embed)

    @commands.group(pass_context=True, hidden=True)
    @checks.is_owner()
    async def blacklist(self, ctx, edit: str):
        """Blacklist users from using commands."""
        # TODO: Finish blacklist command
        if edit.lower() not in ['add', 'remove']:
            await self.embed_notify(ctx, 1, 'Invalid argument!',
                                    'You must specify whether you are adding or removing a user!')
        elif edit.lower() == 'add':
            print()
        elif edit.lower() == 'remove':
            print()


def setup(bot):
    bot.add_cog(Admin(bot))
