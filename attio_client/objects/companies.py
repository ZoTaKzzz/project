"""Companies record client with schema-aware value formatting."""

from __future__ import annotations

from attio_client.objects.base_record import RecordClient


class CompaniesClient(RecordClient):
    object_slug = "companies"
    SCHEMA = {
        "record_id": {"type": "text", "required": False, "unique": True},
        "domains": {"type": "domain", "required": False, "unique": True},
        "name": {"type": "text", "required": False, "unique": False},
        "description": {"type": "text", "required": False, "unique": False},
        "team": {"type": "record-reference", "required": False, "unique": False},
        "categories": {"type": "select", "required": False, "unique": False},
        "primary_location": {"type": "location", "required": False, "unique": False},
        "logo_url": {"type": "text", "required": False, "unique": False},
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
        "estimated_arr_usd": {"type": "select", "required": False, "unique": False},
        "funding_raised_usd": {"type": "currency", "required": False, "unique": False},
        "foundation_date": {"type": "date", "required": False, "unique": False},
        "employee_range": {"type": "select", "required": False, "unique": False},
        "type": {"type": "select", "required": False, "unique": False},
        "users": {"type": "number", "required": False, "unique": False},
        "size_band": {"type": "select", "required": False, "unique": False},
        "priority": {"type": "select", "required": False, "unique": False},
        "current_vendor": {
            "type": "record-reference",
            "required": False,
            "unique": False,
        },
        "contract_end_date": {"type": "date", "required": False, "unique": False},
        "switch_openness": {"type": "select", "required": False, "unique": False},
        "address": {"type": "text", "required": False, "unique": False},
        "general_email": {"type": "text", "required": False, "unique": False},
    }
