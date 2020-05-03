from monzo import Monzo
from nio import AsyncClient

from config import Config
from storage import Storage


class Instance:
    def __init__(
            self,
            config: Config,
            nio_client: AsyncClient,
            monzo_client: Monzo,
            storage: Storage,
    ):
        self.config = config
        self.nio_client = nio_client
        self.monzo_client = monzo_client
        self.storage = storage

