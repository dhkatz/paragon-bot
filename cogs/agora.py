import configparser
import math
import random
from datetime import datetime
from urllib.parse import quote

import peewee
import requests
from discord.ext import commands

from cogs.database import *
from .util.paginator import Pages, EmbedPages


class Agora:
    """Agora.gg related commands."""

    def __init__(self, bot):
        self.bot = bot
        self.hero_file = '{}/heroes.ini'.format('C:/Users/mcilu/PycharmProjects/Paragon-Discord-Bot/Database')
        self.icon_url = 'https://e-stats.io/src/images/games/paragon/logo-white-icon.png'
        self.heroes = configparser.ConfigParser()
        self.heroes.read(self.hero_file)

    def set_heroes(self):
        if 'hero' not in self.bot.db.get_tables():
            Hero.create_table()

        url = 'https://api.agora.gg/v1/gamedata/heroes?lc=en&ssl=true'

        try:
            with requests.get(url=url) as r:
                if r.status_code == 200:
                    js = r.json()
                    for hero in js:
                        lane = self.heroes[hero['slug']]['lane']
                        icon = self.heroes[hero['slug']]['icon']

                        new_hero, created = Hero.get_or_create(agora_hero_id=hero['id'], hero_name=hero['name'],
                                                               slug=hero['slug'],
                                                               type=hero['type'], attack=hero['attack'],
                                                               affinity1=hero['affinity1'],
                                                               affinity2=hero['affinity2'],
                                                               damage_type=hero['damageType'],
                                                               abilities=hero['abilities'], icon=icon,
                                                               agora_data_name=hero['code'], roles=lane)
                        new_hero.save()
        except Exception as e:
            self.bot.logger.exception(e)

    def set_cards(self):
        if 'card' not in self.bot.db.get_tables():
            Card.create_table()

        url = 'https://api.agora.gg/v2/cards'

        try:
            with requests.get(url=url) as r:
                js = r.json()
                for card in js:
                    levels = ''
                    trait = card['trait'] if 'trait' in card else None
                    gold_cost = card['goldCost'] if 'goldCost' in card else 0
                    intellect_cost = card['intellectGemCost'] if 'intellectGemCost' in card else 0
                    agility_cost = card['agilityGemCost'] if 'agilityGemCost' in card else 0
                    vitality_cost = card['vitalityGemCost'] if 'vitalityGemCost' in card else 0

                    for level in card['levels']:
                        levels = str(level['level']) + '|' + level['levelImage'] + '|'
                        for ability in level['abilities']:
                            levels += ability['name'] + ', ' + ability['description'] + '|'

                    new_card, created = Card.get_or_create(card_id=card['id'], card_name=card['name'],
                                                           rarity=card['rarity'], affinity=card['affinity'],
                                                           gold_cost=gold_cost, agility_cost=agility_cost,
                                                           vitality_cost=vitality_cost, intellect_cost=intellect_cost,
                                                           trait=trait, levels=levels)
                    new_card.save()
        except Exception as e:
            self.bot.logger.exception(e)

    def set_gems(self):
        if 'gem' not in self.bot.db.get_tables():
            Gem.create_table()

        url = 'https://api.agora.gg/v2/gems'

        try:
            with requests.get(url=url) as r:
                js = r.json()
                for gem in js:
                    new_gem, created = Gem.get_or_create(gem_name=gem['name'], gem_id=gem['id'],
                                                         template=gem['template'],
                                                         description=gem['description'], slot=gem['slot'],
                                                         stone=gem['stone'], shape=gem['shape'])
                    new_gem.save()
        except Exception as e:
            self.bot.logger.exception(e)

    @staticmethod
    def random_hero():
        """Get a random hero from the database."""
        hero = Hero.get(Hero.id == random.randint(1, Hero.select().count()))
        return hero

    @staticmethod
    def role_hero(role):
        hero = Hero.select().where(Hero.roles.contains(role)).order_by(fn.Random()).get()
        return hero

    @commands.command()
    async def elo(self, ctx):
        """Returns a player's elo by name from Agora.gg"""

        message = str(ctx.message.content).replace(self.bot.command_prefix + 'elo', '')

        # Command has specified a username
        if len(message) > 1:
            user = message.replace(' ', '', 1)
        else:
            try:
                # Player is stored in DB
                player = Player.get(Player.discord_id == ctx.author.id)
                user = player.player_name
            except peewee.DoesNotExist:
                if isinstance(ctx.author, discord.Member):
                    # Public channel message
                    user = ctx.author.nick if ctx.author.nick is not None else ctx.author.name
                else:
                    # Private channel. We have to pull by name or DB
                    user = ctx.author.name

        user_id = self.get_agora_player_id(username=user)
        if user_id == 'null':
            if len(message) > 1:
                await self.bot.embed_notify(ctx, 1, 'Error',
                                            'The user you entered does not exist, please re-check the name!')
            else:
                await self.bot.embed_notify(ctx, 1, 'Error',
                                            'Your discord account does not seem to be the same as your Paragon username, please find your IGN and use the command .elo <PlayerName>. Alternatively, tag your Epic ID to your Discord account by typing .ign <PlayerName>')
            return
        else:
            embed = self.get_agora_player_elo(user_id)
        await ctx.send(embed=embed)

    @commands.command()
    async def stats(self, ctx):
        """Returns a player's stats from Agora.gg"""

        message = str(ctx.message.content).replace(self.bot.command_prefix + 'stats', '')

        # Command has specified a username
        if len(message) > 1:
            user = message.replace(' ', '', 1)
        else:
            try:
                # Player is stored in DB
                player = Player.get(Player.discord_id == ctx.author.id)
                user = player.player_name
            except peewee.DoesNotExist:
                if isinstance(ctx.author, discord.Member):
                    # Public channel message
                    user = ctx.author.nick if ctx.author.nick is not None else ctx.author.name
                else:
                    # Private channel. We have to pull by name or DB
                    user = ctx.author.name

        user_id = self.get_agora_player_id(username=user)
        if user_id == 'null':
            if len(message) > 1:
                await self.bot.embed_notify(ctx, 1, 'Error',
                                            'The user you entered does not seem exist, please re-check the name!')
            else:
                await self.bot.embed_notify(ctx, 1, 'Error',
                                            'Your discord account does not seem to be the same as your Paragon username, please find your IGN and use the command .stats <PlayerName>. Alternatively, tag your Epic ID to your Discord account by typing .ign <PlayerName>')
            return
        else:
            embed = self.get_agora_player_stats(user_id)

        await ctx.send(embed=embed)

    @commands.command()
    async def lpg(self, ctx):
        """Get a player's last played game stats from Agora.gg"""

        message = str(ctx.message.content).replace(self.bot.command_prefix + 'lpg', '')

        # Command has specified a username
        if len(message) > 1:
            user = message.replace(' ', '', 1)
        else:
            try:
                # Player is stored in DB
                player = Player.get(Player.discord_id == ctx.author.id)
                user = player.player_name
            except peewee.DoesNotExist:
                if isinstance(ctx.author, discord.Member):
                    # Public channel message
                    user = ctx.author.nick if ctx.author.nick is not None else ctx.author.name
                else:
                    # Private channel. We have to pull by name or DB
                    user = ctx.author.name

        user_id = self.get_agora_player_id(username=user)
        if user_id == 'null':
            if len(message) > 1:
                await self.bot.embed_notify(ctx, 1, 'Error',
                                            'The user you entered does not seem exist, please re-check the name!')
            else:
                await self.bot.embed_notify(ctx, 1, 'Error',
                                            'Your discord account does not seem to be the same as your Paragon username, please find your IGN and use the command .lpg <PlayerName>. Alternatively, tag your Epic ID to your Discord account by typing .ign <PlayerName>')
            return
        else:
            embed = self.get_agora_player_latest_game_stats(user_id, 0)

        await ctx.send(embed=embed)

    @commands.command(aliases=['deck', 'd'])
    async def herodeck(self, ctx):
        """Returns top three hero decks from Agora.gg"""
        message = str(ctx.message.content).replace(self.bot.command_prefix + ctx.invoked_with, '')

        if len(message) > 1:
            hero = message.replace(' ', '', 1)
        else:
            await self.bot.embed_notify(ctx, 1, 'Error', 'You must specify a hero with this command!')
            return

        try:
            results = Hero.select().where(Hero.hero_name.contains(hero)).get()
        except peewee.DoesNotExist:
            await self.bot.embed_notify(ctx, 1, 'Error',
                                        'Hero does not exist, if the hero is new be patient and try again in a few days!')
            return
        p = EmbedPages(ctx, icon_url=self.icon_url, entries=tuple(
            self.get_agora_hero_deck(hero_name=results.hero_name, image=results.icon, num=i) for i in range(0, 3)))
        await p.paginate()

    @commands.command(aliases=['guide', 'g'])
    async def heroguide(self, ctx):
        """Returns top three hero guides from Agora.gg"""
        message = str(ctx.message.content).replace(self.bot.command_prefix + ctx.invoked_with, '')

        if len(message) > 1:
            hero = message.replace(' ', '', 1)
        else:
            await self.bot.embed_notify(ctx, 1, 'Error', 'You must specify a hero with this command!')
            return

        try:
            results = Hero.select().where(Hero.hero_name.contains(hero)).get()
        except peewee.DoesNotExist:
            await self.bot.embed_notify(ctx, 1, 'Error',
                                        'Hero does not exist, if the hero is new be patient and try again in a few days!')
            return
        p = EmbedPages(ctx, icon_url=self.icon_url, entries=tuple(
            self.get_agora_hero_guide(hero_id=results.agora_data_name, image=results.icon, num=i) for i in range(0, 3)))
        await p.paginate()

    @commands.command()
    async def card(self, ctx, *args):
        """Returns information on a card or multiple cards. Surround a card name with quotes."""
        for search in args:
            results = Card.select().where(Card.card_name == search).count()
            if results == 1:
                embed = self.build_card(search)
            else:
                results = Card.select().where(Card.card_name.contains(search))
                if results.count() > 1:
                    p = EmbedPages(ctx, icon_url=self.icon_url,
                                   entries=tuple(self.build_card(card.card_name) for card in results))
                    await p.paginate()
                    return
                elif results.count() == 0:
                    await self.bot.embed_notify(ctx, 1, 'Error', 'The card you are searching for does not exist!')
                    return
                else:
                    embed = self.build_card(search)
            await ctx.send(embed=embed)

    @commands.command()
    async def cards(self, ctx):
        """Lists all cards in Paragon."""
        try:
            rows = Card.select()
            p = Pages(ctx, entries=tuple(card.card_name for card in rows))
            p.embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            await p.paginate()
        except Exception as e:
            await ctx.send(e)

    @commands.command()
    async def gem(self, ctx, *args):
        """Returns information on a gem or multiple gems. Surround a gem name with quotes."""
        for search in args:
            results = Gem.select().where(Gem.gem_name == search).count()
            if results == 1:
                embed = self.build_gem(search)
            else:
                results = Gem.select().where(Gem.gem_name.contains(search))
                if results.count() > 1:
                    p = EmbedPages(ctx, icon_url=self.icon_url,
                                   entries=tuple(self.build_gem(gem.gem_name) for gem in results))
                    await p.paginate()
                    return
                elif results.count() == 0:
                    await self.bot.embed_notify(ctx, 1, 'Error', 'The gem you are searching for does not exist!')
                    return
                else:
                    embed = self.build_gem(search)
            await ctx.send(embed=embed)

    @commands.command()
    async def ign(self, ctx, epic_id: str = ''):
        """Tag your Paragon IGN to your Discord account. Surround names with spaces in quotes. Empty to see current."""
        embed = discord.Embed()
        if len(epic_id) > 0:
            player_id = self.get_agora_player_id(epic_id)

            if player_id != 'null':
                player_elo = self.get_raw_elo(player_id)
            else:
                await self.bot.embed_notify(ctx, 1, 'Error',
                                            'The Epic ID you entered does not exist! Remember names with spaces need quotes!')
                return

            try:
                player = Player.get(Player.discord_id == ctx.author.id)
                player.player_name = epic_id
                player.save()
                await self.bot.embed_notify(ctx, 0, 'Epic ID Updated', 'You have updated your Epic ID!')
            except peewee.DoesNotExist:
                player = Player(agora_player_id=player_id, discord_id=ctx.author.id, player_name=epic_id,
                                elo=player_elo, team_id=None)
                player.save()
                await self.bot.embed_notify(ctx, 0, 'Epic ID Updated',
                                            'You have attached your Epic ID to your Discord ID!')
        else:
            # User is requesting their current ID!
            try:
                player = Player.get(Player.discord_id == ctx.author.id)
                embed.title = 'Current Epic ID'
                embed.colour = discord.Colour.blue()
                embed.description = player.player_name
                embed.url = 'https://agora.gg/profile/' + player.agora_player_id + '/' + quote(player.player_name,
                                                                                               safe='')
                embed.set_footer(text='Paragon', icon_url=self.icon_url)
                await ctx.send(embed=embed)
            except peewee.DoesNotExist:
                await self.bot.embed_notify(ctx, 1, 'Error',
                                            'No player name specified and no Epic ID was found linked to your account!\n(See \'' + self.bot.command_prefix + 'help ign\' for more command information!)')

    def get_agora_player_id(self, username):
        url = 'https://api.agora.gg/v1/players/search?name=' + username
        player_id = 'null'
        try:
            with requests.get(url=url) as r:
                if r.status_code == 200:
                    js = r.json()
                    if js:
                        player_id = str(js[0]['id'])
        except Exception as e:
            self.bot.logger.exception(e)
        return player_id

    def get_raw_elo(self, player_id):
        """Get a player's elo and ranking as a Discord embed from a Agora.gg"""
        url = 'https://api.agora.gg/v1/players/' + player_id + '?lc=en&ssl=true'
        player_elo = 0
        try:
            with requests.get(url=url) as r:
                if r.status_code == 200:
                    js = r.json()
                    if not js['privacyEnabled'] or str(js['privacyEnabled']) == '':
                        if 'stats' in js:
                            for stat in js['stats']:
                                if stat['mode'] == 4:
                                    player_elo = str(math.floor(stat['elo']))
        except Exception as e:
            self.bot.logger.exception(e)
        return player_elo

    def get_agora_player_elo(self, player_id):
        """Get a player's elo and ranking as a Discord embed from a Agora.gg"""
        url = 'https://api.agora.gg/v1/players/' + player_id + '?lc=en&ssl=true'
        embed = discord.Embed()

        try:
            with requests.get(url=url) as r:
                if r.status_code == 200:
                    js = r.json()
                    player_name = str(js['name'])
                    if not js['privacyEnabled'] or str(js['privacyEnabled']) == '':
                        if 'stats' in js:
                            for stat in js['stats']:
                                info = ''
                                if stat['mode'] == 4:
                                    elo = math.floor(stat['elo'])
                                    info += "Elo: " + str(elo) + '\n'

                                    rank = str(stat['rank']) if 'rank in stat' else 'No Rank'
                                    info += "Rank: " + rank + '\n'

                                    top = str(
                                        round(stat['percentile'], 2)) + '%' if 'percentile' in stat else 'No percent.'
                                    info += "Top: " + top + '\n'

                                    embed.title = player_name
                                    embed.url = 'https://agora.gg/profile/' + player_id + '/' + quote(player_name,
                                                                                                      safe='')
                                    embed.description = info
                                    embed.set_footer(text='Paragon', icon_url=self.icon_url)
                        else:
                            embed.title = 'Error'
                            embed.colour = discord.Colour.dark_red()
                            embed.description = 'There seems to be no data for this account. Please re-check the name.'
                            embed.set_footer(text='Paragon', icon_url=self.icon_url)
                    else:
                        embed.title = 'Error'
                        embed.colour = discord.Colour.dark_red()
                        embed.description = 'This account has been set to private!'
                        embed.set_footer(text='Paragon', icon_url=self.icon_url)
        except Exception as e:
            self.bot.logger.exception(e)
        return embed

    def get_agora_player_stats(self, player_id):
        """Get the overall stats of a player as a Discord embed from Agora.gg"""
        url = 'https://api.agora.gg/v1/players/' + player_id + '?lc=en&ssl=true'
        embed = discord.Embed()

        try:
            with requests.get(url=url) as r:
                if r.status_code == 200:
                    js = r.json()
                    if not js['privacyEnabled'] or str(js['privacyEnabled']) == '':
                        player_name = str(js['name'])
                        if 'stats' in js:
                            for stat in js['stats']:
                                if stat['mode'] == 4:
                                    loss = stat['gamesPlayed'] - stat['wins']
                                    percentage = (stat['wins'] / (stat['wins'] + loss)) * 100

                                    k = stat['kills']
                                    d = stat['deaths']
                                    a = stat['assists']
                                    kda_percent = (k + a) / max(1, d)

                                    embed.title = player_name
                                    embed.url = 'https://agora.gg/profile/' + player_id + '/' + quote(player_name,
                                                                                                      safe='') + ''
                                    embed.description = "Games Played " + str(stat['gamesPlayed'])
                                    embed.add_field(name='Win/Loss/Rate',
                                                    value='{0}/{1}/({2}%)'.format(str(stat['wins']), str(loss), str(
                                                        round(percentage, 3))), inline=True)
                                    embed.add_field(name='KDA',
                                                    value='{0}/{1}/{2} ({3})'.format(str(k), str(d), str(a),
                                                                                     str(round(kda_percent, 2))))
                                    embed.add_field(name='Towers', value=str(stat['towers']), inline=True)
                                    embed.set_footer(text='Paragon', icon_url=self.icon_url)
                        else:
                            embed.title = 'Error'
                            embed.colour = discord.Colour.dark_red()
                            embed.description = 'There seems to be no data for this account. Please re-check the name.'
                            embed.set_footer(text='Paragon', icon_url=self.icon_url)
                    else:
                        embed.title = 'Notice'
                        embed.colour = discord.Colour.dark_red()
                        embed.description = 'This account is set to private'
                        embed.set_footer(text='Paragon', icon_url=self.icon_url)
        except Exception as e:
            self.bot.logger.exception(e)

        return embed

    def get_agora_hero_info(self, hero_id, image):
        """Get information for a specified hero and return a Discord embed object."""
        url = 'https://api.agora.gg/v1/gamedata/heroes/' + hero_id + '?lc=en&ssl=true'
        embed = discord.Embed()

        try:
            with requests.get(url=url) as r:
                if r.status_code == 200:
                    js = r.json()
                    embed.title = str(js['name'])
                    embed.url = 'https://agora.gg/hero/' + str(js['name']).lower() + ''
                    embed.set_thumbnail(url=image)
                    embed.add_field(name='Affinity', value=js['affinity1'] + ' | ' + js['affinity2'])
                    embed.add_field(name='Damage/Type', value=js['attack'] + ' | ' + js['damageType'])
                    embed.set_footer(text='Paragon', icon_url=self.icon_url)
        except Exception as e:
            self.bot.logger.exception(e)

        return embed

    def get_agora_hero_deck(self, hero_name, image, num):
        """Get the most popular decks on Agora.gg for a hero and return a Discord embed object."""
        url = 'https://api.agora.gg/v2/decks?tag=' + quote(hero_name, safe='') + '&sort=-votes&major=1&lc=en&ssl=true'
        embed = discord.Embed(colour=discord.Colour.blue())

        try:
            with requests.get(url=url) as r:
                if r.status_code == 200:
                    js = r.json()
                    embed.title = js[num]['name']
                    embed.url = 'https://agora.gg/deck/' + str(js[num]['id']) + '/' + quote(hero_name, safe='') + ''
                    embed.set_thumbnail(url=image)
                    embed.description = js[num]['description']
                    embed.add_field(name='Patch', value=js[num]['patch'])
                    embed.add_field(name='Votes', value=js[num]['votes'])
                    embed.set_footer(text='Paragon', icon_url=self.icon_url)
        except Exception as e:
            self.bot.logger.exception(e)
        return embed

    def get_agora_hero_guide(self, hero_id, image, num):
        """Get a guide for a specific hero from Agora.gg"""
        url = 'https://api.agora.gg/v1/guides?name=&hero=' + hero_id + '&role=&page=0&sort=votes&&lc=en&ssl=true'
        embed = discord.Embed(colour=discord.Colour.blue())

        try:
            with requests.get(url=url) as r:
                if r.status_code == 200:
                    js = r.json()
                    embed.title = js['data'][num]['name']
                    embed.url = 'https://agora.gg/guide/' + str(js['data'][num]['id'])
                    embed.set_thumbnail(url=image)
                    embed.add_field(name='Votes', value=js['data'][num]['votes'])
                    embed.add_field(name='Role', value=js['data'][num]['role'])
                    embed.add_field(name='Author', value=js['data'][num]['playerName'] + ' (Elo: ' + str(
                        round(js['data'][num]['elo'], 2)) + ')')
                    embed.set_footer(text='Paragon', icon_url=self.icon_url)
        except Exception as e:
            self.bot.logger.exception(e)

        return embed

    def get_agora_player_latest_game_stats(self, player_id, num):
        """Get the stats of a player's most recent game."""
        now = datetime.now()
        now = now.replace(day=1)
        start_year = str(now.replace(month=now.month - 3).year)
        start_month = str(now.replace(month=now.month - 3).month)
        end_year = str(now.replace(month=now.month + 1).year)
        end_month = str(now.replace(month=now.month + 1).month)
        end_day = str(now.replace(month=now.month + 1).day)

        url = 'https://api.agora.gg/v1/players/' + player_id + '/history/match?page=0&start=' + start_year + '-'
        url += start_month + '-01T00:00:00Z&end=' + end_year + '-' + end_month + '-' + end_day + 'T00:00:00Z&lc=en&ssl=true'
        embed = discord.Embed()

        try:
            with requests.get(url=url) as r:
                if r.status_code == 200:
                    js = r.json()

                    if len(js) != 0:
                        time = js[num]['length']
                        final_time = str(math.floor(time / 60))
                        seconds = str((time % 3600) - (math.floor(time / 60) * 60))
                        for i in range(2):
                            for player in js[num]['teams'][i]:
                                if str(player['id']) == player_id:
                                    winning_team = 'Won' if js[num]['winningTeam'] == i else 'Lost'

                                    k = player['kills']
                                    d = player['deaths']
                                    a = player['assists']
                                    kda_percent = k + a
                                    kda_percent = kda_percent / max(1, d)

                                    embed.title = 'Game Played: ' + js[num][
                                        'createdAt'].split('T')[0] + ' (UTC)' + ' Time: ' + final_time + ':' + seconds
                                    embed.url = 'https://agora.gg/game/' + js[num]['id']
                                    embed.colour = discord.Colour.green() if winning_team == 'Won' else discord.Colour.dark_red()
                                    hero = Hero.select().where(Hero.agora_data_name % player['hero']).get()
                                    embed.description = 'Played as ' + hero.hero_name + '. Level ' + str(
                                        player['level']) + '. Player has played ' + str(
                                        player['heroGamesPlayed']) + ' games with this hero.'
                                    embed.add_field(name='Result', value=winning_team)
                                    embed.add_field(name='KDA',
                                                    value=str(k) + '/' + str(d) + '/' + str(a) + ' (' + str(
                                                        round(kda_percent, 2)) + ')')
                                    embed.add_field(name='Towers', value=player['towers'])
                                    embed.add_field(name='Hero DMG', value=player['heroDamage'])
                                    embed.add_field(name='Minion DMG', value=player['minionDamage'])
                                    embed.add_field(name='Jungle DMG', value=player['jungleDamage'])
                                    embed.add_field(name='Replay ID: ', value=js[num]['id'], inline=False)
                                    embed.set_footer(text='Paragon', icon_url=self.icon_url)
                                    break
                    else:
                        embed.title = 'Error'
                        embed.colour = discord.Colour.dark_red()
                        embed.description = 'There was no last played game data found!'
                        embed.set_footer(text='Paragon', icon_url=self.icon_url)
        except Exception as e:
            self.bot.logger.exception(e)

        return embed

    def get_agora_player_current_game(self, player_id: str, team: int):
        """Get the stats of a player's current game."""
        url = 'https://api.agora.gg/v1/games/now/' + player_id + '?lc=en&ssl=true'
        info = []

        try:
            with requests.get(url=url) as r:
                if r.status_code == 200:
                    js = r.json()

                    if str(js).replace('[]', 'null') != 'null':
                        info.append(f'**Team {team + 1}**\n')
                        for player in js['teams'][team]:
                            hero = Hero.select().where(Hero.agora_data_name % player['hero']).get()
                            info.append(player['name'] + ' (' + hero.hero_name + ') | Elo:' + str(player['elo']))
                            info.append(' | Lvl: ' + str(player['level']) + ' | KDA: (' + str(player['kills']))
                            info.append('/' + str(player['deaths']) + '/' + str(player['assists']) + ')\n')
                            info.append('\n')
                        info.append('Replay ID: ' + js['id'] + '\n')
                    else:
                        info.append('[]23?>\n')
        except Exception as e:
            self.bot.logger.exception(e)
        return ''.join(info)

    def build_card(self, card):
        """Build a Discord embed for a card and return it."""
        embed = discord.Embed()

        if Card.select().where(Card.card_name == card).count() > 0:
            result = Card.select().where(Card.card_name == card).get()
        else:
            result = Card.select().where(Card.card_name.contains(card)).get()

        embed.title = result.card_name
        embed.colour = AFFINITY_MAP[result.affinity]
        embed.description = result.affinity + ' | ' + result.rarity
        if result.trait is not None:
            embed.add_field(name='**' + result.trait + '**', value=TRAIT_MAP[result.trait], inline=False)
        for effect in result.levels.split('|')[2:]:
            if len(effect) > 0:
                embed.add_field(name=effect.split(',', 1)[0], value=effect.split(',', 1)[1], inline=False)
        url = 'https://static.agora.gg/cards2/' + result.card_name.replace(' ', '').replace('-', '').replace('\'',
                                                                                                             '').lower() + '-275.jpg'
        print(url)
        embed.set_thumbnail(url=url)
        embed.set_footer(text='Paragon', icon_url=self.icon_url)
        return embed

    def build_gem(self, gem):
        """Build a Discord embed for a gem and return it."""
        embed = discord.Embed()

        if Gem.select().where(Gem.gem_name == gem).count() > 0:
            result = Gem.select().where(Gem.gem_name == gem).get()
        else:
            result = Gem.select().where(Gem.gem_name.contains(gem)).get()

        embed.title = result.gem_name
        embed.colour = STONE_MAP[result.stone]
        embed.description = result.description
        embed.add_field(name='**Stone**', value=result.stone)
        embed.add_field(name='**Slot**', value=str(result.slot))
        embed.add_field(name='**Shape**', value=result.shape)
        # embed.set_thumbnail(url='https://agora.gg/assets/image/deck/' + result.stone + '-' + result.shape + '.png')
        embed.set_footer(text='Paragon', icon_url=self.icon_url)
        return embed


