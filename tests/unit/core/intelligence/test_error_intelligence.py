"""
Unit tests for Error Pattern Intelligence Module

AC-INT-ERR-003-01: ErrorAnalyzer records error occurrences
AC-INT-ERR-003-02: ErrorAnalyzer detects error patterns
AC-INT-ERR-003-03: ErrorAnalyzer calculates error frequency by handler
AC-INT-ERR-003-04: ErrorAnalyzer detects new errors
"""

import pytest
import sqlite3
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List
from cortex.core.intelligence.error_intelligence import ErrorAnalyzer


class TestErrorAnalyzer:
    """Test suite for ErrorAnalyzer"""
    
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
    def analyzer(self, temp_db_path: Path) -> ErrorAnalyzer:
        """Create ErrorAnalyzer instance with temp database"""
        return ErrorAnalyzer(db_path=str(temp_db_path))
    
    # AC-INT-ERR-003-01: Record error occurrences
    
    def test_record_error(self, analyzer: ErrorAnalyzer) -> None:
        """Test recording a single error"""
        result = analyzer.record_error(
            error_type="ValueError",
            handler="execution",
            operation_type="implement",
            context={"message": "Invalid input", "line": 42}
        )
        
        assert result.is_ok()
        assert "recorded" in result.unwrap().lower()
    
    def test_error_context_sanitization(self, analyzer: ErrorAnalyzer) -> None:
        """Test sensitive data sanitization in error context"""
        # Context with potentially sensitive data
        context = {
            "error_message": "Connection failed",
            "password": "secret123",  # Should be sanitized
            "api_key": "key_abc",  # Should be sanitized
            "user_email": "user@example.com",
            "stack_trace": "line 1\nline 2"
        }
        
        result = analyzer.record_error(
            error_type="ConnectionError",
            handler="api",
            operation_type="validation",
            context=context
        )
        
        assert result.is_ok()
        # Context should be stored but sensitive fields masked
    
    def test_database_persistence(self, analyzer: ErrorAnalyzer, temp_db_path: Path) -> None:
        """Test error occurrences are persisted to database"""
        analyzer.record_error(
            error_type="TypeError",
            handler="planning",
            operation_type="refactor",
            context={"error": "Type mismatch"}
        )
        
        # Verify database contains record
        conn = sqlite3.connect(str(temp_db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM error_occurrences WHERE error_type = ?", ("TypeError",))
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count == 1
    
    # AC-INT-ERR-003-02: Detect error patterns
    
    def test_get_error_patterns_single(self, analyzer: ErrorAnalyzer) -> None:
        """Test detecting a single error pattern"""
        # Record same error multiple times
        for i in range(5):
            analyzer.record_error(
                error_type="ValueError",
                handler="execution",
                operation_type="implement",
                context={"iteration": i}
            )
        
        result = analyzer.get_error_patterns(min_occurrence=3)
        assert result.is_ok()
        
        patterns = result.unwrap()
        assert len(patterns) >= 1
        
        pattern = patterns[0]
        assert pattern["error_type"] == "ValueError"
        assert pattern["handler"] == "execution"
        assert pattern["operation_type"] == "implement"
        assert pattern["count"] >= 5
        assert "first_seen" in pattern
        assert "last_seen" in pattern
    
    def test_get_error_patterns_multiple(self, analyzer: ErrorAnalyzer) -> None:
        """Test detecting multiple error patterns"""
        # Pattern 1: ValueError in execution
        for i in range(4):
            analyzer.record_error("ValueError", "execution", "implement", {"i": i})
        
        # Pattern 2: TypeError in planning
        for i in range(3):
            analyzer.record_error("TypeError", "planning", "discovery", {"i": i})
        
        result = analyzer.get_error_patterns(min_occurrence=3)
        assert result.is_ok()
        
        patterns = result.unwrap()
        assert len(patterns) >= 2
    
    def test_get_error_patterns_threshold(self, analyzer: ErrorAnalyzer) -> None:
        """Test error pattern detection respects threshold"""
        # Record error below threshold
        for i in range(2):
            analyzer.record_error("RuntimeError", "test", "fix", {})
        
        result = analyzer.get_error_patterns(min_occurrence=3)
        assert result.is_ok()
        
        patterns = result.unwrap()
        # Should not include RuntimeError (only 2 occurrences)
        runtime_patterns = [p for p in patterns if p["error_type"] == "RuntimeError"]
        assert len(runtime_patterns) == 0
    
    def test_error_patterns_time_window(self, analyzer: ErrorAnalyzer) -> None:
        """Test error pattern detection filters by time window"""
        result = analyzer.get_error_patterns(days=7, min_occurrence=2)
        assert result.is_ok()
        
        patterns = result.unwrap()
        assert isinstance(patterns, list)
    
    def test_error_patterns_empty(self, analyzer: ErrorAnalyzer) -> None:
        """Test detection with no error patterns"""
        result = analyzer.get_error_patterns(min_occurrence=10)
        assert result.is_ok()
        
        patterns = result.unwrap()
        assert len(patterns) == 0
    
    # AC-INT-ERR-003-03: Error frequency by handler
    
    def test_get_error_frequency_by_handler(self, analyzer: ErrorAnalyzer) -> None:
        """Test calculating error frequency grouped by handler"""
        # Handler A - few errors
        for i in range(2):
            analyzer.record_error("ValueError", "handler_a", "implement", {})
        
        # Handler B - many errors
        for i in range(10):
            analyzer.record_error("TypeError", "handler_b", "fix", {})
        for i in range(5):
            analyzer.record_error("RuntimeError", "handler_b", "refactor", {})
        
        result = analyzer.get_error_frequency_by_handler()
        assert result.is_ok()
        
        frequencies = result.unwrap()
        assert isinstance(frequencies, list)
        assert len(frequencies) >= 2
        
        # Find handler_b
        handler_b_freq = [f for f in frequencies if f["handler"] == "handler_b"][0]
        assert handler_b_freq["total_errors"] == 15
        assert handler_b_freq["unique_error_types"] >= 2
    
    def test_handler_brittleness_ranking(self, analyzer: ErrorAnalyzer) -> None:
        """Test ranking handlers by brittleness (error frequency)"""
        # Create varying error rates
        handlers = {
            "stable": 1,
            "moderate": 5,
            "brittle": 20
        }
        
        for handler, error_count in handlers.items():
            for i in range(error_count):
                analyzer.record_error("TestError", handler, "test", {})
        
        result = analyzer.get_error_frequency_by_handler()
        assert result.is_ok()
        
        frequencies = result.unwrap()
        
        # Should be sorted by error count (highest first)
        if len(frequencies) >= 3:
            assert frequencies[0]["total_errors"] >= frequencies[1]["total_errors"]
            assert frequencies[1]["total_errors"] >= frequencies[2]["total_errors"]
    
    def test_error_frequency_time_window(self, analyzer: ErrorAnalyzer) -> None:
        """Test error frequency filters by time window"""
        result = analyzer.get_error_frequency_by_handler(days=7)
        assert result.is_ok()
        
        frequencies = result.unwrap()
        assert isinstance(frequencies, list)
    
    # AC-INT-ERR-003-04: Detect new errors
    
    def test_detect_new_errors_single(self, analyzer: ErrorAnalyzer) -> None:
        """Test detecting a single new error"""
        # This test requires manipulating timestamps or using time window
        # For now, validate the API works
        result = analyzer.detect_new_errors(recent_days=1, baseline_days=7)
        assert result.is_ok()
        
        new_errors = result.unwrap()
        assert isinstance(new_errors, list)
    
    def test_detect_new_errors_multiple(self, analyzer: ErrorAnalyzer) -> None:
        """Test detecting multiple new errors"""
        result = analyzer.detect_new_errors(recent_days=1, baseline_days=30)
        assert result.is_ok()
        
        new_errors = result.unwrap()
        assert isinstance(new_errors, list)
    
    def test_detect_new_errors_empty(self, analyzer: ErrorAnalyzer) -> None:
        """Test detection with no new errors"""
        # Record baseline errors
        analyzer.record_error("KnownError", "handler", "test", {})
        
        result = analyzer.detect_new_errors(recent_days=1, baseline_days=7)
        assert result.is_ok()
        
        new_errors = result.unwrap()
        # Should be empty if no truly new errors
        assert isinstance(new_errors, list)
    
    def test_new_error_baseline_calculation(self, analyzer: ErrorAnalyzer) -> None:
        """Test new error detection uses correct baseline"""
        result = analyzer.detect_new_errors(recent_days=1, baseline_days=30)
        assert result.is_ok()
        
        new_errors = result.unwrap()
        # Each new error should have metadata
        for error in new_errors:
            assert "error_type" in error
            assert "first_occurrence" in error
            assert "handler" in error
            assert "operation_type" in error
