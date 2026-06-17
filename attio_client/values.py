"""Helpers to format Python values into the Attio API's attribute value shapes.

Each public function returns the dict/list structure that the API expects
inside the ``values`` mapping of a record create/update payload.
"""

from __future__ import annotations

from typing import Any


def text(value: str) -> list[dict[str, Any]]:
    return [{"value": value}]


def number(value: int | float) -> list[dict[str, Any]]:
    return [{"value": value}]


def checkbox(value: bool) -> list[dict[str, Any]]:
    return [{"value": value}]


def rating(value: int) -> list[dict[str, Any]]:
    if not 0 <= value <= 5:
        raise ValueError("Rating must be between 0 and 5")
    return [{"value": value}]


def currency(value: float, currency_code: str = "USD") -> list[dict[str, Any]]:
    return [{"currency_value": value, "currency_code": currency_code}]


def date(value: str) -> list[dict[str, Any]]:
    """Expects ISO-8601 date string (YYYY-MM-DD)."""
    return [{"value": value}]


def timestamp(value: str) -> list[dict[str, Any]]:
    """Expects ISO-8601 datetime string."""
    return [{"value": value}]


def domain(value: str) -> list[dict[str, Any]]:
    return [{"domain": value}]


def email_address(address: str, label: str = "primary") -> list[dict[str, Any]]:
    return [{"email_address": address, "label": label}]


def phone_number(number_str: str, label: str = "primary") -> list[dict[str, Any]]:
    return [{"phone_number": number_str, "label": label}]


def location(
    *,
    line_1: str | None = None,
    line_2: str | None = None,
    city: str | None = None,
    state: str | None = None,
    postcode: str | None = None,
    country_code: str | None = None,
) -> list[dict[str, Any]]:
    loc: dict[str, Any] = {}
    if line_1 is not None:
        loc["line_1"] = line_1
    if line_2 is not None:
        loc["line_2"] = line_2
    if city is not None:
        loc["city"] = city
    if state is not None:
        loc["state"] = state
    if postcode is not None:
        loc["postcode"] = postcode
    if country_code is not None:
        loc["country_code"] = country_code
    return [loc]


def personal_name(
    first_name: str,
    last_name: str,
    full_name: str | None = None,
) -> list[dict[str, Any]]:
    val: dict[str, str] = {
        "first_name": first_name,
        "last_name": last_name,
    }
    if full_name is not None:
        val["full_name"] = full_name
    return [val]


def select(value: str) -> list[dict[str, Any]]:
    """Select by option title."""
    return [{"option": value}]


def status(value: str) -> list[dict[str, Any]]:
    """Status by title."""
    return [{"status": value}]


def record_reference(target_record_id: str) -> list[dict[str, Any]]:
    return [{"target_record_id": target_record_id}]


def actor_reference(
    referenced_actor_type: str, referenced_actor_id: str
) -> list[dict[str, Any]]:
    return [
        {
            "referenced_actor_type": referenced_actor_type,
            "referenced_actor_id": referenced_actor_id,
        }
    ]


# -- Convenience mapper -------------------------------------------------------

FORMATTERS: dict[str, Any] = {
    "text": text,
    "number": number,
    "checkbox": checkbox,
    "rating": rating,
    "currency": currency,
    "date": date,
    "timestamp": timestamp,
    "domain": domain,
    "email-address": email_address,
    "phone-number": phone_number,
    "location": location,
    "personal-name": personal_name,
    "select": select,
    "status": status,
    "record-reference": record_reference,
    "actor-reference": actor_reference,
}


def format_value(attr_type: str, value: Any) -> list[dict[str, Any]]:
    """Format a raw Python value using the appropriate Attio type formatter.

    For complex types (location, personal-name, currency) ``value`` should be
    a dict whose keys match the formatter's keyword arguments.
    """
    formatter = FORMATTERS.get(attr_type)
    if formatter is None:
        return [{"value": value}]
    if isinstance(value, dict):
        return formatter(**value)
    return formatter(value)
