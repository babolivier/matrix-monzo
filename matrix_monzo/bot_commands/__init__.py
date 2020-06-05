import abc
from typing import Dict, List

from monzo.errors import BadRequestError, ForbiddenError, UnauthorizedError
from nio import MatrixRoom, RoomMessageText
from oauthlib.oauth2.rfc6749.errors import MissingTokenError

from matrix_monzo.messages import messages
from matrix_monzo.utils import to_event_content
from matrix_monzo.utils.errors import InvalidParamsException, ProcessingError
from matrix_monzo.utils.instance import Instance

COMMANDS = ["verify_device", "say", "show", "login", "move"]
COMMON_WORDS = ["of", "my"]


def runner(f):
    async def wrapped(*args, **kwargs):
        try:
            res = await f(*args, **kwargs)
            if not isinstance(res, dict):
                return to_event_content(res)
            return res
        except (InvalidParamsException, ProcessingError) as e:
            return e.message_content
        except ForbiddenError:
            return messages.get("monzo_token_insufficient_permissions")
        except BadRequestError as e:
            return messages.get_content("monzo_api_error", error=e)
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

    def _body_to_params_dict(self, body: str) -> Dict[str, str]:
        params_l = self._body_to_list(body)

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

    def _body_to_list(self, body: str) -> list:
        body = body.casefold()
        params = body[len(self.PREFIX):]
        params.strip()
        return params.split()

    def _strip_common_words(self, body: str) -> str:
        for word in COMMON_WORDS:
            body = body.replace(f" {word}", "")
            if body.startswith(word):
                body = body.replace(f"{word} ", "")

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
