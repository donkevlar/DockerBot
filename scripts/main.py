import logging
import os
from dotenv import load_dotenv
from interactions import *
from interactions.ext.paginators import Paginator

# Other Files
import docker_lib as c
import settings

# Load env if not running Docker
load_dotenv()

# Test Docker Connection
c.docker_client_connect()

# Create a bot instance
bot = Client(intents=Intents.DEFAULT, basic_logging=True)


@listen()  # this decorator tells snek that it needs to listen for the corresponding event, and run this coroutine
async def on_ready():
    # This event is called when the bot is ready to respond to commands
    logging.info("Ready")
    logging.info(f"This bot is owned by {bot.owner}")


if __name__ == "__main__":
    bot.load_extension('commands')
    logging.info("Successfully loaded commands!")
    # Start the bot
    bot.start(settings.DISCORD_API_SECRET)
