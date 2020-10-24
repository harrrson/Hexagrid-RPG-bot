import os
import random

import secret_file
from discord.ext import commands
from modules.db_management._db_management import Database

prefixes = {}
default_prefix = ['d!dc ']


async def guild_prefix(bot, message):
    guild = message.guild
    if guild:
        return prefixes.get(guild.id, default_prefix)
    else:
        return default_prefix


bot_token = secret_file.BOT_TOKEN

bot = commands.Bot(command_prefix=guild_prefix, case_insensitive=True)


@bot.event
async def on_ready():
    print('Logged in as {}'.format(bot.user.name))

    # for guild in bot.guilds:
    # 	db=Database(guild.id)
    # 	db_conn=await db.connect()
    # 	if not db_conn:
    # 		await db.create_guild_db()
    # 		prefixes[guild.id]=default_prefix
    # 	else:
    # 		result=await db.fetch_table_columns("guild_settings","parameter","pref","value")
    # 		prefixes[guild.id]=result["value"]
    # 		await db.disconnect()
    # print(prefixes)


@bot.command(hidden=True)
@commands.is_owner()
async def load(ctx, extension):
    try:
        bot.load_extension(f'modules.{extension}')
        await ctx.send(f'{extension} loaded succesfully')
    except commands.ExtensionNotFound:
        await ctx.send(f'Cannot find {extenksion} module!')
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
        await ctx.send(f'Module {extension} unloaded succesfully')
    except commands.ExtensionNotLoaded:
        await ctx.send(f'Module {extension} was not loaded')


@bot.command(hidden=True)
@commands.is_owner()
async def reload(ctx, extension):
    try:
        bot.reload_extension(f'modules.{extension}')
        await ctx.send(f'{extension} reloaded succesfully')
    except commands.ExtensionNotLoaded:
        await ctx.send(f'Module {extension} was not loaded')
    except commands.ExtensionNotFound:
        await ctx.send(f'Cannot find {extension} module!')
    except commands.NoEntryPointError:
        await ctx.send(f'No setup() function found in module ')
    except commands.ExtensionFailed:
        await ctx.send(f'Module {extension} raise an error during execution')


#load all modules from ./modules/
# for filename in os.listdir('./modules'):
#     if filename.endswith('.py'):
#         try:
#             bot.load_extension(f'modules.{filename[:-3]}')
#         except:
#             print(f'Cannot load {filename[:-3]} module')

bot.run(bot_token)
