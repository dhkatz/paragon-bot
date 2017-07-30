from urllib.parse import quote

import peewee
from discord.ext import commands

from Util.utility import *


class Agora:
    """Agora.gg related commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def elo(self, ctx):
        """Returns a player's elo by name from Agora.gg"""
        print(ctx.message.server.name + ' called by: ' + ctx.message.author.name)

        embed = discord.Embed()
        message = str(ctx.message.content).replace(self.bot.command_prefix + 'elo', '')

        # Command has specified a username
        if len(message) > 1:
            user = message.replace(' ', '', 1)
        else:
            try:
                Player.get(Player.discord_id == str(ctx.message.author).split('#')[1])
                # Player is stored in DB
                player = Player.select().where(Player.discord_id == str(ctx.message.author).split('#')[1]).get()
                user = player.player_name
            except peewee.DoesNotExist:
                if isinstance(ctx.message.author, discord.Member):
                    # Public channel message
                    user = ctx.message.author.nick if ctx.message.author.nick is not None else ctx.message.author.name
                else:
                    # Private channel. We have to pull by name or DB
                    user = ctx.message.author.name

        user_id = AgoraAPI.get_agora_player_id(username=user)
        if user_id == 'null':
            if len(message) > 1:
                embed.title = 'Error'
                embed.description = 'The user you entered does not seem exist, please re-check the name!'
                embed.set_footer(text='Paragon', icon_url=AgoraAPI.icon_url)
            else:
                embed.title = 'Error'
                embed.description = 'Your discord account does not seem to be the same as your Paragon username, please find you IGN and use the command .elo <PlayerName>. Tired of typing your name everytime? use .ign <PlayerName> to tag your Pragon name to your Discord name. Once tagged just use .elo!'
                embed.set_footer(text='Paragon', icon_url=AgoraAPI.icon_url)
        else:
            embed = AgoraAPI.get_agora_player_elo(user_id)
        await self.bot.send_message(ctx.message.channel, embed=embed)

    @commands.command(pass_context=True)
    async def stats(self, ctx):
        """Returns a player's stats from Agora.gg"""
        print(ctx.message.server.name + ' called by: ' + ctx.message.author.name)

        embed = discord.Embed()
        message = str(ctx.message.content).replace(self.bot.command_prefix + 'stats', '')

        # Command has specified a username
        if len(message) > 1:
            user = message.replace(' ', '', 1)
        else:
            try:
                Player.get(Player.discord_id == str(ctx.message.author).split('#')[1])
                # Player is stored in DB
                player = Player.select().where(Player.discord_id == str(ctx.message.author).split('#')[1]).get()
                user = player.player_name
            except peewee.DoesNotExist:
                if isinstance(ctx.message.author, discord.Member):
                    # Public channel message
                    user = ctx.message.author.nick if ctx.message.author.nick != None else ctx.message.author.name
                else:
                    # Private channel. We have to pull by name or DB
                    user = ctx.message.author.name

        user_id = AgoraAPI.get_agora_player_id(username=user)
        if user_id == 'null':
            if len(message) > 1:
                embed.title = 'Error'
                embed.description = 'The user you entered does not seem exist, please re-check the name!'
                embed.set_footer(text='Paragon', icon_url=AgoraAPI.icon_url)
            else:
                embed.title = 'Error'
                embed.description = 'Your discord account does not seem to be the same as your Paragon username, please find you IGN and use the command .elo <PlayerName>. Tired of typing your name everytime? use .ign <PlayerName> to tag your Pragon name to your Discord name. Once tagged just use .elo!'
                embed.set_footer(text='Paragon', icon_url=AgoraAPI.icon_url)
        else:
            embed = AgoraAPI.get_agora_player_stats(user_id)

        await self.bot.send_message(ctx.message.channel, embed=embed)

    @commands.command(pass_context=True)
    async def lpg(self, ctx):
        """Get a player's last played game stats from Agora.gg"""
        print(ctx.message.server.name + ' called by: ' + ctx.message.author.name)

        embed = discord.Embed()
        message = str(ctx.message.content).replace(self.bot.command_prefix + 'lpg', '')

        # Command has specified a username
        if len(message) > 1:
            user = message.replace(' ', '', 1)
        else:
            try:
                Player.get(Player.discord_id == str(ctx.message.author).split('#')[1])
                # Player is stored in DB
                player = Player.select().where(Player.discord_id == str(ctx.message.author).split('#')[1]).get()
                user = player.player_name
            except peewee.DoesNotExist:
                if isinstance(ctx.message.author, discord.Member):
                    # Public channel message
                    user = ctx.message.author.nick if ctx.message.author.nick != None else ctx.message.author.name
                else:
                    # Private channel. We have to pull by name or DB
                    user = ctx.message.author.name

        user_id = AgoraAPI.get_agora_player_id(username=user)
        if user_id == 'null':
            if len(message) > 1:
                embed.title = 'Error'
                embed.description = 'The user you entered does not seem exist, please re-check the name!'
                embed.set_footer(text='Paragon', icon_url=AgoraAPI.icon_url)
            else:
                embed.title = 'Error'
                embed.description = 'Your discord account does not seem to be the same as your Paragon username, please find you IGN and use the command .elo <PlayerName>. Tired of typing your name every time? use .ign <PlayerName> to tag your Paragon name to your Discord name. Once tagged just use .elo!'
                embed.set_footer(text='Paragon', icon_url=AgoraAPI.icon_url)
        else:
            embed = AgoraAPI.get_agora_player_latest_game_stats(user_id, 0)

        await self.bot.send_message(ctx.message.channel, embed=embed)

    @commands.command(pass_context=True, aliases=['deck', 'd'])
    async def herodeck(self, ctx):
        """Returns top three hero decks from Agora.gg"""
        print(ctx.message.server.name + ' called by: ' + ctx.message.author.name)

        embed = discord.Embed()
        message = str(ctx.message.content).replace(self.bot.command_prefix + ctx.invoked_with, '')

        if len(message) > 1:
            hero = message.replace(' ', '', 1)
        else:
            embed.title = 'Error'
            embed.description = 'You must specify a hero with this command!'
            embed.set_footer(text='Paragon', icon_url=AgoraAPI.icon_url)
            await self.bot.send_message(ctx.message.channel, embed=embed)
            return

        try:
            results = Hero.select().where(Hero.hero_name.contains(hero)).get()
        except peewee.DoesNotExist:
            embed.title = 'Error'
            embed.description = 'Hero does not exist, if the hero is new be patient and try again in a few days!'
            embed.set_footer(text='Paragon', icon_url=AgoraAPI.icon_url)
            await self.bot.send_message(ctx.message.channel, embed=embed)
            return

        for i in range(0, 3):
            embed = AgoraAPI.get_agora_hero_deck(hero_id=results.agora_hero_id, image=results.icon, num=i)
            await self.bot.send_message(ctx.message.channel, embed=embed)

    @commands.command(pass_context=True, aliases=['guide', 'g'])
    async def heroguide(self, ctx):
        """Returns top three hero guides from Agora.gg"""
        print(ctx.message.server.name + ' called by: ' + ctx.message.author.name)

        embed = discord.Embed()
        message = str(ctx.message.content).replace(self.bot.command_prefix + ctx.invoked_with, '')

        if len(message) > 1:
            hero = message.replace(' ', '', 1)
        else:
            embed.title = 'Error'
            embed.description = 'You must specify a hero with this command!'
            embed.set_footer(text='Paragon', icon_url=AgoraAPI.icon_url)
            return embed

        try:
            HERO_DB.connect()
            results = Hero.select().where(Hero.hero_name.contains(hero)).get()
            HERO_DB.close()
        except peewee.DoesNotExist:
            embed.title = 'Error'
            embed.description = 'Hero does not exist, if the hero is new be patient and try again in a few days!'
            embed.set_footer(text='Paragon', icon_url=AgoraAPI.icon_url)
            await self.bot.send_message(ctx.message.channel, embed=embed)
            return

        for i in range(0, 3):
            embed = AgoraAPI.get_agora_hero_deck(hero_id=results.agora_hero_id, image=results.icon, num=i)
            await self.bot.send_message(ctx.message.channel, embed=embed)

    @commands.command(pass_context=True)
    async def card(self, ctx, *args):
        """Returns information on a card or multiple cards. Surround a card name with quotes."""
        for search in args:
            embed = discord.Embed()
            results = Card.select().where(Card.card_name == search).count()
            if results == 1:
                embed = build_card(search)
            else:
                results = Card.select().where(Card.card_name.contains(search))
                if results.count() > 1:
                    description = ''
                    for result in results:
                        description += '[' + result.card_name + '](https://agora.gg/card/' + result.card_id + ')\n'
                    embed.title = 'Multiple Cards Found!'
                    embed.description = description
                    embed.set_footer(text='Paragon', icon_url=AgoraAPI.icon_url)
                elif results.count() == 0:
                    embed.title = 'Error'
                    embed.description = 'The card you are searching for does not exist!'
                    embed.set_footer(text='Paragon', icon_url=AgoraAPI.icon_url)
                else:
                    embed = build_card(search)
            await self.bot.send_message(ctx.message.channel, embed=embed)

    @commands.command(pass_context=True)
    async def ign(self, ctx, epic_id: str = ''):
        """Tag your Paragon IGN to your Discord account. Surround names with spaces in quotes. Empty to see current."""
        user = str(ctx.message.author).split('#')
        embed = discord.Embed()
        if len(epic_id) > 0:
            player_id = AgoraAPI.get_agora_player_id(epic_id)

            if player_id != 'null':
                player_elo = AgoraAPI.get_raw_elo(player_id)
            else:
                embed.title = 'Error'
                embed.description = 'The Epic ID you entered does not exist! Remember names with spaces need quotes!'
                embed.set_footer(text='Paragon', icon_url=AgoraAPI.icon_url)
                await self.bot.send_message(ctx.message.channel, embed=embed)
                return

            try:
                player = Player.get(Player.discord_id == user[1]).get()
                player.player_name = epic_id
                player.save()
                embed.title = 'Success'
                embed.set_footer(text='Paragon', icon_url=AgoraAPI.icon_url)
                embed.description = 'You have updated your Epic ID!'
            except peewee.DoesNotExist:
                player = Player(agora_player_id=player_id, discord_id=user[1], player_name=epic_id,
                                elo=player_elo, team_id=None)
                player.save()
                embed.title = 'Success'
                embed.set_footer(text='Paragon', icon_url=AgoraAPI.icon_url)
                embed.description = 'You have attached your Epic ID to your Discord ID!'
        else:
            # User is requesting their current ID!
            try:
                player = Player.get(Player.discord_id == user[1])
                embed.title = 'Current Epic ID'
                embed.description = player.player_name
                embed.url = 'https://agora.gg/profile/' + player.agora_player_id + '/' + quote(player.player_name,
                                                                                               safe='')
                embed.set_footer(text='Paragon', icon_url=AgoraAPI.icon_url)
            except peewee.DoesNotExist:
                embed.title = 'Error'
                embed.description = 'No player name specified and no Epic ID was found linked to your account!\n'
                embed.description += '(See \'' + self.bot.command_prefix + 'help ign\' for more command information!)'
        await self.bot.send_message(ctx.message.channel, embed=embed)
