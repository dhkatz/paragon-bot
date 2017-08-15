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
                await self.bot.say(js['file'])

    @commands.command(pass_context=True)
    async def shitpost(self, ctx):
        """Have the bot shitpost a Paragon meme in chat."""
        await self.bot.reply('Sorry fam, not able to shitpost yet.')



def setup(bot):
    bot.add_cog(Fun(bot))
