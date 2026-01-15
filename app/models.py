import sqlite3
import os
from app.config import DATABASE_URL

def get_sqlite_path():
    """
    Converts sqlite URL to filesystem path.
    """
    if not DATABASE_URL.startswith("sqlite:"):
        raise RuntimeError("Only sqlite DATABASE_URL is supported")

    # Remove sqlite:///
    path = DATABASE_URL.replace("sqlite:///", "", 1)

    # Ensure parent directory exists
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    return path


def get_connection():
    return sqlite3.connect(
        get_sqlite_path(),
        check_same_thread=False
    )


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            message_id TEXT PRIMARY KEY,
            from_msisdn TEXT NOT NULL,
            to_msisdn TEXT NOT NULL,
            ts TEXT NOT NULL,
            text TEXT,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
