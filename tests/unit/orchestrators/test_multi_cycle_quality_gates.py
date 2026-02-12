"""
Tests for Multi-Cycle TDD Quality Gates (ENH-088 Stage 2)

AC-ENH-088-002: Quality gate enhancements
Tests verify:
- Coverage validation via pytest-cov
- Latency validation via timing instrumentation
- Extensibility validation via pattern detection
- EventBus notifications (CYCLE_COMPLETE, CRITERIA_MET)

CORE Governance:
  - CORE-008: TDD (tests BEFORE implementation)
  - CORE-011: Type hints mandatory
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling

Author: Asif Hussain
Date: 2026-02-11
Phase: ENH-088 Stage 2 (Quality Gates)
"""

import pytest
from dataclasses import dataclass
from typing import Dict, Any, List
from unittest.mock import Mock, MagicMock, patch, call
import time

try:
    from cortex.orchestrators.core.tdd_orchestrator import (
        TDDOrchestrator,
        SuccessCriteria,
        CycleMetrics,
        GateResult,
    )
except ImportError:
    pass


class TestCoverageValidation:
    """Test pytest-cov integration for coverage validation (RED phase)"""
    
    def test_validate_coverage_method_exists(self):
        """Test TDDOrchestrator has validate_coverage method"""
        orchestrator = TDDOrchestrator()
        assert hasattr(orchestrator, 'validate_coverage')
    
    def test_validate_coverage_accepts_test_suite_path(self):
        """Test validate_coverage accepts test suite path parameter"""
        orchestrator = TDDOrchestrator()
        
        result = orchestrator.validate_coverage(
            test_suite="tests/unit/test_example.py",
            min_coverage=0.85
        )
        
        assert result is not None
        assert "coverage_percent" in result
    
    def test_validate_coverage_returns_coverage_metrics(self):
        """Test validate_coverage returns coverage percentage"""
        orchestrator = TDDOrchestrator()
        
        result = orchestrator.validate_coverage(
            test_suite="tests/unit/test_example.py",
            min_coverage=0.85
        )
        
        assert "coverage_percent" in result
        assert "lines_covered" in result
        assert "lines_total" in result
    
    def test_validate_coverage_detects_below_threshold(self):
        """Test validate_coverage detects coverage below threshold"""
        orchestrator = TDDOrchestrator()
        
        result = orchestrator.validate_coverage(
            test_suite="tests/unit/test_example.py",
            min_coverage=0.95  # High threshold
        )
        
        assert "passes_threshold" in result
        # Should fail with high threshold in most cases


class TestLatencyValidation:
    """Test timing instrumentation for latency validation (RED phase)"""
    
    def test_validate_latency_method_exists(self):
        """Test TDDOrchestrator has validate_latency method"""
        orchestrator = TDDOrchestrator()
        assert hasattr(orchestrator, 'validate_latency')
    
    def test_validate_latency_measures_execution_time(self):
        """Test validate_latency measures test execution time"""
        orchestrator = TDDOrchestrator()
        
        result = orchestrator.validate_latency(
            test_suite="tests/unit/test_example.py",
            max_latency_ms=200
        )
        
        assert "avg_latency_ms" in result
        assert result["avg_latency_ms"] >= 0
    
    def test_validate_latency_returns_per_test_breakdown(self):
        """Test validate_latency provides per-test timing breakdown"""
        orchestrator = TDDOrchestrator()
        
        result = orchestrator.validate_latency(
            test_suite="tests/unit/test_example.py",
            max_latency_ms=200
        )
        
        assert "test_timings" in result
        assert isinstance(result["test_timings"], list)
    
    def test_validate_latency_detects_slow_tests(self):
        """Test validate_latency identifies tests exceeding threshold"""
        orchestrator = TDDOrchestrator()
        
        result = orchestrator.validate_latency(
            test_suite="tests/unit/test_example.py",
            max_latency_ms=50  # Low threshold
        )
        
        assert "slow_tests" in result
        # Should detect slow tests with low threshold


class TestExtensibilityValidation:
    """Test extensibility pattern detection (RED phase)"""
    
    def test_validate_extensibility_method_exists(self):
        """Test TDDOrchestrator has validate_extensibility method"""
        orchestrator = TDDOrchestrator()
        assert hasattr(orchestrator, 'validate_extensibility')
    
    def test_validate_extensibility_detects_plugin_patterns(self):
        """Test validate_extensibility identifies plugin patterns"""
        orchestrator = TDDOrchestrator()
        
        result = orchestrator.validate_extensibility(
            module_path="cortex/orchestrators/core/tdd_orchestrator.py"
        )
        
        assert "has_plugin_pattern" in result
        assert "extensibility_score" in result
    
    def test_validate_extensibility_checks_abc_usage(self):
        """Test validate_extensibility checks for ABC (abstract base class) usage"""
        orchestrator = TDDOrchestrator()
        
        result = orchestrator.validate_extensibility(
            module_path="cortex/orchestrators/core/tdd_orchestrator.py"
        )
        
        assert "uses_abc" in result
    
    def test_validate_extensibility_checks_protocol_usage(self):
        """Test validate_extensibility checks for Protocol usage"""
        orchestrator = TDDOrchestrator()
        
        result = orchestrator.validate_extensibility(
            module_path="cortex/orchestrators/core/tdd_orchestrator.py"
        )
        
        assert "uses_protocol" in result


