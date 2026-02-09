# 🔒 AUDIT Phase Enforcement Architecture
**Authority:** cortex-architect.prompt.md v15.3 | **CORE-048 Implementation** | **Production Readiness Gate**

---

## Overview

This document specifies how the AUDIT phase will enforce mandatory governance gates to prevent incomplete/unsafe development from reaching production.

---

## Gate 1: MCP Activation Check (BLOCKER)

**File:** `.github/agents/core/cortex-auditor.md` (update)

```markdown
### MCP Activation Gate (MANDATORY)

**Before starting any audit:** Verify MCP tools available for AUDIT mode.

**Required Tools:**
- `cortex_lens_analyze` — Code intelligence analysis
- `cortex_validate_holistically` — Registry verification (NEW)
- `cortex_challenge` — Challenge generation

**Detection Method:**
```python
def verify_mcp():
    # 1. Check tool registry
    if "cortex_lens_analyze" in get_tools(): return True
    
    # 2. Check environment
    if os.getenv("CORTEX_MCP_ENABLED"): return True
    
    # 3. Check config
    if ".vscode/settings.json" has cortex config: return True
    
    # 4. Halt if all fail
    HALT with setup instructions
```

**Output if Blocked:**
```
❌ MCP Activation Check FAILED

Required tools not found:
  - cortex_lens_analyze: ❌ Not available
  - cortex_validate_holistically: ❌ Not available
  - cortex_challenge: ❌ Not available

Resolution:
  1. python -m cortex.mcp
  2. Reload VS Code
  3. Retry audit

Cannot proceed without MCP tools (CORE-049).
```

---

## Gate 2: Registry Verification (BLOCKER)

**New MCP Tool:** `cortex_validate_holistically`

**Purpose:** Reconcile registry claims vs git evidence vs actual code.

**Execution:**
```python
cortex_validate_holistically(
    target_phases=["phase-48", "phase-51", ...],  # User's request scope
    check_type="comprehensive"  # Registry + Git + Code + Tests
)

Returns:
{
    "phase-48": {
        "registry_status": "completed",
        "registry_tests_claimed": 143,
        "git_evidence": {
            "commit_count": 12,
            "last_modified": "2026-02-08T14:30Z",
            "test_markers": ["143/143", "100% pass"],
            "stages_found": ["S1", "S2", "S3", "S4", "S5", "S6"]
        },
        "actual_test_count": 142,  # Run pytest --collect-only
        "actual_pass_rate": 0.99,
        "tools_exposed": ["cortex_challenge", "cortex_holistic_validate"],
        "tools_missing": [],
        "verdict": "VERIFIED ✅",
        "confidence": 0.98,
        "recommendations": []
    },
    "phase-56-a": {
        "registry_status": "listed_in_phase_56",
        "registry_tests_claimed": null,
        "git_evidence": {
            "commit_count": 1,
            "last_modified": "2026-02-09T10:15Z",
            "test_markers": ["Complete"],
            "stages_found": []
        },
        "actual_test_count": 0,
        "actual_pass_rate": null,
        "tools_exposed": [],
        "tools_missing": ["cortex_relationship_traversal"],
        "verdict": "NEEDS REVIEW ⚠️",
        "confidence": 0.45,
        "recommendations": [
            "Create phase-56-a.yaml with complete specification",
            "Add test suite (currently 0 tests found)",
            "Register MCP tools if applicable"
        ]
    }
}
```

**In AUDIT Display:**
```markdown
### Registry Verification Results

| Phase | Registry | Git Evidence | Tests | Verdict |
|-------|----------|--------------|-------|---------|
| phase-48 | ✅ Completed | ✅ 12 commits | ✅ 143/143 | VERIFIED ✅ |
| phase-51 | ✅ Completed | ✅ 8 commits | ✅ 76/76 | VERIFIED ✅ |
| phase-56-a | ⚠️ Unlisted | ✅ 1 commit | ❌ 0 tests | NEEDS REVIEW ⚠️ |

**Decision:** Phase 48-51 verified for production use. Phase 56-A requires test evidence.

