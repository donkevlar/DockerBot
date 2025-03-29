# official Python runtime as a base image
FROM python:3.12-slim


# Set the working directory to /AudiblePy
WORKDIR /DockerBot

# Copy the current directory contents into the container at /app
COPY scripts/ /DockerBot

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

RUN set -ex \
    && apt-get update \
    && apt-get upgrade -y \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*



CMD ["python", "main.py"]