import logging
import os
import re
import sys

import yaml

from errors import ConfigError

logger = logging.getLogger()


class Config(object):
    def __init__(self, filepath):
        """
        Args:
            filepath (str): Path to config file
        """
        if not os.path.isfile(filepath):
            raise ConfigError(f"Config file '{filepath}' does not exist")

        # Load in the config file at the given filepath
        with open(filepath) as file_stream:
            config = yaml.full_load(file_stream.read())

        # Logging setup
        formatter = logging.Formatter('%(asctime)s | %(name)s [%(levelname)s] %(message)s')

        log_dict = config.get("logging", {})
        log_level = log_dict.get("level", "INFO")
        logger.setLevel(log_level)

        file_logging = log_dict.get("file_logging", {})
        file_logging_enabled = file_logging.get("enabled", False)
        file_logging_filepath = file_logging.get("filepath", "bot.log")
        if file_logging_enabled:
            handler = logging.FileHandler(file_logging_filepath)
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        console_logging = log_dict.get("console_logging", {})
        console_logging_enabled = console_logging.get("enabled", True)
        if console_logging_enabled:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        # Database setup
        self.database = config.get("database", {})

        # Matrix bot account setup
        matrix = config.get("matrix", {})

        self.user_id = matrix.get("user_id")
        if not self.user_id:
            raise ConfigError("matrix.user_id is a required field")
        elif not re.match("@.*:.*", self.user_id):
            raise ConfigError("matrix.user_id must be in the form @name:domain")

        self.password = matrix.get("password")
        if not self.password:
            raise ConfigError("matrix.password is a required field")

        self.device_id = matrix.get("device_id")

        self.homeserver_url = matrix.get("homeserver_url")
        if not self.homeserver_url:
            raise ConfigError("matrix.homeserver_url is a required field")

        self.owner_id = matrix.get("owner_id")
        if not self.owner_id:
            raise ConfigError("matrix.owner_id is a required field")
        elif not re.match("@.*:.*", self.user_id):
            raise ConfigError("matrix.owner_id must be in the form @name:domain")

        self.store_path = matrix.get("store_path")
        if not self.store_path:
            raise ConfigError("matrix.store_path is a required field")

        monzo = config.get("monzo", {})

        self.monzo_access_token = monzo.get("access_token")
        if not self.monzo_access_token:
            raise ConfigError("monzo.access_token is a required field")
