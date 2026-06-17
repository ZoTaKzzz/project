"""Tasks endpoints: /tasks."""

from __future__ import annotations

from typing import Any

from attio_client.base import BaseClient


class TasksEndpoint:
    def __init__(self, http: BaseClient) -> None:
        self._http = http

    def create(
        self,
        content: str,
        *,
        deadline_at: str | None = None,
        is_completed: bool = False,
        assignees: list[str] | None = None,
        linked_records: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "data": {
                "content": content,
                "is_completed": is_completed,
            }
        }
        if deadline_at:
            body["data"]["deadline_at"] = deadline_at
        if assignees:
            body["data"]["assignees"] = [
                {"referenced_actor_type": "workspace-member", "referenced_actor_id": a}
                for a in assignees
            ]
        if linked_records:
            body["data"]["linked_records"] = linked_records
        return self._http.post("tasks", json_body=body)

    def get(self, task_id: str) -> dict[str, Any]:
        return self._http.get(f"tasks/{task_id}")

    def list(self) -> list[dict[str, Any]]:
        resp = self._http.get("tasks")
        return resp.get("data", [])

    def update(
        self,
        task_id: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        return self._http.patch(f"tasks/{task_id}", json_body={"data": kwargs})

    def delete(self, task_id: str) -> dict[str, Any]:
        return self._http.delete(f"tasks/{task_id}")
