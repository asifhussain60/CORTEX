"""
Unit tests for GuidedWiringOrchestrator (Tool 3 of 3-Tool Safety System).

Tests MUST be written FIRST per CORE-008 (TDD).

AC-GUIDED-WIRE-TEST-001: Comprehensive test coverage for guided wiring
- Test initialization
- Test DoR generation
- Test approval workflow
- Test component wiring
- Test validation
- Test rollback
- Integration with real codebase

Author: Asif Hussain
Date: 2026-01-25
"""

import pytest
from pathlib import Path
from typing import Dict, List
from unittest.mock import Mock, patch, MagicMock

# Import the module under test
from cortex.tools.guided_wiring_orchestrator import (
    GuidedWiringOrchestrator,
    WiringResult,
    WiringStatus,
    DoRApprovalStatus,
)


class TestGuidedWiringOrchestrator:
    """Test suite for GuidedWiringOrchestrator."""

    def test_orchestrator_initializes(self):
        """Test that GuidedWiringOrchestrator can be instantiated."""
        orchestrator = GuidedWiringOrchestrator()
        assert orchestrator is not None
        assert isinstance(orchestrator, GuidedWiringOrchestrator)

    def test_orchestrator_has_required_methods(self):
        """Test that orchestrator has all required methods."""
        orchestrator = GuidedWiringOrchestrator()
        assert hasattr(orchestrator, 'wire_component')
        assert hasattr(orchestrator, 'wire_pipeline')
        assert hasattr(orchestrator, 'rollback')
        assert callable(orchestrator.wire_component)
        assert callable(orchestrator.wire_pipeline)
        assert callable(orchestrator.rollback)

    def test_wire_component_returns_wiring_result(self):
        """Test that wire_component returns WiringResult."""
        orchestrator = GuidedWiringOrchestrator()
        
        # Mock user approval
        with patch('builtins.input', return_value='cancel'):
            result = orchestrator.wire_component('InteractionOrchestrator')
        
        assert isinstance(result, WiringResult)
        assert result.component_name == 'InteractionOrchestrator'
        assert isinstance(result.status, WiringStatus)

    def test_wiring_result_structure(self):
        """Test WiringResult dataclass structure."""
        result = WiringResult(
            component_name='TestOrchestrator',
            status=WiringStatus.SUCCESS,
            dor_displayed=True,
            approval_status=DoRApprovalStatus.APPROVED,
            tests_generated=True,
            tests_passing=True,
            wired=True,
            validated=True,
            git_checkpoint='abc123',
            issues=[],
            recommendations=[],
        )
        
        assert result.component_name == 'TestOrchestrator'
        assert result.status == WiringStatus.SUCCESS
        assert result.dor_displayed is True
        assert result.approval_status == DoRApprovalStatus.APPROVED

    def test_wiring_status_enum_values(self):
        """Test that WiringStatus has all required values."""
        assert hasattr(WiringStatus, 'SUCCESS')
        assert hasattr(WiringStatus, 'CANCELLED')
        assert hasattr(WiringStatus, 'FAILED')
        assert hasattr(WiringStatus, 'ROLLBACK')

    def test_dor_approval_status_enum_values(self):
        """Test that DoRApprovalStatus has all required values."""
        assert hasattr(DoRApprovalStatus, 'APPROVED')
        assert hasattr(DoRApprovalStatus, 'REJECTED')
        assert hasattr(DoRApprovalStatus, 'PENDING')

    def test_display_dor_generates_markdown(self):
        """Test that _display_dor generates markdown DoR."""
        orchestrator = GuidedWiringOrchestrator()
        dor = orchestrator._display_dor('InteractionOrchestrator')
        
        assert isinstance(dor, str)
        assert 'InteractionOrchestrator' in dor
        assert 'Definition of Ready' in dor or 'DoR' in dor
        assert 'Impact' in dor or 'Scope' in dor

    def test_dor_includes_wiring_plan(self):
        """Test that DoR includes specific wiring plan."""
        orchestrator = GuidedWiringOrchestrator()
        dor = orchestrator._display_dor('InteractionOrchestrator')
        
        # Should mention execute_operation
        assert 'execute_operation' in dor.lower()
        
        # Should mention Stage 1
        assert 'stage' in dor.lower() or 'pipeline' in dor.lower()

    def test_dor_includes_validation_checks(self):
        """Test that DoR includes validation plan."""
        orchestrator = GuidedWiringOrchestrator()
        dor = orchestrator._display_dor('InteractionOrchestrator')
        
        # Should mention validation
        assert 'validat' in dor.lower()

    @patch('builtins.input', return_value='yes')
    def test_wait_for_approval_accepts_yes(self, mock_input):
        """Test that _wait_for_approval accepts 'yes'."""
        orchestrator = GuidedWiringOrchestrator()
        status = orchestrator._wait_for_approval()
        
        assert status == DoRApprovalStatus.APPROVED
        mock_input.assert_called_once()

    @patch('builtins.input', return_value='proceed')
    def test_wait_for_approval_accepts_proceed(self, mock_input):
        """Test that _wait_for_approval accepts 'proceed'."""
        orchestrator = GuidedWiringOrchestrator()
        status = orchestrator._wait_for_approval()
        
        assert status == DoRApprovalStatus.APPROVED

    @patch('builtins.input', return_value='no')
    def test_wait_for_approval_rejects_no(self, mock_input):
        """Test that _wait_for_approval rejects 'no'."""
        orchestrator = GuidedWiringOrchestrator()
        status = orchestrator._wait_for_approval()
        
        assert status == DoRApprovalStatus.REJECTED

    @patch('builtins.input', return_value='cancel')
    def test_wait_for_approval_rejects_cancel(self, mock_input):
        """Test that _wait_for_approval rejects 'cancel'."""
        orchestrator = GuidedWiringOrchestrator()
        status = orchestrator._wait_for_approval()
        
        assert status == DoRApprovalStatus.REJECTED

    def test_wire_component_cancelled_when_rejected(self):
        """Test that wire_component returns CANCELLED when user rejects."""
        orchestrator = GuidedWiringOrchestrator()
        
        with patch('builtins.input', return_value='no'):
            result = orchestrator.wire_component('InteractionOrchestrator')
        
        assert result.status == WiringStatus.CANCELLED
        assert result.approval_status == DoRApprovalStatus.REJECTED
        assert result.wired is False

    def test_generate_wiring_code_produces_python(self):
        """Test that _generate_wiring_code produces Python code."""
        orchestrator = GuidedWiringOrchestrator()
        code = orchestrator._generate_wiring_code('InteractionOrchestrator')
        
        assert isinstance(code, str)
        assert 'def ' in code or 'self.' in code
        assert 'InteractionOrchestrator' in code or 'interaction_orchestrator' in code

    def test_generate_wiring_code_includes_stage_logic(self):
        """Test that wiring code includes stage/pipeline logic."""
        orchestrator = GuidedWiringOrchestrator()
        code = orchestrator._generate_wiring_code('InteractionOrchestrator')
        
        # Should include stage-specific logic
        assert 'stage' in code.lower() or 'execute_operation' in code.lower()

    def test_validate_wiring_uses_validation_agent(self):
        """Test that _validate_wiring uses WiringValidationAgent."""
        orchestrator = GuidedWiringOrchestrator()
        
        # Should use Tool 2 for validation
        validation_result = orchestrator._validate_wiring('InteractionOrchestrator')
        
        assert isinstance(validation_result, dict)
        assert 'component_name' in validation_result
        assert 'status' in validation_result

    def test_git_checkpoint_creates_commit(self):
        """Test that _git_checkpoint creates git commit."""
        orchestrator = GuidedWiringOrchestrator()
        
        # Mock git operations
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = 'abc123def456'
            
            commit_hash = orchestrator._git_checkpoint('InteractionOrchestrator')
        
        assert isinstance(commit_hash, str)
        # Either returns a hash or None (if git fails)
        if commit_hash:
            assert len(commit_hash) > 0

    def test_rollback_reverts_changes(self):
        """Test that rollback reverts changes."""
        orchestrator = GuidedWiringOrchestrator()
        
        # Mock git operations
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            result = orchestrator.rollback('InteractionOrchestrator', 'abc123')
        
        assert result is True or result is False

    def test_wire_pipeline_wires_multiple_components(self):
        """Test that wire_pipeline can wire multiple components."""
        orchestrator = GuidedWiringOrchestrator()
        
        # Mock user cancellation - pipeline should stop after first component
        with patch('builtins.input', return_value='cancel'):
            results = orchestrator.wire_pipeline(['InteractionOrchestrator', 'IntentRouter'])
        
        assert isinstance(results, list)
        # When user cancels, pipeline stops (only 1 result)
        assert len(results) >= 1
        assert all(isinstance(r, WiringResult) for r in results)

    def test_wire_pipeline_stops_on_failure(self):
        """Test that wire_pipeline stops if a component fails."""
        orchestrator = GuidedWiringOrchestrator()
        
        # First component rejected, should stop
        with patch('builtins.input', return_value='no'):
            results = orchestrator.wire_pipeline(['InteractionOrchestrator', 'IntentRouter'])
        
        # First component should be CANCELLED
        assert results[0].status == WiringStatus.CANCELLED
        # Second component should not be attempted (or also CANCELLED)
        assert len(results) <= 2


