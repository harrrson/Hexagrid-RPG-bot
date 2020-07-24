import discord
import mysql.connector

async def init(db: mysql.connector.MySQLConnection, message:discord.Message, command):
	print(db)