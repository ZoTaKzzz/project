"""Webhooks endpoints: /webhooks."""

from __future__ import annotations

from typing import Any

from attio_client.base import BaseClient


class WebhooksEndpoint:
    def __init__(self, http: BaseClient) -> None:
        self._http = http

    def create(
        self,
        target_url: str,
        subscriptions: list[dict[str, Any]],
    ) -> dict[str, Any]:
        return self._http.post(
            "webhooks",
            json_body={
                "data": {
                    "target_url": target_url,
                    "subscriptions": subscriptions,
                }
            },
        )

    def get(self, webhook_id: str) -> dict[str, Any]:
        return self._http.get(f"webhooks/{webhook_id}")

    def list(self) -> list[dict[str, Any]]:
        resp = self._http.get("webhooks")
        return resp.get("data", [])

    def update(
        self,
        webhook_id: str,
        *,
        target_url: str | None = None,
        subscriptions: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"data": {}}
        if target_url:
            body["data"]["target_url"] = target_url
        if subscriptions is not None:
            body["data"]["subscriptions"] = subscriptions
        return self._http.patch(f"webhooks/{webhook_id}", json_body=body)

    def delete(self, webhook_id: str) -> dict[str, Any]:
        return self._http.delete(f"webhooks/{webhook_id}")
