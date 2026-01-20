# Quick Reference Guide

**CORTEX Status:** ✅ 100% Definition of Ready | 🔴 36% Production Ready (→ 100% in 4 days)  
**Last Updated:** 2026-01-20

---

## I'm New - Where Do I Start?

1. **Read This Page** - You're here! Quick overview of key information
2. **Installation:** [01-getting-started/0-installation.md](../01-getting-started/0-installation.md)
3. **First Steps:** [01-getting-started/1-quickstart.md](../01-getting-started/1-quickstart.md)
4. **Architecture:** [02-architecture/0-overview.md](../02-architecture/0-overview.md)

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

## What's Working (36%)

✅ Infrastructure resilience (connections, circuit breakers, retry, graceful degradation)  
✅ State management & concurrency (transactional, optimistic locking, lock-free registry)  
✅ Fault tolerance & recovery (saga compensation, orphan cleanup, automatic repair)  
✅ Production observability (JSON logging, Prometheus, distributed tracing, health checks)  
✅ 10 completed phases with 658 passing tests

---

## What's Blocking (4 Critical Issues)

| Issue | Impact | Fix Timeline | Details |
|-------|--------|--------------|---------|
| **Tier duplication** | Breaks governance (cortex/brain + cortex_brain) | Phase A (1 day) | [See architecture overview](../02-architecture/0-overview.md) |
| **MCP tools scattered** | No tool discovery/registry (14 tools, no categorization) | Phase B (2 days) | [See API reference](../03-api-reference/0-overview.md) |
| **Hallucination prevention wrong location** | Not integrated into tier system (Python files vs YAML) | Phase A (1 day) | [See governance](../02-architecture/2-multi-tier-architecture.md) |
| **cortex/brain duplicates cortex_brain** | Architectural confusion (35+ duplicate files) | Phase A (1 day) | [See remediation guide](../04-guides/advanced/0-remediation-phases.md) |

---

## Common Tasks

### I Want to Understand the System

**Start here:** [02-architecture/0-overview.md](../02-architecture/0-overview.md)
- System architecture diagram
- 34 phases overview
- 4 critical issues and fixes
- Production readiness timeline

Then dive into:
- [2-multi-tier-architecture.md](../02-architecture/2-multi-tier-architecture.md) - Tier 0/1/2 governance
- [3-orchestration-engine.md](../02-architecture/3-orchestration-engine.md) - Orchestrator lifecycle
- [governance-rules.md](../02-architecture/governance-rules.md) - 29 SKULL rules

### I Want to Use REST API

**Start here:** [03-api-reference/rest-api/0-guide.md](../03-api-reference/rest-api/0-guide.md)
- REST endpoint reference
- Authentication & authorization
- Request/response formats
- Error handling

See also:
- [orchestrators.md](../03-api-reference/rest-api/orchestrators.md) - Orchestrator API
- [domains.md](../03-api-reference/rest-api/domains.md) - Domain API
- [governance.md](../03-api-reference/rest-api/governance.md) - Governance API

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
- [Staging Deployment](../04-guides/deployment/2-staging-deployment.md)
- [Production Deployment](../04-guides/deployment/3-production-deployment.md)
- [Azure Deployment](../04-guides/deployment/4-azure-deployment.md)

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

1. **For Architects:** Read [02-architecture/0-overview.md](../02-architecture/0-overview.md) for system design
2. **For Developers:** Read [04-guides/integration/0-overview.md](../04-guides/integration/0-overview.md) for integration patterns
3. **For Operators:** Read [04-guides/deployment/0-overview.md](../04-guides/deployment/0-overview.md) for deployment
4. **For Learners:** See [06-tutorials/0-index.md](../06-tutorials/0-index.md) for hands-on tutorials

---

## Glossary & Reference

| Term | Definition | See Also |
|------|------------|----------|
| **Tier 0** | Global immutable governance rules (29 SKULL rules) | [Governance](../02-architecture/governance-rules.md) |
| **Tier 1** | Domain-specific rules and customizations | [Multi-tier arch](../02-architecture/2-multi-tier-architecture.md) |
| **Tier 2** | Environment-specific rules (safety, security) | [Multi-tier arch](../02-architecture/2-multi-tier-architecture.md) |
| **Orchestrator** | Stateful business process executor | [Orchestration engine](../02-architecture/3-orchestration-engine.md) |
| **Domain Brain** | Business knowledge ingestion & conflict resolution | [Domain brain](../02-architecture/7-domain-brain.md) |
| **MCP Protocol** | Model Context Protocol for AI assistant integration | [MCP spec](../03-api-reference/mcp-protocol/0-specification.md) |
| **Circuit Breaker** | Failure detection pattern for resilience | [Resilience patterns](../02-architecture/5-resilience-patterns.md) |
| **Saga Compensation** | Distributed transaction rollback pattern | [Resilience patterns](../02-architecture/5-resilience-patterns.md) |

**Full Glossary:** [05-reference/glossary.md](../05-reference/glossary.md)

