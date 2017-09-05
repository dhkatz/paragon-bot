import asyncio
import datetime
import logging
import sys
import time
import traceback
from collections import Counter
from logging.handlers import RotatingFileHandler

import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from cleverwrap import CleverWrap
from discord.ext import commands
from peewee import *
from pytz import timezone

import data.config.load as config

__version__ = '0.25.1'

BOT_DESCRIPTION = '''A Discord bot built for Paragon servers.'''
BOT_STATUS = discord.Game(name='Paragon (Say ' + config.__prefix__ + 'help)')
BOT_DB = SqliteDatabase('C:/Users/mcilu/PycharmProjects/Paragon-Discord-Bot/Database/paragon_bot.db')


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        self.version = __version__
        self.counter = Counter()
        self.uptime = time.time()
        self.logger = set_logger()
        self.scheduler = AsyncIOScheduler(timezone=timezone('US/Pacific'))
        self.scheduler.start()
        self.db = BOT_DB
        super().__init__(*args, command_prefix=config.__prefix__, **kwargs)


def initialize(bot_class=Bot):
    bot = bot_class(description=BOT_DESCRIPTION)

    @bot.event
    async def on_ready():
        if bot.user.id == '308032552243822602':
            bot.dev = True
        else:
            bot.dev = False
        bot.logger.info(f'Logged in as {bot.user.name} ({bot.user.id}) (Dev Mode: {bot.dev})')
        for cog in config.__cogs__:
            try:
                bot.load_extension(cog)
            except Exception as cog_error:
                bot.logger.error(f'Unable to load cog {cog}')
                bot.logger.error(cog_error)
        bot.version = __version__
        bot.start_time = time.time()
        bot.commands_used = Counter()
        bot.owner = discord.utils.find(lambda u: u.id == config.__ownerid__, bot.get_all_members())
        bot.clever = CleverWrap(config.__cleverbot__)
        await bot.change_presence(game=BOT_STATUS)

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
                    raise
        elif isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(title='Command Cooldown', colour=discord.Colour.dark_red(),
                                  description=f'You\'re on cooldown! Try again in {str(error)[34:]}.')
            await bot.send_message(ctx.message.channel, embed=embed)

    @bot.event
    async def on_command(command, ctx):
        bot.counter[command.name] += 1
        msg = ctx.message
        if msg.channel.is_private:
            destination = 'Private Message'
        else:
            destination = f'#{msg.channel.name} ({msg.server.name})'
        bot.logger.info(f'{msg.author.name} in {destination}: {msg.content}')

    @bot.event
    async def on_message(message: discord.Message):
        if message.author.bot or message.author.id in config.__blacklist__:
            return
        if bot.user.mentioned_in(message) and not message.mention_everyone:
            await bot.send_message(message.channel, bot.clever.say(message.clean_content))
        await bot.process_commands(message)

    return bot


def set_logger():
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

    return logger


def main(bot: Bot):
    bot.uptime = time.time()
    yield from bot.login(config.__token__, )
    yield from bot.connect()


if __name__ == '__main__':
    bot = initialize()
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(main(bot))
    except discord.LoginFailure:
        bot.logger.error(traceback.format_exc())
    except Exception as e:
        bot.logger.exception("Fatal exception, attempting graceful logout",
                             exc_info=e)
        loop.run_until_complete(bot.logout())
    finally:
        loop.close()
        exit(0)
