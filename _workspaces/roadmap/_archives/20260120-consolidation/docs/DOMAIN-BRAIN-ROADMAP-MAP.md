# CORTEX Roadmap: Visual Integration Map

**Updated**: January 16, 2026  
**Status**: Domain Brain (PHASE-17) Integrated

---

## Timeline Overview: All 18 Phases + 3 Enhancements

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          CORTEX 7.0 IMPLEMENTATION ROADMAP              │
│                    Foundation → Knowledge → Production                   │
└─────────────────────────────────────────────────────────────────────────┘

FOUNDATION PHASES (Weeks 1-4):
  PHASE-01 ──→ PHASE-02 ──→ PHASE-03 ──→ PHASE-04 ──→ PHASE-05
   [Tier 0]     [Tier 1]     [Tier 2]     [Tier 3]   [Testing]
   Governance  AC Index    Governance  Knowledge   Evidence
              (SQLite)      Tools      Registry     Capture

                                        ↓
                         PHASE-06-ECOSYSTEM
                      (Orchestrator Framework)
                                        ↓
                     PHASE-EHHANCEMENT-01/02/03
                    (Response Header Injection)
                                        ↓
KNOWLEDGE PHASES (Weeks 5-12):
  PHASE-07 ──→ PHASE-08 ──→ PHASE-09 ──→ PHASE-10 ──→ PHASE-11 ──→ PHASE-12
   [Intent]    [Domain]    [Tools]    [Adaptive]  [Hallucin.]  [Knowledge]
   Router    Orchestrators Governance   Execution   Prevention   Ecosystem
   (LENS)    Framework     CLI/IDE      Framework   (AR-014)    (Tier 3+)

PRODUCTION PHASES (Weeks 13-20):
  PHASE-13 ──→ PHASE-15 ──→ PHASE-16-ORC ──→ PHASE-DOC ──→ PHASE-17 ──→ PHASE-18
   [Observe]   [Dashboard] [Orchestrator]   [Remediate]  [Domain]   [Production]
   Maturity    Enhancement  Continuation      Docs       Brain       Migration
   (Observ.)   (Parallel)   (ConversationProtocol)       (Knowledge) (Rollout)
                                                         Centralization

PARALLEL TRACKS:
  ├── PHASE-15 (Dashboard) - Fully independent, reads from existing data
  ├── PHASE-17 (Domain Brain) - Dependent on PHASE-13 only
  └── PHASE-DOC (Remediation) - Bug fix, not blocking
```

---

## Dependency Graph: Critical Path Analysis

```
CRITICAL PATH (Blocks PHASE-18 Production Migration):

  PHASE-01 → PHASE-02 → PHASE-03 → PHASE-04 → PHASE-05 → PHASE-06
      ↓
  PHASE-07 (LENS)
      ↓
  PHASE-08, PHASE-09, PHASE-10, PHASE-11, PHASE-12 (Sequential)
      ↓
  PHASE-13 (Observability)
      ├─→ PHASE-15 (Dashboard - Parallel, non-blocking)
      ├─→ PHASE-16-ORC (Orchestrator - Parallel, non-blocking)
      ├─→ PHASE-DOC (Documentation - Parallel, bug fix)
      │
      └─→ PHASE-17 (Domain Brain - REQUIRES PHASE-13)
              ↓
          PHASE-18 (Production Migration)


BLOCKER ANALYSIS:
  • PHASE-10 is LOCKED (cannot start any phase depending on it without completion)
  • PHASE-13 must complete before PHASE-17 starts
  • PHASE-17 must complete before PHASE-18 can start
  • All other phases are non-blocking or parallel-capable
