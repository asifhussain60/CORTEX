# Quick Reference Guide

**CORTEX Status:** ✅ 100% Definition of Ready | 🔴 36% Production Ready (→ 100% in 4 days)  
**Last Updated:** 2026-01-20

---

## I'm New - Where Do I Start?

1. **Read This Page** - You're here! Quick overview of key information
2. **Installation:** [01-getting-started/0-installation.md](../01-getting-started/0-installation.md)
3. **First Steps:** [01-getting-started/1-quickstart.md](../01-getting-started/1-quickstart.md)
4. **Architecture:** [02-architecture/1-system-overview.md](../02-architecture/1-system-overview.md)

---

## System Status Dashboard

### Definition of Ready: ✅ 100%

| Element | Count | Status |
|---------|-------|--------|
| **Phases Documented** | 34/34 | ✅ Complete |
| **Acceptance Criteria** | 121 | ✅ Defined |
| **Tests Specified** | 664 | ✅ Pre-written |
| **Dependencies Mapped** | All | ✅ Complete |
| **Governance Rules** | 29 SKULL | ✅ Documented |

**Verdict:** ✅ Ready for full implementation

---

### Production Readiness: Current State

```
Current:    36% ████████░░░░░░░░░░░░░░░░░░░░░░░░
Phase A:    60% ██████████████░░░░░░░░░░░░░░░░░░  (1 day)
Phase B:    95% ███████████████████████░░░░░░░░░  (2 days)
Final:     100% ████████████████████████████░░░░  (1 day)
```

| Phase | Work | Duration | Before | After | Unblocks |
|-------|------|----------|--------|-------|----------|
| **A: Consolidate** | Delete duplicates, consolidate tiers | 1 day | 36% | 60% | 2 phases |
| **B: MCP Registry** | Create registry, reorganize tools | 2 days | 60% | 95% | 1 phase |
| **C: Harden** | Test, verify, update docs | 1 day | 95% | 100% | All ready |
| **TOTAL** | Architecture fixes | **4 days** | 36% | **100%** | **All 3 blocked phases** |

---

## What's Working (36% → 100% in 4 Days)

### ✅ Currently Implemented (10 Phases, 551 Tests)

| Phase | Focus | Tests | Status |
|-------|-------|-------|--------|
| **impl-governance-001** | Context-aware rule dispatch (28/29 rules) | 75 | ✅ |
| **impl-intelligence-001** | Routing decision tracking | 12 | ✅ |
| **impl-intelligence-002** | Duration baselines (p50/p95/p99) | 15 | ✅ |
| **impl-intelligence-003** | Error pattern recognition | 15 | ✅ |
| **impl-infra-001** | Resilience (pools, circuit breakers, retries) | 126 | ✅ |
| **impl-state-002** | State mgmt & concurrency (transactional, locking) | 82 | ✅ |
| **impl-recovery-003** | Fault tolerance (saga, orphan cleanup, crash recovery) | 127 | ✅ |
| **impl-ops-004** | Observability (logging, metrics, tracing, health) | 137 | ✅ |
| **consolidation-001** | Source consolidation (src/ → cortex/) | 460 | ✅ |

**Production readiness contribution:** 36% of system ready for deployment

---

### 🟡 Blocking Issues (4 Critical, Fixed in Phase A/B)

| Issue | Impact | Phase | Timeline | Unblocks |
|-------|--------|-------|----------|----------|
| **Tier duplication** | Governance split across 2 locations (breaks precedence) | A | 1 day | arch-011, arch-025 |
| **MCP tools not centralized** | No registry, no discovery, no governance | B | 2 days | arch-022 |
| **Hallucination prevention wrong location** | Python files not integrated into tier system | A | 1 day | arch-011 |
| **cortex/brain duplicates cortex_brain** | Multiple sources of truth (35+ duplicate files) | A | 1 day | All governance |

**Timeline:** Execute Phase A → Phase B → Phase C (4 days total) to achieve 100% readiness

---

### 🔶 Ready for Implementation (21 Stub Phases)

All design-complete with acceptance criteria + pre-written tests. Ready for TDD after Phase A/B:

- **Governance (3):** Hardening, governance tools, complexity gate
- **Intelligence (6):** Preferences, optimization, behavior, anomaly detection, complexity prediction
- **Infrastructure (4):** Advanced networking, monitoring, security, caching  
- **Knowledge (3):** Semantic search, knowledge graph, conflict resolution
- **Orchestration (5):** Intent routing, continuation protocol, adaptive execution, domain orchestrators

