# CORTEX Architecture Reference

> **Updated:** 2026-02-24 (Phase 65 — Enterprise Hardening complete)
> **Status:** Production — all metrics reflect live codebase counts

---

## Overview

CORTEX (**CO**gnitive **R**eal-**T**ime **EX**ecution) is a production-grade AI Engineering Framework
built on a tiered orchestrator architecture, governed by 35 CORE rules, and surfaced through 26 MCP tools.

---

## Architecture Metrics (Live)

| Metric | Count | Source |
|---|---|---|
| Canonical package | `cortex` (single root) | `cortex/__init__.py` |
| Wired orchestrators | 41 (across 10 tiers) | `cortex/core/wiring/specifications/wiring.yaml` |
| MCP tools (production) | 24 | `cortex/mcp/mcp_registry.PRODUCTION_TOOLS` |
| CORE governance rules | 35 active | `cortex-registry/core/tier0-skull/` |
| Test suite | 15,739 tests | `pytest --collect-only` |
| Top-level `cortex/` dirs | 16 canonical | `ls cortex/` |

---

## Orchestrator Tiers

All orchestrators extend `OrchestratorProtocolMixin` (primary, Phase 58) or `OrchestratorBase` (legacy, 2 files only).

| Tier | Count | Purpose |
|---|---|---|
| `core` | 7 | MasterOrchestrator, IntentRouter, TDD, Enforcement, Planning, Stage1/3/4 |
| `domain` | 6 | Refactoring, Digest, Onboarding, Knowledge, Documentation, Reporting |
| `support` | 14 | Vacuum, Debugger, Sweep, BulkDigest, Session, Convergence, … |
| `health` | 1 | HealthOrchestrator (22-endpoint health check) |
| `git` | 3 | GitIntelligence, GitHistory, GitWorkflow |
| `intelligence` | 2 | Intelligence, AgentRules |
| `strategies` | 1 | ExecutionStrategy |
| `synthesis` | 1 | KnowledgeSynthesis |
| `validation_extended` | 2 | Coherence, SolidValidation |
| `workflow` | 4 | WorkflowComposer, TemplateComposer, AuditVerifier, PostPhaseDedup |
| **Total** | **41** | |

---

## MCP Architecture

CORTEX uses **Pylance-style MCP** — auto-starts with VS Code via stdio transport.

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

- **24 production tools** registered in `PRODUCTION_TOOLS` dict (`cortex/mcp/mcp_registry.py`)
- **Tenant auth**: `TenantContextMiddleware` wired in `cortex/mcp/server.py` (Phase 65-A)
- **Tool categories**: governance, knowledge, orchestration, vacuum, digest, onboard, refactor, metrics

---

## Governance

| Rule | Description |
|---|---|
| CORE-002 | All output inline — never create `.md`/`.txt` report files |
| CORE-008 | TDD mandatory — write failing test first |
| CORE-011 | Type hints on all functions |
| CORE-012 | Docstrings on all public APIs |
| CORE-028 | File naming: `snake_case` only |
| CORE-035 | Single canonical implementation — no duplicates |
| CORE-048 | Holistic validation gate before IMPLEMENT/FIX/REFACTOR |
| CORE-049 | Silent autonomous execution (progress bars only) |
| CORE-064 | Sweep Completeness Contract — no partial sweeps |

Full rule catalogue: `cortex-registry/core/tier0-skull/`

---

## File Organization

```
cortex/              ← Python source (16 canonical dirs)
  orchestrators/     ← 41 wired orchestrators across 10 tiers
  mcp/tools/         ← 24 production MCP tools
  core/              ← OrchestratorProtocolMixin, OrchestratorBase, FileFactory, WorkflowEngine
  testing/           ← Test framework, parallel runner, quality gate
  intelligence/      ← LENS, domain brain, knowledge synthesis
  governance/        ← Rule enforcement, compliance
  infrastructure/    ← Audit logger, cache, GitHub client
  templates/         ← Dashboard renderer, response templates
cortex-registry/     ← YAML governance rules, patterns, plans
tests/               ← All tests (mirrors cortex/ structure)
.cortex-runtime/     ← Runtime data (logs, traces, .db files)
cortex-docs/         ← User-facing documentation (HTML/CSS + Markdown)
```

---

## Key Entry Points

| Component | Location |
|---|---|
| MasterOrchestrator | `cortex/orchestrators/core/master_orchestrator.py` |
| IntentRouter | `cortex/orchestrators/core/intent_router.py` |
| TDDOrchestrator | `cortex/orchestrators/core/tdd_orchestrator.py` |
| EnforcementOrchestrator | `cortex/orchestrators/core/enforcement_orchestrator.py` |
| HealthOrchestrator | `cortex/orchestrators/health/health_orchestrator.py` |
| VacuumOrchestrator | `cortex/orchestrators/health/vacuum_orchestrator.py` |
| OrchestratorProtocolMixin | `cortex/core/orchestrator_protocol_mixin.py` |
| OrchestratorBase | `cortex/core/orchestrator_base.py` (legacy) |
| MCP Server | `cortex/mcp/server.py` |
| TenantContextMiddleware | `cortex/mcp/tenant_context_middleware.py` |
| WorkflowEngine | `cortex/core/workflow_engine.py` |

---

## Intelligence Stack

```
LENS Analysis
  └── Language → Examination → Navigation → Synthesis
      ├── cortex/lens/          (analyzers per language/tech)
      ├── cortex/intelligence/  (domain brain, memory tiers)
      └── cortex/knowledge/     (knowledge base, synthesis)

Memory Tiers
  ├── tier0: Runtime working memory
  ├── tier1_learned: Vacuum cleaners + cognitive retention
  └── tier2: Long-term persistent knowledge
```

---

## Phase Completion Status

| Phase | Status | Description |
|---|---|---|
| 58 | ✅ COMPLETE | OrchestratorProtocolMixin rollout (cross-cutting protocol) |
| 59 | ✅ COMPLETE | Deduplication sweep (AuditEntry, Ok/Err, OperationMode) |
| 64 | ✅ COMPLETE | Unified brain golden coverage (7 sub-phases) |
| 65 | ✅ COMPLETE | Enterprise hardening (tenant auth, ImportError sweep, mixin rollout) |
| 60 | ⚪ PLANNED | SLOC reduction target (383K → 180K) |
| 61 | ⚪ PLANNED | Orchestrator consolidation (124 → 22) |
| 67 | ⚪ PLANNED | WorkflowEngine runtime wiring + THIN INDEX fix |
