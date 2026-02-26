---
title: MCP Gateway
consolidates:
  - 04-mcp-overview.md
  - 04-mcp-protocol.md
  - 04-mcp-tools-catalog.md
  - 04-mcp-integration.md
  - 04-mcp-versioning.md
  - 04-mcp-work-item-integration.md
last_verified: 2026-02-26
source_of_truth: cortex/mcp/ + .vscode/settings.json
audience: [Business Leaders, Product Owners, Software Developers]
---

# MCP Gateway

The Model Context Protocol is a JSON-RPC 2.0 communication standard connecting IDEs to CORTEX. CORTEX implements MCP as a Pylance-style stdio server that auto-starts when VS Code opens the workspace — no manual server startup, no Docker containers, no exposed ports.

- **Transport**: stdio (standard input and output)
- **Protocol**: JSON-RPC 2.0
- **Tools**: Thirty-nine active MCP tools across thirteen categories
- **Clients**: VS Code (Copilot Chat), Cursor, Claude Desktop

---

## Protocol — JSON-RPC 2.0

Every MCP message follows JSON-RPC 2.0. The IDE writes requests to stdin and reads responses from stdout. Stderr carries logging and diagnostics only, never protocol data.

| Message Type | Direction | Purpose |
|-------------|-----------|---------|
| tools/list | IDE to CORTEX | Discover available tools |
| tools/call | IDE to CORTEX | Execute a specific tool |
| notifications | CORTEX to IDE | Progress updates and status |
| errors | CORTEX to IDE | Error codes with structured remediation |

### Error Codes

| Code | Meaning |
|------|---------|
| −32600 | Invalid request — fix JSON format |
| −32601 | Method not found — check tool name |
| −32602 | Invalid params — check tool arguments |
| −32603 | Internal error — check CORTEX logs |
| −32700 | Parse error — fix JSON syntax |

### Why stdio?

| Factor | stdio | HTTP |
|--------|-------|------|
| Startup | Instant — IDE spawns process | Requires manual server start |
| Latency | Sub-millisecond (in-process) | Network overhead |
| Security | No exposed ports | Port binding required |
| Lifecycle | IDE manages process lifecycle | Separate process management |
| Configuration | `.vscode/settings.json` | Environment variables |

---

## Configuration and Integration

### VS Code (Primary)

The MCP server auto-starts via `.vscode/settings.json`:

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

Verification: call `cortex_sample_tool` in Copilot Chat. If it responds, MCP is active.

### Cursor

`.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "cortex": {
      "command": "python3",
      "args": ["-m", "cortex.mcp"],
      "transport": "stdio",
      "cwd": "/path/to/CORTEX"
    }
  }
}
```

### Claude Desktop

`claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "cortex": {
      "command": "python3",
      "args": ["-m", "cortex.mcp"],
      "transport": "stdio",
      "cwd": "/path/to/CORTEX"
    }
  }
}
```

### Custom JSON-RPC Client

Any application that speaks JSON-RPC 2.0 over stdio can connect by spawning `python3 -m cortex.mcp` as a subprocess and communicating via stdin and stdout.

### Environment Requirements

| Requirement | Version |
|-------------|---------|
| Python | 3.9 or higher |
| VS Code | 1.85 or higher (for MCP support) |
| Copilot | Latest (with MCP tool calling) |
| Dependencies | `requirements.txt` (pip install -r) |

---

## Thirty-Nine MCP Tools — Catalog

All tools are registered via the ConsolidatedTool base class and exposed through JSON-RPC 2.0 stdio transport. Entry point rule: use `cortex_request_lifecycle` for full lifecycle tracking or `cortex_classify` for intent routing.

### Core and Routing

| Tool | Description |
|------|-------------|
| cortex_classify | Intent classification — routes requests to correct orchestrator |
| cortex_orchestrator | Direct orchestrator invocation — routes to any of fifty-one wired orchestrators |
| cortex_request_lifecycle | Full request lifecycle — classify, plan, execute, validate |
| cortex_ask | Educational questions about CORTEX with truth-based verification |
| cortex_total_recall | Discover and recall CORTEX features, components, architecture |
| cortex_tools_catalog | Discover all thirty-nine MCP tools with category and description |

### Governance and Compliance

| Tool | Description |
|------|-------------|
| cortex_governance | Execute governance actions — enforcement, blocking, remediation with audit logging |
| cortex_load | Load CORE governance rules — skull rules, core rules, audit checklist, response format |
| cortex_validate | CORE rule compliance validation |
| cortex_check | Dependency drift detection — checks requirements.txt against installed packages |

### Intelligence and LENS

| Tool | Description |
|------|-------------|
| cortex_brain_query | Domain brain query — synthesises knowledge from CORTEX cognitive model |
| cortex_challenge | Generate two or more alternatives with trade-off analysis using LENS |
| cortex_intelligence_matrix | Cross-cutting intelligence matrix — correlates LENS, governance, and metrics |
| cortex_refactor | Semantic refactoring — extract, rename, organise across Python, C#, TypeScript |
| cortex_vision | Vision API analysis — UI elements, URLs, issues, structural mappings |
| cortex_knowledge | Knowledge synthesis from governance YAML registries |
| cortex_learning | Unified Reinforcement Signal — emit, history, decay, promote, quarantine, metrics |

### Planning and Audit

