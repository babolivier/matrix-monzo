from typing import Dict

from markdown import markdown

from matrix_monzo.utils.constants import DEFAULT_MSG_TYPE, MsgFormat


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
