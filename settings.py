import pathlib
import os
import logging
import time
from docker_commands import docker_container
from datetime import datetime
from logging.config import dictConfig
from dotenv import load_dotenv

if not docker_container:
    load_dotenv()

DISCORD_API_SECRET = os.getenv('DISCORD_API_SECRET')
