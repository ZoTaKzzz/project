"""Object-specific record clients."""

from attio_client.objects.base_record import RecordClient
from attio_client.objects.companies import CompaniesClient
from attio_client.objects.custom import CustomObjectClient
from attio_client.objects.deals import DealsClient
from attio_client.objects.people import PeopleClient
from attio_client.objects.users import UsersClient
from attio_client.objects.workspaces import WorkspacesClient

__all__ = [
    "RecordClient",
    "CompaniesClient",
    "CustomObjectClient",
    "DealsClient",
    "PeopleClient",
    "UsersClient",
    "WorkspacesClient",
]