Approval required to proceed: "approve" or "skip to P0 checks"
```

---

## Gate 3: Scope Creep Detection (BLOCKING)

**File:** `cortex/governance/scope_creep_detector.py`

**Purpose:** Ensure phases stay within defined boundaries.

**Check:**
```python
def check_scope_creep(phase_id):
    # Load phase definition
    phase_def = load_phase_yaml(phase_id)
    
    # Scan files committed for this phase
    files = get_git_files_for_phase(phase_id)
    
    # Check if files are in allowlist
    outside = []
    for f in files:
        if f not in phase_def['file_allowlist']:
            outside.append(f)
    
    # Analyze dependency contamination
    orchestrators_touched = count_unique_orchestrators(files)
    expected = count_orchestrators(phase_def['scope'])
    
    # Calculate creep index
    creep_index = (len(outside) / len(files)) * 100
    contamination = (orchestrators_touched / expected - 1) * 100
    
    return {
        "creep_index": creep_index,
        "files_outside_scope": outside,
        "orchestrators_affected": orchestrators_touched,
        "expected_orchestrators": expected,
        "contamination_percent": contamination,
        "verdict": "OK" if creep_index < 20 else "REVIEW" if creep_index < 40 else "BLOCK"
    }
```

**In AUDIT Display:**
```markdown
### Scope Creep Analysis

| Phase | Index | Files Outside | Orchestrators | Verdict |
|-------|-------|----------------|----------------|---------|
| phase-48 | 5% | 0/145 | 4/4 ✅ | ✅ IN SCOPE |
| phase-51 | 18% | 3/42 | 2/2 ✅ | ⚠️ MINOR CREEP |

**Decision:** Phase 48 in scope. Phase 51 has minor creep (3 governance files), acceptable.

Approval required: "approve" or "recommend redesign"
```

---

## Gate 4: Challenge Gate (MANDATORY FOR P0)

**File:** `cortex/orchestrators/challenge_gate_orchestrator.py` (NEW)

**Purpose:** Present alternatives before implementing fixes.

**Execution (in AUDIT):**
```
IF P0 findings found:
  → Generate challenge with alternatives
  → Require user confirmation

IF P1 findings found:
  → Generate challenge
  → Allow user to select approach

IF P2 findings found:
  → Optional challenge (can auto-proceed)
```

**Challenge Format:**
```markdown
### ⚠️ MANDATORY CHALLENGE (CORE-048)

**Finding:** 5 bare except clauses detected (CORE-013 violation)

**Your Approach (Auto-Fix):**
- Replace all with specific exception types
- Add logging for each catch
- Pros: Explicit error handling, debuggable
- Cons: 45 LOC changes, slight performance overhead
- ROI: High (fixes 5 violations, sets pattern)

**Alternative A (Manual Fix):**
- User reviews each bare except, fixes selectively
- Pros: Controlled, preserves intent
- Cons: Manual effort (30 min), risk of missing some
- ROI: Medium (fixes only critical ones)

**Alternative B (Defer):**
- Log as TODO, proceed with audit
- Pros: Unblocks current audit cycle
- Cons: Technical debt, violations remain
- ROI: Low (temporary, debt accrues)

**Your Decision:**
Type one of:
- "proceed" — Use approach (auto-fix)
- "use A" — Use alternative A (manual)
- "use B" — Use alternative B (defer)

(No response = challenge blocks recommendations)
```

**Enforcement:**
- If P0 challenge → User MUST decide
- If no decision → AUDIT cannot complete
- Decision logged to AC markers (CORE-027)

---

## Gate 5: Auto-Fix Verification (BLOCKER)

**File:** `cortex/orchestrators/audit_fix_executor.py` (NEW)

**Purpose:** Verify fixes actually work before claiming success.

**Execution:**
```python
for finding in p0_findings + p1_findings:
    if finding.has_auto_fix:
        # Record baseline
        baseline_tests = run_tests(affected_modules)
        
        # Apply fix
        apply_fix(finding)
        
        # Re-run tests
        fixed_tests = run_tests(affected_modules)
        
        # Compare
        if fixed_tests.pass_rate < baseline_tests.pass_rate:
            # Fix broke something
            rollback_fix(finding)
            log_evidence({
                "finding_id": finding.id,
                "fix_applied": finding.fix,
                "baseline_pass_rate": baseline_tests.pass_rate,
                "post_fix_pass_rate": fixed_tests.pass_rate,
                "verdict": "FAILED - Rollback"
            })
            raise FixVerificationFailed(finding)
        else:
            # Fix worked
            log_evidence({
                "finding_id": finding.id,
                "fix_applied": finding.fix,
                "baseline_pass_rate": baseline_tests.pass_rate,
                "post_fix_pass_rate": fixed_tests.pass_rate,
                "verdict": "SUCCESS"
            })
            mark_finding_fixed(finding)
