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
async def on_connect():
	await globals.init(bot)  # initialize global variables


@bot.event
async def on_ready():
	print('Logged in as {}'.format(bot.user.name))
	# load all modules from ./modules/
	for filename in os.listdir('./modules'):
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

	conn = globals.db_connection
	prefixes = await conn.fetch("SELECT guild_id,prefix FROM settings.prefixes;")
	permissions = await conn.fetch('SELECT guild_id,role_id,p_all,p_music FROM settings.permissions;')

	# conversion from Result type to dict for easier parsing
	pref_fetched = {}
	for row in prefixes:
		pref_fetched[int(row['guild_id'])] = str(row['prefix'])

	for row in permissions:
		if globals.permitted_roles.get(int(row['guild_id'])) is None:
			globals.permitted_roles[int(row['guild_id'])] = []
		if row['p_all']:
			globals.permitted_roles[int(row['guild_id'])].append(int(row['role_id']))

	guilds_to_add = []
	for guild in bot.guilds:
		if int(guild.id) in pref_fetched:
			globals.prefixes[int(guild.id)] = str(pref_fetched[int(guild.id)])
		else:
			globals.prefixes[int(guild.id)] = DEFAULT_PREFIX
			guilds_to_add.append(guild.id)

	if guilds_to_add:
		query = 'INSERT INTO settings.prefixes (guild_id , prefix) VALUES '
		for guild in guilds_to_add:
			query += f'({int(guild)} , \'{DEFAULT_PREFIX}\'),'
		query = query[:-1]  # drop last comma
		query += ';'
		result = await conn.execute(query)


@bot.event
async def on_message(msg):
	if msg.content.startswith(f'<@{bot.user.id}>') or msg.content.startswith(f'<@!{bot.user.id}>'):
		await msg.channel.send(f'My prefix for this guild is \'{globals.prefixes.get(msg.guild.id, DEFAULT_PREFIX)}\'')
	await bot.process_commands(msg)


@bot.event
async def on_command_error(ctx, error):
	# if command has local error handler, return
	if hasattr(ctx.command, 'on_error'):
		return

	# get the original exception
	error = getattr(error, 'original', error)

	if isinstance(error, commands.CommandNotFound):
		return

	if isinstance(error, commands.BotMissingPermissions):
		missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
		if len(missing) > 2:
			fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
		else:
			fmt = ' and '.join(missing)
		_message = 'I need the **{}** permission(s) to run this command.'.format(fmt)
		await ctx.send(_message)
		return

	if isinstance(error, commands.DisabledCommand):
		await ctx.send('This command has been disabled.')
		return

	if isinstance(error, commands.CommandOnCooldown):
		await ctx.send("This command is on cooldown, please retry in {}s.".format(math.ceil(error.retry_after)))
		return

	if isinstance(error, commands.MissingPermissions):
		missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
		if len(missing) > 2:
			fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
		else:
			fmt = ' and '.join(missing)
		_message = 'You need the **{}** permission(s) to use this command.'.format(fmt)
		await ctx.send(_message)
		return

	if isinstance(error, commands.UserInputError):
		await ctx.send("Invalid input.")
		await bot.send_command_help(ctx)
		return

	if isinstance(error, commands.NoPrivateMessage):
		try:
			await ctx.author.send('This command cannot be used in direct messages.')
		except discord.Forbidden:
			pass
		return

	if isinstance(error, commands.CheckFailure):
		await ctx.send("You do not have permission to use this command.")
		return

	# ignore all other exception types, but print them to stderr
	print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)

	traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


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
