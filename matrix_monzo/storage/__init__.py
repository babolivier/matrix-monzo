import logging

import psycopg2

from matrix_monzo.storage.stores.accounts import AccountsStore

logger = logging.getLogger(__name__)


class Storage:
    def __init__(self, db_config):
        self.conn = psycopg2.connect(**db_config)
        self.cursor = self.conn.cursor()

        self.account_store = AccountsStore(self.conn)

        logger.info("Database ready")


