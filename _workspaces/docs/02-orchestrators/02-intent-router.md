# Intent Router

**Status:** Production Ready | **Version:** 1.0.0 | **Category:** Core Orchestrators | **Module:** `cortex/orchestrators/core/intent_router.py`

---

## Overview

The **Intent Router** is a sophisticated intent classification and routing engine that serves as **Stage 2** of the MasterOrchestrator's 4-stage orchestration pipeline. It analyzes user requests through the **LENS protocol** to determine the correct execution path for different operation types.

### Purpose

- Parse user requests through LENS framework (Language, Examination, Navigation, Synthesis)
- Classify operations into intent types (IMPLEMENT, FIX, REFACTOR)
- Route operations to appropriate handler/orchestrator
- Score routing confidence (0.0-1.0)
- Cache identical routing decisions
- Maintain audit trail of all routing decisions

---

## Architecture

### Design Pattern: Strategy + Chain of Responsibility

```
┌──────────────────────┐
│  Operation Request   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────────────┐
│  Intent Router                   │
│  (Strategy + Chain of Resp)      │
└──────────┬───────────────────────┘
           │
           ├─ LENS Protocol
           │  └─ Language Analysis
           │  └─ Examination (AST)
           │  └─ Navigation (Git)
           │  └─ Synthesis (Context)
           │
           ├─ Intent Classification
           │  ├─ IMPLEMENT keywords
           │  ├─ FIX keywords
           │  └─ REFACTOR keywords
           │
           ├─ Confidence Scoring
           │  ├─ Keyword matching
           │  ├─ Context relevance
           │  └─ Historical accuracy
           │
           └─ Route Selection
              ├─ Primary route
              ├─ Fallback routes
              └─ Ambiguity handling
```

### Key Components

1. **Intent Classifier**
   - Analyzes operation description and keywords
   - Maps keywords to intent types
   - Computes primary intent from keyword distribution
   - Returns confidence score

2. **Context Analyzer**
   - Extracts domain from operation
   - Identifies urgency level
   - Parses user intent
   - Gathers additional metadata

3. **Routing Engine**
   - Selects handler based on intent & domain
   - Implements routing rules
   - Provides fallback options
   - Records decision

4. **Decision Cache**
   - LRU cache of routing decisions (128 entries)
   - Speeds up repeated operations
   - Invalidates stale entries
   - Reduces routing overhead

5. **Audit Trail**
   - Logs all routing decisions
   - Records confidence scores
   - Tracks routing accuracy
   - Enables debugging

---

## How It Works

### LENS Protocol (Intent Analysis)

```
┌─────────────────────────────────────────┐
│         LENS Protocol Flow              │
└─────────────────────────────────────────┘

1. LANGUAGE (Natural Language Analysis)
   ├─ Tokenize operation description
   ├─ Extract keywords
   ├─ Identify tense and mood
   └─ Compute keyword frequency

2. EXAMINATION (AST & Code Analysis)
   ├─ Parse code structure
   ├─ Analyze affected modules
   ├─ Identify complexity
   └─ Assess scope (file/module/system)

3. NAVIGATION (Git & History Analysis)
   ├─ Review git history
   ├─ Find related changes
   ├─ Identify pattern of changes
   └─ Extract historical context

4. SYNTHESIS (Context Aggregation)
   ├─ Merge all analysis signals
   ├─ Weight each signal
   ├─ Compute final confidence
   └─ Select intent type
```

### Intent Classification Algorithm

```python
def classify_intent(description: str, keywords: List[str]) -> IntentType:
    """
    Classify operation intent using keyword scoring.
    
    Algorithm:
    1. Count IMPLEMENT keywords in description
    2. Count FIX keywords in description
    3. Count REFACTOR keywords in description
    4. Return intent type with highest count
    5. If tie, apply disambiguation logic
    """
    
    implement_score = count_keywords(description, IMPLEMENT_KEYWORDS)
    fix_score = count_keywords(description, FIX_KEYWORDS)
    refactor_score = count_keywords(description, REFACTOR_KEYWORDS)
    
    scores = {
        IntentType.IMPLEMENT: implement_score,
        IntentType.FIX: fix_score,
        IntentType.REFACTOR: refactor_score,
    }
    
    max_intent = max(scores, key=scores.get)
    confidence = scores[max_intent] / max(sum(scores.values()), 1)
    
    return max_intent, confidence
```

### Confidence Scoring

```
Confidence Score = (keyword_match_confidence * 0.4) +
                   (context_relevance * 0.3) +
                   (historical_accuracy * 0.2) +
                   (domain_fit * 0.1)

Range: 0.0 (no confidence) to 1.0 (high confidence)

Classification:
- 0.9-1.0: Very High confidence - auto-route
- 0.7-0.9: High confidence - route with monitoring
- 0.5-0.7: Medium confidence - route with fallback
- 0.3-0.5: Low confidence - disambiguate
- 0.0-0.3: No confidence - require manual routing
```

