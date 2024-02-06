import os
import docker
import logging

from dotenv import load_dotenv

docker_container = True

if not docker_container:
    load_dotenv('.env')

local_connection = os.environ.get('RUNNING_LOCAL', False)

logging.info(f"{os.environ.get('RUNNING_LOCAL')}")
logging.info(f"{os.environ.get('PORT')}")
logging.info(f"{os.environ.get('REMOTE_IP')}")


def docker_client_connect(output: str = None):
    port = os.environ.get('PORT')
    remote_ip = os.environ.get('REMOTE_IP')
    docker_host = f'tcp://{remote_ip}:{port}'

    success_conn = False

    # Try to connect locally
    if local_connection:
        try:
            client = docker.from_env()
            success_conn = True
            if output is None:
                pass
            else:
                print("successfully connected to host via local connection")
                logging.info("successfully connected to host via local connection")
        except TimeoutError or ConnectionError as e:
            print('Error: could not connect to docker host quitting!')
            logging.warning('Error: could not connect to docker host quitting!')
            exit()
    else:

        try:
            client = docker.DockerClient(base_url=docker_host)
            success_conn = True
            if output is None:
                pass
            else:
                print(f"successfully connected to host via URL {docker_host}")
                logging.info(f"successfully connected to host via URL {docker_host}")

        except TimeoutError or ConnectionError as e:
            print('Error: could not connect to docker host quitting!')
            logging.warning('Error: could not connect to docker host quitting!')
            exit()

    return client


def get_containers():
    client = docker_client_connect()
    # List all containers
    containers = client.containers.list()
    all_containers = [container.name for container in containers]
    return all_containers


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

    container = client.containers.get(container_id_or_name)

    container.restart()
    print(f"Successfully Restarted Container: {container_id_or_name}\n")


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

    restart_container('Palworld')
