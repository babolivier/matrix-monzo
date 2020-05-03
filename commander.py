import importlib
from typing import Dict, List

from nio import RoomMessageText

import bot_commands
from messages import messages
from utils.instance import Instance


class Commander:
    def __init__(self, instance: Instance):
        self.instance = instance

        self.commands = []  # type: List[bot_commands.Command]
        for command_name in bot_commands.commands:
            module = importlib.import_module(f'{bot_commands.__name__}.{command_name}')
            self.commands.append(module.command_class(instance))

    async def dispatch(self, event: RoomMessageText) -> Dict[str, str]:
        for command in self.commands:
            if event.body.startswith(command.PREFIX):
                return await command.run(event)

        return messages.get_content("unknown_command")
