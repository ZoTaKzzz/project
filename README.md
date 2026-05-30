# Task Manager

A simple Python task manager that demonstrates file I/O, HTTP requests, data parsing, and database operations.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
python -m task_manager
```

## Project Structure

- `task_manager/` — Main application package
  - `app.py` — CLI entry point
  - `storage.py` — File-based task storage
  - `api_client.py` — HTTP client for fetching remote tasks
  - `parser.py` — Config and data file parsing
  - `db.py` — SQLite database operations
  - `utils.py` — Shared utility functions
