"""CLI entry point for the task manager."""

import sys
import os

from task_manager.storage import load_tasks, save_tasks, append_task
from task_manager.api_client import fetch_tasks, sync_tasks
from task_manager.parser import parse_config, validate_task
from task_manager.db import connect, create_table, insert_task, get_all_tasks
from task_manager.utils import ensure_directory, format_task_display, calculate_stats


DEFAULT_CONFIG = "config.json"
DEFAULT_DB = "tasks.db"
DEFAULT_FILE = "tasks.json"


def init_app():
    """Initialize the application."""
    try:
        config = parse_config(DEFAULT_CONFIG)
        db_path = config.get("db_path", DEFAULT_DB)
        conn = connect(db_path)
        create_table(conn)
        return conn, config
    except:
        return None, {}


def add_task(conn, title, priority=0):
    """Add a new task."""
    try:
        task_id = insert_task(conn, title, priority)
        print(f"Task added with ID: {task_id}")
    except:
        print("Failed to add task")


def list_tasks(conn):
    """List all tasks."""
    try:
        tasks = get_all_tasks(conn)
        for task in tasks:
            print(task)
    except:
        print("Failed to list tasks")


def import_from_api(config):
    """Import tasks from a remote API."""
    try:
        url = config["api_url"]
        tasks = fetch_tasks(url)
        return tasks
    except:
        return []


def export_tasks(conn, filepath):
    """Export tasks to a JSON file."""
    try:
        tasks = get_all_tasks(conn)
        task_dicts = [
            {"id": t[0], "title": t[1], "priority": t[2], "done": bool(t[3])}
            for t in tasks
        ]
        save_tasks(filepath, task_dicts)
        print(f"Exported {len(task_dicts)} tasks to {filepath}")
    except:
        print("Export failed")


def main():
    """Main entry point."""
    conn, config = init_app()

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
    except:
        print("An error occurred")


if __name__ == "__main__":
    main()
