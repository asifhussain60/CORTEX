# MCP Tools Catalog

---
title: MCP Tools Catalog — 24 Canonical Tools
type: reference
audience: [Software Developers, Product Owners, Business Leaders]
last_verified: 2026-02-21
source_of_truth: cortex/mcp/tools/ (return "cortex_*" in name properties)
order: 3
---

> **Brain analogy:** Each MCP tool is a **specialized reflex** — call a specific nerve, get a specific action. `cortex_process_request` is the voluntary motor cortex (conscious commands), while `cortex_health_check` is an autonomic heartbeat monitor. Every reflex routes through the spinal cord (MCP transport).

---

## Overview

24 canonical MCP tools organized across 7 categories. All tools are registered via `ConsolidatedTool` base class and exposed through JSON-RPC 2.0 stdio transport.

**Entry point rule:** All user requests MUST route through `cortex_process_request`. Other tools are internal or auxiliary.

---

## Tool Categories

### Core (4 tools) — `cortex/mcp/tools/core.py`

The primary entry points for all CORTEX operations.

| Tool | Description |
|------|-------------|
| `cortex_process_request` | **MANDATORY entry point.** Routes ALL requests through MasterOrchestrator 4-stage pipeline (Interaction → Intent → Intelligence → Execution). |
| `cortex_challenge` | AI-driven challenge generation using LENS analysis. Validates whether a request is well-scoped before execution. |
| `cortex_classify` | Intent classification via LENS. Returns intent type + confidence for routing decisions. |
| `cortex_request_lifecycle` | Full request lifecycle management — tracks a request from submission to completion with audit trail. |

### Governance (4 tools) — `cortex/mcp/tools/governance.py`

Enforcement, validation, and rule loading.

| Tool | Description |
|------|-------------|
| `cortex_governance` | Execute governance actions — enforcement, blocking, remediation with audit logging. |
| `cortex_validate` | Validate code against CORE governance rules with real rule checking. |
| `cortex_load` | Load governance rules (CORE rules, HEXA-MODE definitions, audit checklists, response format) from YAML registry. |
| `cortex_validate_request` | Validate a request against governance constraints before execution. |

### Intelligence (4 tools) — `cortex/mcp/tools/intelligence.py` + `intelligence_generation.py`

LENS analysis, knowledge access, and git operations.

| Tool | Description |
|------|-------------|
| `cortex_lens` | Run LENS analysis (8 parallel analyzers: AST, Git History, Comment, Import, Security, Pattern, Metrics, Domain). |
| `cortex_knowledge` | Query the CORTEX knowledge base for domain-specific information. |
| `cortex_git` | Git-aware operations — history analysis, commit patterns, branch management. |
| `cortex_generate_tests` | Generate test scaffolds from code analysis with TestQualityGate scoring. |

### Operations (5 tools) — `cortex/mcp/tools/operations.py` + `master_plan_tool.py`

Debug, refactor, plan, onboard, and dashboard operations.

| Tool | Description |
|------|-------------|
| `cortex_debug` | Comprehensive debugging — capture logs, analyze issues, generate fix plans. |
| `cortex_refactor` | Execute semantic refactoring operations (extract, rename, organize) across Python, C#, TypeScript/JavaScript. |
| `cortex_plan` | Generate structured remediation plans from audit results. 4 execution options: Autonomous, Interactive, Review, Cancel. |
| `cortex_onboard` | Onboard repository with holistic LENS analysis + security assessment (P0/P1/P2). |
| `cortex_dashboard` | Generate dashboard suite — landing page + per-repo dashboards with embedded data. |
| `cortex_master_plan` | CortexMasterPlanOrchestrator exposure — strategic planning with phase tracking. |

### Utilities (8 tools) — `cortex/mcp/tools/utilities.py`

Verification, discovery, metrics, and education tools.

| Tool | Description |
|------|-------------|
| `cortex_verify` | Verify CORTEX development environment — Python version, dependencies, MCP connectivity. |
| `cortex_ask` | Ask educational questions about CORTEX architecture with truth-based verification. |
| `cortex_vacuum` | Clean up markdown sprawl with automated archival and verification. |
| `cortex_tools_catalog` | Discover all MCP tools registered in CORTEX. |
| `cortex_total_recall` | Discover and recall CORTEX features and components. |
| `cortex_metrics` | Record and export development metrics — TDD cycles, debug sessions, code generation. |
| `cortex_check` | Quick health check for dependency drift between requirements.txt and installed packages. |
| `cortex_vision` | Analyze images via Vision API for UI elements, URLs, issues, and structural mappings. |
| `cortex_orchestrator` | Direct orchestrator invocation for advanced use cases. |

### Workflow (1 tool) — `cortex/mcp/tools/workflow_tools.py`

| Tool | Description |
|------|-------------|
| `cortex_workflow` | Execute workflow templates — lifecycle and production workflows from `cortex-registry/workflows/`. |

### Work Item Integration (1 tool) — `cortex/mcp/tools/work_item_tool.py`

Provider-agnostic work item access for all ticketing systems (Azure DevOps, Jira, custom).

| Tool | Description |
|------|-------------|
| `cortex_fetch_work_items` | Fetch work items (user stories, bugs, tasks) from the configured ticketing system. Provider is selected via `WORK_ITEM_SOURCE` env var (default: `"ado"`). Returns a list of `WorkItem` dicts with `id`, `title`, `description`, `state`, `type`, `tags`, `url`, and `raw` fields. Supports single-item fetch by `item_id` and provider-specific `filters` (e.g. sprint, state). |

