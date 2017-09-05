from discord.ext import commands

import data.config.load as config
from cogs.database import *


def check_permissions(ctx, perms, *, check=all):
    owner = ctx.message.author.id == config.__ownerid__
    if owner:
        return True

    resolved = ctx.channel.permissions_for(ctx.author)
    return check(getattr(resolved, name, None) == value for name, value in perms.items())


def has_permissions(*, check=all, **perms):
    def predicate(ctx):
        return check_permissions(ctx, perms, check=check)

    return commands.check(predicate)


def check_guild_permissions(ctx: commands.Context, perms, *, check=all):
    owner = ctx.message.author.id == config.__ownerid__
    if owner:
        return True

    if ctx.message.server is None:
        return False

    resolved = ctx.message.author.guild_permissions
    return check(getattr(resolved, name, None) == value for name, value in perms.items())


def has_guild_permissions(*, check=all, **perms):
    def predicate(ctx):
        return check_guild_permissions(ctx, perms, check=check)

    return commands.check(predicate)


# These do not take channel overrides into account

def is_mod():
    def predicate(ctx):
        return check_guild_permissions(ctx, {'manage_guild': True})

    return commands.check(predicate)


def is_admin():
    def predicate(ctx):
        return check_guild_permissions(ctx, {'administrator': True})

    return commands.check(predicate)


def is_owner():
    def predicate(ctx):
        return ctx.message.author.id == config.__ownerid__

    return commands.check(predicate)


def mod_or_permissions(**perms):
    perms['manage_guild'] = True

    def predicate(ctx):
        return check_guild_permissions(ctx, perms, check=any)

    return commands.check(predicate)


def admin_or_permissions(**perms):
    perms['administrator'] = True

    def predicate(ctx):
        return check_guild_permissions(ctx, perms, check=any)

    return commands.check(predicate)


def is_in_guilds(*guild_ids):
    def predicate(ctx):
        guild = ctx.guild
        if guild is None:
            return False
        return guild.id in guild_ids

    return commands.check(predicate)


def music_role(ctx):
    owner = ctx.message.author.id == ctx.message.server.owner.id
    if owner:
        return True

    server = Server.get(Server.server_id == ctx.message.server.id)
    if server.use_music_role == 0:
        return True

    for role in ctx.message.author.roles:
        if role.id == server.music_role_id:
            return True

    return False


def is_music():
    def predicate(ctx):
        return music_role(ctx)

    return commands.check(predicate)
