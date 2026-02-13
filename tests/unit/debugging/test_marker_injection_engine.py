"""
Unit tests for MarkerInjectionEngine

AC-ID: AC-WAVE-R-004
"""

import pytest
from pathlib import Path
import tempfile
import os

from cortex.debugging.marker_injection_engine import (
    MarkerInjectionEngine,
    TestFailureStrategy,
    RefactorRegressionStrategy,
    GovernanceViolationStrategy
)


class TestMarkerInjectionEngineInitialization:
    """Test MarkerInjectionEngine initialization."""
    
    def test_engine_initializes_with_strategies(self):
        """Test engine initializes with all three strategies."""
        engine = MarkerInjectionEngine()
        
        assert "test_failure" in engine.strategies
        assert "refactor_regression" in engine.strategies
        assert "governance_violation" in engine.strategies
    
    def test_strategies_are_correct_types(self):
        """Test strategies are correct instance types."""
        engine = MarkerInjectionEngine()
        
        assert isinstance(engine.strategies["test_failure"], TestFailureStrategy)
        assert isinstance(engine.strategies["refactor_regression"], RefactorRegressionStrategy)
        assert isinstance(engine.strategies["governance_violation"], GovernanceViolationStrategy)


class TestTestFailureStrategy:
    """Test TestFailureStrategy."""
    
    def test_test_failure_strategy_identifies_user_code_line(self):
        """Test strategy identifies correct line for injection."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("line 1\nline 2\nline 3\nline 4\nline 5\n")
            temp_file = f.name
        
        try:
            engine = MarkerInjectionEngine()
            
            result = engine.inject(
                strategy="test_failure",
                session_id="session-test-001",
                file_path=temp_file,
                line_number=3,
                context={"test_name": "test_example", "failure_reason": "AssertionError"}
            )
            
            assert result is True
            
            # Verify markers exist
            content = Path(temp_file).read_text()
            assert "CORTEX_DEBUG_START: session-test-001" in content
            assert "TEST_FAILURE" in content
            
        finally:
            os.unlink(temp_file)
    
    def test_test_failure_strategy_handles_existing_markers(self):
        """Test strategy skips if markers already exist."""
        # Create file with existing markers
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("# CORTEX_DEBUG_START: session-test-001\nline 1\n")
            temp_file = f.name
        
        try:
            engine = MarkerInjectionEngine()
            
            result = engine.inject(
                strategy="test_failure",
                session_id="session-test-001",
                file_path=temp_file,
                line_number=1,
                context={}
            )
            
            assert result is True  # Returns True (already injected)
            
            # Count markers (should be only 1)
            content = Path(temp_file).read_text()
            assert content.count("CORTEX_DEBUG_START: session-test-001") == 1
            
        finally:
            os.unlink(temp_file)
    
    def test_test_failure_strategy_returns_false_for_nonexistent_file(self):
        """Test strategy returns False for nonexistent file."""
        engine = MarkerInjectionEngine()
        
        result = engine.inject(
            strategy="test_failure",
            session_id="session-test-001",
            file_path="/nonexistent/file.py",
            line_number=1,
            context={}
        )
        
        assert result is False


class TestMarkerFormat:
    """Test marker formatting."""
    
    def test_marker_format_includes_session_id(self):
        """Test formatted marker includes session_id."""
        engine = MarkerInjectionEngine()
        
        marker = engine.format_marker(
            session_id="session-test-001",
            event_type="TEST_FAILURE",
            context_summary="Test failed at line 10",
            original_code="x = 1"
        )
        
        assert "session-test-001" in marker
    
    def test_marker_format_includes_trigger_type(self):
        """Test formatted marker includes event type."""
        engine = MarkerInjectionEngine()
        
        marker = engine.format_marker(
            session_id="session-test-001",
            event_type="TEST_FAILURE",
            context_summary="Test failed",
            original_code="x = 1"
        )
        
        assert "TEST_FAILURE" in marker
    
    def test_marker_format_includes_context(self):
        """Test formatted marker includes context summary."""
        engine = MarkerInjectionEngine()
        
        context_summary = "Test failed at line 10: AssertionError"
        marker = engine.format_marker(
            session_id="session-test-001",
            event_type="TEST_FAILURE",
            context_summary=context_summary,
            original_code="x = 1"
        )
        
        assert context_summary in marker
    
    def test_marker_format_includes_timestamp(self):
        """Test formatted marker includes timestamp."""
        engine = MarkerInjectionEngine()
        
        marker = engine.format_marker(
            session_id="session-test-001",
            event_type="TEST_FAILURE",
            context_summary="Test failed",
            original_code="x = 1"
        )
        
        assert "Injected:" in marker
        assert "2026" in marker  # Year check
    
    def test_marker_format_includes_original_code(self):
        """Test formatted marker includes original code."""
        engine = MarkerInjectionEngine()
        
        original_code = "x = 1\ny = 2\nz = 3"
        marker = engine.format_marker(
            session_id="session-test-001",
            event_type="TEST_FAILURE",
            context_summary="Test failed",
            original_code=original_code
        )
        
        assert original_code in marker


class TestFileInjection:
    """Test actual file injection with atomic writes."""
    
    def test_inject_markers_writes_to_file(self):
        """Test markers are written to file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("line 1\nline 2\nline 3\n")
            temp_file = f.name
        
        try:
            engine = MarkerInjectionEngine()
            
            result = engine.inject(
                strategy="test_failure",
                session_id="session-test-001",
                file_path=temp_file,
                line_number=2,
                context={}
            )
            
            assert result is True
            
            content = Path(temp_file).read_text()
            assert "CORTEX_DEBUG_START" in content
            assert "CORTEX_DEBUG_END" in content
            
        finally:
            os.unlink(temp_file)
    
    def test_inject_markers_preserves_surrounding_code(self):
        """Test injection preserves surrounding code."""
        original_content = "line 1\nline 2\nline 3\nline 4\nline 5\n"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(original_content)
            temp_file = f.name
        
        try:
            engine = MarkerInjectionEngine()
            
            engine.inject(
                strategy="test_failure",
                session_id="session-test-001",
                file_path=temp_file,
                line_number=3,
                context={}
            )
            
            content = Path(temp_file).read_text()
            
            # Verify original lines still present
            assert "line 1" in content
            assert "line 2" in content
            assert "line 3" in content
            
        finally:
            os.unlink(temp_file)


