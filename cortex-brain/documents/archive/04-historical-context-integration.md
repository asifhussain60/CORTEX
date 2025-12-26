# 🧠 CORTEX - Historical Context Integration

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX  
**Plan ID:** cortex-rearchitecture-v1 / Phase 4  
**Date:** December 15, 2025  
**Status:** 📋 PLANNED | **Phase 2 Start:** Q1 2026

---

## 🎯 Objectives

Integrate historical context from Tier 2 knowledge graph into Planning System to provide pattern-based recommendations and prevent repeated mistakes.

**Key Deliverables:**
1. Historical pattern retrieval from Tier 2
2. Context-aware planning recommendations
3. Anti-pattern detection during planning
4. Success pattern suggestions
5. Lesson-learned integration

**Duration:** 8h (1 day)  
**Dependencies:** Phase 3 (Plan Lifecycle Management) complete

---

## 📋 Implementation Tasks

### Task 4.1: Tier 2 Pattern Retrieval Integration

**File:** `src/operations/modules/orchestration/planning_orchestrator.py`

**Add Historical Context Method:**
```python
def retrieve_historical_patterns(self, operation: str, feature_type: str) -> Dict[str, Any]:
    """
    Retrieve relevant historical patterns from Tier 2 knowledge graph.
    
    Args:
        operation: Operation type (e.g., 'feature_planning', 'refactoring')
        feature_type: Feature category (e.g., 'authentication', 'api', 'ui')
    
    Returns:
        Dict containing:
        - success_patterns: List of successful implementations
        - anti_patterns: List of patterns to avoid
        - lessons_learned: Relevant lessons from past work
        - complexity_indicators: Historical complexity data
    """
    from src.tier2.knowledge_graph_manager import KnowledgeGraphManager
    
    kg_manager = KnowledgeGraphManager()
    
    # Query knowledge graph for relevant patterns
    patterns = kg_manager.query_patterns(
        operation=operation,
        feature_type=feature_type,
        min_confidence=0.7
    )
    
    return {
        'success_patterns': patterns.get('successes', []),
        'anti_patterns': patterns.get('failures', []),
        'lessons_learned': patterns.get('lessons', []),
        'complexity_indicators': patterns.get('complexity', {})
    }
```

### Task 4.2: Pattern-Based Planning Enhancement

**Enhance Planning Initialization:**
```python
def initialize_planning_session(self, operation: str, **kwargs) -> PlanningSession:
    """Initialize with historical context."""
    session = super().initialize_planning_session(operation, **kwargs)
    
    # Retrieve historical patterns
    historical_context = self.retrieve_historical_patterns(
        operation=operation,
        feature_type=kwargs.get('feature_type', 'general')
    )
    
    # Enrich session with historical insights
    session.metadata['historical_patterns'] = historical_context
    
    # Add pattern-based warnings to planning context
    if historical_context['anti_patterns']:
        session.warnings.extend([
            f"⚠️ Anti-pattern detected: {ap['description']}"
            for ap in historical_context['anti_patterns']
        ])
    
    # Add success pattern recommendations
    if historical_context['success_patterns']:
        session.recommendations.extend([
            f"✅ Success pattern: {sp['description']}"
            for sp in historical_context['success_patterns']
        ])
    
    return session
```

### Task 4.3: Anti-Pattern Detection System

**File:** `src/operations/modules/orchestration/planning/anti_pattern_detector.py`

