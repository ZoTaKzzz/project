"""Custom exceptions for the Attio API client."""

from __future__ import annotations

from typing import Any


class AttioAPIError(Exception):
    """Base exception for all Attio API errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: dict[str, Any] | None = None,
    ) -> None:
        self.status_code = status_code
        self.response_body = response_body or {}
        super().__init__(message)


class AttioAuthError(AttioAPIError):
    """Raised on 401 Unauthorized responses."""


class AttioNotFoundError(AttioAPIError):
    """Raised on 404 Not Found responses."""


class AttioRateLimitError(AttioAPIError):
    """Raised on 429 Too Many Requests responses."""

    def __init__(
        self,
        message: str,
        retry_after: float | None = None,
        **kwargs: Any,
    ) -> None:
        self.retry_after = retry_after
        super().__init__(message, **kwargs)


class AttioValidationError(AttioAPIError):
    """Raised on 400/422 validation errors."""
