# CORTEX Brain Architecture (Current)

**Purpose:** The 3-Layer Intelligence System — How CORTEX Perceives, Reasons, and Acts  
**Audience:** Software Developers, Product Owners, Architects  
**Last Updated:** 2026-02-14  
**Phase:** 12 (Brain Perception, Reasoning, Action Layers)

---

## Executive Summary

### The Three-Layer Brain: From Sensation to Action

Just as the human brain processes information through distinct layers — sensory perception → reasoning → motor output — CORTEX implements a **three-layer intelligence architecture** that transforms raw repository data into validated, executable actions.

Organizations gain adaptive learning capabilities through this architecture, where patterns detected in one repository inform strategies applied to others [Business Leaders]. Product teams benefit from continuously improving intelligence that learns from every interaction without manual configuration [Product Owners]. The architecture provides pattern registry, strategy selection, and execution planning through three coordinated Python modules in `cortex_brain/` [Software Developers].

```
┌─────────────────────────────────────────────────────────────────────┐
│                    🧠 CORTEX 3-LAYER BRAIN ARCHITECTURE              │
└─────────────────────────────────────────────────────────────────────┘

   ┌───────────────────────────────────────────────────────────────┐
   │  1️⃣ PERCEPTION LAYER (Pattern Registry)                       │
   │     "What patterns exist in this repository?"                 │
   │                                                               │
   │  Module: cortex_brain/perception/pattern_registry.py         │
   │  Purpose: Detect known patterns via signature matching        │
   │  Output: PatternMatch (pattern_id, confidence, fields)        │
   └──────────────────────────────┬────────────────────────────────┘
                                  │
                                  ▼
   ┌───────────────────────────────────────────────────────────────┐
   │  2️⃣ REASONING LAYER (Strategy Selector)                       │
   │     "Given these patterns, what's the best approach?"         │
   │                                                               │
   │  Module: cortex_brain/reasoning/strategy_selector.py          │
   │  Purpose: Recommend strategies based on context               │
   │  Output: StrategyRecommendation (strategies, confidence)      │
   └──────────────────────────────┬────────────────────────────────┘
                                  │
                                  ▼
   ┌───────────────────────────────────────────────────────────────┐
   │  3️⃣ ACTION LAYER (Execution Planner)                          │
   │     "How do we execute this strategy step-by-step?"           │
   │                                                               │
   │  Module: cortex_brain/action/execution_planner.py             │
   │  Purpose: Generate concrete execution plans                   │
   │  Output: ExecutionPlan (steps, validation, rollback)          │
   └───────────────────────────────────────────────────────────────┘
```

---

## Layer 1: Perception (Pattern Registry)

### Brain Analogy: The Sensory Cortex

The sensory cortex doesn't see "objects" — it detects patterns of light and shadow that the brain recognizes as shapes. CORTEX's **Pattern Registry** works the same way: it detects signatures (file patterns, import structures, naming conventions) and matches them against known patterns learned from previous repositories.

### Module: `cortex_brain/perception/pattern_registry.py`

Organizations accumulate repository intelligence over time as CORTEX learns common patterns [Business Leaders]. Product teams benefit from automatic detection of framework types, testing patterns, and architectural styles without explicit configuration [Product Owners]. The pattern registry uses signature-based matching with confidence scoring to identify applicable patterns [Software Developers].

**Key Classes:**

```python
@dataclass
class RegisteredPattern:
    """Pattern registered in perception layer."""
    id: str
    name: str
    signature: Dict[str, Any]      # Detection rules (file patterns, imports)
    context: Dict[str, str]        # When applicable (e.g., "framework": "django")
    strategies: List[str]          # Recommended approaches
    risk_factors: List[str]        # Known challenges
    success_rate: float            # Historical effectiveness (0.0-1.0)

@dataclass
class PatternMatch:
    """Result of pattern detection."""
    pattern_id: str
    confidence: float              # Match confidence (0.0-1.0)
    matched_fields: List[str]      # Which signature fields matched
    missing_fields: List[str]      # Which fields didn't match
```

**Detection Flow:**

