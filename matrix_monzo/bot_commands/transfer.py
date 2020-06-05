from matrix_monzo.bot_commands.move import MoveCommand


class TransferCommand(MoveCommand):
    PREFIX = "transfer"
    PARAMS = ["amount", "source", "destination"]
    HELP_DOC = "Alias for the `move` command. See the documentation for the `move` command for more details on how to use this command."


command_class = TransferCommand