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

    async def add_server(self, server: discord.Server):
        self.bot.info('Adding server ' + server.name + ' to database...')
        can_manage = False
        for role in server.me.roles:
            if role.permissions.manage_roles:
                can_manage = True
                break
        if not can_manage:
            error_message = 'Paragon Subreddit Bot does not have the proper permissions! Leaving server. . .'
            await self.bot.send_message(server.owner, content=error_message)
            await self.bot.leave_server(server)
            return

        for role in server.me.roles:
            if role.name == 'Music':
                music_role = role
                guild = Server(server_id=server.id, server_name=server.name, use_music_role=True,
                               music_role_id=music_role.id)
                guild.save()
                self.bot.logger.info('Added server ' + server.name + ' to database!')
                return

        music_permissions = server.default_role
        music_permissions = music_permissions.permissions

        music_role = await self.bot.create_role(server, name='Music', position=-1, permissions=music_permissions,
                                                hoist=False,
                                                colour=discord.Color(11815924), mentionable=False)
        guild = Server(server_id=server.id, server_name=server.name, use_music_role=True, music_role_id=music_role.id)
        guild.save()
        self.bot.logger.info('Added server ' + server.name + ' to database!')

    async def remove_server(self, server: discord.Server):
        self.bot.logger.info('Removing ' + server.name + ' from database...')
        try:
            server_left = Server.get(Server.server_id == server.id)
            server_left.delete_instance()
        except DoesNotExist:
            self.bot.logger.error('Somehow a server we left did not exist in the database!')


class BaseModel(Model):
    class Meta:
        database = BOT_DB


class Server(BaseModel):
    server_id = CharField(unique=True)
    server_name = CharField()
    use_music_role = BooleanField(default=True)
    music_role_id = CharField(null=True)


class Player(BaseModel):
    agora_player_id = CharField(unique=True)
    discord_id = CharField(unique=True)
    player_name = CharField()
    elo = FloatField(default=0)
    tournaments = TextField(null=True)  # Player can be in multiple tournaments
    teams = TextField(null=True)  # Player could be on multiple teams from different tournaments


def setup(bot):
    n = Database(bot)
    bot.add_listener(n.add_server, 'on_server_join')
    bot.add_listener(n.remove_server, 'on_server_remove')
    bot.add_cog(Database(bot))
