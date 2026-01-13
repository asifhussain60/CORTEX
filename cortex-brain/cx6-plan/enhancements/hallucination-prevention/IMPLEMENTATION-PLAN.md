# CORTEX 6.0 - Hallucination Prevention Enhancement Plan

**Date:** 2026-01-13  
**Status:** ARCHITECTURE REVIEW  
**Design Score:** 87/100 → Target: 95/100  
**Estimated Effort:** 25 AC-IDs, 4.5 weeks additional  
**Platform:** 🟢 CROSS-PLATFORM (100% compatible MAC/WIN)

---

## Executive Summary

**Current State:**
CORTEX 6.0 has strong structural protections (87/100 score):
- ✅ Immutable audit trails with hash chain integrity
- ✅ Evidence-based verification (tests + audit logs)
- ✅ Governance enforcement (no override capability)
- ✅ State isolation with atomic transactions
- ✅ Deterministic routing with pattern matching

**Enhancement Goal:**
Add real-time hallucination detection layer (95/100 score):
- ✅ Input validation and sanitization
- ✅ Semantic consistency checks
- ✅ Health metrics and anomaly detection
- ✅ Source attribution and provenance tracking
- ✅ Cross-file coherence validation

**Strategy:**
Integrate 25 new AC-IDs into existing phases using **Phase Enhancement** approach:
1. Add validation layer to Phase 2 (Orchestration Core)
2. Add intelligence components to Phase 4 (Intelligence Layer)
3. Maintain backward compatibility (no breaking changes)
4. 100% cross-platform (MAC/WIN identical implementation)

---

## Architecture Analysis

### Gap 1: No Real-Time Hallucination Detection ⚠️

**Current:** Detect hallucinations AFTER execution (5-60 min latency)
**Missing:** Detect DURING execution (<200ms)
**Impact:** Reactive vs Proactive protection

**Solution:** Add validation layer in MasterOrchestrator pre-execution

```python
# File: src/orchestrators/core/master_orchestrator.py

class MasterOrchestrator:
    def handle_request(self, user_intent: str):
        # NEW: AC-VALIDATE-001 to 005 - Input validation layer
        validation_result = self.input_validator.validate(user_intent)
        
        if validation_result.blocked:
            return validation_result.guidance_message
        
        if validation_result.warnings:
            self.logger.warning(validation_result.warnings)
        
        # Continue with existing flow
        actions = self.evaluate_intent(user_intent)
        ...
```

**New AC-IDs:**
- AC-VALIDATE-001: Intent canonicalization (<10ms)
- AC-VALIDATE-002: AC-ID existence check (<5ms)
- AC-VALIDATE-003: Evidence bundle pre-check (<50ms)
- AC-VALIDATE-004: Cross-reference coherence (<100ms)
- AC-VALIDATE-005: Semantic output validation (<200ms)

**Phase Assignment:** Phase 2 (Orchestration Core) - WIN machine
**Effort:** 5 AC-IDs × 0.6 days = 3 days
**Platform:** 🟢 CROSS-PLATFORM (Python stdlib only)

---

### Gap 2: No Cross-File Coherence Check ⚠️

**Current:** Validate each file independently
**Missing:** Detect contradictions across files
**Example:** Plan recommends Architecture A, company-practices enforce Architecture B

**Solution:** Add knowledge graph validator in Intelligence Layer

```python
# File: src/orchestrators/intelligence/coherence_validator.py

class CoherenceValidator:
    """
    AC-COHERENCE-001 to 004: Cross-file semantic validation
    """
    def validate_recommendation(self, recommendation: str, context: Dict[str, Any]):
        # Load all relevant governance tiers
        tier0_rules = self.load_tier0_rules()
        tier1_requirements = self.load_tier1_requirements()
        tier2_standards = self.load_tier2_standards()
        
        # Check for contradictions
        conflicts = self.detect_conflicts(
            recommendation=recommendation,
            governance_stack=[tier0_rules, tier1_requirements, tier2_standards]
        )
        
        if conflicts:
            return ValidationResult(
                blocked=True,
                reason=f"Recommendation contradicts {conflicts[0].source}",
                guidance=self.suggest_alternative(conflicts)
            )
        
        return ValidationResult(approved=True)
```

**New AC-IDs:**
- AC-COHERENCE-001: Knowledge graph builder (tier0/1/2/3 unified view)
- AC-COHERENCE-002: Contradiction detection engine
- AC-COHERENCE-003: Semantic similarity validator
- AC-COHERENCE-004: Recommendation alignment checker

