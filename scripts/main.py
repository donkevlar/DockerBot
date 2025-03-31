import logging
from dotenv import load_dotenv
from interactions import *

# Other Files
import docker_lib as c
import settings

logger = logging.getLogger("bot")

# Load env if not running Docker
load_dotenv()

# Test Docker Connection
c.docker_client_connect()

# Create a bot instance
bot = Client(intents=Intents.DEFAULT, basic_logging=True)


@listen()  # this decorator tells snek that it needs to listen for the corresponding event, and run this coroutine
async def on_ready():
    # This event is called when the bot is ready to respond to commands
    logger.info(f"DockerBot Version {settings.versionNumber}")
    logger.info(f"This bot is owned by {bot.owner}")
    logger.info("Beep Boop I am ready to serve!")


if __name__ == "__main__":
    bot.load_extension('commands')
    logger.info("Successfully loaded commands!")
    # Start the bot
    bot.start(settings.DISCORD_API_SECRET)
