"""Workspaces record client with schema-aware value formatting."""

from __future__ import annotations

from attio_client.objects.base_record import RecordClient


class WorkspacesClient(RecordClient):
    object_slug = "workspaces"
    SCHEMA = {
        "record_id": {"type": "text", "required": False, "unique": True},
        "workspace_id": {"type": "text", "required": True, "unique": True},
        "name": {"type": "text", "required": False, "unique": False},
        "users": {"type": "record-reference", "required": False, "unique": False},
        "company": {"type": "record-reference", "required": False, "unique": False},
        "avatar_url": {"type": "text", "required": False, "unique": False},
        "status": {"type": "select", "required": False, "unique": False},
        "stage": {"type": "select", "required": False, "unique": False},
    }