| Tool | Description |
|------|-------------|
| cortex_master_plan | Master plan management — cortex-master.yaml operations, phase lifecycle |
| cortex_plan | Structured remediation and project planning with audit-driven decomposition |
| cortex_onboard | Repository onboarding — LENS analysis, security assessment, SQLite dashboard |
| cortex_query_opj | Operational Pattern Journal query — surfaces recurring patterns from execution history |

### Testing and Quality

| Tool | Description |
|------|-------------|
| cortex_generate_tests | TDD test generation — produces failing RED tests from specification |
| cortex_score_tests | Test quality gate — scores test suites against quality thresholds |

### Diagnostics and Health

| Tool | Description |
|------|-------------|
| cortex_health_scan | All twenty-two orchestrator health endpoints — production readiness validation |
| cortex_verify | Verify MCP server health, tool registry, environment, and claims |
| cortex_debug | Debug session capture — logs, error analysis, fix plan generation |
| cortex_metrics | Record and report development metrics — TDD cycles, debug sessions, invocations |

### Automation and Workflows

| Tool | Description |
|------|-------------|
| cortex_workflow | YAML workflow template execution — list, load, and run primitives |
| cortex_list_workflow_templates | List available YAML workflow templates from cortex-registry |
| cortex_scaffold_files | Write source files to disk with governance validation |

### Maintenance and Cleanup

| Tool | Description |
|------|-------------|
| cortex_vacuum | Markdown sprawl cleanup — archives stale files, removes root clutter |
| cortex_vacuum_execute | Full lifecycle vacuum — kill processes, health check, launch |

### VCS (Git)

| Tool | Description |
|------|-------------|
| cortex_git | Git operations — branching, committing, conflict resolution via GitOrchestrator |

### Documentation

| Tool | Description |
|------|-------------|
| cortex_dashboard | Generate static dashboard suite — landing page plus per-repo dashboards |

### Toolkit and Bulk Operations

| Tool | Description |
|------|-------------|
| cortex_batch_transform | Batch data transformation across a collection |
| cortex_enrich | Content enrichment — adds metadata and context to structured data |
| cortex_scan | Workspace scan — discovers files, patterns, structures |
| cortex_bulk_digest_files | Bulk file digest — batch ingestion across three pipelines |
| cortex_sweep_status | Sweep catalogue status — CORE-064 completeness tracking |

---

## Tool Naming and Authoring

All canonical MCP tools follow the pattern `cortex_{domain}_{action}`. Every tool must inherit from ConsolidatedTool, must have a unique name starting with `cortex_`, must define name, description, category, parameters, and execute, and must record audit trail entries on execution.

The `validate_orchestrator_context` guard must be called conditionally:

```python
if orchestrator_context is not None:
    validate_orchestrator_context(orchestrator_context)
```

This allows direct test invocation without a MasterOrchestrator context while enforcing routing in production.

---

## Work Item Integration — Provider Architecture

A provider-agnostic work item integration layer connects any ticketing system to CORTEX through a single MCP tool surface.

### Three-Layer Stack

**Layer 1 — MCP Tool**: `cortex_fetch_work_items` at `cortex/mcp/tools/work_item_tool.py`. Always identical regardless of ticketing system.

**Layer 2 — Provider Factory**: `cortex/repositories/provider_factory.py` reads the `WORK_ITEM_SOURCE` environment variable (defaults to "ado") and instantiates the correct provider. Companies add a new branch to support additional systems.

**Layer 3 — Provider Implementation**: `cortex/repositories/ado/ado_provider.py` implements the ADO adapter. Companies fill in REST calls for their ticketing system.

### WorkItem Dataclass — Canonical Shape

At `cortex/repositories/work_item_provider.py`, the WorkItem dataclass defines the canonical shape:

| Field | Type | Example |
|-------|------|---------|
| id | string | "42" |
| title | string | "As a user, I can log in with SSO" |
| description | string | Acceptance criteria text |
| state | string | "Active", "Resolved", "To Do" |
| type | string | "User Story", "Bug", "Task", "Epic" |
| tags | list of strings | ["auth", "sprint-42"] |
| url | string | Direct browser URL to the item |
| raw | dictionary | Full unmodified API response — escape hatch |

The raw field preserves company-specific fields (Area Path, Sprint, Custom ADO fields, Jira components) intact and accessible.

### WorkItemProvider Protocol

Companies implement this runtime-checkable Protocol once at `cortex/repositories/work_item_provider.py`: `fetch_user_stories(project, **kwargs)`, `fetch_by_id(item_id)`, and `health_check()`. No other CORTEX files need to change when a new provider is added.

### ADO Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| ADO_ORG_URL | Yes | Azure DevOps organisation URL |
| ADO_PAT | Yes | Personal Access Token (empty for managed identity) |
| ADO_PROJECT | Yes | Default project name |

### Adding a New Provider

Create a provider class implementing WorkItemProvider, add it to provider_factory.py with a new WORK_ITEM_SOURCE value, and set the environment variable. The MCP tool surface remains unchanged.

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| MCP server not found | settings.json misconfigured | Verify cwd path and command |
| Tools not appearing | Server failed to start | Run `python3 -m cortex.mcp` in terminal to check |
| Import errors | Missing dependencies | Run `pip install -r requirements.txt` |
| Slow startup | Large workspace scan | First launch scans workspace; subsequent launches are cached |
| Tool timeout | Long-running operation | LENS analysis and onboarding can take thirty to sixty seconds |

---

*All tool counts and component paths verified against live codebase — 26 February 2026*
