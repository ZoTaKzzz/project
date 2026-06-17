"""Notes endpoints: /notes."""

from __future__ import annotations

from typing import Any

from attio_client.base import BaseClient


class NotesEndpoint:
    def __init__(self, http: BaseClient) -> None:
        self._http = http

    def create(
        self,
        parent_object: str,
        parent_record_id: str,
        title: str,
        *,
        content_plaintext: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "data": {
                "parent_object": parent_object,
                "parent_record_id": parent_record_id,
                "title": title,
            }
        }
        if content_plaintext:
            body["data"]["content"] = {
                "type": "doc",
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": content_plaintext}],
                    }
                ],
            }
        return self._http.post("notes", json_body=body)

    def get(self, note_id: str) -> dict[str, Any]:
        return self._http.get(f"notes/{note_id}")

    def list(
        self,
        *,
        parent_object: str | None = None,
        parent_record_id: str | None = None,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {}
        if parent_object:
            params["parent_object"] = parent_object
        if parent_record_id:
            params["parent_record_id"] = parent_record_id
        resp = self._http.get("notes", params=params)
        return resp.get("data", [])

    def delete(self, note_id: str) -> dict[str, Any]:
        return self._http.delete(f"notes/{note_id}")