### Routing Decision Flow

```
┌─ Incoming Operation
│
├─ Check confidence ≥ 0.7?
│  ├─ YES → Auto-route to handler
│  └─ NO → Invoke disambiguation
│
├─ Route to primary handler
│  ├─ Success? → Return decision
│  └─ Failure? → Try fallback
│
├─ Log routing decision
│  ├─ Record confidence
│  ├─ Record handler selection
│  └─ Cache decision
│
└─ Return RoutingDecision
```

---

## How to Use It

### Basic Usage

```python
from cortex.orchestrators.core.intent_router import IntentRouter

# Initialize router
router = IntentRouter()

# Create routing context
context = {
    "operation": "fix_race_condition",
    "description": "Fix race condition in Master Orchestrator",
    "keywords": ["bug", "race condition", "fix"],
    "domain": "core",
    "urgency": "high"
}

# Get routing decision
decision = router.route(context)

print(f"Intent Type: {decision.intent_type}")
print(f"Target Handler: {decision.target_handler}")
print(f"Confidence: {decision.confidence_score}")
print(f"Reasoning: {decision.reasoning}")
```

### Advanced Usage Patterns

#### Pattern 1: Explicit Intent Specification
```python
# Specify intent explicitly to override detection
decision = router.route(
    context=context,
    explicit_intent=IntentType.FIX  # Override detection
)
```

#### Pattern 2: Custom Keyword Sets
```python
# Use custom keywords for domain-specific routing
router.add_custom_keywords(
    intent_type=IntentType.IMPLEMENT,
    keywords=["create", "add", "provision"]
)

decision = router.route(context)
```

#### Pattern 3: Fallback Chain
```python
# Get multiple routing options (primary + fallbacks)
decisions = router.get_routing_options(context)

for decision in decisions:
    print(f"Option: {decision.target_handler} "
          f"(confidence: {decision.confidence_score})")
```

#### Pattern 4: Cache Management
```python
# Clear cache to force re-routing
router.clear_cache()

# Or clear specific entries
router.invalidate_cache_entry(operation_id)

# Check cache statistics
stats = router.get_cache_stats()
print(f"Cache hit rate: {stats['hit_rate']}")
```

---

## Intent Types

### 1. IMPLEMENT
**Purpose:** New feature development or creation

**Keywords:**
- create, add, new, implement, develop
- build, construct, establish, introduce
- feature, enhancement, capability

**Routing Targets:**
- BuilderOrchestrator
- DevelopmentOrchestrator
- ImplementationOrchestrator

**Characteristics:**
- Increases codebase size
- Adds new functionality
- Requires design decisions
- Often requires testing
- May affect other components

### 2. FIX
**Purpose:** Bug fixes and issue resolution

**Keywords:**
- fix, bug, issue, error, problem
- crash, fail, broken, resolve, correct
- repair, patch, race condition

**Routing Targets:**
- FixOrchestrator
- DebugOrchestrator
- HotfixOrchestrator

**Characteristics:**
- Corrects existing behavior
- Usually minimal scope
- Often urgent
- Requires root cause analysis
- May require backport

### 3. REFACTOR
**Purpose:** Code improvement and restructuring

**Keywords:**
- refactor, improve, cleanup, restructure
- simplify, optimize, clean, modernize
- reorganize, rewrite, redesign, performance

**Routing Targets:**
- RefactoringOrchestrator
- OptimizationOrchestrator
- StructuralOrchestrator

**Characteristics:**
- Preserves functionality
- Improves code quality
- Often improves performance
- Requires regression testing
- May span multiple files

---

## Integration Points

### Dependencies

- **EnhancedAuditLogger**: Audit trail logging
- **MasterOrchestrator**: Result aggregation
- **KnowledgeRepository**: Historical data
- **GovernanceRegistry**: Rule validation

### Dependents

- **MasterOrchestrator**: Uses for Stage 2 routing
- **WorkflowOrchestrator**: Uses for intent detection
- **Custom Handlers**: All specialized orchestrators

### MCP Tools Exposed

| Tool | Description | Parameters |
|------|-------------|------------|
| `route_operation` | Route operation by intent | context |
| `classify_intent` | Classify operation intent | description, keywords |
| `get_routing_options` | Get all routing options | context |
| `score_routing_decision` | Score a routing decision | operation, handler |
| `validate_intent` | Validate intent specification | intent_type, operation |

---

## Design Principles

### 1. Separation of Concerns
- Intent classification separate from routing
- Context analysis separate from decision-making
- Audit logging orthogonal to routing logic

