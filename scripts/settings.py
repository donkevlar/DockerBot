import os
from dotenv import load_dotenv

try:
    load_dotenv('.env')
except Exception as e:
    pass

DISCORD_API_SECRET = os.getenv('DISCORD_API_SECRET')
