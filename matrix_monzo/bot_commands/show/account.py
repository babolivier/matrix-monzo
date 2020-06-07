from typing import Dict

from nio import MatrixRoom, RoomMessageText

from matrix_monzo.bot_commands import runner, SubCommand
from matrix_monzo.messages import messages
from matrix_monzo.utils import (
    build_account_description,
    format_date,
    search_through_accounts,
)
from matrix_monzo.utils.errors import InvalidParamsError


class AccountCommand(SubCommand):
    PARENT = "show"
    PREFIX = "account"
    PARAMS = ["account"]
    HELP_DOC = "Show a single account. The final parameter can be omitted if only one current account is linked to the current Monzo user."

    async def run(self, event: RoomMessageText, room: MatrixRoom) -> Dict[str, str]:
        raise NotImplementedError()

    @runner
    async def run_with_params(
        self, params: str, event: RoomMessageText, room: MatrixRoom,
    ) -> Dict[str, str]:
        accounts, raw_res = self.instance.get_monzo_accounts_for_search()

        if len(accounts) == 1:
            account_id = list(accounts.values())[0]
            account = self._get_account_from_id(account_id, raw_res)
        else:
            account = self._get_account_from_params(params, accounts, raw_res)

        balance_res = self.instance.monzo_client.get_balance(account["id"])
        balance_formatted = "%.2f %s" % (
            balance_res["balance"] / 100,
            account["currency"],
        )

        owners = "\n"
        for owner in account["owners"]:
            owners += messages.get(
                message_id="show_one_account_owner_entry",
                name=owner["preferred_name"],
            )

        return messages.get_content(
            message_id="show_one_account_res",
            format_markdown=True,
            description=build_account_description(account),
            balance_with_currency=balance_formatted,
            country_code=account["country_code"],
            account_number=account["account_number"],
            sort_code=account["sort_code"],
            owners=owners,
            creation_date=format_date(account["created"]),
            id=account["id"],
        )

    def _get_account_from_params(
        self, params: str, accounts: dict, raw_res: dict,
    ) -> dict:
        matches = search_through_accounts(params, {}, accounts)

        if not matches:
            raise InvalidParamsError(
                messages.get_content(
                    message_id="show_one_no_match_error",
                    entity="account",
                )
            )
        elif len(matches) > 1:
            raise InvalidParamsError(
                messages.get_content(
                    message_id="show_one_too_many_matches_error",
                    entity="account",
                    match_ids=[account_id for account_id, index in matches],
                )
            )

        account_id, _ = matches[0]

        return self._get_account_from_id(account_id, raw_res)

    def _get_account_from_id(self, account_id: str, raw_res: dict) -> dict:
        for account in raw_res["accounts"]:
            if account["id"] == account_id:
                return account

        raise InvalidParamsError(
            messages.get_content(
                message_id="show_one_no_match_error",
                entity="account",
            )
        )

command_class = AccountCommand