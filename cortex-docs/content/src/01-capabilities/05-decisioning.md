# Decisioning & Routing Capabilities

---
title: CORTEX Decisioning & Routing - Intent Classification System
type: explanation
audience: [Software Developers, Architects, Product Owners]
word_count: 2199
last_verified: 2026-02-15
source_of_truth: cortex/intent_router/ + cortex/orchestrators/ + cortex/02-lens/
format: diátaxis-explanation
voice: third-person-neutral
phase: Production (v8.1)
diagrams: ASCII classification flow, decision trees
order: 6
---

> **Notice:** Intent classification represents a continuously improving system using LENS intelligence. Classification accuracy improves over time as CORTEX learns from more interactions. Performance characteristics reflect production deployment as of v8.1.

---

## Executive Summary

The Decisioning & Routing layer provides intelligent request interpretation and orchestrator selection. Organizations benefit from automatic intent detection that routes development requests to appropriate handlers without manual workflow configuration [Business Leaders]. Product teams gain consistent routing behavior across all CORTEX features with confidence-based fallback strategies [Product Owners]. The system implements 12 intent types, LENS-enhanced classification (95%+ accuracy), composite intent detection, and confidence scoring with P50 latency 20-40ms [Software Developers].

**Core Capabilities:**
- **Intent Classification** — 12 distinct types (IMPLEMENT, FIX, REFACTOR, ANALYZE, TEST, PLAN, AUDIT, DESIGN, DEBUG, DIGEST, QUERY, RECALL)
- **LENS Integration** — Four-phase cycle (Language→Examination→Navigation→Synthesis) enhances accuracy
- **Routing Engine** — Maps intents to 20+ orchestrators with load balancing
- **Composite Detection** — Identifies multiple intents in single request (e.g., IMPLEMENT + TEST)
- **Confidence Scoring** — 0.0-1.0 scale with ≥0.7 threshold for auto-execution
- **Fallback Strategies** — Clarification prompts for low-confidence (<0.5) requests

**Performance:** Classification latency P50: 20ms, P95: 40ms, P99: 60ms. Accuracy: 95%+ for single-intent, 88%+ for composite. Throughput: 500+ requests/second.

---

## Overview

The Decisioning layer provides the intelligence enabling CORTEX to understand user intent and route requests to appropriate orchestrators. Organizations deploy this capability to handle diverse development requests from simple bug fixes to complex multi-stage implementations without manual workflow configuration [Business Leaders].

**System Responsibilities:**

**Intent Classification** — Determining what the user wants to accomplish
- **Keyword Analysis:** Pattern matching against 100+ intent-specific keywords
- **Context Enhancement:** LENS integration for file context, git history, comment analysis
- **Semantic Understanding:** NLP-based intent extraction from natural language
- **Composite Detection:** Identifying multiple intents in single request

**Routing** — Selecting the best orchestrator for the task
- **Orchestrator Mapping:** 12 intents → 20+ orchestrators with priority rules
- **Load Balancing:** Round-robin across orchestrator replicas (Phase 11)
- **Capability Matching:** Validate orchestrator supports required operations
- **Health Checks:** Route around unhealthy orchestrators (circuit breaker)

**Confidence Assessment** — Evaluating certainty of the decision
- **Multi-Factor Scoring:** Keyword match + context + LENS analysis + historical patterns
- **Threshold Gating:** Auto-execute ≥0.7, clarify 0.5-0.7, reject <0.5
- **Uncertainty Quantification:** Confidence intervals for decision robustness

**Fallback Handling** — Managing low-confidence or ambiguous requests
- **Clarification Prompts:** Ask user to disambiguate when confidence <0.5
- **Default Routing:** Route UNKNOWN intents to MasterOrchestrator for analysis
- **Learning Loop:** Store clarifications for future training data

**Classification Flow:**
```
User Request → Keyword Analysis → LENS Enhancement → Composite Detection → Confidence Scoring → Routing Decision
   (10ms)         (5ms)              (20ms)              (3ms)               (2ms)            (orchestrator)
```

---

## Intent Classification

### Supported Intent Types

CORTEX classifies requests into 12 distinct intent types with 95%+ accuracy using LENS-enhanced analysis. Organizations benefit from automatic routing reducing manual workflow configuration [Business Leaders]. Each intent type maps to specialized orchestrators implementing domain-specific workflows [Software Developers].

