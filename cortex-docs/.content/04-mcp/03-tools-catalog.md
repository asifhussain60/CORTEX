# MCP Tools Catalog

---
title: MCP Tools Catalog — 28 Registered Tools (39 Target)
type: reference
audience: [Software Developers, Product Owners, Business Leaders]
last_verified: 2026-02-27
source_of_truth: cortex/mcp/mcp_registry.py
order: 3
---

> **Brain analogy:** Each MCP tool is a **specialized reflex** — call a specific nerve, get a specific action. `cortex_request_lifecycle` is the voluntary motor cortex (conscious commands), while `cortex_verify` is an autonomic health monitor. Every reflex routes through the spinal cord (MCP transport).

---

## Overview

**28 registered canonical MCP tools** organized across 11 categories. All tools are registered in `mcp_registry.py` and exposed through JSON-RPC 2.0 stdio transport (Pylance-style auto-start). Target: 39 registered tools; 11 additional tools are in active planning phases.

**Entry point rule:** Use `cortex_request_lifecycle` for full lifecycle tracking or `cortex_classify` for intent routing.

---

## Tool Categories

### 2.1 Core & Routing — `cortex/mcp/tools/core.py`

| Tool | Description |
|------|-------------|
| `cortex_classify` | Intent classification — routes requests to correct orchestrator pipeline |
| `cortex_orchestrator` | Direct orchestrator invocation — routes to any of the 51 wired orchestrators |
| `cortex_request_lifecycle` | Full request lifecycle — classify → plan → execute → validate |
| `cortex_ask` | Educational questions about CORTEX architecture with truth-based verification |
| `cortex_total_recall` | Discover and recall CORTEX features, components, and architecture |
| `cortex_tools_catalog` | Discover all registered MCP tools with category and description |

### 2.2 Governance & Compliance — `cortex/mcp/tools/governance.py` + `toolkit/validate.py`

| Tool | Description |
|------|-------------|
| `cortex_governance` | Execute governance actions — enforcement, blocking, remediation with audit logging |
| `cortex_load` | Load CORE governance rules — skull-rules, core-rules, audit checklist, response format |
| `cortex_validate` | CORE rule compliance validation — op: compliance \| governance \| rules |
| `cortex_check` | Dependency drift detection — checks requirements.txt vs installed packages |

### 2.3 Intelligence & LENS — `cortex/mcp/tools/intelligence.py` + related

| Tool | File | Description |
|------|------|-------------|
| `cortex_challenge` | `intelligence.py` | Generate ≥2 alternatives with trade-off analysis using LENS-driven reasoning |
| `cortex_refactor` | `intelligence.py` | Semantic refactoring — extract, rename, organize across Python, C#, TypeScript |
| `cortex_vision` | `intelligence.py` | Vision API analysis — UI elements, URLs, issues, and structural mappings |
| `cortex_knowledge` | `operations.py` | Knowledge synthesis from governance YAML registries into actionable insights |

> Note: `cortex_brain_query`, `cortex_intelligence_matrix`, and `cortex_learning` are not registered in `mcp_registry.py` (planned for future phases).

### 2.4 Planning & Audit — various

| Tool | File | Description |
|------|------|-------------|
| `cortex_plan` | `operations.py` | Structured remediation and project planning with audit-driven decomposition |
| `cortex_onboard` | `onboard_repository.py` | Repository onboarding — LENS analysis, security assessment P0/P1/P2, SQLite dashboard |
| `cortex_onboard_v3` | `onboard_repository_v3.py` | Onboard with LENS + LLM business language + SQLite dashboard (Phase 21) |

> Note: `cortex_master_plan` and `cortex_query_opj` are not currently registered in `mcp_registry.py`.

### 2.5 Testing & Quality

| Tool | Description |
|------|-------------|
| `cortex_generate_tests` | TDD test generation — produces failing RED tests from specification (CORE-008) |

> Note: `cortex_score_tests` is not registered as an MCP tool. TestQualityGate scoring is invoked internally by the TDD orchestration pipeline.

### 2.6 Diagnostics & Health

| Tool | File | Description |
|------|------|-------------|
| `cortex_verify` | `toolkit/verify.py` | Verify MCP server health, tool registry, environment, and CORTEX claims |
| `cortex_debug` | `debug_tools.py` | Debug session capture — logs, error analysis, and fix plan generation |
| `cortex_metrics` | `operations.py` | Record and report development metrics — TDD cycles, debug sessions, orchestrator invocations |

> Note: `cortex_health_scan` is not currently registered in `mcp_registry.py`.

### 2.7 Automation & Workflows

| Tool | File | Description |
|------|------|-------------|
| `cortex_workflow` | `workflow_tools.py` | YAML workflow template execution — list, load, and run workflow primitives |
| `cortex_capture_metrics` | `operations.py` | Capture development metrics for analysis |

> Note: `cortex_list_workflow_templates` and `cortex_scaffold_files` are not currently registered in `mcp_registry.py`.

### 2.8 Maintenance & Cleanup

| Tool | File | Description |
|------|------|-------------|
| `cortex_vacuum` | `operations.py` | Markdown sprawl cleanup — archives stale files, removes root clutter (CORE-002) |
| `cortex_transform` | `toolkit/analyze.py` | Transform data using specified transformation |

> Note: `cortex_vacuum_execute` is not currently registered in `mcp_registry.py`.

### 2.9 VCS (Git)

| Tool | File | Description |
|------|------|-------------|
| `cortex_git` | `git_orchestrator_tool.py` | Git operations — branching, committing, conflict resolution via GitOrchestrator |

### 2.10 Documentation

| Tool | File | Description |
|------|------|-------------|
| `cortex_dashboard` | `operations.py` | Generate static dashboard suite — landing page + per-repo dashboards with embedded data |

### 2.11 Toolkit / Bulk Operations

| Tool | File | Description |
|------|------|-------------|
| `cortex_transform` | `toolkit/analyze.py` | Transform data using specified transformation |

> Note: `cortex_batch_transform`, `cortex_enrich`, `cortex_scan`, `cortex_bulk_digest_files`, and `cortex_sweep_status` are not currently registered in `mcp_registry.py`. `cortex_sweep_status` functionality is handled by `SweepCatalogueOrchestrator` internally.

### 2.12 Deprecated

| Tool ID | Replacement |
|---------|-------------|
| `cortex_process_request` | `cortex_request_lifecycle` |
| `cortex_validate_request` | `cortex_validate` |

---

## Practical Examples

**Business Leader:** "28 registered tools with clear entry points. Governance is enforced at the transport layer — developers cannot bypass CORE rules. 11 additional tools are planned toward the 39-tool target."

**Product Owner:** "`cortex_plan` generates remediation plans with 4 execution modes. `cortex_onboard` gives a complete repository assessment in one call. `cortex_generate_tests` automates the RED phase of TDD. `cortex_verify` confirms the MCP server is live."

**Developer:** "I call `cortex_request_lifecycle` for full lifecycle tracking. `cortex_refactor` renames symbols by name — no byte offset needed (Roslyn by-name rename). `cortex_generate_tests` produces a failing RED test from any specification. `cortex_verify(op='mcp')` confirms all 28 registered tools are available."

---

*Verified against `cortex/mcp/mcp_registry.py` · 26 February 2026 · 28 registered canonical MCP tools · 39 target*
