"""Meta endpoints (identify, etc.)."""

from __future__ import annotations

from typing import Any

from attio_client.base import BaseClient


class MetaEndpoint:
    def __init__(self, http: BaseClient) -> None:
        self._http = http

    def identify(self) -> dict[str, Any]:
        """Return info about the current access token and workspace."""
        return self._http.get("self")
