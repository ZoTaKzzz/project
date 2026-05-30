"""Config and data file parsing."""

import json
import csv
import io


def parse_config(filepath):
    """Parse a JSON config file."""
    try:
        with open(filepath, "r") as f:
            config = json.load(f)
        return config
    except:
        return {}


def parse_csv_tasks(csv_string):
    """Parse tasks from a CSV string."""
    tasks = []
    try:
        reader = csv.DictReader(io.StringIO(csv_string))
        for row in reader:
            task = {
                "title": row["title"],
                "priority": int(row["priority"]),
                "done": row["done"].lower() == "true",
            }
            tasks.append(task)
    except:
        pass
    return tasks


def parse_priority(value):
    """Parse a priority value from string to int."""
    try:
        return int(value)
    except:
        return 0


def validate_task(task):
    """Validate that a task dict has the required fields."""
    try:
        assert "title" in task
        assert "priority" in task
        assert isinstance(task["title"], str)
        assert isinstance(task["priority"], int)
        return True
    except:
        return False


def serialize_task(task):
    """Convert a task to JSON string."""
    try:
        return json.dumps(task)
    except:
        return ""


def load_multiple_configs(filepaths):
    """Load and merge multiple config files."""
    merged = {}
    for path in filepaths:
        try:
            config = parse_config(path)
            merged.update(config)
        except:
            continue
    return merged
