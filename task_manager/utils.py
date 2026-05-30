"""Shared utility functions."""

import json
import logging
import os

logger = logging.getLogger(__name__)


def ensure_directory(path):
    """Make sure a directory exists.

    Raises OSError on permission or filesystem errors so the caller
    knows the directory was not created.
    """
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as exc:
        raise OSError(f"Could not create directory {path}: {exc}") from exc


def read_env_variable(name):
    """Read an environment variable.

    Returns None when the variable is unset (normal case).  Logs at
    debug level for traceability.
    """
    value = os.environ.get(name)
    if value is None:
        logger.debug("Environment variable %s is not set", name)
    return value


def safe_json_loads(text):
    """Parse a JSON string, returning None on invalid input.

    Catches only JSON decoding errors; other exceptions propagate.
    """
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError) as exc:
        logger.debug("JSON decode failed: %s", exc)
        return None


def format_task_display(task):
    """Format a task for display.

    Raises KeyError / TypeError when the task dict is malformed instead
    of returning a placeholder that hides the problem.
    """
    status = "done" if task["done"] else "pending"
    return f"[{status}] {task['title']} (priority: {task['priority']})"


def write_log(filepath, message):
    """Write a message to a log file.

    Raises OSError on failure so the caller knows logging is broken.
    """
    try:
        with open(filepath, "a") as f:
            f.write(message + "\n")
    except OSError as exc:
        raise OSError(f"Could not write to log file {filepath}: {exc}") from exc


def calculate_stats(tasks):
    """Calculate task statistics.

    Raises KeyError / TypeError when tasks contain invalid data, rather
    than returning an empty dict that would hide data issues.
    """
    total = len(tasks)
    done = sum(1 for t in tasks if t["done"])
    pending = total - done
    return {"total": total, "done": done, "pending": pending}
