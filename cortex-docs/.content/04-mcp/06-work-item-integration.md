# Work Item Integration (ADO Plugin)

---
title: Work Item Integration — ADO Plugin & Provider Architecture
type: how-to
audience: [Software Developers, Product Owners, Business Leaders]
last_verified: 2026-02-21
source_of_truth: cortex/repositories/ + cortex/mcp/tools/work_item_tool.py
phase: Phase 15 — Work Item Provider
ac_ids: [AC-P15-001, AC-P15-002, AC-P15-003, AC-P15-004, AC-P15-005, AC-P15-006, AC-P15-007, AC-P15-008, AC-P15-009, AC-P15-010]
order: 6
---

> **Brain analogy:** The WorkItemProvider is a **sensory nerve pathway** — your planning tool (ADO, Jira) sends signals about sprint requirements; CORTEX receives them through a standardised nerve ending (`cortex_fetch_work_items`) without caring which sensory receptor generated the signal.

---

## Overview

Phase 15 introduced a **provider-agnostic work item integration layer** that connects any ticketing system to CORTEX through a single MCP tool surface. The architecture is a three-layer stack:

```
[Copilot Chat / IDE]
        │
        │  cortex_fetch_work_items(project="MyProject")
        ▼
[cortex/mcp/tools/work_item_tool.py]  ← MCP surface (always identical)
        │
        │  get_work_item_provider()
        ▼
[cortex/repositories/provider_factory.py]  ← WORK_ITEM_SOURCE env selector
        │
        ├── "ado"     → ADOWorkItemProvider
        ├── "jira"    → JiraWorkItemProvider  (add your own)
        └── "custom"  → YourCompanyProvider   (add your own)
        │
        ▼
[cortex/repositories/ado/ado_provider.py]  ← Company fills in REST calls
        │
        ▼
[WorkItem dataclass]  ← Canonical shape, provider-independent
```

---

## Architecture

### 1. `WorkItem` Dataclass — Canonical Shape

**File:** `cortex/repositories/work_item_provider.py`

```python
@dataclass
class WorkItem:
    id: str            # System.Id  (ADO) / issue.id (Jira)
    title: str         # System.Title
    description: str   # System.Description / acceptance criteria
    state: str         # System.State — "Active", "Resolved", "To Do"
    type: str          # "User Story", "Bug", "Task", "Epic"
    tags: List[str]    # Parsed from System.Tags (semicolon-delimited)
    url: str           # Direct browser URL to item
    raw: Dict[str, Any]  # Full unmodified API response — escape hatch
```

> **The `raw` field is the escape hatch.** CORTEX never parses it. Company-specific fields — Area Path, Sprint, Custom.* ADO fields, Jira components — survive intact and are accessible as `item.raw["fields"]["Custom.YourField"]`.

---

### 2. `WorkItemProvider` Protocol — Integration Contract

**File:** `cortex/repositories/work_item_provider.py`

Companies implement this `@runtime_checkable` Protocol once. No other CORTEX files need to change when a new provider is added.

```python
@runtime_checkable
class WorkItemProvider(Protocol):
    def fetch_user_stories(self, project: str, **kwargs: Any) -> List[WorkItem]:
        """Fetch user stories / sprint backlog for the project."""

    def fetch_by_id(self, item_id: str) -> WorkItem:
        """Fetch a single work item by its system ID."""

    def health_check(self) -> bool:
        """Return True if the ticketing system is reachable."""
```

---

### 3. `ADOWorkItemProvider` — Azure DevOps Adapter

**File:** `cortex/repositories/ado/ado_provider.py`

The supplied ADO adapter is a **production-ready stub** with:
- ✅ Full Protocol compliance (`fetch_user_stories`, `fetch_by_id`, `health_check`)
- ✅ `_map(raw)` helper that correctly maps ADO field paths → `WorkItem` fields
- ✅ `_auth_headers()` helper for PAT-based Basic auth (override for OAuth2 / managed identity)
- ✅ CORE-011 type hints on all methods
- ✅ CORE-012 docstrings on all public APIs
- ⚠️ HTTP client stubs — companies fill in the `fetch_user_stories` and `fetch_by_id` bodies with their ADO REST calls

**Configuration (environment variables):**

