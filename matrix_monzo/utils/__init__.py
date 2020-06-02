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
