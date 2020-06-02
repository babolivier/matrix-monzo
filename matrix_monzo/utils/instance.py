import logging
from typing import Optional

from monzo import Monzo, MonzoOAuth2Client
from nio import AsyncClient, AsyncClientConfig

from matrix_monzo.config import Config
from matrix_monzo.storage import Storage
from matrix_monzo.utils.errors import MonzoInvalidStateError

logger = logging.getLogger(__name__)


class Instance:
    def __init__(
            self,
            config: Config,
    ):
        self.config = config

        self.storage = Storage(self.config.database)

        # TODO: only initialise the Monzo client if we've got an access token in the
        #  database.

        self.monzo_oauth_client = MonzoOAuth2Client(
            client_id=self.config.monzo_client_id,
            client_secret=self.config.monzo_client_secret,
        )

        self.monzo_client = Monzo.from_oauth_session(self.monzo_oauth_client)

        self.nio_client = AsyncClient(
            self.config.homeserver_url,
            self.config.user_id,
            device_id=self.config.device_id,
            config=AsyncClientConfig(
                max_limit_exceeded=0,
                max_timeouts=0,
                store_sync_tokens=True,
            ),
            store_path=self.config.store_path,
        )

        self.auths_in_progress = {}

    async def run(self):
        # First do a sync with full_state = true to retrieve the state of the rooms.
        await self.nio_client.sync(full_state=True)
        logger.info("Initialisation complete, now syncing")
        await self.nio_client.sync_forever(30000)

    def get_monzo_login_url(self, room_id: str) -> str:
        redirect_uri = self.config.http_baseurl + "/auth_callback"

        url, state = self.monzo_oauth_client.authorize_token_url(
            redirect_uri=redirect_uri,
        )

        self.auths_in_progress[state] = room_id

        return url

    def get_monzo_access_token(self, code, state):
        if state not in self.auths_in_progress:
            raise MonzoInvalidStateError()

        return (
            self.monzo_oauth_client.fetch_access_token(code=code),
            self.auths_in_progress[state],
        )
