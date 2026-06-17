"""Base record client that all object-specific clients inherit from."""

from __future__ import annotations

from typing import Any

from attio_client.base import BaseClient
from attio_client.values import format_value


class RecordClient:
    """Generic CRUD wrapper for a specific Attio object.

    Subclasses set ``object_slug`` and optionally ``SCHEMA`` to get
    automatic value formatting.
    """

    object_slug: str = ""
    SCHEMA: dict[str, dict[str, Any]] = {}

    def __init__(self, http: BaseClient) -> None:
        self._http = http

    def _path(self) -> str:
        return f"objects/{self.object_slug}/records"

    def _format_values(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Convert ``{slug: python_value}`` into Attio's nested value format.

        If a slug is in SCHEMA, its type is used for automatic formatting.
        Already-formatted values (lists of dicts) pass through untouched.
        """
        formatted: dict[str, Any] = {}
        for slug, val in raw.items():
            if isinstance(val, list) and val and isinstance(val[0], dict):
                formatted[slug] = val
                continue
            attr_info = self.SCHEMA.get(slug)
            if attr_info:
                formatted[slug] = format_value(attr_info["type"], val)
            else:
                formatted[slug] = format_value("text", val)
        return formatted

    def create(self, values: dict[str, Any]) -> dict[str, Any]:
        return self._http.post(
            self._path(),
            json_body={"data": {"values": self._format_values(values)}},
        )

    def get(self, record_id: str) -> dict[str, Any]:
        return self._http.get(f"{self._path()}/{record_id}")

    def list(
        self,
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
            f"{self._path()}/query",
            json_body=body,
            limit=limit,
        )

    def update(
        self,
        record_id: str,
        values: dict[str, Any],
        *,
        overwrite_multiselect: bool = False,
    ) -> dict[str, Any]:
        method = "PUT" if overwrite_multiselect else "PATCH"
        return self._http._request(
            method,
            f"{self._path()}/{record_id}",
            json_body={"data": {"values": self._format_values(values)}},
        )

    def upsert(
        self,
        values: dict[str, Any],
        matching_attribute: str,
    ) -> dict[str, Any]:
        return self._http.put(
            self._path(),
            json_body={
                "data": {
                    "values": self._format_values(values),
                    "matching_attribute": matching_attribute,
                }
            },
        )

    def delete(self, record_id: str) -> dict[str, Any]:
        return self._http.delete(f"{self._path()}/{record_id}")

    def search(self, query: str, *, limit: int = 20) -> list[dict[str, Any]]:
        resp = self._http.post(
            "records/search",
            json_body={
                "query": query,
                "objects": [self.object_slug],
                "limit": limit,
            },
        )
        return resp.get("data", [])

    def get_attribute_values(
        self,
        record_id: str,
        attribute_slug: str,
        *,
        show_historic: bool = False,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {}
        if show_historic:
            params["show_historic"] = "true"
        resp = self._http.get(
            f"{self._path()}/{record_id}/attributes/{attribute_slug}/values",
            params=params,
        )
        return resp.get("data", [])

    def list_entries(self, record_id: str) -> list[dict[str, Any]]:
        resp = self._http.get(f"{self._path()}/{record_id}/entries")
        return resp.get("data", [])
