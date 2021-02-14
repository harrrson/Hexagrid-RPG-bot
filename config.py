from dotenv import load_dotenv
import os

load_dotenv('.env')

# API credentials
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Bot database credentials
DB_LOGIN = os.getenv("DB_LOGIN")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Database misc
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Lavalink misc
LAVALINK_HOST= os.getenv("LAVALINK_HOST")
LAVALINK_PORT = os.getenv("LAVALINK_PORT")
LAVALINK_PASSWORD = os.getenv("LAVALINK_PASSWORD")

# Bot misc
DEFAULT_PREFIX = os.getenv("DEFAULT_PREFIX")
