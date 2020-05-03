from typing import Dict

from nio import RoomMessageText

from bot_commands.show.accounts import AccountsCommand


class AllAccountsCommand(AccountsCommand):
    PREFIX = "all accounts"
    HELP_DOC = "Show a user's accounts, both open and closed. Accounts that are striked through are closed."

    async def run(self, event: RoomMessageText) -> Dict[str, str]:
        raise NotImplementedError()

    async def run_with_params(
            self, params: str, event: RoomMessageText
    ) -> Dict[str, str]:
        return self.get_accounts(include_closed=True)


command_class = AllAccountsCommand
