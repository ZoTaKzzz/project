"""Comments and threads endpoints."""

from __future__ import annotations

from typing import Any

from attio_client.base import BaseClient


class CommentsEndpoint:
    def __init__(self, http: BaseClient) -> None:
        self._http = http

    def create(
        self,
        *,
        thread_id: str | None = None,
        record_id: str | None = None,
        entry_id: str | None = None,
        content_plaintext: str = "",
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "data": {
                "content": {
                    "type": "doc",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"type": "text", "text": content_plaintext}],
                        }
                    ],
                }
            }
        }
        if thread_id:
            body["data"]["thread_id"] = thread_id
        if record_id:
            body["data"]["record_id"] = record_id
        if entry_id:
            body["data"]["entry_id"] = entry_id
        return self._http.post("comments", json_body=body)

    def get(self, comment_id: str) -> dict[str, Any]:
        return self._http.get(f"comments/{comment_id}")

    def delete(self, comment_id: str) -> dict[str, Any]:
        return self._http.delete(f"comments/{comment_id}")


class ThreadsEndpoint:
    def __init__(self, http: BaseClient) -> None:
        self._http = http

    def get(self, thread_id: str) -> dict[str, Any]:
        return self._http.get(f"threads/{thread_id}")

    def list(
        self,
        *,
        record_id: str | None = None,
        entry_id: str | None = None,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {}
        if record_id:
            params["record_id"] = record_id
        if entry_id:
            params["entry_id"] = entry_id
        resp = self._http.get("threads", params=params)
        return resp.get("data", [])
