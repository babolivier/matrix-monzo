import abc
from typing import Dict, List

from monzo.errors import ForbiddenError, UnauthorizedError
from nio import MatrixRoom, RoomMessageText
from oauthlib.oauth2.rfc6749.errors import MissingTokenError

from matrix_monzo.messages import messages
from matrix_monzo.utils import to_event_content
from matrix_monzo.utils.instance import Instance

COMMANDS = ["verify_device", "say", "show", "login"]
COMMON_WORDS = ["of", "my"]


class InvalidParamsException(Exception):
    def __init__(self, message_content: Dict[str, str]):
        self.message_content = message_content


def runner(f):
    async def wrapped(*args, **kwargs):
        try:
            res = await f(*args, **kwargs)
            if not isinstance(res, dict):
                return to_event_content(res)
            return res
        except InvalidParamsException as e:
            return e.message_content
        except ForbiddenError:
            return messages.get("monzo_token_insufficient_permissions")
        except (UnauthorizedError, MissingTokenError):
            return messages.get("monzo_missing_token")

    return wrapped


class Command(abc.ABC):
    def __init__(self, instance: Instance):
        self.instance = instance

    @property
    @abc.abstractmethod
    def PREFIX(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def PARAMS(self) -> List[str]:
        pass

    @property
    @abc.abstractmethod
    def HELP_DOC(self) -> str:
        pass

    @abc.abstractmethod
    async def run(self, event: RoomMessageText, room: MatrixRoom) -> Dict[str, str]:
        pass

    def string_to_params(self, body: str) -> Dict[str, str]:
        body = self._strip_common_words(body)
        params_s = body[len(self.PREFIX):]
        params_s.strip()
        params_l = params_s.split()

        if len(params_l) != len(self.PARAMS):
            expected_params = " ".join([f'[{param}]' for param in self.PARAMS])
            usage = f'{self.PREFIX} {expected_params}'

            raise InvalidParamsException(
                messages.get_content(
                    message_id="invalid_params",
                    expected_params_number=len(self.PARAMS),
                    actual_params_number=len(params_l),
                    usage=usage,
                )
            )

        params = {}
        for i in range(len(self.PARAMS)):
            params[self.PARAMS[i]] = params_l[i]

        return params

    def _strip_common_words(self, body: str) -> str:
        for word in COMMON_WORDS:
            body = body.replace(f" {word}", "")

        return body

    def usage(self):
        if not self.PARAMS:
            return self.PREFIX

        expected_params = " ".join([f'[{param}]' for param in self.PARAMS])
        return f'{self.PREFIX} {expected_params}'


class MetaCommand(Command, abc.ABC):
    @property
    @abc.abstractmethod
    def SUB_COMMANDS(self) -> List[str]:
        pass

    @abc.abstractmethod
    def get_help_content(self) -> Dict[str, str]:
        pass


class SubCommand(Command, abc.ABC):
    @property
    @abc.abstractmethod
    def PARENT(self) -> str:
        pass

    @abc.abstractmethod
    async def run_with_params(
            self, params: str, event: RoomMessageText, room: MatrixRoom,
    ) -> Dict[str, str]:
        pass

    def usage(self):
        return f'{self.PARENT} {super().usage()}'