### 2. Extensibility
- New intent types can be added
- Custom keyword sets supported
- Routing strategies pluggable
- Handlers can be registered

### 3. Reliability
- Confidence scoring prevents misrouting
- Fallback options ensure alternatives
- Audit trail enables debugging
- Graceful degradation

### 4. Performance
- LRU caching reduces overhead
- Keyword matching is O(n)
- Decision reuse for identical contexts
- Minimal I/O

---

## Governance Rules Enforced

| Rule | Impact |
|------|--------|
| CORE-008 | TDD: intent classification tested |
| CORE-011 | Type hints on all methods |
| CORE-012 | Docstrings required |
| CORE-013 | No bare except clauses |
| CORE-027 | Audit trail logging |

---

## Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| Intent classification | 5-10ms | Keyword scanning |
| Confidence scoring | 2-5ms | Weighted calculation |
| Routing decision | 1-3ms | Lookup + selection |
| Cache hit | <1ms | Direct return |
| Cache miss | 10-15ms | Full analysis |

---

## Testing

### Test Coverage

- **Intent Classification:** 98% coverage
- **Confidence Scoring:** 95% coverage
- **Routing Logic:** 96% coverage
- **Cache Management:** 100% coverage
- **Audit Trail:** 99% coverage

### Key Test Scenarios

1. **Correct Intent Detection**
   - IMPLEMENT operations identified
   - FIX operations identified
   - REFACTOR operations identified

2. **Confidence Scoring**
   - High confidence for clear intents
   - Low confidence for ambiguous operations
   - Proper thresholding

3. **Fallback Routing**
   - Primary route selected
   - Fallback options available
   - Graceful degradation

4. **Cache Behavior**
   - Cache hits work correctly
   - Cache invalidation works
   - TTL expiration works

---

## Best Practices

### DO ✅

- Use LENS protocol for full context analysis
- Check confidence score before auto-routing
- Implement fallback routes for critical operations
- Cache routing decisions for repeated operations
- Log all routing decisions for audit
- Use custom keywords for domain-specific operations
- Validate intent type against operation
- Monitor routing accuracy

### DON'T ❌

- Auto-route operations with low confidence (<0.7)
- Ignore fallback options
- Rely solely on keywords
- Skip audit logging
- Neglect cache management
- Over-customize keyword detection
- Execute without governance validation
- Assume routing is always correct

---

## Troubleshooting

### Issue: Low Confidence Scores

**Cause:** Ambiguous operation descriptions
**Solution:** 
- Provide more specific keywords
- Add domain context
- Use explicit intent specification

### Issue: Incorrect Intent Detection

**Cause:** Operation description uses unexpected keywords
**Solution:**
- Extend keyword set for domain
- Use explicit intent
- Provide additional context

### Issue: Cache Performance Issues

**Cause:** Cache miss rate too high
**Solution:**
- Increase cache size
- Check for cache invalidation issues
- Monitor cache hit rate

---

## Example Workflows

### Workflow 1: Fix a Bug

```python
context = {
    "operation": "fix_memory_leak",
    "description": "Fix memory leak in state manager",
    "keywords": ["bug", "memory", "leak", "fix"],
    "domain": "core",
    "urgency": "high"
}

decision = router.route(context)
# Results: IntentType.FIX, FixOrchestrator, 0.95 confidence
```

### Workflow 2: Ambiguous Operation

```python
context = {
    "operation": "update_system",
    "description": "Update system configuration",
    "keywords": ["update"],  # Ambiguous keyword
    "domain": "infrastructure"
}

decision = router.route(context)
# Results: Low confidence, multiple options provided
# User must disambiguate
```

### Workflow 3: Domain-Specific Routing

```python
# Financial domain with custom keywords
router.add_custom_keywords(
    domain="financial",
    keywords=["transaction", "payment", "reconciliation"]
)

context = {
    "operation": "process_transaction",
    "description": "Process customer payment transaction",
    "domain": "financial",
    "urgency": "critical"
}

decision = router.route(context)
# Routes to FinancialOrchestrator
```

---

## Related Documentation

- 📖 [Master Orchestrator](01-master-orchestrator.md) - Stage 1 coordinator
- 📖 [Workflow Orchestrator](03-workflow-orchestrator.md) - 5-stage workflow
- 📖 [LENS Protocol](../patterns/lens-protocol.md) - Intent analysis framework
- 📖 [Confidence Scoring](../patterns/confidence-scoring.md) - Scoring mechanism

---

## Copyright & License

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

CORTEX Framework - Intent Router Module
Status: Production Ready | Version: 1.0.0

---

**Last Updated:** 2026-01-22 | **Author:** CORTEX Documentation Generator
