import json
import logging
import os
import random
import re

import aiohttp
import discord
from discord.ext import commands


class Fun:
    """Miscellaneous fun commands."""

    def __init__(self, bot):
        self.bot = bot
        self.word_list, self.bases = {}, []
        self.words = Config(os.path.join(os.path.dirname(__file__), 'words.json'))
        self.bot.scheduler.add_job(self.goodnight_jackson, 'cron', hour=23, minute=30)

    async def goodnight_jackson(self):
        self.bot.logger.info('Saying goodnight to Jackson...')
        channel = discord.utils.find(lambda c: c.id == 222462913724547072, self.bot.get_all_channels())
        await channel.send('Goodnight Jackson')

    def shitpost_sub(self, string, regex):
        if regex not in self.word_list or not self.word_list[regex]:
            self.word_list[regex] = self.words[self.words["@replaces"][regex]][:]
        word = self.word_list[regex].pop(random.randrange(len(self.word_list[regex])))
        return re.sub("%" + regex, word, string, 1)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cat(self, ctx):
        """Get a random cat picture from random.cat"""
        if random.randint(0, 1) == 1:
            url = 'https://random.cat/meow'
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as r:
                    if r.status == 200:
                        js = await r.json()
                        await ctx.send(js['file'])
        else:
            cats = ['https://i.imgur.com/MWQb0Ow.jpg', 'https://i.imgur.com/0sQxWhX.jpg',
                    'https://i.imgur.com/jfnNyhN.jpg', 'https://i.imgur.com/PfjDURc.jpg',
                    'https://i.imgur.com/f3D8RHJ.jpg', 'https://i.imgur.com/pYzC7en.jpg',
                    'https://i.imgur.com/v7NNxjK.jpg', 'https://i.imgur.com/Wpj18Yi.jpg',
                    'https://i.imgur.com/Dcyq3Fs.jpg']
            url = random.choice(cats)

            await ctx.send(url)

    @commands.command()
    async def ud(self, ctx, *msg):
        """Search words on Urban Dictionary"""
        word = ' '.join(msg)
        api = "http://api.urbandictionary.com/v0/define"

        async with aiohttp.ClientSession() as session:
            async with session.get(api, params={'term': word}) as r:
                if r.status == 200:
                    response = await r.json()
                else:
                    return await ctx.send("Could not find that word!")

        embed = discord.Embed(title='Urban Dictionary - ' + word, color=0x00FF00)
        embed.description = response['list'][0]['definition']
        embed.set_thumbnail(
            url='https://images-ext-2.discordapp.net/external/B4lcjSHEDA8RcuizSOAdc92ithHovZT6WkRAX-da_6o/https/erisbot.com/assets/emojis/urbandictionary.png')
        embed.add_field(name="Examples:", value=response['list'][0]["example"][:253] + '...')
        embed.set_footer(text="Tags: " + ', '.join(response['tags']))

        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def shitpost(self, ctx):
        """Have the bot shitpost in chat."""
        # Shitpost code from https://github.com/yrsegal/shitpost
        if not self.bases:
            self.bases = self.words["@bases"]
        base = self.bases.pop(random.randrange(len(self.bases)))

        while "%" in base:
            if self.bot.dev:
                self.bot.logger.info(base)
            for regex in self.words["@replaces"]:
                base = self.shitpost_sub(base, regex)

        if self.bot.dev:
            self.bot.logger.info(base)
        self.words.reload()
        await ctx.send(base)

    @commands.command()
    @commands.cooldown(3, 60, commands.BucketType.user)
    async def feedme(self, ctx):
        """Feed your cat some spaghetti."""
        await ctx.send('https://i.imgur.com/MWQb0Ow.jpg')

    @commands.command()
    async def putjacksonindiamond(self, ctx):
        """He'll get there one day."""
        await ctx.send('https://i.imgur.com/xumheZ5.gif')


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
