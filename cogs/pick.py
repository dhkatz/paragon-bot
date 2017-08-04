import random

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
        heroes = ''
        embed = discord.Embed()
        while len(picked) < 5:
            hero = Hero.get(Hero.id == random.randint(1, Hero.select().count()))
            if hero.id in picked:
                continue
            picked.append(hero.id)
            if len(picked) < 5:
                heroes = heroes + hero.hero_name + ", " if len(picked) < 4 else heroes + hero.hero_name + ", and "
            else:
                heroes += hero.hero_name + '|'
        if mirror:
            picked.clear()
        size = len(picked)
        while len(picked) < size + 5:
            hero = Hero.get(Hero.id == random.randint(1, Hero.select().count()))
            if hero.id in picked:
                continue
            picked.append(hero.id)
            if len(picked) < size + 5:
                heroes = heroes + hero.hero_name + ", " if len(
                    picked) < size + 4 else heroes + hero.hero_name + ", and "
            else:
                heroes += hero.hero_name + '|'
        embed.title = heroes.split('|')[0]
        embed.description = heroes.split('|')[1]
        embed.url = 'https://agora.gg/heroes'
        embed.set_footer(text='Paragon', icon_url=AgoraAPI.icon_url)
        await self.bot.send_message(ctx.message.channel, embed=embed)

    @commands.command(pass_context=True)
    async def pickteam(self, ctx):
        """Pick a team with proper roles for each lane."""
        roles = {'ADC': 'ADC', 'SUPP': 'Support', 'MID': 'Midlane', 'OFF': 'Offlane', 'JUNG': 'Jungle'}
        picked = []  # Some heroes can be played in multiple roles, we need to keep track
        embed = discord.Embed()
        embed.title = 'Team Picks'
        for role, name in roles.items():
            hero = Hero.select().where(Hero.roles.contains(role) & Hero.id.not_in(picked)).order_by(fn.Random()).get()
            picked.append(hero.id)
            embed.add_field(name=name, value=hero.hero_name, inline=False)
        await self.bot.send_message(ctx.message.channel, embed=embed)

    @commands.command(pass_context=True, aliases=['pickadc'])
    async def pickcarry(self, ctx):
        """Pick a random ADC."""

        embed = discord.Embed()
        hero = Hero.select().where(Hero.roles.contains('ADC')).order_by(fn.Random()).get()
        embed.title = hero.hero_name
        embed.url = 'https://agora.gg/hero/' + hero.agora_hero_id
        embed.set_thumbnail(url=hero.icon)
        embed.set_footer(text='Paragon', icon_url=AgoraAPI.icon_url)
        await self.bot.send_message(ctx.message.channel, content=ctx.message.author.mention + ' Play:', embed=embed)

    @commands.command(pass_context=True)
    async def picksupport(self, ctx):
        """Pick a random Support."""

        embed = discord.Embed()
        hero = Hero.select().where(Hero.roles.contains('SUPP')).order_by(fn.Random()).get()
        embed.title = hero.hero_name
        embed.url = 'https://agora.gg/hero/' + hero.agora_hero_id
        embed.set_thumbnail(url=hero.icon)
        embed.set_footer(text='Paragon', icon_url=AgoraAPI.icon_url)
        await self.bot.send_message(ctx.message.channel, content=ctx.message.author.mention + ' Play:', embed=embed)

    @commands.command(pass_context=True)
    async def pickmid(self, ctx):
        """Pick a random Midlaner."""

        embed = discord.Embed()
        hero = Hero.select().where(Hero.roles.contains('MID')).order_by(fn.Random()).get()
        embed.title = hero.hero_name
        embed.url = 'https://agora.gg/hero/' + hero.agora_hero_id
        embed.set_thumbnail(url=hero.icon)
        embed.set_footer(text='Paragon', icon_url=AgoraAPI.icon_url)
        await self.bot.send_message(ctx.message.channel, content=ctx.message.author.mention + ' Play:', embed=embed)

    @commands.command(pass_context=True)
    async def pickoff(self, ctx):
        """Pick a random Offlaner."""

        embed = discord.Embed()
        hero = Hero.select().where(Hero.roles.contains('OFF')).order_by(fn.Random()).get()
        embed.title = hero.hero_name
        embed.url = 'https://agora.gg/hero/' + hero.agora_hero_id
        embed.set_thumbnail(url=hero.icon)
        embed.set_footer(text='Paragon', icon_url=AgoraAPI.icon_url)
        await self.bot.send_message(ctx.message.channel, content=ctx.message.author.mention + ' Play:', embed=embed)

    @commands.command(pass_context=True)
    async def pickjungle(self, ctx):
        """Pick a random jungler."""

        embed = discord.Embed()
        hero = Hero.select().where(Hero.roles.contains('JUNG')).order_by(fn.Random()).get()
        embed.title = hero.hero_name
        embed.url = 'https://agora.gg/hero/' + hero.agora_hero_id
        embed.set_thumbnail(url=hero.icon)
        embed.set_footer(text='Paragon', icon_url=AgoraAPI.icon_url)
        await self.bot.send_message(ctx.message.channel, content=ctx.message.author.mention + ' Play:', embed=embed)


def setup(bot):
    bot.add_cog(Pick(bot))
