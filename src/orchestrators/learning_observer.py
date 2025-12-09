"""
CORTEX Learning Observer

Event-driven pattern capture system for automated Knowledge Graph updates.
Subscribes to orchestrator lifecycle events to extract and store patterns.

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.

Design:
    - Observer pattern (decoupled from orchestrators)
    - <50ms overhead per event
    - Automatic Tier 2 storage
    - No blocking operations

Usage:
    from src.orchestrators.learning_observer import LearningObserver
    from src.tier2.knowledge_graph import KnowledgeGraph
    
    kg = KnowledgeGraph()
    observer = LearningObserver(kg)
    
    # Subscribe to orchestrator events
    planning_orchestrator.subscribe(observer)
    tdd_orchestrator.subscribe(observer)
    
    # Observer automatically captures patterns on phase completion
"""

from typing import Dict, Any, Optional
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)


class LearningObserver:
    """
    Observer that captures patterns from orchestrator lifecycle events.
    
    Events:
        - phase_completion: Planning phase completed
        - tdd_cycle_completion: RED→GREEN→REFACTOR cycle completed
        - debug_session_completion: Bug resolution completed
    
    Pattern Types:
        - planning_decision: DoR/DoD decisions, threat model outcomes
        - tdd_cycle: Test-to-code ratios, refactoring frequency
        - bug_resolution: RCA with symptom, root_cause, fix, prevention
    """
    
    def __init__(self, knowledge_graph):
        """
        Initialize observer with Knowledge Graph connection.
        
        Args:
            knowledge_graph: KnowledgeGraph instance for pattern storage
        """
        self.kg = knowledge_graph
        self.start_time = None
    
    def on_phase_completion(self, event: Dict[str, Any]) -> None:
        """
        Handle planning phase completion event.
        
        Event payload:
            - phase_id: str (e.g., "1.1", "2.3")
            - phase_name: str
            - duration_seconds: float
            - dor_compliant: bool
            - dod_compliant: bool
            - threat_model_applied: bool
            - acceptance_criteria_defined: bool
            - estimated_hours: int
            - actual_hours: int (if completed)
        
        Patterns captured:
            - DoR/DoD compliance patterns
            - Estimation accuracy (estimated vs actual)
            - Threat modeling decisions
        """
        self.start_time = datetime.now()
        
        try:
            phase_id = event.get("phase_id")
            phase_name = event.get("phase_name")
            
            # Extract planning decision pattern
            pattern = {
                "title": f"Planning Phase: {phase_name}",
                "content": self._extract_planning_content(event),
                "pattern_type": "workflow",  # Use valid schema pattern type
                "confidence": self._calculate_confidence(event),
                "metadata": {
                    "phase_id": phase_id,
                    "phase_name": phase_name,  # Add phase_name to metadata
                    "dor_compliant": event.get("dor_compliant", False),
                    "dod_compliant": event.get("dod_compliant", False),
                    "threat_model_applied": event.get("threat_model_applied", False),
                    "estimation_accuracy": self._calculate_estimation_accuracy(event),
                    "duration_seconds": event.get("duration_seconds", 0),
                    "estimated_hours": event.get("estimated_hours", 0),
                    "actual_hours": event.get("actual_hours", 0),
                    **{k: v for k, v in event.items() if k not in ['phase_id', 'phase_name']},  # Preserve custom fields
                    "captured_at": datetime.now().isoformat()
                },
                "source": "planning_orchestrator",
                "is_pinned": False,
                "scope": "cortex",
                "namespaces": ["cortex.planning"],
                "is_cortex_internal": True
            }
            
            # Store in Tier 2
            pattern_id = str(uuid.uuid4())
            self.kg.store_pattern(pattern_id=pattern_id, **pattern)
            
            elapsed = (datetime.now() - self.start_time).total_seconds() * 1000
            logger.info(f"✓ Captured planning pattern: {phase_name} ({elapsed:.1f}ms)")
            
            # Validate <50ms performance target
            if elapsed > 50:
                logger.warning(f"⚠️  Pattern capture exceeded 50ms target: {elapsed:.1f}ms")
        
        except Exception as e:
            logger.error(f"❌ Failed to capture planning pattern: {e}")
    
    def on_tdd_cycle_completion(self, event: Dict[str, Any]) -> None:
        """
        Handle TDD cycle completion event.
        
        Event payload:
            - cycle_phase: str ("RED", "GREEN", "REFACTOR")
            - test_count: int
            - code_lines_changed: int
            - duration_seconds: float
            - tests_passed: bool
            - coverage_delta: float
        
        Patterns captured:
            - RED→GREEN→REFACTOR timing
            - Test-to-code ratios
            - Refactoring frequency
        """
        self.start_time = datetime.now()
        
        try:
            cycle_phase = event.get("phase", event.get("cycle_phase"))  # Support both 'phase' and 'cycle_phase'
            
            pattern = {
                "title": f"TDD Cycle: {cycle_phase}",
                "content": self._extract_tdd_content(event),
                "pattern_type": "tdd_cycle",
                "confidence": 0.9,
                "metadata": {
                    "phase": cycle_phase,  # Use consistent field name
                    "cycle_number": event.get("cycle_number", 0),
                    "tests_added": event.get("tests_added", 0),
                    "tests_passing": event.get("tests_passing", 0),
                    "tests_failing": event.get("tests_failing", 0),
                    "code_lines_added": event.get("code_lines_added", 0),
                    "refactoring_applied": event.get("refactoring_applied", False),
                    "test_to_code_ratio": event.get("test_to_code_ratio", 0.0),
                    "duration_seconds": event.get("duration_seconds", 0),
                    **{k: v for k, v in event.items() if k not in ['phase', 'cycle_phase', 'cycle_number']},  # Preserve custom fields
                    "captured_at": datetime.now().isoformat()
                },
                "source": "tdd_workflow_orchestrator",
                "is_pinned": False,
                "scope": "cortex",
                "namespaces": ["cortex.tdd"],
                "is_cortex_internal": True
            }
            
            pattern_id = str(uuid.uuid4())
            self.kg.store_pattern(pattern_id=pattern_id, **pattern)
            
            elapsed = (datetime.now() - self.start_time).total_seconds() * 1000
            logger.info(f"✓ Captured TDD pattern: {cycle_phase} ({elapsed:.1f}ms)")
        
        except Exception as e:
            logger.error(f"❌ Failed to capture TDD pattern: {e}")
    
    def on_debug_session_completion(self, event: Dict[str, Any]) -> None:
        """
        Handle debug session completion event.
        
        Event payload:
            - session_id: str
            - symptom: str
            - root_cause: str
            - fix_applied: str
            - prevention: str
            - affected_features: List[str]
            - recurrence_risk: str ("low", "medium", "high")
            - target: str
            - duration_seconds: float
        
        Patterns captured:
            - RCA (Root Cause Analysis)
            - Bug resolution patterns
            - Recurrence prevention strategies
        """
        self.start_time = datetime.now()
        
        try:
            session_id = event.get("session_id", event.get("bug_id"))
            symptom = event.get("symptom", "Unknown symptom")
            
            pattern = {
                "title": f"Bug Resolution: {symptom[:50]}",
                "content": self._extract_rca_content(event),
                "pattern_type": "bug_resolution",
                "confidence": 0.95,
                "metadata": {
                    # Flatten RCA fields to top level for query compatibility
                    "symptom": symptom,
                    "root_cause": event.get("root_cause", "Unknown"),
                    "fix_applied": event.get("fix_applied", ""),
                    "prevention": event.get("prevention", ""),
                    "recurrence_risk": event.get("recurrence_risk", "medium"),
                    "affected_features": event.get("affected_features", []),
                    # Session metadata
                    "session_id": session_id,
                    "debug_session_id": session_id,
                    "target": event.get("target", ""),
                    "tests_added": event.get("tests_added", 0),
                    "duration_seconds": event.get("duration_seconds", 0),
                    "started_at": event.get("started_at", ""),
                    "completed_at": event.get("completed_at", ""),
                    "captured_at": datetime.now().isoformat(),
                    # Preserve custom fields
                    **{k: v for k, v in event.items() if k not in [
                        'symptom', 'root_cause', 'fix_applied', 'prevention', 
                        'recurrence_risk', 'affected_features', 'session_id', 
                        'target', 'duration_seconds'
                    ]}
                },
                "source": "debug_workflow_orchestrator",
                "is_pinned": False,
                "scope": "cortex",
                "namespaces": ["cortex.debug", "cortex.rca"],
                "is_cortex_internal": True
            }
            
            pattern_id = str(uuid.uuid4())
            self.kg.store_pattern(pattern_id=pattern_id, **pattern)
            
            elapsed = (datetime.now() - self.start_time).total_seconds() * 1000
            logger.info(f"✓ Captured RCA pattern: {session_id} ({elapsed:.1f}ms)")
        
        except Exception as e:
            logger.error(f"❌ Failed to capture RCA pattern: {e}")
    
    # ==================== Private Helper Methods ====================
    
    def _extract_planning_content(self, event: Dict[str, Any]) -> str:
        """Extract planning pattern content from event."""
        lines = [
            f"Phase: {event.get('phase_name', 'Unknown')}",
            f"DoR Compliant: {event.get('dor_compliant', False)}",
            f"DoD Compliant: {event.get('dod_compliant', False)}",
            f"Threat Model Applied: {event.get('threat_model_applied', False)}",
        ]
        
        if event.get("estimated_hours") and event.get("actual_hours"):
            accuracy = self._calculate_estimation_accuracy(event)
            lines.append(f"Estimation Accuracy: {accuracy:.1%}")
        
        return "\n".join(lines)
    
    def _extract_tdd_content(self, event: Dict[str, Any]) -> str:
        """Extract TDD pattern content from event."""
        return "\n".join([
            f"Cycle Phase: {event.get('cycle_phase', 'Unknown')}",
            f"Test Count: {event.get('test_count', 0)}",
            f"Code Lines Changed: {event.get('code_lines_changed', 0)}",
            f"Duration: {event.get('duration_seconds', 0):.1f}s",
            f"Tests Passed: {event.get('tests_passed', False)}",
            f"Coverage Delta: {event.get('coverage_delta', 0.0):.1%}"
        ])
    
    def _extract_rca_content(self, event: Dict[str, Any]) -> str:
        """Extract RCA pattern content from event."""
        return "\n".join([
            f"Symptom: {event.get('symptom', 'Unknown')}",
            f"Root Cause: {event.get('root_cause', 'Unknown')}",
            f"Fix Applied: {event.get('fix_applied', '')}",
            f"Prevention: {event.get('prevention', '')}",
            f"Recurrence Risk: {event.get('recurrence_risk', 'medium')}",
            f"Affected Features: {', '.join(event.get('affected_features', []))}"
        ])
    
    def _calculate_confidence(self, event: Dict[str, Any]) -> float:
        """Calculate pattern confidence based on event data."""
        base_confidence = 0.7
        
        # Increase confidence if DoR/DoD compliant
        if event.get("dor_compliant"):
            base_confidence += 0.1
        if event.get("dod_compliant"):
            base_confidence += 0.1
        
        # Cap at 0.95
        return min(base_confidence, 0.95)
    
    def _calculate_estimation_accuracy(self, event: Dict[str, Any]) -> float:
        """Calculate estimation accuracy (1.0 = perfect, <1.0 = under, >1.0 = over)."""
        estimated = event.get("estimated_hours", 0)
        actual = event.get("actual_hours", 0)
        
        if estimated == 0 or actual == 0:
            return 0.0
        
        return actual / estimated
    
    # ---------------------- RCA Query Interface (Phase 5.1.6) ----------------------
    def query_similar_bugs(self, symptom: str, limit: int = 5) -> list:
        """
        Find similar bug resolutions by symptom.
        
        Args:
            symptom: Bug symptom description
            limit: Maximum results
        
        Returns:
            List of similar RCA patterns with prevention strategies
        """
        return self.kg.query_rca_by_symptom(symptom, limit=limit)
    
    def get_high_risk_bugs(self, feature: Optional[str] = None, limit: int = 10) -> list:
        """
        Get high-risk bugs, optionally filtered by feature.
        
        Args:
            feature: Optional feature filter
            limit: Maximum results
        
        Returns:
            List of high-risk RCA patterns
        """
        if feature:
            return self.kg.query_rca_by_risk_and_feature("high", feature, limit=limit)
        return self.kg.query_rca_by_risk("high", limit=limit)
    
    def get_feature_bug_report(self, feature: str) -> Dict[str, Any]:
        """
        Generate bug impact report for a feature.
        
        Args:
            feature: Feature name
        
        Returns:
            Report with bug count, risk distribution, prevention strategies
        """
        bugs = self.kg.query_rca_by_feature(feature, limit=100)
        
        risk_counts = {"high": 0, "medium": 0, "low": 0}
        for bug in bugs:
            metadata = bug.get("metadata", {})
            if isinstance(metadata, str):
                import json
                try:
                    metadata = json.loads(metadata)
                except:
                    metadata = {}
            
            risk = metadata.get("recurrence_risk", "unknown").lower()
            if risk in risk_counts:
                risk_counts[risk] += 1
        
        preventions = self.kg.get_rca_prevention_strategies(feature, limit=10)
        
        return {
            "feature": feature,
            "total_bugs": len(bugs),
            "risk_distribution": risk_counts,
            "prevention_strategies": [p["prevention"] for p in preventions],
            "top_bugs": bugs[:5]
        }
    
    def generate_rca_summary_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive RCA summary across all patterns.
        
        Returns:
            Summary with total count, risk distribution, feature impact
        """
        summary = self.kg.generate_rca_summary()
        feature_impact = self.kg.generate_feature_impact_report()
        
        return {
            **summary,
            "top_affected_features": feature_impact[:10]
        }

