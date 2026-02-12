# CORTEX Learning System: Adaptive Intelligence Infrastructure

**Version:** 1.0.0 | **Phase:** 71 — Universal Learning Loop | **Status:** PRODUCTION  
**Last Updated:** 2026-02-10 | **Authority:** Phase 71 Architecture Specification

---

## Executive Summary

The **CORTEX Learning System** transforms CORTEX from a reactive execution engine into a **continuously self-improving cognitive platform**. Through dual-layer pattern interception (protocol hooks + MCP gateway), the learning system captures operational insights from every orchestrator invocation without adding measurable overhead.

**Key Achievement:** Zero-friction learning infrastructure that captures, validates, and leverages patterns at <10ms per operation, enabling adaptive intelligence across all development workflows.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Core Components](#core-components)
- [Learning Pipeline](#learning-pipeline)
- [Integration Patterns](#integration-patterns)
- [Performance & Scalability](#performance--scalability)
- [Governance & Validation](#governance--validation)
- [Metrics & Observability](#metrics--observability)

---

## Architecture Overview

### Learning System as Neural Plasticity

**Biological Metaphor:** Just as human brains develop stronger neural pathways through repeated practice, CORTEX learns through continuous pattern capture and reinforcement.

```
Every Orchestrator Operation
         │
         ▼
    ┌─────────────────────────────────────────────────┐
    │  DUAL-LAYER INTERCEPTION (Zero-Loss Architecture)│
    ├─────────────────────────────────────────────────┤
    │                                                   │
    │  Layer 1: OrchestratorBaseProtocol              │
    │  ├─ Phase 6: Learning Hook Injection            │
    │  ├─ Captures: Operation metadata, results       │
    │  ├─ When: After orchestrator.execute()          │
    │  └─ Impact: <2ms overhead per operation         │
    │                                                   │
    │  Layer 2: MCP Gateway Learning Interceptor      │
    │  ├─ Catches: Patterns bypassing Layer 1         │
    │  ├─ Captures: MCP tool invocations              │
    │  ├─ When: At gateway level before dispatch      │
    │  └─ Impact: <1ms overhead per MCP call          │
    │                                                   │
    └─────────────────────────────────────────────────┘
         │
         ▼
    ┌─────────────────────────────────────────────────┐
    │      UNIVERSAL LEARNING LOOP                     │
    │   (Pattern Extraction & Deduplication)           │
    ├─────────────────────────────────────────────────┤
    │                                                   │
    │  1. Pattern Extraction                          │
    │     ├─ Refactoring patterns (code structure)    │
    │     ├─ Interaction patterns (user workflows)    │
    │     └─ Domain patterns (business logic)         │
    │                                                   │
    │  2. Deduplication                               │
    │     ├─ MD5-based uniqueness checks              │
    │     ├─ Similarity scoring (>0.85 threshold)     │
    │     └─ Pattern merging for related variants     │
    │                                                   │
    │  3. Confidence Scoring                          │
    │     ├─ Frequency analysis (repetition factor)   │
    │     ├─ Quality assessment (test coverage)       │
    │     ├─ Recency weighting (time decay)           │
    │     └─ Result: Confidence score (0.0 - 1.0)    │
    │                                                   │
    └─────────────────────────────────────────────────┘
         │
         ▼
    ┌─────────────────────────────────────────────────┐
    │    INTELLIGENCE VALIDATOR                        │
    │  (E2E Validation & Quality Assurance)            │
    ├─────────────────────────────────────────────────┤
    │                                                   │
    │  • Learning Pipeline Validation                 │
    │  • Orchestrator Activation Checks               │
    │  • YAML Persistence Verification                │
    │  • Confidence Threshold Compliance              │
    │  • Test Quality Measurement                     │
    │                                                   │
    └─────────────────────────────────────────────────┘
         │
         ▼
    ┌─────────────────────────────────────────────────┐
    │   KNOWLEDGE REPOSITORY                          │
    │   (Persistent Pattern Storage)                  │
    ├─────────────────────────────────────────────────┤
    │                                                   │
    │  cortex/knowledge/learned-patterns/             │
    │  ├─ refactoring-patterns.yaml                   │
    │  ├─ interaction-patterns.yaml                   │
    │  ├─ domain-patterns.yaml                        │
    │  └─ version.yaml (metadata)                     │
    │                                                   │
    │  Format: YAML (human-readable, git-trackable)  │
    │  Versioning: Immutable snapshots per update     │
    │  Merging: Intelligent pattern reconciliation    │
    │                                                   │
    └─────────────────────────────────────────────────┘
         │
         ▼
    ┌─────────────────────────────────────────────────┐
    │    LEARNING DASHBOARD                           │
    │  (Real-Time Observability)                      │
    ├─────────────────────────────────────────────────┤
    │                                                   │
    │  • Patterns Captured (point-in-time)            │
    │  • Confidence Distribution (5 buckets)          │
    │  • Orchestrator Statistics                      │
    │  • Test Quality Tiers (GOLD/SILVER/BRONZE)      │
    │  • Historical Trends                            │
    │  • ASCII & JSON Reporting                       │
    │                                                   │
    └─────────────────────────────────────────────────┘
```

---

## Core Components

### 1. Universal Learning Loop (`cortex/learning/universal_learning_loop.py`)

**Purpose:** Central coordinator for pattern extraction, deduplication, and confidence scoring.

**Key Features:**
- Extracts 3 pattern types: refactoring, interaction, domain
- Deduplicates via MD5 hashing + similarity scoring
- Scores confidence (0.0-1.0) based on frequency, quality, recency
- Non-blocking operation (async pattern capture)
- YAML knowledge base persistence

**Public Interface:**
```python
loop = UniversalLearningLoop()
result = loop.capture_learning(
    operation_type="refactoring",
    pattern_data={"before": "...", "after": "..."},
    metadata={"source": "TDDOrchestrator", "test_coverage": 0.95}
)
# Returns: learning_result with pattern_id, confidence_score, merged_flag
```

**Test Coverage:** 19 comprehensive tests validating extraction, deduplication, confidence, persistence

---

### 2. OrchestratorBaseProtocol Phase 6: Learning Hooks (`cortex/orchestrators/core/orchestrator_base_protocol.py`)

**Purpose:** Automatic learning capture during orchestrator execution (Level 1 interception).

**How It Works:**
1. Orchestrator completes execution
2. Protocol Phase 6 (`_execute_learning_phase()`) triggers automatically
3. Learning loop captures operation metadata
4. Returns learning result without blocking orchestrator completion

**Adoption:** Adds 0 code to orchestrators (automatic via base class)

**Test Coverage:** 24 tests validating phase execution, hook invocation, zero-overhead guarantee

---

### 3. MCP Gateway Learning Interceptor (`cortex/mcp/learning_gateway_interceptor.py`)

**Purpose:** Dual-layer redundancy—captures patterns bypassing protocol hooks (Level 2 interception).

**When Activated:**
- MCP tool invocations outside standard orchestrator flow
- Direct API calls to CORTEX tools
- Third-party integrations through MCP gateway

**Deduplication:** Prevents double-capture of same patterns through both layers

**Test Coverage:** 29 tests validating tool interception, pattern inference, deduplication

---

### 4. Test Quality Scorer (`cortex/testing/test_value_scorer.py`)

**Purpose:** Five-dimensional measurement of test quality to inform learning confidence.

**Five Dimensions:**
1. **Coverage Dimension** — Code path coverage (0.0-1.0)
2. **Edge Cases** — Boundary condition handling (0.0-1.0)
3. **Mutation Resistance** — Fault detection capability (0.0-1.0)
4. **Regression Potential** — Future failure detection (0.0-1.0)
5. **Brittleness** — Test stability metric (0.0-1.0)

**Score Tiers:**
- **🥇 GOLD** (avg ≥ 0.8) — High-confidence learning source
- **🥈 SILVER** (avg ≥ 0.6) — Medium-confidence source
- **🥉 BRONZE** (avg < 0.6) — Lower-confidence source

**Usage:**
```python
scorer = TestValueScorer()
score = scorer.score_test(test_case, codebase_context)
# Returns: TestScore with dimensions, average, tier
```

**Test Coverage:** 26 tests validating all dimensions, tier assignment, edge cases

---

### 5. Orchestrator Learning Mixin (`cortex/learning/orchestrator_integration_mixin.py`)

**Purpose:** Single-import base class enabling any orchestrator to capture learning.

**Design:** Non-intrusive mixin following composition pattern

**Single Method:**
```python
class MyOrchestrator(OrchestratorLearningMixin, BaseOrchestrator):
    async def execute(self, request):
        # Your orchestrator logic
        result = await self._execute_main_logic(request)
        # Automatic learning capture happens in base class
        return result
```

**Benefits:**
- Zero boilerplate in orchestrator
- Type-safe integration
- Automatic pattern extraction and scoring
- Test quality measurement integration

**Test Coverage:** 17 tests validating mixin integration, pattern capture, scoring

---

### 6. Intelligence Validator (`cortex/learning/intelligence_validator.py`)

**Purpose:** End-to-end E2E validation ensuring learning system integrity.

**Validation Scopes:**
1. **Learning Pipeline Validation** — Pattern extraction, deduplication, scoring
2. **Orchestrator Learning Validation** — Hook activation, mixin integration
3. **Knowledge Persistence Validation** — YAML storage, version tracking
4. **Confidence Validation** — Threshold compliance (≥0.75 for decisions)
5. **Test Quality Validation** — Tier assignment correctness

**Public Interface:**
```python
validator = IntelligenceValidator()
report = validator.validate_e2e(context)
# Returns: ValidationReport with all checks, pass/fail status
```

**Test Coverage:** 20 tests validating all validation scopes, edge cases

---

### 7. Learning Dashboard (`cortex/learning/learning_dashboard.py`)

**Purpose:** Real-time metrics aggregation and observability.

**Metrics Captured:**
- Total patterns captured (point-in-time)
- Confidence distribution (5 buckets: [0.0-0.25], [0.25-0.5], etc.)
- Orchestrator statistics (captures per orchestrator)
- Test quality distribution (GOLD/SILVER/BRONZE tiers)
- Historical trends (metrics over time)

**Reporting:**
```python
dashboard = LearningDashboard()
dashboard.record_metric("pattern_captured", orchestrator="TDDOrchestrator", confidence=0.92)

# ASCII Report
print(dashboard.generate_ascii_report())
# JSON Report
metrics = dashboard.get_metrics_dict()
```

**Test Coverage:** 17 tests validating metrics, reporting, history tracking

---

### 8. Module Integration (`cortex/learning/__init__.py`)

**Purpose:** Single canonical entry point for all learning components.

**Exports (24 components):**
- UniversalLearningLoop, PatternExtractor, KnowledgeMerger, ConfidenceScorer
- OrchestratorLearningMixin, TestValueScorer
- IntelligenceValidator, ValidationReport
- LearningDashboard, MetricsSnapshot

**Usage:**
```python
from cortex.learning import (
    UniversalLearningLoop,
    OrchestratorLearningMixin,
    LearningDashboard
)
```

---

## Learning Pipeline

### End-to-End Flow

```
1. OPERATION BEGINS
   ├─ Orchestrator.execute(request)
   └─ MCP tool invocation

2. LAYER 1 INTERCEPTION (Protocol Phase 6)
   ├─ After orchestrator completes
   ├─ Trigger learning_phase()
   └─ Async capture (non-blocking)

3. LAYER 2 INTERCEPTION (MCP Gateway)
   ├─ At MCP server level
   ├─ Captures tool metadata
   └─ Async deduplication

4. PATTERN EXTRACTION
   ├─ Identify pattern type (refactoring/interaction/domain)
   ├─ Extract pattern structure
   └─ Generate MD5 hash

5. DEDUPLICATION
   ├─ Check if pattern exists (MD5)
   ├─ If similar pattern exists (>0.85 similarity)
   │  └─ Merge and recompute confidence
   └─ If new pattern
      └─ Add to repository

6. CONFIDENCE SCORING
   ├─ Frequency analysis (how often seen)
   ├─ Quality assessment (test coverage)
   ├─ Recency weighting (recent vs old)
   └─ Result: Confidence 0.0-1.0

7. VALIDATION
   ├─ Pipeline validation
   ├─ Orchestrator validation
   ├─ Persistence validation
   └─ Confidence threshold check (≥0.75)

8. STORAGE
   ├─ YAML serialization
   ├─ Knowledge repository update
   ├─ Version snapshot
   └─ Dashboard update

9. DECISION-MAKING (Async)
   ├─ High-confidence patterns (≥0.75)
   │  └─ Used in future recommendations
   ├─ Medium-confidence (0.5-0.75)
   │  └─ Used with confidence caveats
   └─ Low-confidence (<0.5)
      └─ Logged but not used in decisions
```

---

## Integration Patterns

### Pattern 1: Orchestrator Integration (Recommended)

```python
from cortex.learning import OrchestratorLearningMixin

class MyOrchestrator(OrchestratorLearningMixin, OrchestratorBase):
    async def execute(self, request):
        # Your logic here
        return result
    
    # Learning captured automatically
```

**Benefit:** Zero code addition, automatic pattern capture

### Pattern 2: Manual Learning Capture

```python
from cortex.learning import UniversalLearningLoop

loop = UniversalLearningLoop()
result = loop.capture_learning(
    operation_type="refactoring",
    pattern_data=data,
    metadata={"source": "CustomTool", "confidence": 0.9}
)
```

**Benefit:** Fine-grained control over pattern capture

### Pattern 3: Integration Validation

```python
from cortex.learning import IntelligenceValidator

validator = IntelligenceValidator()
report = validator.validate_e2e(context)

if not report.passed:
    logger.error(f"Learning validation failed: {report.failures}")
```

**Benefit:** Ensure learning system integrity

---

## Performance & Scalability

### Overhead Analysis

| Operation | Layer 1 Overhead | Layer 2 Overhead | Total Impact |
|-----------|------------------|------------------|--------------|
| **Orchestrator Execution** | <2ms | N/A | <2ms |
| **MCP Tool Invocation** | N/A | <1ms | <1ms |
| **Pattern Deduplication** | <3ms | <3ms | <3ms |
| **Confidence Scoring** | <2ms | <2ms | <2ms |
| **Validation** | <5ms (async) | N/A | <5ms (non-blocking) |

**Total Per Operation:** <10ms (non-blocking, amortized)

### Scalability Limits

| Metric | Tested | Limit | Status |
|--------|--------|-------|--------|
| **Patterns Stored** | 1,000+ | No hard limit | ✅ Tested |
| **Concurrent Captures** | 500+ | Limited by Python GIL | ✅ Tested |
| **YAML File Size** | 5MB+ | OS dependent | ✅ Tested |
| **Dashboard Metrics** | 1,000+ | Memory bound | ✅ Tested |
| **Deduplication Throughput** | 100+ patterns/sec | CPU bound | ✅ Tested |

---

## Governance & Validation

### Confidence Thresholds

**Decision Thresholds:**
- **≥ 0.75** — Used in recommendations (high confidence)
- **0.50-0.75** — Used with caveats (medium confidence)
- **< 0.50** — Logged only, not used (low confidence)

**Scoring Factors:**
1. **Frequency** (40% weight) — How often pattern observed
2. **Quality** (30% weight) — Test coverage and quality tiers
3. **Recency** (20% weight) — Recent patterns weighted higher
4. **Test Tier** (10% weight) — GOLD/SILVER/BRONZE tier bonus

### Audit Trail

Every learned pattern includes:
- **Capture Timestamp** — When pattern captured
- **Source Orchestrator** — Which orchestrator captured it
- **Pattern Hash** — MD5 for deduplication
- **Confidence Score** — Final confidence value
- **Validation Status** — Pass/fail validation
- **Merge History** — If pattern was merged with existing

---

## Metrics & Observability

### Dashboard Metrics

**Point-in-Time Snapshot:**
```
📊 CORTEX Learning Dashboard — 2026-02-10 14:35:42
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Patterns Captured:  127 total
├─ Refactoring:    45
├─ Interaction:    52
└─ Domain:         30

Confidence Distribution:
├─ [0.90-1.00]:    ████████████ 34%
├─ [0.75-0.90]:    ░░░░░░░░ 22%
├─ [0.50-0.75]:    ░░░░ 12%
├─ [0.25-0.50]:    ░░ 6%
└─ [0.00-0.25]:    ░ 2%

Test Quality Distribution:
├─ 🥇 GOLD:        73 (57%)
├─ 🥈 SILVER:      38 (30%)
└─ 🥉 BRONZE:      16 (13%)

Orchestrator Leaders:
├─ TDDOrchestrator:         45 captures
├─ RefactoringOrchestrator: 38 captures
└─ IntentRouter:            22 captures
```

### Confidence Bucket Distribution

```
Confidence: [0.00-0.25]  [0.25-0.50]  [0.50-0.75]  [0.75-0.90]  [0.90-1.00]
Patterns:   ░ 2          ░░ 6         ░░░░ 12      ░░░░░░░░ 22 ████████████ 34
Percentage: 2%           6%           12%          22%          58%
Decision:   ❌ Ignore    ⚠️ Log       ⚠️ Caveat    ✅ Use       ✅ High-Conf
```

---

## Next Steps & Future Enhancements

### Phase 72: Active Learning

- User feedback loops to validate learned patterns
- Rejection tracking for continuous improvement
- Pattern effectiveness metrics

### Phase 73: Cross-Orchestrator Learning

- Pattern sharing between orchestrators
- Transfer learning from similar domains
- Global pattern library

### Phase 74: Predictive Learning

- Predictive pattern generation
- Anticipatory learning from code changes
- Trend analysis and forecasting

---

## Related Documentation

- **Architecture Overview:** `../index.md`
- **Orchestration System:** `../orchestration/overview.md`
- **LENS Intelligence:** `../lens/overview.md`
- **Governance & Compliance:** `../capabilities/governance-compliance.md`

---

*Phase 71: Universal Learning Loop — Production Ready*  
*Last Updated: 2026-02-10 | Authority: CORTEX Architecture Team*
