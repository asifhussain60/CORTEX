# IntentRouter

**Purpose:** Detailed documentation of the intent classification and routing orchestrator — CORTEX's central request dispatcher  
**Audience:** Architects, Developers  
**Last Updated:** 2026-02-14

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

### The Brain’s Thalamus: The Sensory Relay Station

In the human brain, the **thalamus** sits at the very center — a walnut-sized relay station that every sensory signal must pass through before reaching the cortex. It doesn’t process information deeply itself; instead, it rapidly classifies incoming signals and routes them to the correct specialized brain region. Visual signals go to the visual cortex. Auditory signals go to the auditory cortex. Pain signals go to the somatosensory cortex.

The **IntentRouter** is CORTEX’s thalamus. Every user request passes through it, and within **15 milliseconds**, it classifies the intent and routes the signal to the correct specialist orchestrator. A request to “implement login” fires toward the TDDOrchestrator (motor cortex). A request to “refactor this module” routes to the RefactoringOrchestrator (Wernicke’s area). A request to “analyze security” flows to the UnifiedAnalysisOrchestrator (visual association cortex).

Like the thalamus, the IntentRouter uses a **multi-factor scoring system** to make routing decisions — combining keyword signals (30%), contextual cues from LENS (25%), knowledge base alignment (20%), historical accuracy (15%), and request clarity (10%).

**Key Facts:**
- **Category:** Core (essential request gateway)
- **Priority:** 20 (second only to MasterOrchestrator)
- **System Analogy:** Airport security checkpoint — central classification hub
- **Capabilities:** intent_classification, routing
- **Dependencies:** MasterOrchestrator
- **Classification Speed:** ~15ms (96.2% accuracy)

---

## Intent Classification

### Supported Intent Types

Each intent maps to a specific brain region (orchestrator). The IntentRouter maintains this routing table — think of it as the thalamus’s wiring diagram:

| Intent | Keywords | Target Orchestrator | Brain Analogy |
|--------|----------|---------------------|---------------|
| **IMPLEMENT** | implement, create, build, add | TDDOrchestrator | Motor cortex — disciplined execution |
| **FIX** | fix, bug, error, issue | TDDOrchestrator | Motor cortex — corrective action |
| **REFACTOR** | refactor, improve, optimize | RefactoringOrchestrator | Wernicke’s area — restructuring |
| **ANALYZE** | analyze, review, examine | UnifiedAnalysisOrchestrator | Visual association — perception |
| **TEST** | test, verify, validate | TDDOrchestrator | Motor cortex — verification |
| **ONBOARD** | onboard, setup, initialize | UnifiedOnboardingOrchestrator | Hippocampus — memory formation |
| **PLAN** | plan, phase, roadmap | PlanningOrchestrator | Dorsolateral prefrontal — strategy |
| **QUERY** | what, how, why, explain | UnifiedDiscoveryOrchestrator | Curiosity circuit — exploration |
| **CONVERSATION** | chat, discuss, talk | ConversationOrchestrator | Superior temporal — social cognition |
| **WORKFLOW** | workflow, sequence, pipeline | WorkflowOrchestrator | Basal ganglia — procedural sequences |
| **QUALITY** | audit, compliance, review | UnifiedQualityAssuranceOrchestrator | Anterior cingulate — error detection |
| **UNKNOWN** | (no match) | MasterOrchestrator | Prefrontal cortex — general reasoning |

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