---

## Production Readiness Timeline

```
Current:    36% ████████░░░░░░░░░░░░░░░░░░░░░░░░
Phase A:    60% ██████████████░░░░░░░░░░░░░░░░░░  (1 day: Tier consolidation)
Phase B:    95% ███████████████████████░░░░░░░░░  (2 days: MCP registry)
Final:     100% ████████████████████████████████  (1 day: Verification)
```

| Phase | Work | Duration | Before | After | Unblocks |
|-------|------|----------|--------|-------|----------|
| **A** | Delete tier duplicates, consolidate governance | 1 day | 36% | 60% | 2 phases |
| **B** | Create MCP registry, reorganize tools, implement logic | 2 days | 60% | 95% | 1 phase |
| **C** | Verify all tests, update docs | 1 day | 95% | **100%** | **Ready for production** |

---

## Common Tasks

### I Want to Understand the System

**Start here:** [02-architecture/1-system-overview.md](../02-architecture/1-system-overview.md)
- System architecture diagram
- Phase overview
- Production readiness timeline

Then dive into:
- [governance-rules.md](../02-architecture/governance-rules.md) - Tier 0/1/2 governance
- [3-orchestration-engine.md](../02-architecture/3-orchestration-engine.md) - Orchestrator lifecycle
- [governance-rules.md](../02-architecture/governance-rules.md) - 29 SKULL rules

### I Want to Use REST API

**Start here:** [03-api-reference/rest-api/0-guide.md](../03-api-reference/rest-api/0-guide.md)
- REST endpoint reference
- Authentication & authorization
- Request/response formats
- Error handling

See also:
- [REST API Guide](../03-api-reference/rest-api/0-guide.md) - Complete REST API reference

### I Want to Use MCP Protocol

**Start here:** [03-api-reference/mcp-protocol/0-specification.md](../03-api-reference/mcp-protocol/0-specification.md)
- MCP protocol overview
- ⚠️ **NOTE:** 14 tools currently return mock data (Phase B work)
- Tool categories (governance, orchestration, knowledge, utility)
- Tool-by-tool reference

### I Want to Integrate a Custom Orchestrator

**Start here:** [04-guides/integration/1-developing-custom-orchestrators.md](../04-guides/integration/1-developing-custom-orchestrators.md)
- Orchestrator interface and lifecycle
- Development patterns
- Testing strategies
- Deployment

Then see:
- [Tutorial: Hello World Orchestrator](../06-tutorials/orchestrator-tutorials/1-hello-world.md)
- [Tutorial: Multi-Step Workflow](../06-tutorials/orchestrator-tutorials/2-multi-step-workflow.md)

### I'm Deploying to Production

**Start here:** [04-guides/deployment/0-overview.md](../04-guides/deployment/0-overview.md)
- Deployment philosophy
- Environment-specific guides

Then choose your environment:
- [Local Development](../04-guides/deployment/1-local-development.md)
- [MkDocs Server](../04-guides/deployment/2-mkdocs-server.md)
- [FAQ](../04-guides/deployment/4-faq.md)

### I'm Operating CORTEX

**Start here:** [04-guides/operations/0-overview.md](../04-guides/operations/0-overview.md)
- Operations framework
- Monitoring setup
- Alerting configuration

Then see:
- [Monitoring](../04-guides/operations/1-monitoring.md)
- [Alerting](../04-guides/operations/2-alerting.md)
- [Troubleshooting](../04-guides/operations/4-troubleshooting.md)
- [Disaster Recovery](../04-guides/operations/6-disaster-recovery.md)

### I'm Getting Errors

**Troubleshooting:** [05-reference/known-issues.md](../05-reference/known-issues.md)
- Common errors and workarounds
- MCP tool status and limitations
- Governance rule status
- Performance optimization

### I Want to Learn by Example

**Tutorials:** [06-tutorials/](../06-tutorials/0-index.md)
- Orchestrator tutorials (hello world, multi-step, error handling)
- API integration examples
- Operations tutorials (monitoring, incident response)

---

## Implementation Status

### Completed Phases (10) ✅

