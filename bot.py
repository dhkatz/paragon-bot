import discord
from discord.ext import commands
from Modules.Agora import *

BOT_DESCRIPTION = '''Bot commands using the Python Agora API.'''

bot = commands.Bot(command_prefix='.', description=BOT_DESCRIPTION)
bot.add_cog(Agora(bot))


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


# noinspection SpellCheckingInspection
bot.run('MzA4MDMyNTUyMjQzODIyNjAy.DFnY5Q.T7ztlpMlNdWKpgNs3uj96eXb7ng')
