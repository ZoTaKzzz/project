"""People record client with schema-aware value formatting."""

from __future__ import annotations

from attio_client.objects.base_record import RecordClient


class PeopleClient(RecordClient):
    object_slug = "people"
    SCHEMA = {
        "record_id": {"type": "text", "required": False, "unique": True},
        "name": {"type": "personal-name", "required": False, "unique": False},
        "email_addresses": {"type": "email-address", "required": False, "unique": True},
        "description": {"type": "text", "required": False, "unique": False},
        "company": {"type": "record-reference", "required": False, "unique": False},
        "job_title": {"type": "text", "required": False, "unique": False},
        "avatar_url": {"type": "text", "required": False, "unique": False},
        "phone_numbers": {"type": "phone-number", "required": False, "unique": False},
        "primary_location": {"type": "location", "required": False, "unique": False},
        "angellist": {"type": "text", "required": False, "unique": False},
        "facebook": {"type": "text", "required": False, "unique": False},
        "instagram": {"type": "text", "required": False, "unique": False},
        "linkedin": {"type": "text", "required": False, "unique": False},
        "twitter": {"type": "text", "required": False, "unique": False},
        "twitter_follower_count": {
            "type": "number",
            "required": False,
            "unique": False,
        },
        "source": {"type": "select", "required": False, "unique": False},
        "persona_type": {"type": "select", "required": False, "unique": False},
        "notes": {"type": "text", "required": False, "unique": False},
        "group_membership": {
            "type": "record-reference",
            "required": False,
            "unique": False,
        },
    }
