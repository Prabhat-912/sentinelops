import sqlite3
from pathlib import Path

from app.config import config


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / config["database"]["path"]


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_database():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            cpu_percent REAL NOT NULL,
            memory_percent REAL NOT NULL,
            disk_percent REAL NOT NULL
        )
    """)

    connection.commit()
    connection.close()
