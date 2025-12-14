# Phase 07: Learning Subsystem

**🔗 Breadcrumb:** [← Back to Master Plan](cortex-3.9-master.md)

**Status:** ⏳ Pending  
**Phase ID:** 07  
**Estimated Time:** 3 hours (180 minutes)  
**Actual Start:** -  
**Actual End:** -  
**Actual Work Time:** -  
**Dependencies:** Phase 01 (Tiered Routing) ✅, Phase 02 (Complexity Analyzer) ✅, Phase 03 (Planning Orchestrator 3.0) ✅  
**Blocks:** Phase 17 (Proactive Intelligence)

---

## 🎯 Phase Objective

Implement learning subsystem with `planning_learner.py` to continuously improve routing accuracy through feedback loops and complexity calibration.

**Success Criteria:**
- ✅ `planning_learner.py` module operational
- ✅ Route accuracy feedback loop functional (target: 95%+ accuracy)
- ✅ Complexity calibration with user corrections
- ✅ Learning metrics tracked and persisted
- ✅ Integration with TieredRouter for dynamic improvement
- ✅ 100% test coverage with passing tests

---

## 🏗️ Implementation Plan

### Task 1: Core Learning Engine (1.5 hours)

**Create `src/operations/modules/learning/planning_learner.py`:**

```python
"""
Planning Learner - Continuous improvement for routing accuracy.

Tracks routing decisions, collects feedback, and adapts complexity
scoring to improve Planning System 3.0 tier classification.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json

@dataclass
class RoutingDecision:
    """Record of a routing decision for learning."""
    request: str
    predicted_tier: int
    actual_tier: Optional[int]
    complexity_score: float
    timestamp: str
    feedback: Optional[str] = None
    was_correct: Optional[bool] = None

class PlanningLearner:
    """Learns from routing decisions to improve accuracy."""
    
    def __init__(self, brain_path: Path):
        self.brain_path = brain_path
        self.learning_db = brain_path / "tier2" / "routing_decisions.jsonl"
        self.metrics_file = brain_path / "metrics" / "routing_accuracy.json"
        
        # Learning parameters
        self.calibration_factors = {
            'scope_weight': 0.3,
            'dependencies_weight': 0.25,
            'risk_weight': 0.25,
            'uncertainty_weight': 0.2
        }
        
    def record_decision(self, request: str, tier: int, complexity: float):
        """Record a routing decision for future learning."""
        decision = RoutingDecision(
            request=request,
            predicted_tier=tier,
            actual_tier=None,  # Will be set via feedback
            complexity_score=complexity,
            timestamp=datetime.now().isoformat()
        )
        
        self._append_to_db(decision)
        
    def provide_feedback(self, request: str, correct_tier: int, reason: str = None):
        """User provides feedback on routing accuracy."""
        decisions = self._load_recent_decisions(limit=100)
        
        for decision in decisions:
            if decision.request == request and decision.actual_tier is None:
                decision.actual_tier = correct_tier
                decision.was_correct = (decision.predicted_tier == correct_tier)
                decision.feedback = reason
                self._update_decision(decision)
                self._recalibrate_weights(decision)
                break
                
    def get_accuracy_metrics(self) -> Dict[str, Any]:
        """Calculate current routing accuracy metrics."""
        decisions = self._load_all_decisions()
        
        if not decisions:
            return {'accuracy': 0.0, 'total_decisions': 0}
            
        with_feedback = [d for d in decisions if d.actual_tier is not None]
        correct = [d for d in with_feedback if d.was_correct]
        
        return {
            'accuracy': len(correct) / len(with_feedback) if with_feedback else 0.0,
            'total_decisions': len(decisions),
            'decisions_with_feedback': len(with_feedback),
            'correct_predictions': len(correct),
            'tier_breakdown': self._calculate_tier_accuracy(with_feedback)
        }
        
    def _recalibrate_weights(self, decision: RoutingDecision):
        """Adjust complexity weights based on feedback."""
        if decision.was_correct:
            return  # No adjustment needed
            
        # If predicted tier was too high, reduce weights
        # If predicted tier was too low, increase weights
        adjustment = 0.05 if decision.predicted_tier < decision.actual_tier else -0.05
        
        # Apply adjustment to all weights proportionally
        for key in self.calibration_factors:
            self.calibration_factors[key] = max(0.1, min(0.4, 
                self.calibration_factors[key] + adjustment
            ))
            
        # Normalize weights to sum to 1.0
        total = sum(self.calibration_factors.values())
        self.calibration_factors = {
            k: v / total for k, v in self.calibration_factors.items()
        }
        
        self._save_calibration()
```

### Task 2: Feedback Collection Interface (45 min)

**Integration with TieredRouter:**

```python
# In tiered_router.py

def route_request(self, request: str) -> RoutingDecision:
    """Route request with learning integration."""
    tier = self._classify_tier(request)
    complexity = self.complexity_analyzer.analyze(request)
    
    # Record decision for learning
    if hasattr(self, 'learner'):
        self.learner.record_decision(request, tier, complexity.overall_score)
    
    return RoutingDecision(tier=tier, complexity=complexity)
```

**User Feedback Mechanism:**

