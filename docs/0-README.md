# CORTEX Documentation

> Auto-generated from cortex-impl-map.yaml on 2026-01-21

**Last Updated:** 2026-01-21  
**Version:** 3.9  
**Status:** 62% Production Ready → 100% with Phases F-J  
**Confidence Score:** 62/100 → 100/100

**CORTEX** is an intelligent AI-powered orchestration platform with multi-tier governance architecture, REST/MCP/CLI APIs, and resilience-first design. The system uses immutable tier precedence (tier0 > tier1 > tier2) to govern orchestrators, knowledge ingestion, and domain-specific rules.

### 🚨 Critical Status

**Production Readiness:** 62% → **100% achievable with Phases F-J**

| Phase | Work | Duration | Result |
|-------|------|----------|--------|
| **F** | Export Completion | 1 day | 62% → 68% |
| **G** | Circular Import Fix | 1-2 days | 68% → 75% |
| **E** | TDD Implementation | 15-20 days | 75% → 90% |
| **H-J** | Validation & Governance | 7-9 days | 90% → 100% ✅ COMPLETED |

**See:** [Architecture Overview](02-architecture/1-system-overview.md) | [Implementation Phases](02-architecture/6-implementation-phases.md) | [Definition of Ready](02-architecture/definition-of-ready.md)

### Current Implementation Status

| Component | Status | Tests |
|-----------|--------|-------|
| **Governance Framework** | ✅ IMPLEMENTED | 75 |
| **Intelligence Modules** | ✅ IMPLEMENTED | 42 |
| **Infrastructure Resilience** | ✅ IMPLEMENTED | 126 |
| **State Management & Concurrency** | ✅ IMPLEMENTED | 82 |
| **Error Recovery & Fault Tolerance** | ✅ IMPLEMENTED | 127 |
| **Production Observability** | ✅ IMPLEMENTED | 137 |
| **Source Code Consolidation** | ✅ IMPLEMENTED | 460 |
| **E2E Validation (Phase H)** | ✅ COMPLETED | 11 |
| **CI/CD Validation (Phase I)** | ✅ COMPLETED | 9 |
| **Governance Content (Phase J)** | ✅ COMPLETED | 12 |

**Key Metrics:**
- ✅ **10 implemented phases** (1,081+ tests passing)
- ✅ **2 in-progress phases** (Phase E at 32%)
- 🔄 **8 not-started phases** (Phases F, G pending)
- ✅ **413 Python modules** in canonical `cortex/` package
- ✅ **409 test files** in tests/
- ⚠️ **14 MCP tools** (stub implementations)
- ✅ **257 unique AC IDs tested**

## Quick Navigation

### 🚀 Getting Started
- **[Installation & Setup](01-getting-started/0-installation.md)** - Prerequisites and environment setup
- **[Quick Start](01-getting-started/1-quickstart.md)** - 15-minute hands-on tutorial
- **[First Orchestrator](01-getting-started/2-first-orchestrator.md)** - Create your first orchestrator
- **[Troubleshooting Setup](01-getting-started/3-troubleshooting.md)** - Common setup issues

### 🏗️ Architecture
- **[System Overview](02-architecture/1-system-overview.md)** - Multi-tier architecture and components
- **[Design Principles](02-architecture/2-design-principles.md)** - Core design philosophy
- **[Orchestration Engine](02-architecture/3-orchestration-engine.md)** - ConversationProtocol, complexity gate, response composition
- **[Domain Brain](02-architecture/4-domain-brain.md)** - Knowledge ingestion, BKIO, conflict resolution
- **[Resilience Patterns](02-architecture/5-resilience-patterns.md)** - Circuit breakers, retries, rollback
- **[Architecture Decision Records](02-architecture/adrs/)** - Design decisions and rationale

### 📡 API Reference
- **[REST API](03-api-reference/rest-api/0-guide.md)** - REST endpoints for orchestrators, knowledge, governance
- **[MCP Protocol](03-api-reference/mcp-protocol/0-specification.md)** - JSON-RPC 2.0 MCP server specification
- **[CLI Commands](03-api-reference/cli/0-guide.md)** - Command-line reference
- **[Schemas](03-api-reference/schemas/)** - Data structure definitions

