import discord
import roll
import ci_manager
import db_manager
import help
import secret_file

bot_header='!dc '
test_server_id= secret_file.TEST_SERVER_ID
class Bot_client(discord.Client):

	async def on_ready(self):
		print('Logged as {0}'.format(self.user))

	async def on_guild_join(self,guild):
		await db_manager.check_guild_db(guild)

	async def on_message(self,message : discord.Message):
		if(message.author == self.user):
			return

		if message.content[:len(bot_header)].lower()==bot_header:
			command=message.content[len(bot_header):].split(' ')
			if command[0]=='?':
				await help.init(message,command[1:])
				return
			if command[0].lower()=='roll':
				await roll.init(message, command[1:])
				return

			#if command[0].lower()=='cc' and message.guild.id==test_server_id:
			#	await ci_manager.init(mydb,message,command[1:])
			#	return

			#if command[0].lower()=='session_modules' and message.guild.id==test_server_id:
			#	await db_manager.check_guild_db(message.guild)
			#	return