| Variable | Required | Description |
|----------|----------|-------------|
| `ADO_ORG_URL` | ✅ Yes | `https://dev.azure.com/your-org` |
| `ADO_PAT` | ✅ Yes* | Personal Access Token (* empty for managed identity) |
| `ADO_PROJECT` | ✅ Yes | Default project name |

**Field mapping reference:**

| WorkItem field | ADO REST field |
|----------------|----------------|
| `id` | `work_item["id"]` |
| `title` | `fields["System.Title"]` |
| `description` | `fields["System.Description"]` |
| `state` | `fields["System.State"]` |
| `type` | `fields["System.WorkItemType"]` |
| `tags` | `fields["System.Tags"]` (split on `;`) |
| `url` | `_links["html"]["href"]` |
| `raw` | entire ADO work item dict |

---

### 4. `provider_factory` — Runtime Provider Selection

**File:** `cortex/repositories/provider_factory.py`

Reads `WORK_ITEM_SOURCE` (defaults to `"ado"`) and instantiates the correct provider. Companies add a new `elif` branch to support additional systems.

```python
source = os.getenv("WORK_ITEM_SOURCE", "ado").strip().lower()

if source == "ado":
    return ADOWorkItemProvider(
        org_url=os.getenv("ADO_ORG_URL", ""),
        pat=os.getenv("ADO_PAT", ""),
        project=os.getenv("ADO_PROJECT", ""),
    )
# elif source == "jira":  ← add here
```

---

### 5. `cortex_fetch_work_items` — MCP Tool

**File:** `cortex/mcp/tools/work_item_tool.py`

The 24th canonical MCP tool. Exposed as a standard JSON-RPC tool over stdio.

**Tool schema:**

```json
{
  "name": "cortex_fetch_work_items",
  "description": "Fetch work items from the configured ticketing system (ADO, Jira, custom). Provider selected via WORK_ITEM_SOURCE env var.",
  "inputSchema": {
    "type": "object",
    "required": ["project"],
    "properties": {
      "project": { "type": "string", "description": "Project name or ID" },
      "item_id": { "type": "string", "description": "Optional: fetch single item by ID" },
      "filters": { "type": "object", "description": "Optional provider-specific filters" }
    }
  }
}
```

**Response shape:**

```json
{
  "status": "success",
  "project": "MyProject",
  "count": 12,
  "items": [
    {
      "id": "42",
      "title": "As a user, I can log in with SSO",
      "description": "Acceptance criteria...",
      "state": "Active",
      "type": "User Story",
      "tags": ["auth", "sprint-42"],
      "url": "https://dev.azure.com/org/project/_workitems/edit/42",
      "raw": { "fields": { "Custom.BusinessValue": "High" } }
    }
  ]
}
```

**Governance:** All calls are guarded by `validate_orchestrator_context` (CORE-050 — MCP-first). Requests must route through MasterOrchestrator; direct invocations are rejected.

---

## How to Use

### From Copilot Chat (VS Code)

```
"Fetch all active user stories from the Authentication project"
```

CORTEX routes through `cortex_process_request` → `cortex_fetch_work_items`:

```python
cortex_fetch_work_items(
    project="Authentication",
    filters={"state": "Active"},
    orchestrator_context={"source": "MasterOrchestrator"}
)
```

### Fetch a Single Work Item

```python
cortex_fetch_work_items(
    project="Authentication",
    item_id="42",
    orchestrator_context={"source": "MasterOrchestrator"}
)
```

### Filter by Sprint

```python
cortex_fetch_work_items(
    project="MyProject",
    filters={"sprint": "Sprint 42"},
    orchestrator_context={"source": "MasterOrchestrator"}
)
```

---

## How to Implement Your ADO Calls

Open `cortex/repositories/ado/ado_provider.py` and fill in the two stub methods:

### `fetch_user_stories`

