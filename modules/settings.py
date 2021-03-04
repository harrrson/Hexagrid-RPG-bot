from discord.ext import commands


class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def settings(self, ctx, *, args):
        await ctx.send('No valid command was given!')

    # @settings.command()
    # @command.check

# def setup(bot):
#     bot.add_cog(Settings(bot))