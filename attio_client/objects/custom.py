"""Dynamic client for custom Attio objects.

Loads schema from attio_schema.json so the same RecordClient interface
works for workforce_group, facility, health_system, etc.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from attio_client.base import BaseClient
from attio_client.objects.base_record import RecordClient

_SCHEMA_PATH = Path(__file__).resolve().parent.parent / "attio_schema.json"
_LOADED_SCHEMA: dict[str, list[dict[str, Any]]] | None = None


def _load_schema() -> dict[str, list[dict[str, Any]]]:
    global _LOADED_SCHEMA  # noqa: PLW0603
    if _LOADED_SCHEMA is None:
        raw = json.loads(_SCHEMA_PATH.read_text())
        _LOADED_SCHEMA = {obj["slug"]: obj["attributes"] for obj in raw["objects"]}
    return _LOADED_SCHEMA


class CustomObjectClient(RecordClient):
    """Dynamically configured client for any object defined in attio_schema.json."""

    def __init__(self, http: BaseClient, object_slug: str) -> None:
        super().__init__(http)
        self.object_slug = object_slug
        schema_map = _load_schema()
        attrs = schema_map.get(object_slug, [])
        self.SCHEMA = {
            attr["slug"]: {
                "type": attr["type"],
                "required": attr.get("required", False),
                "unique": attr.get("unique", False),
            }
            for attr in attrs
        }
