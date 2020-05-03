from typing import Any, Dict, List

from nio import RoomMessageText

from bot_commands import SubCommand
from messages import messages


class AccountsCommand(SubCommand):
    PARENT = "show"
    PREFIX = "accounts"
    PARAMS = []
    HELP_DOC = "Show a user's open accounts."

    async def run(self, event: RoomMessageText) -> Dict[str, str]:
        raise NotImplementedError()

    async def run_with_params(
            self, params: str, event: RoomMessageText
    ) -> Dict[str, str]:
        return self.get_accounts()

    def get_accounts(self, include_closed: bool = False):
        accounts_res = self.instance.monzo_client.get_accounts()  # type: Dict[str, List[Dict[Any]]]

        accounts = []
        for account in accounts_res["accounts"]:
            if account["closed"] and not include_closed:
                continue

            balance_res = self.instance.monzo_client.get_balance(account["id"])
            balance = balance_res["balance"] / 100

            message_id = "account_entry"
            if account["closed"]:
                # We don't have to check include_closed here because if the account is
                # closed and include_closed was false we'd already jumped to the next
                # iteration.
                message_id += "_closed"

            accounts.append(messages.get(
                message_id=message_id,
                description=account["description"],
                balance=balance,
                currency=account["currency"],
                id=account["id"],
            ))

        return messages.get_content(
            message_id="accounts",
            format_markdown=True,
            accounts="\n".join(accounts),
        )


command_class = AccountsCommand