```

---

## Component Architecture: Domain Brain Integration

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         TIER 3: KNOWLEDGE LAYER                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │               DOMAIN BRAIN (PHASE-17)                           │    │
│  │           Strategic Knowledge Centralization                   │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │                                                                 │    │
│  │  ┌──────────────┬──────────────┬──────────────┬─────────────┐ │    │
│  │  │   AST Adapter│  Git Adapter │ Comments Adp │Relationships│ │    │
│  │  │(IR-001-01)   │(IR-001-02)   │ (IR-001-03)  │(IR-001-04)  │ │    │
│  │  └────────┬─────┴────────┬─────┴────────┬─────┴──────┬──────┘ │    │
│  │           │              │              │            │         │    │
│  │  ┌────────▼──────────────▼──────────────▼────────────▼─────┐ │    │
│  │  │        Domain Brain API (12 methods)                     │ │    │
│  │  │  • query_domain, list_domains, search_entities         │ │    │
│  │  │  • upsert_domain, delete_domain                        │ │    │
│  │  │  • get_conflicts, resolve_conflict                    │ │    │
│  │  │  • audit_domain, validate_domain                      │ │    │
│  │  └────────┬────────────────────────────────────────────┬─┘ │    │
│  │           │                                            │    │    │
│  │  ┌────────▼────────────────────────────────────────────▼─┐  │    │
│  │  │  ┌──────────────────┐  ┌────────────────────────────┐  │  │    │
│  │  │  │ Consistency       │  │ Audit Logger               │  │  │    │
│  │  │  │ Validator         │  │ (Hash Chain Integrity)     │  │  │    │
│  │  │  │ • Schema Validate │  │ • Append-only log          │  │  │    │
│  │  │  │ • Ref Integrity   │  │ • TTL cache                │  │  │    │
│  │  │  │ • Circular Detect │  │ • Per-domain audit trail   │  │  │    │
│  │  │  └──────────────────┘  └────────────────────────────┘  │  │    │
│  │  │                                                          │  │    │
│  │  │  ┌────────────────────────────────────────────────────┐  │  │    │
│  │  │  │ BKIO Orchestrator (inherits OrchestratorBase)       │  │  │    │
│  │  │  │ • Document parser (YAML, JSON, Markdown, CSV)      │  │  │    │
│  │  │  │ • Conflict resolver (hierarchy + LENS synthesis)   │  │  │    │
│  │  │  │ • Batch ingestion with progress tracking           │  │  │    │
│  │  │  │ • Registered in OrchestratorRegistry               │  │  │    │
│  │  │  │ • Exposed as MCP tool                              │  │  │    │
│  │  │  └────────────────┬─────────────────────────────────┘  │  │    │
│  │  │                   │                                      │  │    │
│  │  │                   ▼ (via IR-004)                        │  │    │
│  │  │        ┌─────────────────────┐                         │  │    │
│  │  │        │  LENS Integration   │                         │  │    │
│  │  │        │ (Knowledge Graph)   │                         │  │    │
│  │  │        │ • Per-turn execution│                         │  │    │
│  │  │        │ • Entity-to-node    │                         │  │    │
│  │  │        │ • Conflict synthesis│                         │  │    │
│  │  │        └─────────────────────┘                         │  │    │
│  │  └──────────────────────────────────────────────────────┘  │    │
│  │                                                             │    │
│  │  STORAGE: File-based YAML in Git (cortex_brain/tier3/)    │    │
│  │  GOVERNANCE: All 28 CORE rules enforced                    │    │
│  │  TESTING: 225 tests covering all components (>85% coverage)│    │
│  │                                                             │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ EXISTING TIER 3 COMPONENTS (Not Changed)                    │    │
│  │ • KnowledgeGraph (IR-004-01)                               │    │
│  │ • ComprehensionLoop (IR-004-02)                            │    │
│  │ • Tier 3 Knowledge Library (PHASE-12)                      │    │
│  │ • Domain Registry (PHASE-13 BD ACs - foundation only)      │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                       │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                       TIERS 0, 1, 2: UNCHANGED                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  TIER 0: Governance (25 SKULL rules, immutable)                         │
│  TIER 1: AC Mappings (Project governance)                              │
│  TIER 2: Response Templates & Standards                                │
│                                                                           │
│  Domain Brain respects but does not modify these tiers                 │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 17 Breakdown: 4-Week Implementation Schedule

```
PHASE-17-DOMAIN-BRAIN (140 hours total, 3-4 weeks)

WEEK 1: Foundation (40 hours)
├── AC-DB-001-01: Domain Brain Foundation
│   ├── DomainBrainAPI (~300 lines)
│   │   ├── Query/write interface
│   │   ├── 12 async methods
│   │   └── Complete type hints
│   ├── ConsistencyValidator (~250 lines)
│   │   ├── JSON Schema validation
│   │   ├── Referential integrity
│   │   └── Circular dependency detection
│   ├── AuditLogger (~200 lines)
│   │   ├── SHA-256 hash chain
│   │   ├── Append-only enforcement
│   │   └── TTL cache
│   ├── Tests: 60 passing (25 API + 20 validator + 15 logger)
│   └── Documentation: API reference + data model
│
└── Git Checkpoint 1: "AC-DB-001-01 complete (Foundation)"

