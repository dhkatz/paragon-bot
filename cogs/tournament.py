from datetime import datetime, timedelta
from time import time

from discord.ext import commands

from cogs.database import *
from cogs.util import checks


class Tournament:
    """Create and run tournaments on your Discord server."""

    def __init__(self, bot):
        self.bot = bot
        self.agora = self.bot.get_cog('Agora')
        self.types = ['ARAM', 'STANDARD']
        self.bot.scheduler.add_job(self.update_tournaments, 'interval', minutes=1)
        self.set_tournaments()
        self.set_teams()

    def set_tournaments(self):
        if 'event' not in self.bot.db.get_tables():
            self.bot.logger.info('Created database Event table')
            Event.create_table()

    def set_teams(self):
        if 'team' not in self.bot.db.get_tables():
            self.bot.logger.info('Created database Team table')
            Team.create_table()

    async def update_tournaments(self):
        self.bot.logger.info(f'Checking unconfirmed tournaments...')
        for event in Event.select().where(not Event.confirmed):
            if event.created < datetime.utcnow() - timedelta(minutes=5):
                self.bot.logger.info(f'Deleted unconfirmed tournament with ID {event.tournament_id}!')
                event.delete_instance()

    @property
    def random_id(self):
        return str(hex(int(time() * 10000000))[8:])

    async def embed_notify(self, ctx: commands.Context, error: int, title: str, message: str):
        """Create and reply Discord embeds in one line."""
        embed = discord.Embed()
        embed.title = title
        embed.colour = discord.Colour.dark_red() if error == 1 else discord.Colour.green() if error == 0 else discord.Colour.blue()
        embed.description = message
        embed.set_footer(text='Paragon', icon_url=self.agora.icon_url)
        await self.bot.send_message(ctx.message.channel, embed=embed)

    @commands.group(pass_context=True)
    async def tournament(self, ctx):
        """Tournament commands related to this server."""
        if ctx.invoked_subcommand is None:
            await self.bot.reply('Please see ' + self.bot.command_prefix + 'help tournament for command usage.')

    @tournament.command(name='list', pass_context=True)
    async def _list(self, ctx):
        print()

    @tournament.command(name='create', pass_context=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _create(self, ctx, tournament_type: str, name: str, date: str):
        """Create a new tournament on this server."""
        embed = discord.Embed()
        try:
            Event.get(Event.creator == ctx.message.author.id)
            await self.embed_notify(ctx, 1, 'Error', 'Currently you cannot create more than one event per account!')
            return
        except DoesNotExist:
            pass
        try:
            Event.get(Event.server_id == ctx.message.server.id)
            await self.embed_notify(ctx, 1, 'Error', 'A tournament already exists on this server!')
            return
        except DoesNotExist:
            pass
        if tournament_type.upper() not in self.types:
            await self.embed_notify(ctx, 1, 'Error', 'Invalid tournament type!')
            return
        try:
            tournament_time = datetime.strptime(date, '%m-%d-%Y %H:%M')
            if tournament_time > datetime.now() + timedelta(days=30):
                await self.embed_notify(ctx, 1, 'Error',
                                        'Unable to create a tournament scheduled for more than a month from now!')
        except:
            await self.embed_notify(ctx, 1, 'Error', 'Invalid time format! Please try again.')
            return
        tournament = Event(server_id=ctx.message.server.id, server_name=ctx.message.server.name, tournament_name=name,
                           type=tournament_type.upper(), event_date=tournament_time,
                           confirmed=False, created=datetime.utcnow(), creator=ctx.message.author.id)
        tournament.save()
        self.bot.logger.info('New tournament created. Awaiting confirmation.')
        embed.title = name
        embed.description = 'Tournament Details'
        embed.colour = discord.Colour.blue()
        embed.add_field(name='Event Type', value=tournament_type.upper())
        embed.add_field(name='Event Time', value=tournament_time.strftime('%m-%d-%Y %H:%M'))
        embed.add_field(name='Event ID', value=ctx.message.server.id)
        embed.add_field(name='Confirmation',
                        value='Please confirm the event by typing **' + self.bot.command_prefix + 'tournament confirm [Event ID]**',
                        inline=False)
        embed.set_footer(text='Paragon', icon_url=self.agora.icon_url)
        await self.bot.say(embed=embed)

    @tournament.command(name='confirm', pass_context=True)
    async def _confirm(self, ctx, unique_id: str):
        """Confirm the creation of a new tournament."""
        found = False
        for tournament in Event.select():
            if tournament.server_id == unique_id and not tournament.confirmed:
                if ctx.message.author.id not in [tournament.creator, self.bot.owner.id]:
                    await self.embed_notify(ctx, 1, 'Error',
                                            'Only the event creator or server staff may confirm events!')
                    return
                tournament.confirmed = True
                tournament.save()
                found = True
                break
        if found:
            await self.embed_notify(ctx, 0, 'Tournament Created',
                                    'Players can now join using **' + self.bot.command_prefix + 'tournament join**')
            self.bot.logger.info('Tournament confirmed with ID ' + unique_id)
        else:
            await self.embed_notify(ctx, 1, 'Error', 'No tournament was found with the provided ID!')

    @tournament.command(name='help', pass_context=True)
    async def _help(self, ctx):
        """Information on how to create a tournament."""
        await self.bot.reply('Please see https://github.com/DoctorJew/Paragon-Discord-Bot for tournament creation!')

    @tournament.command(name='delete', pass_context=True)
    async def _delete(self, ctx):
        """Delete an existing tournament."""
        try:
            tournament = Event.get(Event.server_id == ctx.message.server.id)
            if ctx.message.author.id not in [tournament.creator, self.bot.owner.id]:
                await self.embed_notify(ctx, 1, 'Error', 'Only the event creator or server staff may delete events!')
                return
            for team in Team.select().where(Team.tournament == ctx.message.server.id):
                for player in Player.select().where(Player.teams.contains(team.team_id)):
                    player.teams = str(player.teams).replace(team.team_id + '|', '')
                    player.save()
                team.delete_instance()
            for player in Player.select().where(
                    Player.tournaments.contains(ctx.message.server.id)):  # Remove the tournament from players!
                player.tournaments = str(player.tournaments).replace(ctx.message.server.id + '|', '')
                player.save()
            await self.embed_notify(ctx, 2, 'Tournament Deleted',
                                    'Deleted the tournament called **' + tournament.tournament_name + '**.')
            tournament.delete_instance()
            self.bot.logger.info('Tournament deleted from database')
        except DoesNotExist:
            await self.embed_notify(ctx, 1, 'Error', 'No tournament exists on this server!')

    @tournament.command(name='join', pass_context=True)
    async def _join(self, ctx):
        """Join an ongoing tournament."""
        try:
            tournament = Event.get(Event.server_id == ctx.message.server.id)
        except DoesNotExist:
            await self.embed_notify(ctx, 1, 'Error', 'No tournament exists on this server!')
            return
        try:
            player = Player.get(Player.discord_id == ctx.message.author.id)
            if player.tournaments is not None:
                player.tournaments += ctx.message.server.id + '|'
                player.save()
            else:
                player.tournaments = ''
                player.tournaments += ctx.message.server.id + '|'
                player.save()
            tournament.size = tournament.size + 1
            tournament.save()
            await self.embed_notify(ctx, 0, 'Tournament Joined',
                                    'You joined **' + tournament.tournament_name + '**. Have fun!')
        except DoesNotExist:
            await self.embed_notify(ctx, 1, 'Error', 'You must link your Epic ID to your Discord account!')

    @tournament.command(name='leave', pass_context=True)
    async def _leave(self, ctx):
        """Leave a tournament."""
        try:
            tournament = Event.get(Event.server_id == ctx.message.server.id)
        except DoesNotExist:
            await self.embed_notify(ctx, 1, 'Error', 'No tournament exists on this server!')
            return
        try:
            player = Player.get(Player.discord_id == ctx.message.author.id)
            if player.tournaments is not None:
                player.tournaments = str(player.tournaments).replace(ctx.message.server.id + '|', '')
                await self.embed_notify(ctx, 2, 'Tournament Left',
                                        'You left **' + tournament.tournament_name + '**. See you later!')
                tournament.size = tournament.size - 1
                tournament.save()
            else:
                await self.embed_notify(ctx, 1, 'Error', 'You are not in any tournaments!')
                return
        except DoesNotExist:
            await self.embed_notify(ctx, 1, 'Error', 'You must link your Epic ID to your Discord account!')
            return
        if player.teams is not None:
            for team in Team.select().where(Team.tournament == ctx.message.server.id):
                for team_id in player.teams.split('|'):
                    if team.team_id == team_id:
                        player.teams = str(player.teams).replace(team_id + '|', '')
                        player.save()
                        break

    @tournament.command(name='info', pass_context=True)
    async def _info(self, ctx, unique_id: str):
        """View information about a tournament."""
        embed = discord.Embed()
        try:
            tournament = Event.get(Event.server_id == ctx.message.server.id)
        except DoesNotExist:
            await self.embed_notify(ctx, 1, 'Error', 'No tournament exists on this server!')
            return
        creator = discord.utils.find(lambda u: u.id == tournament.creator, self.bot.get_all_members())
        if tournament.teams is not None and len(
                tournament.teams) > 0:
            size = len(tournament.teams.split('|'))
        else:
            size = 'None'
        embed.title = tournament.tournament_name
        embed.colour = discord.Colour.blue()
        embed.description = 'Created by ' + creator.name + ' in ' + tournament.server_name
        embed.add_field(name='Created', value=tournament.created)
        embed.add_field(name='Time', value=tournament.event_date)
        embed.add_field(name='Type', value=tournament.type)
        embed.add_field(name='Teams', value=size)
        embed.add_field(name='Players', value=tournament.size)
        embed.set_footer(text='Paragon', icon_url=self.agora.icon_url)
        await self.bot.say(embed=embed)

    @tournament.group(name='team', pass_context=True)
    async def team(self, ctx):
        """Team related commands."""
        print()

    @team.command(name='create', pass_context=True)
    @checks.is_mod()
    async def team_create(self, ctx, name: str):
        """Manually add a team to a tournament."""
        try:
            tournament = Event.get(Event.server_id == ctx.message.server.id)
        except DoesNotExist:
            await self.embed_notify(ctx, 1, 'Error', 'No tournament exists on this server!')
            return
        try:
            Team.get(Team.team_name == name)
            await self.embed_notify(ctx, 1, 'Error', 'A team already exists with this name!')
        except DoesNotExist:
            pass
        team_id = self.random_id
        team = Team(team_id=team_id, team_name=name, tournament=tournament.server_id)
        team.save()
        if tournament.teams is None:
            tournament.teams = '' + team_id + '|'
        else:
            tournament.teams += team_id + '|'
        tournament.save()
        embed = discord.Embed()
        embed.title = name
        embed.description = 'Team Details'
        embed.colour = discord.Colour.blue()
        embed.add_field(name='Team Name', value=name)
        embed.add_field(name='Team ID', value=team_id)
        embed.add_field(name='Event Name', value=tournament.tournament_name, inline=False)
        embed.add_field(name='Event ID', value=tournament.server_id)
        embed.set_footer(text='Paragon', icon_url=self.agora.icon_url)
        await self.bot.say(embed=embed)

    @team.command(name='delete', pass_context=True)
    @checks.is_mod()
    async def team_delete(self, ctx, name: str):
        """Delete a team by name or unique ID."""
        try:
            team = Team.get((Team.team_id == name) & (Team.tournament == ctx.message.server.id))
            team_id = team.team_id
            team.delete_instance()
            await self.embed_notify(ctx, 2, 'Team Deleted', 'Deleted ' + team.team_name)
            return
        except DoesNotExist:
            try:
                team = Team.get((Team.team_name % name) & (Team.tournament == ctx.message.server.id))
                team_id = team.team_id
                team.delete_instance()
                await self.embed_notify(ctx, 2, 'Team Deleted', 'Deleted ' + team.team_name)
            except DoesNotExist:
                await self.embed_notify(ctx, 1, 'Error', 'No team exists on this server with that name or ID!')
                return
        try:  # Remove team from tournament
            tournament = Event.get(Event.server_id == ctx.message.server.id)
            tournament.teams = tournament.teams.replace(team_id + '|', '')
        except DoesNotExist:
            await self.embed_notify(ctx, 1, 'Error', 'No tournament exists on this server!')
        for player in Player.select().where(Player.teams.contains(team_id)):  # Remove team from players
            player.teams = player.teams.replace(team_id + '|', '')
            player.save()

    @team.command(name='add', pass_context=True)
    @checks.is_mod()
    async def team_add(self, ctx):
        """Manually add mentioned players to a team."""
        try:
            tournament = Event.get(Event.server_id == ctx.message.server.id)
        except DoesNotExist:
            await self.embed_notify(ctx, 1, 'Error', 'No tournament exists on this server!')
        if ctx.message.mentions is not None:
            for user in ctx.message.mentions:
                print()


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


def setup(bot):
    bot.add_cog(Tournament(bot))
