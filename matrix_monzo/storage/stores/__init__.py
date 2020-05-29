from typing import Any, Callable, Tuple, Optional

from psycopg3 import Connection
from psycopg3.cursor import Cursor


class Store:
    def __init__(self, conn: Connection):
        self.conn = conn

    def with_transaction(self, f: Callable, *args, **kwargs):
        cursor = self.conn.cursor()
        f(cursor, *args, **kwargs)
        self.conn.commit()
        cursor.close()

    def execute_in_transaction(self, statement: str, args: Optional[Tuple[Any]] = None):
        def execute_statement(cur: Cursor):
            cur.execute(statement, args)

        self.with_transaction(execute_statement)
