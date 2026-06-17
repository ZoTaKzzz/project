"""Object management endpoints: /objects."""

from __future__ import annotations

from typing import Any

from attio_client.base import BaseClient


class ObjectsEndpoint:
    def __init__(self, http: BaseClient) -> None:
        self._http = http

    def list(self) -> list[dict[str, Any]]:
        resp = self._http.get("objects")
        return resp.get("data", [])

    def get(self, object_id_or_slug: str) -> dict[str, Any]:
        return self._http.get(f"objects/{object_id_or_slug}")

    def create(
        self,
        api_slug: str,
        singular_noun: str,
        plural_noun: str,
    ) -> dict[str, Any]:
        return self._http.post(
            "objects",
            json_body={
                "data": {
                    "api_slug": api_slug,
                    "singular_noun": singular_noun,
                    "plural_noun": plural_noun,
                }
            },
        )

    def update(
        self,
        object_id_or_slug: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        return self._http.patch(
            f"objects/{object_id_or_slug}",
            json_body={"data": kwargs},
        )
