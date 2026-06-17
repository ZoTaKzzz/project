"""Users record client with schema-aware value formatting."""

from __future__ import annotations

from attio_client.objects.base_record import RecordClient


class UsersClient(RecordClient):
    object_slug = "users"
    SCHEMA = {
        "record_id": {"type": "text", "required": False, "unique": True},
        "person": {"type": "record-reference", "required": False, "unique": False},
        "primary_email_address": {
            "type": "email-address",
            "required": True,
            "unique": True,
        },
        "user_id": {"type": "text", "required": True, "unique": True},
        "workspace": {"type": "record-reference", "required": False, "unique": False},
    }
