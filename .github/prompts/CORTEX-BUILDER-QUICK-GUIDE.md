# CORTEX Issue Remediation Pattern - Quick Visual Guide

## The 5-Stage Lifecycle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ISSUE MANAGEMENT LIFECYCLE                           │
└─────────────────────────────────────────────────────────────────────────────┘

STAGE 1: DISCOVERY
├─ Issue identified via code review, testing, or architecture validation
├─ Output: .github/roadmap/issues/issue-report-NN.yaml
└─ Format: YAML with executive summary, critical issues, evidence

           ↓

STAGE 2: HOLISTIC REVIEW
├─ Read ENTIRE cortex-master.yaml (not sections)
├─ Read ENTIRE issue-report-NN.yaml (not summaries)
├─ Cross-reference implementation:
│  ├─ Grep for mentioned components
│  ├─ Check audit trail evidence
│  └─ Verify tests exist
├─ Decision matrix:
│  ├─ Misunderstanding? → ACCEPT-KNOWN
│  ├─ Already planned? → DEFER to PHASE-XX
│  ├─ Blocks production? → REMEDIATION (create AC-REM-XXX-XX)
│  ├─ Low priority? → DEFER to future phase
│  └─ Architectural? → PHASE-ARCHITECTURE-FIX
└─ Output: Clear decision document

           ↓

STAGE 3: REMEDIATION PLANNING (if REMEDIATION decided)
├─ Create AC-REM-XXX-XX acceptance criteria
│  ├─ AC-REM-001-01: [Fix aspect 1]
│  ├─ AC-REM-001-02: [Fix aspect 2]
│  └─ AC-REM-001-03: [Validation/audit]
├─ Add to cortex-master.yaml phase_tracker
├─ Create phase YAML: PHASE-ISSUE-XXX-REMEDIATION.yaml
├─ Link to audit trail requirements (START/EXECUTE/COMPLETE)
└─ Output: Phase YAML with concrete testable ACs

           ↓

STAGE 4: IMPLEMENTATION
├─ Follow standard phase workflow:
│  ├─ Create tests first (RED state)
│  ├─ Implement code (GREEN state)
│  ├─ Audit logging: AC_START → AC_EXECUTE → AC_COMPLETE
│  ├─ Hash chain verification
│  ├─ Governance rule enforcement
│  └─ 100% test pass rate
├─ Optional: Create specialized agent if complex
└─ Output: All remediation ACs completed with audit trail

           ↓

STAGE 5: CLOSURE
├─ Verify remediation complete:
│  ├─ All ACs: status = COMPLETED
│  ├─ Tests: 100% passing
│  ├─ Audit: START/EXECUTE/COMPLETE entries present
│  ├─ Hash chain: Unbroken
│  └─ Governance: 0 violations
├─ Rename issue file:
│  └─ issue-report-NN.yaml → issue-report-NN-done.yaml
├─ Update cortex-master.yaml:
│  └─ Move to resolved_issues section
└─ Reference in phase completion summary

```

## Decision Matrix Visual

```
┌────────────────────────────────────────────────────────────────────────────┐
│  ISSUE FINDING                   │  VERIFICATION              │  DECISION │
├────────────────────────────────────────────────────────────────────────────┤
│ "Feature X not implemented"      │ Find in architecture_      │  DEFER to │
│                                  │ decisions in master YAML   │  PHASE-XX │
├────────────────────────────────────────────────────────────────────────────┤
│ "Rule Y not enforced"            │ Check governance.db audit  │  ACCEPT-  │
│                                  │ logs, verify tests exist   │  KNOWN    │
├────────────────────────────────────────────────────────────────────────────┤
│ "AST scanning not used"          │ Grep for ASTIntelligence   │ REMEDIATE │
│ (blocks Intent Router)           │ Engine, check phase_tracker│ (AC-REM-) │
├────────────────────────────────────────────────────────────────────────────┤
│ "Performance is slow"            │ Benchmark real vs claimed, │  DEFER to │
│                                  │ no blocking impact         │  PHASE-20 │
├────────────────────────────────────────────────────────────────────────────┤
│ "Architecture fundamentally      │ Deep analysis of design,   │  PHASE-   │
│  flawed"                         │ impact on phases           │  ARCH-FIX │
└────────────────────────────────────────────────────────────────────────────┘
```

## File Organization

```
.github/
│
├─ prompts/
│  ├─ cortex-builder.prompt.md
│  │  └─ [MAIN] References issue remediation pattern
│  │
│  ├─ cortex-builder-issue-remediation-pattern.md
│  │  └─ [NEW] Complete 5-stage pattern documentation
│  │
│  ├─ CORTEX-BUILDER-ENHANCEMENT-SUMMARY.md
│  │  └─ [NEW] Overview + benefits
│  │
│  └─ CORTEX-BUILDER-INTEGRATION-GUIDE.md
│     └─ [NEW] File structure + integration points
│
├─ roadmap/
│  ├─ cortex-master.yaml
│  │  └─ [UPDATED] Add resolved_issues tracking section
│  │
│  ├─ issues/
│  │  ├─ issue-report-01.yaml                    (active)
│  │  ├─ issue-report-02.yaml                    (active)
│  │  ├─ issue-report-01-done.yaml               (closed)
│  │  └─ issue-report-02-done.yaml               (closed)
│  │
│  └─ phases/
│     ├─ phase-13.yaml                           (existing)
│     ├─ phase-issue-001-remediation.yaml        (NEW if needed)
│     └─ phase-issue-002-remediation.yaml        (NEW if needed)
│
└─ agents/
   ├─ cortex-builder.md                          (existing)
   ├─ cortex-review-governance.md                (existing)
   └─ cortex-issue-resolver-ast.md               (NEW if complex)
