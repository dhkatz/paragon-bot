import configparser
import logging

import discord
import requests
from peewee import *

HERO_DB = SqliteDatabase('C:/Users/mcilu/PycharmProjects/Paragon ARAM Bot/Database/test.db')
CARD_DB = SqliteDatabase('C:/Users/mcilu/PycharmProjects/Paragon ARAM Bot/Database/cards.db')
PARAGON_DB = SqliteDatabase('C:/Users/mcilu/PycharmProjects/Paragon ARAM Bot/Database/paragon_bot.db')

HERO_FILE = '{}/heroes.ini'.format('C:/Users/mcilu/PycharmProjects/Paragon ARAM Bot/Database')
HEROES = configparser.ConfigParser()
HEROES.read(HERO_FILE)


class BaseModel(Model):
    class Meta:
        database = HERO_DB


class Server(BaseModel):
    server_id = CharField(unique=True)
    server_name = CharField()
    use_music_role = BooleanField(default=True)
    music_role_id = CharField(null=True)

    class Meta:
        database = PARAGON_DB


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
    elo = FloatField()
    team_id = IntegerField(null=True)  # Unique ID of team player is on

    class Meta:
        database = PARAGON_DB


class Team(BaseModel):
    team_id = IntegerField(unique=True)  # Unique Team ID, assignable to players
    team_name = CharField(null=True)  # Team's chosen name
    team_elo = FloatField(default=0)  # Average team elo
    role_id = CharField(null=True)  # Role for the team
    channel_id = CharField(null=True)  # Text channel for the team
    voice_channel_id = CharField(null=True)  # Voice channel for the team


class TeamPlayer(BaseModel):
    player = ForeignKeyField(Player)
    team = ForeignKeyField(Team)


class Aram(BaseModel):
    server_id = CharField(unique=True)
    server_name = CharField()


class AramTeam(BaseModel):
    ForeignKeyField(Team)
    ForeignKeyField(Aram)


class Card(BaseModel):
    card_id = CharField(unique=True)  # Unique Card ID
    card_name = CharField()
    slot_type = CharField()
    icon = CharField()
    rarity = CharField()
    affinity = CharField()
    cost = CharField()
    upgrade_slots = CharField()
    effects = CharField()
    maxed_effects = CharField(null=True)

    class Meta:
        database = CARD_DB


def set_heroes():
    HERO_DB.connect()
    if 'hero' not in HERO_DB.get_tables():
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
        HERO_DB.close()
    except Exception as e:
        logging.exception(e)

    return HERO_DB


def set_players():
    PARAGON_DB.connect()
    if 'player' not in PARAGON_DB.get_tables():
        Player.create_table()
    PARAGON_DB.close()


def set_servers(client):
    PARAGON_DB.connect()
    if 'server' not in PARAGON_DB.get_tables():
        Server.create_table()


async def add_server(client: discord.Client, server: discord.Server):
    print('NOTICE: Adding server ' + server.name + ' to database...')
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
            print('NOTICE: Added server ' + server.name + ' to database!')
            return

    music_permissions = server.default_role
    music_permissions = music_permissions.permissions

    music_role = await client.create_role(server, name='Music', position=-1, permissions=music_permissions, hoist=False,
                                          colour=discord.Color(11815924), mentionable=False)
    guild = Server(server_id=server.id, server_name=server.name, use_music_role=True, music_role_id=music_role.id)
    guild.save()
    print('NOTICE: Added server ' + server.name + ' to database!')


async def remove_server(server: discord.Server):
    print('NOTICE: Removing ' + server.name + ' from database...')
    try:
        server_left = Server.get(Server.server_id == server.id)
        server_left.delete_instance()
    except DoesNotExist:
        'ERROR: Somehow a server we left did not exist in the database!'


def set_cards():
    CARD_DB.connect()
    if 'card' not in CARD_DB.get_tables():
        Card.create_table()

    url = 'https://api.agora.gg/v1/gamedata/cards?lc=en&ssl=true'

    try:
        with requests.get(url=url) as r:
            js = r.json()
            for card in js:
                card_effects = ''
                max_effects = ''
                for effect in card['effects']:
                    if 'stat' in effect:
                        card_effects += 'stat:' + effect['stat'] + ',value:' + str(effect['value']) + '|'
                    elif 'description' in effect:
                        card_effects += 'description:' + effect['description']
                        if 'cooldown' in effect:
                            card_effects += ',cooldown:' + str(effect['cooldown'])
                        if 'unique' in effect:
                            card_effects += ',unique:' + str(effect['unique'])
                        if 'passive' in effect:
                            card_effects += ',passive:' + str(effect['passive'])
                        card_effects += '|'
                if card['maxedEffects'] is not None:
                    for effect in card['maxedEffects']:
                        if 'stat' in effect:
                            max_effects += 'stat:' + effect['stat'] + ',value:' + str(effect['value']) + '|'
                        elif 'description' in effect:
                            max_effects += 'description:' + effect['description']
                            if 'cooldown' in effect:
                                max_effects += ',cooldown:' + str(effect['cooldown'])
                            if 'unique' in effect:
                                max_effects += ',unique:' + str(effect['unique'])
                            if 'passive' in effect:
                                max_effects += ',passive:' + str(effect['passive'])
                            max_effects += '|'
                new_card, created = Card.get_or_create(card_id=card['id'], card_name=card['name'],
                                                       slot_type=card['slotType'], icon=card['icon'],
                                                       rarity=card['rarity'], affinity=card['affinity'],
                                                       cost=card['cost'], upgrade_slots=card['upgradeSlots'],
                                                       effects=card_effects, maxed_effects=max_effects)
                new_card.save()
            CARD_DB.close()
    except Exception as e:
        logging.exception(e)

    return CARD_DB


def set_aram():
    # TODO
    print()
