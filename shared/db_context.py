"""DB context manager wrapper for safe connection handling."""
from __future__ import annotations
import sqlite3
from contextlib import contextmanager
from typing import Generator


@contextmanager
def db_connection(db_path: str = None) -> Generator[sqlite3.Connection, None, None]:
    """Context manager for SQLite connections. Auto-commit on success, rollback on error."""
    if db_path is None:
        from data_fetch.lof_db.schema import DB_PATH
        db_path = DB_PATH
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()