from typing import Dict, List, Tuple

import dateutil.parser
from markdown import markdown

from matrix_monzo.utils.constants import DEFAULT_MSG_TYPE, LETTERS, MsgFormat


def to_event_content(
    body: str,
    msgtype: str = DEFAULT_MSG_TYPE,
    format_markdown: bool = False,
) -> Dict[str, str]:
    content = {
        "body": body,
        "msgtype": msgtype
    }

    if format_markdown:
        content["format"] = MsgFormat.CUSTOM_HTML
        content["formatted_body"] = markdown(body)

    return content


def build_account_description(account: dict) -> str:
    owners_raw = account["owners"]

    owners = []
    for owner in owners_raw:
        owners.append(owner["preferred_name"] + "'s")

    return "{owners} current account".format(owners="and".join(owners))


def search_through_accounts(s: str, pots: dict, accounts: dict) -> List[Tuple[str, int]]:
    # We can easily have duplicated entry if using a list, e.g. if there's only one
    # account (so we inject the "account" search term) and the user uses the account's ID
    # we'll end up with two matches for the same account ID.
    matches = set()

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

            term_index = find_search_term_in_string(term, s)
            if term_index >= 0:
                index = term_index
            elif account_id.casefold() in s:
                index = s.index(account_id.casefold())

            if index is not None:
                matches.add((account_id, index))

    return list(matches)


def find_search_term_in_string(search_term: str, s: str) -> int:
    search_term = search_term.casefold()

    if search_term in s:
        index = s.index(search_term)
        # Don't match the search term if it's part of a word.
        if (
            (not s.startswith(search_term) and s[index - 1] in LETTERS)
            or (not s.endswith(search_term) and s[index + len(search_term)] in LETTERS)
        ):
            return -1

        return index
    else:
        return -1


def format_date(date_iso: str) -> str:
    creation_date = dateutil.parser.parse(date_iso)

    utc_offset = int(creation_date.utcoffset().total_seconds() / 3600)

    timezone = "UTC"
    if utc_offset > 0:
        timezone += "+%d" % utc_offset
    elif utc_offset < 0:
        timezone += "-%d" % -utc_offset

    return "%02d/%02d/%d (%02d:%02d:%02d %s)" % (
        creation_date.day,
        creation_date.month,
        creation_date.year,
        creation_date.hour,
        creation_date.minute,
        creation_date.second,
        timezone,
    )


def format_bool(value: bool) -> str:
    return "Yes" if value else "No"
