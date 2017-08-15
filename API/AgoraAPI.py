import math
from datetime import datetime
from urllib.parse import quote

import discord

from database.database import *

icon_url = 'https://vignette2.wikia.nocookie.net/paragonthegame/images/f/f4/Paragon-logo.png'


def get_agora_player_id(username):
    url = 'https://api.agora.gg/v1/players/search/' + username + '?lc=en&ssl=true'
    player_id = 'null'
    try:
        with requests.get(url=url) as r:
            if r.status_code == 200:
                js = r.json()
                if js:
                    player_id = str(js[0]['id'])
    except Exception as e:
        logging.exception(e)
    return player_id


def get_raw_elo(player_id):
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
        logging.exception(e)
    return player_elo


def get_agora_player_elo(player_id):
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

                                top = str(round(stat['percentile'], 2)) + '%' if 'percentile' in stat else 'No percent.'
                                info += "Top: " + top + '\n'

                                embed.title = player_name
                                embed.url = 'https://agora.gg/profile/' + player_id + '/' + quote(player_name, safe='')
                                embed.description = info
                                embed.set_footer(text='Paragon', icon_url=icon_url)
                    else:
                        embed.title = 'Error'
                        embed.colour = discord.Colour.dark_red()
                        embed.description = 'There seems to be no data for this account. Please re-check the name.'
                        embed.set_footer(text='Paragon', icon_url=icon_url)
                else:
                    embed.title = 'Error'
                    embed.colour = discord.Colour.dark_red()
                    embed.description = 'This account has been set to private!'
                    embed.set_footer(text='Paragon', icon_url=icon_url)
    except Exception as e:
        logging.exception(e)
    return embed


def get_agora_player_stats(player_id):
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
                                embed.set_footer(text='Paragon', icon_url=icon_url)
                    else:
                        embed.title = 'Error'
                        embed.colour = discord.Colour.dark_red()
                        embed.description = 'There seems to be no data for this account. Please re-check the name.'
                        embed.set_footer(text='Paragon', icon_url=icon_url)
                else:
                    embed.title = 'Notice'
                    embed.colour = discord.Colour.dark_red()
                    embed.description = 'This account is set to private'
                    embed.set_footer(text='Paragon', icon_url=icon_url)
    except Exception as e:
        logging.exception(e)

    return embed


def get_agora_hero_info(hero_id, image):
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
                embed.set_footer(text='Paragon', icon_url=icon_url)
    except Exception as e:
        logging.exception(e)

    return embed


def get_agora_hero_deck(hero_name, image, num):
    """Get the most popular decks on Agora.gg for a hero and return a Discord embed object."""
    url = 'https://api.agora.gg/v2/decks?tag=' + quote(hero_name, safe='') + '&sort=-votes&major=1&lc=en&ssl=true'
    embed = discord.Embed()

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
                embed.set_footer(text='Paragon', icon_url=icon_url)
    except Exception as e:
        logging.exception(e)
    return embed


def get_agora_hero_guide(hero_id, image, num):
    """Get a guide for a specific hero from Agora.gg"""
    url = 'https://api.agora.gg/v1/guides?name=&hero=' + hero_id + '&role=&page=0&sort=votes&&lc=en&ssl=true'
    embed = discord.Embed()

    try:
        with requests.get(url=url) as r:
            if r.status_code == 200:
                js = r.json()
                embed.title = js[num]['name']
                embed.url = 'https://agora.gg/guide/' + str(js[num]['id'])
                embed.set_thumbnail(url=image)
                embed.add_field(name='Votes', value=js[num]['votes'])
                embed.add_field(name='Role', value=js[num]['role'])
                embed.add_field(name='Author', value=js[num]['playerName'] + ' (Elo: ' + str(
                    round(js[num]['elo'], 2)) + ')')
                embed.set_footer(text='Paragon', icon_url=icon_url)
    except Exception as e:
        logging.exception(e)

    return embed


def get_agora_player_latest_game_stats(player_id, num):
    """Get the stats of a player's most recent game."""
    now = datetime.datetime.now()
    now = now.replace(day=1)
    start_year = str(now.replace(month=now.month - 3).year)
    start_month = str(now.replace(month=now.month - 3).month)
    end_year = str(now.replace(month=now.month + 1).year)
    end_month = str(now.replace(month=now.month + 1).month)
    end_day = str(now.replace(month=now.month + 1).day)

    url = 'https://api.agora.gg/v1/players/' + player_id + '/history/match/?page=0&start=' + start_year + '-'
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
                                winning_team = 'Won' if js[num]['winningTeam'] == 0 else 'Lost'

                                k = player['kills']
                                d = player['deaths']
                                a = player['assists']
                                kda_percent = k + a
                                kda_percent = kda_percent / max(1, d)

                                embed.title = 'Game Played: ' + js[num][
                                    'createdAt'].split('T')[0] + ' (UTC)' + ' Time: ' + final_time + ':' + seconds
                                embed.url = 'https://agora.gg/game/' + js[num]['id']
                                embed.colour = discord.Colour.blue()
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
                                embed.set_footer(text='Paragon', icon_url=icon_url)
                                break
                else:
                    embed.title = 'Error'
                    embed.colour = discord.Colour.dark_red()
                    embed.description = 'There was no last played game data found!'
                    embed.set_footer(text='Paragon', icon_url=icon_url)
    except Exception as e:
        logging.exception(e)

    return embed


def get_agora_player_current_game(player_id: str, team: int):
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
        logging.exception(e)
    return ''.join(info)
