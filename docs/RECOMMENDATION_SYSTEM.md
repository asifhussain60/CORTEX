# Solution Recommendation System

**AC-RECOMMENDATION-001**: Intelligent solution evaluation and marking system for CORTEX orchestrators.

## Overview

The Solution Recommendation System automatically evaluates multiple solution options and marks the best one with a ⭐ **RECOMMENDED BY CORTEX** designation for users. This system integrates with both the `InteractionOrchestrator` and `ConversationProtocol` to provide intelligent decision support.

## Architecture

### Components

#### 1. SolutionRecommendationEngine
Located in: `cortex/orchestrators/core/solution_recommendation_engine.py`

Core recommendation engine using weighted multi-factor scoring:

```python
from cortex.orchestrators.core.solution_recommendation_engine import (
    get_recommendation_engine,
    SolutionOption,
    RecommendedSolution,
    RecommendationConfidence
)

# Get the singleton engine
engine = get_recommendation_engine()

# Score a single option (0.0-1.0)
score = engine.score_option(option)

# Get recommendation with best option marked ⭐
recommendation = engine.recommend_best_option(
    options,
    context={"turn_number": 1}
)
```

#### 2. SolutionOption Dataclass
Represents a single solution option with 14 evaluation metrics:

```python
SolutionOption(
    option_id="opt1",
    name="Solution Name",
    description="Detailed description",
    
    # Effort/Risk metrics
    implementation_effort="low|medium|high",
    risk_level="low|medium|high", 
    maintenance_cost="low|medium|high",
    
    # Quality metrics (0.0-1.0)
    cortex_alignment=0.9,           # CORTEX principle adherence
    governance_compliance=0.9,       # Governance rule compliance
    performance_impact=0.8,          # Performance improvement
    scalability_score=0.9,           # Scalability potential
    team_familiarity=0.7,            # Team knowledge of solution
    technical_debt=0.1,              # Technical debt impact (lower is better)
    
    # Supporting info
    pros=["Benefit 1", "Benefit 2"],
    cons=["Issue 1", "Issue 2"],
    dependencies=["other-module"],
    timeline_estimate="2-3 weeks"
)
```

#### 3. RecommendedSolution Dataclass
Structured recommendation output:

```python
RecommendedSolution(
    best_option_id="opt1",
    best_option=SolutionOption(...),  # Marked with ⭐
    confidence=RecommendationConfidence.HIGH,
    reasoning="Detailed explanation...",
    summary="Concise summary with emoji",
    all_options=[...],  # All evaluated options
    option_scores={"opt1": 0.85, "opt2": 0.72},
    user_override_enabled=True  # Allow user to pick alternative
)
```

#### 4. RecommendationConfidence Enum
Confidence levels based on score gaps:

```python
class RecommendationConfidence(Enum):
    HIGH = "high"          # Gap ≥ 30%
    MEDIUM = "medium"      # Gap 15-30%
    LOW = "low"            # Gap 5-15%
    UNCERTAIN = "uncertain" # Gap < 5%
```

### Scoring System

#### Weighted Factors (Total: 1.0)
```python
WEIGHTS = {
    "cortex_alignment": 0.25,        # 25% - CORTEX principle adherence
    "governance_compliance": 0.20,   # 20% - Governance rule compliance
    "implementation_effort": 0.15,   # 15% - Implementation difficulty
    "risk_level": 0.15,              # 15% - Solution risk
    "performance_impact": 0.10,      # 10% - Performance gain
    "scalability_score": 0.05,       # 5% - Scalability
    "team_familiarity": 0.05,        # 5% - Team knowledge
    "technical_debt": 0.05           # 5% - Technical debt reduction
}
```

#### Effort/Risk Normalization
Categorical values (low/medium/high) are normalized to 0.0-1.0:
- `"low"` → 1.0 (most favorable)
- `"medium"` → 0.5
- `"high"` → 0.0 (least favorable)

### Confidence Calculation

Confidence is determined by the gap between best and second-best options:

