import discord
from Database.database import *
from API import AgoraAPI

CARD_MAP = {'description:': '', '{attr:mpreg}': 'Mana Regen', '{attr:mp}': 'Mana', '{attr:hpreg}': 'HP Regen',
            '{attr:hp}': 'HP', 'stat:': '', 'value:': '', 'BasicResistanceRating,': 'Basic Armor: ',
            'AbilityResistanceRating,': 'Ability Armor: ', 'AttackSpeedRating,': 'Attack Speed: ',
            'AttackRating,': 'Power: ', 'AbilityRating,': 'Power: ', 'MaxEnergy,': 'Max Mana: ',
            'CriticalDamageChance,': 'Crit Chance: ', 'MaxHealth,': 'Health: ', 'HealthRegenRate,': 'Health Regen: ',
            'EnergyRegenRate,': 'Mana Regen: ', 'LifeStealRating,': 'Life Steal: ',
            'BasicPenetrationRating,': 'Basic Pen: ', 'AbilityPenetrationRating,': 'Ability Pen: '}


def replace_stat(stat):
    """Replace raw card data with user friendly strings."""
    mapped = stat
    for k, v in CARD_MAP.items():
        mapped = mapped.replace(k, v)
    if 'Crit Chance' in mapped:
        if '0.0' in stat:
            mapped = mapped.replace('0.0', '') + '%'
        elif '0.' in stat:
            mapped = mapped.replace('0.', '') + '%'
    return mapped


def build_card(card):
    """Build a Discord embed for a card and return it."""
    embed = discord.Embed()

    description = max_description = bonus = max_bonus = ''

    if Card.select().where(Card.card_name == card).count() > 0:
        result = Card.select().where(Card.card_name == card).get()
    else:
        result = Card.select().where(Card.card_name.contains(card)).get()

    basic = 'Affinity: ' + result.affinity + '\n'
    basic += 'Rarity: ' + result.rarity + '\n'
    basic += 'Type: ' + result.slot_type + '\n'
    basic += 'Cost: ' + result.cost + '\n'

    effects = str(result.effects)
    for effect in effects.split('|'):
        if 'description:' in effect:
            description += replace_stat(stat=effect)
        else:
            bonus += replace_stat(stat=effect) + '\n'

    max_effects = str(result.maxed_effects)
    for effect in max_effects.split('|'):
        if 'description:' in effect:
            max_description += replace_stat(stat=effect)
        else:
            max_bonus += replace_stat(stat=effect) + '\n'
    embed.title = result.card_name
    embed.url = 'https://agora.gg/card/' + result.card_id
    embed.add_field(name='Basic', value=basic)
    embed.add_field(name='Bonus', value=bonus)
    if len(max_bonus) > 1:
        embed.add_field(name='Upgrade Bonus', value=max_bonus)
    if len(description) > 0:
        header = ''
        if 'unique:True' in description:
            description = description.replace(',unique:True', '')
            header += 'Unique '
            if 'passive:True' in description:
                description = description.replace(',passive:True', '')
                header += 'Passive'
            else:
                header += 'Active'
        embed.add_field(name=header, value=description, inline=False)
    if len(max_description) > 0:
        max_header = 'Upgrade '
        if 'unique:True' in max_description:
            max_description = max_description.replace(',unique:True', '')
            max_header += 'Unique '
            if 'passive:True' in max_description:
                max_description = max_description.replace(',passive:True', '')
                max_header += 'Passive'
            else:
                max_header += 'Active'
        embed.add_field(name=max_header, value=max_description, inline=False)
    embed.set_footer(text='Paragon', icon_url=AgoraAPI.icon_url)
    return embed