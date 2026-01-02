"""
Test Suite: ADO Orchestrator v2 Foundation

Tests for ADOOrchestratorV2 base class, phase structure, and BaseOrchestratorV4_1
inheritance. Validates pure autonomous architecture with database state tracking.

Author: Asif Hussain
Copyright: © 2026 Asif Hussain. All rights reserved.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from src.orchestrators.ado.v2.ado_orchestrator_v2 import (
    ADOOrchestratorV2,
    ADOPhaseV2,
    ADOResultV2
)
from src.database.planning_state_db import PlanningStateDB


class TestADOOrchestratorV2Foundation:
    """Test suite for ADO Orchestrator v2 foundation."""
    
    @pytest.fixture
    def mock_state_db(self):
        """Create mock PlanningStateDB."""
        db = Mock(spec=PlanningStateDB)
        db.create_plan.return_value = "test-plan-id-123"
        db.start_phase.return_value = "test-phase-id-456"
        db.complete_phase.return_value = None
        db.complete_plan.return_value = None
        db.fail_plan.return_value = None
        return db
    
    @pytest.fixture
    def mock_config(self):
        """Return path to real ADO v2 config file."""
        return "cortex-brain/manifests/orchestrators/ado-v2-config.yaml"
    
    def test_orchestrator_v2_inherits_base_v4_1(self, mock_state_db, mock_config):
        """Test: ADO Orchestrator v2 inherits BaseOrchestratorV4_1."""
        from src.orchestrators.base.base_orchestrator_v4_1 import BaseOrchestratorV4_1
        
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        assert isinstance(orchestrator, BaseOrchestratorV4_1)
        assert hasattr(orchestrator, 'execute')
        assert hasattr(orchestrator, 'config')
        assert hasattr(orchestrator, 'state_db')
    
    def test_orchestrator_v2_has_all_phases(self):
        """Test: ADO Orchestrator v2 has all 6 phases defined."""
        assert hasattr(ADOPhaseV2, 'DISCOVERY')
        assert hasattr(ADOPhaseV2, 'VALIDATION')
        assert hasattr(ADOPhaseV2, 'GENERATION')
        assert hasattr(ADOPhaseV2, 'APPROVAL')
        assert hasattr(ADOPhaseV2, 'EXECUTION')
        assert hasattr(ADOPhaseV2, 'COMPLETION')
        
        assert ADOPhaseV2.DISCOVERY.value == "discovery"
        assert ADOPhaseV2.VALIDATION.value == "validation"
        assert ADOPhaseV2.GENERATION.value == "generation"
        assert ADOPhaseV2.APPROVAL.value == "approval"
        assert ADOPhaseV2.EXECUTION.value == "execution"
        assert ADOPhaseV2.COMPLETION.value == "completion"
    
    def test_execute_method_exists(self, mock_state_db, mock_config):
        """Test: Orchestrator v2 has execute() method."""
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        assert hasattr(orchestrator, 'execute')
        assert callable(orchestrator.execute)
    
    def test_execute_requires_feature_parameter(self, mock_state_db, mock_config):
        """Test: execute() requires 'feature' parameter."""
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        result = orchestrator.execute()
        assert result.success is False
        assert result.status == "error"
        assert "feature" in result.message.lower()
    
    def test_execute_returns_ado_result_v2(self, mock_state_db, mock_config):
        """Test: execute() returns ADOResultV2 object."""
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        result = orchestrator.execute(feature="Test Feature", test_mode=True)
        
        assert isinstance(result, ADOResultV2)
        assert hasattr(result, 'status')
        assert hasattr(result, 'success')
        assert hasattr(result, 'phase')
        assert hasattr(result, 'plan_id')
    
    def test_auto_mode_creates_database_plan(self, mock_state_db, mock_config):
        """Test: Auto mode creates plan in database."""
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        result = orchestrator.execute(
            feature="Test Feature",
            mode="auto",
            test_mode=True
        )
        
        mock_state_db.create_plan.assert_called_once()
        call_args = mock_state_db.create_plan.call_args
        assert call_args[1]['feature_name'] == "Test Feature"
        assert call_args[1]['metadata']['orchestrator'] == 'ado_v2'
        assert call_args[1]['metadata']['mode'] == 'auto'
    
    def test_phases_tracked_in_database(self, mock_state_db, mock_config):
        """Test: All phases create database phase records."""
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        result = orchestrator.execute(
            feature="Test Feature",
            mode="auto",
            test_mode=True,
            auto_approve=True
        )
        
        # Should create 6 phase records (all phases in auto mode)
        # DISCOVERY, VALIDATION, GENERATION, APPROVAL (skipped), EXECUTION (skipped), COMPLETION
        assert mock_state_db.start_phase.call_count >= 4  # At minimum these phases
    
    def test_plan_completed_on_success(self, mock_state_db, mock_config):
        """Test: Plan marked complete on successful execution."""
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        result = orchestrator.execute(
            feature="Test Feature",
            test_mode=True,
            auto_approve=True
        )
        
        assert result.success is True
        mock_state_db.complete_plan.assert_called_once_with("test-plan-id-123")
    
    def test_plan_failed_on_exception(self, mock_state_db, mock_config):
        """Test: Plan marked failed on exception."""
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        # Make state_db raise exception
        mock_state_db.start_phase.side_effect = Exception("Database error")
        
        result = orchestrator.execute(
            feature="Test Feature",
            test_mode=True
        )
        
        assert result.success is False
        assert result.status == "error"
        mock_state_db.fail_plan.assert_called_once()
    
    def test_dual_mode_support(self, mock_state_db, mock_config):
        """Test: Orchestrator supports both auto and wizard modes."""
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        # Auto mode
        result_auto = orchestrator.execute(
            feature="Test Feature",
            mode="auto",
            test_mode=True
        )
        assert result_auto is not None
        
        # Wizard mode (may fallback to auto for now)
        result_wizard = orchestrator.execute(
            feature="Test Feature",
            mode="wizard",
            test_mode=True
        )
        assert result_wizard is not None
    
    def test_phase_transitions_logged(self, mock_state_db, mock_config):
        """Test: Phase transitions appear in logs."""
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        result = orchestrator.execute(
            feature="Test Feature",
            test_mode=True,
            auto_approve=True
        )
        
        # Check logs contain phase transitions
        log_text = "\n".join(result.logs)
        assert "Phase transition:" in log_text or "🎭" in log_text
    
    def test_result_contains_plan_id(self, mock_state_db, mock_config):
        """Test: Result contains database plan ID."""
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        result = orchestrator.execute(
            feature="Test Feature",
            test_mode=True
        )
        
        assert result.plan_id == "test-plan-id-123"
    
    def test_config_loading(self, mock_state_db, mock_config):
        """Test: Orchestrator loads config correctly."""
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        assert hasattr(orchestrator, 'ado_config')
        assert hasattr(orchestrator, 'work_item_types')
        assert hasattr(orchestrator, 'complexity_thresholds')


class TestADOOrchestratorV2Phases:
    """Test suite for individual phase execution."""
    
    @pytest.fixture
    def mock_state_db(self):
        """Create mock PlanningStateDB."""
        db = Mock(spec=PlanningStateDB)
        db.create_plan.return_value = "test-plan-id"
        db.start_phase.return_value = "test-phase-id"
        db.complete_phase.return_value = None
        db.complete_plan.return_value = None
        return db
    
    @pytest.fixture
    def mock_config(self):
        """Return path to real ADO v2 config file."""
        return "cortex-brain/manifests/orchestrators/ado-v2-config.yaml"
    
    def test_discovery_phase_executes(self, mock_state_db, mock_config):
        """Test: DISCOVERY phase executes and classifies complexity."""
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        result = orchestrator.execute(
            feature="Test Feature",
            test_mode=True,
            auto_approve=True
        )
        
        assert result.success is True
        assert 'discovery' in result.data
        assert 'complexity' in result.data['discovery']
    
    def test_validation_phase_collects_dor(self, mock_state_db, mock_config):
        """Test: VALIDATION phase collects DoR data."""
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        result = orchestrator.execute(
            feature="Test Feature",
            acceptance_criteria=["AC 1", "AC 2"],
            assumptions=["Assumption 1"],
            constraints=["Constraint 1"],
            test_mode=True,
            auto_approve=True
        )
        
        assert result.success is True
        assert 'validation' in result.data
        validation = result.data['validation']
        assert len(validation['acceptance_criteria']) == 2
        assert len(validation['assumptions']) == 1
        assert len(validation['constraints']) == 1
    
    def test_generation_phase_placeholder(self, mock_state_db, mock_config):
        """Test: GENERATION phase exists (placeholder for now)."""
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        result = orchestrator.execute(
            feature="Test Feature",
            test_mode=True,
            auto_approve=True
        )
        
        assert result.success is True
        assert 'generation' in result.data
    
    def test_approval_phase_skipped_when_auto_approve(self, mock_state_db, mock_config):
        """Test: APPROVAL phase skipped when auto_approve=True."""
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        result = orchestrator.execute(
            feature="Test Feature",
            test_mode=True,
            auto_approve=True
        )
        
        log_text = "\n".join(result.logs)
        assert "Approval phase skipped" in log_text or "auto_approve" in log_text
    
    def test_execution_phase_skipped_in_test_mode(self, mock_state_db, mock_config):
        """Test: EXECUTION phase skipped when test_mode=True."""
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        result = orchestrator.execute(
            feature="Test Feature",
            test_mode=True,
            auto_approve=True
        )
        
        log_text = "\n".join(result.logs)
        assert "Execution phase skipped" in log_text or "test_mode" in log_text
        assert result.items_created == 0
    
    def test_completion_phase_generates_message(self, mock_state_db, mock_config):
        """Test: COMPLETION phase generates success message."""
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        result = orchestrator.execute(
            feature="Test Feature",
            test_mode=True,
            auto_approve=True
        )
        
        assert result.success is True
        assert result.phase == ADOPhaseV2.COMPLETION
        assert result.message is not None
        assert "Test Feature" in result.message


class TestADOOrchestratorV2ErrorHandling:
    """Test suite for error handling and graceful degradation."""
    
    @pytest.fixture
    def mock_state_db(self):
        """Create mock PlanningStateDB."""
        db = Mock(spec=PlanningStateDB)
        db.create_plan.return_value = "test-plan-id"
        db.start_phase.return_value = "test-phase-id"
        db.complete_phase.return_value = None
        db.fail_plan.return_value = None
        return db
    
    @pytest.fixture
    def mock_config(self):
        """Return path to real ADO v2 config file."""
        return "cortex-brain/manifests/orchestrators/ado-v2-config.yaml"
    
    def test_missing_feature_parameter_raises_error(self, mock_state_db, mock_config):
        """Test: Missing feature parameter returns error result."""
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        result = orchestrator.execute(test_mode=True)
        assert result.success is False
        assert result.status == "error"
        assert "feature" in result.message.lower()
    
    def test_database_error_returns_error_result(self, mock_state_db, mock_config):
        """Test: Database errors return error result."""
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        mock_state_db.create_plan.side_effect = Exception("Database connection failed")
        
        result = orchestrator.execute(
            feature="Test Feature",
            test_mode=True
        )
        
        assert result.success is False
        assert result.status == "error"
        assert len(result.errors) > 0
    
    def test_graceful_degradation_review_orchestrator(self, mock_state_db, mock_config):
        """Test: Review orchestrator failure doesn't stop execution."""
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        # Review orchestrator will fail (not implemented)
        result = orchestrator.execute(
            feature="Test Feature",
            test_mode=True,
            auto_approve=True
        )
        
        # Should still succeed
        assert result.success is True
        # Should have warning about review orchestrator
        warning_text = "\n".join(result.warnings)
        assert "review" in warning_text.lower() or len(result.warnings) > 0
    
    def test_graceful_degradation_duplicate_detection(self, mock_state_db, mock_config):
        """Test: Duplicate detection failure doesn't stop execution."""
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        # Duplicate detection will fail (not implemented)
        result = orchestrator.execute(
            feature="Test Feature",
            test_mode=True,
            auto_approve=True
        )
        
        # Should still succeed
        assert result.success is True
        # Should have warning about duplicate detection or succeed silently
        assert result.phase == ADOPhaseV2.COMPLETION
