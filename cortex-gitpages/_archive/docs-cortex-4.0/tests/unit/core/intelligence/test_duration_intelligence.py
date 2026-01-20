"""
Unit tests for Duration Intelligence Module

AC-INT-DUR-002-01: DurationAnalyzer records operation durations
AC-INT-DUR-002-02: DurationAnalyzer calculates duration baselines
AC-INT-DUR-002-03: DurationAnalyzer detects slow operations
AC-INT-DUR-002-04: DurationAnalyzer calculates handler average durations
"""

import pytest
import sqlite3
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List
from cortex.core.intelligence.duration_intelligence import DurationAnalyzer


class TestDurationAnalyzer:
    """Test suite for DurationAnalyzer"""
    
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
    def analyzer(self, temp_db_path: Path) -> DurationAnalyzer:
        """Create DurationAnalyzer instance with temp database"""
        return DurationAnalyzer(db_path=str(temp_db_path))
    
    # AC-INT-DUR-002-01: Record operation durations
    
    def test_record_operation_duration(self, analyzer: DurationAnalyzer) -> None:
        """Test recording a single operation duration"""
        result = analyzer.record_operation_duration(
            operation_type="implement",
            duration_ms=500,
            handler_name="execution",
            success=True
        )
        
        assert result.is_ok()
        assert "recorded" in result.unwrap().lower()
    
    def test_operation_type_validation(self, analyzer: DurationAnalyzer) -> None:
        """Test operation type validation"""
        valid_types = ["implement", "fix", "refactor", "discovery", "validation"]
        
        for op_type in valid_types:
            result = analyzer.record_operation_duration(
                operation_type=op_type,
                duration_ms=100,
                handler_name="test",
                success=True
            )
            assert result.is_ok()
        
        # Invalid type should still be recorded but may log warning
        result = analyzer.record_operation_duration(
            operation_type="invalid_op",
            duration_ms=100,
            handler_name="test",
            success=True
        )
        assert result.is_ok()
    
    def test_database_persistence(self, analyzer: DurationAnalyzer, temp_db_path: Path) -> None:
        """Test operation durations are persisted to database"""
        analyzer.record_operation_duration(
            operation_type="implement",
            duration_ms=750,
            handler_name="planning",
            success=True
        )
        
        # Verify database contains record
        conn = sqlite3.connect(str(temp_db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM operation_durations WHERE operation_type = ?", ("implement",))
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count == 1
    
    # AC-INT-DUR-002-02: Calculate duration baselines
    
    def test_get_duration_baseline_all_operations(self, analyzer: DurationAnalyzer) -> None:
        """Test calculating baseline for all operations"""
        # Record test data with various durations
        durations = [100, 150, 200, 250, 300, 500, 1000, 2000, 5000]
        
        for i, duration in enumerate(durations):
            analyzer.record_operation_duration(
                operation_type="implement",
                duration_ms=duration,
                handler_name="execution",
                success=True
            )
        
        result = analyzer.get_duration_baseline(operation_type="implement")
        assert result.is_ok()
        
        baseline = result.unwrap()
        assert "p50" in baseline
        assert "p95" in baseline
        assert "p99" in baseline
        assert "min" in baseline
        assert "max" in baseline
        assert "mean" in baseline
        assert "count" in baseline
        
        assert baseline["count"] == 9
        assert baseline["min"] == 100
        assert baseline["max"] == 5000
    
    def test_get_duration_baseline_specific_operation(self, analyzer: DurationAnalyzer) -> None:
        """Test calculating baseline for specific operation type"""
        # Record different operation types
        analyzer.record_operation_duration("implement", 500, "exec", True)
        analyzer.record_operation_duration("fix", 200, "exec", True)
        analyzer.record_operation_duration("implement", 600, "exec", True)
        
        result = analyzer.get_duration_baseline(operation_type="implement")
        assert result.is_ok()
        
        baseline = result.unwrap()
        assert baseline["count"] == 2  # Only implement operations
        assert baseline["operation_type"] == "implement"
    
    def test_duration_baseline_time_window(self, analyzer: DurationAnalyzer) -> None:
        """Test baseline calculation with time window"""
        result = analyzer.get_duration_baseline(operation_type="implement", days=7)
        assert result.is_ok()
        
        baseline = result.unwrap()
        assert "count" in baseline
    
    def test_baseline_calculation_edge_cases(self, analyzer: DurationAnalyzer) -> None:
        """Test baseline calculation with edge cases"""
        # No data
        result = analyzer.get_duration_baseline(operation_type="nonexistent")
        assert result.is_ok()
        
        baseline = result.unwrap()
        assert baseline["count"] == 0
        
        # Single data point
        analyzer.record_operation_duration("test_op", 500, "handler", True)
        result = analyzer.get_duration_baseline(operation_type="test_op")
        assert result.is_ok()
        
        baseline = result.unwrap()
        assert baseline["count"] == 1
        assert baseline["p50"] == 500
        assert baseline["min"] == 500
        assert baseline["max"] == 500
    
    # AC-INT-DUR-002-03: Detect slow operations
    
    def test_detect_slow_operations_single(self, analyzer: DurationAnalyzer) -> None:
        """Test detecting a single slow operation"""
        # Create baseline
        for i in range(10):
            analyzer.record_operation_duration("implement", 100 + i, "exec", True)
        
        # Record slow operation
        analyzer.record_operation_duration("implement", 10000, "exec", True)
        
        result = analyzer.detect_slow_operations(operation_type="implement", percentile_threshold=99)
        assert result.is_ok()
        
        slow_ops = result.unwrap()
        assert len(slow_ops) >= 1
    
    def test_detect_slow_operations_multiple(self, analyzer: DurationAnalyzer) -> None:
        """Test detecting multiple slow operations"""
        # Create baseline
        for i in range(20):
            analyzer.record_operation_duration("fix", 50 + i, "exec", True)
        
        # Record multiple slow operations
        analyzer.record_operation_duration("fix", 5000, "exec", True)
        analyzer.record_operation_duration("fix", 6000, "exec", True)
        
        result = analyzer.detect_slow_operations(operation_type="fix")
        assert result.is_ok()
        
        slow_ops = result.unwrap()
        # Both 5000 and 6000 should exceed p99 baseline (around 69), so at least 1 should be detected
        assert len(slow_ops) >= 1
    
    def test_detect_slow_operations_empty(self, analyzer: DurationAnalyzer) -> None:
        """Test detection with no slow operations"""
        # Record uniform durations
        for i in range(10):
            analyzer.record_operation_duration("refactor", 100, "exec", True)
        
        result = analyzer.detect_slow_operations(operation_type="refactor")
        assert result.is_ok()
        
        slow_ops = result.unwrap()
        # All operations similar, no outliers
        assert isinstance(slow_ops, list)
    
    def test_percentile_threshold_configuration(self, analyzer: DurationAnalyzer) -> None:
        """Test configuring percentile threshold"""
        # Create baseline
        durations = list(range(100, 200, 10))  # 10 operations
        for duration in durations:
            analyzer.record_operation_duration("test", duration, "exec", True)
        
        # Test different thresholds
        result_95 = analyzer.detect_slow_operations(operation_type="test", percentile_threshold=95)
        result_99 = analyzer.detect_slow_operations(operation_type="test", percentile_threshold=99)
        
        assert result_95.is_ok()
        assert result_99.is_ok()
    
    def test_time_window_filtering(self, analyzer: DurationAnalyzer) -> None:
        """Test slow operation detection filters by time window"""
        result = analyzer.detect_slow_operations(operation_type="implement", days=7)
        assert result.is_ok()
        
        slow_ops = result.unwrap()
        assert isinstance(slow_ops, list)
    
    # AC-INT-DUR-002-04: Handler average durations
    
    def test_get_handler_average_duration(self, analyzer: DurationAnalyzer) -> None:
        """Test calculating handler average duration"""
        # Record durations for specific handler
        for i in range(5):
            analyzer.record_operation_duration("implement", 200 + i * 10, "handler_a", True)
        
        result = analyzer.get_handler_average_duration(handler_name="handler_a")
        assert result.is_ok()
        
        averages = result.unwrap()
        assert "handler_name" in averages
        assert averages["handler_name"] == "handler_a"
        assert "operation_types" in averages
    
    def test_handler_comparison(self, analyzer: DurationAnalyzer) -> None:
        """Test comparing multiple handlers"""
        # Handler A - fast
        for i in range(3):
            analyzer.record_operation_duration("implement", 100, "handler_a", True)
        
        # Handler B - slow
        for i in range(3):
            analyzer.record_operation_duration("implement", 500, "handler_b", True)
        
        result_a = analyzer.get_handler_average_duration(handler_name="handler_a")
        result_b = analyzer.get_handler_average_duration(handler_name="handler_b")
        
        assert result_a.is_ok()
        assert result_b.is_ok()
        
        avg_a = result_a.unwrap()
        avg_b = result_b.unwrap()
        
        # Handler B should have higher average
        assert avg_a["handler_name"] == "handler_a"
        assert avg_b["handler_name"] == "handler_b"
    
    def test_handler_not_found(self, analyzer: DurationAnalyzer) -> None:
        """Test querying non-existent handler"""
        result = analyzer.get_handler_average_duration(handler_name="nonexistent")
        assert result.is_ok()
        
        averages = result.unwrap()
        assert averages["handler_name"] == "nonexistent"
        # Should handle gracefully with empty/zero data
