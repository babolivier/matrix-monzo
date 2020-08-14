from psycopg3 import Connection

from matrix_monzo.storage.stores import Store


class SelectedAccountsStore(Store):
    def __init__(self, conn: Connection):
        super(SelectedAccountsStore, self).__init__(conn)

        self.execute_in_transaction("""
            CREATE TABLE IF NOT EXISTS selected_accounts (
                user_id TEXT PRIMARY KEY,
                account_id TEXT NOT NULL
            );
        """)

    def get_selected_account(self, user_id: str):
        return self.execute_in_transaction(
            """
                SELECT account_id FROM selected_accounts WHERE user_id = %s;
            """,
            (user_id,)
        )

    def set_selected_account(self, user_id: str, account_id: str):
        self.execute_in_transaction(
            """
                INSERT INTO selected_accounts(user_id, account_id)
                VALUES (%s, %s)
                ON CONFLICT (user_id) DO
                    UPDATE SET account_id = EXCLUDED.account_id
                    WHERE selected_accounts.user_id = EXCLUDED.user_id;
            """,
            (user_id, account_id)
        )
