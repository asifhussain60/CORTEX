"""
Tests for WorkflowComposer convergence_mode extension.

Phase 100 Stage 3 Part 2: Non-breaking extension for convergence-gated execution

Test Coverage:
- convergence_mode parameter (optional, non-breaking)
- StepStateMachine integration when convergence_mode=True
- Standard execution preserved when convergence_mode=False
- Retry loops with backoff
- No regression in existing behavior

Author: Asif Hussain
"""

import pytest
from typing import Dict, Any, List
from unittest.mock import Mock, patch, MagicMock

# AC_START: AC-PHASE100-006
# Description: WorkflowComposer convergence_mode extension


class TestWorkflowComposerConvergenceMode:
    """Test WorkflowComposer convergence_mode parameter."""

    def test_convergence_mode_disabled_uses_standard_logic(self):
        """Should use standard execution when convergence_mode=False."""
        from cortex.orchestrators.workflow.workflow_composer import WorkflowComposer
        from pathlib import Path
        import tempfile

        # Create mock template file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("workflow:\n  name: test\n  steps:\n    - step_id: step1\n      orchestrator: test\n")
            template_path = Path(f.name)

        composer = WorkflowComposer(template_path=template_path)
        workflow = {
            "id": "test-workflow",
            "steps": [{"id": "step1", "action": "test"}],
        }
        context = {"mode": "standard"}

        # convergence_mode defaults to False
        result = composer.execute(workflow, context)

        assert result is not None
        template_path.unlink()  # Cleanup

    @patch("cortex.orchestrators.workflow.step_state_machine.StepStateMachine")
    def test_convergence_mode_enabled_uses_step_fsm(self, mock_fsm_class):
        """Should use StepStateMachine when convergence_mode=True."""
        from cortex.orchestrators.workflow.workflow_composer import WorkflowComposer
        from pathlib import Path
        import tempfile

        # Create mock template file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("workflow:\n  name: test\n  steps:\n    - step_id: step1\n      orchestrator: test\n")
            template_path = Path(f.name)

        mock_fsm = MagicMock()
        mock_fsm.is_terminal_state.side_effect = [False, True]  # Execute once
        mock_fsm.current_state = "PASSED"
        mock_fsm_class.return_value = mock_fsm

        composer = WorkflowComposer(template_path=template_path)
        workflow = {
            "id": "test-workflow",
            "steps": [
                {
                    "id": "step1",
                    "action": "test",
                    "convergence_gate": {"max_cycles": 5},
                }
            ],
        }
        context = {"mode": "convergence"}

        result = composer.execute(workflow, context, convergence_mode=True)

        # Verify StepStateMachine was used
        mock_fsm_class.assert_called()
        assert result is not None
        template_path.unlink()  # Cleanup

    @patch("cortex.orchestrators.workflow.step_state_machine.StepStateMachine")
    def test_convergence_mode_retry_loop(self, mock_fsm_class):
        """Should retry steps until convergence."""
        from cortex.orchestrators.workflow.workflow_composer import WorkflowComposer
        from pathlib import Path
        import tempfile

        # Create mock template file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("workflow:\n  name: test\n  steps:\n    - step_id: step1\n      orchestrator: test\n")
            template_path = Path(f.name)

        mock_fsm = MagicMock()
        # Simulate: PENDING → RUNNING → CHECKING → RETRYING → RUNNING → PASSED
        mock_fsm.is_terminal_state.side_effect = [
            False,
            False,
            False,
            True,
        ]  # 3 cycles
        mock_fsm.current_state = "PASSED"
        mock_fsm_class.return_value = mock_fsm

        composer = WorkflowComposer(template_path=template_path)
        workflow = {
            "id": "test-workflow",
            "steps": [
                {
                    "id": "step1",
                    "action": "test",
                    "convergence_gate": {"max_cycles": 5},
                }
            ],
        }
        context = {"mode": "convergence"}

        result = composer.execute(workflow, context, convergence_mode=True)

        # Verify multiple FSM transitions
        assert mock_fsm.execute_transition.call_count >= 3
        assert result is not None
        template_path.unlink()  # Cleanup

    @patch("cortex.orchestrators.workflow.step_state_machine.StepStateMachine")
    @patch("time.sleep")
    def test_convergence_mode_backoff_strategy(self, mock_sleep, mock_fsm_class):
        """Should apply backoff delay between retries."""
        from cortex.orchestrators.workflow.workflow_composer import WorkflowComposer
        from pathlib import Path
        import tempfile

        # Create mock template file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("workflow:\n  name: test\n  steps:\n    - step_id: step1\n      orchestrator: test\n")
            template_path = Path(f.name)

        mock_fsm = MagicMock()
        mock_fsm.is_terminal_state.side_effect = [False, False, True]
        mock_fsm.current_state = "RETRYING"
        mock_fsm.backoff_delay.return_value = 1.0
        mock_fsm_class.return_value = mock_fsm

        composer = WorkflowComposer(template_path=template_path)
        workflow = {
            "id": "test-workflow",
            "steps": [
                {
                    "id": "step1",
                    "action": "test",
                    "convergence_gate": {
                        "max_cycles": 5,
                        "backoff_strategy": "linear",
                    },
                }
            ],
        }
        context = {"mode": "convergence"}

        result = composer.execute(workflow, context, convergence_mode=True)

        # Verify backoff was called
        mock_fsm.backoff_delay.assert_called()
        mock_sleep.assert_called()
        template_path.unlink()  # Cleanup

    def test_no_regression_existing_callers(self):
        """Should not break existing WorkflowComposer callers."""
        from cortex.orchestrators.workflow.workflow_composer import WorkflowComposer
        from pathlib import Path
        import tempfile

        # Create mock template file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("workflow:\n  name: test\n  steps:\n    - step_id: step1\n      orchestrator: test\n")
            template_path = Path(f.name)

        composer = WorkflowComposer(template_path=template_path)
        workflow = {
            "id": "test-workflow",
            "steps": [{"id": "step1", "action": "test"}],
        }
        context = {"mode": "standard"}

        # Call WITHOUT convergence_mode parameter (existing behavior)
        result = composer.execute(workflow, context)

        # Should work (no TypeError for missing parameter)
        assert result is not None
        template_path.unlink()  # Cleanup

    @patch("cortex.orchestrators.workflow.step_state_machine.StepStateMachine")
    def test_convergence_neuron_integration(self, mock_fsm_class):
        """Should integrate ConvergenceNeuron for success criteria checking."""
        from cortex.orchestrators.workflow.workflow_composer import WorkflowComposer
        from pathlib import Path
        import tempfile

        # Create mock template file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("workflow:\n  name: test\n  steps:\n    - step_id: step1\n      orchestrator: test\n")
            template_path = Path(f.name)

        mock_fsm = MagicMock()
        mock_fsm.is_terminal_state.side_effect = [False, True]
        mock_fsm.current_state = "PASSED"
        mock_fsm_class.return_value = mock_fsm

        composer = WorkflowComposer(template_path=template_path)
        workflow = {
            "id": "test-workflow",
            "steps": [
                {
                    "id": "step1",
                    "action": "test",
                    "convergence_gate": {
                        "max_cycles": 5,
                        "success_criteria": {"tests_pass": True},
                        "convergence_predicate": "tests_pass == True",
                    },
                }
            ],
        }
        context = {"mode": "convergence"}

        result = composer.execute(workflow, context, convergence_mode=True)

        # Verify StepStateMachine initialized with convergence_gate config
        call_args = mock_fsm_class.call_args
        assert "convergence_config" in call_args[1] or call_args[0]
        assert result is not None
        template_path.unlink()  # Cleanup


# AC_COMPLETE: AC-PHASE100-006 ✅ 6/6 tests written (RED phase)
