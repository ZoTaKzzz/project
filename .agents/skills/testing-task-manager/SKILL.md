---
name: testing-task-manager
description: Test the task manager CLI app end-to-end. Use when verifying error handling, storage, database, or API client changes.
---

# Testing the Task Manager

## Quick Start

```bash
cd /home/ubuntu/repos/project
pip install -r requirements.txt
```

## Running the App

The app is a CLI tool:
```bash
python -m task_manager add "Task title" <priority>
python -m task_manager list
python -m task_manager stats
python -m task_manager export tasks.json
```

Config is loaded from `config.json` in the working directory. If missing, defaults are used (SQLite DB at `tasks.db`).

## Testing Strategy

All testing is CLI/shell-based — no GUI, no recording needed.

### Happy Path
Run `add`, `list`, `stats` commands and verify output matches expected values.

### Error Handling (Adversarial Tests)
Use `python -c` one-liners to call module functions directly with bad input. Key test patterns:

1. **Corrupt JSON** — Write bad JSON to a file, call `storage.load_tasks()`. Expect `ValueError` with `"Corrupt task file"`.
2. **Permission denied** — Call `storage.save_tasks('/root/no_permission.json', [])`. Expect `OSError`.
3. **Bad DB path** — Call `db.connect('/root/no_access/test.db')`. Expect `DatabaseError`.
4. **Invalid priority** — Call `parser.parse_priority('high')`. Expect `ValueError`.
5. **Missing file size** — Call `storage.get_file_size('/nonexistent')`. Expect return value `-1` (not `0`).
6. **Validation errors** — Call `parser.validate_task({'title': 123})`. Expect list of error strings.
7. **Sync failure recording** — Call `api_client.sync_tasks([...], 'http://localhost:99999')`. Expect all tasks in result list with `synced=False`.
8. **Bad config at startup** — Write invalid JSON to `config.json`, run CLI. Expect exit code 1 and `"Initialization failed"` in stderr.

### Key Modules
- `task_manager/storage.py` — File I/O with JSON
- `task_manager/db.py` — SQLite operations, custom `DatabaseError`
- `task_manager/api_client.py` — HTTP client, custom `APIError`
- `task_manager/parser.py` — Config/CSV parsing, validation
- `task_manager/utils.py` — Shared helpers
- `task_manager/app.py` — CLI entry point

## Cleanup
Remove `tasks.db` and `config.json` between test runs to start fresh:
```bash
rm -f tasks.db config.json
```

## Devin Secrets Needed
None — all testing is local with SQLite and no external APIs.
