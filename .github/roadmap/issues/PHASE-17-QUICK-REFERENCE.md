# PHASE-17 DOMAIN BRAIN: Quick Reference Card

**Print This. Post on Your Wall.**

---

## THE MISSION

Consolidate 5 knowledge sources (AST, Git, Comments, Relationships, Business Documents) into a unified **Domain Brain** - a queryable, conflict-resolving Tier 3 knowledge system.

**Timeline**: 140 hours (12-14 weeks) across 4 weeks

---

## THE PHASES

```
WEEK 1  ► AC-DB-001-01: Foundation (40h, 60 tests)
WEEK 2  ► AC-DB-002-01: Adapters (35h, 55 tests)  
WEEK 3  ► AC-DB-003-01: BKIO Orchestrator (40h, 70 tests)
WEEK 4  ► AC-DB-004/005/006: Integration (50h, 80 tests)
```

---

## KEY FILES

| File | Purpose |
|------|---------|
| `.github/roadmap/phases/phase-17-domain-brain.yaml` | Full spec (500 lines) |
| `TECHNICAL-IMPLEMENTATION-GUIDE.md` | Pre-Phase 1 decisions |
| `EXECUTION-CHECKLIST.md` | Week-by-week tasks |

---

## PRE-PHASE 1 DECISIONS (Already Made)

```
✓ Storage: File-based YAML (cortex-brain/tier3/)
✓ Conflict Hierarchy: BKIO > RELATIONSHIPS > AST > GIT > LENS
✓ Approval: Interactive CLI workflow
✓ API: 12 async methods (query, upsert, validate, etc.)
✓ Performance: <100ms queries, <5s batch ingestion
```

---

## THE 6 ACs

```
AC-DB-001-01: Foundation
├─ DomainBrainAPI (12 methods, 300 lines)
├─ ConsistencyValidator (250 lines)
├─ AuditLogger with hash chain (200 lines)
└─ 60 tests ✓

AC-DB-002-01: Adapters  
├─ ASTAdapter (connects IR-001-01)
├─ GitAdapter (connects IR-001-02)
├─ CommentsAdapter (connects IR-001-03)
├─ RelationshipsAdapter (connects IR-001-04)
└─ 55 tests ✓

AC-DB-003-01: BKIO Orchestrator
├─ Inherits OrchestratorBase (proven pattern)
├─ Document parser (YAML, JSON, Markdown, CSV)
├─ Conflict resolver (hierarchy + LENS)
├─ Auto-registered as MCP tool
└─ 70 tests ✓

AC-DB-004-01: LENS Integration
├─ Connect to IR-004 Knowledge Graph
├─ Per-turn execution
├─ Entity→GraphNode conversion
└─ 40 tests ✓

AC-DB-005-01: E2E Testing
├─ Full workflow validation
├─ Multi-source conflict resolution
├─ Regression tests (all 1,300 existing pass)
└─ 30 tests ✓

AC-DB-006-01: Documentation
├─ Architecture guide (50+ pages)
├─ API reference
├─ Troubleshooting guide
├─ Governance compliance
└─ 10 tests ✓

TOTAL: 225 TESTS ✓ (100% pass required)
```

---

## DEPENDENCIES

```
REQUIRES: PHASE-13-OBSERVABILITY-MATURITY
  └─ Domain registry foundation (BD ACs)

PROVIDES: Foundation for PHASE-18-PRODUCTION-MIGRATION
  └─ Domain Brain graduation

LEVERAGES:
  ├─ OrchestratorBase (PHASE-06)
  ├─ IR-001-01/02/03/04 (PHASE-07) ← 4 intelligence sources
  ├─ IR-004 Knowledge Graph (PHASE-07)
  └─ All governance tools (PHASE-09)
```

---

## GOVERNANCE RULES (28 CORE)

**TDD Pattern**
- Write tests FIRST (RED → GREEN)
- 225 tests minimum

**Type Safety**
- Type hints on ALL functions
- Type check before commit

**Documentation**  
- Docstrings (Google style) on all public APIs
- Comments on complex logic

**Audit Trail**
- AC_START → AC_EXECUTE → AC_COMPLETE
- 6 ACs × 3 entries = 18 minimum audit entries
- Hash chain integrity verified

**Git Discipline**
- Checkpoint before each major action
- Clean commit messages

