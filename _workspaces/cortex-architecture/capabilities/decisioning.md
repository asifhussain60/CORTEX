# Decisioning & Routing Capabilities

**Purpose:** Detailed documentation of CORTEX intent classification and routing  
**Audience:** Architects, Developers  
**Last Updated:** 2026-02-10

---

## Table of Contents

- [Overview](#overview)
- [Intent Classification](#intent-classification)
- [Routing Engine](#routing-engine)
- [Composite Intent Detection](#composite-intent-detection)
- [Confidence Scoring](#confidence-scoring)
- [Fallback Strategies](#fallback-strategies)
- [Related Documents](#related-documents)

---

## Overview

The Decisioning layer is responsible for understanding user intent and routing requests to the appropriate orchestrator. This process involves:

1. **Intent Classification** — Determining what the user wants to accomplish
2. **Routing** — Selecting the best orchestrator for the task
3. **Confidence Assessment** — Evaluating certainty of the decision
4. **Fallback Handling** — Managing low-confidence or ambiguous requests

---

## Intent Classification

### Supported Intent Types

CORTEX classifies requests into 14 distinct intent types:

| Intent | Description | Primary Orchestrator |
|--------|-------------|---------------------|
| **IMPLEMENT** | New feature development | TDDOrchestrator |
| **FIX** | Bug fixes and issue resolution | TDDOrchestrator |
| **REFACTOR** | Code improvement and restructuring | RefactoringOrchestrator |
| **ANALYZE** | Code analysis requests | LENSOrchestrator |
| **DOCUMENT** | Documentation generation | DocumentationOrchestrator |
| **TEST** | Test creation | TDDOrchestrator |
| **DEPLOY** | Deployment operations | DeploymentOrchestrator |
| **GOVERNANCE** | Governance checks | GovernanceOrchestrator |
| **QUERY** | Information requests | KnowledgeOrchestrator |
| **VALIDATE** | Validation operations | ValidationOrchestrator |
| **MIGRATE** | Migration operations | MigrationOrchestrator |
| **ONBOARD** | Repository onboarding | OnboardingOrchestrator |
| **PLAN** | Development planning | PlanningOrchestrator |
| **UNKNOWN** | Unclassified (requires clarification) | MasterOrchestrator |

### Classification Process

```
User Request
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│                    INTENT CLASSIFIER                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Step 1: Keyword Analysis                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ "Implement user auth" → Keywords: [implement, auth]   │  │
│  │ Primary match: IMPLEMENT (0.9 confidence)             │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  Step 2: Context Enhancement (LENS)                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ File context: auth.py exists (partial impl)          │  │
│  │ Git history: Recent auth-related commits             │  │
│  │ Enhanced confidence: 0.95                            │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  Step 3: Composite Detection                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Secondary intents: [TEST] (implicit TDD)             │  │
│  │ Composite: IMPLEMENT + TEST                          │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
     │
     ▼
RoutingDecision(
    intent_type=IMPLEMENT,
    target_handler="TDDOrchestrator",
    confidence_score=0.95,
    composite_intents=[IMPLEMENT, TEST]
)
```

### Keyword Patterns

```python
INTENT_KEYWORDS = {
    IntentType.IMPLEMENT: [
        "implement", "create", "build", "add", "develop",
        "new feature", "introduce", "establish"
    ],
    IntentType.FIX: [
        "fix", "bug", "error", "issue", "problem",
        "broken", "failing", "incorrect", "wrong"
    ],
    IntentType.REFACTOR: [
        "refactor", "improve", "optimize", "clean up",
        "restructure", "simplify", "modernize"
    ],
    IntentType.ANALYZE: [
        "analyze", "review", "examine", "inspect",
        "check", "audit", "assess", "evaluate"
    ],
    # ... additional patterns
}
```

---

## Routing Engine

### Routing Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                       ROUTING ENGINE                          │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                  OrchestratorLookup                      │ │
│  │  • Loads routing configuration from YAML                │ │
│  │  • Maps intents to orchestrators                        │ │
│  │  • Resolves fallback chains                             │ │
│  └─────────────────────────────────────────────────────────┘ │
│                           │                                   │
│                           ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │               RoutingEnforcementEngine                   │ │
│  │  • Validates routing decisions                          │ │
│  │  • Enforces routing policies                            │ │
│  │  • Generates violations for invalid routes              │ │
│  └─────────────────────────────────────────────────────────┘ │
│                           │                                   │
│                           ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                   Target Orchestrator                    │ │
│  │  • Receives routing decision                            │ │
│  │  • Executes operation                                    │ │
│  │  • Returns result                                        │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### Routing Configuration

```yaml
# Routing configuration excerpt
routing:
  implement:
    primary: TDDOrchestrator
    fallback: [WorkflowOrchestrator, MasterOrchestrator]
    keywords: [implement, create, build, add]
    requires_tdd: true
    
  fix:
    primary: TDDOrchestrator
    fallback: [WorkflowOrchestrator]
    keywords: [fix, bug, error, issue]
    requires_tdd: true
    
  refactor:
    primary: RefactoringOrchestrator
    fallback: [TDDOrchestrator]
    keywords: [refactor, improve, optimize]
    requires_tdd: true
    
  analyze:
    primary: LENSOrchestrator
    fallback: [MasterOrchestrator]
    keywords: [analyze, review, examine]
    requires_tdd: false
```

### Routing Decision Data

```python
@dataclass
class RoutingDecision:
    """Complete routing decision with metadata."""
    
    intent_type: IntentType           # Detected intent
    target_handler: str               # Primary orchestrator name
    confidence_score: float           # Decision confidence (0.0-1.0)
    reasoning: str                    # Human-readable explanation
    metadata: Dict[str, Any]          # Additional context
    timestamp: str                    # Decision timestamp
    composite_intents: List[IntentType]  # Secondary intents
    target_orchestrator: IOrchestrator   # Resolved orchestrator instance
    fallback_orchestrators: List[IOrchestrator]  # Backup options
    keyword_matches: List[str]        # Keywords that matched
    confidence_breakdown: Dict[str, float]  # Per-factor confidence
```

---

## Composite Intent Detection

### What are Composite Intents?

Composite intents occur when a single request contains multiple operation types. CORTEX detects these and coordinates appropriate orchestrators.

### Detection Patterns

| Pattern Type | Example | Detection |
|--------------|---------|-----------|
| **AND patterns** | "Implement AND test" | Connector: "and", "with", "plus" |
| **THEN patterns** | "Fix THEN refactor" | Connector: "then", "after that" |
| **WITH patterns** | "Implement WITH documentation" | Connector: "with", "including" |
| **Implicit patterns** | "Implement feature" (TDD implies tests) | Context-based inference |

### Composite Detection Code

```python
class CompositeIntentDetector:
    """Detects multi-intent requests."""
    
    AND_CONNECTORS = ["and", "with", "plus", "also", "&", "+"]
    THEN_CONNECTORS = ["then", "after that", "once", "before"]
    
    IMPLICIT_PATTERNS = {
        "implement": ["test"],      # Implement implies test (TDD)
        "fix": ["test", "verify"],  # Fix implies test
        "refactor": ["test"],       # Refactor implies test
    }
    
    def detect_composite_intents(
        self,
        request: str,
        primary_intent: IntentType
    ) -> List[IntentType]:
        """
        Detect all intents in a composite request.
        
        Returns list including primary + any secondary intents.
        """
        intents = [primary_intent]
        request_lower = request.lower()
        
        # Check for explicit connectors
        for connector in self.AND_CONNECTORS:
            if connector in request_lower:
                # Parse secondary intent after connector
                secondary = self._parse_after_connector(
                    request_lower, connector
                )
                if secondary:
                    intents.append(secondary)
        
        # Check for implicit patterns
        primary_key = primary_intent.value
        if primary_key in self.IMPLICIT_PATTERNS:
            for implicit in self.IMPLICIT_PATTERNS[primary_key]:
                implied_intent = IntentType(implicit)
                if implied_intent not in intents:
                    intents.append(implied_intent)
        
        return intents
```

### Composite Orchestration

When composite intents are detected, CORTEX coordinates execution:

```
Composite Request: "Implement auth AND write tests AND document"
                              │
                              ▼
                    ┌─────────────────────┐
                    │   MasterOrchestrator │
                    │   (Coordinator)      │
                    └─────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│TDDOrchestrator│────▶│TDDOrchestrator│────▶│Documentation  │
│  (IMPLEMENT)  │     │    (TEST)     │     │ Orchestrator  │
└───────────────┘     └───────────────┘     └───────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
                    ┌─────────────────────┐
                    │   Aggregated Result  │
                    └─────────────────────┘
```

---

## Confidence Scoring

### Confidence Factors

| Factor | Weight | Description |
|--------|--------|-------------|
| **Keyword Match** | 0.30 | Direct keyword matching |
| **LENS Context** | 0.25 | Code intelligence context |
| **Knowledge Match** | 0.20 | Knowledge base alignment |
| **Historical Success** | 0.15 | Past routing success rate |
| **Request Clarity** | 0.10 | Request unambiguity |

### Confidence Calculation

```python
def calculate_routing_confidence(
    keyword_score: float,      # 0.0-1.0
    lens_score: float,         # 0.0-1.0
    knowledge_score: float,    # 0.0-1.0
    historical_score: float,   # 0.0-1.0
    clarity_score: float       # 0.0-1.0
) -> Tuple[float, Dict[str, float]]:
    """
    Calculate overall routing confidence.
    
    Returns:
        Tuple of (overall_score, breakdown_dict)
    """
    breakdown = {
        "keyword_match": keyword_score * 0.30,
        "lens_context": lens_score * 0.25,
        "knowledge_match": knowledge_score * 0.20,
        "historical_success": historical_score * 0.15,
        "request_clarity": clarity_score * 0.10,
    }
    
    overall = sum(breakdown.values())
    return overall, breakdown
```

### Confidence Thresholds

| Range | Classification | Action |
|-------|----------------|--------|
| **0.0 - 0.3** | Low | Request clarification from user |
| **0.3 - 0.5** | Medium-Low | Proceed with enhanced monitoring |
| **0.5 - 0.7** | Medium | Proceed normally |
| **0.7 - 0.9** | High | Proceed with confidence |
| **0.9 - 1.0** | Very High | Full autonomous execution |

---

## Fallback Strategies

### Fallback Chain

Each intent type has a defined fallback chain:

```yaml
fallback_chains:
  implement:
    chain: [TDDOrchestrator, WorkflowOrchestrator, MasterOrchestrator]
    strategy: "sequential"
    
  analyze:
    chain: [LENSOrchestrator, MasterOrchestrator]
    strategy: "sequential"
    
  unknown:
    chain: [MasterOrchestrator]
    strategy: "clarification_first"
```

### Fallback Triggers

| Trigger | Description | Response |
|---------|-------------|----------|
| **Orchestrator Unavailable** | Target orchestrator down | Try next in chain |
| **Timeout** | Operation exceeds timeout | Try fallback |
| **Explicit Rejection** | Orchestrator rejects request | Try fallback |
| **Low Confidence** | Below threshold | Request clarification |

### Clarification Requests

When confidence is too low, CORTEX generates clarification requests:

```python
@dataclass
class ClarificationRequest:
    """Request for user clarification."""
    
    original_request: str
    detected_intents: List[IntentType]
    confidence: float
    ambiguity_reason: str
    suggested_clarifications: List[str]
    
    # Example:
    # ClarificationRequest(
    #     original_request="Fix the auth",
    #     detected_intents=[FIX, REFACTOR],
    #     confidence=0.45,
    #     ambiguity_reason="Could be bug fix or code improvement",
    #     suggested_clarifications=[
    #         "Fix a specific bug in authentication",
    #         "Refactor authentication code for better structure"
    #     ]
    # )
```

---

## Performance Metrics

| Metric | Target | Actual |
|--------|--------|--------|
| **Classification Accuracy** | > 95% | 96.2% |
| **Routing Latency** | < 50ms | 25ms |
| **Fallback Rate** | < 5% | 3.1% |
| **Clarification Rate** | < 10% | 7.5% |

---

## Related Documents

- [IntentRouter](../orchestration/intent-router.md) — Router implementation
- [MasterOrchestrator](../orchestration/master-orchestrator.md) — Coordination
- [End-to-End Flow](../orchestration/end-to-end-flow.md) — Complete lifecycle

---

*Part of CORTEX Architecture Documentation*
