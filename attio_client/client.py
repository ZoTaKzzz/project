"""Main entry point — the ``AttioClient`` facade.

Usage::

    from attio_client import AttioClient

    client = AttioClient("your-api-key")

    # Standard objects
    companies = client.companies.list(limit=10)
    client.people.upsert(
        {"name": {"first_name": "Jane", "last_name": "Doe"},
         "email_addresses": "jane@example.com"},
        matching_attribute="email_addresses",
    )

    # Custom objects (healthcare domain)
    facility = client.custom("facility")
    facility.create({"name": "General Hospital", "bed_count": 300})

    # Low-level endpoints
    client.objects.list()
    client.notes.create("companies", record_id, "Follow-up note")
"""

from __future__ import annotations

from attio_client.base import BaseClient
from attio_client.endpoints.attributes import AttributesEndpoint
from attio_client.endpoints.comments import CommentsEndpoint, ThreadsEndpoint
from attio_client.endpoints.entries import EntriesEndpoint
from attio_client.endpoints.lists import ListsEndpoint
from attio_client.endpoints.meta import MetaEndpoint
from attio_client.endpoints.notes import NotesEndpoint
from attio_client.endpoints.objects import ObjectsEndpoint
from attio_client.endpoints.records import RecordsEndpoint
from attio_client.endpoints.tasks import TasksEndpoint
from attio_client.endpoints.webhooks import WebhooksEndpoint
from attio_client.endpoints.workspace_members import WorkspaceMembersEndpoint
from attio_client.objects.companies import CompaniesClient
from attio_client.objects.custom import CustomObjectClient
from attio_client.objects.deals import DealsClient
from attio_client.objects.people import PeopleClient
from attio_client.objects.users import UsersClient
from attio_client.objects.workspaces import WorkspacesClient


class AttioClient:
    """High-level facade exposing both typed object clients and raw endpoints."""

    def __init__(self, api_key: str) -> None:
        self._http = BaseClient(api_key)

        # -- Standard object clients (schema-aware) --------------------------
        self.companies = CompaniesClient(self._http)
        self.people = PeopleClient(self._http)
        self.deals = DealsClient(self._http)
        self.users = UsersClient(self._http)
        self.workspaces = WorkspacesClient(self._http)

        # -- Low-level endpoint modules --------------------------------------
        self.records = RecordsEndpoint(self._http)
        self.objects = ObjectsEndpoint(self._http)
        self.attributes = AttributesEndpoint(self._http)
        self.lists = ListsEndpoint(self._http)
        self.entries = EntriesEndpoint(self._http)
        self.notes = NotesEndpoint(self._http)
        self.tasks = TasksEndpoint(self._http)
        self.comments = CommentsEndpoint(self._http)
        self.threads = ThreadsEndpoint(self._http)
        self.webhooks = WebhooksEndpoint(self._http)
        self.workspace_members = WorkspaceMembersEndpoint(self._http)
        self.meta = MetaEndpoint(self._http)

        # Cache for custom object clients
        self._custom_cache: dict[str, CustomObjectClient] = {}

    def custom(self, object_slug: str) -> CustomObjectClient:
        """Return a schema-aware client for a custom object.

        The schema is loaded from ``attio_schema.json`` so attribute types
        are automatically formatted.

        Common custom objects in this workspace::

            client.custom("facility")
            client.custom("health_system")
            client.custom("physician_group")
            client.custom("department")
            client.custom("workforce_group")
            client.custom("software_deployment")
            client.custom("group_membership")   # Decision Makers
        """
        if object_slug not in self._custom_cache:
            self._custom_cache[object_slug] = CustomObjectClient(
                self._http, object_slug
            )
        return self._custom_cache[object_slug]

    def identify(self) -> dict:
        """Return info about the current access token and workspace."""
        return self.meta.identify()
