"""Thin sqlite3 wrapper. Row factory = dict-like access."""
import sqlite3
from pathlib import Path
from contextlib import contextmanager


def connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init(db_path: str, schema_sql: str) -> None:
    schema = Path(schema_sql).read_text()
    with connect(db_path) as conn:
        conn.executescript(schema)


@contextmanager
def tx(db_path: str):
    conn = connect(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
