# CORTEX Agent Architecture Diagram

**Version**: 2.0 (2026-01-18)  
**Status**: Complete with Gap Detection Integration

---

## System Architecture (ASCII Diagram)

```
┌───────────────────────────────────────────────────────────────────────────┐
│                         CORTEX Master Control                              │
│                      (CORTEX.prompt.md - Orchestrator)                    │
│                                                                             │
│  Intent → Route to Agent → Execute → Verify → Report → Update Roadmap    │
└───────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        v                           v                           v
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────────┐
│  BUILDER AGENT   │      │  PLANNER AGENT   │      │ GAP DETECTION AGENT  │
│ (Implementation) │      │ (Planning)       │      │ (NEW - Verification) │
│                  │      │                  │      │                      │
│ Responsibilities:│      │ Responsibilities:│      │ Responsibilities:    │
│ • Implement code │      │ • Analyze status │      │ • Design check       │
│ • TDD + tests    │      │ • Plan next ACs  │      │ • Implementation chk │
│ • Governance     │      │ • Track progress │      │ • Exposure check     │
│ • Audit logging  │      │ • Gap inventory  │      │ • Governance verify  │
│ • Phase 1.5:     │      │ • Compliance     │      │ • Documentation chk  │
│   GAP CHECK ✓    │      │   reporting      │      │                      │
└────────┬─────────┘      └────────┬─────────┘      └──────────┬───────────┘
         │                         │                           │
         └────────────┬────────────┴───────────┬────────────────┘
                      │                       │
                      v                       v
            ┌─────────────────────────────────────────┐
            │   Single Source of Truth (SSOT)         │
            │                                         │
            │  1. cortex-master.yaml                  │
            │     - phase_tracker (AC status)         │
            │     - ac_breakdown (counts)             │
            │     - completion_percentage             │
            │                                         │
            │  2. cortex-brain/state/governance.db    │
            │     - audit_log (events)                │
            │     - entry_hash (chain integrity)      │
            │                                         │
            │  3. cortex-brain/tier0/governance/      │
            │     - core-rules.yaml (28 rules)        │
            │     - phase-enforcement-map.yaml        │
            │     - ac-validation-checklist.yaml      │
            └─────────────────────────────────────────┘
                      │                       │
        ┌─────────────┼───────────┬──────────┼─────────────┐
        │             │           │          │             │
        v             v           v          v             v
   ┌─────────┐  ┌──────────┐ ┌────────┐ ┌──────────┐ ┌─────────┐
   │REVIEW   │  │REVIEW    │ │REVIEW  │ │REVIEW    │ │REVIEW   │
   │GOVER-   │  │BRITTL-   │ │HALLUC- │ │DEBT      │ │ASSUMP-  │
   │NANCE    │  │ENESS     │ │INATION │ │ANALYSIS  │ │TIONS    │
   │         │  │          │ │        │ │          │ │         │
   │Verifies:│  │Finds:    │ │Detects:│ │Identifies│ │Validates│
   │• CORE   │  │• Edge    │ │• AI    │ │• Unused  │ │• Assump-│
   │  rules  │  │  cases   │ │  risks │ │  code    │ │  tions  │
   │• Audit  │  │• Struct. │ │• Output│ │• Debt    │ │• Method │
   │  trail  │  │  weak-   │ │  issues│ │• Duplic. │ │  (NEW)  │
   │• Hash   │  │  nesses  │ │        │ │  code    │ │         │
   │  chain  │  │• Brittl. │ │        │ │• Tech    │ │         │
   │• Gap    │  │  code    │ │        │ │  debt    │ │         │
   │  verify │  │          │ │        │ │          │ │         │
   │ (NEW)   │  │          │ │        │ │          │ │         │
   └─────────┘  └──────────┘ └────────┘ └──────────┘ └─────────┘
        │             │           │          │             │
        └─────────────┼───────────┴──────────┼─────────────┘
                      │                      │
                      v                      v
            ┌──────────────────────────────────┐
            │  cortex-review-enhanced.prompt   │
            │  (v2.1 Review Orchestrator)      │
            │                                  │
            │  Pre-review validation:          │
            │  • Gate 0A: Data freshness       │
            │  • Gate 0B: Test fixture filter  │
            │  • Gate 0C: Assumption verify    │
            │                                  │
            │  Core review:                    │
            │  • Call all 5 review agents      │
            │  • Aggregate findings            │
            │  • Grade evidence (A/B/C)        │
            │  • Find root causes (6 types)    │
            │  • Check for DESIGN-BUILD gaps   │
            │    (NEW - mandatory check)       │
            │                                  │
            │  Post-review:                    │
            │  • Generate finding report       │
            │  • Create remediation ACs        │
            │  • Schedule new phases           │
            └──────────────────────────────────┘
                      │
                      v
            ┌──────────────────────────┐
            │  Final Output & Report   │
            │                          │
            │  • Finding inventory     │
            │  • Evidence grades       │
            │  • Root cause analysis   │
            │  • Remediation plan      │
            │  • Gap remediation path  │
            │    (e.g., Phase-22)      │
            │  • Updated roadmap       │
            └──────────────────────────┘
                      │
                      v
            ┌──────────────────────────┐
            │ UPDATE cortex-master.yaml│
            │                          │
            │  • phase_tracker updated │
            │  • new ACs scheduled     │
            │  • new phases created    │
            │  • timeline adjusted     │
            └──────────────────────────┘
```

