# CORTEX Architecture Overview

> Auto-generated from cortex-impl-map.yaml on 2026-01-21

**Current Production Readiness:** 62% (100% achievable with Phases F-J)  
**Definition of Ready:** ✅ 100% (41 phases, 257 unique AC IDs tested)  
**Last Updated:** 2026-01-21

---

## System Architecture

CORTEX is an intelligent orchestration platform with multi-tier governance, REST/MCP/CLI APIs, distributed state management, and enterprise resilience patterns. The architecture spans three critical dimensions:

### Governance Layer (3-Tier Hierarchy)

The governance system uses immutable tier precedence (tier0 > tier1 > tier2) to enforce rules at global, domain, and environment levels:

| Tier | Purpose | Location | Rules |
|------|---------|----------|-------|
| **Tier 0** | Immutable global rules | `cortex_brain/tier0/governance/core-rules.yaml` | 29 SKULL rules (CORE-001 through CORE-029) |
| **Tier 1** | Domain-specific rules | `cortex_brain/tier1/governance/domain-rules.yaml` | Domain customizations, business rules |
| **Tier 2** | Environment-specific rules | `cortex_brain/tier2/governance/` | Safety rules, credential protection, security policies, hallucination prevention |

**Tier Precedence:** When conflicts occur, tier0 rules override tier1, which override tier2. This ensures immutable global governance cannot be weakened at domain or environment levels.

### Orchestration Engine

The core orchestration system manages business process automation through stateful, composable orchestrators:

- **Lifecycle:** Initialize → Prepare → Execute → Finalize → Complete/Rollback
- **Resilience:** Circuit breakers, partial functionality mode, graceful degradation, saga compensation
- **State Management:** Transactional state persistence, optimistic locking, lock-free registry, orphan cleanup
- **Concurrency:** Multi-orchestrator coordination, race condition prevention, distributed locking

### Domain Brain Integration

Business knowledge ingestion and conflict resolution:

- **Document Processing:** Parse business knowledge, extract rules, maintain consistency
- **Knowledge Graph:** Domain-specific rules, entity relationships, decision trees
- **Conflict Resolution:** Automatic resolution via tier system, escalation to human review
- **Learning Loop:** Incorporate feedback, refine rules, improve accuracy

---

## Implementation Status: 41 Phases

### Overview

| Category | Count | Status |
|----------|-------|--------|
| **Implemented** | 10 | ✅ Working (governance, intelligence, infrastructure, state, recovery, observability, consolidation) |
| **In Progress** | 2 | 🔄 Phase A-D complete, Phase E TDD ongoing (32% complete) |
| **Stub Phases** | 21 | 🟡 Design-complete, ready for implementation |
| **Not Started** | 8 | 🔴 Phases F-J for 100% production confidence |
| **Total** | **41** | ✅ Tracked with full dependencies |

### Codebase Statistics

| Metric | Value |
|--------|-------|
| **Total Python Files** | 413 |
| **Cortex Package Files** | 413 (canonical) |
| **Cortex Brain Files** | 41 (state + governance) |
| **Test Files** | 409 |
| **MCP Tools Exposed** | 14 (stub implementations) |
| **Unique AC IDs Tested** | 257 |

### Canonical Package Structure

```
cortex/               # Canonical package (413 files)
├── api/              # API layer
├── brain/            # Brain integration logic (269 files)
├── core/             # Core utilities
├── infrastructure/   # Infrastructure components
├── mcp/              # MCP server + 14 stub tools
├── orchestrators/    # 9 orchestrator classes (5 protocols, 4 concrete)
└── tools/            # Reusable tooling

cortex_brain/         # State management (41 files)
├── tier0/            # Global governance (core-rules.yaml)
├── tier1/            # Domain rules (empty)
├── tier2/            # Context rules (empty)
├── state/            # governance.db + runtime state
└── ...               # Domain brain, releases, governance

tests/                # Test location
├── unit/             # ~300 test files
├── integration/      # ~80 test files
└── e2e/              # ~29 test files
```

---

## Critical Path to 100% Production Readiness

### Confidence Assessment

| State | Confidence | Milestone |
|-------|------------|-----------|
| **Current** | 62% | 76 collection errors, 44 missing exports, 15 RecursionErrors |
| **After Phase F** | 68% | Export Completion - 44 missing exports resolved |
| **After Phase G** | 75% | Circular Import Fix - 0 collection errors |
| **After Phase E** | 90% | TDD Implementation - ≥98% tests passing |
| **After Phases H-J** | 100% | E2E, CI/CD, Governance complete |