```

**Success Report Requirement:**
```
AUDIT can report "complete" ONLY IF:
  ✅ 100% of P0 findings fixed OR approved-manual
  ✅ 100% of P1 findings fixed OR approved-manual OR approved-defer
  ✅ All fixes verified (test pass rate maintained)
  ✅ Zero new violations introduced
  ✅ All evidence chains present
```

---

## Gate 6: Recommendation Filtering (GATING RECOMMENDATIONS)

**File:** `cortex/governance/recommendation_filter.py` (NEW)

**Purpose:** Prevent recommending rejected patterns.

**Checks:**
```python
def filter_recommendation(recommendation):
    """Gate each recommendation before display."""
    
    # Check 1: Rejection History
    similar = find_similar_rejections(recommendation, threshold=0.3)
    if similar:
        log_and_block(
            reason="Similar recommendation was rejected",
            previous_rejection=similar,
            action="Skip this recommendation"
        )
        return None
    
    # Check 2: Regression Risk
    risk_score = calculate_regression_risk(recommendation)
    if risk_score > 0.7:
        log_and_warn(
            reason="High regression risk",
            risk_score=risk_score,
            action="Display with caution disclaimer"
        )
        add_disclaimer(recommendation)
    
    # Check 3: Test Health
    if has_failing_tests(recommendation.affected_files):
        log_and_defer(
            reason="Affected area has failing tests",
            action="Defer recommendation until tests fixed"
        )
        return None
    
    # Check 4: Duplication (CORE-035)
    duplicates = find_similar_implementations(recommendation)
    if duplicates:
        log_and_recommend_dedup(
            reason="Duplicate pattern detected",
            duplicates=duplicates,
            action="Recommend deduplication first"
        )
        return recommendation.as_deduplication_recommendation()
    
    # All gates passed
    return recommendation
```

**Rejection History Format:**
```yaml
# docs/meta/rejected_recommendations/2026-02/REJ-20260209-001.yaml
rejected_recommendation:
  id: "REJ-20260209-001"
  timestamp: "2026-02-09T14:30:00Z"
  original_recommendation: "Refactor MetricsCalculator to functional style"
  reason: "User rejected - too risky for production"
  context_hash: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  confidence_score: 0.85
  similar_recommendations_blocked: 2  # Future blocking count
  by_agent: "RefactoringOrchestrator"
  user_feedback: "Prefer maintaining OOP style for team familiarity"
```

---

## AUDIT Phase Complete Flow

```python
def audit_phase_complete():
    """Full AUDIT phase with all enforcement gates."""
    
    # Gate 0: MCP Check
    if not verify_mcp():
        return HALT_SESSION
    
    # Gate 1: Registry Verification
    verification_result = cortex_validate_holistically(target_phases)
    if verification_result.has_discrepancies():
        display_verification_summary(verification_result)
        if not user_approves("Registry verification shows gaps. Proceed?"):
            return AUDIT_BLOCKED
    
    # Gate 2: Scope Creep
    scope_result = check_scope_creep_all_phases(target_phases)
    if scope_result.creep_index > 40:
        return AUDIT_BLOCKED_CREEP
    
    # Gate 3: Run P0 checks
    p0_findings = run_p0_checks()
    
    # Gate 4: Challenge (if P0 findings)
    if p0_findings:
        challenge = generate_challenge(p0_findings)
        display_challenge(challenge)
        user_decision = get_user_decision()  # Must decide
        if not user_decision:
            return AUDIT_BLOCKED_NO_CHALLENGE_RESPONSE
    
    # Gate 5: Auto-fix with verification
    user_approval = get_approval("approve fixes")
    for finding in p0_findings:
        if can_auto_fix(finding):
            apply_and_verify_fix(finding)  # Raises if verification fails
    
    # Gate 6: Filter recommendations
    recommendations = generate_recommendations()
    filtered_recs = [r for r in recommendations if filter_recommendation(r)]
    
    # Success (all gates passed)
    display_audit_report(
        findings=p0_findings,
        fixed_count=count_fixed(p0_findings),
        recommendations=filtered_recs,
        evidence_chain=build_evidence_chain()
    )
    
    return AUDIT_COMPLETE
```

---

## MCP Tool Registration

**File:** `.github/agents/core/cortex-mcp-gateway.md`

Add new tools:
```yaml
cortex_validate_holistically:
  category: "audit"
  purpose: "Verify phase claims against git evidence and code"
  parameters:
    - target_phases: ["phase-48", ...] or "all"
    - check_type: "registry" | "comprehensive"
  returns: {phase_id: {verdict, confidence, recommendations}}
  enforced_by: "AUDIT phase Gate 2"

