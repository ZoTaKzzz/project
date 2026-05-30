"""HTTP client for fetching remote tasks."""

import logging

import requests

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Raised when the remote API returns an unexpected response."""


def fetch_tasks(url):
    """Fetch tasks from a remote API.

    Raises requests.RequestException on network errors and APIError on
    non-2xx responses so the caller can decide how to react.
    """
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def post_task(url, task):
    """Post a new task to the remote API.

    Returns the response JSON on success.
    Raises on network or HTTP errors.
    """
    response = requests.post(url, json=task, timeout=10)
    response.raise_for_status()
    return response.json()


def update_remote_task(url, task_id, data):
    """Update a task on the remote server.

    Raises on failure so the caller can show a meaningful message.
    """
    response = requests.put(f"{url}/{task_id}", json=data, timeout=10)
    response.raise_for_status()


def delete_remote_task(url, task_id):
    """Delete a task from the remote server.

    Raises on failure instead of silently swallowing the error.
    """
    response = requests.delete(f"{url}/{task_id}", timeout=10)
    response.raise_for_status()


def fetch_user_profile(url, user_id):
    """Fetch a user profile from the API.

    Raises on network / HTTP errors instead of returning an empty dict
    that would be indistinguishable from a user with no fields.
    """
    resp = requests.get(f"{url}/users/{user_id}", timeout=10)
    resp.raise_for_status()
    return resp.json()


def sync_tasks(local_tasks, remote_url):
    """Sync local tasks with remote server.

    Returns a list of result dicts, one per task. Each entry reports
    whether the sync succeeded or failed (with the error message),
    so no task is silently dropped.
    """
    results = []
    for task in local_tasks:
        try:
            resp = requests.post(remote_url, json=task, timeout=10)
            resp.raise_for_status()
            results.append({"task": task, "synced": True, "error": None})
        except requests.RequestException as exc:
            logger.warning("Failed to sync task %s: %s", task, exc)
            results.append({"task": task, "synced": False, "error": str(exc)})
    return results
