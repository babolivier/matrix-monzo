from typing import Dict


class ConfigError(RuntimeError):
    """An error encountered during reading the config file

    Args:
        msg (str): The message displayed to the user on error
    """
    def __init__(self, msg):
        super(ConfigError, self).__init__("%s" % (msg,))


class MonzoInvalidStateError(RuntimeError):
    def __init__(self):
        super(MonzoInvalidStateError, self).__init__("Invalid state in the login callback")


class ClientError(Exception):
    """An error that contains data to send to the user's client.

    Args:
        message_content: The content of the m.room.message event to send the user.
    """
    def __init__(self, message_content: Dict[str, str]):
        self.message_content = message_content


class InvalidParamsException(ClientError):
    pass


class ProcessingError(ClientError):
    pass