```python
def fetch_user_stories(self, project: str, **kwargs: Any) -> List[WorkItem]:
    effective_project = project or self._default_project
    wiql = f"""
        SELECT [System.Id] FROM WorkItems
        WHERE [System.TeamProject] = '{effective_project}'
        AND [System.WorkItemType] = 'User Story'
        AND [System.State] != 'Removed'
    """
    # POST /{org}/{project}/_apis/wit/wiql?api-version=7.1
    response = requests.post(
        f"{self._org_url}/{effective_project}/_apis/wit/wiql",
        json={"query": wiql},
        headers=self._auth_headers(),
        params={"api-version": "7.1"},
        timeout=30,
    )
    response.raise_for_status()
    ids = [item["id"] for item in response.json()["workItems"]]

    # GET /_apis/wit/workitems?ids=1,2,3&$expand=all
    detail_response = requests.get(
        f"{self._org_url}/_apis/wit/workitems",
        params={"ids": ",".join(str(i) for i in ids), "$expand": "all", "api-version": "7.1"},
        headers=self._auth_headers(),
        timeout=30,
    )
    detail_response.raise_for_status()
    return [self._map(item) for item in detail_response.json()["value"]]
```

### `fetch_by_id`

```python
def fetch_by_id(self, item_id: str) -> WorkItem:
    response = requests.get(
        f"{self._org_url}/_apis/wit/workitems/{item_id}",
        params={"$expand": "all", "api-version": "7.1"},
        headers=self._auth_headers(),
        timeout=30,
    )
    response.raise_for_status()
    return self._map(response.json())
```

---

## How to Add a New Provider (e.g. Jira)

**Step 1** — Create `cortex/repositories/jira/jira_provider.py` implementing `WorkItemProvider`:

```python
class JiraWorkItemProvider:
    def fetch_user_stories(self, project: str, **kwargs) -> List[WorkItem]: ...
    def fetch_by_id(self, item_id: str) -> WorkItem: ...
    def health_check(self) -> bool: ...
```

**Step 2** — Add to `provider_factory.py`:

```python
elif source == "jira":
    from cortex.repositories.jira.jira_provider import JiraWorkItemProvider
    return JiraWorkItemProvider(
        base_url=os.getenv("JIRA_BASE_URL", ""),
        token=os.getenv("JIRA_API_TOKEN", ""),
        project_key=os.getenv("JIRA_PROJECT_KEY", ""),
    )
```

**Step 3** — Set `WORK_ITEM_SOURCE=jira` in your deployment config. No other CORTEX files change.

---

## Testing

Golden tests in `tests/golden/test_work_item_provider_truth.py` validate:

| Test | What It Checks |
|------|---------------|
| `test_work_item_provider_module_importable` | Protocol importable |
| `test_work_item_dataclass_required_fields` | All 8 `WorkItem` fields present |
| `test_work_item_raw_field_is_dict_typed` | `raw` field is `Dict[str, Any]` |
| `test_work_item_instantiation` | `WorkItem` can be constructed |
| `test_ado_provider_importable` | `ADOWorkItemProvider` importable |
| `test_ado_provider_has_fetch_user_stories` | Method exists and is callable |
| `test_ado_provider_has_fetch_by_id` | Method exists and is callable |
| `test_ado_provider_has_health_check` | Method exists and is callable |
| `test_ado_provider_satisfies_protocol` | `isinstance(ado, WorkItemProvider)` |

Run with: `make test-batch` (or the CORTEX: Smoke Tests VS Code task).

---

## Governance

| Rule | Application |
|------|-------------|
| CORE-011 | Type hints on all provider methods |
| CORE-012 | Docstrings on all public APIs |
| CORE-028 | snake_case file naming (`ado_provider.py`, `work_item_tool.py`) |
| CORE-035 | Single canonical `WorkItemProvider` Protocol — no duplicates |
| CORE-050 | MCP-first: `cortex_fetch_work_items` is the only external surface |

---

## Practical Examples

**Business Leader:** "CORTEX pulls sprint work items directly from ADO into every developer's context. Teams stop switching tabs — backlog items flow into their workflow automatically."

**Product Owner:** "Call `cortex_fetch_work_items(project='MyProject', filters={'sprint': 'Sprint 42'})` to get all active stories. State, tags, URL, and custom fields are all in the response. Filter by state or sprint without changing any configuration."

**Developer:** "I set `ADO_ORG_URL`, `ADO_PAT`, and `ADO_PROJECT` once in my env. I fill in the two stub methods in `ado_provider.py` with standard ADO REST calls. From that point, `cortex_fetch_work_items` just works — I never touch the MCP layer or the factory."

---

*Verified against `cortex/repositories/` + `cortex/mcp/tools/work_item_tool.py` · Phase 15 · 21 February 2026*
