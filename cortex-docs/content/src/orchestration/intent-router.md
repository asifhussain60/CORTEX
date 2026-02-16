# Intent Router

---
title: Intent Router - CORTEX Request Classification Engine
type: explanation
audience: [Product Owners, Software Developers]
word_count: 1200
last_verified: 2026-02-15
source_of_truth: cortex/intent_router/ + cortex-registry/master/
format: diátaxis-explanation
voice: third-person-blended
phase: Production (v8.1)
related_orchestrators: [MasterOrchestrator, TDDOrchestrator, LENSSynthesis]
---

> **Notice:** Intent classification represents a continuously improving system using LENS intelligence. Classification accuracy improves over time as CORTEX learns from more interactions. Performance characteristics reflect production deployment as of v8.1. Organizations should validate routing accuracy against their specific use case patterns.

---

**Category:** Core Orchestrator  
**Priority:** 20  
**Updated:** 2026-02-15

---

## Overview

### The Logistics Coordinator

Think of an airport security checkpoint — every passenger must pass through it, and within seconds, security staff classify and route them to the correct terminal. Business class passengers go to Priority Lane. International travelers go to Terminal 3. Domestic travelers go to Terminal 1.

The **IntentRouter** is CORTEX's security checkpoint. Every user request passes through it, and within **15 milliseconds**, it classifies the intent and routes the signal to the correct specialist orchestrator. A request to "implement login" routes to the TDDOrchestrator. A request to "refactor this module" routes to the RefactoringOrchestrator. A request to "analyze security" flows to the UnifiedAnalysisOrchestrator.

The IntentRouter uses a **multi-factor scoring system** to make routing decisions — combining keyword signals (30%), contextual cues from LENS (25%), knowledge base alignment (20%), historical accuracy (15%), and request clarity (10%).

**Key Facts:**
- **Category:** Core (essential request gateway)
- **Priority:** 20 (second only to MasterOrchestrator)
- **Real-World Analogy:** Airport security checkpoint — central classification hub
- **Capabilities:** intent_classification, routing
- **Dependencies:** MasterOrchestrator
- **Classification Speed:** ~15ms (96.2% accuracy)

---

## Intent Classification

### Supported Intent Types

Each intent maps to a specific orchestrator. The IntentRouter maintains this routing table:

| Intent | Keywords | Target Orchestrator | Real-World Analogy |
|--------|----------|---------------------|--------------------|
| **IMPLEMENT** | implement, create, build, add | TDDOrchestrator | Construction crew — disciplined building |
| **FIX** | fix, bug, error, issue | TDDOrchestrator | Repair technician — corrective action |
| **REFACTOR** | refactor, improve, optimize | RefactoringOrchestrator | Renovation specialist — restructuring |
| **ANALYZE** | analyze, review, examine | UnifiedAnalysisOrchestrator | Building inspector — examination |
| **TEST** | test, verify, validate | TDDOrchestrator | Quality assurance — verification |
| **ONBOARD** | onboard, setup, initialize | UnifiedOnboardingOrchestrator | Initial setup — first-time configuration |
| **PLAN** | plan, roadmap, strategy | PlanningOrchestrator | Project manager — strategic planning |
| **QUERY** | what, how, why, explain | UnifiedDiscoveryOrchestrator | Research librarian — information discovery |
| **CONVERSATION** | chat, discuss, talk | ConversationOrchestrator | Receptionist — interactive communication |
| **WORKFLOW** | workflow, sequence, pipeline | WorkflowOrchestrator | Assembly line coordinator — process sequencing |
| **QUALITY** | audit, compliance, review | UnifiedQualityAssuranceOrchestrator | Compliance auditor — standards enforcement |
| **UNKNOWN** | (no match) | MasterOrchestrator | General manager — fallback coordination |

### Classification Algorithm

