import random

import discord
from discord.ext import commands

from API import AgoraAPI
from Database.database import *


class Pick:
    """Pick a random hero or set of heroes."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def pick(self, ctx):
        """Pick a random hero."""

        embed = discord.Embed()
        hero = Hero.get(Hero.id == random.randint(1, Hero.select().count()))
        embed.title = hero.hero_name
        embed.url = 'https://agora.gg/hero/' + hero.agora_hero_id
        embed.set_thumbnail(url=hero.icon)
        embed.set_footer(text='Paragon', icon_url=AgoraAPI.icon_url)
        await self.bot.send_message(ctx.message.channel, content=ctx.message.author.mention + ' Play:', embed=embed)

    @commands.command(pass_context=True)
    async def pick5(self, ctx):
        """Pick 5 random heroes."""
        embed = discord.Embed()
        picked = []
        heroes = ''
        while len(picked) < 5:
            hero = Hero.get(Hero.id == random.randint(1, Hero.select().count()))
            if hero.id in picked:
                continue
            picked.append(hero.id)
            if len(picked) < 5:
                heroes = heroes + hero.hero_name + ", " if len(picked) < 4 else heroes + hero.hero_name + ", and "
            else:
                heroes += hero.hero_name
        embed.title = heroes
        embed.url = 'https://agora.gg/heroes'
        embed.set_footer(text='Paragon', icon_url=AgoraAPI.icon_url)
        await self.bot.send_message(ctx.message.channel, embed=embed)

    @commands.command(pass_context=True)
    async def pick10(self, ctx, mirror: bool = False):
        """Pick 10 random heroes."""

        picked = []
