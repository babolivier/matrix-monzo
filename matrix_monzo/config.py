import logging
import os
import re
import sys

import yaml

from matrix_monzo.utils.errors import ConfigError

logger = logging.getLogger()


class Config(object):
    # Default Oauth2 client credentials. These credentials are for a non-confidential app,
    # which means it isn't given a refresh token, and users need to re-auth every now and
    # then. Users can change this by overriding these credentials with ones for a
    # confidential app.
    DEFAULT_CLIENT_ID = "oauth2client_00009vYJnWrxXmMxnpWLSL"
    DEFAULT_CLIENT_SECRET = (
        "mnzpub.p8xIoxEn5HSPmeSsgYloROfT9ZZZ2u7VhONAOrJTUsy4Y7Gj"
        "ZFfuDGvtiE+phlnGkPiELuDTcvTSdd7cMDxh"
    )

    def __init__(self, filepath: str):
        """Load the config file at the given path, and configure the logging.

        Args:
            filepath: Path to config file
        """
        if not os.path.isfile(filepath):
            raise ConfigError(f"Config file '{filepath}' does not exist")

        # Load in the config file at the given file path.
        with open(filepath) as file_stream:
            config = yaml.full_load(file_stream.read())

        # Configure logging format.
        formatter = logging.Formatter('%(asctime)s | %(name)s [%(levelname)s] %(message)s')

        # Set the log level, falling back to INFO if none was provided.
        log_dict = config.get("logging", {})
        log_level = log_dict.get("level", "INFO")
        logger.setLevel(log_level)

        # If configured so, set a file logging handler.
        file_logging = log_dict.get("file_logging", {})
        file_logging_enabled = file_logging.get("enabled", False)
        if file_logging_enabled:
            file_logging_filepath = file_logging.get("filepath", "matrix-monzo.log")
            handler = logging.FileHandler(file_logging_filepath)
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        # If configured so, set a console logging handler.
        console_logging = log_dict.get("console_logging", {})
        console_logging_enabled = console_logging.get("enabled", True)
        if console_logging_enabled:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        # peewee (used by nio's storage layer) is very verbose when logging at the DEBUG
        # level, so we're forcing it to the INFO level so the debug logs are readable.
        logging.getLogger("peewee").setLevel("INFO")

        # Database setup.
        self.database = config.get("database", {})

        # Matrix bot account setup.
        matrix = config.get("matrix", {})

        # Configure the bot's user ID.
        self.user_id = matrix.get("user_id")
        if not self.user_id:
            raise ConfigError("matrix.user_id is a required field")
        elif not re.match("@.*:.*", self.user_id):
            raise ConfigError("matrix.user_id must be in the form @name:domain")

        # Configure the bot's password.
        self.password = matrix.get("password")
        if not self.password:
            raise ConfigError("matrix.password is a required field")

        # Configure the device ID the bot is going to use.
        self.device_id = matrix.get("device_id")
        if not self.device_id:
            raise ConfigError("matrix.device_id is a required field")

        # Configure the URL the bot will connect to.
        self.homeserver_url = matrix.get("homeserver_url")
        if not self.homeserver_url:
            raise ConfigError("matrix.homeserver_url is a required field")

        # Configure the bot's owner, i.e. the only user the bot will interact with.
        self.owner_id = matrix.get("owner_id")
        if not self.owner_id:
            raise ConfigError("matrix.owner_id is a required field")
        elif not re.match("@.*:.*", self.user_id):
            raise ConfigError("matrix.owner_id must be in the form @name:domain")

        # Configure the path where nio will store encryption and sync data.
        self.store_path = matrix.get("store_path")
        if not self.store_path:
            raise ConfigError("matrix.store_path is a required field")

        # Monzo setup.
        monzo = config.get("monzo", {})

        # Oauth2 app credentials, default to the default credentials.
        self.monzo_client_id = monzo.get("client_id", self.DEFAULT_CLIENT_ID)
        self.monzo_client_secret = monzo.get("client_secret", self.DEFAULT_CLIENT_SECRET)

        # HTTP setup.
        http = config.get("http", {})

        # The address to which to bind the aiohttp listener.
        self.http_address = http.get("bind_address")
        if not self.http_address:
            raise ConfigError("http.bind_address is a required field")

        # The port the aiohttp listener will use.
        self.http_port = http.get("port")
        if not self.http_port:
            raise ConfigError("http.port is a required field")

        # The public base URL for the HTTP server. Used to tell the Monzo API where to
        # redirect after logging in, and where to send webhooks.
        self.http_baseurl = http.get("public_baseurl")
        if not self.http_port:
            raise ConfigError("http.public_baseurl is a required field")
