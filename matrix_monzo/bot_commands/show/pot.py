from typing import Dict

from nio import MatrixRoom, RoomMessageText

from matrix_monzo.bot_commands import runner, SubCommand
from matrix_monzo.messages import messages
from matrix_monzo.utils import (
    format_date,
    format_bool,
)
from matrix_monzo.utils.errors import InvalidParamsError


class PotCommand(SubCommand):
    PARENT = "show"
    PREFIX = "pot"
    PARAMS = ["pot"]
    HELP_DOC = "Show a single pot."

    async def run(self, event: RoomMessageText, room: MatrixRoom) -> Dict[str, str]:
        raise NotImplementedError()

    @runner
    async def run_with_params(
        self, params: str, event: RoomMessageText, room: MatrixRoom,
    ) -> Dict[str, str]:
        pots, raw_res = self.instance.get_monzo_pots_for_search()

        pot = self._get_pot_from_params(params, pots, raw_res)

        balance_formatted = "%.2f %s" % (
            pot["balance"] / 100,
            pot["currency"],
        )

        pot_type = messages.get(
            message_id="show_one_pot_type_unknown",
            type=pot["type"],
        )
        if pot["type"] == "default":
            pot_type = messages.get("show_one_pot_type_default")
        elif pot["type"] == "flexible_savings":
            pot_type = messages.get("show_one_pot_type_flexible_savings")

        if pot["isa_wrapper"]:
            pot_type += " (%s)" % pot["isa_wrapper"]

        return messages.get_content(
            message_id="show_one_pot_res",
            format_markdown=True,
            name=pot["name"],
            balance_with_currency=balance_formatted,
            type=pot_type,
            round_up=format_bool(pot["round_up"]),
            locked=format_bool(pot["locked"]),
            bills=format_bool(pot["available_for_bills"]),
            creation_date=format_date(pot["created"]),
            last_update=format_date(pot["updated"]),
            id=pot["id"],
        )

    def _get_pot_from_params(
        self, params: str, pots: dict, raw_res: dict,
    ) -> dict:
        matches = set()

        for name, pot_id in pots.items():
            if name in params or pot_id in params:
                matches.add(pot_id)

        if not matches:
            raise InvalidParamsError(
                messages.get_content(
                    message_id="no_match_error",
                    entity="pot",
                )
            )
        elif len(matches) > 1:
            raise InvalidParamsError(
                messages.get_content(
                    message_id="too_many_matches_error",
                    entity="pot",
                    match_ids=", ".join([pot_id for pot_id in matches]),
                )
            )

        pot_id = list(matches)[0]

        return self._get_pot_from_id(pot_id, raw_res)

    def _get_pot_from_id(self, pot_id: str, raw_res: dict) -> dict:
        for pot in raw_res["pots"]:
            if pot["id"] == pot_id:
                return pot

        raise InvalidParamsError(
            messages.get_content(
                message_id="no_match_error",
                entity="pot",
            )
        )


command_class = PotCommand