**Required parameters:**
- `project` *(string, required)* — Project name or identifier in the source system.
- `item_id` *(string, optional)* — When supplied, fetches a single work item by ID.
- `filters` *(object, optional)* — Provider-specific filter dict (e.g. `{"sprint": "Sprint 42", "state": "Active"}`).

**Environment variables (ADO provider):**

| Variable | Required | Description |
|----------|----------|-------------|
| `WORK_ITEM_SOURCE` | No (default: `"ado"`) | Provider selector |
| `ADO_ORG_URL` | Yes | Azure DevOps org URL (e.g. `https://dev.azure.com/your-org`) |
| `ADO_PAT` | Yes* | Personal Access Token (* empty for managed identity) |
| `ADO_PROJECT` | Yes | Default project name |

> **Architecture note:** `cortex_fetch_work_items` is **provider-agnostic**. The `ADOWorkItemProvider` (`cortex/repositories/ado/ado_provider.py`) implements the `WorkItemProvider` Protocol — companies replace the stub bodies with their ADO REST client calls. See `04-mcp/06-work-item-integration.md` for the full integration guide.

---

## Specialized Tool Modules (Phase 12 consolidation targets)

In addition to the 24 canonical tools above, several specialized modules provide focused capabilities:

### Health Tools — `cortex/mcp/tools/health_check_tool.py` + `health_scan_tool.py`

| Function | Description |
|----------|-------------|
| `cortex_health_check` | System health validation with component status reporting. |
| `cortex_health_scan` | Deep health scan across all CORTEX subsystems. |

### Brain Collaboration — `cortex/mcp/tools/brain_collaboration_tools.py`

| Function | Description |
|----------|-------------|
| `cortex_intelligence_sync` | Synchronize intelligence across brain tiers. |
| `cortex_intelligence_merge` | Merge intelligence insights from multiple sources. |
| `cortex_intelligence_share` | Share intelligence between orchestrators. |

### Coherence — `cortex/mcp/tools/coherence_tools.py`

| Function | Description |
|----------|-------------|
| `cortex_validate_coherence` | Validate architectural coherence across components. |

### Specialized Modules

| Module | File | Purpose |
|--------|------|---------|
| Task Complexity | `analyze_task_complexity.py` | Analyze task complexity before execution |
| STS Analyzer | `sts_analyzer.py` | Semantic Text Similarity analysis |
| Test Quality | `test_quality_tool.py` | TestQualityGate scoring (0–9) |
| Vacuum Execute | `vacuum_execute_tool.py` | Execute vacuum operations on stale artifacts |
| Workflow Runtime | `workflow_runtime_tool.py` | Runtime workflow execution engine |
| Onboard Infrastructure | `onboard_infrastructure.py` | Infrastructure-specific onboarding |
| Debug Tools | `debug_tools.py` | Debug session management (capture, analyze, fix) |

### Deployment Suite — `cortex/mcp/tools/deployment/`

| Tool | File | Purpose |
|------|------|---------|
| Canary Deployer | `canary_deployer.py` | Canary deployment management |
| Health Checker | `health_checker.py` | Deployment health validation |
| Release Builder | `release_builder.py` | Release artifact building |
| Rollback | `rollback.py` | Deployment rollback operations |
| Sanitizer | `sanitizer.py` | Pre-deployment sanitization |

### Multi-Repo Suite — `cortex/mcp/tools/multi_repo/`

| Tool | File | Purpose |
|------|------|---------|
| Context Switcher | `context_switcher.py` | Switch between repository contexts |
| Cross-Repo Search | `cross_repo_search.py` | Search across multiple repositories |
| Dependency Graph | `dependency_graph.py` | Cross-repo dependency visualization |
| Profile Manager | `profile_manager.py` | Repository profile management |
| Project Scanner | `project_scanner.py` | Multi-project scanning |
| Shared Audit | `shared_audit.py` | Cross-repo audit trail |

### Toolkit Suite — `cortex/mcp/tools/toolkit/`

| Tool | File | Purpose |
|------|------|---------|
| Analyze | `analyze.py` | Deep analysis operations |
| Cleanup | `cleanup.py` | Workspace cleanup |
| Diagnose | `diagnose.py` | Diagnostic operations |
| Validate | `validate.py` | Validation operations |
| Verify | `verify.py` | Environment verification |

---

## Tool Architecture

```
ConsolidatedTool (base class)
├── name → "cortex_*"           # Canonical name
├── description → str           # Tool description
├── category → ToolCategory     # CORE, GOVERNANCE, INTELLIGENCE, etc.
├── parameters → List[ToolParameter]
└── execute(args) → ToolResult  # Execution logic
```

All tools inherit from `ConsolidatedTool` (defined in `cortex/mcp/mcp_tool_base.py`), ensuring consistent:
- Parameter validation
- Error handling
- Audit trail recording
- Governance gate enforcement

---

## Practical Examples

**Business Leader:** "24 canonical tools, one entry point (`cortex_process_request`). Developers can't bypass governance — the architecture enforces it."

**Product Owner:** "When planning a sprint, `cortex_plan` generates remediation plans from audit results with 4 execution modes. `cortex_onboard` gives a complete repository assessment in one call."

**Developer:** "I call `cortex_process_request` with `operation: 'implement'` and my request. It routes through MasterOrchestrator, runs LENS analysis, classifies intent, enforces TDD, and returns structured output. I can also use `cortex_verify` to check my environment and `cortex_tools_catalog` to discover available tools. For sprint work, I call `cortex_fetch_work_items` with my ADO project name to pull user stories directly into my development context."

---

*Verified against `cortex/mcp/tools/` — 38 Python files, 24 canonical tool names · 21 February 2026*
