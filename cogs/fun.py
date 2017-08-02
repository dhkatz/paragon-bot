from discord.ext import commands
import aiohttp


class Fun:
    """Miscellaneous fun commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def cat(self, ctx):
        """Get a random cat picture from random.cat"""
        url = 'https://random.cat/meow'

        async with aiohttp.get(url) as r:
            if r.status == 200:
                js = await r.json()
                await self.bot.send_message(ctx.message.channel, js['file'])
                await self.bot.edit_profile()


def setup(bot):
    bot.add_cog(Fun(bot))