```

## Remediation AC Naming Convention

```
AC-REM-XXX-YY

Where:
  REM = REMediation (fixed prefix)
  XXX = Issue number (001, 002, 003...)
  YY  = AC count within issue (01, 02, 03...)

Examples:
  AC-REM-001-01  → First AC for Issue-001 remediation
  AC-REM-001-02  → Second AC for Issue-001 remediation
  AC-REM-002-01  → First AC for Issue-002 remediation
```

## Audit Trail Per Remediation AC

```
AC-REM-001-01  (ASTIntelligenceEngine integration)
├─ AC_START
│  └─ timestamp: 2026-01-16T14:00:00
│     message: "Remediation implementation started"
│
├─ AC_EXECUTE (multiple)
│  ├─ Test RED: test_intent_router_ast_integration FAILING
│  ├─ Implementation: Modified InteractionOrchestrator.comprehend_request()
│  ├─ Test GREEN: test_intent_router_ast_integration PASSING
│  ├─ Audit check: Governance rules enforced
│  └─ timestamp: 2026-01-16T14:15:00
│
└─ AC_COMPLETE
   └─ timestamp: 2026-01-16T14:30:00
      message: "AC-REM-001-01 verified complete with 4 tests passing"
      hash: "abc123def456..."
      previous_hash: "xyz789..."
```

## Agent Creation Decision Tree

```
                          Issue Needs Fixing?
                                 │
                    ┌────────────┴────────────┐
                    NO                        YES
                    │                         │
            ACCEPT-KNOWN                  Complexity?
            or DEFER                      │
                                    ┌─────┴─────┐
                                    │           │
                            Simple  │           │ Complex
                            (1-2ph) │           │ (3+ phases)
                                    │           │
                              No    │           │    YES
                            Agent   │           │
                           Needed   │      CREATE AGENT
                                    │   cortex-issue-XX.md
                                    │
                                    Create
                                   AC-REM-
                                   XXX-XX
```

## Closure Process Visual

```
┌──────────────────────────────────────────────────────────────┐
│  Issue Remediation Complete?                                 │
│  ✓ All ACs = COMPLETED                                       │
│  ✓ Tests = 100% passing                                      │
│  ✓ Audit entries = 3+ per AC                                 │
│  ✓ Hash chain = Unbroken                                     │
│  ✓ Governance violations = 0                                 │
└──────────────────────────────────────────────────────────────┘
              │
              │ YES
              ↓
┌──────────────────────────────────────────────────────────────┐
│  STEP 1: Rename Issue File                                   │
│                                                              │
│  issue-report-01.yaml                                        │
│           ↓                                                  │
│  issue-report-01-done.yaml  ← Visual closure marker          │
└──────────────────────────────────────────────────────────────┘
              │
              ↓
┌──────────────────────────────────────────────────────────────┐
│  STEP 2: Update cortex-master.yaml                           │
│                                                              │
│  pending_issues:                                             │
│    - ISSUE-001: AST Scanning    ✗ (remove)                  │
│                                                              │
│  resolved_issues:                                            │
│    - ISSUE-001: AST Scanning    ✓ (add)                     │
│      status: RESOLVED                                        │
│      resolution_date: 2026-01-16                            │
│      remediation_acs: 3                                      │
│      tests_passing: 12                                       │
│      audit_entries: 9                                        │
└──────────────────────────────────────────────────────────────┘
              │
              ↓
┌──────────────────────────────────────────────────────────────┐
│  STEP 3: Phase Completion Reference                          │
│                                                              │
│  phase_completion:                                           │
│    resolved_issues:                                          │
│      - ISSUE-001: AST Scanning Integration                   │
│        remediation_acs: [AC-REM-001-01, 02, 03]             │
│        status: RESOLVED                                      │
│        verification_date: 2026-01-16T14:30:00Z              │
└──────────────────────────────────────────────────────────────┘
              │
              ↓
         ✓ CLOSED
```

## Quick Reference: When to Use Each Decision

```
ACCEPT-KNOWN
├─ Issue finding is based on misunderstanding
├─ Feature is already implemented (differently than claimed)
├─ Working as designed per architecture decisions
└─ Action: Document why it's not an issue, close

DEFER
├─ Issue is real but already planned in PHASE-XX
├─ Issue is low priority
├─ Issue doesn't block current/near-term work
└─ Action: Cross-reference future phase, close

REMEDIATION
├─ Issue is real AND blocks current/critical path
├─ Issue is architectural and production-blocking
├─ Issue impacts governance enforcement
├─ Action: Create AC-REM-XXX-XX, execute phase workflow

ARCHITECTURE-FIX
├─ Issue reveals fundamental design flaw
├─ Issue impacts multiple phases negatively
├─ Issue requires reconsideration of core patterns
└─ Action: Create PHASE-ARCHITECTURE-FIX, analysis-heavy
```

---

**Pattern Benefits**:
- ✓ Holistic (reads full context, not sections)
- ✓ Efficient (quick decision matrix, no ambiguity)
- ✓ Trackable (AC-IDs, audit trail, renamed files)
- ✓ Reproducible (documented 5-stage lifecycle)
- ✓ Scalable (agent option for complex domains)
