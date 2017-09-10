import asyncio
import os
import sys

import aiohttp
import discord
from discord.ext import commands
from .database import Player
from peewee import DoesNotExist

from .util.paginator import Pages


class Admin:
    """Commands executable only by the bot owner."""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='bot', hidden=True)
    @commands.is_owner()
    async def admin(self, ctx):
        """Bot related commands. (Bot owner only)"""
        if ctx.invoked_subcommand is None:
            await self.bot.embed_notify(ctx, 1, 'Error', 'You must invoke a subcommand!')

    @admin.command(aliases=['quit'], hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx):
        """Shutdown the bot. (Bot owner only)"""
        await ctx.send('**:ok:** Goodbye!')
        self.bot.logout()
        sys.exit(0)

    @admin.command(hidden=True)
    @commands.is_owner()
    async def restart(self, ctx):
        """Restart the bot program. (Bot owner only)"""
        await ctx.send('**:ok:** Be back soon!')
        self.bot.logout()
        sys.exit(6)

    @admin.command(name='name', hidden=True)
    @commands.is_owner()
    async def _name(self, ctx, name: str):
        """Change the bot's username. (Bot owner only)"""
        await self.bot.user.edit(username=name)
        await self.bot.embed_notify(ctx, 0, 'Success', 'Changed my name to ' + name)

    @admin.command(hidden=True)
    @commands.is_owner()
    async def avatar(self, ctx, url: str):
        """Set the bot's avatar image. (Bot owner only)"""
        temp_avatar = 'temp_avatar.png'
        async with aiohttp.ClientSession() as session:
            async with session.get(''.join(url)) as img:
                with open(temp_avatar, 'wb') as f:
                    f.write(await img.read())
        with open(temp_avatar, 'rb') as f:
            await self.bot.user.edit(avatar=f.read())
        os.remove(temp_avatar)
        await asyncio.sleep(2)
        embed = discord.Embed(title='Success', description='Changed my avatar!', colour=discord.Colour.green())
        await ctx.send(embed=embed)

    @admin.group(name='blacklist', hidden=True)
    @commands.is_owner()
    async def blacklist(self, ctx):
        """Blacklist users from using commands. (Bot owner only)"""
        if 'add' not in str(ctx.invoked_subcommand) and 'remove' not in str(ctx.invoked_subcommand):
            if Player.select().where(Player.blacklist == True).count() > 0:
                try:
                    rows = Player.select().where(Player.blacklist == False)
                    p = Pages(ctx, entries=tuple(self.bot.get_user(int(player.discord_id)).name for player in rows))
                    p.embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
                    await p.paginate()
                except Exception as e:
                    await ctx.send(e)
            else:
                await self.bot.embed_notify(ctx, 2, 'Notice', 'There are no blacklisted users!')

    @blacklist.command(name='add', hidden=True)
    @commands.is_owner()
    async def add_blacklist(self, ctx, user: discord.Member):
        """Add a user to the blacklist. (Bot owner only)"""
        try:
            data = Player.get(Player.discord_id == str(user.id))
        except DoesNotExist:
            data = Player(discord_id=user.id, blacklist=True)
            data.save()
        else:
            if data.blacklist:
                await self.bot.embed_notify(ctx, 2, 'Notice', f'{user.nick} is already blacklisted!')
                return
            data.blacklist = True
            data.save()

        await self.bot.embed_notify(ctx, 0, 'Success', f'{user.nick} was blacklisted')

    @blacklist.command(name='remove', hidden=True)
    @commands.is_owner()
    async def remove_blacklist(self, ctx, user: discord.Member):
        """Remove a user from the blacklist. (Bot owner only)"""
        try:
            data = Player.get(Player.discord_id == str(user.id))
        except DoesNotExist:
            data = Player(discord_id=user.id, blacklist=False)
            data.save()
        else:
            if not data.blacklist:
                await self.bot.embed_notify(ctx, 2, 'Notice', f'{user.nick} is not blacklisted!')
                return
            data.blacklist = False
            data.save()

        await self.bot.embed_notify(ctx, 0, 'Success', f'{user.nick} was removed from the blacklist!')


def setup(bot):
    bot.add_cog(Admin(bot))
