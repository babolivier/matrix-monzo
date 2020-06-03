from typing import Dict

from nio import MatrixRoom, RoomMessageText

from matrix_monzo.bot_commands import runner, SubCommand
from matrix_monzo.messages import messages


class PotsCommand(SubCommand):
    PARENT = "show"
    PREFIX = "pots"
    PARAMS = []
    HELP_DOC = "Show a user's open pots."

    async def run(self, event: RoomMessageText, room: MatrixRoom) -> Dict[str, str]:
        raise NotImplementedError()

    @runner
    async def run_with_params(
            self, params: str, event: RoomMessageText, room: MatrixRoom,
    ) -> Dict[str, str]:
        res = self.instance.monzo_client.get_pots()

        pots = []
        for pot in res["pots"]:
            # TODO: Maybe implement a "show all pots" command that include deleted pots?
            if pot["deleted"]:
                continue

            pots.append(
                messages.get(
                    message_id="pot_entry",
                    name=pot["name"],
                    balance=pot["balance"] / 100,
                    currency=pot["currency"],
                    id=pot["id"],
                )
            )

        return messages.get_content(
            message_id="pots",
            format_markdown=True,
            pots="\n".join(pots),
        )


command_class = PotsCommand
