import logging

import praw
from discord.ext import commands

import data.config.load as config


class Reddit:
    """Reddit related commands. Designed for use by /r/Paragon moderators only!"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = logging.getLogger('discord')
        self.user_agent = '/r/Paragon Post Collection Bot'
        self.subreddit_name = 'doctorjewtest'
        self.reddit = praw.Reddit(user_agent=self.user_agent, client_id=config.__reddit__['client_id'],
                                  client_secret=config.__reddit__['client_secret'],
                                  username=config.__reddit__['username'],
                                  password=config.__reddit__['password'])
        # Make sure we are logged in!
        self.logger.info('Logged into Reddit as ' + str(self.reddit.user.me()))

    @commands.command(pass_context=True)
    async def reddit(self, ctx):
        print(ctx.message.author)


def setup(bot):
    bot.add_cog(Reddit(bot))
