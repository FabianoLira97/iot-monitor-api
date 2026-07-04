from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any

DEFAULT_DB_PATH = "iot_monitor.db"


def get_database_path() -> str:
    """Return the SQLite database path from the environment or default file."""
    return os.getenv("DATABASE_URL", DEFAULT_DB_PATH).replace("sqlite:///", "")


def get_connection() -> sqlite3.Connection:
    """Create a SQLite connection with rows accessible as dictionaries."""
    db_path = get_database_path()
    path = Path(db_path)
    if path.parent and str(path.parent) not in ("", "."):
        path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(db_path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    """Convert a sqlite Row into a plain dictionary."""
    if row is None:
        return None
    return dict(row)


def init_db() -> None:
    """Create database tables if they do not exist."""
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS sensors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                localizacao TEXT NOT NULL,
                descricao TEXT,
                ativo INTEGER NOT NULL DEFAULT 1,
                criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sensor_id INTEGER NOT NULL,
                temperatura REAL NOT NULL,
                umidade REAL NOT NULL,
                status TEXT NOT NULL,
                criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(sensor_id) REFERENCES sensors(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_readings_sensor_id ON readings(sensor_id);
            CREATE INDEX IF NOT EXISTS idx_readings_status ON readings(status);
            CREATE INDEX IF NOT EXISTS idx_readings_criado_em ON readings(criado_em);
            """
        )
