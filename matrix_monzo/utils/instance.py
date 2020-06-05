import logging

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

        self._monzo_oauth_client = self.setup_monzo_oauth_client()
        self.monzo_client: Monzo = Monzo.from_oauth_session(self._monzo_oauth_client)

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

    def setup_monzo_oauth_client(self):
        def refresh_token_in_store(token):
            self.storage.token_store.store_token(self.config.owner_id, token)

        existing_token = self.storage.token_store.get_token(self.config.owner_id)
        if existing_token:
            return MonzoOAuth2Client(
                client_id=self.config.monzo_client_id,
                client_secret=self.config.monzo_client_secret,
                access_token=existing_token.get("access_token"),
                refresh_token=existing_token.get("refresh_token"),
                expires_at=existing_token.get("expires_at"),
                refresh_callback=refresh_token_in_store,
            )
        else:
            return MonzoOAuth2Client(
                client_id=self.config.monzo_client_id,
                client_secret=self.config.monzo_client_secret,
                refresh_callback=refresh_token_in_store,
            )


    async def run(self):
        # First do a sync with full_state = true to retrieve the state of the rooms.
        await self.nio_client.sync(full_state=True)
        logger.info("Initialisation complete, now syncing")

        while True:
            try:
                await self.nio_client.sync_forever(30000)
            except Exception:
                logger.info("Connectivity to the homeserver has been lost, retrying...")

    def get_monzo_login_url(self, room_id: str) -> str:
        redirect_uri = self.config.http_baseurl + "/auth_callback"

        url, state = self._monzo_oauth_client.authorize_token_url(
            redirect_uri=redirect_uri,
        )

        self.auths_in_progress[state] = room_id

        return url

    def get_monzo_access_token(self, code, state):
        if state not in self.auths_in_progress:
            raise MonzoInvalidStateError()

        return (
            self._monzo_oauth_client.fetch_access_token(code=code),
            self.auths_in_progress[state],
        )
