import configparser
import logging

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
    team_name = CharField()
    team_elo = FloatField()


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
