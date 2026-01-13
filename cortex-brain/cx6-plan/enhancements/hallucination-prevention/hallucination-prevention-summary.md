# CORTEX 6.0 - Hallucination Prevention: Quick Reference

**Date:** 2026-01-13  
**TL;DR:** Current design is strong (87/100) but has 5 gaps. Recommend adding 15 AC-IDs to Phase 2 for real-time detection.

---

## Current Design Strength: 87/100 ✅

### What It Prevents WELL:

| Threat | Current Defense | Strength |
|--------|-----------------|----------|
| Falsifying audit logs | Hash chain + tamper detection | ⭐⭐⭐⭐⭐ |
| Claiming unfinished work | Evidence bundles (tests + audit) | ⭐⭐⭐⭐⭐ |
| Bypassing governance | Immutable CORE rules, no override | ⭐⭐⭐⭐⭐ |
| State corruption | SQLite WAL + atomic transactions | ⭐⭐⭐⭐ |
| Non-deterministic routing | Pattern matching + logging | ⭐⭐⭐⭐ |

---

## 5 Critical Gaps Found 🚨

### Gap 1: No Real-Time Detection ⚠️
```
Current: Catch hallucinations AFTER (5-60 min latency)
Missing: Catch DURING execution (<200ms)
Fix: AC-VALIDATE-001 to 005 (Semantic validation)
Impact: Move from reactive → proactive
Phase: Phase 2 (4 days, 10 AC-IDs)
```

### Gap 2: No Cross-File Coherence Check ⚠️
```
Current: Validate each file independently
Missing: Detect contradictions across files
Example: Recommend Architecture A (in plan) vs Architecture B (in company-practices)
Fix: AC-COHERENCE-001 to 004 (Knowledge graph validation)
Phase: Phase 4 or 1.5 (Intelligence)
```

### Gap 3: No Input Validation ⚠️
```
Current: Trust user input (accept "implement AC-FAKE-999")
Missing: Sanitize intent before processing
Fix: AC-VALIDATE-006 to 010 (Intent validation)
Effort: 6 AC-IDs, 3 days, Phase 2 enhancement
```

### Gap 4: No Source Attribution ⚠️
```
Current: Log WHAT happened, not WHY recommended
Missing: Track which knowledge base → recommendation
Example: "Use PostgreSQL" — from company-practices or LLM guess?
Fix: AC-EXPLAIN-001 to 005 (Provenance tracking)
Phase: Phase 4 (Intelligence layer)
```

### Gap 5: No Anomaly Detection ⚠️
```
Current: Manual review if something goes wrong
Missing: Automated baseline + deviation detection
Example: Test pass rate drops from 95% → 40%, not noticed until catastrophic
Fix: AC-METRICS-001 to 005 (Predictability metrics)
Effort: 5 AC-IDs, 3 days, Phase 2/3
```

---

## Recommended Enhancement Plan

### TIER A: Critical Before Phase 3 ⚡

**Add to Phase 2 (Orchestration Core):**

```
15 NEW AC-IDs Total:

INPUT VALIDATION (Gap 1 + Gap 3):
  • AC-VALIDATE-001: Intent canonicalization (<10ms)
  • AC-VALIDATE-002: AC-ID existence check (<5ms)
  • AC-VALIDATE-003: Evidence bundle pre-check (<50ms)
  • AC-VALIDATE-004: Cross-reference coherence (<100ms)
  • AC-VALIDATE-005: Semantic output validation (<200ms)
  • AC-VALIDATE-006: AC-ID format validation
  • AC-VALIDATE-007: Phase alignment enforcement
  • AC-VALIDATE-008: Request contradiction detection
  • AC-VALIDATE-009: Resource limit validation
  • AC-VALIDATE-010: Prerequisite dependency check

HEALTH METRICS (Gap 5):
  • AC-METRICS-001: Test success rate baseline + deviation
  • AC-METRICS-002: Execution latency tracking
  • AC-METRICS-003: Evidence completeness validation
  • AC-METRICS-004: Governance violation alerting
  • AC-METRICS-005: Input rejection rate analysis

Timeline Impact:
  Current Phase 2: 14 days (2 weeks)
  With Tier A: 17-18 days (2.5 weeks)
  Critical? YES - closes 5 vulnerability classes
```

### TIER B: Important But Not Blocking

**Add to Phase 1.5 or 4 (Intelligence):**

```
SEMANTIC COHERENCE (Gap 2):
  • AC-COHERENCE-001 to 004: Knowledge graph consistency
  Timeline: Phase 4 (8 weeks out)
  Importance: HIGH - but less critical than real-time validation

SOURCE ATTRIBUTION (Gap 4):
  • AC-EXPLAIN-001 to 005: Recommendation provenance
  Timeline: Phase 4
  Importance: MEDIUM - useful for debugging but not blocking
```

---

## Current Protection Mechanisms (Good News)

### ✅ Immutable Audit Trail
```
Mechanism: SQLite + hash chain (event_hash + prev_event_hash)
Protection: Cannot tamper with operation history
Test Coverage: AC-AUDIT-007 (proven)
Rating: ⭐⭐⭐⭐⭐ Excellent
```

