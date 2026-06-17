"""Deals record client with schema-aware value formatting."""

from __future__ import annotations

from attio_client.objects.base_record import RecordClient


class DealsClient(RecordClient):
    object_slug = "deals"
    SCHEMA = {
        "record_id": {"type": "text", "required": False, "unique": True},
        "name": {"type": "text", "required": True, "unique": False},
        "stage": {"type": "status", "required": True, "unique": False},
        "owner": {"type": "actor-reference", "required": True, "unique": False},
        "value": {"type": "currency", "required": False, "unique": False},
        "associated_people": {
            "type": "record-reference",
            "required": False,
            "unique": False,
        },
        "associated_company": {
            "type": "record-reference",
            "required": False,
            "unique": False,
        },
        "location": {"type": "location", "required": False, "unique": False},
        "warmth": {"type": "select", "required": False, "unique": False},
        "notes": {"type": "text", "required": False, "unique": False},
        "point_of_contact": {
            "type": "record-reference",
            "required": False,
            "unique": False,
        },
        "group_size": {"type": "number", "required": False, "unique": False},
        "current_vendor": {
            "type": "record-reference",
            "required": False,
            "unique": False,
        },
        "primary_pain": {"type": "text", "required": False, "unique": False},
        "champion": {"type": "record-reference", "required": False, "unique": False},
        "price_per_user": {"type": "currency", "required": False, "unique": False},
    }
