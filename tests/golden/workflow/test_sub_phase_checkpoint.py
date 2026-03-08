"""
Golden workflow tests for Phase-138-c.
Tests WorkflowComposer.compose_for_sub_phase() — checkpoint-wrapped execution.
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cortex.orchestrators.workflow.workflow_composer import (
    WorkflowComposer,
    WorkflowExecutionResult,
)

# Patch target — module-level import in workflow_composer
_PATCH_TARGET = (
    "cortex.orchestrators.workflow.workflow_composer.SubPhaseCheckpointInjector"
)


@pytest.fixture
def non_git_workspace(tmp_path: Path) -> Path:
    """Temp dir without .git directory."""
    return tmp_path


def _bare_composer() -> WorkflowComposer:
    """Return a WorkflowComposer with minimal init — avoids template I/O."""
    composer = WorkflowComposer.__new__(WorkflowComposer)
    composer._execution_history = []  # type: ignore[attr-defined]
    composer._event_handlers = {}  # type: ignore[attr-defined]
    composer._epilogue_hooks = []  # type: ignore[attr-defined]
    composer._template = {"workflow": {"steps": []}}  # type: ignore[attr-defined]
    composer._template_path = Path("dummy.yaml")  # type: ignore[attr-defined]
    composer._steps = []  # type: ignore[attr-defined]
    return composer


class TestWorkflowComposerComposeForSubPhase:
    """WorkflowComposer.compose_for_sub_phase() golden tests."""

    def test_compose_for_sub_phase_method_exists(self) -> None:
        """compose_for_sub_phase() method exists on WorkflowComposer."""
        assert hasattr(WorkflowComposer, "compose_for_sub_phase")
        assert callable(getattr(WorkflowComposer, "compose_for_sub_phase"))

    def test_compose_for_sub_phase_wraps_in_checkpoint(self) -> None:
        """SubPhaseCheckpointInjector.wrap_sub_phase() is called during execution."""
        composer = _bare_composer()
        template_data: dict = {"id": "test-template", "steps": []}
        expected = WorkflowExecutionResult(success=True, steps_completed=0, total_steps=0)

        with patch(_PATCH_TARGET) as MockClass:
            mock_inst = MagicMock()
            MockClass.return_value = mock_inst
            mock_inst.wrap_sub_phase.return_value = expected

            result = composer.compose_for_sub_phase(
                sub_phase_id="test-sub-phase",
                template_data=template_data,
            )

        mock_inst.wrap_sub_phase.assert_called_once()
        assert result is expected

    def test_compose_for_sub_phase_passes_template_data(self) -> None:
        """template_data is forwarded to execute_from_template inside callback."""
        composer = _bare_composer()
        template_data: dict = {"id": "test-template", "steps": [], "custom": "value"}
        captured: list = []

        def fake_execute(td, context=None, convergence_mode=False):  # type: ignore[no-untyped-def]
            captured.append(td)
            return WorkflowExecutionResult(success=True, steps_completed=0, total_steps=0)

        with patch.object(composer, "execute_from_template", side_effect=fake_execute):
            with patch(_PATCH_TARGET) as MockClass:
                mock_inst = MagicMock()
                MockClass.return_value = mock_inst

                def call_through(sub_phase_id, callback):  # type: ignore[no-untyped-def]
                    return callback()

                mock_inst.wrap_sub_phase.side_effect = call_through
                composer.compose_for_sub_phase(
                    sub_phase_id="138-b",
                    template_data=template_data,
                )

        assert len(captured) == 1
        assert captured[0] is template_data

    def test_compose_for_sub_phase_returns_result(self) -> None:
        """compose_for_sub_phase() returns WorkflowExecutionResult."""
        composer = _bare_composer()
        expected = WorkflowExecutionResult(success=True, steps_completed=2, total_steps=2)

        with patch(_PATCH_TARGET) as MockClass:
            mock_inst = MagicMock()
            MockClass.return_value = mock_inst
            mock_inst.wrap_sub_phase.return_value = expected

            result = composer.compose_for_sub_phase(
                sub_phase_id="phase-138-c",
                template_data={"id": "t", "steps": []},
            )

        assert result is expected

    def test_compose_for_sub_phase_non_git(self, non_git_workspace: Path) -> None:
        """Non-git workspace: execution still proceeds (checkpoint skipped gracefully)."""
        composer = _bare_composer()
        skipped_result = WorkflowExecutionResult(
            success=True, steps_completed=0, total_steps=0
        )

        with patch(_PATCH_TARGET) as MockClass:
            mock_inst = MagicMock()
            MockClass.return_value = mock_inst
            mock_inst.wrap_sub_phase.return_value = skipped_result

            result = composer.compose_for_sub_phase(
                sub_phase_id="non-git-phase",
                template_data={"id": "t", "steps": []},
                workspace=non_git_workspace,
            )

        assert result.success is True

    def test_existing_compose_methods_unaffected(self) -> None:
        """Existing WorkflowComposer.compose() still returns a list of steps."""
        composer = _bare_composer()
        steps = composer.compose()
        assert isinstance(steps, list)