| Intent | Description | Primary Orchestrator | MCP Tool | Avg Latency |
|--------|-------------|---------------------|----------|-------------|
| **IMPLEMENT** | New feature development | TDDOrchestrator | `cortex_process_request` | 500-2000ms |
| **FIX** | Bug fixes and issue resolution | TDDOrchestrator | `cortex_process_request` | 400-1500ms |
| **REFACTOR** | Code improvement and restructuring | RefactoringOrchestrator | `cortex_process_request` | 300-1200ms |
| **ANALYZE** | Code analysis requests | LENSSynthesis | `cortex_lens_analyze` | 300-800ms |
| **TEST** | Test creation (standalone) | TDDOrchestrator | `cortex_process_request` | 200-600ms |
| **AUDIT** | Governance/health checks | EnforcementOrchestrator | `cortex_audit` | 500-1500ms |
| **QUERY** | Information requests | InteractionOrchestrator | (inline response) | 50-200ms |
| **PLAN** | Development planning/phase mgmt | PlanOrchestrator | `cortex_plan_setup/resolve` | 100-400ms |
| **DESIGN** | Architecture reviews | ChallengeEngine | `cortex_challenge` | 200-600ms |
| **DEBUG** | Debug injection + analysis | DebugOrchestrator | `cortex_debug_inject` | 150-500ms |
| **DIGEST** | Session learning extraction | DigestOrchestrator | `cortex_digest_session` | 300-1000ms |
| **RECALL** | Feature discovery | TotalRecallOrchestrator | `cortex_total_recall` | 200-800ms |
| **UNKNOWN** | Unclassified (needs clarification) | MasterOrchestrator | (clarification prompt) | 100ms |

**Intent Evolution:** CORTEX v8.0 introduced DEBUG, DIGEST, RECALL intents. Earlier versions (v6.x-v7.x) had 9 intents. Future versions may add MIGRATE, OPTIMIZE, SECURITY-AUDIT as specialized intents.

### Classification Process

The intent classifier implements a four-stage pipeline combining keyword matching, LENS intelligence, composite detection, and confidence scoring. Product teams benefit from high-accuracy classification (95%+ single-intent, 88%+ composite) without manual intent specification [Product Owners].

```
User Request: "Implement user authentication with JWT tokens"
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│              INTENT CLASSIFIER (P50: 20ms total)             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Stage 1: Keyword Analysis (5ms)                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Keywords extracted: [implement, authentication, JWT]  │  │
│  │ Pattern match: "implement" → IMPLEMENT (0.85 conf)   │  │
│  │ Domain hints: "auth" → security domain               │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  Stage 2: LENS Context Enhancement (20ms)                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ L: File scan → auth.py exists (100 LOC, partial)     │  │
│  │ E: AST analysis → missing JWT validation            │  │
│  │ N: Import graph → no jwt library imported            │  │
│  │ S: Synthesis → Gap analysis suggests IMPLEMENT       │  │
│  │ Enhanced confidence: 0.85 → 0.93                     │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  Stage 3: Composite Detection (3ms)                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Security domain → AUDIT governance check implied     │  │
│  │ IMPLEMENT → TEST implicit (TDD workflow)             │  │
│  │ Composite intents: [IMPLEMENT, TEST, AUDIT]          │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  Stage 4: Confidence Scoring (2ms)                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Keyword match: 0.85 * 0.3 = 0.255                    │  │
│  │ LENS context: 0.93 * 0.5 = 0.465                     │  │
│  │ Historical patterns: 0.90 * 0.2 = 0.180              │  │
│  │ Final confidence: 0.255 + 0.465 + 0.180 = 0.90      │  │
│  │ Threshold: ≥0.7 → AUTO-EXECUTE                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
     │
     ▼
RoutingDecision(
    intent_type=IntentType.IMPLEMENT,
    target_handler="TDDOrchestrator",
    mcp_tool="cortex_process_request",
    confidence_score=0.90,
    composite_intents=[IMPLEMENT, TEST, AUDIT],
    estimated_duration_ms=1200,
    estimated_files=2
)
```

**Classification Performance by Request Type:**

| Request Type | Keyword Match | LENS Boost | Final Confidence | Latency |
|--------------|---------------|------------|------------------|----------|
| **Single verb** ("implement auth") | 0.85 | +0.10 | 0.95 | 18ms |
| **Multi-step** ("refactor + test") | 0.70 | +0.15 | 0.85 | 28ms |
| **Ambiguous** ("check the payment code") | 0.50 | +0.25 | 0.75 | 35ms |
| **Complex** ("design auth flow + implement") | 0.60 | +0.20 | 0.80 | 42ms |
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
    primary: UnifiedAnalysisOrchestrator
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
    chain: [UnifiedAnalysisOrchestrator, MasterOrchestrator]
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

- [IntentRouter](../03-orchestration/intent-router.md) — Router implementation
- [MasterOrchestrator](../03-orchestration/master-orchestrator.md) — Coordination
- [End-to-End Flow](../03-orchestration/end-to-end-flow.md) — Complete lifecycle

---

*Part of CORTEX Architecture Documentation*