cortex_challenge_gate:
  category: "governance"
  purpose: "Generate challenges with alternative approaches"
  parameters:
    - findings: [{id, type, severity, ...}]
    - alternatives: [{approach, pros, cons, roi}]
  returns: {challenge_text, requires_decision: bool}
  enforced_by: "AUDIT phase Gate 4"

cortex_audit_fix_executor:
  category: "governance"
  purpose: "Apply fixes and verify no regressions"
  parameters:
    - findings: [finding_objects]
    - run_tests: bool
    - rollback_on_failure: bool
  returns: {fixed_count, failed_count, evidence_chain}
  enforced_by: "AUDIT phase Gate 5"

cortex_recommendation_filter:
  category: "governance"
  purpose: "Filter recommendations to prevent regressions"
  parameters:
    - recommendations: [rec_objects]
    - check_rejection_history: bool
    - check_regression_risk: bool
  returns: {filtered_recommendations, blocked_reasons}
  enforced_by: "AUDIT phase Gate 6"
```

---

## Integration Points

### 1. cortex-architect.prompt.md

**Update:** Add AUDIT enforcement section
```markdown
## AUDIT Phase Mandatory Gating

AUDIT phase MUST enforce all 6 gates before success report:

1. MCP Activation (BLOCKER)
2. Registry Verification (BLOCKER)
3. Scope Creep Detection (BLOCKER)
4. Challenge Gate (BLOCKER for P0)
5. Auto-Fix Verification (BLOCKER)
6. Recommendation Filtering (GATING ONLY)

See: AUDIT_ENFORCEMENT_ARCHITECTURE.md for details.
```

### 2. cortex-auditor.md

**Update:** Add Gate 1-6 execution steps

### 3. CORE-048 (Holistic Validation Gate)

**Status Change:** From "conceptual" to "implemented with gates"

---

## Success Metrics

| Metric | Target | Method |
|--------|--------|--------|
| Challenge gate accuracy | >95% | User satisfaction survey |
| Registry verification match | >98% | Automated comparison tests |
| False-positive auto-fix rate | <1% | Test regression tracking |
| Recommendation filtering block rate | 10-15% | Rejection history analysis |
| Scope creep index (avg) | <20% | Phase analysis reports |
| Audit completion rate (no blockers) | >90% | Session tracking |

---

## Testing

**Test File:** `tests/governance/test_audit_enforcement_gates.py`

```python
class TestAuditEnforcementGates:
    
    def test_gate1_mcp_activation_blocking(self):
        """Gate 1: AUDIT halts if MCP unavailable."""
        assert audit_phase() raises MCP_UNAVAILABLE
    
    def test_gate2_registry_verification_reconciliation(self):
        """Gate 2: Registry claims match git evidence."""
        result = validate_holistically(["phase-48"])
        assert result["phase-48"]["verdict"] == "VERIFIED"
    
    def test_gate3_scope_creep_detection(self):
        """Gate 3: Detects files outside phase scope."""
        result = check_scope_creep("phase-48")
        assert result["files_outside_scope"] == []
    
    def test_gate4_challenge_blocks_without_decision(self):
        """Gate 4: Challenge requires user decision."""
        assert challenge_gate() raises NO_DECISION_ERROR
    
    def test_gate5_fix_verification_regression_detection(self):
        """Gate 5: Fix verification catches regressions."""
        apply_and_verify_fix(finding) raises TEST_FAILURE
        assert finding_rolled_back()
    
    def test_gate6_recommendation_filter_rejection_history(self):
        """Gate 6: Filters recommendations by rejection history."""
        rec = filter_recommendation(similar_to_rejected)
        assert rec is None
```

---

## Rollout Plan

**Phase 1 (Days 1-2):** Implement Gate 1-2 (MCP + Registry)
**Phase 2 (Days 3-4):** Implement Gate 3-4 (Scope + Challenge)
**Phase 3 (Days 5-6):** Implement Gate 5-6 (Fix + Filter)
**Phase 4 (Day 7):** Integration testing
**Phase 5 (Day 8):** Documentation + Training

---

## Conclusion

This enforcement architecture transforms AUDIT from a "report generator" into a **production readiness validator** with multiple safety gates. Each gate is specific, testable, and aligned with existing CORE rules.
