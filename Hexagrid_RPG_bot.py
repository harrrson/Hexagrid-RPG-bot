from discord.ext import commands
from discord import Intents
from asyncpg import Connection, connect
from config import BOT_TOKEN, DEFAULT_PREFIX, DB_HOST, DB_PORT, DB_LOGIN, DB_NAME, DB_PASSWORD

# configure bot intents
intents = Intents.none()
intents.guilds = True
intents.members = True
intents.messages = True


# Command for per-guild prefixes
async def guild_prefix(bot, message):
	guild = message.guild
	if guild:
		if int(guild.id) in bot.prefixes:
			return bot.prefixes[int(guild.id)]
		else:
			if isinstance(bot.db_conn, Connection) and not bot.db_conn.is_closed():
				if "prefix_select" not in bot.prep_queries:
					bot.prep_queries["prefix_select"] = await bot.db_conn.prepare(
						'SELECT prefix FROM settings.prefixes WHERE guild_id=$1')
				if "prefix_insert" not in bot.prep_queries:
					bot.prep_queries["prefix_insert"] = await bot.db_conn.prepare(
						'INSERT INTO settings.prefixes(guild_id,prefix) VALUES ($1, \"$2\")')
				if "perms_select" not in bot.prep_queries:
					bot.prep_queries["perms_select"] = await bot.db_conn.prepare(
						'SELECT role_id,p_admin,p_music FROM settings.permissions WHERE guild_id=$1')
				result_prefix = await bot.prep_queries["prefix_select"].fetchrow(int(guild.id))
				if result_prefix is not None:
					prefix = result_prefix.get('prefix')
					result_perms=await bot.prep_queries["perms_select"].fetch(int(guild.id))
					if result_perms is not None:
						perms=dict(result_perms)

					if prefix is not None:
						bot.prefixes[int(guild.id)] = prefix
					else:
						bot.prefixes[int(guild.id)] = DEFAULT_PREFIX
				else:
					await bot.prep_queries["prefix_insert"].fetch(int(guild.id), DEFAULT_PREFIX)
					bot.prefixes[int(guild.id)] = DEFAULT_PREFIX
				return bot.prefixes[int(guild.id)]

			else:
				return DEFAULT_PREFIX
	else:
		return DEFAULT_PREFIX


# Bot initialization
bot = commands.Bot(command_prefix=guild_prefix, case_insensitive=True, intents=intents)

# Initialization of global variables stored in bot class
bot.prep_queries = {}
bot.prefixes = {}
bot.permissions = {}
bot.db_conn = None


@bot.event
async def on_connect():
	bot.db_conn = await connect(host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_LOGIN, password=DB_PASSWORD)
	print("db")


@bot.event
async def on_ready():
	print("Connected as {0}".format(bot.user.name))


@bot.command()
async def test(ctx, *args):
	print('test')
	await ctx.send("Działa")
	return


bot.run(BOT_TOKEN)
