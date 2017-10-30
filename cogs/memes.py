import discord
from discord.ext import commands
from peewee import *
from datetime import datetime, timedelta
from discord.errors import Forbidden

meme_db = SqliteDatabase('meme_archive.db')


class Memes:
    """Meme archive"""

    def __init__(self, bot):
        self.bot = bot
        self.feed = self.bot.get_channel(361573491591479297)
        self.archive = self.bot.get_channel(365568113510711326)
        self.setup_memes()
        self.bot.scheduler.add_job(self.clean_memes, 'cron', hour=2)

    @staticmethod
    def setup_memes():
        if 'meme' not in meme_db.get_tables():
            Meme.create_table()

    @staticmethod
    def clean_memes():
        for meme in Meme.select().where(Meme.posted == 0):
            if meme.date < datetime.utcnow() - timedelta(weeks=1):
                meme.delete_instance()

    async def add_meme(self, meme, message):
        ctx = await self.bot.get_context(message)
        author = self.bot.get_user(meme.author)
        embed = discord.Embed()
        embed.set_author(name=author.name, icon_url=author.avatar_url)
        embed.description = 'Archived on {}'.format(datetime.now().strftime('%a %B %d, %Y'))
        meme.archive_id = await self.archive.send(embed=embed)
        meme.posted = True
        self.bot.logger.info(f'Archived meme by {author.name} ({author.id})')
        meme.save()

    async def remove_meme(self, meme, message: discord.Message):
        ctx = await self.bot.get_context(message)
        try:
            if meme.posted and message.id == meme.archive_id:
                await message.delete()
        except Forbidden:
            if ctx.valid:
                await self.bot.embed_notify(ctx, 1, 'Error', 'Could not remove meme below threshold!')
        else:
            await self.bot.embed_notify(ctx, 2, 'Notice', 'A meme was removed from the archive!')
        meme.delete_instance()

    async def on_raw_reaction_add(self, emoji: discord.PartialReactionEmoji, message_id, channel_id, user_id):
        """Meme hall of fame, adding votes."""
        if channel_id not in (self.feed.id, self.archive.id):
            return

        if emoji.is_custom_emoji() and emoji.id in [358750319586574346, 358750319083126784]:
            meme = None
            channel = self.bot.get_channel(channel_id)
            message = await channel.get_message(message_id)
            try:
                meme = Meme.get((Meme.message == message_id) | (Meme.archive_id == message_id))
            except DoesNotExist:
                meme = Meme(message=message_id, channel=channel_id, author=message.author.id, votes=0,
                            date=datetime.utcnow())

            if meme is None:
                return

            if emoji.id == 358750319586574346:
                meme.votes += 1
            elif emoji.id == 358750319083126784:
                meme.votes -= 1

            meme.save()

            if meme.votes >= 10 and not meme.posted:
                await self.add_meme(meme, message)

            if meme.votes < 10 and meme.posted:
                await self.remove_meme(meme, message)
                return

    async def on_raw_reaction_remove(self, emoji: discord.PartialReactionEmoji, message_id, channel_id, user_id):
        """Meme hall of fame, removing votes."""
        if channel_id not in [self.feed.id, self.archive.id]:
            return

        if emoji.is_custom_emoji() and emoji.id in [358750319586574346, 358750319083126784]:
            meme = None
            channel = self.bot.get_channel(channel_id)
            message = channel.get_message(message_id)
            try:
                meme = Meme.get((Meme.message == message_id) | (Meme.archive_id == message_id))
            except DoesNotExist:  # How could this possibly not exist?
                meme = Meme(message=message_id, channel=channel_id, author=message.author.id, votes=0,
                            date=datetime.utcnow())

            if meme is None:
                return
            if emoji.id == 358750319586574346:
                meme.votes -= 1
            elif emoji.id == 358750319083126784:
                meme.votes += 1

            meme.save()

            if meme.votes >= 10 and not meme.posted:
                await self.add_meme(meme, message)

            if meme.votes < 10 and meme.posted:
                await self.remove_meme(meme, message)

    @commands.group(name='meme')
    @commands.is_owner()
    async def meme(self, ctx):
        """Meme base command"""
        if ctx.invoked_subcommand is None:
            pass

    @meme.command(name='archive')
    @commands.is_owner()
    async def meme_archive(self, ctx, message_id: int):
        meme = None
        message = await ctx.channel.get_message(message_id)
        try:
            meme = Meme.get((Meme.message == message_id) | (Meme.archive_id == message_id))
        except DoesNotExist:
            meme = Meme(message=message_id, channel=ctx.channel.id, author=message.author.id, votes=0,
                        date=datetime.utcnow())

        if meme is not None:
            if not meme.posted:
                await self.add_meme(meme, message)
            else:
                self.bot.embed_notify(ctx, 1, 'Error', 'Meme is already archived!')


def setup(bot):
    bot.add_cog(Memes(bot))


class Meme(Model):
    message = IntegerField(unique=True)
    channel = IntegerField()
    author = IntegerField()
    votes = IntegerField(default=0)
    posted = BooleanField(default=False)
    archive_id = IntegerField(null=True)
    date = DateTimeField()

    class Meta:
        database = meme_db
