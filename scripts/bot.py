import logging
import os

from dotenv import load_dotenv
from interactions import Client, Intents, slash_command, SlashContext, listen, AutocompleteContext, \
    OptionType, slash_option
from interactions.ext.paginators import Paginator

# Other Files
import docker_commands as c
import settings

# Load env if not running Docker
load_dotenv()

versionNumber = '0.0.5'
logging.info(f'Starting DockerBot! Version: {versionNumber}')

# Test Docker Connection
c.docker_client_connect()

# Define the entry point of the bot

# Create a bot instance
bot = Client(intents=Intents.DEFAULT, basic_logging=True)

exclusion_list = [os.getenv('EXCLUSIONS')]


@listen()  # this decorator tells snek that it needs to listen for the corresponding event, and run this coroutine
async def on_ready():
    # This event is called when the bot is ready to respond to commands
    print("Ready")
    print(f"This bot is owned by {bot.owner}")


@slash_command(name="restart-container", description="Restart a container using the container name")
@slash_option(name="container_name", opt_type=OptionType.STRING, description="Enter Container Name", required=True,
              autocomplete=True)
async def simple_restart_container(ctx: SlashContext, container_name: str):
    print("Starting Command! simple-restart")
    options_running = c.get_running_containers()

    for cont in options_running:
        if cont == container_name:
            await ctx.defer()

            c.restart_container(container_name)

            print(f'Executed Restart Successfully: {cont}')

            await ctx.send(f"Executed Restart Successfully: {cont}", ephemeral=True)
            logging.info('Successfully executed simple-restart-container')


# Current best working autocomplete, can use this as template later
@simple_restart_container.autocomplete("container_name")
async def autocomplete_restart_containers(ctx: AutocompleteContext):
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


@slash_command(name="stop-container", description="Stop a container with the container name")
@slash_option(name="container_name", opt_type=OptionType.STRING, description="Enter Container Name", required=True,
              autocomplete=True)
async def simple_stop_container(ctx: SlashContext, container_name: str):
    options_running = c.get_running_containers()

    for cont in options_running:
        if cont == container_name:
            await ctx.defer(ephemeral=True)
            c.stop_container(container_name)
            print(cont)
            await ctx.send(f"Stopping {cont}", ephemeral=True)
            logging.info('Successfully executed simple-stop-container')


# Current best working autocomplete, can use this as template later
@simple_stop_container.autocomplete("container_name")
async def autocomplete_stopped_containers(ctx: AutocompleteContext):
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
    options_stopped = c.get_stopped_containers()

    for container in options_stopped:
        if container == container_name:
            try:
                await ctx.defer(ephemeral=True)
                c.start_container(container_name)
                await ctx.send(f"Successfully started container: {container_name}", ephemeral=True)
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
        if string_option_input == container.lower() and \
                string_option_input not in exclusion_list:
            container_choices += [{"name": f'{container}', "value": f'{container}'}]

    logging.info(f'Container found:{container_choices}')
    await ctx.send(choices=container_choices)


@slash_command(name="get-containers", description="List all running containers")
@slash_option(name="container_name",
              description="Enter a name to see the status of a specific container",
              required=False, opt_type=OptionType.STRING, autocomplete=True)
@slash_option(name="filter",
              description="Filter for container list. "
                          "Do not use with container name search argument.",
              required=False, opt_type=OptionType.STRING, autocomplete=True)
async def get_containers(ctx: SlashContext, container_name: str = None, filter: str = "All"):
    formatted_info = ''
    count = 0
    await ctx.defer(ephemeral=True)

    try:
        # Check filter options
        if filter == "running":
            options_ = c.get_running_containers()
            print(f"Filter Set: {filter}")
        elif filter == "exited":
            options_ = c.get_stopped_containers()
            print(f"Filter Set: {filter}")
        else:
            options_ = c.get_containers()
            print(f"Filter Set: {filter}")
            if container_name is not None:
                for container in options_:
                    if container_name == container.name.lower():
                        formatted_info = f'{container.name} | status: {container.status}\n'
                        break

        # execute when a container name is present
        if container_name is not None and filter != "all":
            for container in options_:
                if container_name == container.lower():
                    formatted_info = f'{container}\n'
                    break
        elif container_name is None and filter == "all":

            for container in options_:
                count += 1
                formatted_info += f'{count}: {container.name} | status: {container.status}\n'

        elif container_name is None and filter != "all":

            for container in options_:
                count += 1
                formatted_info += f'{count}: {container}\n'

        paginator = Paginator.create_from_string(bot, formatted_info, page_size=350)

        await paginator.send(ctx, ephemeral=True)
        logging.info('Successfully executed get-running-containers')

    except Exception as e:
        await ctx.send("Could not complete your request at this time due to an error!", ephemeral=True)
        print("Error occured: ", e)


@get_containers.autocomplete("container_name")
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


@get_containers.autocomplete("filter")
async def autocomplete_filter_get_containers(ctx: AutocompleteContext):
    # Get user input from discord
    string_option_input = ctx.input_text
    choices = [
        {"name": "Running", "value": "running"},
        {"name": "Exited", "value": "exited"},
        {"name": "All", "value": "all"}
    ]

    await ctx.send(choices=choices)


@slash_command(name="get-logs", description="Get container logs")
@slash_option(name="container_name", opt_type=OptionType.STRING, description="Enter Container Name", autocomplete=True,
              required=True)
async def simple_get_container_logs(ctx: SlashContext, container_name: str):
    options_ = c.get_running_containers()

    for container in options_:
        if container == container_name:
            try:
                await ctx.defer(ephemeral=True)
                logs = c.get_container_logs(container_name)

                paginator = Paginator.create_from_string(bot, logs, page_size=2000)

                await paginator.send(ctx, ephemeral=True)
                logging.info("Successfully executed get-logs")
            except Exception as e:
                logging.warning("Could not execute get-logs")
                await ctx.send("Could not complete your request at this time due to an error!", ephemeral=True)
                print(e)


@simple_get_container_logs.autocomplete("container_name")
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


if __name__ == "__main__":
    # Start the bot
    bot.start(settings.DISCORD_API_SECRET)
