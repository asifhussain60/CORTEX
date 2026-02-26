# MCP Tools Catalog

---
title: MCP Tools Catalog — 38 Active Tools
type: reference
audience: [Software Developers, Product Owners, Business Leaders]
last_verified: 2026-02-26
source_of_truth: cortex/mcp/tools/ (return "cortex_*" in name properties)
order: 3
---

> **Brain analogy:** Each MCP tool is a **specialized reflex** — call a specific nerve, get a specific action. `cortex_request_lifecycle` is the voluntary motor cortex (conscious commands), while `cortex_verify` is an autonomic health monitor. Every reflex routes through the spinal cord (MCP transport).

---

## Overview

**38 active canonical MCP tools** organized across 12 categories. All tools are registered via `ConsolidatedTool` base class and exposed through JSON-RPC 2.0 stdio transport (Pylance-style auto-start).

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
| `cortex_tools_catalog` | Discover all 38 MCP tools with category and description |

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
| `cortex_brain_query` | `brain.py` | Domain brain query — synthesises knowledge from CORTEX's cognitive model |
| `cortex_challenge` | `intelligence.py` | Generate ≥2 alternatives with trade-off analysis using LENS-driven reasoning |
| `cortex_intelligence_matrix` | `intelligence.py` | Cross-cutting intelligence matrix — correlates LENS, governance, and metrics |
| `cortex_refactor` | `intelligence.py` | Semantic refactoring — extract, rename, organize across Python, C#, TypeScript |
| `cortex_vision` | `intelligence.py` | Vision API analysis — UI elements, URLs, issues, and structural mappings |
| `cortex_knowledge` | `operations.py` | Knowledge synthesis from governance YAML registries into actionable insights |

### 2.4 Planning & Audit — various

| Tool | File | Description |
|------|------|-------------|
| `cortex_master_plan` | `master_plan_tool.py` | Master plan management — cortex-master.yaml operations, phase lifecycle |
| `cortex_plan` | `operations.py` | Structured remediation and project planning with audit-driven decomposition |
| `cortex_onboard` | `onboard_repository.py` | Repository onboarding — LENS analysis, security assessment P0/P1/P2, SQLite dashboard |
| `cortex_query_opj` | `opj_tool.py` | Operational Pattern Journal query — surfaces recurring patterns from execution history |

### 2.5 Testing & Quality — `cortex/mcp/tools/test_quality_tool.py`

| Tool | Description |
|------|-------------|
| `cortex_generate_tests` | TDD test generation — produces failing RED tests from specification (CORE-008) |
| `cortex_score_tests` | Test quality gate — scores test suites against CORTEX quality thresholds |

### 2.6 Diagnostics & Health

| Tool | File | Description |
|------|------|-------------|
| `cortex_health_scan` | `health_scan_tool.py` | All 22 orchestrator health endpoints — production readiness validation |
| `cortex_verify` | `toolkit/verify.py` | Verify MCP server health, tool registry, environment, and CORTEX claims |
| `cortex_debug` | `debug_tools.py` | Debug session capture — logs, error analysis, and fix plan generation |
| `cortex_metrics` | `operations.py` | Record and report development metrics — TDD cycles, debug sessions, orchestrator invocations |

### 2.7 Automation & Workflows

| Tool | File | Description |
|------|------|-------------|
| `cortex_workflow` | `workflow_tools.py` | YAML workflow template execution — list, load, and run workflow primitives |
| `cortex_list_workflow_templates` | `list_workflow_templates.py` | List available YAML workflow templates from cortex-registry (Phase 23) |
| `cortex_scaffold_files` | `scaffold_files_tool.py` | Write arbitrary-language source files to disk with governance validation |

### 2.8 Maintenance & Cleanup

| Tool | File | Description |
|------|------|-------------|
| `cortex_vacuum` | `operations.py` | Markdown sprawl cleanup — archives stale files, removes root clutter (CORE-002) |
| `cortex_vacuum_execute` | `vacuum_execute_tool.py` | Full lifecycle vacuum — kill processes, health check, launch |

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
| `cortex_batch_transform` | `toolkit/analyze.py` | Batch data transformation across a collection |
| `cortex_enrich` | `utilities.py` | Content enrichment — adds metadata and context to structured data |
| `cortex_scan` | `toolkit/analyze.py` | Workspace scan — discovers files, patterns, and structures |
| `cortex_bulk_digest_files` | `bulk_digest.py` | Bulk file digest — batch ingestion across 3 pipelines |
| `cortex_sweep_status` | `sweep_status_tool.py` | Sweep catalogue status — CORE-064 completeness tracking |

### 2.12 Deprecated

| Tool ID | Replacement |
|---------|-------------|
| `cortex_process_request` | `cortex_request_lifecycle` |
| `cortex_validate_request` | `cortex_validate` |

---

## Practical Examples

**Business Leader:** "38 active tools with clear entry points. Governance is enforced at the transport layer — developers cannot bypass CORE rules."

**Product Owner:** "`cortex_plan` generates remediation plans with 4 execution modes. `cortex_onboard` gives a complete repository assessment in one call. `cortex_sweep_status` tracks long-running refactor sweeps across sessions (CORE-064). `cortex_query_opj` surfaces patterns from operational history to inform planning."

**Developer:** "I call `cortex_request_lifecycle` for full lifecycle tracking. `cortex_refactor` renames symbols by name — no byte offset needed (Roslyn by-name rename). `cortex_scaffold_files` emits workflow pipeline artefacts to disk. `cortex_generate_tests` produces a failing RED test from any specification."

---

*Verified against `cortex/mcp/tools/` live code · 26 February 2026 · 38 active canonical MCP tools · Phase 82 complete*