---

## Data Flow: AC-ID Lifecycle with Gap Detection

```
START AC-IMPLEMENTATION
        │
        v
   BUILDER LOADS cortex-master.yaml
   BUILDER LOADS governance.db
   BUILDER LOADS core-rules.yaml
        │
        v
   ┌─ PHASE 0: PRE-START
   │  • Git checkpoint
   │  • Log AC_START to audit
   │
   ├─ PHASE 1: IMPLEMENTATION (with Continuous Validation)
   │  • Write code
   │  • Enforce CORE-011 (type hints)
   │  • Enforce CORE-012 (docstrings)
   │  • Enforce CORE-013 (error handling)
   │  • Log AC_EXECUTE during tests
   │
   ├─ PHASE 1.5: DESIGN-BUILD GAP DETECTION (NEW)
   │  • Check component in phase YAML ✓
   │  • Check implementation matches design ✓
   │  • Check @mcp_tool decorator (if applicable) ✓
   │  • Check component exported ✓
   │  • Check component registered ✓
   │  • Check governance audit trail ✓
   │  • Check documentation complete ✓
   │  │
   │  ├─ IF ALL CHECKS PASS:
   │  │  → Continue to Phase 2
   │  │
   │  └─ IF ANY CHECK FAILS:
   │     → Document gap
   │     → Create remediation AC
   │     → Report gap to Planner
   │     → Do NOT allow phase lock
   │
   ├─ PHASE 2: COMPLETION (with Validation)
   │  • Tests 100% passing
   │  • Code review passed
   │  • Log AC_COMPLETE to audit
   │  • Git commit with AC-ID
   │  • Update cortex-master.yaml
   │
   └─ END AC-IMPLEMENTATION

RESULT: Either AC COMPLETE (with full audit trail) or FLAGGED_GAP (with remediation AC)
```

---

## Gap Detection Flow (NEW)