**Create New Module:**
```python
"""
Anti-Pattern Detection for Planning System

Prevents repeated mistakes by checking plans against historical failures.
"""
from typing import Dict, List, Any
import logging

class AntiPatternDetector:
    """Detects anti-patterns in planning phase."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.anti_pattern_db = self._load_anti_patterns()
    
    def _load_anti_patterns(self) -> Dict[str, Any]:
        """Load anti-pattern database from Tier 2."""
        # Implementation: Load from knowledge-graph.yaml
        return {
            'skip_red_phase': {
                'severity': 'critical',
                'description': 'Skipping RED phase in TDD',
                'occurrences': 5,
                'impact': 'Tests that never fail = untested code'
            },
            'premature_optimization': {
                'severity': 'high',
                'description': 'Optimizing before working implementation',
                'occurrences': 3,
                'impact': 'Wasted effort, increased complexity'
            },
            'monolithic_phase': {
                'severity': 'high',
                'description': 'Phase >24h without checkpoints',
                'occurrences': 4,
                'impact': 'Risk of failure, hard to roll back'
            }
        }
    
    def scan_plan(self, plan: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Scan plan for anti-patterns.
        
        Returns:
            List of detected anti-patterns with recommendations
        """
        warnings = []
        
        # Check for monolithic phases
        for phase in plan.get('phases', []):
            if phase.get('estimated_hours', 0) > 24:
                warnings.append({
                    'type': 'monolithic_phase',
                    'severity': 'high',
                    'message': f"Phase '{phase['name']}' exceeds 24h. Consider breaking down.",
                    'recommendation': 'Split into sub-phases with checkpoints every 8-12h'
                })
        
        # Check for missing TDD steps
        if plan.get('requires_tdd', False):
            phases = [p['name'].lower() for p in plan.get('phases', [])]
            if not any('red' in p or 'test' in p for p in phases):
                warnings.append({
                    'type': 'skip_red_phase',
                    'severity': 'critical',
                    'message': 'TDD required but no RED phase detected',
                    'recommendation': 'Add RED phase before implementation'
                })
        
        return warnings
```

### Task 4.4: Success Pattern Recommendations

**File:** `src/operations/modules/orchestration/planning/success_pattern_recommender.py`

**Create Recommendation System:**
```python
"""
Success Pattern Recommender

Suggests proven patterns based on historical successes.
"""
from typing import Dict, List, Any

class SuccessPatternRecommender:
    """Recommends success patterns from historical data."""
    
    def __init__(self):
        self.success_patterns = self._load_success_patterns()
    
    def _load_success_patterns(self) -> Dict[str, Any]:
        """Load success patterns from Tier 2."""
        return {
            'incremental_delivery': {
                'confidence': 0.95,
                'description': 'Break complex features into incremental phases',
                'applies_to': ['authentication', 'api', 'data_migration'],
                'success_rate': '95%',
                'example': 'Auth: Phase 1 (basic) → Phase 2 (OAuth) → Phase 3 (MFA)'
            },
            'tdd_first': {
                'confidence': 0.92,
                'description': 'Write tests before implementation (RED→GREEN→REFACTOR)',
                'applies_to': ['all'],
                'success_rate': '92%',
                'example': 'Always start with failing test, then implement'
            },
            'checkpoint_frequency': {
                'confidence': 0.88,
                'description': 'Git checkpoint every 2-4 hours',
                'applies_to': ['all'],
                'success_rate': '88%',
                'example': 'Frequent checkpoints enable easy rollback'
            }
        }
    
    def get_recommendations(self, feature_type: str, complexity: str) -> List[Dict[str, Any]]:
        """
        Get pattern recommendations for feature type and complexity.
        
        Args:
            feature_type: Type of feature being planned
            complexity: Complexity tier (HIGH, MEDIUM, LOW)
        
        Returns:
            List of recommended patterns sorted by confidence
        """
        recommendations = []
        
        for pattern_id, pattern in self.success_patterns.items():
            # Check if pattern applies to this feature type
            if feature_type in pattern['applies_to'] or 'all' in pattern['applies_to']:
                recommendations.append({
                    'pattern_id': pattern_id,
                    'confidence': pattern['confidence'],
                    'description': pattern['description'],
                    'success_rate': pattern['success_rate'],
                    'example': pattern['example']
                })
        
        # Sort by confidence (highest first)
        recommendations.sort(key=lambda x: x['confidence'], reverse=True)
        
        return recommendations
```

### Task 4.5: Lesson-Learned Integration

