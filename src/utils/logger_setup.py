import json
import logging.config

from constants import common_constants as constant

def setup_logging():
    with open(constant.LOGGING_CONFIG_FILE, "r", encoding="utf-8") as file:
        config = json.load(file)

    logging.config.dictConfig(config)