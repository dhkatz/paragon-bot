import discord
from peewee import *

from bot import BOT_DB


class Database:
    """Database storage for the bot."""

    def __init__(self, bot):
        self.bot = bot
        self.set_players()
        self.set_servers()

    def set_players(self):
        if 'player' not in self.bot.db.get_tables():
            self.bot.logger.info('Created database Player table')
            Player.create_table()

    def set_servers(self):
        if 'server' not in self.bot.db.get_tables():
            self.bot.logger.info('Created database Server table')
            Server.create_table()

    async def on_guild_join(self, guild: discord.Guild):
        self.bot.logger.info(f'Adding server {guild.name} to database...')
        can_manage = False
        for role in guild.me.roles:
            if role.permissions.manage_roles:
                can_manage = True
                break
        if not can_manage:
            await guild.owner.send(embed=self.bot.embed_notify(None, 1, 'Invalid Permissions', f'{guild.me.nick} does not have the proper permissions! Leaving server. . .'))
            return await guild.leave()

        new_guild = Server(server_id=guild.id, server_name=guild.name)
        new_guild.save()
        self.bot.logger.info(f'Added server {guild.name} to database!')

    async def on_guild_remove(self, guild: discord.Guild):
        self.bot.logger.info('Removing ' + guild.name + ' from database...')
        try:
            server_left = Server.get(Server.guild_id == guild.id)
            server_left.delete_instance()
        except DoesNotExist:
            self.bot.logger.error('Somehow a server we left did not exist in the database!')


class BaseModel(Model):
    class Meta:
        database = BOT_DB


class Server(BaseModel):
    guild_id = CharField(unique=True)
    guild_name = CharField()  # Technically don't need to store this but helps with readability...


class Player(BaseModel):
    agora_player_id = CharField(unique=True, default='')
    discord_id = CharField(unique=True)
    player_name = CharField(default='')
    elo = FloatField(default=0)
    tournaments = TextField(null=True)  # Player can be in multiple tournaments
    teams = TextField(null=True)  # Player could be on multiple teams from different tournaments
    blacklist = BooleanField(default=False)


def setup(bot):
    bot.add_cog(Database(bot))
