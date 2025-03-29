import os
import logging
from logging.config import dictConfig
from dotenv import load_dotenv

load_dotenv()

versionNumber = '1.0.2'
logging.info(f'Starting DockerBot! Version: {versionNumber}')

DISCORD_API_SECRET = os.getenv('DISCORD_API_SECRET')

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,  # Fixed typo: disabled_existing_loggers should be disable_existing_loggers
    "formatters": {
        "verbose": {
            "format": "%(levelname)-5s - %(asctime)s - %(module)-5s : %(message)s",
            "datefmt": "%H:%M:%S",  # Apply datefmt here for verbose formatter
        },
        "standard": {
            "format": "%(levelname)-5s - %(asctime)s : %(message)s",
            "datefmt": "%H:%M:%S",  # Apply datefmt here for standard formatter
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "console2": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
    },
    "loggers": {
        "bot": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "discord": {
            "handlers": ["console2"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

dictConfig(LOGGING_CONFIG)