**Phase Assignment:** Phase 4 (Intelligence Layer) - MAC machine
**Effort:** 4 AC-IDs × 1.2 days = 4.8 days (LLM integration complexity)
**Platform:** 🟢 CROSS-PLATFORM (OpenAI/Anthropic APIs platform-agnostic)

---

### Gap 3: No Input Validation ⚠️

**Current:** Trust user input without sanitization
**Missing:** Validate intent before processing
**Example:** Accept "implement AC-FAKE-999" without checking existence

**Solution:** Add input validator to MasterOrchestrator

```python
# File: src/orchestrators/validation/input_validator.py

class InputValidator:
    """
    AC-VALIDATE-006 to 010: User intent validation
    """
    def validate(self, user_intent: str) -> ValidationResult:
        # AC-VALIDATE-006: Format validation
        if not self.is_valid_format(user_intent):
            return ValidationResult(
                blocked=True,
                reason="Intent format invalid",
                guidance="Use format: 'implement AC-{CATEGORY}-{NNN}'"
            )
        
        # AC-VALIDATE-007: Phase alignment
        ac_ids = self.extract_ac_ids(user_intent)
        for ac_id in ac_ids:
            if not self.is_in_current_phase(ac_id):
                return ValidationResult(
                    blocked=True,
                    reason=f"{ac_id} not in current phase",
                    guidance=f"Current phase: {self.get_current_phase()}"
                )
        
        # AC-VALIDATE-008: Contradiction detection
        contradictions = self.detect_contradictions(user_intent)
        if contradictions:
            return ValidationResult(
                blocked=True,
                reason="Request contains contradictions",
                guidance=contradictions
            )
        
        # AC-VALIDATE-009: Resource limits
        estimated_effort = self.estimate_effort(user_intent)
        if estimated_effort > self.MAX_SINGLE_REQUEST:
            return ValidationResult(
                blocked=True,
                reason="Request exceeds CORE-001 limits",
                guidance="Break into smaller increments"
            )
        
        # AC-VALIDATE-010: Prerequisite check
        missing_deps = self.check_prerequisites(ac_ids)
        if missing_deps:
            return ValidationResult(
                blocked=True,
                reason=f"Missing prerequisites: {missing_deps}",
                guidance="Implement dependencies first"
            )
        
        return ValidationResult(approved=True)
```

**New AC-IDs:**
- AC-VALIDATE-006: AC-ID format validation
- AC-VALIDATE-007: Phase alignment enforcement
- AC-VALIDATE-008: Request contradiction detection
- AC-VALIDATE-009: Resource limit validation (CORE-001)
- AC-VALIDATE-010: Prerequisite dependency check

**Phase Assignment:** Phase 2 (Orchestration Core) - WIN machine
**Effort:** 5 AC-IDs × 0.5 days = 2.5 days
**Platform:** 🟢 CROSS-PLATFORM (Python stdlib only)

---

### Gap 4: No Source Attribution ⚠️

**Current:** Log WHAT happened, not WHY recommended
**Missing:** Track which knowledge source influenced decision
**Example:** "Use PostgreSQL" - from company-practices or LLM hallucination?

**Solution:** Add provenance tracking to governance merger

```python
# File: src/orchestrators/core/governance_merger.py

class GovernanceMerger:
    """
    Enhanced with AC-EXPLAIN-001 to 005: Provenance tracking
    """
    def recommend(self, context: Dict[str, Any]) -> Recommendation:
        # Evaluate all tiers with provenance
        tier0_result = self.evaluate_tier0(context)  # AC-EXPLAIN-001
        tier1_result = self.evaluate_tier1(context)  # AC-EXPLAIN-002
        tier2_result = self.evaluate_tier2(context)  # AC-EXPLAIN-003
        tier3_result = self.evaluate_tier3(context)  # AC-EXPLAIN-004
        
        # Merge with provenance tracking
        recommendation = self.merge_with_provenance([
            tier0_result,
            tier1_result,
            tier2_result,
            tier3_result
        ])
        
        # AC-EXPLAIN-005: Audit trail with source attribution
        self.logger.info(
            "Recommendation generated",
            recommendation=recommendation.value,
            sources={
                "tier0": tier0_result.rules_applied,
                "tier1": tier1_result.requirements_applied,
                "tier2": tier2_result.standards_applied,
                "tier3": tier3_result.patterns_applied
            },
            confidence=recommendation.confidence_score
        )
        
        return recommendation
```

