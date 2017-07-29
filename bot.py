from Modules.Agora import *
from Modules.Pick import *

BOT_DESCRIPTION = '''Bot commands using the Python Agora API.'''

bot = commands.Bot(command_prefix='.', description=BOT_DESCRIPTION)
bot.add_cog(Agora(bot))
bot.add_cog(Pick(bot))


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


# noinspection SpellCheckingInspection
bot.run('MzA4MDMyNTUyMjQzODIyNjAy.DFnY5Q.T7ztlpMlNdWKpgNs3uj96eXb7ng')