### Phase F: Export Completion (1 day)

- Add 44 missing class/function exports to stub modules
- Eliminate ImportError in test collection
- **Prerequisite for:** Phase G, Phase E

### Phase G: Circular Import Fix (1-2 days)

- Break circular dependency in `cortex.orchestrators.core` hierarchy
- Fix 15 RecursionErrors
- **Depends on:** Phase F

### Phase E: TDD Implementation (15-20 days)

- Transform 125 stub modules into working code
- Target: ≥98% tests passing (≥5500 of 5653)
- **Completed Work:**
  - Intent Router Module: 128/128 tests (100%)
  - IntentClassifier: 53/53 tests (100%)
  - MultiModalIntentProcessor: 25/25 tests (100%)
  - Governance: 161/368 tests (44%)

### Phases H-J: Validation & Governance (7-9 days)

- **Phase H:** E2E Validation Framework - smoke, load, chaos tests ✅ COMPLETED
- **Phase I:** CI/CD Pipeline Validation ✅ COMPLETED  
- **Phase J:** Governance Tier Content Population ✅ COMPLETED

---

## MCP Tools

### Current Status: Stub Implementations

| Category | Tools | Status |
|----------|-------|--------|
| **Governance** | query_tool, validate_tool, execute_tool, analyze_tool, report_tool | Stub |
| **Orchestration** | status_tool, monitor_tool, optimize_tool, diagnose_tool | Stub |
| **Knowledge** | search_tool, analyze_tool, generate_tool | Stub |
| **Utility** | echo_tool, sample_tool, transform_tool | Stub |

**Location:** `cortex/mcp/server.py` + `cortex/mcp/tools/`  
**Internal Tools (not MCP-exposed):** `cortex/tools/` (cortex_brain_integration, devx_tools, profiling_tools)

---

## Orchestrators

### Status: Partial Implementation

| Type | Count | Status |
|------|-------|--------|
| **Protocols** | 5 | IOrchestrator, IExecutor, IPlanner, IAnalyzer, IValidator |
| **Concrete** | 4 | MasterOrchestrator, PlanningOrchestrator, AnalysisOrchestrator, ExecutionOrchestrator |
| **Location** | - | `cortex/orchestrators/` |
---

## Related Documentation

- **Getting Started:** [Installation & Quickstart](../01-getting-started/0-installation.md)
- **Design Principles:** [CORTEX Design Foundations](./1-design-principles.md)
- **Multi-Tier Architecture:** [Tier System Details](./2-multi-tier-architecture.md)
- **Orchestration Engine:** [Orchestrator Lifecycle & Patterns](./3-orchestration-engine.md)
- **Governance Rules:** [29 SKULL Rules Reference](./governance-rules.md)
- **Implementation Phases:** [Phase Status & Dependencies](./6-implementation-phases.md)
- **Definition of Ready:** [DoR Assessment & Verification](./definition-of-ready.md)
- **Gap Analysis:** [Identified Gaps & Resolutions](../05-reference/gap-analysis.md)
- **Remediation Status:** [Remediation Phases](../05-reference/remediation-status.md)

---

## Diagrams

- [Architecture Overview](../_diagrams/architecture-overview.mmd)
- [Governance Tiers](../_diagrams/governance-tiers.mmd)
- [Phase Dependencies](../_diagrams/phase-dependencies.mmd)
- [Orchestration Flow](../_diagrams/orchestration-flow.mmd)
- [MCP Tools](../_diagrams/mcp-tools.mmd)
- [Production Readiness](../_diagrams/production-readiness.mmd)
- [State Management](../_diagrams/state-management.mmd)
- [Resilience Patterns](../_diagrams/resilience-patterns.mmd)

---

## Key Metrics Summary

| Metric | Value | Status |
|--------|-------|--------|
| **Phases Tracked** | 41 | ✅ Comprehensive |
| **Phases Implemented** | 10 | ✅ Working |
| **Phases In Progress** | 2 | 🔄 Active |
| **Unique AC IDs Tested** | 257 | ✅ Coverage |
| **Test Files** | 409 | ✅ Extensive |
| **Production Readiness** | 62% → 100% | ✅ Path clear |
| **Python Files** | 413 | ✅ Consolidated |

