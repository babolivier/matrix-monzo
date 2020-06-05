from nio import MatrixRoom, RoomMessageText

from matrix_monzo.bot_commands import Command, runner


class SayCommand(Command):
    PREFIX = "say"
    PARAMS = ["word"]
    HELP_DOC = ""

    @runner
    async def run(self, event: RoomMessageText, room: MatrixRoom):
        params = self._body_to_params_dict(event.body)
        return params["word"]


command_class = SayCommand
