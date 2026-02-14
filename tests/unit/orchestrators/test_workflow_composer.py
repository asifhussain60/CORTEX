"""
Tests for WorkflowComposer — Phase 84 Stage 1.

Motor neuron that sequences workflow steps dynamically from YAML templates.
Part of CORTEX brain metaphor: WorkflowComposer = motor neuron that executes
actions based on higher-level commands.

AC_START: AC-P84-S1-T1-001
Phase: 84 | Stage: 1 | Priority: P0
Description: TDD RED phase for WorkflowComposer
Requirements: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import pytest
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch, mock_open


# =============================================================================
# Import targets (expected to fail in RED phase)
# =============================================================================
try:
    from cortex.orchestrators.workflow.workflow_composer import (
        WorkflowComposer,
        WorkflowStep,
        WorkflowExecutionResult,
    )
except ImportError:
    WorkflowComposer = None
    WorkflowStep = None
    WorkflowExecutionResult = None


# =============================================================================
# WORKFLOW STEP DATACLASS TESTS
# =============================================================================
class TestWorkflowStep:
    """Test WorkflowStep dataclass structure."""

    @pytest.mark.skipif(WorkflowStep is None, reason="WorkflowStep not yet implemented")
    def test_workflow_step_has_required_fields(self):
        """WorkflowStep has step_id, orchestrator_name, parameters."""
        step = WorkflowStep(
            step_id="scan",
            orchestrator_name="LENSOrchestrator",
            parameters={"target": "src/"},
        )
        assert step.step_id == "scan"
        assert step.orchestrator_name == "LENSOrchestrator"
        assert step.parameters == {"target": "src/"}

    @pytest.mark.skipif(WorkflowStep is None, reason="WorkflowStep not yet implemented")
    def test_workflow_step_optional_description(self):
        """WorkflowStep has optional description field."""
        step = WorkflowStep(
            step_id="fix",
            orchestrator_name="TDDOrchestrator",
            parameters={},
            description="Apply security fixes",
        )
        assert step.description == "Apply security fixes"


# =============================================================================
# WORKFLOW COMPOSER INIT TESTS
# =============================================================================
class TestWorkflowComposerInit:
    """Test WorkflowComposer initialization."""

    @pytest.mark.skipif(WorkflowComposer is None, reason="WorkflowComposer not yet implemented")
    def test_workflow_composer_loads_template(self):
        """AC-P84-S1-T1-001: WorkflowComposer.__init__ loads YAML template from path."""
        template_content = """workflow:
  name: Test Workflow
  steps:
    - step_id: scan
      orchestrator: LENSOrchestrator
      parameters:
        target: src/
"""
        template_path = Path("workflows/test-workflow.yaml")
        
        with patch.object(Path, "exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=template_content)):
            
            composer = WorkflowComposer(template_path=template_path)
            assert composer is not None
            assert composer.workflow_name == "Test Workflow"

    @pytest.mark.skipif(WorkflowComposer is None, reason="WorkflowComposer not yet implemented")
    def test_workflow_composer_handles_missing_template(self):
        """WorkflowComposer raises FileNotFoundError for missing template."""
        template_path = Path("workflows/nonexistent.yaml")
        
        with pytest.raises(FileNotFoundError):
            WorkflowComposer(template_path=template_path)

    @pytest.mark.skipif(WorkflowComposer is None, reason="WorkflowComposer not yet implemented")
    def test_workflow_composer_handles_invalid_yaml(self):
        """WorkflowComposer raises ValueError for invalid YAML syntax."""
        template_path = Path("workflows/invalid.yaml")
        
        with patch.object(Path, "exists", return_value=True), \
             patch("builtins.open", mock_open(read_data="invalid: yaml: syntax:")):
            
            with pytest.raises(ValueError):
                WorkflowComposer(template_path=template_path)


# =============================================================================
# WORKFLOW COMPOSER compose() TESTS
# =============================================================================
class TestWorkflowComposerCompose:
    """Test WorkflowComposer.compose() method."""

    @pytest.mark.skipif(WorkflowComposer is None, reason="WorkflowComposer not yet implemented")
    def test_compose_returns_step_list(self):
        """AC-P84-S1-T1-002: compose() returns list of WorkflowStep objects."""
        template_content = """workflow:
  name: Test Workflow
  steps:
    - step_id: scan
      orchestrator: LENSOrchestrator
      parameters:
        target: src/
    - step_id: fix
      orchestrator: TDDOrchestrator
      parameters:
        mode: auto
"""
        template_path = Path("workflows/test-workflow.yaml")
        
        with patch.object(Path, "exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=template_content)):
            composer = WorkflowComposer(template_path=template_path)
            steps = composer.compose()
            
            assert len(steps) == 2
            assert all(isinstance(step, WorkflowStep) for step in steps)
            assert steps[0].step_id == "scan"
            assert steps[1].step_id == "fix"

    @pytest.mark.skipif(WorkflowComposer is None, reason="WorkflowComposer not yet implemented")
    def test_compose_preserves_step_order(self):
        """compose() returns steps in template order."""
        template_content = """workflow:
  name: Ordered Workflow
  steps:
    - step_id: first
      orchestrator: OrchestratorA
      parameters: {}
    - step_id: second
      orchestrator: OrchestratorB
      parameters: {}
    - step_id: third
      orchestrator: OrchestratorC
      parameters: {}
