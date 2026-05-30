"""Config and data file parsing."""

import csv
import io
import json
import logging

logger = logging.getLogger(__name__)


def parse_config(filepath):
    """Parse a JSON config file.

    Returns an empty dict when the file doesn't exist (optional config).
    Raises on permission errors or invalid JSON so the caller knows the
    config could not be loaded.
    """
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.info("Config file %s not found, using defaults", filepath)
        return {}
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in config file {filepath}: {exc}") from exc


def parse_csv_tasks(csv_string):
    """Parse tasks from a CSV string.

    Raises ValueError when required columns are missing or values are
    malformed so the caller can report which row is broken.
    """
    tasks = []
    reader = csv.DictReader(io.StringIO(csv_string))
    for row_num, row in enumerate(reader, start=1):
        try:
            task = {
                "title": row["title"],
                "priority": int(row["priority"]),
                "done": row["done"].lower() == "true",
            }
        except KeyError as exc:
            raise ValueError(
                f"CSV row {row_num} is missing required column: {exc}"
            ) from exc
        except ValueError as exc:
            raise ValueError(f"CSV row {row_num} has an invalid value: {exc}") from exc
        tasks.append(task)
    return tasks


def parse_priority(value):
    """Parse a priority value from string to int.

    Raises ValueError when the value is not a valid integer, instead of
    silently returning 0 (which could mask bad input).
    """
    try:
        return int(value)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Invalid priority value: {value!r}") from exc


def validate_task(task):
    """Validate that a task dict has the required fields.

    Returns a list of human-readable error strings (empty means valid).
    Uses explicit checks rather than assertions so validation is never
    disabled by ``python -O``.
    """
    errors = []
    if "title" not in task:
        errors.append("missing 'title'")
    elif not isinstance(task["title"], str):
        errors.append("'title' must be a string")

    if "priority" not in task:
        errors.append("missing 'priority'")
    elif not isinstance(task["priority"], int):
        errors.append("'priority' must be an integer")

    return errors


def serialize_task(task):
    """Convert a task to JSON string.

    Raises TypeError on non-serialisable values instead of returning
    an empty string that hides the real problem.
    """
    return json.dumps(task)


def load_multiple_configs(filepaths):
    """Load and merge multiple config files.

    Logs a warning for each missing file but raises on corrupt JSON so
    the caller knows about genuinely broken configs.
    """
    merged = {}
    for path in filepaths:
        config = parse_config(path)
        merged.update(config)
    return merged
