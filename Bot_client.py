import discord
from discord.ext import commands

class Bot_client(commands.Bot):
	"""description of class"""

	async def on_ready(self):
		print('Logged as {0}'.format(self.user))

	@commands.command(name='roll')
	async def roll(self, ctx):
		if ctx.invoked_subcommand is None:
			print('test')