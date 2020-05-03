import importlib
from typing import Dict

from nio import RoomMessageText

from bot_commands import MetaCommand, SubCommand, runner
from messages import messages
from utils.instance import Instance


class ShowCommand(MetaCommand):
    PREFIX = "show"
    PARAMS = ["entity"]
    SUB_COMMANDS = ["accounts"]
    HELP_DOC = "Show the desired entity."

    def __init__(self, instance: Instance):
        super(ShowCommand, self).__init__(instance)

        self.help = {}

        self.sub_commands = {}  # type: Dict[str, SubCommand]
        for sub_command in self.SUB_COMMANDS:
            module = importlib.import_module(f'{__name__}.{sub_command}')
            self.sub_commands[sub_command] = module.command_class(instance)

        self.trailing_words = ["my", "all"]

        self._build_help()

    def get_help_content(self) -> Dict[str, str]:
        return self.help

    @runner
    async def run(self, event: RoomMessageText) -> Dict[str, str]:
        params = event.body[len(self.PREFIX):].strip()

        params = self._strip_trailing_words(params)

        split_params = params.split()

        for name, sub_command in self.sub_commands.items():
            if name == split_params[0]:
                return await sub_command.run_with_params(
                    " ".join(split_params[1:]), event,
                )

        return messages.get_content("unknown_command")

    def _strip_trailing_words(self, body: str) -> str:
        for word in self.trailing_words:
            preceding_space = f' {word} '
            no_preceding_space = f'{word} '

            to_replace = None
            if body.startswith(preceding_space):
                to_replace = preceding_space
            elif body.startswith(no_preceding_space):
                to_replace = no_preceding_space

            if to_replace:
                body = body.replace(to_replace, "")

        return body

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
