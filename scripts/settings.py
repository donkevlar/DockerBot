import os
import logging

from dotenv import load_dotenv

load_dotenv()

versionNumber = '1.0.1'
logging.info(f'Starting DockerBot! Version: {versionNumber}')

DISCORD_API_SECRET = os.getenv('DISCORD_API_SECRET')
