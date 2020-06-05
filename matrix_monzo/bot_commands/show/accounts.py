from typing import Any, Dict, List

from nio import MatrixRoom, RoomMessageText

from matrix_monzo.bot_commands import runner, SubCommand
from matrix_monzo.messages import messages
from matrix_monzo.utils import build_account_description
from matrix_monzo.utils.errors import ProcessingError


class AccountsCommand(SubCommand):
    PARENT = "show"
    PREFIX = "accounts"
    PARAMS = []
    HELP_DOC = "Show a user's open accounts."

    async def run(self, event: RoomMessageText, room: MatrixRoom) -> Dict[str, str]:
        raise NotImplementedError()

    @runner
    async def run_with_params(
            self, params: str, event: RoomMessageText, room: MatrixRoom,
    ) -> Dict[str, str]:
        return self.get_accounts()

    def get_accounts(self, include_closed: bool = False):
        accounts_res = self.instance.monzo_client.get_accounts()  # type: Dict[str, List[Dict[Any]]]

        if len(accounts_res["accounts"]) == 0:
            raise ProcessingError(messages.get_content("account_no_accounts_error"))

        accounts = []
        for account in accounts_res["accounts"]:
            if account["closed"] and not include_closed:
                continue

            balance_res = self.instance.monzo_client.get_balance(account["id"])
            balance_formatted = "%.2f" % (balance_res["balance"] / 100)

            message_id = "account_entry"
            if account["closed"]:
                # We don't have to check include_closed here because if the account is
                # closed and include_closed was false we'd already jumped to the next
                # iteration.
                message_id += "_closed"

            accounts.append(messages.get(
                message_id=message_id,
                description=build_account_description(account),
                balance=balance_formatted,
                currency=account["currency"],
                id=account["id"],
            ))

        return messages.get_content(
            message_id="accounts",
            format_markdown=True,
            accounts="\n".join(accounts),
        )


command_class = AccountsCommand
