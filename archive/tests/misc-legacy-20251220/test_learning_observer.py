"""
Tests for LearningObserver

Test coverage:
    - Phase completion event handling
    - TDD cycle event handling
    - Debug session event handling (RCA capture)
    - Performance validation (<50ms overhead)
    - Error handling and logging

Author: Asif Hussain
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
import time

from src.orchestrators.learning_observer import LearningObserver


class TestLearningObserver:
    """Test suite for LearningObserver pattern capture."""
    
    @pytest.fixture
    def mock_kg(self):
        """Mock Knowledge Graph for testing."""
        kg = Mock()
        kg.store_pattern = Mock(return_value={"pattern_id": "test-123"})
        return kg
    
    @pytest.fixture
    def observer(self, mock_kg):
        """Create LearningObserver instance with mocked KG."""
        return LearningObserver(mock_kg)
    
    # ==================== Phase Completion Tests ====================
    
    def test_on_phase_completion_captures_pattern(self, observer, mock_kg):
        """Test that phase completion event captures planning pattern."""
        # Arrange
        event = {
            "phase_id": "1.1",
            "phase_name": "Requirements Analysis",
            "duration_seconds": 120.5,
            "dor_compliant": True,
            "dod_compliant": True,
            "threat_model_applied": True,
            "acceptance_criteria_defined": True,
            "estimated_hours": 8,
            "actual_hours": 10
        }
        
        # Act
        observer.on_phase_completion(event)
        
        # Assert
        mock_kg.store_pattern.assert_called_once()
        call_args = mock_kg.store_pattern.call_args
        
        assert call_args.kwargs["pattern_type"] == "workflow"
        assert "Requirements Analysis" in call_args.kwargs["title"]
        assert call_args.kwargs["metadata"]["dor_compliant"] is True
        assert call_args.kwargs["metadata"]["dod_compliant"] is True
        assert call_args.kwargs["source"] == "planning_orchestrator"
        assert "cortex.planning" in call_args.kwargs["namespaces"]
    
    def test_phase_completion_calculates_estimation_accuracy(self, observer, mock_kg):
        """Test estimation accuracy calculation."""
        event = {
            "phase_id": "2.3",
            "phase_name": "Implementation",
            "estimated_hours": 10,
            "actual_hours": 12  # 20% over estimate
        }
        
        observer.on_phase_completion(event)
        
        call_args = mock_kg.store_pattern.call_args
        accuracy = call_args.kwargs["metadata"]["estimation_accuracy"]
        
        assert accuracy == 1.2  # actual / estimated = 12 / 10
    
    def test_phase_completion_performance_under_50ms(self, observer, mock_kg):
        """Test that pattern capture completes in <50ms."""
        event = {
            "phase_id": "3.1",
            "phase_name": "Testing",
            "duration_seconds": 60.0
        }
        
        start = time.time()
        observer.on_phase_completion(event)
        elapsed_ms = (time.time() - start) * 1000
        
        assert elapsed_ms < 50, f"Pattern capture took {elapsed_ms:.1f}ms (target: <50ms)"
    
    def test_phase_completion_error_handling(self, observer, mock_kg):
        """Test error handling when storage fails."""
        mock_kg.store_pattern.side_effect = Exception("Database error")
        
        event = {"phase_id": "4.1", "phase_name": "Deployment"}
        
        # Should not raise exception
        observer.on_phase_completion(event)
    
    # ==================== TDD Cycle Tests ====================
    
    def test_on_tdd_cycle_completion_captures_pattern(self, observer, mock_kg):
        """Test that TDD cycle event captures TDD pattern."""
        event = {
            "phase": "GREEN",
            "test_count": 5,
            "code_lines_changed": 42,
            "duration_seconds": 180.0,
            "tests_passed": True,
            "coverage_delta": 0.08
        }
        
        observer.on_tdd_cycle_completion(event)
        
        mock_kg.store_pattern.assert_called_once()
        call_args = mock_kg.store_pattern.call_args
        
        assert call_args.kwargs["pattern_type"] == "tdd_cycle"
        assert "GREEN" in call_args.kwargs["title"]
        assert call_args.kwargs["metadata"]["phase"] == "GREEN"
        assert call_args.kwargs["metadata"]["test_count"] == 5
        assert call_args.kwargs["source"] == "tdd_workflow_orchestrator"
        assert "cortex.tdd" in call_args.kwargs["namespaces"]
    
    def test_tdd_cycle_red_phase_captured(self, observer, mock_kg):
        """Test RED phase cycle captured."""
        event = {
            "phase": "RED",
            "test_count": 3,
            "code_lines_changed": 0,
            "duration_seconds": 30.0,
            "tests_passed": False
        }
        
        observer.on_tdd_cycle_completion(event)
        
        call_args = mock_kg.store_pattern.call_args
        assert call_args.kwargs["metadata"]["tests_passed"] is False
        assert call_args.kwargs["metadata"]["phase"] == "RED"
    
    def test_tdd_cycle_refactor_phase_captured(self, observer, mock_kg):
        """Test REFACTOR phase cycle captured."""
        event = {
            "phase": "REFACTOR",
            "test_count": 5,
            "code_lines_changed": 25,
            "duration_seconds": 120.0,
            "tests_passed": True
        }
        
        observer.on_tdd_cycle_completion(event)
        
        call_args = mock_kg.store_pattern.call_args
        assert call_args.kwargs["metadata"]["phase"] == "REFACTOR"
    
    # ==================== Debug Session (RCA) Tests ====================
    
    def test_on_debug_session_completion_captures_rca(self, observer, mock_kg):
        """Test that debug session captures RCA pattern."""
        event = {
            "bug_id": "BUG-123",
            "symptom": "Authentication timeout on login",
            "root_cause": "Missing retry logic in auth service",
            "fix_applied": "Added exponential backoff with 3 retries",
            "prevention": "Review all network calls for retry patterns",
            "affected_features": ["login", "authentication"],
            "recurrence_risk": "high",
            "tests_added": 2,
            "duration_seconds": 300.0
        }
        
        observer.on_debug_session_completion(event)
        
        mock_kg.store_pattern.assert_called_once()
        call_args = mock_kg.store_pattern.call_args
        
        assert call_args.kwargs["pattern_type"] == "bug_resolution"
        assert "Authentication timeout" in call_args.kwargs["title"]
        assert call_args.kwargs["metadata"]["symptom"] == event["symptom"]
        assert call_args.kwargs["metadata"]["root_cause"] == event["root_cause"]
        assert call_args.kwargs["metadata"]["recurrence_risk"] == "high"
        assert call_args.kwargs["metadata"]["affected_features"] == ["login", "authentication"]
        assert call_args.kwargs["source"] == "debug_workflow_orchestrator"
        assert "cortex.debug" in call_args.kwargs["namespaces"]
        assert "cortex.rca" in call_args.kwargs["namespaces"]
    
    def test_rca_high_recurrence_risk_flagged(self, observer, mock_kg):
        """Test high recurrence risk patterns are flagged."""
        event = {
            "bug_id": "BUG-456",
            "symptom": "SQL injection vulnerability",
            "root_cause": "Missing input validation",
            "fix_applied": "Added parameterized queries",
            "prevention": "Security review all DB calls",
            "affected_features": ["search", "user_profile"],
            "recurrence_risk": "high"  # Critical risk
        }
        
        observer.on_debug_session_completion(event)
        
        call_args = mock_kg.store_pattern.call_args
        assert call_args.kwargs["metadata"]["recurrence_risk"] == "high"
        assert call_args.kwargs["confidence"] == 0.95  # High confidence for security bugs
    
    def test_rca_captures_affected_features(self, observer, mock_kg):
        """Test affected features are captured for cross-feature analysis."""
        event = {
            "bug_id": "BUG-789",
            "symptom": "Memory leak in dashboard",
            "root_cause": "Event listeners not cleaned up",
            "fix_applied": "Added cleanup in componentWillUnmount",
            "prevention": "Review lifecycle methods",
            "affected_features": ["dashboard", "metrics", "charts"],
            "recurrence_risk": "medium"
        }
        
        observer.on_debug_session_completion(event)
        
        call_args = mock_kg.store_pattern.call_args
        assert len(call_args.kwargs["metadata"]["affected_features"]) == 3
        assert "dashboard" in call_args.kwargs["metadata"]["affected_features"]
    
    def test_rca_pattern_performance(self, observer, mock_kg):
        """Test RCA pattern capture completes in <50ms."""
        event = {
            "bug_id": "BUG-999",
            "symptom": "Performance regression",
            "root_cause": "N+1 query problem",
            "fix_applied": "Added eager loading",
            "prevention": "Review ORM queries",
            "affected_features": ["api"],
            "recurrence_risk": "low"
        }
        
        start = time.time()
        observer.on_debug_session_completion(event)
        elapsed_ms = (time.time() - start) * 1000
        
        assert elapsed_ms < 50, f"RCA capture took {elapsed_ms:.1f}ms (target: <50ms)"
    
    # ==================== Confidence Calculation Tests ====================
    
    def test_confidence_calculation_base(self, observer):
        """Test base confidence calculation."""
        event = {}
        confidence = observer._calculate_confidence(event)
        assert confidence == 0.7  # Base confidence
    
    def test_confidence_increases_with_dor(self, observer):
        """Test confidence increases with DoR compliance."""
        event = {"dor_compliant": True}
        confidence = observer._calculate_confidence(event)
        assert abs(confidence - 0.8) < 0.01  # 0.7 + 0.1 (floating point tolerance)
    
    def test_confidence_increases_with_dod(self, observer):
        """Test confidence increases with DoD compliance."""
        event = {"dod_compliant": True}
        confidence = observer._calculate_confidence(event)
        assert abs(confidence - 0.8) < 0.01  # 0.7 + 0.1 (floating point tolerance)
    
    def test_confidence_caps_at_095(self, observer):
        """Test confidence capped at 0.95."""
        event = {"dor_compliant": True, "dod_compliant": True}
        confidence = observer._calculate_confidence(event)
        assert abs(confidence - 0.9) < 0.01  # 0.7 + 0.1 + 0.1 (floating point tolerance)
    
    # ==================== Estimation Accuracy Tests ====================
    
    def test_estimation_accuracy_perfect(self, observer):
        """Test perfect estimation accuracy (1.0)."""
        event = {"estimated_hours": 10, "actual_hours": 10}
        accuracy = observer._calculate_estimation_accuracy(event)
        assert accuracy == 1.0
    
    def test_estimation_accuracy_underestimate(self, observer):
        """Test underestimation (actual > estimated)."""
        event = {"estimated_hours": 10, "actual_hours": 15}
        accuracy = observer._calculate_estimation_accuracy(event)
        assert accuracy == 1.5  # 50% underestimate
    
    def test_estimation_accuracy_overestimate(self, observer):
        """Test overestimation (actual < estimated)."""
        event = {"estimated_hours": 10, "actual_hours": 8}
        accuracy = observer._calculate_estimation_accuracy(event)
        assert accuracy == 0.8  # 20% overestimate
    
    def test_estimation_accuracy_zero_handling(self, observer):
        """Test zero handling in estimation."""
        event = {"estimated_hours": 0, "actual_hours": 10}
        accuracy = observer._calculate_estimation_accuracy(event)
        assert accuracy == 0.0  # Safe default
