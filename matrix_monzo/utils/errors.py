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
