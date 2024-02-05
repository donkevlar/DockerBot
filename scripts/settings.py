import os
from scripts.docker_commands import docker_container
from dotenv import load_dotenv

if not docker_container:
    load_dotenv()

DISCORD_API_SECRET = os.getenv('DISCORD_API_SECRET')
