# Intent Router

> Auto-generated from cortex-impl-map.yaml on 2026-01-21

**Last Updated:** 2026-01-21  
**Audience:** Architects, Developers  
**Prerequisites:** [System Overview](1-system-overview.md), [Orchestration Engine](3-orchestration-engine.md)

## Overview

The Intent Router is the intelligent entry point for all CORTEX operations. It uses the LENS Protocol to parse user intent, classify requests, and route them to the appropriate domain orchestrator with high confidence.

## LENS Protocol

LENS (Language, Examination, Navigation, Synthesis) is a four-phase protocol for comprehensive intent comprehension:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           LENS Protocol Pipeline                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌────────────┐│
│   │   LANGUAGE   │    │ EXAMINATION  │    │  NAVIGATION  │    │ SYNTHESIS  ││
│   │              │    │              │    │              │    │            ││
│   │ • NLP Parse  │───▶│ • AST Scan   │───▶│ • Git Hist   │───▶│ • Merge    ││
│   │ • Intent     │    │ • Code Struct│    │ • Changes    │    │ • Context  ││
│   │ • Entities   │    │ • Deps       │    │ • Authors    │    │ • Score    ││
│   └──────────────┘    └──────────────┘    └──────────────┘    └────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Phase 1: Language

Natural language parsing to extract intent signals:

| Component | Function |
|-----------|----------|
| **Intent Parser** | Extracts action verbs (IMPLEMENT, ANALYZE, PLAN) |
| **Entity Extractor** | Identifies files, modules, concepts |
| **Context Detector** | Determines urgency, scope, constraints |

### Phase 2: Examination

AST analysis and code structure examination:

| Component | Function |
|-----------|----------|
| **AST Scanner** | Parses target files for structure |
| **Dependency Mapper** | Identifies module relationships |
| **Complexity Analyzer** | Estimates change complexity |

### Phase 3: Navigation

Git history and change pattern analysis:

| Component | Function |
|-----------|----------|
| **History Analyzer** | Recent commits, change frequency |
| **Author Tracker** | Last modifier, ownership |
| **Hot Spot Detector** | Frequently changed areas |

### Phase 4: Synthesis

Context aggregation and confidence scoring:

| Component | Function |
|-----------|----------|
| **Context Merger** | Combines all LENS phases |
| **Confidence Scorer** | 0.0-1.0 routing confidence |
| **Route Selector** | Chooses target orchestrator |

## Module Architecture

The Intent Router is implemented in `cortex/intent_router/` with 16 modules:

```
cortex/intent_router/
├── __init__.py
├── classifier.py           # Intent classification
├── confidence_scorer.py    # Routing confidence calculation
├── context_manager.py      # Context aggregation
├── disambiguator.py        # Ambiguity resolution
├── documentation.py        # Documentation helpers
├── documentation_manager.py# Doc management
├── edge_case_handler.py    # Edge case handling
├── fallback_strategy.py    # Fallback routing
├── intent_learner.py       # ML-based intent learning
├── multimodal_processor.py # Multi-input processing
├── observability.py        # Metrics and tracing
├── orchestration_integrator.py # Orchestrator integration
├── performance_metrics.py  # Performance tracking
├── routing_engine.py       # Core routing logic
└── test_framework.py       # Testing utilities
```

## Intent Classification

The classifier categorizes intents into routing targets:

| Intent Type | Description | Target Orchestrator |
|-------------|-------------|---------------------|
| **IMPLEMENT** | Create or modify code | ExecutionOrchestrator |
| **ANALYZE** | Examine code/patterns | AnalysisOrchestrator |
| **PLAN** | Create implementation plan | PlanningOrchestrator |
| **INTEGRATE** | Connect systems/modules | IntegrationOrchestrator |
| **QUERY** | Retrieve information | QueryOrchestrator |
| **VALIDATE** | Check compliance/tests | ValidationOrchestrator |

## Confidence Scoring

The confidence scorer produces a 0.0-1.0 score based on:

```python
confidence = (
    intent_clarity × 0.30 +      # How clear is the intent?
    context_completeness × 0.25 + # Do we have enough context?
    historical_match × 0.25 +     # Similar past requests?
    disambiguation_result × 0.20  # Resolved ambiguity?
)
```

### Confidence Thresholds

| Score | Action |
|-------|--------|
| ≥ 0.85 | Auto-route with high confidence |
| 0.60-0.85 | Route with summary confirmation |
| 0.35-0.60 | Request clarification |
| < 0.35 | Use fallback strategy |

## Disambiguation

When intent is ambiguous, the disambiguator prompts for clarification:

```python
class Disambiguator:
    def resolve(self, intent: Intent) -> DisambiguationResult:
        """
        Resolve ambiguous intent through:
        1. Context expansion (more files, history)
        2. Pattern matching (similar past intents)
        3. User clarification (explicit questions)
        """
```

## Fallback Strategy

When routing confidence is low, fallback strategies are applied:

| Strategy | Trigger | Action |
|----------|---------|--------|
| **Clarification** | Confidence < 0.35 | Ask specific questions |
| **Default Route** | Repeated failures | Route to MasterOrchestrator |
| **Escalation** | Critical operation | Require explicit confirmation |

## Integration with Orchestrators

The routing engine dispatches to orchestrators via the registry:

```python
from cortex.orchestrators.registry import OrchestratorRegistry

class RoutingEngine:
    def route(self, intent: ClassifiedIntent) -> Orchestrator:
        orchestrator = OrchestratorRegistry.get(intent.target)
        return orchestrator.with_context(intent.context)
```

## Observability

The intent router exposes metrics for monitoring:

| Metric | Type | Description |
|--------|------|-------------|
| `intent_router_requests_total` | Counter | Total routing requests |
| `intent_router_confidence_score` | Histogram | Confidence distribution |
| `intent_router_disambiguation_rate` | Gauge | % requiring disambiguation |
| `intent_router_fallback_rate` | Gauge | % using fallback |

## Related

- [Intent Router Flow Diagram](../_diagrams/intent-router-flow.mmd)
- [Orchestration Engine](3-orchestration-engine.md)
- [Domain Brain](4-domain-brain.md)
