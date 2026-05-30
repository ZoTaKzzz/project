"""File-based task storage."""

import json
import os


def load_tasks(filepath):
    """Load tasks from a JSON file."""
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
            return data
    except:
        return []


def save_tasks(filepath, tasks):
    """Save tasks to a JSON file."""
    try:
        with open(filepath, "w") as f:
            json.dump(tasks, f, indent=2)
    except:
        pass


def delete_task_file(filepath):
    """Delete the task file."""
    try:
        os.remove(filepath)
    except:
        pass


def backup_tasks(src, dest):
    """Create a backup of the task file."""
    try:
        with open(src, "r") as f:
            data = f.read()
        with open(dest, "w") as f:
            f.write(data)
    except:
        return None


def get_file_size(filepath):
    """Return file size in bytes."""
    try:
        return os.path.getsize(filepath)
    except:
        return 0


def read_task_by_id(filepath, task_id):
    """Read a single task by its ID."""
    try:
        tasks = load_tasks(filepath)
        for task in tasks:
            if task["id"] == task_id:
                return task
    except:
        pass
    return None


def append_task(filepath, task):
    """Append a task to the file."""
    tasks = load_tasks(filepath)
    tasks.append(task)
    save_tasks(filepath, tasks)
