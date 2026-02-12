# IntentRouter

**Purpose:** Detailed documentation of the intent classification and routing orchestrator  
**Audience:** Architects, Developers  
**Last Updated:** 2026-02-10

---

## Table of Contents

- [Overview](#overview)
- [Intent Classification](#intent-classification)
- [Routing Logic](#routing-logic)
- [Composite Intent Detection](#composite-intent-detection)
- [Confidence Scoring](#confidence-scoring)
- [Inputs and Outputs](#inputs-and-outputs)
- [Related Documents](#related-documents)

---

## Overview

The **IntentRouter** analyzes operation context and determines the appropriate execution path for different operation types. It serves as the intelligence layer for request routing.

**Key Facts:**
- **Category:** Core
- **Priority:** 20
- **Capabilities:** intent_classification, routing
- **Dependencies:** MasterOrchestrator

---

## Intent Classification

### Supported Intent Types

| Intent | Keywords | Target Orchestrator |
|--------|----------|---------------------|
| **IMPLEMENT** | implement, create, build, add, develop | TDDOrchestrator |
| **FIX** | fix, bug, error, issue, problem | TDDOrchestrator |
| **REFACTOR** | refactor, improve, optimize, clean | RefactoringOrchestrator |
| **ANALYZE** | analyze, review, examine, inspect | LENSOrchestrator |
| **DOCUMENT** | document, docs, readme, explain | DocumentationOrchestrator |
| **TEST** | test, verify, validate, check | TDDOrchestrator |
| **DEPLOY** | deploy, release, publish, ship | DeploymentOrchestrator |
| **GOVERNANCE** | audit, compliance, governance | GovernanceOrchestrator |
| **QUERY** | what, how, why, explain (questions) | KnowledgeOrchestrator |
| **VALIDATE** | validate, verify, ensure | ValidationOrchestrator |
| **MIGRATE** | migrate, upgrade, convert | MigrationOrchestrator |
| **ONBOARD** | onboard, setup, initialize | OnboardingOrchestrator |
| **PLAN** | plan, phase, roadmap, schedule | PlanningOrchestrator |
| **UNKNOWN** | (no match) | MasterOrchestrator |

### Classification Algorithm

```python
def classify_intent(self, request: str) -> IntentType:
    """
    Classify user request into intent type.
    
    Uses multi-stage classification:
    1. Keyword matching (fast)
    2. Context enhancement (LENS)
    3. Historical pattern matching
    """
    request_lower = request.lower()
    scores: Dict[IntentType, float] = {}
    
    # Stage 1: Keyword matching
    for intent, keywords in self.INTENT_KEYWORDS.items():
        match_count = sum(1 for kw in keywords if kw in request_lower)
        if match_count > 0:
            scores[intent] = match_count / len(keywords)
    
    # Stage 2: Context enhancement
    if self.lens_context:
        context_boost = self._calculate_context_boost(
            request_lower,
            self.lens_context
        )
        for intent, boost in context_boost.items():
            scores[intent] = scores.get(intent, 0) + boost
    
    # Stage 3: Historical patterns
    historical_boost = self._get_historical_boost(request_lower)
    for intent, boost in historical_boost.items():
        scores[intent] = scores.get(intent, 0) + boost
    
    # Return highest scoring intent
    if scores:
        return max(scores, key=scores.get)
    return IntentType.UNKNOWN
```

---

## Routing Logic

### Routing Decision Process

```
┌─────────────────────────────────────────────────────────────────┐
│                      ROUTING DECISION                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Input: User Request + Context                                   │
│                              │                                   │
│                              ▼                                   │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                 Intent Classification                      │ │
│  │  "Implement user auth" → IMPLEMENT (0.9)                  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │               Orchestrator Lookup                          │ │
│  │  IMPLEMENT → TDDOrchestrator                              │ │
│  │  Fallback: [WorkflowOrchestrator, MasterOrchestrator]     │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │               Availability Check                           │ │
│  │  TDDOrchestrator: ✅ Available                            │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │               Confidence Calculation                       │ │
│  │  Keyword: 0.3 + LENS: 0.25 + Knowledge: 0.2              │ │
│  │  + Historical: 0.15 + Clarity: 0.1 = 0.92               │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  Output: RoutingDecision                                         │
│  • intent_type: IMPLEMENT                                        │
│  • target_handler: TDDOrchestrator                              │
│  • confidence_score: 0.92                                        │
│  • reasoning: "Strong keyword match + file context"             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Orchestrator Lookup

```python
class OrchestratorLookup:
    """Lookup orchestrators by intent and capability."""
    
    def __init__(self, wiring_contract: Dict):
        self.routing_config = self._build_routing_table(wiring_contract)
    
    def lookup(self, intent: IntentType) -> Optional[IOrchestrator]:
        """Find orchestrator for intent."""
        config = self.routing_config.get(intent.value)
        if not config:
            return None
        
        primary = config["primary"]
        return self._get_orchestrator_instance(primary)
    
    def get_fallback_chain(self, intent: IntentType) -> List[IOrchestrator]:
        """Get fallback orchestrators for intent."""
        config = self.routing_config.get(intent.value)
        if not config:
            return []
        
        return [
            self._get_orchestrator_instance(name)
            for name in config.get("fallback", [])
        ]
```

---

## Composite Intent Detection

### Detection Logic

The IntentRouter detects composite intents when requests contain multiple operations:

```python
class CompositeIntentDetector:
    """Detects multi-intent requests."""
    
    AND_CONNECTORS = ["and", "with", "plus", "also", "&", "+"]
    THEN_CONNECTORS = ["then", "after that", "once"]
    
    IMPLICIT_PATTERNS = {
        "implement": ["test"],  # TDD implies testing
        "fix": ["test", "verify"],
        "refactor": ["test"],
    }
    
    def detect(
        self,
        request: str,
        primary: IntentType
    ) -> List[IntentType]:
        """Detect all intents in request."""
        intents = [primary]
        request_lower = request.lower()
        
        # Explicit detection
        for connector in self.AND_CONNECTORS + self.THEN_CONNECTORS:
            if connector in request_lower:
                secondary = self._parse_secondary(request_lower, connector)
                if secondary and secondary not in intents:
                    intents.append(secondary)
        
        # Implicit detection
        primary_key = primary.value
        if primary_key in self.IMPLICIT_PATTERNS:
            for implicit in self.IMPLICIT_PATTERNS[primary_key]:
                intent = IntentType(implicit)
                if intent not in intents:
                    intents.append(intent)
        
        return intents
```

### Composite Examples

| Request | Primary | Secondary | Handling |
|---------|---------|-----------|----------|
| "Implement and test auth" | IMPLEMENT | TEST | Sequential: TDD → TDD |
| "Fix bug then refactor" | FIX | REFACTOR | Sequential: TDD → Refactoring |
| "Analyze with documentation" | ANALYZE | DOCUMENT | Parallel: LENS + Doc |
| "Implement feature" | IMPLEMENT | TEST (implicit) | TDD enforces tests |

---

## Confidence Scoring

### Score Components

| Component | Weight | Source |
|-----------|--------|--------|
| **Keyword Match** | 0.30 | Direct keyword matching |
| **LENS Context** | 0.25 | Code intelligence alignment |
| **Knowledge Match** | 0.20 | Knowledge base relevance |
| **Historical Success** | 0.15 | Past routing accuracy |
| **Request Clarity** | 0.10 | Unambiguity measure |

### Confidence Calculation

```python
def calculate_confidence(
    self,
    keyword_score: float,
    lens_score: float,
    knowledge_score: float,
    historical_score: float,
    clarity_score: float
) -> RoutingConfidence:
    """
    Calculate routing confidence with breakdown.
    """
    breakdown = {
        "keyword_match": keyword_score * 0.30,
        "lens_context": lens_score * 0.25,
        "knowledge_match": knowledge_score * 0.20,
        "historical_success": historical_score * 0.15,
        "request_clarity": clarity_score * 0.10,
    }
    
    overall = sum(breakdown.values())
    
    return RoutingConfidence(
        overall=overall,
        breakdown=breakdown,
        threshold_met=overall >= 0.3
    )
```

### Confidence Actions

| Confidence Range | Action |
|------------------|--------|
| 0.0 - 0.3 | Request clarification |
| 0.3 - 0.5 | Proceed with monitoring |
| 0.5 - 0.7 | Proceed normally |
| 0.7 - 0.9 | Proceed with confidence |
| 0.9 - 1.0 | Full autonomous execution |

---

## Inputs and Outputs

### RoutingContext Input

```python
@dataclass
class RoutingContext:
    """Input context for routing decision."""
    
    operation: str              # Operation name/request
    description: Optional[str]  # Additional description
    domain: Optional[str]       # Target domain
    keywords: Optional[List[str]]  # Extracted keywords
    urgency: str               # low, medium, high, critical
    user_intent: Optional[str]  # Explicit user intent
    metadata: Dict[str, Any]    # Additional metadata
```

### RoutingDecision Output

```python
@dataclass
class RoutingDecision:
    """Complete routing decision."""
    
    intent_type: IntentType           # Detected intent
    target_handler: str               # Primary orchestrator
    confidence_score: float           # Overall confidence
    reasoning: str                    # Human-readable explanation
    metadata: Dict[str, Any]          # Additional context
    timestamp: str                    # Decision time
    composite_intents: List[IntentType]  # Secondary intents
    target_orchestrator: IOrchestrator   # Resolved instance
    fallback_orchestrators: List[IOrchestrator]  # Backups
    keyword_matches: List[str]        # Matched keywords
    confidence_breakdown: Dict[str, float]  # Per-factor scores
```

---

## Performance Metrics

| Metric | Target | Actual |
|--------|--------|--------|
| **Classification Time** | < 25ms | 15ms |
| **Accuracy** | > 95% | 96.2% |
| **Clarification Rate** | < 10% | 7.5% |
| **Fallback Rate** | < 5% | 3.1% |

---

## Related Documents

- [MasterOrchestrator](master-orchestrator.md) — Coordination
- [Decisioning Capabilities](../capabilities/decisioning.md) — Intent classification
- [End-to-End Flow](end-to-end-flow.md) — Complete lifecycle

---

*Part of CORTEX Architecture Documentation*
