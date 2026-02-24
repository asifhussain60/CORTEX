# MCP Tools Catalog

---
title: MCP Tools Catalog — 26 Active Tools
type: reference
audience: [Software Developers, Product Owners, Business Leaders]
last_verified: 2026-02-23
source_of_truth: cortex/mcp/tools/ (return "cortex_*" in name properties)
order: 3
---

> **Brain analogy:** Each MCP tool is a **specialized reflex** — call a specific nerve, get a specific action. `cortex_request_lifecycle` is the voluntary motor cortex (conscious commands), while `cortex_verify` is an autonomic health monitor. Every reflex routes through the spinal cord (MCP transport).

---

## Overview

**26 active canonical MCP tools** organized across 7 categories (28 total — `cortex_process_request` and `cortex_validate_request` are deprecated). All tools are registered via `ConsolidatedTool` base class and exposed through JSON-RPC 2.0 stdio transport.

**Entry point rule:** Use `cortex_request_lifecycle` for full lifecycle tracking or `cortex_classify` for intent routing. `cortex_process_request` is deprecated — do not use.

---

## Tool Categories

### Core (3 active tools) — `cortex/mcp/tools/core.py`

| Tool | Description |
|------|-------------|
| `cortex_challenge` | AI-driven challenge generation using LENS analysis. Validates whether a request is well-scoped before execution. |
| `cortex_classify` | Intent classification via LENS. Returns intent type + confidence for routing decisions. |
| `cortex_request_lifecycle` | Full request lifecycle management — tracks a request from submission to completion with audit trail. |

> ⚠️ `cortex_process_request` — **deprecated** (WAVE-100). Use `cortex_request_lifecycle` instead.

### Governance (3 active tools) — `cortex/mcp/tools/governance.py`

| Tool | Description |
|------|-------------|
| `cortex_governance` | Execute governance actions — enforcement, blocking, remediation with audit logging. |
| `cortex_validate` | Validate code against CORE governance rules with real rule checking. |
| `cortex_load` | Load governance rules (CORE rules, HEXA-MODE definitions, audit checklists, response format) from YAML registry. |

> ⚠️ `cortex_validate_request` — **deprecated**. Use `cortex_validate` instead.

### Intelligence (4 tools) — `cortex/mcp/tools/intelligence.py` + `intelligence_generation.py`

| Tool | Description |
|------|-------------|
| `cortex_knowledge` | Query the CORTEX knowledge base for domain-specific information. |
| `cortex_git` | Git-aware operations — history analysis, commit patterns, branch management. |
| `cortex_generate_tests` | Generate test scaffolds from code analysis with TestQualityGate scoring. |
| `cortex_scaffold_files` | Scaffold files for workflow pipeline artefacts (ScaffoldWriter, Gap G2 closed). |

### Operations (6 tools)

| Tool | File | Description |
|------|------|-------------|
| `cortex_debug` | `debug_tools.py` | Comprehensive debugging — capture logs, analyze issues, generate fix plans. |
| `cortex_refactor` | `operations.py` | Semantic refactoring (extract, rename, organize) — Roslyn by-name symbol rename. |
| `cortex_plan` | `operations.py` | Generate structured remediation plans from audit results (4 execution modes). |
| `cortex_onboard` | `onboard_repository.py` | Onboard repository with LENS analysis + security assessment (P0/P1/P2). |
| `cortex_dashboard` | `operations.py` | Generate dashboard suite — landing page + per-repo dashboards. |
| `cortex_master_plan` | `master_plan_tool.py` | Strategic planning with phase tracking via CortexMasterPlanOrchestrator. |

### Utilities (9 tools) — `cortex/mcp/tools/utilities.py`

| Tool | Description |
|------|-------------|
| `cortex_verify` | Verify CORTEX development environment — Python version, dependencies, MCP connectivity. |
| `cortex_ask` | Ask educational questions about CORTEX architecture with truth-based verification. |
| `cortex_vacuum` | Clean up markdown sprawl with automated archival and verification. |
| `cortex_tools_catalog` | Discover all MCP tools registered in CORTEX. |
| `cortex_total_recall` | Discover and recall CORTEX features and components. |
| `cortex_metrics` | Record and export development metrics — TDD cycles, debug sessions, code generation. |
| `cortex_check` | Health check for dependency drift between requirements.txt and installed packages. |
| `cortex_vision` | Analyze images via Vision API for UI elements, URLs, issues, and structural mappings. |
| `cortex_orchestrator` | Direct orchestrator invocation for advanced use cases. |

### Workflow (1 tool)

| Tool | File | Description |
|------|------|-------------|
| `cortex_workflow` | `operations.py` | Execute workflow templates from `cortex-registry/workflows/`. |

### Work Item Integration (1 tool) — `cortex/mcp/tools/work_item_tool.py`

| Tool | Description |
|------|-------------|
| `cortex_fetch_work_items` | Provider-agnostic work item access (Azure DevOps, Jira, custom). Returns `WorkItem` dicts with `id`, `title`, `description`, `state`, `type`, `tags`, `url`, `raw`. Provider selected via `WORK_ITEM_SOURCE` env var (default: `"ado"`). |

### Sweep Completeness (1 tool) — `cortex/mcp/tools/sweep_status_tool.py`

| Tool | Description |
|------|-------------|
| `cortex_sweep_status` | CORE-064 Sweep Completeness Contract tool. Query sweep catalogue state — open sweeps, resolved items, assert exhaustion. Storage: `.cortex-runtime/sweeps/{sweep_id}.db` (SQLite WAL). |

---

## Practical Examples

**Business Leader:** "26 active tools with clear entry points. Governance is enforced at the transport layer — developers cannot bypass CORE rules."

**Product Owner:** "`cortex_plan` generates remediation plans with 4 execution modes. `cortex_onboard` gives a complete repository assessment in one call. `cortex_sweep_status` tracks long-running refactor sweeps across sessions (CORE-064). `cortex_fetch_work_items` pulls ADO sprint work items directly into developer context."

**Developer:** "I call `cortex_request_lifecycle` for full lifecycle tracking. `cortex_refactor` renames symbols by name — no byte offset needed (Roslyn by-name rename). `cortex_scaffold_files` emits workflow pipeline artefacts to disk."

---

*Verified against `cortex/mcp/tools/` live code · 24 February 2026 · 26 active canonical tools (28 total — 2 deprecated) · Phase 66/67 complete*
