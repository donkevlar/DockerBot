import logging
import discord
from discord.ext import commands
from datetime import datetime
from dotenv import load_dotenv

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

@bot.event
async def on_ready():
    await bot.tree.sync()
    logging.info(f'Bot is ready. Logged in as {bot.user}')


class SelectMenu(discord.ui.View):
    def __init__(self, ctx):
        super().__init__()

        self.ctx = ctx

    client = c.docker_client_connect()
    containers = client.containers.list()
    options_running = c.get_running_containers()

    options = [discord.SelectOption(label=container_name, value=container_name) for container_name in options_running]

    @discord.ui.select(placeholder='Select a docker to start', options=options)
    async def menu_callback(self, interaction: discord.Interaction, Select):
        Select.disabled = True
        selected_container = Select.values[0]
        await interaction.response.defer()
        await interaction.message.delete()
        await self.ctx.invoke(bot.get_command('start_container'), container_name=selected_container)


@bot.tree.command()
async def start_container(ctx, container_name: str):
    client = c.docker_client_connect()
    try:
        container = client.containers.get(container_name)
        container.start()
        await ctx.send(f"Successfully started container: {container_name}")
    except Exception as e:
        await ctx.send(f"Error starting container {container_name}: {e}")


if __name__ == "__main__":
    bot.run(settings.DISCORD_API_SECRET, root_logger=True)
