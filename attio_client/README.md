# Attio API Python Client

A clean, OOP wrapper around the [Attio REST API](https://docs.attio.com/rest-api/overview.md) for managing CRM records — hospitals, facilities, health systems, physician groups, people, companies, deals, and more.

## Architecture

```
attio-client/
├── client.py              # AttioClient facade — main entry point
├── base.py                # HTTP transport: auth, retries, rate-limit backoff, pagination
├── exceptions.py          # Typed exceptions (auth, 404, rate-limit, validation)
├── values.py              # Value formatters for every Attio attribute type
├── attio_schema.json      # Workspace schema (objects + attributes)
├── endpoints/             # Low-level, 1:1 endpoint wrappers
│   ├── records.py         # Generic record CRUD + search
│   ├── objects.py         # Object management
│   ├── attributes.py      # Attribute + select/status option management
│   ├── lists.py           # List management
│   ├── entries.py         # List entry CRUD
│   ├── notes.py           # Notes
│   ├── tasks.py           # Tasks
│   ├── comments.py        # Comments & threads
│   ├── webhooks.py        # Webhooks
│   ├── workspace_members.py
│   └── meta.py            # Token identification
└── objects/               # Schema-aware record clients
    ├── base_record.py     # RecordClient base class
    ├── companies.py       # CompaniesClient
    ├── people.py          # PeopleClient
    ├── deals.py           # DealsClient
    ├── users.py           # UsersClient
    ├── workspaces.py      # WorkspacesClient
    └── custom.py          # CustomObjectClient (loads schema from JSON)
```

## Quick Start

```python
from attio_client import AttioClient

client = AttioClient("your-api-key")

# -- Standard objects (typed, schema-aware) ----------------------------------

# List companies
companies = client.companies.list(limit=10)

# Create/upsert a person by email
client.people.upsert(
    {
        "name": {"first_name": "Jane", "last_name": "Doe"},
        "email_addresses": "jane@example.com",
        "job_title": "CTO",
    },
    matching_attribute="email_addresses",
)

# Create a deal
client.deals.create({
    "name": "Acme Hospital - Scheduling Platform",
    "stage": "Qualification",
    "value": {"value": 50000, "currency_code": "USD"},
})

# -- Custom objects (healthcare domain) --------------------------------------

facilities = client.custom("facility")
health_systems = client.custom("health_system")
physicians = client.custom("physician_group")
departments = client.custom("department")
workforce = client.custom("workforce_group")
deployments = client.custom("software_deployment")
decision_makers = client.custom("group_membership")

# Create a facility
facilities.create({
    "name": "Memorial General Hospital",
    "bed_count": 450,
    "hospital_type": "General Acute Care",
    "trauma_level": "Level II",
})

# Upsert a health system by name
health_systems.upsert(
    {"name": "HCA Healthcare", "state": "TN", "number_of_hospitals": 182},
    matching_attribute="name",
)

# -- Low-level endpoints -----------------------------------------------------

# Search across all objects
results = client.records.search("Memorial Hospital")

# Manage attributes
attrs = client.attributes.list("objects", "facility")

# Add a note to a record
client.notes.create("companies", "<record-id>", "Follow-up scheduled")

# Identify the current token
info = client.identify()
```

## Value Formatting

The client automatically formats Python values into Attio's API structure.
Pass plain Python types and the client handles the rest:

| Python value | Attio type | What you pass |
|---|---|---|
| `"Acme Corp"` | text | `"Acme Corp"` |
| `42` | number | `42` |
| `"jane@acme.com"` | email-address | `"jane@acme.com"` |
| `"+1-555-0123"` | phone-number | `"+1-555-0123"` |
| `"acme.com"` | domain | `"acme.com"` |
| `"2024-03-15"` | date | `"2024-03-15"` |
| `{"value": 50000, "currency_code": "USD"}` | currency | dict |
| `{"first_name": "Jane", "last_name": "Doe"}` | personal-name | dict |
| `{"city": "Nashville", "state": "TN"}` | location | dict |
| `"Option Title"` | select | `"Option Title"` |
| `"Status Title"` | status | `"Status Title"` |
| `"<record-id>"` | record-reference | target record ID |

## Error Handling

```python
from attio_client import AttioClient, AttioNotFoundError, AttioRateLimitError

client = AttioClient("your-api-key")

try:
    record = client.companies.get("non-existent-id")
except AttioNotFoundError:
    print("Record not found")
except AttioRateLimitError as e:
    print(f"Rate limited — retry after {e.retry_after}s")
```

## Workspace Schema

The `attio_schema.json` file defines all objects and their attributes in this
workspace. The `CustomObjectClient` reads this file to provide automatic value
formatting for custom objects. Update this file when you add/modify objects or
attributes in Attio.

### Objects in this workspace

| Slug | Display Name | Key Attributes |
|---|---|---|
| `companies` | Company | domains, name, priority, type, size_band |
| `people` | Person | name, email_addresses, job_title, company |
| `deals` | Deal | name, stage, owner, value |
| `users` | User | primary_email_address, user_id |
| `workspaces` | Workspace | workspace_id, name |
| `facility` | Facility | name, bed_count, hospital_type, trauma_level |
| `health_system` | Health System | name, state, number_of_hospitals |
| `physician_group` | Physician Group | name, number_of_clinicians, ownership |
| `department` | Department | name, department_type, facility |
| `workforce_group` | Workforce Group | name, staffing_model, workers |
| `software_deployment` | Software Deployment | name, status, pricing |
| `group_membership` | Decision Makers | person, job_title, phone_number, email_addresses |