```python
# Current S3: Pattern detection in new repository
registry = PatternRegistry()

# Register learned patterns (from previous repos)
registry.register_pattern(RegisteredPattern(
    id="django-monolith",
    name="Django Monolith Architecture",
    signature={
        "has_django": True,
        "settings_path": "*/settings.py",
        "single_app": True,
        "no_api_versioning": True
    },
    context={"framework": "django", "architecture": "monolith"},
    strategies=["api-versioning-migration", "service-decomposition"],
    risk_factors=["database-coupling", "shared-state"],
    success_rate=0.87
))

# Detect patterns in new repository
repo_profile = {
    "has_django": True,
    "settings_path": "backend/settings.py",
    "single_app": True,
    "no_api_versioning": True
}

matches = registry.detect_patterns(repo_profile, confidence_threshold=0.75)
# Result: [PatternMatch(pattern_id="django-monolith", confidence=0.95, ...)]
```

**Signature Matching Algorithm:**

1. **Field Matching:** Compare repository profile against pattern signatures
2. **Partial Match Handling:** Patterns with 70%+ field matches are candidates
3. **Confidence Scoring:** `confidence = (matched_fields / total_fields)`
4. **Threshold Filtering:** Only patterns ≥ confidence_threshold returned

**Performance Characteristics:**
- Organizations may experience pattern detection completing within 50-150ms for typical repositories
- Results depend on pattern registry size and signature complexity
- High-confidence matches (≥0.85) typically indicate strong applicability

---

## Layer 2: Reasoning (Strategy Selector)

### Brain Analogy: The Prefrontal Cortex

The executive center takes sensory information and makes decisions: "Given that I see a car approaching, I should wait before crossing." CORTEX's **Strategy Selector** performs similar reasoning: "Given that this is a Django monolith with API coupling, the recommended strategy is incremental service decomposition."

### Module: `cortex_brain/reasoning/strategy_selector.py`

Organizations benefit from context-aware strategy recommendations informed by historical effectiveness patterns [Business Leaders]. Product teams receive ranked strategy options with confidence scores and risk assessments [Product Owners]. The strategy selector evaluates patterns, context, and constraints to recommend optimal approaches [Software Developers].

**Key Classes:**

```python
@dataclass
class Strategy:
    """Recommended strategy."""
    id: str
    name: str
    description: str
    applicable_contexts: List[str]  # When this strategy works
    prerequisites: List[str]        # What's needed first
    estimated_effort: str           # "low", "medium", "high"
    success_rate: float             # Historical effectiveness

@dataclass
class StrategyRecommendation:
    """Strategy recommendation with confidence."""
    strategies: List[Strategy]
    confidence: float               # Overall recommendation confidence
    reasoning: str                  # Why these strategies
    alternatives: List[Strategy]    # Other options considered
```

**Strategy Selection Flow:**

```python
# Current S3: Strategy selection based on detected patterns
selector = StrategySelector()

# Input: Pattern matches from perception layer
pattern_matches = [
    PatternMatch(pattern_id="django-monolith", confidence=0.95, ...)
]

# Context: Repository characteristics
context = {
    "team_size": "5-10",
    "timeline": "6-months",
    "risk_tolerance": "medium",
    "has_tests": True,
    "test_coverage": 0.72
}

# Select strategies
recommendation = selector.select_strategies(
    patterns=pattern_matches,
    context=context,
    max_strategies=3
)

# Result: StrategyRecommendation with ranked strategies
# 1. "Incremental Service Decomposition" (confidence: 0.89)
# 2. "API Gateway Introduction" (confidence: 0.76)
# 3. "Database Partitioning" (confidence: 0.68)
```

**Selection Algorithm:**

1. **Context Matching:** Filter strategies applicable to detected patterns
2. **Constraint Evaluation:** Check prerequisites (tests, timeline, team size)
3. **Success Rate Weighting:** Prioritize strategies with high historical success
4. **Confidence Scoring:** `confidence = pattern_confidence × context_fit × success_rate`
5. **Ranking:** Sort by confidence, return top N strategies

**Strategy Catalog (Sample):**

| Strategy ID | Name | Applicable Contexts | Success Rate |
|------------|------|---------------------|--------------|
| `api-versioning-migration` | Introduce API Versioning | Django monolith, legacy API | 0.87 |
| `service-decomposition` | Incremental Microservices | Monolith with clear domains | 0.82 |
| `database-partitioning` | Database Decomposition | Shared database coupling | 0.75 |
| `gateway-introduction` | API Gateway Pattern | Multiple backends | 0.79 |

---

