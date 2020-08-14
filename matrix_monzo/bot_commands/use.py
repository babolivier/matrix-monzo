from nio import MatrixRoom, RoomMessageText

from matrix_monzo.bot_commands import Command, runner
from matrix_monzo.messages import messages
from matrix_monzo.utils import search_through_accounts
from matrix_monzo.utils.errors import InvalidParamsError


class UseCommand(Command):
    PREFIX = "use"
    PARAMS = ["account"]
    HELP_DOC = "Use the given account account in future commands. Required for showing and interacting with pots."

    @runner
    async def run(self, event: RoomMessageText, room: MatrixRoom):
        params = self._body_to_list(event.body)

        accounts, _ = self.instance.get_monzo_accounts_for_search()
        matches = search_through_accounts("".join(params[1:]), {}, accounts)

        if len(matches) == 0:
            raise InvalidParamsError(
                messages.get_content(
                    message_id="no_match_error",
                    entity="account",
                )
            )
        if len(matches) > 1:
            raise InvalidParamsError(
                messages.get_content(
                    message_id="too_many_matches_error",
                    entity="account",
                    match_ids=", ".join([account_id for account_id, index in matches]),
                )
            )

        account_id = matches[0][0]
        self.instance.storage.selected_account_store.set_selected_account(
            event.sender, account_id,
        )

        return messages.get("use_success", account_id=account_id)


command_class = UseCommand