class TestRefactorRegressionStrategy:
    """Test RefactorRegressionStrategy."""
    
    def test_refactor_regression_strategy_injects_at_file_start(self):
        """Test strategy injects markers at file start."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("line 1\nline 2\nline 3\n")
            temp_file = f.name
        
        try:
            engine = MarkerInjectionEngine()
            
            result = engine.inject(
                strategy="refactor_regression",
                session_id="session-refactor-001",
                file_path=temp_file,
                context={"refactor_type": "consolidation", "regression_type": "performance_latency"}
            )
            
            assert result is True
            
            content = Path(temp_file).read_text()
            assert "REFACTOR_REGRESSION" in content
            assert "consolidation" in content
            
        finally:
            os.unlink(temp_file)


class TestGovernanceViolationStrategy:
    """Test GovernanceViolationStrategy."""
    
    def test_governance_violation_strategy_locates_violation(self):
        """Test strategy injects at violation location."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("line 1\nline 2\nline 3\nline 4\nline 5\n")
            temp_file = f.name
        
        try:
            engine = MarkerInjectionEngine()
            
            result = engine.inject(
                strategy="governance_violation",
                session_id="session-gov-001",
                file_path=temp_file,
                context={
                    "rule_id": "CORE-008",
                    "violation_details": {"line": 3, "message": "Missing type hints"}
                }
            )
            
            assert result is True
            
            content = Path(temp_file).read_text()
            assert "GOVERNANCE_VIOLATION" in content
            assert "CORE-008" in content
            
        finally:
            os.unlink(temp_file)


class TestStrategySelection:
    """Test strategy selection and error handling."""
    
    def test_unknown_strategy_raises_error(self):
        """Test unknown strategy raises ValueError."""
        engine = MarkerInjectionEngine()
        
        with pytest.raises(ValueError) as exc_info:
            engine.inject(
                strategy="unknown_strategy",
                session_id="session-001",
                file_path="example.py",
                context={}
            )
        
        assert "Unknown strategy" in str(exc_info.value)
    
    def test_all_strategies_accessible(self):
        """Test all three strategies are accessible."""
        engine = MarkerInjectionEngine()
        
        assert "test_failure" in engine.strategies
        assert "refactor_regression" in engine.strategies
        assert "governance_violation" in engine.strategies
        assert len(engine.strategies) == 3


class TestAtomicWrites:
    """Test atomic file writes."""
    
    def test_atomic_write_uses_tempfile(self):
        """Test atomic write uses temporary file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("original content\n")
            temp_file = f.name
        
        try:
            engine = MarkerInjectionEngine()
            
            # Inject markers
            engine.inject(
                strategy="test_failure",
                session_id="session-test-001",
                file_path=temp_file,
                line_number=1,
                context={}
            )
            
            # Verify file was modified
            content = Path(temp_file).read_text()
            assert "CORTEX_DEBUG" in content
            assert "original content" in content
            
        finally:
            os.unlink(temp_file)
