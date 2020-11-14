import asyncpg

import secret_file


async def init(bot):
	global db_connection, prefixes, permitted_roles
	prefixes = {}
	permitted_roles = {}
	db_connection = await asyncpg.connect(host='127.0.0.1', port=secret_file.db_port, user=secret_file.db_login,
	                                      password=secret_file.db_password, database=secret_file.db_name)
