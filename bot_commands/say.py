from nio import RoomMessageText

from bot_commands import Command, runner


class SayCommand(Command):
    PREFIX = "say"
    PARAMS = ["expression"]

    @runner
    async def run(self, event: RoomMessageText):
        params = self.body_to_params(event.body)
        return params["expression"]


command_class = SayCommand
