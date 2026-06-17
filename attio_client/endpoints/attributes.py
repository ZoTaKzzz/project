"""Attribute management endpoints."""

from __future__ import annotations

from typing import Any

from attio_client.base import BaseClient


class AttributesEndpoint:
    def __init__(self, http: BaseClient) -> None:
        self._http = http

    def _path(self, target_type: str, target_slug: str) -> str:
        """``target_type`` is 'objects' or 'lists'."""
        return f"{target_type}/{target_slug}/attributes"

    def list(self, target_type: str, target_slug: str) -> list[dict[str, Any]]:
        resp = self._http.get(self._path(target_type, target_slug))
        return resp.get("data", [])

    def get(
        self, target_type: str, target_slug: str, attribute_slug: str
    ) -> dict[str, Any]:
        return self._http.get(
            f"{self._path(target_type, target_slug)}/{attribute_slug}"
        )

    def create(
        self,
        target_type: str,
        target_slug: str,
        *,
        title: str,
        api_slug: str,
        type_: str,
        is_required: bool = False,
        is_unique: bool = False,
        is_multiselect: bool = False,
        default_value: Any = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "data": {
                "title": title,
                "api_slug": api_slug,
                "type": type_,
                "is_required": is_required,
                "is_unique": is_unique,
                "is_multiselect": is_multiselect,
            }
        }
        if default_value is not None:
            body["data"]["default_value"] = default_value
        return self._http.post(self._path(target_type, target_slug), json_body=body)

    def update(
        self,
        target_type: str,
        target_slug: str,
        attribute_slug: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        return self._http.patch(
            f"{self._path(target_type, target_slug)}/{attribute_slug}",
            json_body={"data": kwargs},
        )

    # -- Select options -------------------------------------------------------

    def list_select_options(
        self, target_type: str, target_slug: str, attribute_slug: str
    ) -> list[dict[str, Any]]:
        resp = self._http.get(
            f"{self._path(target_type, target_slug)}/{attribute_slug}/options"
        )
        return resp.get("data", [])

    def create_select_option(
        self,
        target_type: str,
        target_slug: str,
        attribute_slug: str,
        title: str,
    ) -> dict[str, Any]:
        return self._http.post(
            f"{self._path(target_type, target_slug)}/{attribute_slug}/options",
            json_body={"data": {"title": title}},
        )

    def update_select_option(
        self,
        target_type: str,
        target_slug: str,
        attribute_slug: str,
        option_id: str,
        title: str,
    ) -> dict[str, Any]:
        return self._http.patch(
            f"{self._path(target_type, target_slug)}/{attribute_slug}/options/{option_id}",
            json_body={"data": {"title": title}},
        )

    # -- Statuses -------------------------------------------------------------

    def list_statuses(
        self, target_type: str, target_slug: str, attribute_slug: str
    ) -> list[dict[str, Any]]:
        resp = self._http.get(
            f"{self._path(target_type, target_slug)}/{attribute_slug}/statuses"
        )
        return resp.get("data", [])

    def create_status(
        self,
        target_type: str,
        target_slug: str,
        attribute_slug: str,
        title: str,
    ) -> dict[str, Any]:
        return self._http.post(
            f"{self._path(target_type, target_slug)}/{attribute_slug}/statuses",
            json_body={"data": {"title": title}},
        )

    def update_status(
        self,
        target_type: str,
        target_slug: str,
        attribute_slug: str,
        status_id: str,
        title: str,
    ) -> dict[str, Any]:
        return self._http.patch(
            f"{self._path(target_type, target_slug)}/{attribute_slug}/statuses/{status_id}",
            json_body={"data": {"title": title}},
        )
