import os
import sqlite3

DB_PATH = os.getenv("DB_PATH", "/data/stats.db")


def init_db() -> None:
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS snapshots (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                client       TEXT    NOT NULL,
                torrent_hash TEXT    NOT NULL,
                torrent_name TEXT    NOT NULL,
                uploaded     INTEGER NOT NULL,
                captured_at  TEXT    NOT NULL
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_snapshots_captured_at
            ON snapshots (captured_at)
        """)


def already_collected_today(client: str, date: str) -> bool:
    with _connect() as conn:
        row = conn.execute(
            "SELECT 1 FROM snapshots WHERE client = ? AND DATE(captured_at) = ? LIMIT 1",
            (client, date),
        ).fetchone()
    return row is not None


def insert_snapshots(client: str, torrents: list[dict], captured_at: str) -> None:
    with _connect() as conn:
        conn.executemany(
            """
            INSERT INTO snapshots (client, torrent_hash, torrent_name, uploaded, captured_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            [(client, t["hash"], t["name"], t["uploaded"], captured_at) for t in torrents],
        )


def _connect() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)
