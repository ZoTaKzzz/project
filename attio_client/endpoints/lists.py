"""List management endpoints: /lists."""

from __future__ import annotations

from typing import Any

from attio_client.base import BaseClient


class ListsEndpoint:
    def __init__(self, http: BaseClient) -> None:
        self._http = http

    def list(self) -> list[dict[str, Any]]:
        resp = self._http.get("lists")
        return resp.get("data", [])

    def get(self, list_id_or_slug: str) -> dict[str, Any]:
        return self._http.get(f"lists/{list_id_or_slug}")

    def create(
        self,
        name: str,
        *,
        parent_object: str,
        workspace_access: str = "full-access",
    ) -> dict[str, Any]:
        return self._http.post(
            "lists",
            json_body={
                "data": {
                    "name": name,
                    "parent_object": parent_object,
                    "workspace_access": workspace_access,
                }
            },
        )

    def update(
        self,
        list_id_or_slug: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        return self._http.patch(
            f"lists/{list_id_or_slug}",
            json_body={"data": kwargs},
        )
