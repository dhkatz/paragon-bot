from datetime import datetime
from time import time

from discord.ext import commands

from API import AgoraAPI
from Database.database import *
from Util import checks


class Tournament:
    """Create and run tournaments on your Discord server."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.types = ['ARAM', 'STANDARD']

    @property
    def random_id(self):
        return str(hex(int(time() * 10000000))[8:])

    async def embed_notify(self, ctx: commands.Context, error: int, title: str, message: str):
        """Create and reply Discord embeds in one line."""
        embed = discord.Embed()
        embed.title = title
        embed.colour = discord.Colour.dark_red() if error == 1 else discord.Colour.green() if error == 0 else discord.Colour.blue()
        embed.description = message
        embed.set_footer(text='Paragon', icon_url=AgoraAPI.icon_url)
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
    async def _create(self, ctx, tournament_type: str, name: str, date: str, unique_id: str = ''):
        """Create a new tournament on this server."""
        embed = discord.Embed()
        try:
            Event.get(Event.creator == ctx.message.author.id)
            await self.embed_notify(ctx, 1, 'Error', 'Currently you cannot create more than one event per account!')
            return
        except DoesNotExist:
            pass
        if len(unique_id) != 8 and len(unique_id) != 0:
            await self.embed_notify(ctx, 1, 'Error', 'Your unique ID must be 8 characters!')
            return
        try:
            Event.get(Event.tournament_id == unique_id)
            await self.embed_notify(ctx, 1, 'Error', 'A tournament already exists with the provided ID!')
            return
        except DoesNotExist:
            pass
        try:
            tournament_time = datetime.datetime.strptime(date, '%m-%d-%Y %H:%M')
            if tournament_time > datetime.datetime.now() + datetime.timedelta(days=30):
                await self.embed_notify(ctx, 1, 'Error',
                                        'Unable to create a tournament scheduled for more than a month from now!')
        except:
            await self.embed_notify(ctx, 1, 'Error', 'Invalid time format! Please try again.')
            return
        if tournament_type.upper() not in self.types:
            await self.embed_notify(ctx, 1, 'Error', 'Invalid tournament type!')
            return
        tournament_id = self.random_id if len(unique_id) == 0 else unique_id
        tournament = Event(server_id=ctx.message.server.id, server_name=ctx.message.server.name, tournament_name=name,
                           tournament_id=tournament_id, type=tournament_type.upper(), event_date=tournament_time,
                           confirmed=False, created=datetime.datetime.utcnow(), creator=ctx.message.author.id)
        tournament.save()
        embed.title = name
        embed.description = 'Tournament Details'
        embed.colour = discord.Colour.blue()
        embed.add_field(name='Event Type', value=tournament_type.upper())
        embed.add_field(name='Event Time', value=tournament_time.strftime('%m-%d-%Y %H:%M'))
        embed.add_field(name='Event ID', value=tournament_id)
        embed.add_field(name='Confirmation',
                        value='Please confirm the event by typing **' + self.bot.command_prefix + 'tournament confirm [Event ID]**',
                        inline=False)
        embed.set_footer(text='Paragon', icon_url=AgoraAPI.icon_url)
        await self.bot.send_message(ctx.message.channel, embed=embed)

    @tournament.command(name='confirm', pass_context=True)
    async def _confirm(self, ctx, unique_id: str):
        """Confirm the creation of a new tournament."""
        if len(unique_id) != 8:
            await self.embed_notify(ctx, 1, 'Error', 'The tournament ID is 8 characters!')
            return
        found = False
        for tournament in Event.select():
            if tournament.tournament_id == unique_id and not tournament.confirmed:
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
                                    'Players can now join using **' + self.bot.command_prefix + 'tournament join ' + unique_id + '**')
        else:
            await self.embed_notify(ctx, 1, 'Error', 'No tournament was found with the provided ID!')

    @tournament.command(name='help', pass_context=True)
    async def _help(self, ctx):
        """Information on how to create a tournament."""
        await self.bot.reply('Please see https://github.com/DoctorJew/Paragon-Discord-Bot for tournament creation!')

    @tournament.command(name='delete', pass_context=True)
    async def _delete(self, ctx, unique_id: str):
        """Delete an existing tournament."""
        if len(unique_id) != 8:
            await self.embed_notify(ctx, 1, 'Error', 'The tournament ID is 8 characters!')
            return
        try:
            tournament = Event.get(Event.tournament_id == unique_id)
            if ctx.message.author.id not in [tournament.creator, self.bot.owner.id]:
                await self.embed_notify(ctx, 1, 'Error', 'Only the event creator or server staff may delete events!')
                return
            # TODO - Delete teams associated with tournament
            for player in Player.select().where(
                    Player.tournaments.contains(unique_id)):  # Remove the tournament from players!
                player.tournaments = str(player.tournaments).replace(unique_id + '|', '')
            await self.embed_notify(ctx, 2, 'Tournament Deleted',
                                    'Deleted the tournament called **' + tournament.tournament_name + '**.')
            tournament.delete_instance()
        except DoesNotExist:
            await self.embed_notify(ctx, 1, 'Error', 'No tournament exists with the provided ID!')

    @tournament.command(name='join', pass_context=True)
    async def _join(self, ctx, unique_id: str):
        """Join an ongoing tournament."""
        if len(unique_id) != 8:
            await self.embed_notify(ctx, 1, 'Error', 'The tournament ID is 8 characters!!')
            return
        try:
            tournament = Event.get(Event.tournament_id == unique_id)
        except DoesNotExist:
            await self.embed_notify(ctx, 1, 'Error', 'No tournament exists with the provided ID!')
            return
        try:
            player = Player.get(Player.discord_id == ctx.message.author.id)
            if player.tournaments is not None:
                player.tournaments += unique_id + '|'
                player.save()
            else:
                player.tournaments = ''
                player.tournaments += unique_id + '|'
                player.save()
            tournament.size = tournament.size + 1
            tournament.save()
            await self.embed_notify(ctx, 0, 'Tournament Joined',
                                    'You joined **' + tournament.tournament_name + '**. Have fun!')
        except DoesNotExist:
            await self.embed_notify(ctx, 1, 'Error', 'You must link your Epic ID to your Discord account!')

    @tournament.command(name='leave', pass_context=True)
    async def _leave(self, ctx, unique_id: str):
        """Leave a tournament."""
        if len(unique_id) != 8:
            await self.embed_notify(ctx, 1, 'Error', 'The tournament ID is 8 characters!!')
            return
        try:
            tournament = Event.get(Event.tournament_id == unique_id)
        except DoesNotExist:
            await self.embed_notify(ctx, 1, 'Error', 'No tournament exists with the provided ID!')
            return
        try:
            player = Player.get(Player.discord_id == ctx.message.author.id)
            if player.tournaments is not None:
                player.tournaments = str(player.tournaments).replace(unique_id + '|', '')
                await self.embed_notify(ctx, 2, 'Tournament Left',
                                        'You left **' + tournament.tournament_name + '**. See you later!')
                player.save()
                tournament.size = tournament.size - 1
                tournament.save()
            else:
                await self.embed_notify(ctx, 1, 'Error', 'You are not in any tournaments!')
        except DoesNotExist:
            await self.embed_notify(ctx, 1, 'Error', 'You must link your Epic ID to your Discord account!')

    @tournament.command(name='info', pass_context=True)
    async def _info(self, ctx, unique_id: str):
        """View information about a tournament."""
        embed = discord.Embed()
        try:
            tournament = Event.get(Event.tournament_id == unique_id)
        except DoesNotExist:
            await self.embed_notify(ctx, 1, 'Error', 'No tournament exists with the provided ID!')
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
        embed.set_footer(text='Paragon', icon_url=AgoraAPI.icon_url)
        await self.bot.send_message(ctx.message.channel, embed=embed)

    @tournament.group(name='team', pass_context=True)
    async def team(self, ctx):
        """Team related commands."""
        print()

    @team.command(name='create', pass_context=True)
    @checks.is_mod()
    async def team_create(self, ctx, unique_id: str, name: str):
        """Manual team creation"""
        await self.bot.reply('YES')


def setup(bot):
    bot.add_cog(Tournament(bot))
