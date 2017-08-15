import asyncio
import os
import sys

import aiohttp
from discord.ext import commands

from util import checks


class Admin():
    """Commands executable only by the bot owner."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

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
        await self.bot.say(f'**:ok:** My new Avatar!\n {self.bot.user.avatar_url}')


def setup(bot):
    bot.add_cog(Admin(bot))
