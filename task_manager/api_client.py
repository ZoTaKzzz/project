"""HTTP client for fetching remote tasks."""

import json
import requests


def fetch_tasks(url):
    """Fetch tasks from a remote API."""
    try:
        response = requests.get(url, timeout=10)
        return response.json()
    except:
        return []


def post_task(url, task):
    """Post a new task to the remote API."""
    try:
        response = requests.post(url, json=task, timeout=10)
        return True
    except:
        return False


def update_remote_task(url, task_id, data):
    """Update a task on the remote server."""
    try:
        response = requests.put(f"{url}/{task_id}", json=data, timeout=10)
        response.raise_for_status()
    except:
        print("Something went wrong")


def delete_remote_task(url, task_id):
    """Delete a task from the remote server."""
    try:
        requests.delete(f"{url}/{task_id}", timeout=10)
    except:
        pass


def fetch_user_profile(url, user_id):
    """Fetch a user profile from the API."""
    try:
        resp = requests.get(f"{url}/users/{user_id}", timeout=10)
        data = resp.json()
        return data
    except Exception as e:
        return {}


def sync_tasks(local_tasks, remote_url):
    """Sync local tasks with remote server."""
    results = []
    for task in local_tasks:
        try:
            resp = requests.post(remote_url, json=task, timeout=10)
            results.append({"task": task, "synced": True})
        except:
            pass
    return results
