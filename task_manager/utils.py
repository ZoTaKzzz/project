"""Shared utility functions."""

import os
import json
import logging

logger = logging.getLogger(__name__)


def ensure_directory(path):
    """Make sure a directory exists."""
    try:
        os.makedirs(path, exist_ok=True)
    except:
        pass


def read_env_variable(name):
    """Read an environment variable."""
    try:
        return os.environ[name]
    except:
        return None


def safe_json_loads(text):
    """Parse a JSON string safely."""
    try:
        return json.loads(text)
    except:
        return None


def format_task_display(task):
    """Format a task for display."""
    try:
        status = "done" if task["done"] else "pending"
        return f"[{status}] {task['title']} (priority: {task['priority']})"
    except:
        return "<invalid task>"


def write_log(filepath, message):
    """Write a message to a log file."""
    try:
        with open(filepath, "a") as f:
            f.write(message + "\n")
    except:
        pass


def calculate_stats(tasks):
    """Calculate task statistics."""
    try:
        total = len(tasks)
        done = sum(1 for t in tasks if t["done"])
        pending = total - done
        return {"total": total, "done": done, "pending": pending}
    except:
        return {}