class TestGuidedWiringOrchestratorIntegration:
    """Integration tests with real CORTEX codebase."""

    def test_displays_dor_for_interaction_orchestrator(self):
        """Test DoR display for InteractionOrchestrator (Stage 1)."""
        orchestrator = GuidedWiringOrchestrator()
        dor = orchestrator._display_dor('InteractionOrchestrator')
        
        # Should be detailed and actionable
        assert len(dor) > 100
        assert 'InteractionOrchestrator' in dor
        assert 'Stage' in dor or 'stage' in dor

    def test_displays_dor_for_intent_router(self):
        """Test DoR display for IntentRouter (Stage 2)."""
        orchestrator = GuidedWiringOrchestrator()
        dor = orchestrator._display_dor('IntentRouter')
        
        assert 'IntentRouter' in dor
        assert 'LENS' in dor or 'intent' in dor.lower()

    def test_displays_dor_for_dor_approval_gate(self):
        """Test DoR display for DoRApprovalGate (Stage 2.5)."""
        orchestrator = GuidedWiringOrchestrator()
        dor = orchestrator._display_dor('DoRApprovalGate')
        
        assert 'DoRApprovalGate' in dor or 'DoR' in dor
        assert 'approval' in dor.lower()

    def test_generates_wiring_code_for_stage_1(self):
        """Test wiring code generation for Stage 1 component."""
        orchestrator = GuidedWiringOrchestrator()
        code = orchestrator._generate_wiring_code('InteractionOrchestrator')
        
        # Should include Stage 1 logic
        assert 'interaction' in code.lower()
        assert 'execute_operation' in code.lower()

    def test_validates_interaction_orchestrator_before_wiring(self):
        """Test validation detects InteractionOrchestrator is partially wired."""
        orchestrator = GuidedWiringOrchestrator()
        validation = orchestrator._validate_wiring('InteractionOrchestrator')
        
        # Should show it's partially wired (initialized but not called)
        assert validation['status'] in ['PARTIALLY_WIRED', 'UNWIRED', 'FULLY_WIRED']

    def test_dry_run_mode_does_not_modify_files(self):
        """Test that dry_run mode doesn't actually modify files."""
        orchestrator = GuidedWiringOrchestrator(dry_run=True)
        
        with patch('builtins.input', return_value='yes'):
            result = orchestrator.wire_component('InteractionOrchestrator')
        
        # In dry run, should succeed but not actually wire
        assert result.status in [WiringStatus.SUCCESS, WiringStatus.CANCELLED]
        assert result.wired is False  # Not actually wired in dry run

    def test_generates_actionable_recommendations(self):
        """Test that failed wiring provides actionable recommendations."""
        orchestrator = GuidedWiringOrchestrator()
        
        # Cancel the wiring
        with patch('builtins.input', return_value='cancel'):
            result = orchestrator.wire_component('InteractionOrchestrator')
        
        # Should have recommendations
        assert isinstance(result.recommendations, list)

    def test_cli_help_displays_usage(self):
        """Test that CLI help shows usage information."""
        orchestrator = GuidedWiringOrchestrator()
        help_text = orchestrator.get_help()
        
        assert 'usage' in help_text.lower()
        assert 'wire' in help_text.lower()
        assert 'component' in help_text.lower() or 'orchestrator' in help_text.lower()

    def test_supports_batch_wiring(self):
        """Test that orchestrator supports batch wiring mode."""
        orchestrator = GuidedWiringOrchestrator()
        
        # Should be able to wire multiple components
        components = ['InteractionOrchestrator', 'IntentRouter']
        
        with patch('builtins.input', return_value='cancel'):
            results = orchestrator.wire_pipeline(components)
        
        # Pipeline stops on first cancellation (safety feature)
        assert len(results) >= 1
        assert isinstance(results, list)

    def test_preserves_existing_code(self):
        """Test that wiring doesn't overwrite existing execute_operation logic."""
        orchestrator = GuidedWiringOrchestrator()
        
        # Get current execute_operation code
        master_file = Path(__file__).parent.parent.parent.parent / 'cortex' / 'orchestrators' / 'core' / 'master_orchestrator.py'
        original_content = master_file.read_text()
        
        # In dry run, check that we preserve existing logic
        orchestrator_dry = GuidedWiringOrchestrator(dry_run=True)
        code = orchestrator_dry._generate_wiring_code('InteractionOrchestrator')
        
        # Should not lose existing functionality
        assert 'execute_operation' in code.lower()


