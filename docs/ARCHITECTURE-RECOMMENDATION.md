# CORTEX Architecture Reference

> **Status:** Production — all metrics reflect live codebase counts

---

## Overview

CORTEX (**CO**gnitive **R**eal-**T**ime **EX**ecution) is a production-grade AI Engineering Framework
built on a tiered orchestrator architecture, governed by CORE rules, and surfaced through registered MCP tools.

---

## Architecture Metrics (Live)

| Metric | Source |
|---|---|
| Canonical package: `cortex` (single root) | `cortex/__init__.py` |
| Wired orchestrators (across 4 tiers) | `cortex/core/wiring/specifications/wiring.yaml` |
| MCP tools (registered + planned) | `cortex/mcp/tools/` |
| CORE governance rules (+ AC rules) | `cortex-registry/core/tier0-skull/` |
| Comprehensive test suite | `pytest --collect-only` |
| Top-level `cortex/` dirs | `ls cortex/` |

---

## Orchestrator Tiers

All orchestrators extend `OrchestratorProtocolMixin` (primary) or `OrchestratorBase` (legacy, 2 files only).

| Tier | Purpose |
|---|---|
| `core` | MasterOrchestrator, IntentRouter, TDD, Enforcement, Planning, Stage1/3/4, … |
| `domain` | Refactoring, Digest, Onboarding, Knowledge, Documentation, Reporting, … |
| `support` | Vacuum, Debugger, Sweep, BulkDigest, Session, Convergence, … |
| `git` | GitIntelligence, GitHistory, GitWorkflow, … |

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

- **Production tools** registered in `cortex/mcp/tools/` (Pylance-style stdio transport)
- **Tenant auth**: `TenantContextMiddleware` wired in `cortex/mcp/server.py`
- **Tool categories**: governance, knowledge, orchestration, vacuum, digest, onboard, refactor, metrics, learning, vision

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
cortex/              ← Python source (20 canonical dirs)
  orchestrators/     ← Wired orchestrators across 4 tiers (core, domain, support, git)
  mcp/tools/         ← Registered MCP tools
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
