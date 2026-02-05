"""
Tests for TDDOrchestrator + BrittlenessScanner integration (AC-PHASE24-005)

Tests:
1. BrittlenessScanner called pre-execution (before TDD RED phase)
2. BrittlenessScanner called post-execution (after TDD GREEN phase)
3. Violations logged to audit trail as warnings (non-blocking)
4. Regression checks don't block TDD flow (warnings only)

Author: Asif Hussain
Phase: 24.5 (Integration)
TDD: RED phase - write failing tests first
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator
from cortex.orchestrators.support.brittleness_scanner import (
    BrittlenessScanner,
    BrittlenessReport,
    CircularDependencyViolation
)


class TestTDDRegressionIntegration:
    """Test BrittlenessScanner integration with TDDOrchestrator"""
    
    @pytest.fixture
    def tdd_orchestrator(self, tmp_path):
        """Create TDDOrchestrator instance"""
        return TDDOrchestrator(knowledge_root=tmp_path)
    
    @pytest.fixture
    def mock_brittleness_scanner(self):
        """Create mock BrittlenessScanner"""
        scanner = Mock(spec=BrittlenessScanner)
        # Default: no violations
        clean_report = BrittlenessReport(
            brittleness_score=0.0,
            circular_dependencies=[],
            coupling_violations=[],
            scanned_path="/test/path"
        )
        scanner.scan.return_value = clean_report
        return scanner
    
    def test_brittleness_scan_before_tdd_execution(
        self, tdd_orchestrator, mock_brittleness_scanner
    ):
        """Test BrittlenessScanner called BEFORE TDD execution"""
        # Inject mock scanner
        tdd_orchestrator._brittleness_scanner = mock_brittleness_scanner
        
        # Execute TDD request
        context = {
            "source": "mcp_gateway",
            "module_path": "cortex/test_module.py",
            "domain": "testing"
        }
        
        result = tdd_orchestrator._execute_domain_logic(
            "implement test feature", None, context
        )
        
        # Assert: BrittlenessScanner.scan() called
        assert mock_brittleness_scanner.scan.called, (
            "BrittlenessScanner.scan() should be called before TDD execution"
        )
        
        # Assert: Called at least once (pre-execution scan)
        assert mock_brittleness_scanner.scan.call_count >= 1, (
            f"Expected at least 1 scan call, got {mock_brittleness_scanner.scan.call_count}"
        )
    
    def test_brittleness_violations_logged_as_warnings(
        self, tdd_orchestrator, mock_brittleness_scanner, caplog
    ):
        """Test brittleness violations logged as warnings (non-blocking)"""
        # Setup: Scanner returns violations
        violation_report = BrittlenessReport(
            brittleness_score=0.8,
            circular_dependencies=[
                CircularDependencyViolation(
                    cycle_path=["module_a", "module_b", "module_a"],
                    severity="HIGH",
                    description="Circular dependency detected"
                )
            ],
            scanned_path="/test/path"
        )
        mock_brittleness_scanner.scan.return_value = violation_report
        tdd_orchestrator._brittleness_scanner = mock_brittleness_scanner
        
        # Execute TDD request
        context = {
            "source": "mcp_gateway",
            "module_path": "cortex/test_module.py",
            "domain": "testing"
        }
        
        import logging
        with caplog.at_level(logging.WARNING):
            result = tdd_orchestrator._execute_domain_logic(
                "implement test feature", None, context
            )
        
        # Assert: Violations logged as warnings
        # Note: This test will FAIL initially (RED phase)
        assert any(
            "brittleness" in record.message.lower() or "circular" in record.message.lower()
            for record in caplog.records
        ), "Brittleness violations should be logged as warnings"
    
    def test_regression_checks_non_blocking(
        self, tdd_orchestrator, mock_brittleness_scanner
    ):
        """Test regression checks don't block TDD execution"""
        # Setup: Scanner returns HIGH severity violations
        violation_report = BrittlenessReport(
            brittleness_score=0.9,  # Very brittle
            circular_dependencies=[
                CircularDependencyViolation(
                    cycle_path=["a", "b", "c", "a"],
                    severity="HIGH",
                    description="Critical cycle"
                )
            ],
            scanned_path="/test/path"
        )
        mock_brittleness_scanner.scan.return_value = violation_report
        tdd_orchestrator._brittleness_scanner = mock_brittleness_scanner
        
        # Execute TDD request
        context = {
            "source": "mcp_gateway",
            "module_path": "cortex/test_module.py",
            "domain": "testing"
        }
        
        result = tdd_orchestrator._execute_domain_logic(
            "implement test feature", None, context
        )
        
        # Assert: TDD execution succeeds despite violations
        assert result.is_ok(), (
            "TDD execution should succeed even with HIGH brittleness violations "
            "(warnings only, non-blocking)"
        )
    
    def test_scanner_failure_does_not_block_tdd(
        self, tdd_orchestrator
    ):
        """Test scanner exceptions don't block TDD execution"""
        # Setup: Scanner raises exception
        failing_scanner = Mock(spec=BrittlenessScanner)
        failing_scanner.scan.side_effect = Exception("Scanner crashed")
        tdd_orchestrator._brittleness_scanner = failing_scanner
        
        # Execute TDD request
        context = {
            "source": "mcp_gateway",
            "module_path": "cortex/test_module.py",
            "domain": "testing"
        }
        
        result = tdd_orchestrator._execute_domain_logic(
            "implement test feature", None, context
        )
        
        # Assert: TDD execution succeeds despite scanner failure
        assert result.is_ok(), (
            "TDD execution should succeed even if BrittlenessScanner crashes"
        )
