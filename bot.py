import logging
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from datetime import datetime

# Other Files
import docker_commands as c
import settings

# Load env if not running docker
if not c.docker_container:
    load_dotenv()

versionNumber = '0.0.1'


current_time = datetime.now()
logging.info(f'\nStarting up bookshelf traveller v.{versionNumber}\n')

# Test Docker Connection
c.docker_client_connect()

# Discord Bot Setup
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="$", intents=intents)







if __name__ == "__main__":
    bot.run(settings.DISCORD_API_SECRET, root_logger=True)
