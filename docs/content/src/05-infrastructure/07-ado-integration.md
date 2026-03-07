# ADO Integration

---
title: Azure DevOps Integration — Work Item Provider
type: how-to
audience: [Software Developers, Product Owners]
last_verified: 2026-02-21
source_of_truth: cortex/repositories/ado/ado_provider.py + cortex/intelligence/knowledge/ado_context_mapper.py
order: 7
---

> **Brain analogy:** ADO Integration is CORTEX's **short-term memory refresh** — it pulls the current sprint's active work items into intelligence context, ensuring orchestrators respond to what the team is working on *right now*, not just what the codebase has historically looked like.

---

## Overview

CORTEX integrates with **Azure DevOps (ADO)** through a provider-agnostic `WorkItemProvider` Protocol. The `ADOWorkItemProvider` fetches user stories, bugs, and tasks from ADO and the `ADOContextMapper` normalises them into structured sprint context consumed by `UnifiedIntelligenceProvider.full()`.

This integration was introduced in **Phase 20** (ADO + Brain-Tier Synthesis).

---

## Architecture

```
Environment Variables
  ADO_ORG_URL + ADO_PAT + ADO_PROJECT
          ↓
ADOWorkItemProvider          ← cortex/repositories/ado/ado_provider.py
  └── fetch_stories(project, sprint) → List[WorkItem]
          ↓
ADOContextMapper             ← cortex/intelligence/knowledge/ado_context_mapper.py
  └── ADOContextMapper.map(stories) → {
          "sprint_name": "Sprint 42",
          "stories": [...],
          "open_count": 7,
          "in_progress_count": 3
      }
          ↓
UnifiedIntelligenceProvider.full()
  └── context.sprint_context → dict
```

---

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `WORK_ITEM_SOURCE` | No (default: `"ado"`) | Provider selector (`"ado"` or custom) |
| `ADO_ORG_URL` | **Yes** | Azure DevOps organisation URL — e.g. `https://dev.azure.com/your-org` |
| `ADO_PAT` | **Yes** | Personal Access Token (or empty string for managed identity) |
| `ADO_PROJECT` | **Yes** | Default project name — e.g. `"MyProject"` |

### Setting Up Environment Variables

```bash
export ADO_ORG_URL="https://dev.azure.com/your-org"
export ADO_PAT="your-personal-access-token"
export ADO_PROJECT="MyProject"
```

For CI/CD pipelines, inject these as pipeline variables or GitHub Actions secrets.

---

## WorkItemProvider Protocol

Any ticketing system can be plugged in by implementing the `WorkItemProvider` Protocol:

```python
from typing import Protocol, List
from cortex.models.work_item import WorkItem

class WorkItemProvider(Protocol):
    """Provider-agnostic work item access protocol."""

    async def fetch_stories(
        self,
        project: str,
        sprint: str | None = None,
        filters: dict | None = None,
    ) -> List[WorkItem]:
        """Fetch work items from the ticketing system."""
        ...

    async def fetch_item(self, project: str, item_id: str) -> WorkItem:
        """Fetch a single work item by ID."""
        ...
```

### WorkItem Schema

```python
@dataclass
class WorkItem:
    id: str                     # Provider-specific ID (e.g. "12345")
    title: str                  # Work item title
    description: str            # Full description text
    state: str                  # "New", "Active", "Resolved", "Closed"
    type: str                   # "User Story", "Bug", "Task", "Feature"
    tags: List[str]             # Tags/labels
    url: str                    # Deep link to work item in source system
    raw: dict                   # Provider-specific raw response
```

---

## ADOContextMapper

`ADOContextMapper` converts a raw list of `WorkItem` objects into the structured sprint context dict consumed by `UnifiedIntelligenceProvider`:

```python
from cortex.intelligence.knowledge.ado_context_mapper import ADOContextMapper
from cortex.models.work_item import WorkItem

stories: List[WorkItem] = await ado_provider.fetch_stories("MyProject")

context = ADOContextMapper.map(stories)
# Returns:
# {
#     "sprint_name": "Sprint 42",        ← from System.IterationPath last segment
#     "stories": [
#         {"id": "101", "title": "...", "state": "Active", "area_path": "..."},
#         ...
#     ],
#     "open_count": 4,                   ← state in ("New", "Active")
#     "in_progress_count": 2             ← state == "Active"
# }
```

`ADOContextMapper.map()` is a **classmethod** — no instantiation needed.

---

## MCP Surface — `cortex_fetch_work_items`

The `cortex_fetch_work_items` MCP tool provides direct access to work items from Copilot Chat:

```
Tool: cortex_fetch_work_items
File: cortex/mcp/tools/work_item_tool.py

Parameters:
  project    (string, required)  — Project name in the source system
  item_id    (string, optional)  — When set, fetches a single item
  filters    (object, optional)  — Provider-specific filters:
               { "sprint": "Sprint 42", "state": "Active" }
```

**Example — fetch all active stories in Sprint 42:**
```
@cortex cortex_fetch_work_items project="MyProject" filters={"sprint": "Sprint 42", "state": "Active"}
```

**Example — fetch single work item:**
```
@cortex cortex_fetch_work_items project="MyProject" item_id="12345"
```

---

## Using a Custom Provider

To replace ADO with Jira or a custom system:

1. Set `WORK_ITEM_SOURCE=jira` (or any custom string)
2. Implement `WorkItemProvider` Protocol
3. Register the provider in `cortex/repositories/work_item_registry.py`

The `ADOContextMapper` is provider-agnostic — it works with any `List[WorkItem]` regardless of source.

---

## Practical Examples

**Developer:** "I run `cortex_fetch_work_items` at sprint start to pull all active stories into my context. CORTEX's `full()` analysis then cross-references them with LENS findings — so if a story touches the auth module, I get PCI-DSS rules surfaced automatically."

**Product Owner:** "ADO integration means my sprint board and CORTEX are in sync. When I ask CORTEX to plan the next sprint, it already knows what's in flight."

---

## Related Documents

- [Company Domain Synthesis](../02-lens/05-company-domain-synthesis.md) — How domain profiles combine with sprint context
- [MCP Tools Catalog](../04-mcp/03-tools-catalog.md) — `cortex_fetch_work_items` full reference
- [Context Synthesis](../02-lens/04-synthesis.md) — `UnifiedIntelligenceProvider` tier model

---

*Verified against `cortex/repositories/ado/ado_provider.py` + `cortex/intelligence/knowledge/ado_context_mapper.py` · Phase 20 complete · 21 February 2026*
