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
from cogs.database import *

__version__ = '0.31.1'

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
        self.dev = True
        self.icon_url = 'https://e-stats.io/src/images/games/paragon/logo-white-icon.png'
        self.clever = CleverWrap(config.__cleverbot__)
        super().__init__(*args, command_prefix=config.__prefix__, **kwargs)

    async def embed_notify(self, ctx: commands.Context, error: int, title: str, message: str):
        """Create and reply Discord embeds in one line."""
        embed = discord.Embed()
        embed.title = title
        embed.colour = discord.Colour.dark_red() if error == 1 else discord.Colour.green() if error == 0 else discord.Colour.blue()
        embed.description = message
        embed.set_footer(text='Paragon', icon_url=self.icon_url)
        await ctx.send(embed=embed)


def initialize(bot_class=Bot):
    bot = bot_class(description=BOT_DESCRIPTION)

    @bot.event
    async def on_ready():
        if bot.user.id == 308032552243822602:
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
        bot.commands_used = Counter()
        await bot.change_presence(game=BOT_STATUS)

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await bot.embed_notify(ctx, 1, 'Error', 'This command cannot be used in private messages.')
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send(':x: This command has been disabled.')
        elif isinstance(error, commands.CommandInvokeError):
            if bot.dev:
                raise error
            else:
                embed = discord.Embed(title=':x: Command Error', colour=0x992d22)  # Dark Red
                embed.add_field(name='Error', value=str(error))
                embed.add_field(name='Server', value=ctx.guild)
                embed.add_field(name='Channel', value=ctx.channel)
                embed.add_field(name='User', value=ctx.author.name)
                embed.add_field(name='Message', value=ctx.message.clean_content)
                embed.timestamp = datetime.datetime.utcnow()
                try:
                    await bot.owner.send(embed=embed)
                except:
                    raise
        elif isinstance(error, commands.CommandOnCooldown):
            await bot.embed_notify(ctx, 1, 'Command Cooldown', f'You\'re on cooldown! Try again in {str(error)[34:]}.')
        elif isinstance(error, commands.CheckFailure):
            await bot.embed_notify(ctx, 1, 'Command Error', 'You do not have permission to use this command!')
        else:
            raise error

    @bot.event
    async def on_command(ctx):
        bot.counter[ctx.command.name] += 1
        if isinstance(ctx.channel, discord.abc.PrivateChannel):
            destination = 'Private Message'
        else:
            destination = f'#{ctx.channel.name} ({ctx.guild.name})'
        bot.logger.info(f'{ctx.author.name} in {destination}: {ctx.message.content}')

    @bot.event
    async def on_message(message: discord.Message):
        if Player.select().where(
                        (Player.discord_id == str(message.author.id)) & (Player.blacklist == True)).count() != 0:
            ctx = await bot.get_context(message)
            if ctx.valid:
                await bot.embed_notify(ctx, 1, 'Error', 'You are blacklisted from commands!')
            return
        if bot.user.mentioned_in(message) and not message.mention_everyone:
            await message.channel.send(bot.clever.say(message.clean_content))
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