---

## TESTING BREAKDOWN

```
AC-DB-001-01 (60 tests)
├─ API: 25 tests
├─ Validator: 20 tests
└─ Logger: 15 tests

AC-DB-002-01 (55 tests)
├─ AST: 15 tests
├─ Git: 12 tests
├─ Comments: 14 tests
└─ Relationships: 14 tests

AC-DB-003-01 (70 tests)
├─ BKIO: 25 tests
├─ Parser: 20 tests
└─ Resolver: 25 tests

AC-DB-004-01 (40 tests)
├─ LENS: 25 tests
└─ Adapter: 15 tests

AC-DB-005-01 (30 tests)
├─ Workflow: 15 tests
└─ Regression: 15 tests

AC-DB-006-01 (10 tests)
├─ Documentation: 5 tests
└─ Governance: 5 tests

COVERAGE TARGET: >85% for all components
PASS REQUIREMENT: 225/225 (100%)
```

---

## GIT CHECKPOINTS

```bash
# Before AC-001
git commit -m "checkpoint: before PHASE-17-DOMAIN-BRAIN"

# After AC-001
git commit -m "checkpoint: AC-DB-001-01 complete (Foundation)"

# After AC-002
git commit -m "checkpoint: AC-DB-002-01 complete (Adapters)"

# After AC-003
git commit -m "checkpoint: AC-DB-003-01 complete (BKIO)"

# After AC-004
git commit -m "checkpoint: AC-DB-004-01 complete (LENS)"

# After AC-005
git commit -m "checkpoint: AC-DB-005-01 complete (E2E)"

# After AC-006 (Phase Complete)
git commit -m "checkpoint: PHASE-17 complete (ready PHASE-18)"
git tag -a v17.0 -m "PHASE-17: Domain Brain Complete"
```

---

## SUCCESS CRITERIA (Phase Complete When)

- [x] 6/6 ACs implemented
- [x] 225/225 tests passing
- [x] >85% code coverage
- [x] Audit trail complete (18+ entries, hash chain verified)
- [x] BKIO in OrchestratorRegistry + MCP tool
- [x] LENS integration working
- [x] Zero governance violations
- [x] Documentation complete
- [x] Git history clean

---

## PERFORMANCE TARGETS

```
Query latency:         <100ms
Batch ingestion:       <5s for 100+ docs
Validation overhead:   <50ms
Audit logging:         <10ms per entry
API method latency:    <50ms average
```

---

## ARCHITECTURE PATTERN

```
BKIO Orchestrator
  ├─ Inherits: OrchestratorBase (PHASE-06)
  ├─ Registers: @orchestrator decorator (auto-discovery)
  ├─ Exposes: MCP tools (governance context injected)
  ├─ Uses: 4 IR-001-XX sources (intelligence layers)
  ├─ Resolves: Conflicts via hierarchy + LENS
  └─ Tracks: Full audit trail with hash chain

Connection to LENS (IR-004):
  ├─ Per-turn execution (not cached)
  ├─ Domain entities → GraphNodes
  ├─ Relationships → GraphEdges
  └─ Conflict synthesis via LENS reasoning
```

---

## THE 4 INTELLIGENCE ADAPTERS

```
ASTAdapter (IR-001-01)
  └─ Queries AST Intelligence for function/class metadata
  └─ Maps to domain entities
  └─ Extracts semantic relationships

GitAdapter (IR-001-02)
  └─ Queries Git commit history
  └─ Extracts blame information
  └─ Rebuilds domain evolution timeline

CommentsAdapter (IR-001-03)
  └─ Parses docstrings & comments
  └─ Extracts design decisions
  └─ Links to domain entities

RelationshipsAdapter (IR-001-04)
  └─ Queries code dependency graph
  └─ Extracts service dependencies
  └─ Maps domain interactions
```

---

## CONFLICT RESOLUTION HIERARCHY

```
Priority Order (Highest to Lowest):

1. BKIO (Business Knowledge)        ← Highest priority
2. RELATIONSHIPS (Code Graph)       ← Factual relationships
3. AST (Static Analysis)            ← Factual but limited
4. GIT (Commit History)             ← Factual but coarse
5. LENS (Synthesized)               ← Synthesized (lowest)

If Same Priority = Defer to Manual Review

Pseudocode:
  if source_A.priority > source_B.priority:
      use source_A
  elif source_A.priority == source_B.priority:
      defer_to_manual_review()
  else:
      use source_B
```

