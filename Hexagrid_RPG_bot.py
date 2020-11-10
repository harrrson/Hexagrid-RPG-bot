import os

from discord.ext import commands

import secret_file

prefixes = {}
default_prefix = [secret_file.prefix]  # tired for switching prefix every time


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
