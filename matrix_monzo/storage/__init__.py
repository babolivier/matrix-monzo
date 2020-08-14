import logging

import psycopg2
from psycopg2.extras import LoggingConnection

from matrix_monzo.storage.stores.selected_accounts import SelectedAccountsStore
from matrix_monzo.storage.stores.tokens import TokensStore

logger = logging.getLogger(__name__)


class Storage:
    def __init__(self, db_config):
        self.conn = psycopg2.connect(connection_factory=LoggingConnection, **db_config)
        self.conn.initialize(logger)
        self.cursor = self.conn.cursor()

        self.selected_account_store = SelectedAccountsStore(self.conn)
        self.token_store = TokensStore(self.conn)

        logger.info("Database ready")


