# FAQ — MCP Tools & Integration

---
title: FAQ — MCP Tools & Integration
type: reference
audience: [Software Developers, Product Owners]
last_verified: 2026-02-25
source_of_truth: cortex/mcp/tools/ + cortex/repositories/
order: 5
---

> **Purpose:** Answers to questions about the 28 registered MCP tools (39 target), how the MCP server works, and how to integrate with external systems like Azure DevOps. All answers verified against live code.

---

## How many MCP tools does CORTEX expose?

**28 registered canonical MCP tools (39 target):**

| Category | Active Tools | Deprecated |
|----------|-------------|-----------|
| Core | 3 | `cortex_process_request` (use `cortex_request_lifecycle`) |
| Governance | 3 | `cortex_validate_request` (use `cortex_validate`) |
| Intelligence | 4 | — |
| Operations | 6 | — |
| Utilities | 9 | — |
| Workflow | 1 | — |
| Work Items | 1 | — |
| Sweep Completeness | 1 | — |

All 28 registered tools (39 target) are registered via the `ConsolidatedTool` base class (`cortex/mcp/mcp_tool_base.py`) and exposed through JSON-RPC 2.0 stdio transport.

---

## What is the correct entry point MCP tool?

For **full lifecycle tracking**, use `cortex_request_lifecycle`.

For **intent classification only**, use `cortex_classify`.

> ⚠️ `cortex_process_request` is **deprecated** (WAVE-100). Do not use it in new integrations. It will be removed in a future release.

---

## What transport does CORTEX MCP use?

**Pylance-style stdio** in development — identical to how Pylance auto-starts when VS Code opens a Python workspace. The MCP server process is started automatically by VS Code reading `.vscode/settings.json`.

**HTTP transport** is available for production deployments via `deployment/mcp-gateway-config.yaml`.

Configuration in `.vscode/settings.json`:
```json
{
  "github.copilot.chat.mcpServers": {
    "cortex": {
      "command": "python3",
      "args": ["-m", "cortex.mcp"],
      "transport": "stdio",
      "cwd": "${workspaceFolder}"
    }
  }
}
```

---

## What does `cortex_validate` check?

`cortex_validate` runs real CORE rule checks against provided code or file paths:

- CORE-011 (type hints present on all functions)
- CORE-012 (docstrings on public APIs)
- CORE-028 (snake_case file naming)
- CORE-035 (no duplicate implementations)
- CORE-008 (test exists before implementation)
- Architecture integrity (imports from canonical `cortex.*` only)

Results are returned as a structured object with `rule_id`, `severity`, `file`, `line`, and `suggestion` for each violation.

---

## How do I list all available MCP tools?

Call `cortex_tools_catalog` from Copilot Chat:
```
Call cortex_tools_catalog
```

This returns all 28 registered tools (39 target) with their descriptions, categories, and parameter schemas. It reads directly from the live tool registry — always current.

---

## What is `cortex_onboard` and what does it return?

`cortex_onboard` runs the full repository onboarding pipeline:

1. LENS 15-component scan
2. Security assessment (P0/P1/P2 severity classification)
3. Domain classification
4. Tech stack fingerprint
5. Architecture pattern detection

**Returns:** A structured assessment with:
- Security findings (severity + file + line + remediation suggestion)
- Complexity hotspots (top 10 by cyclomatic complexity)
- Tech stack detected (frameworks, languages, versions)
- Architecture patterns matched (from the 9-pattern registry)
- Recommended next steps (governance gaps, refactor candidates)

**Storage:** Results saved to `.cortex-runtime/` for subsequent `cortex_classify` and `cortex_validate` calls.

---

## What is `cortex_refactor` and how does it handle symbol renaming?

`cortex_refactor` performs **semantic refactoring** across Python, C#, and TypeScript/JavaScript:

| Operation | Description |
|-----------|-------------|
| `extract` | Extract method/class from selected code |
| `rename` | Rename symbol by name (no byte offset required) |
| `organize` | Organize imports, sort methods |
| `move` | Move class/function to a different module |

**Key capability:** C# symbol rename uses **Roslyn by-name rename** — you provide the symbol name, not a byte offset or line number. CORTEX finds all usages across the solution and renames consistently.

**Usage:**
```
Call cortex_refactor with {"operation": "rename", "language": "csharp", "symbol_name": "OldClassName", "new_name": "NewClassName"}
```

---

## How does CORTEX handle CORE-064 sweep tracking?

CORE-064 sweep tracking is handled by `SweepCatalogueOrchestrator` (not an MCP tool — invoked internally by the enforcement pipeline):

- **Query open sweeps:** call `orchestrator.list_open_sweeps()` — returns all sweeps with open items
- **Check a specific sweep:** call `orchestrator.get_open_issues(sweep_id)` — returns item-level progress
- **Assert exhaustion:** call `orchestrator.assert_exhausted(sweep_id)` — fails if any items remain open
- **Mark item resolved:** call `orchestrator.close_item(sweep_id, item_id)`

