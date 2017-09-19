import praw, prawcore, discord, asyncio
from discord.ext import commands

import data.config.load as config
from .util.paginator import EmbedPages
import time


class Reddit:
    """Reddit related commands. Designed for use by /r/Paragon moderators only!"""

    def __init__(self, bot):
        self.bot = bot
        self.instance = praw.Reddit(user_agent='/r/Paragon Discord Bot', client_id=config.__reddit__['client_id'],
                                    client_secret=config.__reddit__['client_secret'],
                                    username=config.__reddit__['username'], password=config.__reddit__['password'])
        self.subreddit = self.instance.subreddit('paragon')
        self.bot.logger.info('Logged into Reddit as ' + str(self.instance.user.me()))

    @commands.group(name='reddit')
    async def reddit(self, ctx):
        pass

    @reddit.command(name='sticky')
    async def reddit_stickied(self, ctx):
        """Get the current stickied posts from /r/Paragon!"""
        embeds = []
        for i in range(1, 3):
            try:
                sticky = self.subreddit.sticky(number=i)
            except prawcore.NotFound:
                continue
            else:
                embeds.append(await self.build_submission_embed(sticky))
        if len(embeds) == 0:
            self.bot.embed_notify(ctx, 2, 'Notice', 'There are currently no announcements!')
            return
        p = EmbedPages(ctx, icon_url=self.bot.icon_url, entries=embeds)
        await p.paginate()

    @commands.command(name='official')
    async def reddit_official(self, ctx):
        """Get official posts from Epic Games currently on the front page."""
        embeds = []
        for submission in self.subreddit.hot():
            if str(submission.link_flair_text).upper() == 'OFFICIAL':
                embeds.append(await self.build_submission_embed(submission))

        if len(embeds) == 0:
            self.bot.embed_notify(ctx, 2, 'Notice', 'There are currently no official posts!')
            return

        p = EmbedPages(ctx, icon_url=self.bot.icon_url, entries=embeds)
        await p.paginate()

    @staticmethod
    async def build_submission_embed(submission):
        embed = discord.Embed()
        embed.title = submission.title
        embed.url = submission.shortlink
        embed.description = submission.selftext[:240] + '...'
        embed.add_field(name='Author', value=submission.author.name, inline=False)
        embed.add_field(name='Time', value=time.strftime("%a, %d %b %Y %H:%M", time.gmtime(submission.created_utc)),
                        inline=False)
        return embed


def setup(bot):
    bot.add_cog(Reddit(bot))
