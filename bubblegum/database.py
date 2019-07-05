import sqlite3
from contextlib import contextmanager

from bubblegum import BG_PATH
from bubblegum.errors import BubblegumError

DB_PATH = BG_PATH / 'history.db'


@contextmanager
def cursor():
    with sqlite3.connect(str(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        yield cursor
        cursor.close()


class DB:
    def __init__(self):
        with cursor() as c:
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY,
                    time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    url TEXT NOT NULL,
                    deletion_url TEXT
                )
                """
            )

    def log_upload(self, img_url, del_url):
        with cursor() as c:
            c.execute(
                """
                INSERT INTO history (
                  url,
                  deletion_url
                )
                VALUES
                (?, ?)
                """, (img_url, del_url)
            )

    def fetch_history(self, sort='asc', limit=25, offset=0):
        if sort not in {'asc', 'desc'}:
            raise BubblegumError('Invalid history sort passed.')
        with cursor() as c:
            c.execute(
                f"""
                SELECT
                  id,
                  time,
                  url,
                  deletion_url
                FROM history
                ORDER BY ID {sort}
                LIMIT ? OFFSET ?
                """, (limit, offset)
            )
            for row in c.fetchall():
                yield (
                    row[col] for col in [
                        'id',
                        'time',
                        'url',
                        'deletion_url',
                    ]
                )


db = DB()