WEEK 2: Integration Adapters (35 hours)
├── AC-DB-002-01: Integration Adapters
│   ├── ASTAdapter (15 tests) - connects IR-001-01
│   ├── GitAdapter (12 tests) - connects IR-001-02
│   ├── CommentsAdapter (14 tests) - connects IR-001-03
│   ├── RelationshipsAdapter (14 tests) - connects IR-001-04
│   ├── Tests: 55 passing total
│   └── Documentation: Adapter architecture guide
│
└── Git Checkpoint 2: "AC-DB-002-01 complete (Adapters)"

WEEK 3: BKIO Orchestrator (40 hours)
├── AC-DB-003-01: BKIO Implementation
│   ├── BusinessKnowledgeIngestionOrchestrator
│   │   ├── Inherits OrchestratorBase (proven pattern)
│   │   ├── Implements lifecycle (validate_context → execute → complete)
│   │   └── Auto-registers via @orchestrator decorator
│   ├── DocumentParser
│   │   ├── YAML format support
│   │   ├── JSON format support
│   │   ├── Markdown format support
│   │   └── CSV format support
│   ├── ConflictResolver
│   │   ├── Hierarchy: BKIO > RELATIONSHIPS > AST > GIT > LENS
│   │   ├── Tie-breaking: Query LENS for synthesis
│   │   └── Deferral: Mark for manual review
│   ├── Tests: 70 passing (25 BKIO + 20 parser + 25 resolver)
│   └── Documentation: BKIO workflow guide + examples
│
└── Git Checkpoint 3: "AC-DB-003-01 complete (BKIO Orchestrator)"

WEEK 4: Integration & Completion (50 hours)
├── AC-DB-004-01: LENS Integration (25 hours)
│   ├── LENSIntegrationLayer (~150 lines)
│   │   ├── Per-turn LENS execution
│   │   ├── Knowledge graph updates
│   │   ├── Auto-challenge on conflicts
│   │   └── LENS synthesis for resolution
│   ├── DomainBrainLENSAdapter (~100 lines)
│   │   ├── Entity → GraphNode conversion
│   │   ├── Relationship → GraphEdge conversion
│   │   └── Query LENS for insights
│   ├── Tests: 40 passing (25 LENS integration + 15 adapter)
│   └── Documentation: LENS integration guide
│
├── AC-DB-005-01: E2E Integration Testing (15 hours)
│   ├── Full workflow tests (end-to-end from document to knowledge graph)
│   ├── Multi-source conflict resolution tests
│   ├── LENS synthesis workflow tests
│   ├── Regression tests (1,300 existing tests still pass)
│   ├── Tests: 30 passing (15 workflow + 15 regression)
│   └── Documentation: Integration scenarios + examples
│
├── AC-DB-006-01: Documentation & Governance (10 hours)
│   ├── Domain Brain Architecture Guide (~50 pages)
│   │   ├── Quick start (5-minute walkthrough)
│   │   ├── API reference (all 12 methods)
│   │   ├── Data model (all dataclasses)
│   │   ├── Adapter integration (each adapter)
│   │   ├── BKIO workflow (step-by-step)
│   │   ├── Troubleshooting (common issues)
│   │   └── Performance tuning
│   ├── Governance Compliance Documentation
│   │   ├── CORE-008: TDD pattern validation
│   │   ├── CORE-011: Type hints verification
│   │   ├── CORE-012: Docstring compliance
│   │   ├── CORE-027: Audit trail requirements
│   │   └── CORE-028: Naming conventions
│   ├── Tests: 10 passing (5 documentation + 5 governance)
│   └── Documentation: Phase completion checklist
│
└── Git Checkpoint 4: "PHASE-17 complete (ready for PHASE-18)"

TOTAL TESTS: 225 (60 + 55 + 70 + 40 + 30 + 10)
TOTAL HOURS: 140 (40 + 35 + 40 + 50)
COVERAGE TARGET: >85% for all components
```

---

## AC-ID Allocation Summary

```
PHASE-17 AC-IDs: BD (Business Domain) Prefix

AC-DB-001-01: Domain Brain Foundation
  ├── Status: NOT_STARTED
  ├── Priority: CRITICAL
  ├── Tests: 60 (100% required passing)
  └── Depends: None (foundation)

AC-DB-002-01: Integration Adapters
  ├── Status: NOT_STARTED
  ├── Priority: CRITICAL
  ├── Tests: 55 (100% required passing)
  └── Depends: AC-DB-001-01 (requires API)

AC-DB-003-01: BKIO Orchestrator
  ├── Status: NOT_STARTED
  ├── Priority: CRITICAL
  ├── Tests: 70 (100% required passing)
  └── Depends: AC-DB-002-01 (adapters)