```python
def collect_feedback(router: TieredRouter, request: str, user_tier: int):
    """Collect user feedback on routing accuracy."""
    learner = router.learner
    
    if learner:
        reason = input("Why was the routing incorrect? (optional): ")
        learner.provide_feedback(request, user_tier, reason)
        
        # Show updated accuracy
        metrics = learner.get_accuracy_metrics()
        print(f"Current routing accuracy: {metrics['accuracy']:.2%}")
```

### Task 3: Complexity Calibration (45 min)

**Adaptive Complexity Scoring:**

```python
class ComplexityAnalyzer:
    """Enhanced with learning-based calibration."""
    
    def __init__(self, learner: PlanningLearner = None):
        self.learner = learner
        self.default_weights = {
            'scope': 0.3,
            'dependencies': 0.25,
            'risk': 0.25,
            'uncertainty': 0.2
        }
        
    def analyze(self, request: str) -> ComplexityScore:
        """Analyze with learned calibration."""
        # Get learned weights if available
        weights = self.learner.calibration_factors if self.learner else self.default_weights
        
        # Calculate dimension scores
        scope = self._score_scope(request)
        deps = self._score_dependencies(request)
        risk = self._score_risk(request)
        uncertainty = self._score_uncertainty(request)
        
        # Apply learned weights
        overall = (
            scope * weights['scope_weight'] +
            deps * weights['dependencies_weight'] +
            risk * weights['risk_weight'] +
            uncertainty * weights['uncertainty_weight']
        )
        
        return ComplexityScore(
            scope=scope,
            dependencies=deps,
            risk=risk,
            uncertainty=uncertainty,
            overall_score=overall
        )
```

---

## 📦 Expected Deliverables

### Code Deliverables
- ✅ `src/operations/modules/learning/planning_learner.py`
- ✅ `src/operations/modules/learning/__init__.py`
- ✅ Integration hooks in `tiered_router.py`
- ✅ Integration hooks in `complexity_analyzer.py`
- ✅ Feedback collection utilities

### Data Structures
- ✅ `cortex-brain/tier2/routing_decisions.jsonl` (learning database)
- ✅ `cortex-brain/metrics/routing_accuracy.json` (accuracy tracking)
- ✅ Calibration factors persistence

### Test Deliverables
- ✅ `tests/test_planning_learner.py`
  - Decision recording tests
  - Feedback processing tests
  - Calibration adjustment tests
  - Accuracy metric calculation tests
- ✅ Integration test: Router + Learner workflow

### Documentation Deliverables
- ✅ Learning subsystem architecture documentation
- ✅ Feedback collection guide for users
- ✅ Calibration algorithm explanation
- ✅ Accuracy improvement tracking guide

---

## 🔄 Next Steps

1. **Phase 01-03 Validation:** Ensure routing and planning orchestrators operational
2. **Data Collection Period:** Gather 100+ routing decisions for initial calibration
3. **Feedback Collection:** Implement user feedback prompts in CLI
4. **Metrics Dashboard:** Create visualization for routing accuracy trends
5. **Integration with Phase 17:** Proactive intelligence uses learning insights

---

## 🔗 Integration Points

### Upstream Dependencies
- **TieredRouter (Phase 01):** Core routing decisions to learn from
- **ComplexityAnalyzer (Phase 02):** Complexity scores to calibrate
- **Planning Orchestrator 3.0 (Phase 03):** Execution outcomes to validate

### Downstream Consumers
- **Proactive Intelligence (Phase 17):** Uses learning insights for recommendations
- **System Maintenance (Phase 06):** Accuracy metrics in healthcheck
- **Integration Tests (Phase 16):** Validation of learning effectiveness

### Data Flow
```
User Request → TieredRouter → Record Decision → PlanningLearner
                    ↓                                  ↓
             Execute Operation                  Store in tier2/
                    ↓                                  ↓
             User Feedback → Provide Feedback → Recalibrate Weights
                                                       ↓
                                              Update ComplexityAnalyzer
```

---

## 🚨 Risk Mitigation

### Risk 1: Insufficient Feedback Data
**Mitigation:**
- Start with default weights validated against 100+ manual classifications
- Implement automated feedback for obvious misclassifications
- Prompt users for feedback on borderline cases only

### Risk 2: Weight Oscillation
**Mitigation:**
- Implement learning rate decay (reduce adjustment over time)
- Set weight boundaries (0.1 to 0.4 per dimension)
- Require minimum 10 samples before recalibration

### Risk 3: Privacy Concerns
**Mitigation:**
- Store only request text, not sensitive data
- Implement data retention policy (90 days)
- Allow opt-out of learning data collection

---

## 📊 Success Metrics

- ✅ Routing accuracy improves from 70% to 95%+ over 1000 operations
- ✅ Calibration stabilizes after 200-300 feedback samples
- ✅ Tier 1/2 accuracy reaches 98%+ (simpler classifications)
- ✅ Tier 3/4 accuracy reaches 90%+ (complex classifications)
- ✅ Learning overhead <50ms per decision
- ✅ Feedback collection rate ≥20% of total operations

---

**Phase Owner:** Asif Hussain  
**Phase Status:** ⏳ Awaiting Phase 01-03 completion  
**Last Updated:** 2024-12-14