### 📚 How-To Guides
- **[Deployment](04-guides/deployment/0-overview.md)** - Local, staging, and production deployment
  - [Local Development](04-guides/deployment/1-local-development.md)
  - [Troubleshooting](04-guides/operations/4-troubleshooting.md)
  - [FAQ](04-guides/deployment/4-faq.md)
- **[Integration](04-guides/integration/0-overview.md)** - Building custom orchestrators and integrations
- **[Operations](04-guides/operations/0-overview.md)** - Monitoring, alerting, and compliance
- **[Advanced](04-guides/advanced/0-overview.md)** - Resilience configuration and optimization

### 📖 Reference
- **[Glossary](05-reference/glossary.md)** - Term definitions
- **[FAQ](05-reference/faq.md)** - Frequently asked questions
- **[Known Issues](05-reference/known-issues.md)** - Issues and workarounds
- **[Changelog](05-reference/changelog.md)** - Version history
- **[Compliance](05-reference/compliance-mappings.md)** - GDPR/HIPAA/SOC2 mappings

### 🎓 Tutorials
- **[Orchestrator Tutorials](06-tutorials/orchestrator-tutorials/0-index.md)** - Hands-on examples
- **[API Integration](06-tutorials/api-integration/0-index.md)** - API integration patterns
- **[Operations](06-tutorials/operations/0-index.md)** - Operational tasks

### 🤝 Contributing
- **[Contributing Guidelines](07-contributing/1-contributing-guidelines.md)** - How to contribute
- **[Development Setup](07-contributing/2-development-setup.md)** - Local development environment
- **[Testing](07-contributing/3-testing-strategy.md)** - Testing approach
- **[Pull Request Process](07-contributing/5-pull-request-process.md)** - PR workflow

---

## Core Capabilities

### ✅ Implemented Phases (10 Completed)

