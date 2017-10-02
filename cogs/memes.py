import discord
from peewee import *
from datetime import datetime

meme_db = SqliteDatabase('meme_archive.db')


class Memes:
    """Meme archive"""
    def __init__(self, bot):
        self.bot = bot
        self.setup_table()

    @staticmethod
    def setup_table():
        if 'meme' not in meme_db.get_tables():
            Meme.create_table()

    async def on_raw_reaction_add(self, emoji: discord.PartialReactionEmoji, message_id, channel_id, user_id):
        """Meme hall of fame"""
        if channel_id != 222462913724547072:
            return

        if emoji.is_custom_emoji() and emoji.id in [362849684756365313, 362849697397997570]:
            print("FOUND A MEME")
            meme = None
            try:
                meme = Meme.get(Meme.message == message_id)
            except DoesNotExist:
                channel = self.bot.get_channel(channel_id)
                message = channel.get_message(message_id)
                meme = Meme(message=message_id, channel=channel_id, user_id=message.author.id)
            finally:
                if meme is None:
                    return
                if emoji.id == 362849684756365313:
                    meme.votes += 1
                elif emoji.id == 362849697397997570:
                    meme.votes -= 1
                meme.save()

            if meme.votes >= 10 and not meme.posted:
                channel = self.bot.get_channel(362842783452495877)
                author = self.bot.get_user(meme.author)
                embed = discord.Embed()
                embed.set_author(name=author.name, icon_url=author.avatar_url)
                embed.description = 'Archived on {}'.format(datetime.now().strftime('%a %B %d, %Y'))


def setup(bot):
    bot.add_cog(Memes(bot))


class Meme(Model):
    message = IntegerField(unique=True)
    channel = IntegerField()
    author = IntegerField()
    votes = IntegerField(default=0)
    posted = BooleanField(default=False)

    class Meta:
        database = meme_db