```
                    PHASE COMPLETION
                           │
                           v
        ┌─ GAP DETECTION AGENT ACTIVATES
        │
        ├─ PHASE 1: DESIGN CHECK
        │  • Query cortex-master.yaml for AC-IDs
        │  • Verify AC marked COMPLETED
        │  • Check tests pass 100% (from audit log)
        │
        ├─ PHASE 2: IMPLEMENTATION CHECK
        │  • Grep for component code
        │  • Verify NOT stubbed (no TODO)
        │  • Check implementation matches design YAML
        │
        ├─ PHASE 3: EXPOSURE CHECK
        │  • Check @mcp_tool decorator present
        │  • Grep for __all__ export
        │  • Verify MCPServer registration
        │  • Check tool discovery endpoint
        │
        ├─ PHASE 4: GOVERNANCE CHECK
        │  • Query audit_log for AC_START ✓
        │  • Query audit_log for AC_EXECUTE ✓
        │  • Query audit_log for AC_COMPLETE ✓
        │  • Verify hash chain unbroken
        │
        └─ PHASE 5: DOCUMENTATION CHECK
           • Check README updated
           • Check MCP schema documented
           • Check usage examples provided
                           │
                           v
        ┌─ IF ALL 5 CHECKS PASS:
        │  → No gap found
        │  → Report: "COMPONENT_READY"
        │
        └─ IF ANY CHECK FAILS:
           → Gap found
           → Generate gap finding
           → Suggest remediation AC
           → Report: "GAP_DETECTED"
                           │
                           v
           ┌─ CREATE REMEDIATION
           │  • Gap → AC-ID (e.g., AC-MCP-001-02)
           │  • AC-ID → Phase (e.g., Phase-22)
           │  • Phase added to cortex-master.yaml
           │  • Planner informed for scheduling
           │
           └─ TRACK GAP
              • Gap stored in gap_inventory
              • Linked to remediation AC
              • Quarterly audit includes in report
```

---

## Agent Responsibility Matrix

```
┌──────────────────────┬──────┬────────┬───────┬──────┬───────┬─────┬────────┐
│ Responsibility       │ Bild │ Plan   │ Gvn   │ Brit │ Hall  │ Debt│ Gap    │
├──────────────────────┼──────┼────────┼───────┼──────┼───────┼─────┼────────┤
│ Implement code       │ ✅   │        │       │      │       │     │        │
│ Enforce CORE rules   │ ✅   │        │ ✅    │      │       │     │ ✅ (24)│
│ Log audit trail      │ ✅   │        │ ✅    │      │       │     │        │
│ Plan next steps      │      │ ✅     │ ✅    │      │       │     │ ✅     │
│ Detect gaps          │      │ ✅     │       │      │       │     │ ✅✅✅  │
│ Find brittleness     │      │        │       │ ✅   │       │     │        │
│ Find hallucination   │      │        │       │      │ ✅    │     │        │
│ Find debt            │      │        │       │      │       │ ✅  │        │
│ Verify assumptions   │      │        │       │      │       │     │ (7)    │
│ Check exposure       │ ✅ 1.5│       │ ✅    │      │       │     │ ✅✅✅  │
│ Verify governance    │      │        │ ✅✅✅ │      │       │     │ ✅     │
│ Generate reports     │      │ ✅     │       │      │       │     │ ✅     │
└──────────────────────┴──────┴────────┴───────┴──────┴───────┴─────┴────────┘

Legend:
✅    = Primary responsibility
✅✅✅ = Core focus (multiple checks)
(N)   = Reference specific feature/rule
```

---

## Communication Protocol

```
SCENARIO: Complete AC Implementation

1. BUILDER STARTS
   Message: "AC-XXX-XXX implementation starting"
   To: Git commit message
   Trigger: PLANNER reads git log

2. BUILDER COMPLETES CODE
   Message: "AC-XXX-XXX implementation complete"
   To: Git log + governance.db (AC_EXECUTE event)
   Trigger: GAP_DETECTION monitors governance.db

3. GAP DETECTION RUNS
   Message: "Running gap detection on AC-XXX-XXX"
   → Checks all 5 phases
   
   IF FAIL:
   Message: "Gap detected: [component] not [reason]"
   To: cortex-gap-detection findings
   Trigger: PLANNER queries findings, BUILDER notified

4. BUILDER COMPLETES PHASE 1.5
   Message: "Phase 1.5 gap checks: PASS"
   To: governance.db (AC_COMPLETE event)
   Trigger: PLANNER marks AC complete

5. PHASE COMPLETE
   Message: "PHASE-XX complete, audit verified"
   To: cortex-master.yaml (phase_tracker: locked=true)
   Trigger: All agents update reports

6. QUARTERLY AUDIT
   Message: "Running quarterly gap audit"
   Via: /gap-audit command
   Trigger: Show gap trends, recommend new phases
```

