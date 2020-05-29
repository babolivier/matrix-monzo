import importlib
from typing import Dict

from nio import RoomMessageText

from matrix_monzo.bot_commands import MetaCommand, SubCommand, runner
from matrix_monzo.messages import messages
from matrix_monzo.utils.instance import Instance


class ShowCommand(MetaCommand):
    PREFIX = "show"
    PARAMS = ["entity"]
    SUB_COMMANDS = ["accounts", "all_accounts"]
    HELP_DOC = "Show the desired entity."

    def __init__(self, instance: Instance):
        super(ShowCommand, self).__init__(instance)

        self.help = {}

        self.sub_commands = {}  # type: Dict[str, SubCommand]
        for sub_command in self.SUB_COMMANDS:
            module = importlib.import_module(f'{__name__}.{sub_command}')
            command = module.command_class(instance)
            self.sub_commands[command.PREFIX] = command

        self._build_help()

    def get_help_content(self) -> Dict[str, str]:
        return self.help

    @runner
    async def run(self, event: RoomMessageText) -> Dict[str, str]:
        params = event.body[len(self.PREFIX):].strip()

        for name, sub_command in self.sub_commands.items():
            if params.startswith(name):
                return await sub_command.run_with_params(params, event)

        return messages.get_content("unknown_command")

    def _build_help(self):
        sub_commands_help = []
        for name, sub_command in self.sub_commands.items():
            sub_commands_help.append(messages.get(
                message_id="help_entry",
                prefix=f'{sub_command.PARENT} {sub_command.PREFIX}',
                help_doc=sub_command.HELP_DOC.strip("."),
                usage=sub_command.usage(),
            ))

        self.help = messages.get_content(
            message_id="help_meta_command",
            format_markdown=True,
            prefix=self.PREFIX,
            help_doc=self.HELP_DOC,
            sub_commands="\n".join(sub_commands_help),
        )


command_class = ShowCommand