**New AC-IDs:**
- AC-EXPLAIN-001: Tier 0 provenance tracking (SKULL rules)
- AC-EXPLAIN-002: Tier 1 provenance tracking (business requirements)
- AC-EXPLAIN-003: Tier 2 provenance tracking (engineering standards)
- AC-EXPLAIN-004: Tier 3 provenance tracking (learned patterns)
- AC-EXPLAIN-005: Unified provenance audit trail

**Phase Assignment:** Phase 4 (Intelligence Layer) - MAC machine
**Effort:** 5 AC-IDs × 0.8 days = 4 days
**Platform:** 🟢 CROSS-PLATFORM (Python stdlib + SQLite)

---

### Gap 5: No Anomaly Detection ⚠️

**Current:** Manual review if something goes wrong
**Missing:** Automated baseline + deviation detection
**Example:** Test pass rate drops from 95% → 40%, not noticed until catastrophic

**Solution:** Add health metrics to TodoManager

```python
# File: src/orchestrators/todo/todo_manager.py

class TodoManager:
    """
    Enhanced with AC-METRICS-001 to 005: Health metrics
    """
    def track_progress(self, ac_id: str, result: ExecutionResult):
        # Existing tracking
        self._update_tracker(ac_id, result)
        
        # NEW: AC-METRICS-001 to 005 - Health monitoring
        self.metrics_collector.record(
            ac_id=ac_id,
            test_success_rate=result.test_pass_rate,  # AC-METRICS-001
            execution_latency=result.duration_ms,     # AC-METRICS-002
            evidence_completeness=result.evidence_score,  # AC-METRICS-003
            governance_violations=result.violations,  # AC-METRICS-004
        )
        
        # Anomaly detection
        anomalies = self.metrics_collector.detect_anomalies(ac_id)
        if anomalies:
            self.logger.warning(
                "Anomaly detected",
                ac_id=ac_id,
                anomalies=anomalies,
                baseline=self.metrics_collector.get_baseline()
            )
            # AC-METRICS-005: Alert system
            self.alert_system.notify(anomalies)
```

**New AC-IDs:**
- AC-METRICS-001: Test success rate baseline + deviation
- AC-METRICS-002: Execution latency tracking
- AC-METRICS-003: Evidence completeness validation
- AC-METRICS-004: Governance violation alerting
- AC-METRICS-005: Input rejection rate analysis

**Phase Assignment:** Phase 2 (Orchestration Core) - WIN machine
**Effort:** 5 AC-IDs × 0.6 days = 3 days
**Platform:** 🟢 CROSS-PLATFORM (Python stdlib + SQLite)

---

## Phase Integration Strategy

### Phase 2 Enhancement (WIN Machine)

**Current AC-IDs:** AC-ORCH-001 to AC-TODO-004 (12 AC-IDs)
**New AC-IDs:** AC-VALIDATE-001 to 010, AC-METRICS-001 to 005 (15 AC-IDs)
**Total:** 27 AC-IDs

**Timeline Impact:**
- Current Phase 2: 2 weeks (14 days)
- With enhancements: 2.5 weeks (17.5 days)
- Additional: 3.5 days

**Integration Points:**
```
MasterOrchestrator.handle_request()
  ├─ [NEW] InputValidator (AC-VALIDATE-001 to 010)
  ├─ GovernanceMerger (existing)
  ├─ TodoManager (existing)
  │   └─ [NEW] MetricsCollector (AC-METRICS-001 to 005)
  └─ Lifecycle callbacks (existing)
```

