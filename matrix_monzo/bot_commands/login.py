from nio import MatrixRoom, RoomMessageText

from matrix_monzo.bot_commands import Command, runner
from matrix_monzo.messages import messages


class LoginCommand(Command):
    PREFIX = "login"
    PARAMS = []
    HELP_DOC = "Authenticate against the Monzo API."

    @runner
    async def run(self, event: RoomMessageText, room: MatrixRoom):
        if self.instance.is_logged_in():
            return messages.get_content("login_already_logged_in")

        return messages.get_content(
            message_id="login",
            format_markdown=True,
            login_url=self.instance.get_monzo_login_url(room.room_id),
        )


command_class = LoginCommand