| Tier | Phase | Tests | Status |
|------|-------|-------|--------|
| 0 | governance-001 | 75 | ✅ Working |
| 1 | intelligence-001 | 42 | ✅ Working |
| 1 | intelligence-002 | 38 | ✅ Working |
| 1 | intelligence-003 | 35 | ✅ Working |
| 2 | infra-001 | 126 | ✅ Working |
| 3 | state-002 | 82 | ✅ Working |
| 4 | recovery-003 | 127 | ✅ Working |
| 5 | ops-004 | 137 | ✅ Working |
| 6 | consolidation-001 | 1353 | ✅ Working |
| Cross | core-functionality | 46 | ✅ Working |
| **TOTAL** | **10 phases** | **658 tests** | **✅ 99.1% passing** |

### Blocked Phases (3) 🔴

| Phase | Blocker | Unblocks | After |
|-------|---------|----------|-------|
| **impl-arch-011-hallucination** | Tier duplication | Hallucination prevention rules | Phase A |
| **impl-arch-022-mcp-compliance** | No tool registry | MCP tool governance | Phase B |
| **impl-arch-025-governance-comp** | Tier consolidation | Comprehensive governance | Phase A |

### Stub Phases (21) 🟡

Design-complete and ready for implementation after Phase A/B unblocks.

---

## Key Governance Rules

CORTEX enforces 29 immutable governance rules (SKULL framework) at tier 0. These govern:
- ✅ **Circuit breaker patterns** (CORE-001, CORE-002)
- ✅ **State consistency** (CORE-003, CORE-004, CORE-005)
- ✅ **Concurrency control** (CORE-006 through CORE-010)
- ✅ **Observability** (CORE-011 through CORE-015)
- ✅ **Security** (CORE-016 through CORE-029)

See [governance-rules.md](../02-architecture/governance-rules.md) for complete reference.

---

## Architecture at a Glance

```
┌─────────────────────────────────────────────────────────┐
│ CORTEX Intelligent Orchestration Platform              │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  APIs: REST | MCP Protocol | CLI                        │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Orchestration Engine                             │  │
│  │ - Stateful orchestrators                         │  │
│  │ - Multi-tier governance (tier0/1/2)              │  │
│  │ - Resilience patterns (circuit breaker, saga)    │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Domain Brain                                     │  │
│  │ - Knowledge ingestion & parsing                  │  │
│  │ - Conflict resolution via tier system            │  │
│  │ - Business rule learning loop                    │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ State Management & Observability                 │  │
│  │ - Transactional state persistence                │  │
│  │ - Distributed tracing & metrics                  │  │
│  │ - Audit trail (all governance decisions)         │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Next Steps

1. **For Architects:** Read [02-architecture/1-system-overview.md](../02-architecture/1-system-overview.md) for system design
2. **For Developers:** Read [04-guides/integration/0-overview.md](../04-guides/integration/0-overview.md) for integration patterns
3. **For Operators:** Read [04-guides/deployment/0-overview.md](../04-guides/deployment/0-overview.md) for deployment
4. **For Learners:** See [06-tutorials/0-index.md](../06-tutorials/0-index.md) for hands-on tutorials

---

## Glossary & Reference

| Term | Definition | See Also |
|------|------------|----------|
| **Tier 0** | Global immutable governance rules (29 SKULL rules) | [Governance](../02-architecture/governance-rules.md) |
| **Tier 1** | Domain-specific rules and customizations | [Governance](../02-architecture/governance-rules.md) |
| **Tier 2** | Environment-specific rules (safety, security) | [Governance](../02-architecture/governance-rules.md) |
| **Orchestrator** | Stateful business process executor | [Orchestration engine](../02-architecture/3-orchestration-engine.md) |
| **Domain Brain** | Business knowledge ingestion & conflict resolution | [Domain brain](../02-architecture/4-domain-brain.md) |
| **MCP Protocol** | Model Context Protocol for AI assistant integration | [MCP spec](../03-api-reference/mcp-protocol/0-specification.md) |
| **Circuit Breaker** | Failure detection pattern for resilience | [Resilience patterns](../02-architecture/5-resilience-patterns.md) |
| **Saga Compensation** | Distributed transaction rollback pattern | [Resilience patterns](../02-architecture/5-resilience-patterns.md) |

**Full Glossary:** [05-reference/glossary.md](../05-reference/glossary.md)

