import random

import discord
from discord.ext import commands

from API import AgoraAPI
from Database.database import *


class Pick:
    """Pick a random hero or set of heroes from Agora."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def pick(self, ctx):
        embed = discord.Embed()

        hero = Hero.get(Hero.id == random.randint(1, Hero.select().count() + 1))
        embed.title = hero.hero_name
        embed.url = 'https://agora.gg/hero/' + hero.agora_hero_id
        embed.set_thumbnail(url=hero.icon)
        embed.set_footer(text='Paragon', icon_url=AgoraAPI.icon_url)
        await self.bot.send_message(ctx.message.channel, embed=embed)
