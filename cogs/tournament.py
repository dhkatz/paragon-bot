from datetime import datetime
from time import time

from discord.ext import commands

from API import AgoraAPI
from Database.database import *


class Tournament:
    """Create and run tournaments on your Discord server."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.types = ['ARAM', 'STANDARD']

    @property
    def random_id(self):
        return str(hex(int(time() * 10000000))[8:])

    @commands.group(pass_context=True)
    async def tournament(self, ctx):
        """Tournament commands related to this server."""
        if ctx.invoked_subcommand is None:
            await self.bot.reply('Please see ' + self.bot.command_prefix + 'help tournament for command usage.')

    @tournament.command(name='create', pass_context=True)
    @commands.cooldown(1, 600, commands.BucketType.user)
    async def _create(self, ctx, type: str, name: str, date: str):
        """Create a new tournament on this server."""
        embed = discord.Embed()
        try:
            Event.get(Event.creator == ctx.message.author.id)
            self.bot.reply('Currently you cannot create more than one event per account!')
            return
        except DoesNotExist:
            pass
        try:
            tournament_time = datetime.datetime.strptime(date, '%m-%d-%Y %H:%M')
            if tournament_time > datetime.datetime.now() + datetime.timedelta(days=30):
                await self.bot.reply('You cannot create a tournament scheduled for more than a month from now!')
        except:
            embed.title = 'Error'
            embed.description = 'Invalid time format! Please try again!'
            embed.colour = discord.Colour.dark_red()
            await self.bot.send_message(ctx.message.channel, embed=embed)
            return
        if type.upper() not in self.types:
            embed.title = 'Error'
            embed.description = 'Invalid tournament type!'
            embed.colour = discord.Colour.dark_red()
            embed.set_footer(text='Paragon', icon_url=AgoraAPI.icon_url)
            await self.bot.send_message(ctx.message.channel, embed=embed)
            return
        tournament_id = self.random_id
        tournament = Event(server_id=ctx.message.server.id, server_name=ctx.message.server.name, tournament_name=name,
                           tournament_id=tournament_id, type=type.upper(), event_date=tournament_time,
                           confirmed=False, created=datetime.datetime.utcnow(), creator=ctx.message.author.id)
        tournament.save()
        embed.title = name
        embed.description = 'Tournament Details'
        embed.add_field(name='Event Type', value=type.upper())
        embed.add_field(name='Event Time', value=tournament_time.strftime('%m-%d-%Y %H:%M'))
        embed.add_field(name='Event ID', value=tournament_id)
        await self.bot.send_message(ctx.message.channel, embed=embed)
        await self.bot.say(
            'Please confirm the event by typing ' + self.bot.command_prefix + 'tournament confirm UNIQUEID\nIf you do not confirm within 5 minutes your tournament will be removed!')

    @tournament.command(name='confirm', pass_context=True)
    async def _confirm(self, ctx, unique_id: str):
        """Confirm the creation of a new tournament."""
        embed = discord.Embed()
        if len(unique_id) != 8:
            await self.bot.reply('The tournament ID is 8 characters!')
            return
        found = False
        for tournament in Event.select():
            if tournament.tournament_id == unique_id and not tournament.confirmed:
                if ctx.message.author.id not in [tournament.creator, self.bot.owner.id]:
                    await self.bot.reply('Only the event creator or server admins can confirm events!')
                    return
                tournament.confirmed = True
                tournament.save()
                found = True
                break
        if found:
            embed.title = 'Tournament Created'
            embed.description = 'You created a new tournament!\nPlayers can now join using "' + self.bot.command_prefix + 'tournament join ' + unique_id + '"'
            await self.bot.send_message(ctx.message.channel, embed=embed)
        else:
            embed.title = 'Error'
            embed.description = 'No tournament was found with the provided ID! Please try again.'
            embed.colour = discord.Colour.dark_red()
            await self.bot.send_message(ctx.message.channel, embed=embed)

    @tournament.command(name='help', pass_context=True)
    async def _help(self, ctx):
        """Information on how to create a tournament."""
        await self.bot.reply('Please see https://github.com/DoctorJew/Paragon-Discord-Bot for tournament creation!')

    @tournament.command(name='delete', pass_context=True)
    async def _delete(self, ctx, unique_id: str):
        """Delete an existing tournament."""
        if len(unique_id) != 8:
            await self.bot.reply('The tournament ID is 8 characters!')
            return
        try:
            tournament = Event.get(Event.tournament_id == unique_id)
            if ctx.message.author.id not in [tournament.creator, self.bot.owner.id]:
                await self.bot.reply('Only the event creator or server admins can delete events!')
                return
            # TODO - Delete teams associated with tournament
            for player in Player.select().where(
                    Player.tournaments.contains(unique_id)):  # Remove the tournament from players!
                player.tournaments = str(player.tournaments).replace(unique_id + '|', '')
            await self.bot.reply('Deleted the tournament called ' + tournament.tournament_name + '.')
            tournament.delete_instance()
        except DoesNotExist:
            await self.bot.reply('No tournament exists with the provided ID!')

    @tournament.command(name='join', pass_context=True)
    async def _join(self, ctx, unique_id: str):
        """Join an ongoing tournament."""
        if len(unique_id) != 8:
            await self.bot.reply('The tournament ID is 8 characters!')
            return
        try:
            tournament = Event.get(Event.tournament_id == unique_id)
        except DoesNotExist:
            await self.bot.reply('No tournament exists with the provided ID!')
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
            self.bot.reply('You joined ' + tournament.tournament_name + '!')
        except DoesNotExist:
            await self.bot.reply('You must link your Epic ID to your Discord account before joining!')

    @tournament.command(name='leave', pass_context=True)
    async def _leave(self, ctx, unique_id: str):
        """Leave a tournament."""
        if len(unique_id) != 8:
            await self.bot.reply('The tournament ID is 8 characters!')
            return
        try:
            tournament = Event.get(Event.tournament_id == unique_id)
        except DoesNotExist:
            await self.bot.reply('No tournament exists with the provided ID!')
            return
        try:
            player = Player.get(Player.discord_id == ctx.message.author.id)
            if player.tournaments is not None:
                player.tournaments = str(player.tournaments).replace(unique_id + '|', '')
                await self.bot.reply('You left ' + tournament.tournament_name + '!')
                player.save()
            else:
                await self.bot.reply('You are not in any tournaments!')
        except DoesNotExist:
            await self.bot.reply('You must link your Epic ID to your Discord account before leaving!')

    @tournament.command(name='info', pass_context=True)
    async def _info(self, ctx, unique_id: str):
        """View information about a tournament."""
        embed = discord.Embed()
        try:
            tournament = Event.get(Event.tournament_id == unique_id)
        except DoesNotExist:
            embed.title = 'Error'
            embed.description = 'No tournament exists with the provided ID!'
            embed.colour = discord.Colour.dark_red()
            await self.bot.send_message(ctx.message.channel, embed=embed)
            return
        creator = discord.utils.find(lambda u: u.id == tournament.creator, self.bot.get_all_members())
        if tournament.teams is not None and len(
                tournament.teams) > 0:
            size = len(tournament.teams.split('|'))
        else:
            size = 'None'
        embed.title = tournament.tournament_name
        embed.description = 'Created by ' + creator.name + ' in ' + tournament.server_name
        embed.add_field(name='Created', value=tournament.created)
        embed.add_field(name='Time', value=tournament.event_date)
        embed.add_field(name='Type', value=tournament.type)
        embed.add_field(name='Teams', value=size)
        embed.add_field(name='Players', value=tournament.size)
        await self.bot.send_message(ctx.message.channel, embed=embed)


def setup(bot):
    bot.add_cog(Tournament(bot))
