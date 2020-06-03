import json
import logging
from typing import Optional

from psycopg3 import Connection

from matrix_monzo.storage.stores import Store

logger = logging.getLogger(__name__)


class TokensStore(Store):
    def __init__(self, conn: Connection):
        super(TokensStore, self).__init__(conn)

        self.execute_in_transaction("""
            CREATE TABLE IF NOT EXISTS tokens (
                user_id TEXT PRIMARY KEY,
                token_json TEXT NOT NULL
            );
        """)

    def store_token(self, user_id: str, token_dict: dict):
        logger.info("Storing Monzo token for %s", user_id)

        token_str = json.dumps(token_dict)
        self.execute_in_transaction(
            """
            INSERT INTO tokens (user_id, token_json) VALUES(%s, %s)
            ON CONFLICT (user_id) DO UPDATE SET token_json = %s;
            """,
            (user_id, token_str, token_str),
        )

    def get_token(self, user_id: str) -> Optional[str]:
        rows = self.execute_in_transaction(
            """
            SELECT token_json FROM tokens WHERE user_id = %s;
            """,
            (user_id,)
        )

        if rows:
            return json.loads(rows[0][0])
        else:
            return None