---

## Integration Points

```
1. Builder → Governance.db
   What: AC_START, AC_EXECUTE, AC_COMPLETE
   When: Before, during, after implementation
   Why: Audit trail verification

2. Builder → cortex-master.yaml
   What: Updated phase_tracker
   When: Phase completion
   Why: Roadmap synchronization

3. Gap Detection → All Agents
   What: Gap findings with evidence grades
   When: Per-phase completion
   Why: Coordinated remediation

4. Planner → Gap Detection
   What: Gap inventory queries
   When: Progress report generation
   Why: Integrated gap tracking

5. Reviewers → cortex-review-enhanced.prompt
   What: Findings with root causes
   When: Review completion
   Why: Orchestrated review process

6. cortex-review-enhanced → cortex-master.yaml
   What: Remediation ACs, new phases
   When: Review complete
   Why: Roadmap updates
```

---

## Success Criteria Visualization

```
BEFORE REFACTORING                 AFTER REFACTORING
────────────────────────────────────────────────────────

Agents: Isolated               →    Agents: Coordinated
  • No gap detection                • Systematic detection
  • Ad-hoc reviews                  • Integrated reviews
  • No feedback loop                • Feedback loop

Data: Multiple sources         →    Data: Single source
  • Conflicting info                • cortex-master.yaml
  • Audit trail gaps                • governance.db
  • Governance confusion            • tier0 rules

Governance: Incomplete         →    Governance: Complete
  • Some rules enforced             • All rules enforced
  • Manual verification             • Automated checks
  • Gap detection missing           • Gap detection (NEW)

Results: Unpredictable         →    Results: Predictable
  • Some gaps missed                • All gaps caught
  • Inconsistent evidence           • Consistent grading
  • Manual remediation              • Automated scheduling
```

---

## Files Generated (This Refactoring)

```
Agent files created:
  .github/agents/cortex-gap-detection.md ........................ NEW
  .github/agents/cortex-builder.md ............................. UPDATED
  .github/agents/cortex-planner.md ............................. UPDATED
  .github/agents/cortex-review-governance.md ................... UPDATED

Reference documentation created:
  .github/AGENT-SYSTEM-INTEGRATION.md .......................... NEW
  .github/AGENTS-AND-PROMPTS-INDEX.md .......................... NEW
  .github/PHASE-22-IMPLEMENTATION-READY.md ..................... NEW
  .github/REFACTORING-COMPLETE-SUMMARY.md ...................... NEW
  .github/CORTEX-AGENT-ARCHITECTURE-DIAGRAM.md ................. NEW (this file)

Prompt files updated:
  .github/prompts/cortex-review-enhanced.prompt.md ............. v2.1 (previous)

Phase planning:
  .github/roadmap/phases/phase-22-mcp-protocol-compliance.yaml .. NEW (previous)
```

---

## System Health Checklist

- [x] All agents reference same SSOT
- [x] All agents enforce same governance rules
- [x] Evidence grading consistent across agents
- [x] Root cause taxonomy shared
- [x] Gap detection integrated into builder
- [x] Gap detection integrated into planner
- [x] Gap detection integrated into governance reviewer
- [x] Communication protocol defined
- [x] Audit trail maintained
- [x] Quarterly audit capability enabled

**System Status**: ✅ READY FOR PRODUCTION

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
