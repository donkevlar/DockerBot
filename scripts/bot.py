import logging
from dotenv import load_dotenv
from interactions import Client, Intents, slash_command, SlashContext, listen, AutocompleteContext, \
    OptionType, slash_option
from interactions.ext.paginators import Paginator

# Other Files
import docker_commands as c
import settings

# Load env if not running Docker
try:
    load_dotenv('.env')
except Exception as e:
    pass

versionNumber = '0.0.5'
logging.info(f'Starting DockerBot! Version: {versionNumber}')

# Test Docker Connection
c.docker_client_connect()

# Define the entry point of the bot

# Create a bot instance
bot = Client(intents=Intents.DEFAULT, basic_logging=True)

exclusion_list = []


@listen()  # this decorator tells snek that it needs to listen for the corresponding event, and run this coroutine
async def on_ready():
    # This event is called when the bot is ready to respond to commands
    print("Ready")
    print(f"This bot is owned by {bot.owner}")


@slash_command(name="restart-container", description="Restart a container using the container name")
@slash_option(name="container_name", opt_type=OptionType.STRING, description="Enter Container Name", required=True)
async def simple_restart_container(ctx: SlashContext, container_name: str):
    print("Starting Command! simple-restart")
    options_running = c.get_running_containers()

    for cont in options_running:
        if cont == container_name:
            await ctx.defer()

            c.restart_container(container_name)

            print(f'Executed Restart Successfully: {cont}')

            await ctx.send(f"Executed Restart Successfully: {cont}")
            logging.info('Successfully executed simple-restart-container')


# Current best working autocomplete, can use this as template later
@simple_restart_container.autocomplete("container_name")
async def autocomplete_running_containers(ctx: AutocompleteContext):
    # Get user input from discord
    string_option_input = ctx.input_text
    # Get running containers
    options_running = c.get_running_containers()
    container_choices = []

    for container in options_running:
        if (string_option_input == container or string_option_input == container.lower()) and \
                string_option_input not in exclusion_list:
            container_choices += [{"name": f'{container}', "value": f'{container}'}]
            print(f'Searched for: {string_option_input} | Found: {container} ')
            logging.info(f'Searched for: {string_option_input} | Found: {container} ')

    await ctx.send(choices=container_choices)


# Define the bots command handler
@slash_command(name="start-container", description="Start a container with the container name")
@slash_option(name="container_name", opt_type=OptionType.STRING, description="Enter Container Name", autocomplete=True,
              required=True)
async def simple_start_container(ctx: SlashContext, container_name: str):
    options_running = c.get_running_containers()

    selected = options_running

    if selected is container_name:
        try:
            await ctx.defer(ephemeral=True)
            c.start_container(container_name)
            await ctx.send(f"Starting {container_name}")
            logging.info("Successfully executed simple-start-container")
        except Exception as e:
            logging.warning("Could not execute simple-start-container")
            print(e)


@simple_start_container.autocomplete("container_name")
async def autocomplete_start_container(ctx: AutocompleteContext):
    # Get user input from discord
    string_option_input = ctx.input_text
    # Get running containers
    options_running = c.get_stopped_containers()
    container_choices = []

    for container in options_running:
        if string_option_input == container or string_option_input == container.lower() and \
                string_option_input not in exclusion_list:
            container_choices += [{"name": f'{container}', "value": f'{container}'}]

    logging.info(f'Container found:{container_choices}')
    await ctx.send(choices=container_choices)


@slash_command(name="get-running-containers", description="List all running containers")
@slash_option(name="container_name",
              description="Enter a name to see the status of a specific container",
              required=False, opt_type=OptionType.STRING, autocomplete=True)
async def get_running_containers(ctx: SlashContext, container_name: str = None):
    options_running = c.get_running_containers()
    formatted_info = ''
    count = 0
    # discord to wait for callback
    await ctx.defer(ephemeral=True)

    for container in options_running:
        count += 1
        if container_name is not None and container_name == container:
            formatted_info = f'{container_name} is Running'
            break
        else:
            formatted_info += f'{count}: {container}\n'

    paginator = Paginator.create_from_string(bot, formatted_info, page_size=200)

    await paginator.send(ctx)
    logging.info('Successfully executed get-running-containers')


@get_running_containers.autocomplete("container_name")
async def autocomplete_running_containers(ctx: AutocompleteContext):
    # Get user input from discord
    string_option_input = ctx.input_text
    # Get running containers
    options_running = c.get_running_containers()
    container_choices = []

    for container in options_running:
        if string_option_input == container or string_option_input == container.lower() and \
                string_option_input not in exclusion_list:
            container_choices += [{"name": f'{container}', "value": f'{container}'}]
            print(f'Searched for: {string_option_input} | Found: {container} ')
            logging.info(f'Searched for: {string_option_input} | Found: {container} ')

    await ctx.send(choices=container_choices)


# Define the bots command handler
@slash_command(name="stop-container", description="Stop a container with the container name", group_name="simple")
@slash_option(name="container_name", opt_type=OptionType.STRING, description="Enter Container Name", required=True)
async def simple_stop_container(ctx: SlashContext, container_name: str):
    options_exited = c.get_stopped_containers()

    for cont in options_exited:
        if cont == container_name:
            await ctx.defer(ephemeral=True)
            c.stop_container(container_name)
            print(cont)
            await ctx.send(f"Starting {cont}")
            logging.info('Successfully executed simple-stop-container')


@simple_stop_container.autocomplete("container_name")
async def autocomplete_stopped_containers(ctx: AutocompleteContext):
    # Get user input from discord
    string_option_input = ctx.input_text
    # Get running containers
    options_running = c.get_running_containers()
    container_choices = []

    for container in options_running:
        if string_option_input == container or string_option_input == container.lower() and \
                string_option_input not in exclusion_list:
            container_choices += [{"name": f'{container}', "value": f'{container}'}]

    await ctx.send(choices=container_choices)

if __name__ == "__main__":
    # Start the bot
    bot.start(settings.DISCORD_API_SECRET)
