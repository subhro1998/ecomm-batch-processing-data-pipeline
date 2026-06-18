import json
import logging.config

from src.constants import common_constants


def setup_logging():
    with open(common_constants.LOGGING_CONFIG_FILE, "r", encoding="utf-8") as file:
        config = json.load(file)

    logging.config.dictConfig(config)