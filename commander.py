import importlib
from typing import Dict, List

from monzo import Monzo
from nio import AsyncClient, RoomMessageText

import bot_commands
from config import Config
from messages import messages


class Commander:
    def __init__(self, config: Config, nio_client: AsyncClient, monzo_client: Monzo):
        self.config = config
        self.nio_client = nio_client
        self.monzo_client = monzo_client

        self.commands = []  # type: List[bot_commands.Command]
        for command_name in bot_commands.commands:
            module = importlib.import_module(f'{bot_commands.__name__}.{command_name}')
            self.commands.append(module.command_class(config, nio_client, monzo_client))

    async def dispatch(self, event: RoomMessageText) -> Dict[str, str]:
        for command in self.commands:
            if event.body.startswith(command.PREFIX):
                return await command.run(event)

        return messages.get_content("unknown_command")
