from Modules.Agora import *
from Modules.Pick import *
from Modules.Info import *
from Modules.Music import *

BOT_DESCRIPTION = '''Bot commands using the Python Agora API.'''
BOT_COMMAND_PREFIX = '.'
BOT_STATUS = discord.Game(name='Say ' + BOT_COMMAND_PREFIX + 'help')

bot = commands.Bot(command_prefix=BOT_COMMAND_PREFIX, description=BOT_DESCRIPTION)
bot.add_cog(Agora(bot))
bot.add_cog(Pick(bot))
bot.add_cog(Info(bot))
bot.add_cog(Music(bot))


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    await bot.change_presence(game=BOT_STATUS)


# noinspection SpellCheckingInspection
bot.run('MzA4MDMyNTUyMjQzODIyNjAy.DFnY5Q.T7ztlpMlNdWKpgNs3uj96eXb7ng')