| Phase ID | Title | Focus | Tests | Status | Files |
|----------|-------|-------|-------|--------|-------|
| **impl-governance-001** | Context-Aware Governance | 28/29 CORE rules functional, situational dispatch | 75 | ✅ | cortex/brain/core/governance/*.py |
| **impl-intelligence-001** | Routing Decision Intelligence | Tracks routing accuracy, misrouting detection | 12 | ✅ | cortex/core/intelligence/routing_intelligence.py |
| **impl-intelligence-002** | Operation Duration Intelligence | P50/P95/P99 baselines, slow operation detection | 15 | ✅ | cortex/core/intelligence/duration_intelligence.py |
| **impl-intelligence-003** | Error Pattern Recognition | Error analysis, pattern detection, brittle handler ID | 15 | ✅ | cortex/core/intelligence/error_intelligence.py |
| **impl-infra-001** | Infrastructure Resilience | Connection pools, circuit breakers, retries, degradation | 126 | ✅ | cortex/infrastructure/*.py (5 modules, 418+ LOC) |
| **impl-state-002** | State Management & Concurrency | Transactional state, optimistic locking, lock-free registry | 82 | ✅ | cortex/infrastructure/transaction_manager.py, cortex/core/state/*.py |
| **impl-recovery-003** | Error Recovery & Fault Tolerance | Saga compensation, orphan cleanup, crash recovery, fault isolation | 127 | ✅ | cortex/core/recovery/saga_coordinator.py (418 LOC), orphan_cleaner.py (481 LOC) |
| **impl-ops-004** | Production Observability | Structured logging, Prometheus metrics, distributed tracing, health checks, profiling | 137 | ✅ | cortex/infrastructure/*.py, deployment/grafana/*.json, deployment/prometheus/alerts.yaml |
| **consolidation-001** | Source Code Consolidation | src/ → cortex/ (1,353 imports consolidated, 16,935 legacy lines removed) | 460 | ✅ | cortex/ (canonical structure) |

**Total Implemented:** 551 tests passing, 2,028+ lines of production code, 7 critical patterns verified

### 🟡 Blocked Phases (3 Waiting for Phase A/B)

| Phase ID | Title | Blocker | Unblocked By | Timeline |
|----------|-------|---------|--------------|----------|
| **impl-arch-011** | Hallucination Prevention | Tier structure duplication (Phase A) | Phase A consolidation (1 day) | → 100% ready |
| **impl-arch-022** | MCP Compliance | No tool registry or centralization (Phase B) | Phase B MCP registry (2 days) | → 100% ready |
| **impl-arch-025** | Governance Composition | Tier duplication (Phase A) | Phase A consolidation (1 day) | → 100% ready |

### 🔶 Stub Phases (21 Design-Complete, TDD-Ready)

These phases are fully designed with 121 acceptance criteria and 664 tests pre-written, ready for implementation:

**Governance (3):** SKULL protocol, context API, governance tools  
**Intelligence (6):** Preference learning, performance optimization, behavior patterns, anomaly detection, complexity prediction, intent synthesis  
**Infrastructure (4):** Advanced networking, performance monitoring, security hardening, caching  
**Knowledge (3):** Semantic search, knowledge graph, conflict resolution  
**Orchestration (5):** Intent routing, continuation protocol, adaptive execution, domain orchestrators, ecosystem integration

**Implementation Status:** Will begin immediately after Phase A/B completion (estimated 2-3 weeks for TDD implementation phase)

### Completed & Production-Ready Capabilities

| Capability | Description | Phase | Tests |
|------------|-------------|-------|-------|
| **Context-Aware Governance** | 28/29 CORE rules operational, situational dispatch | impl-governance-001 | 75 |
| **Routing Intelligence** | Decision outcome tracking with SQLite persistence | impl-intelligence-001 | 12 |
| **Duration Baselines** | P50/P95/P99 calculation, slow op detection | impl-intelligence-002 | 15 |
| **Error Pattern Analysis** | Context-sanitized pattern detection, handler tracking | impl-intelligence-003 | 15 |
| **Connection Resilience** | Pool management, bulkhead isolation, resource limits | impl-infra-001 | 126 |
| **Circuit Breakers** | Fail-fast protection, graceful degradation | impl-infra-001 | 126 |
| **Retry Strategies** | Exponential backoff, jitter, max attempts | impl-infra-001 | 126 |
| **Transactional State** | ACID compliance, rollback on failure | impl-state-002 | 82 |
| **Optimistic Locking** | Non-blocking concurrent updates | impl-state-002 | 82 |
| **Lock-Free Registry** | Concurrent-safe orchestrator discovery | impl-state-002 | 82 |
| **Saga Compensation** | Distributed transaction rollback (418 LOC) | impl-recovery-003 | 127 |
| **Orphan Cleanup** | Automatic recovery of lost operations | impl-recovery-003 | 127 |
| **Crash Recovery** | Resume interrupted orchestrations | impl-recovery-003 | 127 |
| **Fault Isolation** | Component failure containment | impl-recovery-003 | 127 |
| **Structured Logging** | JSON + correlation IDs + PII redaction (516 LOC) | impl-ops-004 | 137 |
| **Prometheus Metrics** | RED method, cardinality control (462 LOC) | impl-ops-004 | 137 |
| **Distributed Tracing** | OpenTelemetry with sampling (362 LOC) | impl-ops-004 | 137 |
| **Health Checks** | Liveness/readiness distinction | impl-ops-004 | 137 |
| **Grafana Dashboards** | System, governance, database views + alerts | impl-ops-004 | 137 |

**Total:** 10 phases complete, 551+ tests passing (100% pass rate)

### Key Architectural Patterns

| Pattern | Implementation | Benefit |
|---------|----------------|---------|
| **Multi-Tier Governance** | Tier 0 (immutable) → Tier 3 (knowledge) | Safety, flexibility |
| **ContinuationDecision** | Explicit turn termination reasons | Testability, auditability |
| **Approval Matrix** | Complexity-based confirmation | UX optimization |
| **Hash Chain Audit** | Tamper-evident logging | Compliance, trust |
| **Circuit Breaker** | Resilience with fail-fast | Reliability |
| **BKIO Conflict Resolution** | Hierarchical priority + LENS synthesis | Knowledge integrity |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CORTEX Platform                                 │
├──────────────────┬──────────────────┬──────────────────┬───────────────────┤
│   REST API       │   MCP Server     │      CLI         │   Copilot Chat    │
│   (FastAPI)      │   (JSON-RPC)     │   (cortex-*)     │   (Prompts)       │
└────────┬─────────┴────────┬─────────┴────────┬─────────┴─────────┬─────────┘
         │                  │                  │                   │
         └──────────────────┴──────────────────┴───────────────────┘
                                     │
                    ┌────────────────▼────────────────┐
                    │     LENS Protocol (Intent)      │
                    │  Language → Examination →       │
                    │  Navigation → Synthesis         │
                    └────────────────┬────────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         │                           │                           │
         ▼                           ▼                           ▼
┌─────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│    TIER 0       │     │   Master Orchestrator│     │    Domain Brain     │
│  Governance     │     │   (Conversation      │     │  (Tier 3 Knowledge) │
│  (29 CORE rules)│     │    Protocol)         │     │  (4 Adapters, BKIO) │
└─────────────────┘     └─────────────────────┘     └─────────────────────┘
                                     │
                    ┌────────────────▼────────────────┐
                    │    Response Composition         │
                    │  (6 modes, 5 tones, templates)  │
                    └────────────────┬────────────────┘
                                     │
                    ┌────────────────▼────────────────┐
                    │    Audit Trail + Hash Chain     │
                    │  (5000+ entries, unbroken)      │
                    └─────────────────────────────────┘
```

---

## For Different Roles

**Architects & Designers**
→ Start with [System Overview](02-architecture/1-system-overview.md) then [Design Principles](02-architecture/2-design-principles.md)

**Developers**
→ Start with [Quick Start](01-getting-started/1-quickstart.md) then [First Orchestrator](01-getting-started/2-first-orchestrator.md)

**Integrators**
→ Start with [MCP Protocol](03-api-reference/mcp-protocol/0-specification.md) or [REST API](03-api-reference/rest-api/0-guide.md)

**Operators**
→ Start with [Deployment Guide](04-guides/deployment/0-overview.md) then [Troubleshooting](04-guides/operations/4-troubleshooting.md)

**Contributors**
→ Start with [Contributing Guidelines](07-contributing/1-contributing-guidelines.md) then [Development Setup](07-contributing/2-development-setup.md)

---

## Document Status

| Section | Status | Last Updated |
|---------|--------|--------------|
| Getting Started | ✅ Complete | 2026-01-21 |
| Architecture | ✅ Complete | 2026-01-21 |
| API Reference | ✅ Complete | 2026-01-21 |
| Guides | 🔄 Expanding | 2026-01-21 |
| Reference | ✅ Complete | 2026-01-21 |
| Tutorials | 🔄 In Progress | 2026-01-21 |
| Contributing | 🔄 In Progress | 2026-01-21 |
| Diagrams | ✅ Complete | 2026-01-21 |

---

## Diagrams

- [Architecture Overview](_diagrams/architecture-overview.mmd)
- [Governance Tiers](_diagrams/governance-tiers.mmd)
- [Phase Dependencies](_diagrams/phase-dependencies.mmd)
- [Orchestration Flow](_diagrams/orchestration-flow.mmd)
- [MCP Tools](_diagrams/mcp-tools.mmd)
- [Production Readiness](_diagrams/production-readiness.mmd)
- [State Management](_diagrams/state-management.mmd)
- [Resilience Patterns](_diagrams/resilience-patterns.mmd)

---

**Source of Truth:** `_workspaces/roadmap/cortex-impl-map.yaml`  
**Governance Database:** `cortex_brain/state/governance.db`  
**Test Suite:** 409 test files, 257 unique AC IDs tested
