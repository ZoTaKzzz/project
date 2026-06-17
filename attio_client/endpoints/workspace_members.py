"""Workspace members endpoints."""

from __future__ import annotations

from typing import Any

from attio_client.base import BaseClient


class WorkspaceMembersEndpoint:
    def __init__(self, http: BaseClient) -> None:
        self._http = http

    def list(self) -> list[dict[str, Any]]:
        resp = self._http.get("workspace_members")
        return resp.get("data", [])

    def get(self, member_id: str) -> dict[str, Any]:
        return self._http.get(f"workspace_members/{member_id}")