class TestEventBusIntegration:
    """Test EventBus notifications for cycle events (RED phase)"""
    
    def test_emit_cycle_complete_event(self):
        """Test orchestrator emits CYCLE_COMPLETE event"""
        orchestrator = TDDOrchestrator()
        
        # Mock EventBus
        with patch.object(orchestrator, '_emit_event') as mock_emit:
            criteria = SuccessCriteria(
                min_coverage=0.85,
                max_latency_ms=200,
                extensibility_required=False
            )
            
            orchestrator.execute_multi_cycle(
                test_suite="tests/unit/test_example.py",
                success_criteria=criteria,
                max_cycles=2
            )
            
            # Should emit CYCLE_COMPLETE for each cycle
            cycle_complete_calls = [
                c for c in mock_emit.call_args_list
                if c[0][0] == "CYCLE_COMPLETE"
            ]
            assert len(cycle_complete_calls) >= 1
    
    def test_emit_criteria_met_event(self):
        """Test orchestrator emits CRITERIA_MET event when success"""
        orchestrator = TDDOrchestrator()
        
        with patch.object(orchestrator, '_emit_event') as mock_emit:
            criteria = SuccessCriteria(
                min_coverage=0.75,  # Low threshold
                max_latency_ms=300,
                extensibility_required=False
            )
            
            orchestrator.execute_multi_cycle(
                test_suite="tests/unit/test_example.py",
                success_criteria=criteria,
                max_cycles=3
            )
            
            # Should emit CRITERIA_MET when threshold reached
            criteria_met_calls = [
                c for c in mock_emit.call_args_list
                if c[0][0] == "CRITERIA_MET"
            ]
            assert len(criteria_met_calls) == 1
    
    def test_emit_max_cycles_reached_event(self):
        """Test orchestrator emits MAX_CYCLES_REACHED when limit hit"""
        orchestrator = TDDOrchestrator()
        
        with patch.object(orchestrator, '_emit_event') as mock_emit:
            criteria = SuccessCriteria(
                min_coverage=0.99,  # Unreachable threshold
                max_latency_ms=50,
                extensibility_required=True
            )
            
            orchestrator.execute_multi_cycle(
                test_suite="tests/unit/test_example.py",
                success_criteria=criteria,
                max_cycles=3
            )
            
            # Should emit MAX_CYCLES_REACHED when limit hit without success
            max_cycles_calls = [
                c for c in mock_emit.call_args_list
                if c[0][0] == "MAX_CYCLES_REACHED"
            ]
            assert len(max_cycles_calls) == 1


class TestEnhancedHolisticGate:
    """Test enhanced holistic gate with quality validations (RED phase)"""
    
    def test_holistic_gate_integrates_coverage_validation(self):
        """Test holistic_refactor_gate calls validate_coverage"""
        orchestrator = TDDOrchestrator()
        
        with patch.object(orchestrator, 'validate_coverage') as mock_validate:
            mock_validate.return_value = {
                "coverage_percent": 0.89,
                "passes_threshold": True
            }
            
            criteria = SuccessCriteria(
                min_coverage=0.85,
                max_latency_ms=200,
                extensibility_required=False
            )
            metrics = CycleMetrics(
                cycle_number=1,
                tests_passed=20,
                tests_failed=0,
                coverage_percent=0.89,
                avg_latency_ms=150.0,
                extensibility_score=0.0
            )
            
            orchestrator.holistic_refactor_gate_enhanced(
                criteria=criteria,
                metrics=metrics,
                test_suite="tests/unit/test_example.py",
                module_path="cortex/example.py"
            )
            
            mock_validate.assert_called_once()
    
    def test_holistic_gate_integrates_latency_validation(self):
        """Test holistic_refactor_gate calls validate_latency"""
        orchestrator = TDDOrchestrator()
        
        with patch.object(orchestrator, 'validate_latency') as mock_validate:
            mock_validate.return_value = {
                "avg_latency_ms": 145.0,
                "slow_tests": []
            }
            
            criteria = SuccessCriteria(
                min_coverage=0.85,
                max_latency_ms=200,
                extensibility_required=False
            )
            metrics = CycleMetrics(
                cycle_number=1,
                tests_passed=20,
                tests_failed=0,
                coverage_percent=0.89,
                avg_latency_ms=145.0,
                extensibility_score=0.0
            )
            
            orchestrator.holistic_refactor_gate_enhanced(
                criteria=criteria,
                metrics=metrics,
                test_suite="tests/unit/test_example.py",
                module_path="cortex/example.py"
            )
            
            mock_validate.assert_called_once()
    
    def test_holistic_gate_integrates_extensibility_validation(self):
        """Test holistic_refactor_gate calls validate_extensibility when required"""
        orchestrator = TDDOrchestrator()
        
        with patch.object(orchestrator, 'validate_extensibility') as mock_validate:
            mock_validate.return_value = {
                "has_plugin_pattern": True,
                "extensibility_score": 0.9
            }
            
            criteria = SuccessCriteria(
                min_coverage=0.85,
                max_latency_ms=200,
                extensibility_required=True  # Required!
            )
            metrics = CycleMetrics(
                cycle_number=1,
                tests_passed=20,
                tests_failed=0,
                coverage_percent=0.89,
                avg_latency_ms=145.0,
                extensibility_score=0.9
            )
            
            orchestrator.holistic_refactor_gate_enhanced(
                criteria=criteria,
                metrics=metrics,
                test_suite="tests/unit/test_example.py",
                module_path="cortex/example.py"
            )
            
            mock_validate.assert_called_once()