```python
def classify_intent(self, request: str) -> IntentType:
    """
    Classify user request into intent type.
    
    Uses multi-stage classification:
    1. Keyword matching (fast)
    2. LENS context analysis (accurate)
    3. Knowledge base alignment (domain-aware)
    4. Historical pattern matching (learned)
    """
    
    # Stage 1: Fast keyword matching (30% weight)
    keyword_score = self._keyword_match(request)
    
    # Stage 2: LENS context (25% weight)
    lens_context = self.lens.analyze(request, quick=True)
    context_score = self._context_score(lens_context)
    
    # Stage 3: Knowledge base (20% weight)
    kb_score = self.knowledge_base.align(request)
    
    # Stage 4: Historical accuracy (15% weight)
    history_score = self._historical_match(request)
    
    # Stage 5: Clarity check (10% weight)
    clarity_score = self._clarity_check(request)
    
    # Weighted combination
    total_score = (
        keyword_score * 0.30 +
        context_score * 0.25 +
        kb_score * 0.20 +
        history_score * 0.15 +
        clarity_score * 0.10
    )
    
    # Return highest-scoring intent
    return self._select_intent(total_score)
```

---

## Routing Strategy

### Priority-Based Routing

Orchestrators are registered with priorities (10-195). IntentRouter routes to the highest-priority orchestrator that matches the intent:

```
Priority 10:  MasterOrchestrator (fallback)
Priority 20:  IntentRouter (self-reference for meta-operations)
Priority 30:  InteractionOrchestrator (communication)
Priority 40:  LENSSynthesis (intelligence)
Priority 50:  EnforcementOrchestrator (governance)
Priority 55:  TDDOrchestrator (implementation)
Priority 60:  RefactoringOrchestrator (code improvement)
...and so on
```

### Confidence Threshold

- **High Confidence (>0.85):** Route immediately
- **Medium Confidence (0.6-0.85):** Add clarifying context
- **Low Confidence (<0.6):** Route to MasterOrchestrator for disambiguation

### Fallback Behavior

If no orchestrator matches the intent:
1. Route to MasterOrchestrator (Priority 10)
2. Log ambiguous request for learning
3. Request user clarification if needed

---

## Performance Characteristics

### Latency Breakdown

| Stage | Time | Description |
|-------|------|-------------|
| Keyword matching | 2-5ms | Fast regex/token matching |
| LENS quick analysis | 5-10ms | Lightweight context scan |
| Knowledge base lookup | 2-4ms | Redis cache hit |
| Historical matching | 1-2ms | SQLite query |
| Clarity scoring | 1-2ms | Syntax analysis |
| **Total** | **11-23ms** | **Average: 15ms** |

### Accuracy Metrics

| Metric | Target | Current |
|--------|--------|---------|
| **Classification Accuracy** | 95%+ | 96.2% |
| **False Positives** | <3% | 2.1% |
| **Ambiguous Requests** | <5% | 3.8% |
| **Latency P95** | <25ms | 18ms |

---

## Integration Points

### Upstream Dependencies

- **MasterOrchestrator:** Receives requests, manages lifecycle
- **InteractionOrchestrator:** Provides request parsing

### Downstream Targets

- **TDDOrchestrator:** IMPLEMENT, FIX, TEST intents
- **RefactoringOrchestrator:** REFACTOR intents
- **UnifiedAnalysisOrchestrator:** ANALYZE intents
- **UnifiedQualityAssuranceOrchestrator:** QUALITY, AUDIT intents
- **PlanningOrchestrator:** PLAN intents
- **WorkflowOrchestrator:** WORKFLOW intents
- **ConversationOrchestrator:** CONVERSATION intents
- **UnifiedDiscoveryOrchestrator:** QUERY intents
- **UnifiedOnboardingOrchestrator:** ONBOARD intents

### Data Flow

```
User Request
    ↓
MasterOrchestrator
    ↓
IntentRouter (classify + route)
    ↓
Target Orchestrator (execute)
    ↓
MasterOrchestrator (response)
    ↓
User Response
```

---

## Error Handling

### Classification Failures

**Scenario:** Unable to classify with confidence

**Action:**
1. Log to `intelligence_audit.db`
2. Route to MasterOrchestrator (fallback)
3. Add to learning corpus for future improvement

**User Impact:** Graceful degradation (still processed, may be slower)

### Routing Failures

**Scenario:** Target orchestrator unavailable

