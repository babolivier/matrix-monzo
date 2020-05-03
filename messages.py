import json
from typing import Dict, Optional

from utils import to_event_content


class _Messages:
    def __init__(self, path):
        with open(path) as fp:
            self._dict = json.load(fp)  # type: Dict[str, str]

    def get(self, message_id: str, **kwargs) -> str:
        if message_id in self._dict:
            return self._dict[message_id].format(**kwargs)

        if "undefined_key" in self._dict:
            return self._dict[message_id].format(message=message_id)

        return f'Error: Undefined message: {message_id}'

    def get_optional(self, message_id: str) -> Optional[str]:
        return self._dict.get(message_id)

    def get_content(
            self, message_id: str, format_markdown=False, **kwargs,
    ) -> Dict[str, str]:
        return to_event_content(
            self.get(message_id, **kwargs), format_markdown=format_markdown,
        )


messages = _Messages("res/messages.json")
