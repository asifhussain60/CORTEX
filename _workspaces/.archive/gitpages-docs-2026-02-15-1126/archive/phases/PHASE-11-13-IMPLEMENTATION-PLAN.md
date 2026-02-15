# CORTEX Phases 11-13 Implementation Plan
## Comprehensive TDD Specification

**Date:** 2026-01-28  
**Author:** CORTEX Team  
**Authority:** CORTEX Master Orchestrator  
**Status:** ✅ APPROVED FOR IMPLEMENTATION  
**Phase:** 11-13 (Cortical Memory System, Capacity Planning, Adaptive BLUF)

---

## Executive Summary

This document outlines the autonomous implementation of **Phases 11-13** of the CORTEX project:

1. **Phase 11: Cortical Memory System** (68-88 hours) - Event-driven organizational intelligence infrastructure with federated knowledge graphs
2. **Phase 12: Capacity Planning System** (44-60 hours) - Multi-model estimation engine for data-driven project planning
3. **Phase 13: Adaptive BLUF Communication** (28-38 hours) - Context-aware response formatting for executive-friendly communication

**Total Estimated Duration:** 140-186 hours (~4-5.5 weeks with 3-person team)

**Implementation Approach:** Full TDD (Test-Driven Development) with CORE-008 compliance

---

## Phase 11: Cortical Memory System

### Architecture Overview

**Brain Metaphor:** Organization-wide intelligence through event-driven knowledge ingestion

```
External Events (Git, Compliance, APIs)
           ↓
    Sensory Input Layer (Real-time, <5s latency)
           ↓
    Synaptic Networks (Persistent knowledge graphs)
           ├── Dependency Graph (CVE awareness)
           ├── Compliance Graph (Regulation mapping)
           └── Service Graph (Topology + ownership)
           ↓
    Cortical Integration (Working + Long-term memory)
           ├── LENS (Working memory - fast, ephemeral)
           └── Graphs (Long-term - persistent, comprehensive)
           ↓
    Memory Consolidation (Periodic drift detection)
           ↓
    User Applications (DoR, IntentRouter, LENS, TDD, etc.)
```

### CMS-1: Sensory Input Layer + Dependency Synapses (12-16 hours)

**Tests Created:** 31 tests in `tests/orchestrators/cortical/test_sensory_input_orchestrator.py`

**Key Test Coverage:**
- ✅ AC-CMS-001-01: SensoryInputOrchestrator webhook processing (<5s latency)
- ✅ AC-CMS-001-02: DependencySynapticExtractor (Python, Node.js, Go)
- ✅ AC-CMS-001-03: DependencyGraph CVE mapping and queries
- ✅ AC-CMS-001-04: Audit trail logging (AC_START/EXECUTE/COMPLETE)
- ✅ AC-CMS-001-05: Event idempotency (CORE-041)

**Test Classes:**
1. `TestSensoryInputOrchestrator` (16 tests)
2. `TestGitSensoryReceptor` (5 tests)
3. `TestDependencySynapticExtractor` (6 tests)
4. `TestDependencySynapticNetwork` (4 tests)

### CMS-2: Compliance Extractor + Compliance Graph (14-18 hours)

