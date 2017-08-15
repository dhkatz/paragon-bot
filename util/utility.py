import discord
from database.database import *
from API import AgoraAPI

AFFINITY_MAP = {'Chaos': discord.Colour.dark_red(), 'Order': discord.Colour.gold(), 'Growth': discord.Colour.green(),
                'Knowledge': discord.Colour.blue(), 'Death': discord.Colour.dark_purple()}
STONE_MAP = {'Agility': discord.Colour.orange(), 'Intellect': discord.Colour.purple(),
             'Vitality': discord.Colour.green()}

TRAIT_MAP = {'Cultivate': 'Gold cost is reduced per attribute point purchased.',
             'Elevate': 'Increases effectiveness of passive per attribute point purchased.',
             'Combustible': 'Effect disappears upon death', 'Cursed': 'Card cannot be unequipped.',
             'Consumable': 'Card is removed after activation.'}


def build_card(card):
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
    embed.set_thumbnail(url=url)
    embed.set_footer(text='Paragon', icon_url=AgoraAPI.icon_url)
    return embed


def build_gem(gem):
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
    embed.set_footer(text='Paragon', icon_url=AgoraAPI.icon_url)
    return embed