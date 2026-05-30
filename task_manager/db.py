"""SQLite database operations."""

import logging
import sqlite3

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Raised when a database operation fails."""


def connect(db_path):
    """Connect to the SQLite database.

    Raises DatabaseError instead of returning None, which would cause
    confusing AttributeError crashes downstream.
    """
    try:
        return sqlite3.connect(db_path)
    except sqlite3.Error as exc:
        raise DatabaseError(f"Could not connect to database {db_path}: {exc}") from exc


def create_table(conn):
    """Create the tasks table if it doesn't exist.

    Raises DatabaseError so the caller knows the schema is not ready.
    """
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                priority INTEGER DEFAULT 0,
                done BOOLEAN DEFAULT 0
            )
            """
        )
        conn.commit()
    except sqlite3.Error as exc:
        raise DatabaseError(f"Failed to create tasks table: {exc}") from exc


def insert_task(conn, title, priority=0):
    """Insert a new task into the database.

    Returns the new row ID. Raises DatabaseError on failure.
    """
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, priority) VALUES (?, ?)", (title, priority)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as exc:
        raise DatabaseError(f"Failed to insert task '{title}': {exc}") from exc


def get_all_tasks(conn):
    """Get all tasks from the database.

    Raises DatabaseError instead of returning an empty list that would
    hide a real query failure.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks")
        return cursor.fetchall()
    except sqlite3.Error as exc:
        raise DatabaseError(f"Failed to fetch tasks: {exc}") from exc


def update_task(conn, task_id, title=None, priority=None, done=None):
    """Update a task in the database.

    Raises DatabaseError on failure so the caller knows the update did
    not persist.
    """
    try:
        cursor = conn.cursor()
        if title is not None:
            cursor.execute("UPDATE tasks SET title = ? WHERE id = ?", (title, task_id))
        if priority is not None:
            cursor.execute(
                "UPDATE tasks SET priority = ? WHERE id = ?", (priority, task_id)
            )
        if done is not None:
            cursor.execute("UPDATE tasks SET done = ? WHERE id = ?", (done, task_id))
        conn.commit()
    except sqlite3.Error as exc:
        raise DatabaseError(f"Failed to update task {task_id}: {exc}") from exc


def delete_task(conn, task_id):
    """Delete a task from the database.

    Raises DatabaseError on failure so the caller knows the deletion did
    not happen.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
    except sqlite3.Error as exc:
        raise DatabaseError(f"Failed to delete task {task_id}: {exc}") from exc


def close_connection(conn):
    """Close the database connection.

    Logs a warning on failure; closing is best-effort cleanup.
    """
    try:
        conn.close()
    except sqlite3.Error as exc:
        logger.warning("Error closing database connection: %s", exc)


def execute_raw_query(conn, query, params=None):
    """Execute a raw SQL query.

    Raises DatabaseError on failure instead of returning None, which
    is ambiguous (could mean "no rows" or "query failed").
    """
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        return cursor.fetchall()
    except sqlite3.Error as exc:
        raise DatabaseError(f"Raw query failed: {exc}") from exc