"""
        template_path = Path("workflows/ordered.yaml")
        
        with patch.object(Path, "exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=template_content)):
            composer = WorkflowComposer(template_path=template_path)
            steps = composer.compose()
            
            assert [s.step_id for s in steps] == ["first", "second", "third"]


# =============================================================================
# WORKFLOW COMPOSER execute() TESTS
# =============================================================================
class TestWorkflowComposerExecute:
    """Test WorkflowComposer.execute() method."""

    @pytest.mark.skipif(WorkflowComposer is None, reason="WorkflowComposer not yet implemented")
    def test_execute_runs_steps_sequentially(self):
        """AC-P84-S1-T1-003: execute() calls orchestrators in template order."""
        template_content = """workflow:
  name: Test
  steps:
    - step_id: step1
      orchestrator: OrchestratorA
      parameters: {}
"""
        template_path = Path("workflows/test.yaml")
        
        with patch.object(Path, "exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=template_content)):
            composer = WorkflowComposer(template_path=template_path)
            
            # Mock orchestrator registry
            mock_orch_a = MagicMock()
            mock_orch_a.execute.return_value = {"success": True}
            
            with patch.object(composer, "_get_orchestrator", return_value=mock_orch_a):
                result = composer.execute()
                
                assert result.success is True
                mock_orch_a.execute.assert_called_once()

    @pytest.mark.skipif(WorkflowComposer is None, reason="WorkflowComposer not yet implemented")
    def test_missing_orchestrator_handled(self):
        """AC-P84-S1-T1-004: execute() logs warning if orchestrator not found."""
        template_content = """workflow:
  name: Missing Orchestrator Test
  steps:
    - step_id: invalid
      orchestrator: NonExistentOrchestrator
      parameters: {}
"""
        template_path = Path("workflows/missing-orch.yaml")
        
        with patch.object(Path, "exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=template_content)):
            composer = WorkflowComposer(template_path=template_path)
            
            with patch.object(composer, "_get_orchestrator", return_value=None):
                result = composer.execute()
                
                # Should complete but log warning
                assert result.success is False
                assert "NonExistentOrchestrator" in result.error_message

    @pytest.mark.skipif(WorkflowComposer is None, reason="WorkflowComposer not yet implemented")
    def test_workflow_composed_event_emitted(self):
        """AC-P84-S1-T1-005: WORKFLOW_COMPOSED event fired with step_count."""
        template_content = """workflow:
  name: Event Test
  steps:
    - step_id: step1
      orchestrator: OrchestratorA
      parameters: {}
    - step_id: step2
      orchestrator: OrchestratorB
      parameters: {}
"""
        template_path = Path("workflows/event-test.yaml")
        
        with patch.object(Path, "exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=template_content)):
            composer = WorkflowComposer(template_path=template_path)
            
            emitted_events = []
            
            def capture_event(event_name: str, data: Dict[str, Any]) -> None:
                emitted_events.append((event_name, data))
            
            composer._emit_event = capture_event
            
            mock_orch = MagicMock()
            mock_orch.execute.return_value = {"success": True}
            
            with patch.object(composer, "_get_orchestrator", return_value=mock_orch):
                composer.execute()
                
                # Check WORKFLOW_COMPOSED event emitted
                event_names = [e[0] for e in emitted_events]
                assert "WORKFLOW_COMPOSED" in event_names
                
                # Check event data has step_count
                workflow_event = next(e for e in emitted_events if e[0] == "WORKFLOW_COMPOSED")
                assert workflow_event[1]["step_count"] == 2

    @pytest.mark.skipif(WorkflowComposer is None, reason="WorkflowComposer not yet implemented")
    def test_execute_tracks_history(self):
        """execute() tracks execution history per workflow run."""
        template_content = """workflow:
  name: History Test
  steps:
    - step_id: step1
      orchestrator: OrchestratorA
      parameters: {}
"""
        template_path = Path("workflows/history-test.yaml")
        
        with patch.object(Path, "exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=template_content)):
            composer = WorkflowComposer(template_path=template_path)
            
            mock_orch = MagicMock()
            mock_orch.execute.return_value = {"success": True}
            
            with patch.object(composer, "_get_orchestrator", return_value=mock_orch):
                composer.execute()
                composer.execute()
                
                history = composer.get_execution_history()
                assert len(history) == 2


# =============================================================================
# WORKFLOW EXECUTION RESULT TESTS
# =============================================================================
class TestWorkflowExecutionResult:
    """Test WorkflowExecutionResult dataclass."""

    @pytest.mark.skipif(WorkflowExecutionResult is None, reason="WorkflowExecutionResult not yet implemented")
    def test_workflow_execution_result_structure(self):
        """WorkflowExecutionResult has success, steps_completed, error_message."""
        result = WorkflowExecutionResult(
            success=True,
            steps_completed=3,
            total_steps=3,
            error_message=None,
        )
        assert result.success is True
        assert result.steps_completed == 3
        assert result.total_steps == 3

    @pytest.mark.skipif(WorkflowExecutionResult is None, reason="WorkflowExecutionResult not yet implemented")
    def test_workflow_execution_result_with_error(self):
        """WorkflowExecutionResult captures error when workflow fails."""
        result = WorkflowExecutionResult(
            success=False,
            steps_completed=1,
            total_steps=3,
            error_message="Orchestrator 'BadOrch' not found",
        )
        assert result.success is False
        assert result.error_message is not None


# =============================================================================
# AC_COMPLETE: AC-P84-S1-T1-001 (RED phase — tests expected to fail/skip)
# =============================================================================
