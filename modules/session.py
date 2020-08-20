from discord.ext import commands
# from .session_modules._character_managemant import *
# from .session_modules._session_management import *
from .db_management._db_management import *

class SessionManager(commands.Cog,name='RPG session management'):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='session', invoke_without_command=True)
    async def session(self, ctx, invalid_command: str = None, *, dump=None):
        if invalid_command is None:
            return
        else:
            return await ctx.send(f'{invalid_command} is not a valid command!')

    @session.command(name='list')
    async def list(self,ctx,session_status:str=None):
        pass
        # db=Database(ctx.message.guild.id)
        # conn_result=await db.connect()
        # if not conn_result:
        #     await db.create_guild_db()
        # conn_result=await db.connect()

def setup(bot):
    bot.add_cog(SessionManager(bot))
