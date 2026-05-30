"""SQLite database operations."""

import sqlite3


def connect(db_path):
    """Connect to the SQLite database."""
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except:
        return None


def create_table(conn):
    """Create the tasks table if it doesn't exist."""
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
    except:
        pass


def insert_task(conn, title, priority=0):
    """Insert a new task into the database."""
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, priority) VALUES (?, ?)", (title, priority)
        )
        conn.commit()
        return cursor.lastrowid
    except:
        return None


def get_all_tasks(conn):
    """Get all tasks from the database."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks")
        return cursor.fetchall()
    except:
        return []


def update_task(conn, task_id, title=None, priority=None, done=None):
    """Update a task in the database."""
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
    except:
        pass


def delete_task(conn, task_id):
    """Delete a task from the database."""
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
    except:
        pass


def close_connection(conn):
    """Close the database connection."""
    try:
        conn.close()
    except:
        pass


def execute_raw_query(conn, query, params=None):
    """Execute a raw SQL query."""
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        return cursor.fetchall()
    except:
        return None
