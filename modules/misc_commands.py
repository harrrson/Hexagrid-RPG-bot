from discord.ext import commands


class MiscStuff(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def invite(self, ctx):
		await ctx.send('Want me to join your guild? Here is my authorization link:\nhttps://tinyurl.com/hexagrid')


def setup(bot):
	bot.add_cog(MiscStuff(bot))
