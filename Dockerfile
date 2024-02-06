# official Python runtime as a base image
FROM python:3.11-slim

# Use an official MongoDB runtime as a base image
# FROM mongo:latest

# Set the working directory to /AudiblePy
WORKDIR /DockerBot

# Copy the current directory contents into the container at /app
COPY Scripts/bot.py /DockerBot
COPY Scripts/docker_commands.py /DockerBot
COPY Scripts/requirements.txt /DockerBot
COPY Scripts/settings.py /DockerBot

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

RUN set -ex \
    && apt-get update \
    && apt-get upgrade -y \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*



CMD ["python", "bot.py"]