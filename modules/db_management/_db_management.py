import asyncpg
import secret_file

class Database:
    def __init__(self,guild_id):
        self.guild_id = guild_id
        self.db=None

    async def connect(self):
        """Connect to database. Return true when connection is succesfull"""
        try:
            self.db=await asyncpg.connect(user=secret_file.db_login,password=secret_file.db_password,database=f'guild_{self.guild_id}',host='localhost')
            return True
        except asyncpg.InvalidCatalogNameError:
            return False

    async def create_guild_db(self):
        """Creating separate database for guild."""
        self.db=await asyncpg.connect(user=secret_file.db_login,password=secret_file.db_password,database='template1',host='localhost')
        await self.db.execute(f'CREATE DATABASE guild_{self.guild_id} OWNER {secret_file.db_login};')
        await self.disconnect()
        await self.connect()
        await self.db.execute('CREATE TABLE guild_settings(parameter VARCHAR(4) NOT NULL, value VARCHAR(10) NOT NULL);')
        await self.db.execute("INSERT INTO guild_settings(parameter,value) VALUES \
                                ('pref','d!dc '),\
                                ('lang','en');")
        await self.disconnect()

    async def disconnect(self):
        await self.db.close()

    async def change_value_in_table(self,table,column_name,name,*value_pairs):
        query=f'UPDATE {table} SET {",".join("=".join(params) for params in value_pairs)} WHERE {column_name}=\'{name}\';'
        await self.db.execute(query)


    async def fetch_table_columns(self,table,column_name,name,*columns):
        query = f'SELECT {",".join(columns)} FROM {table} WHERE {column_name} = \'{name}\';'
        result=await self.db.fetchrow(query)
        return result
