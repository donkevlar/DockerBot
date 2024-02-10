import logging
import os
from dotenv import load_dotenv
from interactions import Client, Intents, slash_command, SlashContext, listen, AutocompleteContext, \
    OptionType, slash_option, Permissions, slash_default_member_permission, BaseContext, check, Task, IntervalTrigger
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


# Custom check for ownership
async def ownership_check(ctx: BaseContext):
    # Default only owner can use this bot
    ownership = os.getenv('OWNER_ONLY', True)
    if ownership:
        # Check to see if user is the owner while ownership var is true
        if ctx.bot.owner.username == ctx.user.username:
            print(f"{ctx.user.username}, you are the owner and ownership is enabled!")
            return True

        else:
            print(f"{ctx.user.username}, is not the owner and ownership is enabled!")
            return False
    else:
        return True


def option_container_name():
    def wrapper(func):
        return slash_option(
            name="container_name",
            opt_type=OptionType.STRING,
            description="Enter Container Name",
            required=True,
            autocomplete=True
        )(func)

    return wrapper


@listen()  # this decorator tells snek that it needs to listen for the corresponding event, and run this coroutine
async def on_ready():
    # This event is called when the bot is ready to respond to commands
    print("Ready")
    print(f"This bot is owned by {bot.owner}")


@slash_command(name="restart-container", description="Restart a container using the container name")
@check(ownership_check)
@slash_default_member_permission(Permissions.USE_SLASH_COMMANDS)
@option_container_name()
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
@check(ownership_check)
@slash_default_member_permission(Permissions.USE_SLASH_COMMANDS)
@option_container_name()
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
@check(ownership_check)
@slash_default_member_permission(Permissions.USE_SLASH_COMMANDS)
@option_container_name()
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
@check(ownership_check)
@slash_default_member_permission(Permissions.USE_SLASH_COMMANDS)
@slash_option(name="container_name",
              description="Enter a container name.",
              required=False, opt_type=OptionType.STRING, autocomplete=True)
@slash_option(name="filter",
              description="Filter for container list. "
                          "Do not use with container name search argument.",
              required=False, opt_type=OptionType.STRING, autocomplete=True)
async def get_containers(ctx: SlashContext, container_name: str = None, filter: str = "all"):
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

        elif container_name is not None and filter == "all":

            for container in options_:
                count += 1
                if container.lower() == container_name:
                    formatted_info += f'{count}: {container.name} | status: {container.status}\n'

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

    if string_option_input is not None or string_option_input != "":
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
@check(ownership_check)
@slash_default_member_permission(Permissions.USE_SLASH_COMMANDS)
@option_container_name()
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

    if container_choices != '' or container_choices is not None:
        await ctx.send(choices=container_choices)


@slash_command(name="discord_user")
@check(ownership_check)
@slash_default_member_permission(Permissions.ADMINISTRATOR)
async def test_discord_user(ctx: SlashContext):
    await ctx.send(f"current user: {ctx.user.username} | owner: {ctx.bot.owner.username}")


### TO DO -> Figure out Tasks
# @Task.create(IntervalTrigger(hours=1))
# async def check_container_status(ctx):
#     container_name = ctx.input_text
#     options_ = c.get_containers()
#     for container in options_:
#         if container_name == container.name:
#             formatted_container = f"{container.name} | status: {container.status}"
#             return formatted_container


# @slash_command(name="container_monitor", description="Create a recurring status check for a specific container")
# @slash_option(name="container_name", opt_type=OptionType.STRING, description="Enter Container Name",
# autocomplete=True, required=True) @check(ownership_check) @slash_default_member_permission(
# Permissions.USE_SLASH_COMMANDS) async def container_monitor(ctx: SlashContext, cont_name: str):
# check_container_status.start(*cont_name)
#
#
# @container_monitor.autocomplete("container_name")
# async def autocomplete_running_containers(ctx: AutocompleteContext):
#     # Get user input from discord
#     string_option_input = ctx.input_text
#     # Get running containers
#     options_running = c.get_running_containers()
#     container_choices = []
#
#     for container in options_running:
#         if string_option_input == container or string_option_input == container.lower() and \
#                 string_option_input not in exclusion_list:
#             container_choices += [{"name": f'{container}', "value": f'{container}'}]
#             print(f'Searched for: {string_option_input} | Found: {container} ')
#             logging.info(f'Searched for: {string_option_input} | Found: {container} ')
#
#     if container_choices != '' or container_choices is not None:
#         await ctx.send(choices=container_choices)
#
#
# @slash_command(name="container_monitor_stop", description="Stop any running container monitoring tasks")
# @check(ownership_check)
# @slash_default_member_permission(Permissions.USE_SLASH_COMMANDS)
# async def container_monitor_stop(ctx: SlashContext):
#     check_container_status.stop()
#     await ctx.send(f"Stopped Task: container_monitor")

if __name__ == "__main__":
    # Start the bot
    bot.start(settings.DISCORD_API_SECRET)