**Backward Compatibility:** ✅ YES
- New validators are additive (don't break existing flow)
- Metrics collection is passive (doesn't block operations)
- All new components have feature flags for gradual rollout

---

### Phase 4 Enhancement (MAC Machine)

**Current AC-IDs:** AC-INTENT-001 to AC-KNOWLEDGE-008 (20 AC-IDs)
**New AC-IDs:** AC-COHERENCE-001 to 004, AC-EXPLAIN-001 to 005 (9 AC-IDs)
**Total:** 29 AC-IDs

**Timeline Impact:**
- Current Phase 4: 2 weeks (14 days)
- With enhancements: 2.75 weeks (19.25 days)
- Additional: 5.25 days

**Integration Points:**
```
LLMIntentClassifier
  ├─ [NEW] CoherenceValidator (AC-COHERENCE-001 to 004)
  └─ [NEW] ProvenanceTracker (AC-EXPLAIN-001 to 005)

GovernanceMerger
  └─ [NEW] ProvenanceTracker (AC-EXPLAIN-001 to 005)
```

**Backward Compatibility:** ✅ YES
- Coherence checks run in parallel (don't block LLM calls)
- Provenance tracking is logging enhancement (non-blocking)
- Feature flags allow gradual rollout

---

## Cross-Platform Validation

**All 25 new AC-IDs are 100% cross-platform:**

| Component | Python Dependencies | Platform-Specific? |
|-----------|-------------------|-------------------|
| InputValidator | stdlib (re, json) | ❌ NO |
| MetricsCollector | stdlib + SQLite | ❌ NO |
| CoherenceValidator | OpenAI/Anthropic API | ❌ NO (HTTP-based) |
| ProvenanceTracker | stdlib + SQLite | ❌ NO |

**CORE-005 Compliance:** ✅ YES
- All file operations use `pathlib.Path`
- No hardcoded `/Users/` or `C:\\` paths
- Pre-commit hooks enforce portability

**Integration Tests Required:**
```python
@pytest.mark.cross_platform
def test_input_validator_mac_win():
    """AC-VALIDATE-001 to 010 work identically on both platforms"""
    validator = InputValidator()
    result = validator.validate("implement AC-AUDIT-001")
    assert result.approved is True

@pytest.mark.cross_platform
def test_metrics_collector_mac_win():
    """AC-METRICS-001 to 005 SQLite operations cross-platform"""
    collector = MetricsCollector()
    collector.record(ac_id="AC-TEST-001", test_pass_rate=0.95)
    baseline = collector.get_baseline()
    assert baseline is not None

@pytest.mark.cross_platform
def test_coherence_validator_mac_win():
    """AC-COHERENCE-001 to 004 LLM calls platform-agnostic"""
    validator = CoherenceValidator()
    result = validator.validate_recommendation("Use SQLite", {})
    assert result.approved is True
```

---

## Evidence Bundle Requirements

**Each new AC-ID requires standard evidence:**

```
cortex-brain/documents/evidence-bundles/hallucination-prevention/
├─ AC-VALIDATE-001/
│   ├─ manifest.yaml
│   ├─ test_results.json (pytest output)
│   └─ audit_trace.jsonl (governance log)
├─ AC-VALIDATE-002/
│   └─ ...
└─ AC-METRICS-005/
    └─ ...
```

**Acceptance Criteria:**
- ✅ Test coverage ≥80% (per AC-ID)
- ✅ Cross-platform tests pass on MAC and WIN
- ✅ Audit trail complete with provenance
- ✅ Evidence bundle validates via `scripts/audit_based_evidence_validator.py`

---

## Dashboard Visualization

**Plan Viewer Enhancements:**

```javascript
// cortex-brain/cx6-plan/viewer/plan-viewer.html

// Show enhancement badge for Phase 2 and Phase 4
function renderPhaseCard(phase) {
    let enhancementBadge = '';
    if (phase.id === 2 || phase.id === 4) {
        enhancementBadge = `
            <span class="badge badge-enhancement">
                🛡️ HALLUCINATION PREVENTION
            </span>
        `;
    }
    
    return `
        <div class="phase-card">
            <h3>Phase ${phase.id}: ${phase.name}</h3>
            ${enhancementBadge}
            <div class="ac-count">
                ${phase.ac_ids_complete}/${phase.ac_ids_total} AC-IDs
            </div>
        </div>
    `;
}
```

**New Metrics Display:**
```
Phase 2: Orchestration Core (🛡️ Enhanced)
├─ Base AC-IDs: 12/12 (100%)
├─ Enhancement AC-IDs: 0/15 (0%) ← NEW
└─ Total: 12/27 (44%)

Phase 4: Intelligence Layer (🛡️ Enhanced)
├─ Base AC-IDs: 0/20 (0%)
├─ Enhancement AC-IDs: 0/9 (0%) ← NEW
└─ Total: 0/29 (0%)
```

---

## Implementation Sequence

**Recommended Order:**

### Week 1-2: Phase 2 Base (WIN)
Implement existing AC-ORCH-001 to AC-TODO-004 (12 AC-IDs)

### Week 3: Phase 2 Enhancement - Input Validation (WIN)
- Day 1-2: AC-VALIDATE-006 to 010 (format, phase, prerequisites)
- Day 3-4: AC-VALIDATE-001 to 005 (canonicalization, semantic checks)
- Day 5: Integration tests + evidence bundles

### Week 4: Phase 2 Enhancement - Metrics (WIN)
- Day 1-2: AC-METRICS-001 to 003 (baseline, latency, evidence)
- Day 3: AC-METRICS-004 to 005 (violations, rejection rate)
- Day 4-5: Integration tests + evidence bundles

### Week 5-6: Phase 4 Base (MAC)
Implement existing AC-INTENT-001 to AC-KNOWLEDGE-008 (20 AC-IDs)

### Week 7: Phase 4 Enhancement - Coherence (MAC)
- Day 1-3: AC-COHERENCE-001 to 004 (knowledge graph, contradiction detection)
- Day 4-5: Integration tests + evidence bundles

### Week 8: Phase 4 Enhancement - Provenance (MAC)
- Day 1-3: AC-EXPLAIN-001 to 005 (tier provenance tracking)
- Day 4-5: Integration tests + cross-platform validation

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| LLM API rate limits | MEDIUM | MEDIUM | Implement caching + fallback to deterministic checks |
| Validator false positives | HIGH | LOW | Feature flags + gradual rollout |
| Performance degradation | LOW | MEDIUM | <200ms budget per validator, monitored |
| Cross-platform compatibility | LOW | HIGH | Integration tests on both platforms before merge |
| Scope creep | MEDIUM | HIGH | Strict AC-ID boundaries, no feature additions |

---

## Success Metrics

**Target: Design Score 87 → 95 (8-point improvement)**

| Metric | Baseline | Target | Validation |
|--------|----------|--------|------------|
| Real-time detection latency | N/A | <200ms | AC-VALIDATE-005 performance test |
| Input rejection rate | 0% | <5% | AC-METRICS-005 tracking |
| Coherence check coverage | 0% | 100% | AC-COHERENCE-004 integration |
| Provenance tracking | 0% | 100% | AC-EXPLAIN-005 audit trail |
| Anomaly detection accuracy | N/A | ≥90% | AC-METRICS-001 baseline validation |

**Overall Success Criteria:**
- ✅ All 25 AC-IDs implemented with evidence bundles
- ✅ Cross-platform tests pass on MAC and WIN
- ✅ No breaking changes to existing orchestrators
- ✅ Dashboard shows enhancement badges
- ✅ Design score reaches 95/100

---

## Rollout Strategy

**Phase 1: Development (Week 3-4, Week 7-8)**
- Implement AC-IDs on WIN (Phase 2) and MAC (Phase 4)
- Feature flags OFF (new components dormant)
- Integration tests validate cross-platform compatibility

**Phase 2: Alpha Testing (Week 9)**
- Enable feature flags in test environment
- Run 100-intent semantic test corpus
- Collect metrics on false positive rate

**Phase 3: Beta Testing (Week 10)**
- Enable feature flags in development workflow
- Monitor real-world usage patterns
- Tune validator thresholds based on feedback

**Phase 4: Production (Week 11)**
- Enable all validators by default
- Dashboard shows hallucination prevention metrics
- Audit trail includes provenance for all recommendations

---

## Conclusion

**Recommendation:** ✅ APPROVE with phased rollout

**Rationale:**
1. **Architecture-compliant:** Integrates seamlessly into existing Phase 2 and Phase 4
2. **Non-breaking:** All enhancements additive with feature flags
3. **Cross-platform:** 100% compatible MAC/WIN (CORE-005 compliant)
4. **Evidence-based:** Each AC-ID has test coverage + audit trail
5. **High ROI:** 8-point design score improvement for 4.5 weeks effort

**Next Steps:**
1. Update `master-plan.yaml` with 25 new AC-IDs
2. Update `AC-INDEX.yaml` with acceptance criteria
3. Create feature branch: `git checkout -b feat/hallucination-prevention`
4. Implement Phase 2 enhancements (WIN machine)
5. Implement Phase 4 enhancements (MAC machine)
6. Run cross-platform integration tests
7. Merge to main after CI/CD validation

---

**Document Location:** `cortex-brain/cx6-plan/enhancements/hallucination-prevention/IMPLEMENTATION-PLAN.md`
**Related Documents:**
- `hallucination-prevention-summary.md` (quick reference)
- `hallucination-prevention-holistic-review.md` (detailed analysis)
- `hallucination-prevention-integration.md` (technical blueprint)
- `request-challenge-hallucination-toolkit-build.md` (architectural conflict analysis)

**Author:** GitHub Copilot Autonomous Analysis  
**Date:** 2026-01-13  
**Status:** READY FOR MASTERORCHESTRATOR REVIEW