Storage: `.cortex-runtime/sweeps/{sweep_id}.db` (SQLite WAL, one file per sweep).

> Note: `cortex_sweep_status` is referenced in older documentation but is not currently registered in `mcp_registry.py`. It is planned toward the 39-tool target.

---

## How does `cortex_fetch_work_items` work?

`cortex_fetch_work_items` provides **provider-agnostic work item access** — the same MCP tool surface regardless of whether you use Azure DevOps, Jira, or a custom system.

**Required parameters:**
- `project` *(string)* — project name in your ticketing system

**Optional parameters:**
- `item_id` *(string)* — fetch a single item by ID
- `filters` *(object)* — provider-specific filters (e.g. `{"sprint": "Sprint 42", "state": "Active"}`)

**Environment variables (ADO provider):**
| Variable | Required | Description |
|----------|----------|-------------|
| `WORK_ITEM_SOURCE` | No (default: `"ado"`) | Provider selector |
| `ADO_ORG_URL` | Yes | `https://dev.azure.com/your-org` |
| `ADO_PAT` | Yes* | Personal Access Token (* empty for managed identity) |
| `ADO_PROJECT` | Yes | Default project name |

**Returns:** List of `WorkItem` dicts with `id`, `title`, `description`, `state`, `type`, `tags`, `url`, `raw` (full API response).

---

## How do I add a new work item provider (e.g. Jira)?

Implement the `WorkItemProvider` Protocol (`cortex/repositories/work_item_provider.py`):

```python
from cortex.repositories.work_item_provider import WorkItemProvider, WorkItem
from typing import Protocol, List, Optional, Dict, Any

class JiraWorkItemProvider:
    def fetch_user_stories(self, project: str, filters: Optional[Dict] = None) -> List[WorkItem]:
        ...
    
    def fetch_by_id(self, item_id: str) -> WorkItem:
        ...
    
    def health_check(self) -> bool:
        ...
```

Then register it in `cortex/repositories/provider_factory.py` under a new `WORK_ITEM_SOURCE` key (e.g. `"jira"`). Set `WORK_ITEM_SOURCE=jira` in your deployment config.

The `cortex_fetch_work_items` MCP tool surface is identical — no changes required upstream.

---

## What is `cortex_vacuum` and when should I use it?

`cortex_vacuum` is the **markdown sprawl cleanup tool** — it removes stale, orphaned, and duplicate markdown files from the workspace.

**Triggers:**
- `/vacuum` command in Copilot Chat
- Stage 5 of `/audit fix` (automatic)
- Weekly cleanup (scheduled)

**What it removes:**
- Orphaned `*-report.md`, `*-status.md`, `*-summary.md` files not in any index
- Duplicate documentation (same content, different paths)
- Stale session notes and execution logs

**What it preserves:**
- `cortex-docs/.content/` — canonical documentation
- `cortex-registry/` — governance YAML files
- Files explicitly referenced in `mkdocs.yml` or navigation indexes

---

## Can I call CORTEX MCP tools from outside VS Code?

Yes — any MCP-compatible client works. The transport is standard JSON-RPC 2.0 over stdio. You can also:

1. **HTTP transport:** Configure `deployment/mcp-gateway-config.yaml` for HTTP access from CI/CD pipelines
2. **Direct Python:** Import and call orchestrators directly (bypasses MCP, no governance gates):
   ```python
   from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator
   orch = TDDOrchestrator()
   result = await orch.execute({"request": "implement auth middleware"})
   ```
3. **Automated testing:** Tests call orchestrators directly — this is the canonical pattern in `tests/`

---

## Why does the MCP server sometimes fail to start?

Common causes and fixes:

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ModuleNotFoundError: No module named 'cortex'` | `pip install -r requirements.txt` not run | Run `pip install -r requirements.txt` |
| `Python 3.x < 3.9 is not supported` | Wrong Python version | Use Python 3.9+ |
| Server starts but tools return errors | Missing env variables | Check `ADO_ORG_URL`, `ADO_PAT` if using work items |
| MCP not detected by VS Code | `.vscode/settings.json` missing | Run `python3 scripts/setup-mcp.py` |

To skip the automatic preflight check (useful in CI): set `CORTEX_SKIP_PREFLIGHT=true`.

---

## What is `cortex_plan` and what are the 4 execution modes?

`cortex_plan` generates a **structured remediation plan** from audit results:

| Mode | Description |
|------|-------------|
| **1 — Autonomous** | CORTEX executes the plan automatically without stopping |
| **2 — Interactive** | CORTEX pauses at each step for your approval |
| **3 — Review** | Plan is shown for review — no execution |
| **4 — Cancel** | Plan is discarded |

Autonomous mode follows CORE-064 (Sweep Completeness) — it creates a SweepCatalogue entry and tracks every item through to completion.

---

*Verified against `cortex/mcp/tools/` (source: mcp_registry.py, 28 registered canonical tools) · 25 February 2026 · Phase 83 Complete*
