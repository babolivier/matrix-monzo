from typing import Callable, Optional

import psycopg2
from psycopg3 import Connection
from psycopg3.cursor import Cursor


class Store:
    def __init__(self, conn: Connection):
        self.conn = conn

    def with_transaction(self, f: Callable, *args, **kwargs):
        cursor = self.conn.cursor()
        f(cursor, *args, **kwargs)
        self.conn.commit()

        try:
            ret = cursor.fetchall()
        except psycopg2.ProgrammingError:
            ret = None

        cursor.close()

        return ret

    def execute_in_transaction(self, statement: str, args: Optional[tuple] = None):
        def execute_statement(cur: Cursor):
            cur.execute(statement, args)

        return self.with_transaction(execute_statement)
