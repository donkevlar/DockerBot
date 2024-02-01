import logging
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from datetime import datetime
import docker_commands as c

if not c.docker_container:
    load_dotenv()

versionNumber = '0.0.1'

c.docker_client_connect()

# Get Discord Token from ENV
token = os.environ.get("DISCORD_TOKEN")

current_time = datetime.now()
logging.info(f'\nStarting up bookshelf traveller v.{versionNumber}\n')
