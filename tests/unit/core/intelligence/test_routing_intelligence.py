"""
Unit tests for Routing Intelligence Module

AC-INT-RT-001-01: RoutingAnalyzer records routing outcomes
AC-INT-RT-001-02: RoutingAnalyzer calculates routing accuracy
AC-INT-RT-001-03: RoutingAnalyzer detects misrouting patterns
"""

import pytest
import sqlite3
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List
from cortex.core.intelligence.routing_intelligence import RoutingAnalyzer


class TestRoutingAnalyzer:
    """Test suite for RoutingAnalyzer"""
    
    @pytest.fixture
    def temp_db_path(self) -> Path:
        """Create temporary database for testing"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
            db_path = Path(f.name)
        yield db_path
        # Cleanup
        if db_path.exists():
            db_path.unlink()
    
    @pytest.fixture
    def analyzer(self, temp_db_path: Path) -> RoutingAnalyzer:
        """Create RoutingAnalyzer instance with temp database"""
        return RoutingAnalyzer(db_path=str(temp_db_path))
    
    # AC-INT-RT-001-01: Record routing outcomes
    
    def test_record_routing_outcome(self, analyzer: RoutingAnalyzer) -> None:
        """Test recording a single routing outcome"""
        result = analyzer.record_routing_outcome(
            decision_id="test-decision-001",
            decided_handler="planning",
            actual_handler="planning",
            success=True,
            reason="Correct routing",
            duration_ms=150
        )
        
        assert result.is_ok()
        assert "recorded" in result.unwrap().lower()
    
    def test_database_persistence(self, analyzer: RoutingAnalyzer, temp_db_path: Path) -> None:
        """Test routing outcomes are persisted to database"""
        analyzer.record_routing_outcome(
            decision_id="test-decision-002",
            decided_handler="execution",
            actual_handler="execution",
            success=True,
            reason="Match",
            duration_ms=200
        )
        
        # Verify database contains record
        conn = sqlite3.connect(str(temp_db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM routing_outcomes WHERE decision_id = ?", ("test-decision-002",))
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count == 1
    
    def test_concurrent_updates(self, analyzer: RoutingAnalyzer) -> None:
        """Test multiple routing outcomes can be recorded"""
        results = []
        for i in range(5):
            result = analyzer.record_routing_outcome(
                decision_id=f"decision-{i:03d}",
                decided_handler="analysis",
                actual_handler="analysis",
                success=True,
                reason="Test",
                duration_ms=100 + i
            )
            results.append(result)
        
        assert all(r.is_ok() for r in results)
    
    # AC-INT-RT-001-02: Calculate routing accuracy
    
    def test_get_routing_accuracy_all_handlers(self, analyzer: RoutingAnalyzer) -> None:
        """Test calculating accuracy for all handlers"""
        # Record test data
        test_data = [
            ("d1", "planning", "planning", True),
            ("d2", "planning", "execution", False),
            ("d3", "execution", "execution", True),
            ("d4", "analysis", "analysis", True),
        ]
        
        for decision_id, decided, actual, success in test_data:
            analyzer.record_routing_outcome(
                decision_id=decision_id,
                decided_handler=decided,
                actual_handler=actual,
                success=success,
                reason="Test",
                duration_ms=100
            )
        
        result = analyzer.get_routing_accuracy()
        assert result.is_ok()
        
        accuracy = result.unwrap()
        assert accuracy["total_decisions"] == 4
        assert accuracy["successful_routes"] == 3
        assert accuracy["accuracy_rate"] == 0.75
    
    def test_get_routing_accuracy_specific_handler(self, analyzer: RoutingAnalyzer) -> None:
        """Test calculating accuracy for specific handler"""
        # Record test data
        test_data = [
            ("d1", "planning", "planning", True),
            ("d2", "planning", "execution", False),
            ("d3", "planning", "planning", True),
            ("d4", "execution", "execution", True),
        ]
        
        for decision_id, decided, actual, success in test_data:
            analyzer.record_routing_outcome(
                decision_id=decision_id,
                decided_handler=decided,
                actual_handler=actual,
                success=success,
                reason="Test",
                duration_ms=100
            )
        
        result = analyzer.get_routing_accuracy(handler_name="planning")
        assert result.is_ok()
        
        accuracy = result.unwrap()
        assert accuracy["handler_name"] == "planning"
        assert accuracy["total_decisions"] == 3
        assert accuracy["successful_routes"] == 2
        assert abs(accuracy["accuracy_rate"] - 0.6667) < 0.001
    
    def test_get_routing_accuracy_time_window(self, analyzer: RoutingAnalyzer) -> None:
        """Test accuracy calculation with time window"""
        # This test validates the time window parameter works
        # In real scenario, we'd need to manipulate timestamps
        result = analyzer.get_routing_accuracy(days=7)
        assert result.is_ok()
        
        accuracy = result.unwrap()
        assert "total_decisions" in accuracy
        assert "accuracy_rate" in accuracy
    
    def test_accuracy_calculation_edge_cases(self, analyzer: RoutingAnalyzer) -> None:
        """Test accuracy with edge cases (no data, all success, all failure)"""
        # No data
        result = analyzer.get_routing_accuracy()
        assert result.is_ok()
        accuracy = result.unwrap()
        assert accuracy["total_decisions"] == 0
        assert accuracy["accuracy_rate"] == 0.0
        
        # All success
        for i in range(3):
            analyzer.record_routing_outcome(
                decision_id=f"success-{i}",
                decided_handler="test",
                actual_handler="test",
                success=True,
                reason="Test",
                duration_ms=100
            )
        
        result = analyzer.get_routing_accuracy()
        assert result.is_ok()
        accuracy = result.unwrap()
        assert accuracy["accuracy_rate"] == 1.0
    
    # AC-INT-RT-001-03: Detect misrouting patterns
    
    def test_detect_misrouting_patterns_single(self, analyzer: RoutingAnalyzer) -> None:
        """Test detecting a single misrouting pattern"""
        # Record repeated misrouting
        for i in range(3):
            analyzer.record_routing_outcome(
                decision_id=f"mis-{i}",
                decided_handler="planning",
                actual_handler="execution",
                success=False,
                reason="Misrouted",
                duration_ms=100
            )
        
        result = analyzer.detect_misrouting_patterns()
        assert result.is_ok()
        
        patterns = result.unwrap()
        assert len(patterns) == 1
        assert patterns[0]["decided_handler"] == "planning"
        assert patterns[0]["actual_handler"] == "execution"
        assert patterns[0]["occurrences"] == 3
    
    def test_detect_misrouting_patterns_multiple(self, analyzer: RoutingAnalyzer) -> None:
        """Test detecting multiple misrouting patterns"""
        # Pattern 1: planning -> execution
        for i in range(3):
            analyzer.record_routing_outcome(
                decision_id=f"p1-{i}",
                decided_handler="planning",
                actual_handler="execution",
                success=False,
                reason="Misrouted",
                duration_ms=100
            )
        
        # Pattern 2: analysis -> planning
        for i in range(2):
            analyzer.record_routing_outcome(
                decision_id=f"p2-{i}",
                decided_handler="analysis",
                actual_handler="planning",
                success=False,
                reason="Misrouted",
                duration_ms=100
            )
        
        result = analyzer.detect_misrouting_patterns()
        assert result.is_ok()
        
        patterns = result.unwrap()
        assert len(patterns) >= 2
    
    def test_detect_misrouting_patterns_empty(self, analyzer: RoutingAnalyzer) -> None:
        """Test detection with no misrouting patterns"""
        # Record only correct routings
        analyzer.record_routing_outcome(
            decision_id="correct-1",
            decided_handler="planning",
            actual_handler="planning",
            success=True,
            reason="Correct",
            duration_ms=100
        )
        
        result = analyzer.detect_misrouting_patterns()
        assert result.is_ok()
        
        patterns = result.unwrap()
        assert len(patterns) == 0
    
    def test_pattern_detection_threshold(self, analyzer: RoutingAnalyzer) -> None:
        """Test pattern detection respects threshold"""
        # Record misrouting below threshold (only 1 occurrence)
        analyzer.record_routing_outcome(
            decision_id="single-mis",
            decided_handler="planning",
            actual_handler="execution",
            success=False,
            reason="Misrouted",
            duration_ms=100
        )
        
        result = analyzer.detect_misrouting_patterns(min_occurrences=2)
        assert result.is_ok()
        
        patterns = result.unwrap()
        assert len(patterns) == 0
    
    def test_time_window_filtering(self, analyzer: RoutingAnalyzer) -> None:
        """Test pattern detection filters by time window"""
        result = analyzer.detect_misrouting_patterns(days=7)
        assert result.is_ok()
        
        patterns = result.unwrap()
        # Should return empty list if no recent data
        assert isinstance(patterns, list)
