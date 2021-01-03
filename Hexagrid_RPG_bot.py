from discord.ext import commands
from discord import Intents
from asyncpg import Connection
from config import BOT_TOKEN, DEFAULT_PREFIX

# configure bot intents
intents = Intents.none()
intents.guilds = True
intents.members = True
intents.message = True


# Command for per-guild prefixes
async def guild_prefix(bot, message):
	guild = message.guild
	if guild:
		if int(guild.id) in bot.prefixes:
			return bot.prefixes.get(int(guild.id))
		else:
			if isinstance(bot.db_conn, Connection) and not bot.db_conn.is_closed():
				if "prefix_select" not in bot.prep_queries:
					bot.prep_queries["prefix_select"] = bot.db_conn.prepare(
						"SELECT prefix from settings.prefixes WHERE guild_id=$1")
				if "prefix_insert" not in bot.prep_queries:
					bot.prep_queries["prefix_insert"] = bot.db_conn.prepare(
						"INSERT INTO settings.prefixes(guild_id,role_id,p_all,p_music)")
				if "perms_select" not in bot.prep_queries:
					bot.prep_queries["perms_select"] = bot.db_conn.prepare(
						"SELECT role_id settings.prefixes WHERE guild_id=$1")
				result_prefix = await bot.prep_queries["prefix_select"].fetchrow(int(guild.id))
				if result_prefix is not None:
					prefix = result_prefix.get('prefix')
					if prefix is not None:
						bot.prefixes[int(guild.id)] = prefix
					else:
						bot.prefixes[int(guild.id)] = DEFAULT_PREFIX
				else:
					bot.prep_queries["prefix_insert"].execute()
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

bot.run(BOT_TOKEN)