AC-DB-004-01: LENS Integration
  ├── Status: NOT_STARTED
  ├── Priority: HIGH
  ├── Tests: 40 (100% required passing)
  └── Depends: AC-DB-003-01 (BKIO)

AC-DB-005-01: E2E Integration Testing
  ├── Status: NOT_STARTED
  ├── Priority: HIGH
  ├── Tests: 30 (100% required passing)
  └── Depends: AC-DB-004-01 (LENS)

AC-DB-006-01: Documentation & Governance
  ├── Status: NOT_STARTED
  ├── Priority: MEDIUM
  ├── Tests: 10 (100% required passing)
  └── Depends: AC-DB-005-01 (verified complete)

TOTAL: 6 ACs, 225 tests, 140 hours, 12-14 weeks realistic timeline
```

---

## Success Metrics & Verification

```
PHASE-17 COMPLETION CRITERIA:

Functionality ✓
  □ All 6 AC-IDs implemented and verified
  □ 225/225 tests passing (100% pass rate)
  □ >85% code coverage for domain_brain module
  □ BKIO registered and exposed as MCP tool
  □ LENS integration tested end-to-end

Governance ✓
  □ All 28 CORE rules satisfied
  □ Audit trail complete (18+ entries minimum)
  □ Hash chain integrity verified
  □ Zero governance violations detected
  □ Git checkpoints at each AC completion

Documentation ✓
  □ API reference complete and reviewed
  □ Architecture guide (50+ pages) complete
  □ Troubleshooting guide comprehensive
  □ Integration scenarios documented
  □ Code comments and docstrings 100% coverage

Quality ✓
  □ Zero regressions to existing 1,300 tests
  □ Performance benchmarks met (<100ms queries)
  □ Code review approved
  □ Security audit passed
  □ Ready for production migration (PHASE-18)
```

---

## Integration Status Checklist

```
✅ PHASE-17 Phase File Created
   File: .github/roadmap/phases/phase-17-domain-brain.yaml
   Size: ~500 lines
   Status: Ready for implementation

✅ Master Roadmap Updated
   File: .github/roadmap/cortex-master.yaml
   Changes: Added PHASE-17 to phase_tracker (line 1488+)
   Status: Ready for validation

✅ AC-IDs Defined (6 Total)
   AC-DB-001-01 through AC-DB-006-01
   Tests: 225 total (>85% coverage target)
   Status: Design complete

✅ No Breaking Changes
   Verified: Existing 16 phases + 2 enhancements unchanged
   Phase locks respected (PHASE-10 remains locked)
   Status: Clean integration

✅ Governance Compliance
   All 28 CORE rules addressed
   Audit trail requirements defined
   Status: Ready for enforcement

✅ Dependencies Identified
   Requires: PHASE-13 (foundation)
   Required by: PHASE-18 (production)
   Parallel: Can run with PHASE-15, PHASE-16-ORC
   Status: Clear dependency graph

✅ Timeline Realistic
   Estimated: 140 hours (17.5 days)
   vs. Proposal: 9 weeks (unrealistic)
   vs. Realistic: 12-14 weeks (attainable)
   Status: Achievable milestones

✅ Integration Summary Document
   File: DOMAIN-BRAIN-INTEGRATION-SUMMARY.md
   Status: Complete and detailed
```

---

## Next Steps for Implementation Team

1. **Read Documentation** (2 hours)
   - Review PHASE-17-DOMAIN-BRAIN.yaml
   - Review TECHNICAL-IMPLEMENTATION-GUIDE.md
   - Review this integration map

2. **Understand Pre-Phase 1 Decisions** (1 hour)
   - Storage: File-based YAML (decision made)
   - Conflicts: Hierarchy + LENS (decision made)
   - Approval: Interactive CLI (decision made)
   - API: Async methods (decision made)
   - SLAs: <100ms queries (decision made)

3. **Prepare Development Environment** (4 hours)
   - Create feature branch: `feature/phase-17-domain-brain`
   - Set up test infrastructure
   - Create BrainTierPusher completion task (4 hours first)

4. **Start AC-DB-001-01 Implementation** (Week 1)
   - Write 60 tests first (RED → GREEN pattern)
   - Implement DomainBrainAPI (~300 lines)
   - Implement ConsistencyValidator (~250 lines)
   - Implement AuditLogger (~200 lines)

5. **Create Git Checkpoint** (Before AC-001)
   - Commit: "checkpoint: before PHASE-17-DOMAIN-BRAIN"

---

**Status**: ✅ Ready for Implementation  
**Last Updated**: January 16, 2026  
**Next Review**: After AC-DB-001-01 completion