---

## STARTING AC-001: First Steps

```
1. Create tests/ directory for Domain Brain tests
2. Write 60 tests (RED state)
3. Run tests (all fail)
4. Implement code:
   ├─ DomainBrainAPI (~300 lines)
   ├─ ConsistencyValidator (~250 lines)
   ├─ AuditLogger (~200 lines)
5. Run tests (GREEN state)
6. Code review
7. Git checkpoint
8. Continue to AC-002
```

---

## DECISION CHECKLIST: Pre-Phase 1

Before starting, verify:

- [x] Storage mechanism: YAML files in Git (DECIDED)
- [x] Conflict resolution: Hierarchy + LENS (DECIDED)
- [x] Approval workflow: Interactive CLI (DECIDED)
- [x] API design: 12 async methods (DECIDED)
- [x] Performance targets: <100ms queries (DECIDED)

**If these change, escalate immediately!**

---

## DOCUMENTS YOU NEED TO READ

**Essential (Before Starting)**:
1. `phase-17-domain-brain.yaml` (this phase spec)
2. `TECHNICAL-IMPLEMENTATION-GUIDE.md` (pre-Phase 1 decisions)
3. This card ← You are here

**Reference (As Needed)**:
4. `EXECUTION-CHECKLIST.md` (week-by-week tasks)
5. `DOMAIN-BRAIN-INTEGRATION-SUMMARY.md` (executive overview)
6. `DOMAIN-BRAIN-ROADMAP-MAP.md` (visual timeline)

**Background (Optional)**:
7. `EXECUTIVE-SUMMARY-issue-report-02.md` (5-min decision summary)
8. `REVIEW-issue-report-02.md` (30-min detailed analysis)

---

## RED FLAGS 🚩

**Stop and escalate if:**

1. 🚩 Phase requirements change mid-week
2. 🚩 Test coverage drops below 80%
3. 🚩 Query latency exceeds 100ms
4. 🚩 Git checkpoint not created at AC boundary
5. 🚩 Governance rules violated
6. 🚩 Breaking changes to existing phases
7. 🚩 Regressions in existing test suite (1,300+ tests)
8. 🚩 Audit trail incomplete (missing START/EXECUTE/COMPLETE)

---

## PHASE MILESTONES

```
Week 1: ✓ FOUNDATION (AC-001, 60 tests)
Week 2: ✓ ADAPTERS (AC-002, 55 tests)
Week 3: ✓ BKIO (AC-003, 70 tests)
Week 4: ✓ INTEGRATION (AC-004/005/006, 80 tests)

TOTAL: 225 tests, 140 hours
COMPLETION: Ready for PHASE-18-PRODUCTION-MIGRATION
```

---

## QUICK CONTACTS

**Questions About:**

- Architecture Design → See phase-17-domain-brain.yaml
- Pre-Phase 1 Decisions → See TECHNICAL-IMPLEMENTATION-GUIDE.md
- Weekly Tasks → See EXECUTION-CHECKLIST.md
- Timeline/Dependencies → See DOMAIN-BRAIN-ROADMAP-MAP.md
- Integration/Governance → See DOMAIN-BRAIN-INTEGRATION-SUMMARY.md

---

## KEY METRICS

```
Hours/Week:        35-40 (sustainable)
Tests/Week:        60+ (increasing)
Code Coverage:     >85% target
Git Commits:       1 per AC (clean history)
Documentation:     100% of public APIs
Governance Rules:  28/28 CORE rules (zero violations)
```

---

## REMEMBER

```
✓ This is ADDITIVE (no breaking changes)
✓ This is PROVEN (uses established patterns)
✓ This is REALISTIC (140h, not 108h)
✓ This is TESTED (225 tests, >85% coverage)
✓ This is GOVERNANCE-COMPLIANT (all 28 CORE rules)
✓ This is READY (pre-Phase 1 decisions made)

You have everything you need to succeed.

Let's build the Domain Brain! 🧠
```

---

**Phase**: PHASE-17-DOMAIN-BRAIN  
**Status**: Ready for Implementation  
**Last Updated**: January 16, 2026  
**Print Date**: _______________  
