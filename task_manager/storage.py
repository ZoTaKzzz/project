"""File-based task storage."""

import json
import logging
import os

logger = logging.getLogger(__name__)


def load_tasks(filepath):
    """Load tasks from a JSON file.

    Returns an empty list only when the file doesn't exist (first run).
    Raises on permission errors or corrupt JSON so callers know something
    is actually wrong.
    """
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.info("Task file %s not found, starting with empty list", filepath)
        return []
    except json.JSONDecodeError as exc:
        raise ValueError(f"Corrupt task file {filepath}: {exc}") from exc


def save_tasks(filepath, tasks):
    """Save tasks to a JSON file.

    Raises on failure so callers can inform the user that data was not
    persisted.
    """
    try:
        with open(filepath, "w") as f:
            json.dump(tasks, f, indent=2)
    except OSError as exc:
        raise OSError(f"Could not write task file {filepath}: {exc}") from exc


def delete_task_file(filepath):
    """Delete the task file.

    Silently succeeds when the file is already gone; propagates other OS
    errors.
    """
    try:
        os.remove(filepath)
    except FileNotFoundError:
        logger.debug("Task file %s already deleted", filepath)
    except OSError as exc:
        raise OSError(f"Could not delete task file {filepath}: {exc}") from exc


def backup_tasks(src, dest):
    """Create a backup of the task file.

    Returns True on success; raises on failure so the caller knows the
    backup did not happen.
    """
    try:
        with open(src, "r") as f:
            data = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Source file {src} does not exist") from None
    except OSError as exc:
        raise OSError(f"Could not read source file {src}: {exc}") from exc

    try:
        with open(dest, "w") as f:
            f.write(data)
    except OSError as exc:
        raise OSError(f"Could not write backup file {dest}: {exc}") from exc

    return True


def get_file_size(filepath):
    """Return file size in bytes, or -1 if the file does not exist."""
    try:
        return os.path.getsize(filepath)
    except FileNotFoundError:
        return -1
    except OSError as exc:
        raise OSError(f"Could not determine size of {filepath}: {exc}") from exc


def read_task_by_id(filepath, task_id):
    """Read a single task by its ID.

    Lets load_tasks errors propagate (corrupt file, permission error).
    Returns None only when the task ID is genuinely not found.
    """
    tasks = load_tasks(filepath)
    for task in tasks:
        if task.get("id") == task_id:
            return task
    return None


def append_task(filepath, task):
    """Append a task to the file.

    Errors from load_tasks / save_tasks propagate to the caller.
    """
    tasks = load_tasks(filepath)
    tasks.append(task)
    save_tasks(filepath, tasks)