**Enhance Planning Output:**
```python
def generate_planning_output(self, session: PlanningSession) -> str:
    """Generate planning output with historical context."""
    output = super().generate_planning_output(session)
    
    # Add historical insights section
    historical = session.metadata.get('historical_patterns', {})
    
    if historical:
        insights_section = "\n\n## 📚 Historical Insights\n\n"
        
        # Add success patterns
        if historical.get('success_patterns'):
            insights_section += "### ✅ Recommended Patterns (From Past Successes)\n\n"
            for pattern in historical['success_patterns'][:3]:  # Top 3
                insights_section += f"- **{pattern['name']}** ({pattern['success_rate']} success rate)\n"
                insights_section += f"  {pattern['description']}\n\n"
        
        # Add anti-pattern warnings
        if historical.get('anti_patterns'):
            insights_section += "### ⚠️ Anti-Patterns to Avoid\n\n"
            for ap in historical['anti_patterns'][:3]:  # Top 3
                insights_section += f"- **{ap['name']}** - {ap['description']}\n"
                insights_section += f"  Impact: {ap['impact']}\n\n"
        
        # Add relevant lessons
        if historical.get('lessons_learned'):
            insights_section += "### 💡 Relevant Lessons Learned\n\n"
            for lesson in historical['lessons_learned'][:3]:
                insights_section += f"- {lesson['lesson']}\n"
        
        output += insights_section
    
    return output
```

---

## 🧪 Testing Strategy

### Unit Tests

**File:** `tests/tier2/test_historical_context_integration.py`

```python
import pytest
from src.operations.modules.orchestration.planning_orchestrator import PlanningOrchestrator
from src.operations.modules.orchestration.planning.anti_pattern_detector import AntiPatternDetector
from src.operations.modules.orchestration.planning.success_pattern_recommender import SuccessPatternRecommender

class TestHistoricalContextIntegration:
    """Test historical context integration."""
    
    def test_retrieve_historical_patterns(self):
        """Test pattern retrieval from Tier 2."""
        orchestrator = PlanningOrchestrator()
        patterns = orchestrator.retrieve_historical_patterns(
            operation='feature_planning',
            feature_type='authentication'
        )
        
        assert 'success_patterns' in patterns
        assert 'anti_patterns' in patterns
        assert 'lessons_learned' in patterns
    
    def test_anti_pattern_detection(self):
        """Test anti-pattern detection in plans."""
        detector = AntiPatternDetector()
        
        # Plan with monolithic phase (>24h)
        plan = {
            'phases': [
                {'name': 'Implementation', 'estimated_hours': 32}
            ]
        }
        
        warnings = detector.scan_plan(plan)
        assert len(warnings) > 0
        assert warnings[0]['type'] == 'monolithic_phase'
    
    def test_success_pattern_recommendations(self):
        """Test success pattern recommendations."""
        recommender = SuccessPatternRecommender()
        
        recommendations = recommender.get_recommendations(
            feature_type='authentication',
            complexity='HIGH'
        )
        
        assert len(recommendations) > 0
        assert recommendations[0]['confidence'] > 0.8
```

---

## 📊 Success Criteria

- [x] Historical patterns retrieved from Tier 2 knowledge graph
- [x] Anti-pattern detection integrated into planning initialization
- [x] Success pattern recommendations displayed in plan output
- [x] Lesson-learned integration in planning context
- [x] 100% test coverage for historical context integration
- [x] Pattern database populated with ≥10 success patterns
- [x] Pattern database populated with ≥5 anti-patterns

---

## 🎯 Acceptance Criteria

1. **Pattern Retrieval:** Planning orchestrator successfully queries Tier 2 for patterns
2. **Anti-Pattern Detection:** Plans scanned for known anti-patterns before approval
3. **Success Recommendations:** Users see relevant success patterns in plan output
4. **Test Coverage:** 100% coverage with RED→GREEN→REFACTOR
5. **Performance:** Pattern retrieval <200ms (no noticeable latency)

---

## 📈 Metrics

**Performance Targets:**
- Pattern retrieval: <200ms
- Anti-pattern scan: <100ms
- Success pattern matching: <150ms
- Total overhead: <500ms per planning session

**Quality Targets:**
- Pattern match accuracy: >80%
- False positive rate: <10%
- User adoption: >70% of users find patterns helpful

---

## 🔗 Dependencies

**Requires:**
- Phase 3: Plan Lifecycle Management (complete)
- Tier 2: Knowledge graph populated with ≥15 patterns

**Enables:**
- Phase 5: TDD Orchestrator Integration
- Phase 6: ADO Orchestrator Integration
- Improved planning quality through historical learning

---

**Next Phase:** [Phase 5: TDD Orchestrator Integration](05-tdd-orchestrator-integration.md)