```python
def _determine_confidence(self, scores: List[float]) -> RecommendationConfidence:
    scores_sorted = sorted(scores, reverse=True)
    if len(scores_sorted) < 2:
        return RecommendationConfidence.HIGH
    
    gap_percentage = (scores_sorted[0] - scores_sorted[1]) / scores_sorted[0]
    
    if gap_percentage >= 0.30:
        return RecommendationConfidence.HIGH      # Clear winner
    elif gap_percentage >= 0.15:
        return RecommendationConfidence.MEDIUM    # Moderate difference
    elif gap_percentage >= 0.05:
        return RecommendationConfidence.LOW       # Close call
    else:
        return RecommendationConfidence.UNCERTAIN # Very close
```

## Integration Points

### 1. InteractionOrchestrator Integration

Method: `InteractionOrchestrator.evaluate_solution_options()`

```python
from cortex.orchestrators.core.interaction_orchestrator import InteractionOrchestrator

orchestrator = InteractionOrchestrator(...)

# Evaluate solutions and get recommendation with ⭐ marking
recommendation = orchestrator.evaluate_solution_options(
    solution_options=[
        {
            "option_id": "opt1",
            "name": "Solution A",
            "cortex_alignment": 0.95,
            "governance_compliance": 0.90,
            # ... other metrics
        },
        {
            "option_id": "opt2",
            "name": "Solution B",
            "cortex_alignment": 0.75,
            "governance_compliance": 0.80,
            # ... other metrics
        }
    ],
    round_context=round_context  # Optional
)

# Response format:
{
    "best_option": {
        "option_id": "opt1",
        "name": "Solution A",
        "description": "...",
        "marked_as": "⭐ RECOMMENDED BY CORTEX"
    },
    "confidence": "high",
    "reasoning": "Detailed explanation...",
    "summary": "🟢 CORTEX Recommends: Solution A",
    "alternative_options": [
        {
            "option_id": "opt2",
            "name": "Solution B",
            "score": 0.72,
            "why_not_recommended": "Score: 0.72 vs best: 0.85"
        }
    ],
    "user_can_override": True
}
```

### 2. ConversationProtocol Integration

Method: `ConversationProtocol.get_recommended_option()`

```python
from cortex.brain.core.orchestrator.conversation_protocol import ConversationProtocol

protocol = ConversationProtocol(...)

# Get recommendation in turn context
recommendation = protocol.get_recommended_option(
    solution_options=[
        {"option_id": "opt1", ...},
        {"option_id": "opt2", ...}
    ]
)

# Recommendation is logged in audit trail (AC-RECOMMENDATION-001)
# and included in turn output
```

## Usage Examples

### Example 1: Simple Recommendation

```python
from cortex.orchestrators.core.solution_recommendation_engine import (
    SolutionOption,
    get_recommendation_engine
)

# Create options
options = [
    SolutionOption(
        option_id="refactor",
        name="Refactor to microservices",
        description="Break into independent services",
        implementation_effort="high",
        risk_level="high",
        maintenance_cost="low",
        cortex_alignment=0.95,
        governance_compliance=0.90,
        performance_impact=0.85,
        scalability_score=0.95,
        team_familiarity=0.4,
        technical_debt=0.1,
        pros=["Scalable", "Independently deployable"],
        cons=["High complexity", "Distributed tracing needed"]
    ),
    SolutionOption(
        option_id="optimize",
        name="Optimize monolith",
        description="Performance improvements to existing code",
        implementation_effort="low",
        risk_level="low",
        maintenance_cost="medium",
        cortex_alignment=0.7,
        governance_compliance=0.85,
        performance_impact=0.6,
        scalability_score=0.5,
        team_familiarity=0.9,
        technical_debt=0.6,
        pros=["Quick wins", "Team familiar"],
        cons=["Limited scalability", "Increases tech debt"]
    )
]

# Get recommendation
engine = get_recommendation_engine()
recommendation = engine.recommend_best_option(options)

print(f"⭐ Recommended: {recommendation.best_option.name}")
print(f"Confidence: {recommendation.confidence.value}")
print(f"\nReasoning:\n{recommendation.reasoning}")
```

### Example 2: In a Challenge Flow

```python
def execute_turn_with_challenge(self, user_request):
    # ... build LENS context ...
    
    # Generate challenge if needed
    challenge = self.challenge_engine.generate_challenge(...)
    
    if challenge.has_disagreement:
        # Evaluate solution options from challenge
        options = challenge.challenge_options
        
        # Get recommendation
        recommendation = self.evaluate_solution_options(options)
        
        # Return with marked best option
        return {
            "type": "challenge_with_recommendation",
            "challenge": challenge,
            "recommendation": recommendation,
            "requires_user_choice": True
        }
```

