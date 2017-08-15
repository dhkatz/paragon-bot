import configparser
import datetime
import logging

import discord
import requests
from peewee import *

PARAGON_DB = SqliteDatabase('C:/Users/mcilu/PycharmProjects/Paragon-Discord-Bot/Database/paragon_bot.db')

HERO_FILE = '{}/heroes.ini'.format('C:/Users/mcilu/PycharmProjects/Paragon-Discord-Bot/Database')
HEROES = configparser.ConfigParser()
HEROES.read(HERO_FILE)

logger = logging.getLogger('discord')


class BaseModel(Model):
    class Meta:
        database = PARAGON_DB


class Server(BaseModel):
    server_id = CharField(unique=True)
    server_name = CharField()
    use_music_role = BooleanField(default=True)
    music_role_id = CharField(null=True)


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


class Player(BaseModel):
    agora_player_id = CharField(unique=True)
    discord_id = CharField(unique=True)
    player_name = CharField()
    elo = FloatField(default=0)
    tournaments = TextField(null=True)  # Player can be in multiple tournaments
    teams = TextField(null=True)  # Player could be on multiple teams from different tournaments


class Team(BaseModel):
    team_id = CharField(unique=True)  # Unique Team ID, assignable to players
    team_name = CharField(null=True)  # Team's chosen name
    tournament = CharField(unique=True)  # Tournament associated with team
    team_elo = FloatField(default=0)  # Average team elo
    role_id = CharField(null=True)  # Role for the team
    channel_id = CharField(null=True)  # Text channel for the team
    voice_channel_id = CharField(null=True)  # Voice channel for the team


class Event(BaseModel):
    server_id = CharField(unique=True)
    server_name = CharField()
    creator = CharField()
    tournament_name = CharField()
    type = CharField()
    teams = TextField(null=True)
    size = IntegerField(default=0)
    confirmed = BooleanField(default=False)
    created = DateTimeField()
    event_date = DateTimeField()


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


class Gem(BaseModel):
    gem_id = CharField(unique=True)  # Unique Gem ID
    gem_name = CharField()
    template = CharField()
    description = TextField()
    slot = SmallIntegerField()
    stone = CharField()
    shape = CharField()


def set_heroes():
    if 'hero' not in PARAGON_DB.get_tables():
        Hero.create_table()

    url = 'https://api.agora.gg/v1/gamedata/heroes?lc=en&ssl=true'

    try:
        with requests.get(url=url) as r:
            if r.status_code == 200:
                js = r.json()
                for hero in js:
                    lane = HEROES[hero['slug']]['lane']
                    icon = HEROES[hero['slug']]['icon']

                    new_hero, created = Hero.get_or_create(agora_hero_id=hero['id'], hero_name=hero['name'],
                                                           slug=hero['slug'],
                                                           type=hero['type'], attack=hero['attack'],
                                                           affinity1=hero['affinity1'],
                                                           affinity2=hero['affinity2'], damage_type=hero['damageType'],
                                                           abilities=hero['abilities'], icon=icon,
                                                           agora_data_name=hero['code'], roles=lane)
                    new_hero.save()
    except Exception as e:
        logger.exception(e)


def set_players():
    if 'player' not in PARAGON_DB.get_tables():
        Player.create_table()


def set_tournaments():
    if 'event' not in PARAGON_DB.get_tables():
        Event.create_table()


def update_tournaments():
    for event in Event.select().where(not Event.confirmed):
        if event.created < datetime.datetime.utcnow() - datetime.timedelta(minutes=5):
            logger.info(f'Deleted unconfirmed tournament with ID {event.tournament_id}!')
            event.delete_instance()


def set_servers(client):
    if 'server' not in PARAGON_DB.get_tables():
        Server.create_table()


def set_teams():
    if 'team' not in PARAGON_DB.get_tables():
        Team.create_table()


async def add_server(client: discord.Client, server: discord.Server):
    logger.info('Adding server ' + server.name + ' to database...')
    can_manage = False
    for role in server.me.roles:
        if role.permissions.manage_roles:
            can_manage = True
            break
    if not can_manage:
        error_message = 'Paragon Subreddit Bot does not have the proper permissions! Leaving server. . .'
        await client.send_message(server.owner, content=error_message)
        await client.leave_server(server)
        return

    for role in server.me.roles:
        if role.name == 'Music':
            music_role = role
            guild = Server(server_id=server.id, server_name=server.name, use_music_role=True,
                           music_role_id=music_role.id)
            guild.save()
            logger.info('Added server ' + server.name + ' to database!')
            return

    music_permissions = server.default_role
    music_permissions = music_permissions.permissions

    music_role = await client.create_role(server, name='Music', position=-1, permissions=music_permissions, hoist=False,
                                          colour=discord.Color(11815924), mentionable=False)
    guild = Server(server_id=server.id, server_name=server.name, use_music_role=True, music_role_id=music_role.id)
    guild.save()
    logger.info('Added server ' + server.name + ' to database!')


async def remove_server(server: discord.Server):
    logger.info('Removing ' + server.name + ' from database...')
    try:
        server_left = Server.get(Server.server_id == server.id)
        server_left.delete_instance()
    except DoesNotExist:
        logger.error('Somehow a server we left did not exist in the database!')


def set_cards():
    if 'card' not in PARAGON_DB.get_tables():
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
        logger.exception(e)


def set_gems():
    if 'gem' not in PARAGON_DB.get_tables():
        Gem.create_table()

    url = 'https://api.agora.gg/v2/gems'

    try:
        with requests.get(url=url) as r:
            js = r.json()
            for gem in js:
                new_gem, created = Gem.get_or_create(gem_name=gem['name'], gem_id=gem['id'], template=gem['template'],
                                                     description=gem['description'], slot=gem['slot'],
                                                     stone=gem['stone'], shape=gem['shape'])
                new_gem.save()
    except Exception as e:
        logger.exception(e)


def setup_tables(client):
    set_players()
    set_heroes()
    set_cards()
    set_gems()
    set_tournaments()
    set_servers(client)
    set_teams()