## Layer 3: Action (Execution Planner)

### Brain Analogy: The Motor Cortex

The action processor translates decisions into precise muscle movements: "To pick up the cup, contract these muscles in this sequence." CORTEX's **Execution Planner** translates strategies into concrete steps: "To implement API versioning, first add version headers, then create v2 endpoints, then deprecate v1."

### Module: `cortex_brain/action/execution_planner.py`

Organizations receive actionable execution plans with clear steps and validation criteria [Business Leaders]. Product teams can track progress through defined stages with rollback procedures for each step [Product Owners]. The execution planner generates step-by-step plans with commands, validation checks, and risk mitigation [Software Developers].

**Key Classes:**

```python
@dataclass
class ExecutionStep:
    """Single step in execution plan."""
    order: int
    action: str                     # What to do
    command: Optional[str]          # How to do it (CLI command or MCP tool)
    validation: str                 # How to verify success
    rollback: Optional[str]         # How to undo if needed
    estimated_duration: str         # Time estimate

@dataclass
class ExecutionPlan:
    """Complete execution plan."""
    strategy_id: str
    steps: List[ExecutionStep]
    total_estimated_duration: str
    risk_level: str                 # "low", "medium", "high"
    prerequisites_met: bool
```

**Execution Planning Flow:**

```python
# Current S3: Generate execution plan for selected strategy
planner = ExecutionPlanner()

# Input: Selected strategy from reasoning layer
strategy = Strategy(
    id="api-versioning-migration",
    name="Introduce API Versioning",
    ...
)

# Context: Repository details
repo_context = {
    "framework": "django",
    "has_rest_framework": True,
    "api_endpoints": 47,
    "current_version": None
}

# Generate plan
plan = planner.generate_plan(strategy, repo_context)

# Result: ExecutionPlan with 5 steps
# Step 1: Add versioning middleware (15min)
# Step 2: Create v1 namespace (30min)
# Step 3: Implement version headers (45min)
# Step 4: Add deprecation warnings (20min)
# Step 5: Update documentation (30min)
```

**Sample Execution Plan:**

```python
ExecutionPlan(
    strategy_id="api-versioning-migration",
    steps=[
        ExecutionStep(
            order=1,
            action="Add API version middleware",
            command="cortex_refactor --operation=add_middleware --file=settings.py",
            validation="Check middleware in MIDDLEWARE list",
            rollback="Remove VersioningMiddleware from MIDDLEWARE",
            estimated_duration="15 minutes"
        ),
        ExecutionStep(
            order=2,
            action="Create v1 API namespace",
            command="cortex_refactor --operation=extract_module --target=api/v1/",
            validation="Test v1 endpoints respond with version header",
            rollback="Restore original URL structure",
            estimated_duration="30 minutes"
        ),
        # ... additional steps
    ],
    total_estimated_duration="2.5 hours",
    risk_level="low",
    prerequisites_met=True
)
```

---

## Integration: The Complete Cognitive Loop

### End-to-End Example: Onboarding Django Monolith

**Scenario:** Organization onboards new Django repository with API coupling issues.

```python
# PERCEPTION: Detect patterns
registry = PatternRegistry()
repo_profile = analyze_repository("/path/to/django-app")
matches = registry.detect_patterns(repo_profile, confidence_threshold=0.75)
# Detected: "django-monolith" (confidence: 0.95)

# REASONING: Select strategies
selector = StrategySelector()
context = extract_context(repo_profile)
recommendation = selector.select_strategies(matches, context)
# Recommended: "api-versioning-migration" (confidence: 0.89)

# ACTION: Generate plan
planner = ExecutionPlanner()
plan = planner.generate_plan(recommendation.strategies[0], context)
# Plan: 5 steps, 2.5 hours, low risk

# EXECUTION: Via orchestrators
execution_result = TDDOrchestrator.execute_plan(plan)
# Result: API versioning implemented, 47 endpoints migrated
```

**Cognitive Flow Visualization:**

