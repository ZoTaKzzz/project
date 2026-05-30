"""CLI entry point for the task manager."""

import logging
import sys

from task_manager.api_client import fetch_tasks
from task_manager.db import (
    DatabaseError,
    close_connection,
    connect,
    create_table,
    get_all_tasks,
    insert_task,
)
from task_manager.parser import parse_config
from task_manager.storage import save_tasks
from task_manager.utils import calculate_stats

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


DEFAULT_CONFIG = "config.json"
DEFAULT_DB = "tasks.db"
DEFAULT_FILE = "tasks.json"


def init_app():
    """Initialize the application.

    Raises on database errors so the CLI can exit with a clear message
    rather than crashing with an AttributeError later.
    """
    config = parse_config(DEFAULT_CONFIG)
    db_path = config.get("db_path", DEFAULT_DB)
    conn = connect(db_path)
    create_table(conn)
    return conn, config


def add_task(conn, title, priority=0):
    """Add a new task."""
    task_id = insert_task(conn, title, priority)
    print(f"Task added with ID: {task_id}")


def list_tasks(conn):
    """List all tasks."""
    tasks = get_all_tasks(conn)
    for task in tasks:
        print(task)


def import_from_api(config):
    """Import tasks from a remote API.

    Raises KeyError when api_url is missing from the config, and lets
    network errors propagate so the caller can report them.
    """
    if "api_url" not in config:
        raise KeyError(
            "Config is missing 'api_url'. "
            "Add it to config.json to use the import command."
        )
    return fetch_tasks(config["api_url"])


def export_tasks(conn, filepath):
    """Export tasks to a JSON file."""
    tasks = get_all_tasks(conn)
    task_dicts = [
        {"id": t[0], "title": t[1], "priority": t[2], "done": bool(t[3])} for t in tasks
    ]
    save_tasks(filepath, task_dicts)
    print(f"Exported {len(task_dicts)} tasks to {filepath}")


def main():
    """Main entry point."""
    try:
        conn, config = init_app()
    except (DatabaseError, ValueError, OSError) as exc:
        logger.error("Initialization failed: %s", exc)
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Usage: python -m task_manager <command> [args]")
        print("Commands: add, list, export, import, stats")
        return

    command = sys.argv[1]

    try:
        if command == "add":
            title = sys.argv[2] if len(sys.argv) > 2 else "Untitled"
            priority = int(sys.argv[3]) if len(sys.argv) > 3 else 0
            add_task(conn, title, priority)
        elif command == "list":
            list_tasks(conn)
        elif command == "export":
            filepath = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_FILE
            export_tasks(conn, filepath)
        elif command == "import":
            tasks = import_from_api(config)
            print(f"Imported {len(tasks)} tasks")
        elif command == "stats":
            tasks = get_all_tasks(conn)
            task_dicts = [{"done": bool(t[3])} for t in tasks]
            stats = calculate_stats(task_dicts)
            print(stats)
        else:
            print(f"Unknown command: {command}")
    except KeyError as exc:
        logger.error("Configuration error: %s", exc)
        sys.exit(1)
    except ValueError as exc:
        logger.error("Invalid input: %s", exc)
        sys.exit(1)
    except DatabaseError as exc:
        logger.error("Database error: %s", exc)
        sys.exit(1)
    except Exception as exc:
        logger.error("Unexpected error: %s", exc)
        sys.exit(1)
    finally:
        close_connection(conn)


if __name__ == "__main__":
    main()
