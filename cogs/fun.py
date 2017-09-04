import json
import logging
import os
import random
import re

import aiohttp
import discord
from discord.ext import commands
from gtts import gTTS


class Fun:
    """Miscellaneous fun commands."""

    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord')
        self.word_list, self.bases = {}, []
        self.words = Config(os.path.join(os.path.dirname(__file__), 'words.json'))
        self.bot.scheduler.add_job(self.goodnight_jackson, 'cron', hour=22, minute=30)

    async def goodnight_jackson(self):
        self.logger.info('Saying goodnight to Jackson...')
        channel = discord.utils.find(lambda c: c.id == '222462913724547072', self.bot.get_all_channels())
        await self.bot.send_message(channel, 'Goodnight Jackson')

    def shitpost_sub(self, string, regex):
        if regex not in self.word_list or not self.word_list[regex]:
            self.word_list[regex] = self.words[self.words["@replaces"][regex]][:]
        word = self.word_list[regex].pop(random.randrange(len(self.word_list[regex])))
        return re.sub("%" + regex, word, string, 1)

    @commands.command(pass_context=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cat(self, ctx):
        """Get a random cat picture from random.cat"""
        url = 'https://random.cat/meow'

        async with aiohttp.get(url) as r:
            if r.status == 200:
                js = await r.json()
                await self.bot.say(js['file'])

    @commands.command(pass_context=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def shitpost(self, ctx):
        """Have the bot shitpost in chat."""
        # Shitpost code from https://github.com/yrsegal/shitpost
        if not self.bases:
            self.bases = self.words["@bases"]
        base = self.bases.pop(random.randrange(len(self.bases)))

        while "%" in base:
            if self.bot.dev:
                self.logger.info(base)
            for regex in self.words["@replaces"]:
                base = self.shitpost_sub(base, regex)

        if self.bot.dev:
            self.logger.info(base)
        self.words.reload()
        await self.bot.say(base)

    @commands.command(pass_context=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def tts(self, ctx, message: str):
        """Have the bot join your channel and say what you said."""
        # Thanks to https://stackoverflow.com/questions/9893175/google-text-to-speech-api/31791632#31791632
        tts = gTTS(text=message, lang='en')
        tts.save('temp.mp3')

    @commands.command(pass_context=True)
    @commands.cooldown(3, 60, commands.BucketType.user)
    async def feedme(self, ctx):
        """Feed your cat some spaghetti."""
        await self.bot.say('https://i.imgur.com/MWQb0Ow.jpg')


class Config:
    """
    A JSON read-only loader that will update automatically from `path`.
    """

    def __init__(self, path):
        self.path = path
        self.lastmodtime = os.path.getctime(path)  # get the last modified time of the target file
        self.data = json.load(open(path))

    def reload(self):
        if os.path.getctime(self.path) > self.lastmodtime:  # check the last modified time of the target file
            self.data = json.load(open(self.path))
            self.lastmodtime = os.path.getctime(self.path)

    # These are extensions of self.data's methods, except they run self.reload.
    def __getitem__(self, y):
        self.reload()
        return self.data[y]

    def __contains__(self, key):
        self.reload()
        return key in self.data

    def get(self, k, d=None):
        self.reload()
        return self.data.get(k, d)


def setup(bot):
    bot.add_cog(Fun(bot))
