from typing import Dict, List

from nio import RoomMessageText, MatrixRoom

from matrix_monzo.bot_commands import Command, runner
from matrix_monzo.messages import messages


class LogoutCommand(Command):
    PREFIX = "logout"
    PARAMS = []
    HELP_DOC = "Log the current user out of Monzo."

    @runner
    async def run(self, event: RoomMessageText, room: MatrixRoom) -> Dict[str, str]:
        self.instance.invalidate_monzo_token()
        return messages.get_content("logout_success")


command_class = LogoutCommand