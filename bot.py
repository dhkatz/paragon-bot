import asyncio
import datetime
import logging
import sys
import time
from collections import Counter
from logging.handlers import RotatingFileHandler

import discord
from cleverwrap import CleverWrap
from discord.ext import commands

import config.load as config
import database.database as db

__version__ = '0.15.1'

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
log_format = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')

ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(log_format)
ch.setLevel(logging.INFO)
logger.addHandler(ch)

fh = RotatingFileHandler(filename='discordbot.log', maxBytes=1024 * 5, backupCount=2, encoding='utf-8', mode='w')
fh.setFormatter(log_format)
logger.addHandler(fh)

BOT_DESCRIPTION = '''A Discord bot built for Paragon servers.'''
BOT_STATUS = discord.Game(name='Paragon (Say ' + config.__prefix__ + 'help)')

bot = commands.Bot(command_prefix=config.__prefix__, description=BOT_DESCRIPTION)


@bot.event
async def on_ready():
    if bot.user.id == '308032552243822602':
        bot.dev = True
    else:
        bot.dev = False
    logger.info(f'Logged in as {bot.user.name} ({bot.user.id}) (Dev Mode: {bot.dev})')
    for cog in config.__cogs__:
        try:
            bot.load_extension(cog)
        except Exception:
            logger.error(f'Unable to load cog {cog}')
    bot.version = __version__
    bot.start_time = time.time()
    bot.commands_used = Counter()
    bot.owner = discord.utils.find(lambda u: u.id == config.__ownerid__, bot.get_all_members())
    bot.clever = CleverWrap(config.__cleverbot__)
    await bot.change_presence(game=BOT_STATUS)
    await setup_data_tables(bot)


@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.NoPrivateMessage):
        await bot.send_message(ctx.message.author, 'This command cannot be used in private messages.')
    elif isinstance(error, commands.DisabledCommand):
        await bot.say(':x: This command has been disabled.')
    elif isinstance(error, commands.CommandInvokeError):
        if bot.dev:
            raise error
        else:
            embed = discord.Embed(title=':x: Command Error', colour=0x992d22)  # Dark Red
            embed.add_field(name='Error', value=str(error))
            embed.add_field(name='Server', value=ctx.message.server)
            embed.add_field(name='Channel', value=ctx.message.channel)
            embed.add_field(name='User', value=ctx.message.author)
            embed.add_field(name='Message', value=ctx.message.clean_content)
            embed.timestamp = datetime.datetime.utcnow()
            try:
                await bot.send_message(bot.owner, embed=embed)
            except:
                pass


@bot.event
async def on_command(command, ctx):
    bot.commands_used[command.name] += 1
    msg = ctx.message
    if msg.channel.is_private:
        destination = 'Private Message'
    else:
        destination = f'#{msg.channel.name} ({msg.server.name})'
    logger.info(f'{msg.author.name} in {destination}: {msg.content}')


@bot.event
async def on_server_join(server):
    await asyncio.sleep(3)  # We wait for Discord to create the bot's role!
    await db.add_server(bot, server)


@bot.event
async def on_server_remove(server):
    logger.info(f'Bot left server: {server.name}')
    await db.remove_server(server)


@bot.event
async def on_message(message):
    if bot.user.mentioned_in(message):
        await bot.send_message(message.channel, bot.clever.say(message.clean_content))
    await bot.process_commands(message)

async def setup_data_tables(client):
    logger.info(f'Setting up data tables...')
    db.setup_tables(client)
    logger.info(f'Successfully setup data tables!')

async def check_tournament():
    await bot.wait_until_ready()
    while not bot.is_closed:
        await asyncio.sleep(60)
        logger.info(f'Checking unconfirmed tournaments...')
        db.update_tournaments()

bot.loop.create_task(check_tournament())
bot.run(config.__token__)
