from nio import RoomMessageText

from matrix_monzo.bot_commands import Command, runner


class SayCommand(Command):
    PREFIX = "say"
    PARAMS = ["word"]
    HELP_DOC = "Repeat a given expression. Useful to debug command routing."

    @runner
    async def run(self, event: RoomMessageText):
        params = self.string_to_params(event.body)
        return params["word"]


command_class = SayCommand
