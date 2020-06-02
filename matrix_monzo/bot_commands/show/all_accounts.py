from typing import Dict

from nio import MatrixRoom, RoomMessageText

from matrix_monzo.bot_commands import runner
from matrix_monzo.bot_commands.show.accounts import AccountsCommand


class AllAccountsCommand(AccountsCommand):
    PREFIX = "all accounts"
    HELP_DOC = "Show a user's accounts, both open and closed. Closed accounts will be displayed striked through."

    async def run(self, event: RoomMessageText, room: MatrixRoom) -> Dict[str, str]:
        raise NotImplementedError()

    @runner
    async def run_with_params(
            self, params: str, event: RoomMessageText, room: MatrixRoom,
    ) -> Dict[str, str]:
        return self.get_accounts(include_closed=True)


command_class = AllAccountsCommand
