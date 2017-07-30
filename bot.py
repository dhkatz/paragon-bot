from Modules.Agora import *
from Modules.Pick import *
from Modules.Info import *
from Modules.Music import *
from Modules.Fun import *
from discord.ext.commands import errors

BOT_DESCRIPTION = '''A Discord bot built for Paragon servers.'''
BOT_COMMAND_PREFIX = '.'
BOT_STATUS = discord.Game(name='Say ' + BOT_COMMAND_PREFIX + 'help')
BOT_TOKEN = 'MzA4MDMyNTUyMjQzODIyNjAy.DFnY5Q.T7ztlpMlNdWKpgNs3uj96eXb7ng'

bot = commands.Bot(command_prefix=BOT_COMMAND_PREFIX, description=BOT_DESCRIPTION)
bot.add_cog(Agora(bot))
bot.add_cog(Pick(bot))
bot.add_cog(Info(bot))
bot.add_cog(Music(bot))
bot.add_cog(Fun(bot))


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    await bot.change_presence(game=BOT_STATUS)
    await setup_data_tables(bot)


@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, errors.CheckFailure):
        await bot.send_message(ctx.message.channel,
                               content='You do not have permission to use ' + bot.command_prefix + ctx.invoked_with)


@bot.event
async def on_server_join(server):
    await asyncio.sleep(3)  # We wait for Discord to create the bot's role!
    await add_server(bot, server)


@bot.event
async def on_server_remove(server):
    print('NOTICE: Bot left server ' + server.name)
    await remove_server(server)


async def setup_data_tables(client):
    print('NOTICE: Setting up data tables...')
    set_players()
    set_heroes()
    set_cards()
    set_servers(client)
    print('NOTICE: Successfully setup data tables!')


bot.run(BOT_TOKEN)
