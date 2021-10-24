from discord.ext import commands
from discord import Intents, Message
from asyncpg import Connection, connect
import os
import argparse
from memory_profiler import memory_usage

from config import BOT_TOKEN, DEFAULT_PREFIX, DB_HOST, DB_PORT, DB_LOGIN, DB_NAME, DB_PASSWORD

# configure bot intents

intents = Intents.none()
intents.guilds = True
intents.members = True
intents.messages = True
intents.voice_states = True


async def create_connection(bot_instance):
    pass
    # bot_instance.db_conn = await connect(host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_LOGIN,
    #                                      password=DB_PASSWORD)
    # bot_instance.prep_queries["prefix_select"] = await bot_instance.db_conn.prepare(
    #     'SELECT prefix FROM settings.prefixes WHERE guild_id=$1')
    # bot_instance.prep_queries["prefix_insert"] = await bot_instance.db_conn.prepare(
    #     '''INSERT INTO settings.prefixes(guild_id,prefix) VALUES ($1, "$2")''')
    # bot_instance.prep_queries["perms_select"] = await bot_instance.db_conn.prepare(
    #     'SELECT role_id,p_admin,p_music FROM settings.permissions WHERE guild_id=$1')


# Command for per-guild prefixes
async def guild_prefix(bot, message):
    guild = message.guild
    if guild:
        if int(guild.id) in bot.prefixes:
            return bot.prefixes[int(guild.id)]
        else:
            if isinstance(bot.db_conn, Connection) and not bot.db_conn.is_closed():
                result_prefix = await bot.db_conn.fetchrow(
                    'SELECT prefix FROM settings.prefixes WHERE guild_id=%d' % int(guild.id))
                result_perms = await bot.db_conn.fetch(
                    'SELECT role_id,p_admin,p_music FROM settings.permissions WHERE guild_id=%d' % int(guild.id))
                if result_prefix is not None:
                    prefix = result_prefix.get('prefix')
                    if prefix is not None:
                        bot.prefixes[int(guild.id)] = prefix
                    else:
                        bot.prefixes[int(guild.id)] = DEFAULT_PREFIX
                else:
                    bot.prefixes[int(guild.id)] = DEFAULT_PREFIX

                if result_perms is not None:
                    for record in result_perms:
                        perms = dict(record)
                        bot.permissions[int(perms["role_id"])] = {"admin": bool(perms["p_admin"]),
                                                                  "music": bool(perms["p_music"])}
                return bot.prefixes[int(guild.id)]

            else:
                return DEFAULT_PREFIX
    else:
        return DEFAULT_PREFIX


# Bot initialization
bot = commands.Bot(command_prefix=guild_prefix, case_insensitive=True, intents=intents)

# CLI arguments
parser = argparse.ArgumentParser(description='Bot CLI arguments')
parser.add_argument('-m', '--music', help='load music module', action='store_true')
args = parser.parse_args()

# Initialization of global variables stored in bot class
bot.prep_queries = {}
bot.prefixes = {}
bot.permissions = {}
bot.db_conn = None


@bot.event
async def on_connect():
    await create_connection(bot)


@bot.event
async def on_ready():
    print("Connected as {0}".format(bot.user.name))
    for filename in os.listdir('./modules'):
        if filename == 'music.py' and not args.music: continue
        if filename.endswith('.py'):
            try:
                bot.load_extension(f'modules.{filename[:-3]}')
                print(f'{filename[:-3]} loaded successfully')
            except commands.ExtensionAlreadyLoaded:
                print(f'Module {filename[:-3]} is already loaded!')
            except commands.NoEntryPointError:
                print(f'No setup() function found in module {filename[:-3]}')
            except commands.ExtensionFailed as e:
                print(f'Module {filename[:-3]} raise an error during execution')
                print(str(e))


@bot.event
async def on_message(msg: Message):
    if msg.content.startswith(f'<@{bot.user.id}>') or msg.content.startswith(f'<@!{bot.user.id}>'):
        prefix = bot.prefixes.get(msg.guild.id, DEFAULT_PREFIX)
        await msg.channel.send(
            "Prefix for this guild is '%s'" % prefix + (", take care to spaces" if " " in prefix else ""))
    if msg.content.startswith("zamknij bota"):
        await bot.close()
    await bot.process_commands(msg)


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


@bot.command()
async def test(ctx, *args):
    await ctx.send("Działa")
    return

mem_usage = memory_usage()
print(f'Memory usage pre-run: {mem_usage[0]} MB')

bot.run(BOT_TOKEN)