**Action:**
1. Check orchestrator health status
2. Attempt alternate orchestrator (if available)
3. If all fail, return error to user
4. Log incident for monitoring

**User Impact:** Clear error message with resolution steps

---

## Configuration

### Routing Rules

Location: `cortex-registry/master/orchestrator-routing.yaml`

```yaml
routing_rules:
  - intent: IMPLEMENT
    target: TDDOrchestrator
    priority: 55
    confidence_threshold: 0.7
    
  - intent: REFACTOR
    target: RefactoringOrchestrator
    priority: 60
    confidence_threshold: 0.75
    
  # ... additional rules
```

### Tuning Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `keyword_weight` | 0.30 | 0.0-1.0 | Keyword matching importance |
| `context_weight` | 0.25 | 0.0-1.0 | LENS context importance |
| `kb_weight` | 0.20 | 0.0-1.0 | Knowledge base importance |
| `history_weight` | 0.15 | 0.0-1.0 | Historical pattern importance |
| `clarity_weight` | 0.10 | 0.0-1.0 | Request clarity importance |
| `confidence_threshold` | 0.60 | 0.0-1.0 | Minimum confidence to route |

---

## Learning & Adaptation

### Historical Pattern Matching

IntentRouter learns from past classifications:

```python
class HistoricalMatcher:
    """Learn from past routing decisions."""
    
    def record_routing(self, request: str, intent: IntentType, 
                      success: bool, user_feedback: Optional[str]):
        """Record routing decision and outcome."""
        self.db.insert({
            'request_hash': hash(request),
            'intent': intent,
            'success': success,
            'feedback': user_feedback,
            'timestamp': now()
        })
    
    def learn_patterns(self):
        """Periodic learning from historical data."""
        patterns = self.db.query("""
            SELECT request_pattern, intent, 
                   AVG(success) as success_rate
            FROM routing_history
            GROUP BY request_pattern, intent
            HAVING COUNT(*) >= 5
        """)
        
        # Update classification weights
        for pattern in patterns:
            if pattern.success_rate > 0.9:
                self.boost_confidence(pattern)
            elif pattern.success_rate < 0.6:
                self.reduce_confidence(pattern)
```

### Continuous Improvement

- **Daily:** Analyze routing accuracy from previous 24h
- **Weekly:** Retrain classification model with new data
- **Monthly:** Review and update routing rules

---

## Testing

### Unit Tests

```python
def test_intent_classification():
    router = IntentRouter()
    
    # Test IMPLEMENT intent
    assert router.classify("implement user login") == IntentType.IMPLEMENT
    
    # Test REFACTOR intent
    assert router.classify("refactor authentication module") == IntentType.REFACTOR
    
    # Test ANALYZE intent
    assert router.classify("analyze security vulnerabilities") == IntentType.ANALYZE
    
    # Test ambiguous request
    result = router.classify("help me with code")
    assert result.confidence < 0.6  # Should trigger clarification
```

### Integration Tests

```python
def test_end_to_end_routing():
    request = "implement payment processing"
    
    # Should route to TDDOrchestrator
    orchestrator = intent_router.route(request)
    
    assert orchestrator.name == "TDDOrchestrator"
    assert orchestrator.priority == 55
    assert orchestrator.is_available()
```

---

## Monitoring

### Key Metrics

| Metric | Collection | Alert Threshold |
|--------|------------|-----------------|
| Classification Latency | Per-request | P95 > 30ms |
| Accuracy Rate | Daily aggregate | <94% |
| Ambiguous Requests | Per-request | >8% daily |
| Fallback Rate | Per-request | >10% daily |
| Orchestrator Availability | Continuous | <99% |

### Dashboards

**Grafana Panel:** Intent Router Performance
- Classification latency histogram
- Accuracy rate time series
- Intent distribution pie chart
- Fallback rate gauge

---

## See Also

- [Master Orchestrator](./master-orchestrator.md)
- [TDD Orchestrator](./tdd-orchestrator.md)
- [Orchestration Overview](./overview.md)
- [End-to-End Flow](./end-to-end-flow.md)

---

*Generated by CORTEX Architecture Team | Updated 2026-02-14*
