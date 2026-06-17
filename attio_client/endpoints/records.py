"""Generic /objects/{object}/records endpoints."""

from __future__ import annotations

from typing import Any

from attio_client.base import BaseClient


class RecordsEndpoint:
    """CRUD operations on records for any object slug."""

    def __init__(self, http: BaseClient) -> None:
        self._http = http

    def _path(self, object_slug: str) -> str:
        return f"objects/{object_slug}/records"

    def create(
        self,
        object_slug: str,
        values: dict[str, Any],
    ) -> dict[str, Any]:
        return self._http.post(
            self._path(object_slug),
            json_body={"data": {"values": values}},
        )

    def get(self, object_slug: str, record_id: str) -> dict[str, Any]:
        return self._http.get(f"{self._path(object_slug)}/{record_id}")

    def list(
        self,
        object_slug: str,
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
            f"{self._path(object_slug)}/query",
            json_body=body,
            limit=limit,
        )

    def update(
        self,
        object_slug: str,
        record_id: str,
        values: dict[str, Any],
        *,
        overwrite_multiselect: bool = False,
    ) -> dict[str, Any]:
        method = "PUT" if overwrite_multiselect else "PATCH"
        return self._http._request(
            method,
            f"{self._path(object_slug)}/{record_id}",
            json_body={"data": {"values": values}},
        )

    def upsert(
        self,
        object_slug: str,
        values: dict[str, Any],
        matching_attribute: str,
    ) -> dict[str, Any]:
        return self._http.put(
            self._path(object_slug),
            json_body={
                "data": {
                    "values": values,
                    "matching_attribute": matching_attribute,
                }
            },
        )

    def delete(self, object_slug: str, record_id: str) -> dict[str, Any]:
        return self._http.delete(f"{self._path(object_slug)}/{record_id}")

    def search(
        self,
        query: str,
        *,
        object_slugs: list[str] | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        body: dict[str, Any] = {"query": query, "limit": limit}
        if object_slugs:
            body["objects"] = object_slugs
        resp = self._http.post("records/search", json_body=body)
        return resp.get("data", [])

    def get_attribute_values(
        self,
        object_slug: str,
        record_id: str,
        attribute_slug: str,
        *,
        show_historic: bool = False,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {}
        if show_historic:
            params["show_historic"] = "true"
        resp = self._http.get(
            f"{self._path(object_slug)}/{record_id}/attributes/{attribute_slug}/values",
            params=params,
        )
        return resp.get("data", [])

    def list_entries(
        self,
        object_slug: str,
        record_id: str,
    ) -> list[dict[str, Any]]:
        resp = self._http.get(
            f"{self._path(object_slug)}/{record_id}/entries",
        )
        return resp.get("data", [])
