import abc
from typing import Dict, List

from nio import RoomMessageText

from utils import to_event_content
from messages import messages
from utils.instance import Instance

commands = ["verify_device", "say"]


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

    @abc.abstractmethod
    async def run(self, event: RoomMessageText) -> Dict[str, str]:
        pass

    def body_to_params(self, body: str) -> Dict[str, str]:
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
