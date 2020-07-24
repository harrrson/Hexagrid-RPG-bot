import discord
import asyncio
import aiomysql
import secret_file

async def connect_to_db(id):
	db=await aiomysql.connect(
					host="localhost",
					user=secret_file.DB_LOGIN,
					password=secret_file.DB_PASSWORD,
					database=str(id))
	return db

async def disconnect_from_db(db):
	db.close()

#Check, if guild's database exists
#Every server have it's own database
async def check_guild_db(guild):
	db=await aiomysql.connect(
					host="localhost",
					user=secret_file.DB_LOGIN,
					password=secret_file.DB_PASSWORD)
	cur=await db.cursor()
	await cur.execute('SHOW DATABASES like \''+str(guild.id)+'\'')
	print(guild.id)
	r=await cur.fetchall()
	if not r:
		await cur.execute('CREATE SCHEMA `'+str(guild.id)+'` DEFAULT CHARACTER SET utf8 COLLATE utf8_polish_ci')
	await cur.close()
	db.close()