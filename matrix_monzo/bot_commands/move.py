from typing import Dict, List, Union

from nio import MatrixRoom, RoomMessageText

from matrix_monzo.bot_commands import Command, runner
from matrix_monzo.messages import messages
from matrix_monzo.utils.errors import InvalidParamsException

SUPPORTED_CURRENCIES = ["£", "GBP", "$", "USD"]


class MoveCommand(Command):
    PREFIX = "move"
    PARAMS = ["amount", "source", "destination"]
    HELP_DOC = "Move money between pots or accounts. Prepend the source with a \"from\" and the destination with a \"to\" for more accuracy."

    @runner
    async def run(self, event: RoomMessageText, room: MatrixRoom):
        pots = self._get_pots()
        accounts = self._get_accounts()
        params = self._get_params(event.body, pots, accounts)

        # We don't want to deal with transfers where the destination and the source are
        # the same. We could, if it's a pot, but it's better to just raise an error here.
        if params["source"]["id"] == params["destination"]["id"]:
            raise InvalidParamsException(
                messages.get_content("move_same_account_pot_error")
            )

        return messages.get_content("debug_parse_success", params=params)

    def _get_params(self, body: str, pots: dict, accounts: dict) -> dict:
        # This is a long command that doesn't use commas in its grammar, so just to
        # ensure none get in the way we replace it with a space, so str.split() does the
        # right thing.
        body = body.replace(",", " ")
        params_l = self._body_to_list(body)

        if "from" in params_l or "to" in params_l:
            return self._get_to_from_params(params_l, pots, accounts)
        else:
            return self._get_basic_params(params_l, pots, accounts)

    def _get_basic_params(self, params_l: list, pots: dict, accounts: dict) -> dict:
        # Retrieve the amount to transfer.
        params = {"amount": self._process_amount(params_l[0])}

        # Remove the amount from the remaining params so it doesn't get in the way.
        params_l.pop(0)

        # If the amount was provided in the form "10 GPB", catch that and also remove the
        # currency.
        if params_l[1] in SUPPORTED_CURRENCIES:
            params_l.pop(0)

        # Stringify the params as, from here, it's easier to work with strings.
        params_s = " ".join(params_l)

        # Pots or accounts that match the params string.
        # For each match, we're storing its index in the string so that we can figure
        # out which is the source and which is the destination, along with its type
        # (i.e. pot vs account) so we can figure out which API calls to make.
        matches: List[dict] = []

        # Attempt to match a pot's name or ID with a section of the params string.
        for name, pot_id in pots.items():
            index = None

            if name.casefold() in params_s:
                index = params_s.index(name.casefold())
            elif pot_id in params_s:
                index = params_s.index(pot_id)

            if index is not None:
                matches.append(
                    {
                        "id": pot_id,
                        "type": "pot",
                        "index": index,
                    }
                )

        # Retrieve the accounts that might have a match in the params string.
        account_matches = self._search_through_accounts(params_s, pots, accounts)
        matches += account_matches

        match_ids = [match["id"] for match in matches]

        # We need two matches: one source and one destination. If we don't have that,
        # tell the user we can't process this result.
        if len(matches) != 2:
            raise InvalidParamsException(
                messages.get_content(
                    message_id="move_wrong_match_number_error",
                    nb_match=len(matches),
                    match_ids=", ".join(match_ids),
                )
            )

        # If both matches have the same index, then we don't really have two matches.
        if matches[0]["index"] == matches[1]["index"]:
            raise InvalidParamsException(
                messages.get_content("move_basic_parse_error")
            )

        # Figure out the source and destination depending on which match
        if matches[0]["index"] > matches[1]["index"]:
            params["source"] = matches[0]
            params["destination"] = matches[1]
        else:
            params["source"] = matches[1]
            params["destination"] = matches[0]

        return params

    def _get_to_from_params(self, params_l: list, pots: dict, accounts: dict) -> dict:
        # Make sure we have both a "from" and a "to".
        err_content = None
        if "from" in params_l and "to" not in params_l:
            err_content = messages.get_content(
                message_id="move_to_from_missing_error",
                param_found="from",
                param_not_found="to",
                direction_found="source",
                direction_not_found="destination",
            )
        if "to" in params_l and "from" not in params_l:
            err_content = messages.get_content(
                message_id="move_to_from_missing_error",
                param_found="to",
                param_not_found="from",
                direction_found="destination",
                direction_not_found="source",
            )

        # Make sure neither the "from" nor the "to" is starting the command.
        if params_l.index("from") == 0 or params_l.index("to") == 0:
            err_content = messages.get_content("move_to_from_start_error")

        # If one of the previous checks failed, raise the error.
        if err_content:
            raise InvalidParamsException(err_content)

        params: Dict[str, Union[dict, str, float]] = {}

        # Get the index of the "from" and the index of the "to".
        from_index = params_l.index("from")
        to_index = params_l.index("to")

        # Figure out which came first and extract the source and the destination
        # accordingly.
        if to_index < from_index:
            first_direction_index = to_index
            source = " ".join(params_l[to_index+1:from_index])
            destination = " ".join(params_l[from_index+1:])
        else:
            # We don't need to check for equality between the indexes because at
            # this point know both words exist as distinct elements of the list, and
            # thus have different indexes.
            first_direction_index = from_index
            source = " ".join(params_l[from_index+1:to_index])
            destination = " ".join(params_l[to_index+1:])

        # Extract and process the amount, and the currency if it's provided.
        amount_with_maybe_currency = "".join(params_l[:first_direction_index])
        params["amount"] = self._process_amount(amount_with_maybe_currency)

        def _search_in_pots(s, param_key):
            # Check if the param is a perfect match with the name of a pot.
            if s in pots.keys():
                params[param_key] = {
                    "id": pots[s],
                    "type": "pot",
                }

                return

            # Check if at least one pot could be matched against the param.
            # We also check whether the ID of a pot is mentioned in the param, in which
            # case we consider it a perfect match and return immediately.
            match_ids = []
            for name, pot_id in pots.items():
                if name in s:
                    match_ids.append(pot_id)
                elif pot_id.casefold() in s:
                    params[param_key] = {
                        "id": pot_id,
                        "type": "pot",
                    }

                    return

            # If we got more than one match, then the command is too ambiguous for us.
            # Tell the user that, and also tell them they can use IDs (which this error
            # message does).
            if len(match_ids) > 1:
                raise InvalidParamsException(
                    messages.get_content(
                        message_id="move_wrong_number_for_direction_error",
                        direction=param_key,
                        nb_match=len(match_ids),
                        match_ids=", ".join(match_ids)
                    )
                )

            # If we got a match (because at this point we can't have more than one), go
            # with it.
            if len(match_ids):
                params[param_key] = {
                    "id": match_ids[0],
                    "type": "pot",
                }

        # Try to match the source and the destination against pot names and IDs.
        _search_in_pots(source, "source")
        _search_in_pots(destination, "destination")

        def _search_in_accounts(s, param_key):
            # Try to match the param to an account.
            account_matches = self._search_through_accounts(s, pots, accounts)

            # If we got more than one match, or we got a match but we've already matched
            # a pot, then raise an error.
            if (
                len(account_matches) and param_key in params.keys()
                or len(account_matches) > 1
            ):
                match_ids = [match["id"] for match in account_matches]
                match_ids += params[param_key]["id"]
                raise InvalidParamsException(
                    messages.get_content(
                        message_id="move_wrong_number_for_direction_error",
                        direction=param_key,
                        nb_match=len(account_matches) + 1,
                        match_ids=", ".join(match_ids)
                    )
                )

            # If we got a match (because at this point we can't have more than one), go
            # with it.
            if len(account_matches):
                params[param_key] = {
                    "id": account_matches[0]["id"],
                    "type": "account",
                }

        # Try to match the source and the destination against account names and IDs.
        _search_in_accounts(source, "source")
        _search_in_accounts(destination, "destination")

        return params

    def _process_amount(self, amount: str) -> float:
        # Check if the param can be used as a number as is.
        if self._can_parse_into_float(amount):
            return float(amount)
        else:
            # Loop over supported currencies to see if we can find one in the param.
            for currency in SUPPORTED_CURRENCIES:
                # The currency is expected to be
                if amount.endswith(currency) or amount.startswith(currency):
                    # Replace the currency with nothing, then see if we can use the
                    # resulting string as a number.
                    amount = amount.replace(currency, "")
                    if self._can_parse_into_float(amount):
                        return float(amount)

            # If no match were found, then tell the user we don't support the currency.
            # We don't need the currency to do the transfer, so it's just a check to make
            # sure we do the transfer as the user intends.
            raise InvalidParamsException(
                messages.get_content(
                    message_id="move_unsupported_currency_error",
                    currencies_and_symbols=", ".join(SUPPORTED_CURRENCIES),
                )
            )

    def _search_through_accounts(self, s: str, pots: dict, accounts: dict) -> List[dict]:
        matches = []

        # If there's only one account, then we can add "account" (so we match "my
        # account", "main account", "current account", etc.) as the search term matching
        # this account's ID.
        if len(accounts) == 1:
            # Before injecting the search term, make sure it doesn't clash with the name
            # of a pot.
            clashing_with_pot = False

            for name in pots.keys():
                if "account" in name:
                    clashing_with_pot = True
                    break

            if not clashing_with_pot:
                accounts["account"] = accounts[list(accounts.keys())[0]]

        # Iterate over the accounts to see if one matches.
        for search_params, account_id in accounts.items():
            # Search terms for accounts are comma-separated, so turn that into a list.
            search_terms = search_params.split(",")

            # If either the search term or the account's ID is mentioned, then consider
            # it a match.
            for term in search_terms:
                index = None

                if term.casefold() in s:
                    index = s.index(term.casefold())
                elif account_id in s:
                    index = s.index(account_id)

                if index is not None:
                    matches.append(
                        {
                            "id": account_id,
                            "type": "account",
                            "index": index
                        }
                    )

        return matches

    def _get_pots(self) -> dict:
        # Retrieve the list of pots for this user against the Monzo API.
        res = self.instance.monzo_client.get_pots()

        # Iterate over the pots and add the non-deleted pots in a dict that maps the
        # pot's name to its ID.
        pots = {}
        for pot in res["pots"]:
            if pot["deleted"]:
                continue

            # Case fold the pot's name so we don't run into issues because of the case.
            pots[pot["name"].casefold()] = pot["id"]

        return pots

    def _get_accounts(self) -> dict:
        # Retrieve the list of accounts for this user against the Monzo API.
        res = self.instance.monzo_client.get_accounts()

        # Iterate over the accounts and add the open accounts in a dict that maps search
        # terms to an account's ID. Currently, the search terms is a comma-separated list
        # of the account's owners.
        accounts = {}
        for account in res["accounts"]:
            if account["closed"]:
                continue

            owners_names = []
            for owner in account["owners"]:
                owners_names.append(owner["preferred_name"])

            # Format the list and case fold it so we don't run into issues because of the
            # case.
            key = ",".join(owners_names)
            accounts[key.casefold()] = account["id"]

        return accounts

    def _can_parse_into_float(self, s: str) -> bool:
        try:
            float(s)
            return True
        except ValueError:
            return False


command_class = MoveCommand