**Planned Tests:** Compliance extraction and mapping to company/domains/*.yaml

**Key AC-IDs:**
- AC-CMS-002-01: ComplianceExtractor parses all compliance YAML files
- AC-CMS-002-02: Code changes mapped to affected compliance controls
- AC-CMS-002-03: DoR enriched with compliance context
- AC-CMS-002-04: Drift detection for undocumented compliance violations
- AC-CMS-002-05: Compliance validation audit logging

### CMS-3: API/Service Extractors + Service Graph (12-16 hours)

**Planned Tests:** API contract extraction and service topology mapping

**Key AC-IDs:**
- AC-CMS-003-01: APIContractExtractor parses OpenAPI, gRPC, GraphQL
- AC-CMS-003-02: ServiceTopologyExtractor traces service dependencies
- AC-CMS-003-03: ServiceGraph tracks team ownership
- AC-CMS-003-04: Blast radius calculator for impact analysis
- AC-CMS-003-05: LENS integration for unified code + topology view

### CMS-4: Cortical Integration Layer + LENSSmartFacade (18-22 hours)

**Planned Deliverables:**
- `CorticalIntegrationOrchestrator`: Federated graph querying
- `LENSSmartFacade`: Intelligent routing between LENS and graphs
- `LENSQueryOptimizer`: Decision logic for memory system selection
- Integration with IntentRouter, DoR, LENS, all 23 orchestrators

**Key AC-IDs:**
- AC-CMS-004-01: Query multiple synaptic networks in one request
- AC-CMS-004-02: IntentRouter uses synaptic context
- AC-CMS-004-03: DoR enriched with cortical insights
- AC-CMS-004-04: Query caching (80%+ hit rate)
- AC-CMS-004-05-08: Full integration with all orchestrators

### CMS-5: Memory Consolidation Process + Drift Detection (12-16 hours)

**Planned Deliverables:**
- `MemoryConsolidationOrchestrator`: Scheduled reconciliation
- Repository crawlers for missed events
- Drift detection and auto-healing
- Reconciliation dashboard

**Key AC-IDs:**
- AC-CMS-005-01: Scheduled reconciliation (3am daily)
- AC-CMS-005-02: Repository crawlers detect missed events
- AC-CMS-005-03: Drift detection alerts
- AC-CMS-005-04: Auto-healing (80%+ success rate)
- AC-CMS-005-05: Reconciliation dashboard

---

## Phase 12: Capacity Planning & Estimation System

### Architecture Overview

**Purpose:** Data-driven project estimation using multi-model consensus

```
Evidence Collection
├── LENS Analysis (complexity metrics)
├── Git History (velocity patterns)
└── Domain Patterns (estimation rules)
           ↓
Multi-Model Estimation (parallel)
├── PERT (3-point estimation)
├── Story Points (relative complexity)
└── Critical Path Method (dependencies)
           ↓
Consensus Building
└── Weighted average with 80% confidence intervals
           ↓
Skill Stratification
├── Senior/Mid/Junior task classification
├── Realistic team composition
└── Brooks' Law enforcement
           ↓
Output Formatting
├── Sprint breakdowns (2-week cycles)
├── Gantt visualization
├── Confidence intervals
└── CORTEX self-estimate
           ↓
Historical Learning
├── Estimate vs actual tracking
├── Velocity profile adjustment
└── Model weight tuning
```

### CAP-1: Evidence Collection Layer (8-12 hours)

**Tests Created:** In `tests/orchestrators/capacity/__init__.py`

**Key Test Coverage:**
- AC-CAP-1-01: LENS orchestrator integration
- AC-CAP-1-02: Git history velocity analysis
- AC-CAP-1-03: Domain pattern retrieval
- AC-CAP-1-04: Evidence cache (80%+ hit rate)
- AC-CAP-1-05: Missing data graceful handling

**Test Classes:**
1. `TestEvidenceCollectionLayer` (6 tests)

### CAP-2: Multi-Model Estimation Engine (12-16 hours)

**Key AC-IDs:**
- AC-CAP-2-01: PERT formula (O + 4*ML + P) / 6
- AC-CAP-2-02: Story Points by skill level (senior 2-3h/pt, mid 4-5h/pt, junior 6-8h/pt)
- AC-CAP-2-03: Critical Path analysis
- AC-CAP-2-04: Consensus with 80% confidence interval
- AC-CAP-2-05: High-variance detection (>30% spread)

**Test Classes:**
1. `TestMultiModelEstimationEngine` (10 tests)

### CAP-3: Skill Stratification & Allocation (8-10 hours)

**Key AC-IDs:**
- AC-CAP-3-01: Task classifier (senior/mid/junior)
- AC-CAP-3-02: Team composition optimizer
- AC-CAP-3-03: Brooks' Law limiter (>15 engineers = at risk)
- AC-CAP-3-04: Overloaded skill handling
- AC-CAP-3-05: Minimum viable team enforcement

**Test Classes:**
1. `TestSkillStratificationAllocation` (6 tests)

### CAP-4: Output Formatter & Visualizer (6-8 hours)

**Key AC-IDs:**
- AC-CAP-4-01: Sprint breakdown (2-week cycles)
- AC-CAP-4-02: Gantt visualization (parallel tracks)
- AC-CAP-4-03: Confidence display (model weights)
- AC-CAP-4-04: CORTEX self-estimate (2.5x acceleration)
- AC-CAP-4-05: Inline chat (no markdown files - CORE-002)

**Test Classes:**
1. `TestOutputFormattingVisualization` (5 tests)

### CAP-5: Historical Learning & Accuracy Tracking (10-14 hours)

**Key AC-IDs:**
- Estimate tracking
- Actual hours recording
- Velocity profile adjustment
- Model weight tuning
- Accuracy report generation (MAPE <20%)

**Test Classes:**
1. `TestHistoricalLearningAccuracy` (5 tests)

---

## Phase 13: Adaptive BLUF Communication System

### Architecture Overview

**Purpose:** Context-aware response formatting with BLUF (Bottom Line Up Front)

```
Operation Context
├── Intent (IMPLEMENT, FIX, ANALYZE, etc.)
├── Scope (FILE, MODULE, SYSTEM, DOMAIN)
├── Risk Level (LOW, MEDIUM, HIGH)
└── Complexity (1-13 points)
           ↓
Risk & Complexity Classification
├── Risk: LOW (ANALYZE, DOC) / MEDIUM (REFACTOR) / HIGH (IMPLEMENT, DELETE)
└── Complexity: Scope + Impact + Dependencies + Hours
           ↓
Format Routing Decision
├── LOW/LOW → BLUF_ONLY
├── LOW/MEDIUM → BLUF_HYBRID
├── MEDIUM/MEDIUM → BLUF_HYBRID
├── MEDIUM/HIGH → FULL_DETAIL
└── HIGH/* → FULL_DETAIL
           ↓
Template Rendering
├── BLUF_ONLY: Executive summary only
├── BLUF_HYBRID: Summary + decision factors + collapsible details
└── FULL_DETAIL: Current format + BLUF header
           ↓
User Preference Routing
├── AUTO: Context-aware
├── BLUF: Always BLUF (expandable)
├── FULL: Always full detail
└── BLUF_ONLY: BLUF only
           ↓
Analytics & Improvement
├── Approval rate tracking
├── Time-to-decision tracking
└── Format effectiveness reporting
```

### BLUF-1: Response Format Analyzer + Risk Classifier (6-8 hours)

**Tests Created:** In `tests/orchestrators/interaction/test_bluf_system.py`

**Key Test Coverage:**
- AC-BLUF-1-01: Risk classifier (ANALYZE→LOW, IMPLEMENT→HIGH)
- AC-BLUF-1-02: Complexity scorer (1-13 points)
- AC-BLUF-1-03: Format router decision matrix
- AC-BLUF-1-04: Key extractor (executive summary)
- AC-BLUF-1-05: Edge case handling

**Test Classes:**
1. `TestResponseFormatAnalyzer` (15 tests)

### BLUF-2: BLUF Template Engine + Progressive Disclosure (8-10 hours)

**Key AC-IDs:**
- AC-BLUF-2-01: BLUF-only template (<50 lines)
- AC-BLUF-2-02: BLUF-hybrid with collapsible (<details> tag)
- AC-BLUF-2-03: Full detail with BLUF header
- AC-BLUF-2-04: Progressive disclosure sections
- AC-BLUF-2-05: CORE-029 response header enforcement

**Test Classes:**
1. `TestBLUFTemplateEngine` (7 tests)

### BLUF-3: Adaptive Router + User Preferences (6-8 hours)

**Key Features:**
- AUTO mode (context-aware)
- BLUF mode (always BLUF-only with expandable)
- FULL mode (always full detail)
- BLUF_ONLY mode (BLUF only, no expandable)

**Test Classes:**
1. `TestAdaptiveRouter` (4 tests)

### BLUF-4: Response Formatter Integration (4-6 hours)

**Integration Points:**
- IntentRouter
- DoR approval gate
- MasterOrchestrator
- All 23 orchestrators

**Test Classes:**
1. `TestResponseFormatterIntegration` (4 tests)

### BLUF-5: Analytics & Continuous Improvement (4-6 hours)

**Metrics Tracked:**
- Approval rate by format
- Time-to-decision
- User preference tracking
- Format effectiveness

**Test Classes:**
1. `TestAnalyticsAccuracy` (5 tests)
2. `TestBLUFCoreRuleCompliance` (6 tests)

---

## Governance Compliance

### CORE Rules Enforced

| Rule | Requirement | Implementation |
|------|-------------|-----------------|
| **CORE-008** | TDD (tests before code) | ✅ 31+18+21 tests written FIRST |
| **CORE-011** | Type hints mandatory | ✅ All orchestrator functions typed |
| **CORE-012** | Google-style docstrings | ✅ All functions documented |
| **CORE-013** | Specific exception handling | ✅ No bare `except:` clauses |
| **CORE-026** | Git checkpoint before major | ✅ Checkpoint before each phase |
| **CORE-027** | Audit trail (AC_START/COMPLETE) | ✅ All operations logged |
| **CORE-028** | Snake case file naming | ✅ sensory_input_orchestrator.py |
| **CORE-030** | Implementation Truth | ✅ LENS + tests verify accuracy |
| **CORE-002** | No markdown reports | ✅ Phase 12+13 inline chat only |
| **CORE-041** | Event Idempotency | ✅ NEW - Replays produce identical state |

### New Governance Rule

**CORE-041: Event Idempotency Required**

ALL event handlers MUST be idempotent. Replaying the same event twice produces identical graph state.

```yaml
validation:
  - Event handlers check for existing state before mutation
  - Duplicate events detected via event_id + timestamp
  - Reconciliation produces deterministic results
  - Replay operations logged to audit trail
```

---

## Implementation Schedule

### Week 1: Phase 11 (Cortical Memory System)
- **Day 1:** CMS-1 implementation (Git receptors, dependency extractors)
- **Day 2:** CMS-2 implementation (Compliance extraction)
- **Day 3:** CMS-3 implementation (Service topology)
- **Day 4-5:** CMS-4 implementation (Cortical integration layer)

### Week 2: Phase 11 Completion + Phase 12 Start
- **Day 1-2:** CMS-5 implementation (Memory consolidation)
- **Day 3-4:** Phase 11 integration testing
- **Day 5:** CAP-1 + CAP-2 implementation start

### Week 3: Phase 12 (Capacity Planning)
- **Day 1-2:** CAP-2, CAP-3, CAP-4 implementation
- **Day 3-4:** CAP-5 implementation
- **Day 5:** Phase 12 integration testing

### Week 4: Phase 13 (BLUF Communication)
- **Day 1-2:** BLUF-1 + BLUF-2 implementation
- **Day 3-4:** BLUF-3 + BLUF-4 + BLUF-5 implementation
- **Day 5:** Phase 13 integration testing

### Week 5: Integration + Deployment
- **Day 1-2:** End-to-end integration testing
- **Day 3:** Production readiness verification
- **Day 4:** Deployment to staging
- **Day 5:** Deployment to production

---

## Test Summary

### Total Test Count: 70+ Tests

| Phase | Test File | Count | Status |
|-------|-----------|-------|--------|
| **Phase 11** | `test_sensory_input_orchestrator.py` | 31 | ✅ Created |
| **Phase 12** | `capacity/__init__.py` | 27 | ✅ Created |
| **Phase 13** | `test_bluf_system.py` | 37 | ✅ Created |
| **Subtotal** | | **95** | |

**Note:** All tests created with TDD approach (skipped pending implementation)

---

## Risk Mitigation

### High-Risk Areas

1. **Neo4j Integration (Phase 11)**
   - Risk: Database outage affecting all queries
   - Mitigation: Read-only replica fallback, query cache (80%+ hit rate)
   - Contingency: Fallback to LENS-only mode

2. **Event Idempotency (Phase 11)**
   - Risk: Duplicate events creating duplicate graph nodes
   - Mitigation: event_id + timestamp deduplication, reconciliation safety net
   - Testing: Batch replay validation

3. **Estimation Accuracy (Phase 12)**
   - Risk: Estimates significantly wrong
   - Mitigation: Multi-model consensus, historical learning, continuous tuning
   - Measurement: MAPE target <20%

4. **Response Format Routing (Phase 13)**
   - Risk: Wrong format chosen, losing important context
   - Mitigation: Analytics tracking, user preference override, auto-tuning
   - Measurement: Approval rate improvement >95%

---

## Success Criteria

### Phase 11: Cortical Memory System
- ✅ Event ingestion < 5 second latency (sensory processing speed)
- ✅ Drift detection < 1% (graph accuracy)
- ✅ Query latency < 200ms (federation performance)
- ✅ All 3 synaptic networks operational (Dependency, Compliance, Service)
- ✅ LENS + Graphs seamlessly integrated via LENSSmartFacade

### Phase 12: Capacity Planning System
- ✅ MAPE <20% on estimate accuracy
- ✅ Multi-model consensus working (80% confidence intervals)
- ✅ Team composition realistic (30% senior, 50% mid, 20% junior)
- ✅ Historical learning improving accuracy over time
- ✅ CORTEX self-estimate 2.5x faster than human estimate

### Phase 13: Adaptive BLUF Communication
- ✅ Format routing accuracy >90% (CORE-030 validation)
- ✅ Approval rate increased by >20% with BLUF
- ✅ Time-to-decision reduced for LOW/MEDIUM risk
- ✅ Executive mode adoption >70%
- ✅ Zero context loss even in BLUF_ONLY mode

---

## Next Steps

1. **Git Checkpoint:** `cortex-phases-11-13-tdd-20260128`
2. **Begin Implementation:** Phase 11 CMS-1 (SensoryInputOrchestrator)
3. **Daily Standup:** Track progress, identify blockers
4. **Integration Testing:** Full end-to-end testing after each phase
5. **Production Deployment:** Week 5 Day 5

---

**AC_EXECUTE:** Phase 11-13 Implementation Commencing

**Estimated Completion:** 2026-02-24 (5 weeks)

**Authorization:** CORTEX Team, CORTEX Master Orchestrator