### Example 3: Audit Trail Integration

The recommendation engine automatically logs to audit trail:

```python
# In ConversationProtocol.get_recommended_option()
if self._audit_logger:
    self._audit_logger.log_operation_complete(
        ac_id="AC-RECOMMENDATION-001",
        operation="OPTION_EVALUATION",
        success=True,
        details={
            "best_option": recommendation.best_option.name,
            "confidence": recommendation.confidence.value,
            "score": engine.score_option(recommendation.best_option),
        },
    )
```

## Output Format

### JSON Serialization

```json
{
  "best_option": {
    "option_id": "opt1",
    "name": "Solution A",
    "description": "High-quality implementation",
    "marked_as": "⭐ RECOMMENDED BY CORTEX"
  },
  "confidence": "high",
  "reasoning": "✅ CORTEX Recommendation: Solution A\n\nConfidence: HIGH\nOverall Score: 0.85/1.0\n\nKey Strengths:\n  • High CORTEX alignment (95%)\n  • Governance compliant (90%)\n  • Excellent scalability\n\nScoring Breakdown:\n  • CORTEX Alignment: 95%\n  • Governance Compliance: 90%\n  ...",
  "summary": "🟢 CORTEX Recommends: Solution A\nImplementation: medium effort\nRisk: low | Timeline: TBD",
  "alternative_options": [
    {
      "option_id": "opt2",
      "name": "Solution B",
      "description": "Alternative approach",
      "score": 0.72,
      "why_not_recommended": "Score: 0.72 vs best: 0.85"
    }
  ],
  "user_can_override": true
}
```

## Testing

Comprehensive test suite in: `tests/unit/orchestrators/test_solution_recommendation_integration.py`

```bash
# Run all recommendation tests
pytest tests/unit/orchestrators/test_solution_recommendation_integration.py -v

# Run specific test
pytest tests/unit/orchestrators/test_solution_recommendation_integration.py::TestSolutionRecommendationEngine::test_recommend_best_option_marks_with_star -v
```

### Test Coverage

- ✅ Singleton pattern enforcement
- ✅ Single option scoring (0.0-1.0 scale)
- ✅ Best option marking with ⭐
- ✅ Confidence calculation (HIGH/MEDIUM/LOW/UNCERTAIN)
- ✅ Score gap analysis
- ✅ Reasoning generation
- ✅ Alternative preservation
- ✅ Data serialization (to_dict)

## Governance & Compliance

### CORE Rules Applied

- **CORE-030**: Implementation Truth - Recommendation engine tested before integration
- **CORE-035**: Single Canonical Implementation - One recommendation engine per workspace
- **AC-RECOMMENDATION-001**: Marked in audit trail with full context

### Audit Trail

All recommendations are logged:

```
AC_ID: AC-RECOMMENDATION-001
Operation: OPTION_EVALUATION
Details:
  - best_option: Solution name
  - confidence: high/medium/low/uncertain
  - score: 0.85
```

## Performance

- **Scoring**: O(n) where n = number of options
- **Confidence**: O(log n) due to sorting
- **Typical time**: < 10ms for 10 options
- **Memory**: Minimal - no caching of engine (singleton)

## Best Practices

1. **Provide Complete Metrics**: Fill all 14 evaluation fields for accurate scoring
2. **Use Realistic Ranges**: Keep numeric scores 0.0-1.0, use standard effort/risk values
3. **Add Pros/Cons**: Include at least 2-3 items each for better reasoning
4. **Handle Overrides**: Design UX to accept user selection of alternative options
5. **Log Context**: Pass `round_context` for audit trail completeness

## Future Enhancements

- [ ] Custom weight profiles for different domains
- [ ] Machine learning-based weight optimization
- [ ] Historical recommendation accuracy tracking
- [ ] Multi-level recommendation (compare within categories)
- [ ] Integration with cost estimation engines
- [ ] Automated follow-up recommendations

## See Also

- `cortex/orchestrators/core/solution_recommendation_engine.py` - Implementation
- `cortex/orchestrators/core/interaction_orchestrator.py` - Orchestrator integration
- `cortex/brain/core/orchestrator/conversation_protocol.py` - Protocol integration
- `tests/unit/orchestrators/test_solution_recommendation_integration.py` - Tests