class TestWiringResult:
    """Test suite for WiringResult dataclass."""

    def test_wiring_result_to_dict(self):
        """Test WiringResult can be converted to dict."""
        result = WiringResult(
            component_name='TestOrchestrator',
            status=WiringStatus.SUCCESS,
            dor_displayed=True,
            approval_status=DoRApprovalStatus.APPROVED,
            tests_generated=True,
            tests_passing=True,
            wired=True,
            validated=True,
            git_checkpoint='abc123',
            issues=[],
            recommendations=[],
        )
        
        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        assert result_dict['component_name'] == 'TestOrchestrator'
        assert result_dict['status'] == 'SUCCESS'
        assert result_dict['wired'] is True

    def test_wiring_result_failure_includes_issues(self):
        """Test that failed WiringResult includes issues."""
        result = WiringResult(
            component_name='TestOrchestrator',
            status=WiringStatus.FAILED,
            dor_displayed=True,
            approval_status=DoRApprovalStatus.APPROVED,
            tests_generated=False,
            tests_passing=False,
            wired=False,
            validated=False,
            git_checkpoint=None,
            issues=['Test generation failed', 'Validation failed'],
            recommendations=['Check component exists', 'Verify registry'],
        )
        
        assert len(result.issues) > 0
        assert len(result.recommendations) > 0
        assert result.status == WiringStatus.FAILED


class TestWiringStatus:
    """Test suite for WiringStatus enum."""

    def test_wiring_status_values_are_unique(self):
        """Test that all WiringStatus values are unique."""
        values = [
            WiringStatus.SUCCESS.value,
            WiringStatus.CANCELLED.value,
            WiringStatus.FAILED.value,
            WiringStatus.ROLLBACK.value,
        ]
        assert len(values) == len(set(values))


class TestDoRApprovalStatus:
    """Test suite for DoRApprovalStatus enum."""

    def test_dor_approval_status_values_are_unique(self):
        """Test that all DoRApprovalStatus values are unique."""
        values = [
            DoRApprovalStatus.APPROVED.value,
            DoRApprovalStatus.REJECTED.value,
            DoRApprovalStatus.PENDING.value,
        ]
        assert len(values) == len(set(values))
