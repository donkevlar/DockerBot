import os
import docker

from dotenv import load_dotenv


docker_container = False
local_connection = os.environ.get('RUNNING_LOCAL', False)

if not docker_container:
    load_dotenv('.env')


def docker_client_connect():
    port = os.environ.get('PORT')
    remote_ip = os.environ.get('REMOTE_IP')
    docker_host = f'tcp://{remote_ip}:{port}'

    # Try to connect locally
    if local_connection:
        try:
            client = docker.from_env()
        except TimeoutError or ConnectionError as e:
            print('Error: could not connect to docker host quitting!')
            exit()
    else:

        try:
            client = docker.DockerClient(base_url=docker_host)

        except TimeoutError or ConnectionError as e:
            print('Error: could not connect to docker host quitting!')
            exit()

    return client


def get_containers():
    client = docker_client_connect()
    # List all containers
    containers = client.containers.list(all=True)

    # create dictionary
    container_dict_name = {}
    container_dict_id = {}
    formatted_list = ""
    total_count = 0

    # Print container IDs and names
    for container in containers:
        total_count += 1
        # Create Formatted List
        formatted_list += f"{total_count}. Name: {container.name} , ID: {container.id}, " \
                          f"Status: {container.status}\n"

        # Create Dictionary by name
        container_dict_name[container.name] = (container.id, container.status)
        # Create Dictionary by ID
        container_dict_id[container.id] = (container.name, container.status)

    return container_dict_name, container_dict_id, formatted_list, total_count


def get_running_containers():
    client = docker_client_connect()
    containers = client.containers.list()
    running_containers = [container.name for container in containers if container.status == 'running']
    return running_containers


def get_stopped_containers():
    client = docker_client_connect()
    containers = client.containers.list()
    stopped_containers = [container.name for container in containers if container.status == 'exited']
    return stopped_containers


def restart_container(container_id_or_name):
    client = docker_client_connect()

    try:
        container = client.containers.get(container_id_or_name)

        container.restart()
        print(f"Successfully Restarted Container: {container_id_or_name}\n")

    except Exception as e:
        print(f"Error: {e}")


def stop_container(container_id_or_name):

    # Connect to docker host
    client = docker_client_connect()

    containers = client.containers.list(all=True)

    for container in containers:
        if container.name == container_id_or_name and container.status == "running":
            try:
                container = client.containers.get(container_id_or_name)
                container.stop()
                print(f"Successfully Stopped Container: {container_id_or_name}\n")

            except Exception as e:
                print(f"Error: {e}")

        elif container.name == container_id_or_name and container.status != "running":
            print("Unsuccessful: Docker is either already stopped or the ID entered is not valid.")


def start_container(container_id_or_name):
    # Connect to docker host
    client = docker_client_connect()

    containers = client.containers.list(all=True)

    for container in containers:
        if container.name == container_id_or_name and container.status == "exited":
            try:
                container = client.containers.get(container_id_or_name)
                container.start()
                print(f"Successfully Started Container: {container_id_or_name}\n")

            except Exception as e:
                print(f"Error: {e}")

        elif container.name == container_id_or_name and container.status != "exited":
            print("Unsuccessful: Docker is either already running or the ID entered is not valid.")


if __name__ == '__main__':

    start_container('FoundryVTT')
