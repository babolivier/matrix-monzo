from psycopg3 import Connection

from storage.stores import Store


class AccountsStore(Store):
    def __init__(self, conn: Connection):
        super(AccountsStore, self).__init__(conn)

        self.execute_in_transaction("""
            CREATE TABLE IF NOT EXISTS accounts (
                id TEXT PRIMARY KEY,
                description TEXT NOT NULL,
                balance REAL NOT NULL DEFAULT 0,
                currency TEXT NOT NULL
            );
        """)
