from typing import Dict, List

from nio import RoomMessageText

from bot_commands import SubCommand
from utils import to_event_content


class AccountsCommand(SubCommand):
    PARENT = "show"
    PREFIX = "accounts"
    PARAMS = []
    HELP_DOC = "Show a user's accounts."

    async def run(self, event: RoomMessageText) -> Dict[str, str]:
        raise NotImplementedError()

    async def run_with_params(
            self, params: str, event: RoomMessageText
    ) -> Dict[str, str]:
        return to_event_content("success!")


command_class = AccountsCommand
