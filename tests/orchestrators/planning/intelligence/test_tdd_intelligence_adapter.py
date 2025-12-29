"""
Tests for TDDIntelligenceAdapter

Validates TDD workflow enforcement, phase transitions, and strategy generation.

Week 9 Day 1: 7 comprehensive tests
"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta

from src.orchestrators.planning.intelligence.tdd_intelligence_adapter import (
    TDDIntelligenceAdapter,
    TDDPhase,
    TDDPhaseStatus,
    TDDWorkflowValidation,
    TDDStrategy
)


class TestTDDIntelligenceAdapterInit:
    """Test adapter initialization."""
    
    def test_init_default(self, tmp_path):
        """Test default initialization."""
        adapter = TDDIntelligenceAdapter(tmp_path)
        
        assert adapter.project_root == tmp_path
        assert adapter.enforce_strict is True
        assert adapter._current_workflow is None
        assert adapter._phase_history == []
    
    def test_init_non_strict(self, tmp_path):
        """Test initialization with non-strict mode."""
        adapter = TDDIntelligenceAdapter(tmp_path, enforce_strict=False)
        
        assert adapter.enforce_strict is False


class TestREDPhaseValidation:
    """Test RED phase validation."""
    
    def test_red_phase_valid(self, tmp_path):
        """Test valid RED phase (all tests failing)."""
        context = {
            "test_files": ["tests/test_feature.py"],
            "test_results": {
                "total": 5,
                "passed": 0,
                "failed": 5
            }
        }
        
        adapter = TDDIntelligenceAdapter(tmp_path)
        status = adapter._validate_red_phase(context)
        
        assert status.phase == TDDPhase.RED
        assert status.dor_passed is True
        assert status.dod_passed is True
        assert status.status == "complete"
        assert status.tests_written == 5
        assert status.tests_failing == 5
    
    def test_red_phase_invalid_passing_tests(self, tmp_path):
        """Test invalid RED phase (some tests passing)."""
        context = {
            "test_files": ["tests/test_feature.py"],
            "test_results": {
                "total": 5,
                "passed": 2,
                "failed": 3
            }
        }
        
        adapter = TDDIntelligenceAdapter(tmp_path)
        status = adapter._validate_red_phase(context)
        
        assert status.dod_passed is False
        assert "RED phase violation" in status.validation_errors[0]


class TestGREENPhaseValidation:
    """Test GREEN phase validation."""
    
    def test_green_phase_valid(self, tmp_path):
        """Test valid GREEN phase (all tests passing)."""
        context = {
            "implementation_files": ["src/feature.py"],
            "test_results": {
                "total": 5,
                "passed": 5,
                "failed": 0
            }
        }
        
        adapter = TDDIntelligenceAdapter(tmp_path)
        status = adapter._validate_green_phase(context)
        
        assert status.phase == TDDPhase.GREEN
        assert status.dod_passed is True
        assert status.status == "complete"
        assert status.tests_passing == 5
    
    def test_green_phase_incomplete(self, tmp_path):
        """Test incomplete GREEN phase (tests still failing)."""
        context = {
            "implementation_files": ["src/feature.py"],
            "test_results": {
                "total": 5,
                "passed": 3,
                "failed": 2
            }
        }
        
        adapter = TDDIntelligenceAdapter(tmp_path)
        status = adapter._validate_green_phase(context)
        
        assert status.dod_passed is False
        assert "still failing" in status.validation_errors[0]


class TestREFACTORPhaseValidation:
    """Test REFACTOR phase validation."""
    
    def test_refactor_phase_valid(self, tmp_path):
        """Test valid REFACTOR phase (tests passing, low complexity)."""
        context = {
            "test_results": {
                "total": 5,
                "passed": 5,
                "failed": 0
            },
            "code_quality": {
                "complexity": 10
            }
        }
        
        adapter = TDDIntelligenceAdapter(tmp_path)
        status = adapter._validate_refactor_phase(context)
        
        assert status.phase == TDDPhase.REFACTOR
        assert status.dor_passed is True
        assert status.dod_passed is True
        assert status.status == "complete"
    
    def test_refactor_phase_high_complexity(self, tmp_path):
        """Test REFACTOR phase with high complexity."""
        context = {
            "test_results": {
                "total": 5,
                "passed": 5,
                "failed": 0
            },
            "code_quality": {
                "complexity": 25
            }
        }
        
        adapter = TDDIntelligenceAdapter(tmp_path)
        status = adapter._validate_refactor_phase(context)
        
        assert status.dod_passed is False
        assert "Complexity" in status.validation_errors[0]


class TestPhaseTransitions:
    """Test phase transition logic."""
    
    def test_can_transition_red_to_green_valid(self, tmp_path):
        """Test valid transition from RED to GREEN."""
        current_status = TDDPhaseStatus(
            phase=TDDPhase.RED,
            status="complete",
            tests_written=5,
            tests_passing=0,
            tests_failing=5,
            dor_passed=True,
            dod_passed=True
        )
        
        adapter = TDDIntelligenceAdapter(tmp_path)
        can_transition, issues = adapter.can_transition_to_phase(TDDPhase.GREEN, current_status)
        
        assert can_transition is True
        assert len(issues) == 0
    
    def test_can_transition_red_to_green_invalid(self, tmp_path):
        """Test invalid transition from RED to GREEN (tests passing)."""
        current_status = TDDPhaseStatus(
            phase=TDDPhase.RED,
            status="in_progress",
            tests_written=5,
            tests_passing=2,  # VIOLATION: Should be 0
            tests_failing=3,
            dor_passed=True,
            dod_passed=False
        )
        
        adapter = TDDIntelligenceAdapter(tmp_path)
        can_transition, issues = adapter.can_transition_to_phase(TDDPhase.GREEN, current_status)
        
        assert can_transition is False
        assert len(issues) > 0
        assert any("already passing" in issue for issue in issues)
    
    def test_can_transition_green_to_refactor_valid(self, tmp_path):
        """Test valid transition from GREEN to REFACTOR."""
        current_status = TDDPhaseStatus(
            phase=TDDPhase.GREEN,
            status="complete",
            tests_written=5,
            tests_passing=5,
            tests_failing=0,
            dor_passed=True,
            dod_passed=True
        )
        
        adapter = TDDIntelligenceAdapter(tmp_path)
        can_transition, issues = adapter.can_transition_to_phase(TDDPhase.REFACTOR, current_status)
        
        assert can_transition is True
        assert len(issues) == 0


class TestWorkflowValidation:
    """Test complete workflow validation."""
    
    def test_validate_tdd_workflow_complete(self, tmp_path):
        """Test validation of complete TDD workflow."""
        feature_context = {
            "test_files": ["tests/test_feature.py"],
            "implementation_files": ["src/feature.py"],
            "test_results": {
                "total": 5,
                "passed": 5,
                "failed": 0
            },
            "code_quality": {
                "complexity": 10
            }
        }
        
        adapter = TDDIntelligenceAdapter(tmp_path)
        validation = adapter.validate_tdd_workflow(feature_context, current_phase=TDDPhase.REFACTOR)
        
        assert isinstance(validation, TDDWorkflowValidation)
        assert validation.current_phase == TDDPhase.REFACTOR
        assert validation.quality_score > 0
    
    def test_validate_tdd_workflow_with_violations(self, tmp_path):
        """Test validation with TDD violations."""
        feature_context = {
            "test_files": ["tests/test_feature.py"],
            "implementation_files": [],  # No implementation yet
            "test_results": {
                "total": 5,
                "passed": 3,  # VIOLATION: Some tests passing in RED
                "failed": 2
            }
        }
        
        adapter = TDDIntelligenceAdapter(tmp_path)
        validation = adapter.validate_tdd_workflow(feature_context)
        
        assert validation.is_valid is False
        assert len(validation.violations) > 0
        assert len(validation.recommendations) > 0


class TestStrategyGeneration:
    """Test TDD strategy generation."""
    
    def test_generate_tdd_strategy_simple(self, tmp_path):
        """Test TDD strategy for simple feature."""
        feature_scope = {
            "files_affected": ["src/models/user.py"],
            "complexity": "low"
        }
        
        adapter = TDDIntelligenceAdapter(tmp_path)
        strategy = adapter.generate_tdd_strategy(feature_scope, complexity="low")
        
        assert isinstance(strategy, TDDStrategy)
        assert strategy.estimated_cycles > 0
        assert strategy.estimated_duration_minutes > 0
        assert len(strategy.implementation_order) > 0
    
    def test_generate_tdd_strategy_api_changes(self, tmp_path):
        """Test TDD strategy for API changes."""
        feature_scope = {
            "files_affected": [
                "src/api/user_endpoint.py",
                "src/models/user.py"
            ]
        }
        
        adapter = TDDIntelligenceAdapter(tmp_path)
        strategy = adapter.generate_tdd_strategy(feature_scope, complexity="medium")
        
        assert strategy.recommended is True
        assert any("API" in reason for reason in strategy.reasoning)
        assert len(strategy.test_first_modules) > 0
        
        # Verify implementation order (models before API)
        assert "user.py" in strategy.implementation_order[0]