```
Repository Onboarding Request
        ↓
┌──────────────────────┐
│  🔍 PERCEPTION       │  Pattern Registry detects:
│  Pattern Registry    │  - Django framework (conf: 0.98)
│                      │  - Monolith architecture (conf: 0.95)
└──────┬───────────────┘  - No API versioning (conf: 1.0)
       │
       ▼
┌──────────────────────┐
│  🧠 REASONING        │  Strategy Selector recommends:
│  Strategy Selector   │  1. API versioning (conf: 0.89)
│                      │  2. Service decomposition (conf: 0.76)
└──────┬───────────────┘  3. Gateway pattern (conf: 0.68)
       │
       ▼
┌──────────────────────┐
│  ⚡ ACTION           │  Execution Planner generates:
│  Execution Planner   │  - 5 concrete steps
│                      │  - Validation checks per step
└──────┬───────────────┘  - Rollback procedures
       │
       ▼
   TDDOrchestrator → Implementation
```

---

## Adaptive Learning Integration

### Continuous Intelligence Improvement

Organizations benefit from intelligence that improves with every repository processed [Business Leaders]. The brain architecture feeds learning back into the perception layer, creating a continuous improvement cycle [Product Owners]. Pattern success rates and strategy effectiveness update automatically based on execution outcomes [Software Developers].

**Learning Loop (Current):**

1. **Pattern Detection** → Perception layer identifies patterns
2. **Strategy Selection** → Reasoning layer recommends approaches
3. **Execution** → Action layer generates and executes plan
4. **Outcome Capture** → Success/failure recorded with context
5. **Pattern Update** → Success rates adjusted in registry
6. **Strategy Refinement** → Confidence scores updated based on outcomes

**Example: Pattern Success Rate Evolution**

```python
# Initial pattern registration
pattern = RegisteredPattern(
    id="django-monolith",
    success_rate=0.70,  # Initial estimate
    ...
)

# After 10 successful applications
# Adaptive learning updates:
pattern.success_rate = 0.87  # Improved based on actual results

# After encountering edge case (no tests)
# New risk factor added:
pattern.risk_factors.append("requires-test-coverage")
```

---

## Performance Characteristics

Organizations may experience these performance patterns based on internal testing:

| Layer | Operation | Target | Typical | Notes |
|-------|-----------|--------|---------|-------|
| **Perception** | Pattern detection | <100ms | 75ms | Scales with pattern count |
| **Reasoning** | Strategy selection | <150ms | 110ms | Scales with strategy catalog |
| **Action** | Plan generation | <200ms | 160ms | Scales with plan complexity |
| **End-to-End** | Full cognitive loop | <500ms | 345ms | Perception → Reasoning → Action |

> **Notice:** Performance measurements reflect internal testing environments with typical repository sizes (5k-50k LOC). Production results depend on repository complexity, pattern registry size, and system resources. No guarantee of specific performance outcomes.

---

## Implementation Details

### Module Locations

```
cortex_brain/
├── perception/
│   └── pattern_registry.py        # Layer 1: Pattern detection
├── reasoning/
│   └── strategy_selector.py       # Layer 2: Strategy selection
├── action/
│   └── execution_planner.py       # Layer 3: Execution planning
└── state/
    └── learning_state.py          # Cross-layer learning state
```

### Testing Coverage (Current S3)

| Component | Tests | Coverage | Status |
|-----------|-------|----------|--------|
| PatternRegistry | 21 tests | 94% | ✅ Current S3 |
| StrategySelector | 23 tests | 96% | ✅ Current S3 |
| ExecutionPlanner | 25 tests | 95% | ✅ Current S3 |
| **Total** | **69 tests** | **95%** | **✅ Complete** |

### Governance Compliance

- ✅ **CORE-008:** TDD implementation (RED → GREEN → REFACTOR)
- ✅ **CORE-011:** Type hints on all parameters and returns
- ✅ **CORE-012:** Google-style docstrings with full parameter documentation
- ✅ **CORE-027:** AC markers (AC-PHASE12-S3-001 through AC-PHASE12-S3-025)

---

## Related Documentation

- [AI & Intelligence Capabilities](./ai-intelligence.md) — LENS and intelligence systems
- [Orchestration Overview](../orchestration/overview.md) — How orchestrators use brain layers
- [Learning Architecture](../infrastructure/learning-architecture.md) — Adaptive learning system
- [CORTEX Brain State](./brain-state.md) — State management for learning

---

> **Notice:** Brain architecture capabilities represent system design intentions for pattern-based intelligence. Actual pattern detection accuracy, strategy effectiveness, and execution success depend on repository characteristics, historical data availability, and operational context. Organizations should evaluate applicability through pilot testing with representative repositories.
