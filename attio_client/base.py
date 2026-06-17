"""Low-level HTTP transport for the Attio REST API."""

from __future__ import annotations

import time
from typing import Any

import requests

from attio_client.exceptions import (
    AttioAPIError,
    AttioAuthError,
    AttioNotFoundError,
    AttioRateLimitError,
    AttioValidationError,
)

BASE_URL = "https://api.attio.com/v2"
MAX_RETRIES = 3
BACKOFF_FACTOR = 1.0


class BaseClient:
    """Handles authentication, request dispatch, pagination, and retries."""

    def __init__(self, api_key: str, base_url: str = BASE_URL) -> None:
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )
        self._base_url = base_url.rstrip("/")

    # -- HTTP primitives ------------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self._base_url}/{path.lstrip('/')}"
        last_exc: Exception | None = None

        for attempt in range(MAX_RETRIES):
            resp = self._session.request(method, url, params=params, json=json_body)

            if resp.status_code < 400:
                return resp.json() if resp.content else {}

            body = resp.json() if resp.content else {}
            msg = body.get("message", resp.text)

            if resp.status_code == 401:
                raise AttioAuthError(msg, status_code=401, response_body=body)
            if resp.status_code == 404:
                raise AttioNotFoundError(msg, status_code=404, response_body=body)
            if resp.status_code == 429:
                retry_after = float(
                    resp.headers.get("Retry-After", BACKOFF_FACTOR * (2**attempt))
                )
                last_exc = AttioRateLimitError(
                    msg,
                    retry_after=retry_after,
                    status_code=429,
                    response_body=body,
                )
                time.sleep(retry_after)
                continue
            if resp.status_code in (400, 422):
                raise AttioValidationError(
                    msg, status_code=resp.status_code, response_body=body
                )
            if resp.status_code >= 500:
                last_exc = AttioAPIError(
                    msg, status_code=resp.status_code, response_body=body
                )
                time.sleep(BACKOFF_FACTOR * (2**attempt))
                continue

            raise AttioAPIError(msg, status_code=resp.status_code, response_body=body)

        raise last_exc  # type: ignore[misc]

    def get(self, path: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._request("GET", path, params=params)

    def post(
        self,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self._request("POST", path, json_body=json_body, params=params)

    def put(
        self,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self._request("PUT", path, json_body=json_body)

    def patch(
        self,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self._request("PATCH", path, json_body=json_body)

    def delete(self, path: str) -> dict[str, Any]:
        return self._request("DELETE", path)

    # -- Pagination -----------------------------------------------------------

    def paginate(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Auto-paginate through a list endpoint, collecting all results."""
        all_items: list[dict[str, Any]] = []
        offset = 0
        page_size = min(limit, 500) if limit else 500

        while True:
            body = dict(json_body or {})
            body["limit"] = page_size
            body["offset"] = offset

            resp = self._request(method, path, json_body=body, params=params)
            data = resp.get("data", [])
            all_items.extend(data)

            if limit and len(all_items) >= limit:
                return all_items[:limit]

            next_cursor = resp.get("next_page_offset")
            if next_cursor is None or len(data) < page_size:
                break
            offset = next_cursor

        return all_items