### ✅ Evidence-Based Verification
```
3-Part Evidence Bundle:
  1. manifest.yaml (completion metadata)
  2. test_results.json (80%+ pass rate required)
  3. audit_trace.jsonl (full governance log)

Protection: Tests PROVE work done, not just claimed
Validation Gates: 3 gates (test/audit/governance)
Rating: ⭐⭐⭐⭐⭐ Excellent
```

### ✅ Immutable Governance
```
23 CORE rules (Tier 0): HIGHEST precedence, NO override possible
Enforcement: Pre-execution + mid-execution + post-execution hooks
Rating: ⭐⭐⭐⭐⭐ Excellent
```

### ✅ State Isolation
```
SQLite WAL mode: Atomic state transitions
Rollback on Failure: Automatic recovery
Rating: ⭐⭐⭐⭐ Excellent (minor: Tier 1 JSON not ACID)
```

### ✅ Deterministic Routing
```
Pattern Matching: Same input → same route (repeatable)
Logging: All routing decisions audited
Rating: ⭐⭐⭐⭐ Excellent (minor: LLM fallback is stochastic)
```

---

## Risk Assessment

### If Enhancements NOT Added

```
Risk Probability: MEDIUM-HIGH
Risk Impact: Hallucinations undetected for 30-120 minutes

Scenario:
  1. Copilot claims "AC-PLAN-999 implemented"
  2. No real-time validation
  3. User believes claim, builds on it
  4. Hours later, verification finds no evidence
  5. Cascading rollback required

Mitigation: Add Tier A enhancements before Phase 3
```

### If Enhancements ARE Added

```
Risk Probability: LOW
Risk Impact: Hallucinations caught <200ms

Detection Flow:
  1. Copilot claims "AC-PLAN-999 implemented"
  2. AC-VALIDATE-002 checks AC-INDEX: NOT FOUND
  3. Block claim, suggest real AC-ID
  4. Audit logs rejection
  5. User gets correct guidance immediately
```

---

## Master Plan Integration

### Option 1: Integrate into Phase 2 (RECOMMENDED)

```yaml
Phase 2: Orchestration Core (Current: 14 days)
  
ADD to Phase 2:
  • Week 1.5 (overlap with MasterOrchestrator):
    - AC-VALIDATE-001 to 010 (10 ACs, ~40 person-hours TDD)
    - AC-METRICS-001 to 005 (5 ACs, ~20 person-hours TDD)

New Phase 2: 18-20 days (2.5 weeks)
Total Project Timeline: +5 days (not critical path)
Go-Live Impact: Minimal (Phase 2 gate adds validation, not delay)
```

### Option 2: New Phase 1.5 (Conservative)

```yaml
Phase 1: Foundation (DONE) ✅
Phase 1.5 NEW: Validation Infrastructure (1 week)
  • AC-VALIDATE-001 to 010
  • AC-METRICS-001 to 005
  
Phase 2: Orchestration (Start 1 week later)
Timeline Impact: +1 week total
```

### Option 3: Defer to Phase 4 (NOT RECOMMENDED)

```
Risk: Phases 2-3 output not validated
Mitigation: Manual verification (labor intensive)
Recommendation: Don't choose this path
```

---

## Implementation Checklist

### For Phase 2 Enhancement (Recommended)

```
☐ Add 15 AC-IDs to cortex-brain/cx6-plan/master-plan.yaml
☐ Create AC-VALIDATE-001 to 010 in AC-INDEX.yaml
☐ Create AC-METRICS-001 to 005 in AC-INDEX.yaml
☐ Design TDD test skeletons for all 15 ACs
☐ Implement AC-VALIDATE pre-execution hooks
☐ Integrate AC-METRICS into EnhancedAuditLogger
☐ Test false positive rate <1% on golden corpus
☐ Update Phase 2 gate criteria (add validation gates)
☐ Estimate: 60 person-hours, 5 business days
```

---

## Expected Outcomes

### After Adding Tier A Enhancements:

```
Detection Latency: 5-60 minutes → <200ms ⚡
False Positive Rate: Unknown → <1% ✅
Hallucination Classes Addressed: 3/5 ✅
Undetected Risks: 2/5 (coherence + provenance, Phase 4)

Example Before:
  ❌ Copilot: "AC-PLAN-999 complete"
  ❌ No validation
  ❌ User trusts claim
  ❌ Hours later: found to be false

Example After:
  ✅ Copilot: "AC-PLAN-999 complete"
  ✅ AC-VALIDATE-002: NOT in AC-INDEX
  ✅ Block claim within 5ms
  ✅ Suggest real AC-ID immediately
```

---

## Questions for Architecture Review

1. **Timeline Flexibility:** Can Phase 2 expand from 14 to 18 days? (Recommended)
2. **Tier 1 JSON:** Should progress-tracker.json use SQLite for ACID? (Nice-to-have)
3. **LLM Classifier Fallback:** Should deterministic routing have stochastic backup? (Current design OK)
4. **Phase 1.5 Sequencing:** Add Intelligence discovery before Phase 2? (Separate decision)

---

**Detailed Analysis:** See `hallucination-prevention-holistic-review.md`  
**Master Plan Location:** `cortex-brain/cx6-plan/master-plan.yaml`  
**AC-INDEX Location:** `cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml`

