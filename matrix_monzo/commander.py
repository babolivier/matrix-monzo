import importlib
from typing import Dict, List

from nio import MatrixRoom, RoomMessageText

from matrix_monzo import bot_commands
from matrix_monzo.messages import messages
from matrix_monzo.utils.instance import Instance


class Commander:
    def __init__(self, instance: Instance):
        self.instance = instance
        self.help_doc = {}

        self.commands = []  # type: List[bot_commands.Command]
        for command_name in bot_commands.COMMANDS:
            module = importlib.import_module(f'{bot_commands.__name__}.{command_name}')
            self.commands.append(module.command_class(instance))

        self._build_help_doc()

    async def dispatch(self, event: RoomMessageText, room: MatrixRoom) -> Dict[str, str]:
        if event.body.startswith("help"):
            return self._dispatch_help(event)

        for command in self.commands:
            if event.body.startswith(command.PREFIX):
                return await command.run(event, room)

        return messages.get_content("unknown_command")

    def _dispatch_help(self, event: RoomMessageText) -> Dict[str, str]:
        if event.body == "help":
            return self.help_doc

        target = event.body.replace("help ", "")
        for command in self.commands:
            if not isinstance(command, bot_commands.MetaCommand):
                continue
            if command.PREFIX == target:
                return command.get_help_content()

        return messages.get_content("unknown_command")

    def _build_help_doc(self):
        commands = []
        meta_commands = []

        for command in self.commands:
            if isinstance(command, bot_commands.MetaCommand):
                meta_commands.append(command)
            else:
                commands.append(command)

        commands_help_doc = "\n".join(self._build_help_list(commands))
        meta_commands_help_doc = "\n".join(self._build_help_list(meta_commands))

        self.help_doc = messages.get_content(
            message_id="help",
            format_markdown=True,
            commands=commands_help_doc,
            meta_commands=meta_commands_help_doc,
        )

    def _build_help_list(self, commands: List[bot_commands.Command]) -> List[str]:
        commands_help_list = []
        for command in commands:
            if command.HELP_DOC:
                commands_help_list.append(messages.get(
                    message_id="help_entry",
                    prefix=command.PREFIX,
                    help_doc=command.HELP_DOC.strip("."),
                    usage=command.usage(),
                ))

        return commands_help_list
