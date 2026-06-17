"""Attio API Python Client.

A clean, OOP wrapper around the Attio REST API for managing CRM records
(hospitals, facilities, health systems, physician groups, people, etc.).
"""

from attio_client.client import AttioClient
from attio_client.exceptions import (
    AttioAPIError,
    AttioAuthError,
    AttioNotFoundError,
    AttioRateLimitError,
    AttioValidationError,
)

__all__ = [
    "AttioClient",
    "AttioAPIError",
    "AttioAuthError",
    "AttioNotFoundError",
    "AttioRateLimitError",
    "AttioValidationError",
]
