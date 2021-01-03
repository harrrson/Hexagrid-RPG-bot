import math
import os
import sys
import traceback

import discord
from discord.ext import commands

import globals
import secret_file

DEFAULT_PREFIX = secret_file.prefix  # tired for switching prefix every time

intents = discord.Intents.none()
intents.guilds = True
intents.members = True
intents.messages = True


async def guild_prefix(bot, message):
    guild = message.guild
    if guild:
        prefix = globals.prefixes.get(int(guild.id), DEFAULT_PREFIX)
    else:
        prefix = DEFAULT_PREFIX
    return prefix


bot_token = secret_file.BOT_TOKEN

bot = commands.Bot(command_prefix=guild_prefix, case_insensitive=True, intents=intents)


@bot.event
async def on_ready():
    print('Logged in as {}'.format(bot.user.name))


@bot.command(hidden=True)
@commands.is_owner()
async def load(ctx, extension):
    try:
        bot.load_extension(f'modules.{extension}')
        await ctx.send(f'{extension} loaded successfully')
    except commands.ExtensionNotFound:
        await ctx.send(f'Cannot find {extension} module!')
    except commands.ExtensionAlreadyLoaded:
        await ctx.send(f'Module {extension} is already loaded!')
    except commands.NoEntryPointError:
        await ctx.send(f'No setup() function found in module ')
    except commands.ExtensionFailed as e:
        await ctx.send(f'Module {extension} raise an error during execution')
        print(str(e))


@bot.command(hidden=True)
@commands.is_owner()
async def unload(ctx, extension):
    try:
        bot.unload_extension(f'modules.{extension}')
        await ctx.send(f'Module {extension} unloaded successfully')
    except commands.ExtensionNotLoaded:
        await ctx.send(f'Module {extension} was not loaded')


@bot.command(hidden=True)
@commands.is_owner()
async def reload(ctx, extension):
    try:
        bot.reload_extension(f'modules.{extension}')
        await ctx.send(f'{extension} reloaded successfully')
    except commands.ExtensionNotLoaded:
        await ctx.send(f'Module {extension} was not loaded')
    except commands.ExtensionNotFound:
        await ctx.send(f'Cannot find {extension} module!')
    except commands.NoEntryPointError:
        await ctx.send(f'No setup() function found in module ')
    except commands.ExtensionFailed:
        await ctx.send(f'Module {extension} raise an error during execution')


bot.run(bot_token)
