from discord.ext import commands

from cogs.database import *


class Pick:
    """Pick a random hero or set of heroes."""

    def __init__(self, bot):
        self.bot = bot
        self.agora = self.bot.get_cog('Agora')  # Requires the Agora extension be loaded

    @commands.command(pass_context=True)
    async def pick(self, ctx):
        """Pick a random hero."""

        embed = discord.Embed()
        hero = self.agora.random_hero()
        embed.title = hero.hero_name
        embed.url = 'https://agora.gg/hero/' + hero.agora_hero_id
        embed.set_thumbnail(url=hero.icon)
        embed.set_footer(text='Paragon', icon_url=self.agora.icon_url)
        await self.bot.say(content=ctx.message.author.mention + ' Play:', embed=embed)

    @commands.command(pass_context=True)
    async def pick5(self, ctx):
        """Pick 5 random heroes."""
        embed = discord.Embed()
        picked = []
        heroes = ''
        while len(picked) < 5:
            hero = self.agora.random_hero()
            if hero.id in picked:
                continue
            picked.append(hero.id)
            if len(picked) < 5:
                heroes = heroes + hero.hero_name + ", " if len(picked) < 4 else heroes + hero.hero_name + ", and "
            else:
                heroes += hero.hero_name
        embed.title = heroes
        embed.url = 'https://agora.gg/heroes'
        embed.set_footer(text='Paragon', icon_url=self.agora.icon_url)
        await self.bot.say(embed=embed)

    @commands.command(pass_context=True)
    async def pick10(self, ctx, mirror: bool = False):
        """Pick 10 random heroes."""
        picked = []
        heroes = ''
        embed = discord.Embed()
        while len(picked) < 5:
            hero = self.agora.random_hero()
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
            hero = self.agora.random_hero()
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
        embed.set_footer(text='Paragon', icon_url=self.agora.icon_url)
        await self.bot.say(embed=embed)

    @commands.command(pass_context=True)
    async def pickteam(self, ctx):
        """Pick a team with proper roles for each lane."""
        roles = {'ADC': 'ADC', 'SUPP': 'Support', 'MID': 'Midlane', 'OFF': 'Offlane', 'JUNG': 'Jungle'}
        picked = []  # Some heroes can be played in multiple roles, we need to keep track
        embed = discord.Embed()
        embed.title = 'Team Picks'
        for role, name in roles.items():
            found = False
            while not found:
                hero = self.agora.role_hero(role)
                if hero.id in picked:
                    continue
                found = True
            picked.append(hero.id)
            embed.add_field(name=name, value=hero.hero_name, inline=False)
        await self.bot.say(embed=embed)

    @commands.command(pass_context=True, aliases=['pickadc'])
    async def pickcarry(self, ctx):
        """Pick a random ADC."""

        embed = discord.Embed()
        hero = self.agora.role_hero('ADC')
        embed.title = hero.hero_name
        embed.url = 'https://agora.gg/hero/' + hero.agora_hero_id
        embed.set_thumbnail(url=hero.icon)
        embed.set_footer(text='Paragon', icon_url=self.agora.icon_url)
        await self.bot.say(content=ctx.message.author.mention + ' Play:', embed=embed)

    @commands.command(pass_context=True)
    async def picksupport(self, ctx):
        """Pick a random Support."""

        embed = discord.Embed()
        hero = self.agora.role_hero('SUPP')
        embed.title = hero.hero_name
        embed.url = 'https://agora.gg/hero/' + hero.agora_hero_id
        embed.set_thumbnail(url=hero.icon)
        embed.set_footer(text='Paragon', icon_url=self.agora.icon_url)
        await self.bot.say(content=ctx.message.author.mention + ' Play:', embed=embed)

    @commands.command(pass_context=True)
    async def pickmid(self, ctx):
        """Pick a random Midlaner."""

        embed = discord.Embed()
        hero = self.agora.role_hero('MID')
        embed.title = hero.hero_name
        embed.url = 'https://agora.gg/hero/' + hero.agora_hero_id
        embed.set_thumbnail(url=hero.icon)
        embed.set_footer(text='Paragon', icon_url=self.agora.icon_url)
        await self.bot.say(content=ctx.message.author.mention + ' Play:', embed=embed)

    @commands.command(pass_context=True)
    async def pickoff(self, ctx):
        """Pick a random Offlaner."""

        embed = discord.Embed()
        hero = self.agora.role_hero('OFF')
        embed.title = hero.hero_name
        embed.url = 'https://agora.gg/hero/' + hero.agora_hero_id
        embed.set_thumbnail(url=hero.icon)
        embed.set_footer(text='Paragon', icon_url=self.agora.icon_url)
        await self.bot.say(content=ctx.message.author.mention + ' Play:', embed=embed)

    @commands.command(pass_context=True)
    async def pickjungle(self, ctx):
        """Pick a random jungler."""

        embed = discord.Embed()
        hero = self.agora.role_hero('JUNG')
        embed.title = hero.hero_name
        embed.url = 'https://agora.gg/hero/' + hero.agora_hero_id
        embed.set_thumbnail(url=hero.icon)
        embed.set_footer(text='Paragon', icon_url=self.agora.icon_url)
        await self.bot.say(content=ctx.message.author.mention + ' Play:', embed=embed)


def setup(bot):
    bot.add_cog(Pick(bot))
