import sqlite3
from pathlib import Path

DATABASE_PATH = Path("events.db")


def get_connection():
    """
    Creates a SQLite connection.

    check_same_thread=False allows FastAPI request handlers to use the
    connection safely in this simple application setup.
    """
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    """
    Creates required tables if they do not already exist.
    Data stays persistent in events.db between application runs.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            total_seats INTEGER NOT NULL CHECK(total_seats > 0),
            event_date TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            user_name TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('active', 'cancelled')),
            registered_at TEXT NOT NULL,
            cancelled_at TEXT,
            FOREIGN KEY(event_id) REFERENCES events(id)
        )
    """)

    # This prevents the same user from having two ACTIVE registrations
    # for the same event, but still allows the user to register again
    # after a previous registration was cancelled.
    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS unique_active_registration
        ON registrations(event_id, user_name)
        WHERE status = 'active'
    """)

    conn.commit()
    conn.close()