AFFINITY_MAP = {'Chaos': discord.Colour.dark_red(), 'Order': discord.Colour.gold(), 'Growth': discord.Colour.green(),
                'Knowledge': discord.Colour.blue(), 'Death': discord.Colour.dark_purple()}
STONE_MAP = {'Agility': discord.Colour.orange(), 'Intellect': discord.Colour.purple(),
             'Vitality': discord.Colour.green()}

TRAIT_MAP = {'Cultivate': 'Gold cost is reduced per attribute point purchased.',
             'Elevate': 'Increases effectiveness of passive per attribute point purchased.',
             'Combustible': 'Effect disappears upon death', 'Cursed': 'Card cannot be unequipped.',
             'Consumable': 'Card is removed after activation.'}


class Hero(BaseModel):
    agora_hero_id = CharField(unique=True)
    hero_name = CharField()
    slug = CharField()
    type = CharField()
    attack = CharField()
    affinity1 = CharField()
    affinity2 = CharField()
    damage_type = CharField()
    abilities = CharField(null=True)
    icon = CharField()
    agora_data_name = CharField()
    roles = CharField()


class Card(BaseModel):
    card_id = CharField(unique=True)  # Unique Card ID
    card_name = CharField()
    rarity = CharField()
    affinity = CharField()
    trait = CharField(null=True)
    gold_cost = IntegerField(default=0)
    agility_cost = SmallIntegerField(default=0)
    vitality_cost = SmallIntegerField(default=0)
    intellect_cost = SmallIntegerField(default=0)
    levels = CharField()
    icon = CharField()


class Gem(BaseModel):
    gem_id = CharField(unique=True)  # Unique Gem ID
    gem_name = CharField()
    template = CharField()
    description = TextField()
    slot = SmallIntegerField()
    stone = CharField()
    shape = CharField()


def setup(bot):
    bot.add_cog(Agora(bot))
