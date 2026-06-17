"""List entry endpoints: /lists/{list}/entries."""

from __future__ import annotations

from typing import Any

from attio_client.base import BaseClient


class EntriesEndpoint:
    def __init__(self, http: BaseClient) -> None:
        self._http = http

    def _path(self, list_slug: str) -> str:
        return f"lists/{list_slug}/entries"

    def create(
        self,
        list_slug: str,
        parent_record_id: str,
        *,
        parent_object: str,
        entry_values: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "data": {
                "parent_record_id": parent_record_id,
                "parent_object": parent_object,
            }
        }
        if entry_values:
            body["data"]["entry_values"] = entry_values
        return self._http.post(self._path(list_slug), json_body=body)

    def get(self, list_slug: str, entry_id: str) -> dict[str, Any]:
        return self._http.get(f"{self._path(list_slug)}/{entry_id}")

    def list(
        self,
        list_slug: str,
        *,
        filter_: dict[str, Any] | None = None,
        sorts: list[dict[str, Any]] | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        body: dict[str, Any] = {}
        if filter_ is not None:
            body["filter"] = filter_
        if sorts is not None:
            body["sorts"] = sorts
        return self._http.paginate(
            "POST",
            f"{self._path(list_slug)}/query",
            json_body=body,
            limit=limit,
        )

    def update(
        self,
        list_slug: str,
        entry_id: str,
        entry_values: dict[str, Any],
        *,
        overwrite_multiselect: bool = False,
    ) -> dict[str, Any]:
        method = "PUT" if overwrite_multiselect else "PATCH"
        return self._http._request(
            method,
            f"{self._path(list_slug)}/{entry_id}",
            json_body={"data": {"entry_values": entry_values}},
        )

    def upsert_by_parent(
        self,
        list_slug: str,
        parent_record_id: str,
        parent_object: str,
        entry_values: dict[str, Any],
    ) -> dict[str, Any]:
        return self._http.put(
            self._path(list_slug),
            json_body={
                "data": {
                    "parent_record_id": parent_record_id,
                    "parent_object": parent_object,
                    "entry_values": entry_values,
                }
            },
        )

    def delete(self, list_slug: str, entry_id: str) -> dict[str, Any]:
        return self._http.delete(f"{self._path(list_slug)}/{entry_id}")

    def get_attribute_values(
        self,
        list_slug: str,
        entry_id: str,
        attribute_slug: str,
        *,
        show_historic: bool = False,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {}
        if show_historic:
            params["show_historic"] = "true"
        resp = self._http.get(
            f"{self._path(list_slug)}/{entry_id}/attributes/{attribute_slug}/values",
            params=params,
        )
        return resp.get("data", [])
