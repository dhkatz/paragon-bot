import praw, prawcore, discord, asyncio
from discord.ext import commands

import data.config.load as config


class Reddit:
    """Reddit related commands. Designed for use by /r/Paragon moderators only!"""

    def __init__(self, bot):
        self.bot = bot
        self.user_agent = '/r/Paragon Post Collection Bot'
        self.subreddit_name = 'paragon'
        self.reddit = None
        self.subreddit = None

    async def login(self):
        # self.reddit = praw.Reddit(user_agent=self.user_agent, client_id=config.__reddit__['client_id'],
        #                           client_secret=config.__reddit__['client_secret'],
        #                           username=config.__reddit__['username'],
        #                           password=config.__reddit__['password'])
        # self.reddit.subreddit(self.subreddit_name)
        # # Make sure we are logged in!
        # self.bot.logger.info('Logged into Reddit as ' + str(self.reddit.user.me()))
        self.bot.logger.info('Test event.')

    @commands.group(name='reddit')
    async def reddit(self, ctx):
        """Useful Reddit commands."""
        if ctx.invoked_subcommand is None:
            await ctx.send('Reddit functionality is still a WIP!')

    @reddit.command(name='stickied')
    async def reddit_stickied(self, ctx):
        """Get the current stickied posts from /r/Paragon!"""
        for i in range(1, 3):
            try:
                sticky = self.subreddit.sticky(number=i)

            except prawcore.NotFound:
                continue
            embed = discord.Embed()
            embed.title = sticky.title
            embed.url = sticky.shortlink
            await ctx.send(embed=embed)
            print(vars(sticky))


def setup(bot):
    n = Reddit(bot)
    bot.add_listener(n.login, 'on_ready')
    bot.add_cog(n)
