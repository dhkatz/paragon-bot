import peewee
from discord.ext import commands

from Modules.Utility import *

BOT_DESCRIPTION = '''Bot commands using the Python Agora API.'''

bot = commands.Bot(command_prefix='.', description=BOT_DESCRIPTION)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.command(pass_context=True)
async def elo(ctx):
    """Returns a player's elo by name from Agora.gg"""
    print(ctx.message.server.name + ' called by: ' + ctx.message.author.name)

    embed = discord.Embed()
    message = str(ctx.message.content).replace(bot.command_prefix + 'elo', '')

    # Command has specified a username
    if len(message) > 1:
        user = message.replace(' ', '', 1)
    else:
        # Public channel message
        if isinstance(ctx.message.author, discord.Member):
            user = str(ctx.message.author.nick)
        # Private channel. We have to pull by name or DB
        else:
            user = str(ctx.message.author.name)

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

    bot.send_message(ctx.message.channel, embed=embed)


@bot.command(pass_context=True)
async def stats(ctx):
    """Returns a player's stats from Agora.gg"""
    print(ctx.message.server.name + ' called by: ' + ctx.message.author.name)

    embed = discord.Embed()
    message = str(ctx.message.content).replace(bot.command_prefix + 'stats', '')

    # Command has specified a username
    if len(message) > 1:
        user = message.replace(' ', '', 1)
    else:
        # Public channel message
        if isinstance(ctx.message.author, discord.Member):
            user = str(ctx.message.author.nick)
        # Private channel. We have to pull by name or DB
        else:
            user = str(ctx.message.author.name)

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

    bot.send_message(ctx.message.channel, embed=embed)


@bot.command(pass_context=True)
async def lpg(ctx):
    """Get a player's last played game stats from Agora.gg"""
    print(ctx.message.server.name + ' called by: ' + ctx.message.author.name)

    embed = discord.Embed()
    message = str(ctx.message.content).replace(bot.command_prefix + 'lpg', '')

    # Command has specified a username
    if len(message) > 1:
        user = message.replace(' ', '', 1)
    else:
        # Public channel message
        if isinstance(ctx.message.author, discord.Member):
            user = str(ctx.message.author.nick)
        # Private channel. We have to pull by name or DB
        else:
            user = str(ctx.message.author.name)

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

    bot.send_message(ctx.message.channel, embed=embed)


@bot.command(pass_context=True, aliases=['deck', 'd'])
async def herodeck(ctx):
    """Returns top three hero decks from Agora.gg"""
    print(ctx.message.server.name + ' called by: ' + ctx.message.author.name)

    embed = discord.Embed()
    message = str(ctx.message.content).replace(bot.command_prefix + ctx.invoked_with, '')

    if len(message) > 1:
        hero = message.replace(' ', '', 1)
    else:
        embed.title = 'Error'
        embed.description = 'You must specify a hero with this command!'
        embed.set_footer(text='Paragon', icon_url=AgoraAPI.icon_url)
        return embed

    try:
        results = Hero.select().where(Hero.hero_name.contains(hero)).get()
    except peewee.DoesNotExist:
        embed.title = 'Error'
        embed.description = 'Hero does not exist, if the hero is new be patient and try again in a few days!'
        embed.set_footer(text='Paragon', icon_url=AgoraAPI.icon_url)
        bot.send_message(ctx.message.channel, embed=embed)
        return

    for i in range(0, 3):
        embed = AgoraAPI.get_agora_hero_deck(hero_id=results.agora_hero_id, image=results.icon, num=i)
        bot.send_message(ctx.message.channel, embed=embed)


@bot.command(pass_context=True, aliases=['guide', 'g'])
async def heroguide(ctx):
    """Returns top three hero guides from Agora.gg"""
    print(ctx.message.server.name + ' called by: ' + ctx.message.author.name)

    embed = discord.Embed()
    message = str(ctx.message.content).replace(bot.command_prefix + ctx.invoked_with, '')

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
        bot.send_message(ctx.message.channel, embed=embed)
        return

    for i in range(0, 3):
        embed = AgoraAPI.get_agora_hero_deck(hero_id=results.agora_hero_id, image=results.icon, num=i)
        bot.send_message(ctx.message.channel, embed=embed)


@bot.command(pass_context=True)
async def card(ctx, *args):
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
        bot.send_message(ctx.message.channel, embed=embed)


@bot.command(pass_context=True)
async def ign(ctx):
    """Tag your Paragon IGN to your Discord account."""
    user = str(ctx.message.author).split('#')
    print(user)


# @bot.group(pass_context=True)
# async def cool(ctx):
#     """Says if a user is cool.
#     In reality this just checks if a subcommand is being invoked.
#     """
#     if ctx.invoked_subcommand is None:
#         await bot.say('No, {0.subcommand_passed} is not cool'.format(ctx))
#
#
# @cool.command(name='bot')
# async def _bot():
#     """Is the bot cool?"""
#     await bot.say('Yes, the bot is cool.')


# noinspection SpellCheckingInspection
bot.run('MzA4MDMyNTUyMjQzODIyNjAy.DFnY5Q.T7ztlpMlNdWKpgNs3uj96eXb7ng')
