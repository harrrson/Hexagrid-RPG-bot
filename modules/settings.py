from discord.ext import commands
from Hexagrid_RPG_bot import prefixes
from .db_management._db_management import *

async def check_permissions(ctx):
    author=ctx.message.author.id
    guild_owner=ctx.message.guild.owner.id
    bot_owner=ctx.bot.owner_id
    if (author==guild_owner) or (author==bot_owner):
        return True
    else:
        await ctx.send('You are not allowed to use this command')
        return False

class Settings(commands.Cog):
    def __init__(self,bot):
        self.bot= bot

    @commands.group(name='settings',invoke_without_command=True)
    @commands.guild_only()
    async def settings(self,ctx):
        pass

    @settings.command(name='change_prefix')
    @commands.guild_only()
    @commands.check(check_permissions)
    async def change_prefix(self,ctx,prefix: str):
        db=Database(ctx.message.guild.id)
        if await db.connect():
            await db.change_value_in_table('guild_settings',"parameter" ,"pref",('value',f'\'{prefix}\''))
            prefixes[ctx.message.guild.id]=prefix
            print(prefixes)
            await db.disconnect()
            await ctx.send(f'Prefix succesfully changed to \'{prefix}\'')
        else:
            await ctx.send('Cannot update prefix.')

def setup(bot):
    bot.add_cog(Settings(bot))
