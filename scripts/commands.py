import logging
import os
from dotenv import load_dotenv
from interactions import *
from interactions.ext.paginators import Paginator
# Other Files
import docker_lib as c
import db

# TODO Add better logging similar to bookshelf-traveller
# Logger Config
logger = logging.getLogger("bot")
handler = logging.StreamHandler()
console_handler = logger.handlers[0]
original_formatter = console_handler.formatter

# Load env if not running Docker
load_dotenv()

exclusion_list = [os.getenv('EXCLUSIONS')]


# Custom check for ownership
async def ownership_check(ctx: BaseContext, application=''):
    # Default only owner can use this bot
    # Check to see if user is the owner while ownership var is true
    if ctx.bot.owner.username == ctx.user.username:
        return True
    else:
        # Check if any users are populated in the management db
        users = db.get_all_users()
        user_num = len(users)

        if user_num == 0:
            logger.debug(f"No users found, authentication failed.")
            return False

        elif user_num > 0 and application != '':
            # Check if current user is in the managed application list
            user_id = ctx.user.id
            apps = db.get_user_applications(user_id)

            if application in apps:
                logger.info(f"User {user_id} authenticated successfully for application {application}!")
                return True
            else:
                return False

        else:
            return False


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


class DockerCommands(Extension):
    def __init__(self, bot):
        pass

    @slash_command(name="restart-container", description="Restart a container using the container name")
    @slash_default_member_permission(Permissions.USE_SLASH_COMMANDS)
    @option_container_name()
    async def simple_restart_container(self, ctx: SlashContext, container_name: str):
        # Verify if an application manager
        manager = await ownership_check(ctx, application=container_name)
        # If not allowed to run application
        if not manager:
            await ctx.send('Permission Denied!', ephemeral=True)
            return

        print("Starting Command! simple-restart")
        await ctx.defer()
        options_running = c.get_running_containers()

        if container_name in options_running:

            c.restart_container(container_name)

            print(f'Executed Restart Successfully: {container_name}')

            await ctx.send(f"Executed Restart Successfully: {container_name}", ephemeral=True)
            logging.info('Successfully executed simple-restart-container')

    @slash_command(name="stop-container", description="Stop a container with the container name")
    @slash_default_member_permission(Permissions.USE_SLASH_COMMANDS)
    @option_container_name()
    async def simple_stop_container(self, ctx: SlashContext, container_name: str):
        # Verify if an application manager
        manager = await ownership_check(ctx, application=container_name)
        # If not allowed to run application
        if not manager:
            await ctx.send('Permission Denied!', ephemeral=True)
            return

        options_running = c.get_running_containers()

        if container_name in options_running:
            await ctx.defer(ephemeral=True)
            c.stop_container(container_name)
            await ctx.send(f"Stopping {container_name}", ephemeral=True)
            logging.info('Successfully executed simple-stop-container')

    # Define the bots command handler
    @slash_command(name="start-container", description="Start a container with the container name")
    @slash_default_member_permission(Permissions.USE_SLASH_COMMANDS)
    @option_container_name()
    async def simple_start_container(self, ctx: SlashContext, container_name: str):
        # Verify if an application manager
        manager = await ownership_check(ctx, application=container_name)
        # If not allowed to run application
        if not manager:
            await ctx.send('Permission Denied!', ephemeral=True)
            return

        options_stopped = c.get_stopped_containers()

        if container_name in options_stopped:
            try:
                await ctx.defer(ephemeral=True)
                c.start_container(container_name)
                await ctx.send(f"Successfully started container: {container_name}", ephemeral=True)
                logging.info("Successfully executed simple-start-container")
            except Exception as e:
                logging.warning("Could not execute simple-start-container")
                print(e)

    @slash_command(name="get-containers", description="List all running containers")
    @slash_default_member_permission(Permissions.USE_SLASH_COMMANDS)
    @slash_option(name="container_name",
                  description="Enter a container name.",
                  required=False, opt_type=OptionType.STRING, autocomplete=True)
    @slash_option(name="filter",
                  description="Filter for container list. "
                              "Do not use with container name search argument.",
                  required=False, opt_type=OptionType.STRING, autocomplete=True)
    async def get_containers(self, ctx: SlashContext, container_name: str = None, filter: str = "all"):
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

            paginator = Paginator.create_from_string(self.bot, formatted_info, page_size=350)

            await paginator.send(ctx, ephemeral=True)
            logging.info('Successfully executed get-running-containers')

        except Exception as e:
            await ctx.send("Could not complete your request at this time due to an error!", ephemeral=True)
            print("Error occured: ", e)

    @slash_command(name="get-logs", description="Get container logs")
    @slash_default_member_permission(Permissions.USE_SLASH_COMMANDS)
    @option_container_name()
    async def simple_get_container_logs(self, ctx: SlashContext, container_name: str):
        # Verify if an application manager
        manager = await ownership_check(ctx, application=container_name)
        # If not allowed to run application
        if not manager:
            await ctx.send('Permission Denied!', ephemeral=True)
            return
        options_ = c.get_running_containers()

        for container in options_:
            if container == container_name:
                try:
                    await ctx.defer(ephemeral=True)
                    logs = c.get_container_logs(container_name)

                    paginator = Paginator.create_from_string(self.bot, logs, page_size=2000)

                    await paginator.send(ctx, ephemeral=True)
                    logging.info("Successfully executed get-logs")
                except Exception as e:
                    logging.warning("Could not execute get-logs")
                    await ctx.send("Could not complete your request at this time due to an error!", ephemeral=True)
                    print(e)

    @slash_command(name="add-manager", description="Add application manager")
    @check(ownership_check)
    @option_container_name()
    @slash_option(name='user', description="Discord User", opt_type=OptionType.USER, required=True)
    async def add_user_manager(self, ctx: SlashContext, user, container_name: str):

        await ctx.defer(ephemeral=True)
        try:
            result = db.add_user(int(user), application=container_name)

            if result:
                discord_user = await self.bot.fetch_user(user)
                username = discord_user.username
                await ctx.send(
                    f"Successfully added user {username} as an application manager for application {container_name}")

        except Exception as e:
            logger.warning(f"Could not add user {user} as an application manager due to {e}")
            await ctx.send(
                "Could not complete the operation, please try again later. View the logs for more information.")

    @check(ownership_check)
    @slash_command(name='remove-manager', description="remove a manager from an application")
    async def remove_app_manager(self, ctx: SlashContext, user, container_name: str):
        pass
    # Auto Complete ---------------------------------------------
    #
    @simple_start_container.autocomplete("container_name")
    async def autocomplete_start_container(self, ctx: AutocompleteContext):
        # Get user input from discord
        string_option_input = ctx.input_text
        string_option_input_lower = string_option_input.lower()
        # Get running containers
        options_running = c.get_stopped_containers()
        options_running.sort()
        print("Sorted: ", options_running)
        container_choices = []
        if ctx.input_text == "":
            count = 0
            for option in options_running:
                count += 1
                if count <= 25:
                    container_choices.append({"name": option, "value": option})

        else:
            for container in options_running:
                if string_option_input_lower in container.lower() and \
                        string_option_input_lower not in exclusion_list:
                    container_choices.append({"name": f'{container}', "value": f'{container}'})

            logging.info(f'Container found:{container_choices}')

        await ctx.send(choices=container_choices)

    @simple_stop_container.autocomplete("container_name")
    @simple_restart_container.autocomplete("container_name")
    async def autocomplete_stopped_containers(self, ctx: AutocompleteContext):
        # Get user input from discord
        string_option_input = ctx.input_text
        # Get running containers
        options_running = c.get_running_containers()
        options_running.sort()
        container_choices = []

        if ctx.input_text == "":
            count = 0
            for option in options_running:
                count += 1
                if count <= 25:
                    container_choices.append({"name": option, "value": option})

        else:
            for container in options_running:
                if (string_option_input == container or string_option_input in container.lower()) and \
                        string_option_input not in exclusion_list:
                    container_choices += [{"name": f'{container}', "value": f'{container}'}]
                    print(f'Searched for: {string_option_input} | Found: {container} ')
                    logging.info(f'Searched for: {string_option_input} | Found: {container} ')

        await ctx.send(choices=container_choices)

    @get_containers.autocomplete("container_name")
    async def autocomplete_running_containers(self, ctx: AutocompleteContext):
        # Get user input from discord
        string_option_input = ctx.input_text
        # Get running containers
        options_running = c.get_running_containers()
        options_running.sort()
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
    async def autocomplete_filter_get_containers(self, ctx: AutocompleteContext):
        # Get user input from discord
        string_option_input = ctx.input_text
        choices = [
            {"name": "Running", "value": "running"},
            {"name": "Exited", "value": "exited"},
            {"name": "All", "value": "all"}
        ]

        await ctx.send(choices=choices)

    @simple_get_container_logs.autocomplete("container_name")
    async def autocomplete_running_containers(self, ctx: AutocompleteContext):
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

    @add_user_manager.autocomplete("container_name")
    async def autocomplete_all_containers(self, ctx: AutocompleteContext):
        # Get user input from discord
        string_option_input = ctx.input_text
        string_option_input_lower = string_option_input.lower()
        # Get running containers
        options_ = c.get_all_containers()
        container_choices = []
        if ctx.input_text == "":
            count = 0
            for option in options_:
                count += 1
                if count <= 25:
                    container_choices.append({"name": option, "value": option})

        else:
            for container in options_:
                if string_option_input_lower in container.lower() and \
                        string_option_input_lower not in exclusion_list:
                    container_choices.append({"name": f'{container}', "value": f'{container}'})

            logging.info(f'Container found:{container_choices}')

        await ctx.send(choices=container_choices)
