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


@pytest.fixture
def mock_git_workspace(tmp_path: Path) -> Path:
    """Temp dir with fake .git directory."""
    (tmp_path / ".git").mkdir()
    return tmp_path


@pytest.fixture
def non_git_workspace(tmp_path: Path) -> Path:
    """Temp dir without .git directory."""
    return tmp_path


_PATCH_TARGET = "cortex.orchestrators.workflow.workflow_composer.SubPhaseCheckpointInjector"


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
        captured: list[object] = []

        def fake_execute(
            td: object, context: object = None, convergence_mode: bool = False
        ) -> WorkflowExecutionResult:
            captured.append(td)
            return WorkflowExecutionResult(success=True, steps_completed=0, total_steps=0)

        with patch.object(composer, "execute_from_template", side_effect=fake_execute):
            with patch(_PATCH_TARGET) as MockClass:
                mock_inst = MagicMock()
                MockClass.return_value = mock_inst

                def call_through(sub_phase_id: str, callback: object) -> object:
                    return callback()  # type: ignore[operator]

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
        skipped_result = WorkflowExecutionResult(success=True, steps_completed=0, total_steps=0)

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


    def test_compose_for_sub_phase_wraps_in_checkpoint(self) -> None:
        """SubPhaseCheckpointInjector.wrap_sub_phase() is called during execution."""
        composer = _bare_composer()
        template_data: dict = {"id": "test-template", "steps": []}
        expected = WorkflowExecutionResult(success=True, steps_completed=0, total_steps=0)

        with patch(
            "cortex.core.sub_phase_checkpoint_injector.SubPhaseCheckpointInjector"
        ) as MockClass:
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

        captured: list[object] = []

        def fake_execute_from_template(
            td: object, context: object = None, convergence_mode: bool = False
        ) -> WorkflowExecutionResult:
            captured.append(td)
            return WorkflowExecutionResult(success=True, steps_completed=0, total_steps=0)

        with patch.object(composer, "execute_from_template", side_effect=fake_execute_from_template):
            with patch(
                "cortex.core.sub_phase_checkpoint_injector.SubPhaseCheckpointInjector"
            ) as MockClass:
                mock_inst = MagicMock()
                MockClass.return_value = mock_inst

                def call_through(sub_phase_id: str, callback: object) -> object:
                    return callback()  # type: ignore[operator]

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

        with patch(
            "cortex.core.sub_phase_checkpoint_injector.SubPhaseCheckpointInjector"
        ) as MockClass:
            mock_inst = MagicMock()
            MockClass.return_value = mock_inst
            mock_inst.wrap_sub_phase.return_value = expected

            result = composer.compose_for_sub_phase(
                sub_phase_id="phase-138-c",
                template_data={"id": "t", "steps": []},
            )

        assert result is expected

    def test_compose_for_sub_phase_non_git(self, non_git_workspace: Path) -> None:
        """Non-git workspace: checkpoint skipped=True but execution still proceeds."""
        composer = _bare_composer()
        skipped_result = WorkflowExecutionResult(success=True, steps_completed=0, total_steps=0)

        with patch(
            "cortex.core.sub_phase_checkpoint_injector.SubPhaseCheckpointInjector"
        ) as MockClass:
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


    def test_compose_for_sub_phase_wraps_in_checkpoint(
        self, mock_git_workspace: Path
    ) -> None:
        """SubPhaseCheckpointInjector.wrap_sub_phase() is called during execution."""
        from cortex.core.sub_phase_checkpoint_injector import (
            CheckpointState,
            SubPhaseCheckpointInjector,
        )

        composer = WorkflowComposer.__new__(WorkflowComposer)
        # Minimal init to avoid template loading
        composer._execution_history = []  # type: ignore[attr-defined]
        composer._event_handlers = {}  # type: ignore[attr-defined]
        composer._epilogue_hooks = []  # type: ignore[attr-defined]

        template_data = {"id": "test-template", "steps": []}
        fake_state = CheckpointState(
            sub_phase_id="test-sub-phase",
            baseline_sha="a" * 40,
            stash_created=False,
            skipped=False,
        )

        with patch(
            "cortex.core.sub_phase_checkpoint_injector.SubPhaseCheckpointInjector",
            autospec=True,
        ) as MockInjectorClass:
            mock_injector_instance = MagicMock()
            MockInjectorClass.return_value = mock_injector_instance
            mock_injector_instance.create_checkpoint.return_value = fake_state
            expected = WorkflowExecutionResult(
                success=True, steps_completed=0, total_steps=0
            )
            mock_injector_instance.wrap_sub_phase.return_value = expected

            with patch(
                "cortex.orchestrators.workflow.workflow_composer.SubPhaseCheckpointInjector",
                MockInjectorClass,
            ):
                result = composer.compose_for_sub_phase(
                    sub_phase_id="test-sub-phase",
                    template_data=template_data,
                )
        mock_injector_instance.wrap_sub_phase.assert_called_once()
        assert isinstance(result, WorkflowExecutionResult)

    def test_compose_for_sub_phase_passes_template_data(
        self, mock_git_workspace: Path
    ) -> None:
        """template_data is forwarded to the internal execution."""
        from cortex.core.sub_phase_checkpoint_injector import (
            CheckpointState,
        )

        composer = WorkflowComposer.__new__(WorkflowComposer)
        composer._execution_history = []  # type: ignore[attr-defined]
        composer._event_handlers = {}  # type: ignore[attr-defined]
        composer._epilogue_hooks = []  # type: ignore[attr-defined]

        template_data = {"id": "test-template", "steps": [], "custom": "value"}

        with patch(
            "cortex.orchestrators.workflow.workflow_composer.SubPhaseCheckpointInjector"
        ) as MockInjector:
            mock_injector_instance = MagicMock()
            MockInjector.return_value = mock_injector_instance
            captured: list[object] = []

            def fake_wrap(sub_phase_id: str, callback: object) -> WorkflowExecutionResult:
                # Execute the callback to capture what template_data was passed
                result = callback()  # type: ignore[operator]
                captured.append(result)
                return result  # type: ignore[return-value]

            mock_injector_instance.wrap_sub_phase.side_effect = fake_wrap

            composer.compose_for_sub_phase(
                sub_phase_id="138-b",
                template_data=template_data,
            )

        # The callback should have been called (template_data processed)
        assert len(captured) == 1

    def test_compose_for_sub_phase_returns_result(self) -> None:
        """compose_for_sub_phase() returns WorkflowExecutionResult."""
        composer = WorkflowComposer.__new__(WorkflowComposer)
        composer._execution_history = []  # type: ignore[attr-defined]
        composer._event_handlers = {}  # type: ignore[attr-defined]
        composer._epilogue_hooks = []  # type: ignore[attr-defined]

        expected_result = WorkflowExecutionResult(
            success=True, steps_completed=2, total_steps=2
        )

        with patch(
            "cortex.orchestrators.workflow.workflow_composer.SubPhaseCheckpointInjector"
        ) as MockInjector:
            mock_instance = MagicMock()
            MockInjector.return_value = mock_instance
            mock_instance.wrap_sub_phase.return_value = expected_result

            result = composer.compose_for_sub_phase(
                sub_phase_id="phase-138-c",
                template_data={"id": "t", "steps": []},
            )

        assert result is expected_result

    def test_compose_for_sub_phase_non_git(self, non_git_workspace: Path) -> None:
        """Non-git workspace: checkpoint skipped=True but execution still proceeds."""
        from cortex.core.sub_phase_checkpoint_injector import (
            CheckpointState,
        )

        composer = WorkflowComposer.__new__(WorkflowComposer)
        composer._execution_history = []  # type: ignore[attr-defined]
        composer._event_handlers = {}  # type: ignore[attr-defined]
        composer._epilogue_hooks = []  # type: ignore[attr-defined]

        with patch(
            "cortex.orchestrators.workflow.workflow_composer.SubPhaseCheckpointInjector"
        ) as MockInjector:
            mock_instance = MagicMock()
            MockInjector.return_value = mock_instance
            # Simulate the injector creating a skipped checkpoint but still executing
            skipped_result = WorkflowExecutionResult(
                success=True, steps_completed=0, total_steps=0
            )
            mock_instance.wrap_sub_phase.return_value = skipped_result

            result = composer.compose_for_sub_phase(
                sub_phase_id="non-git-phase",
                template_data={"id": "t", "steps": []},
                workspace=non_git_workspace,
            )

        assert result.success is True

    def test_existing_compose_methods_unaffected(self) -> None:
        """Existing WorkflowComposer.compose() still returns a list of steps."""
        # Use a minimal init to avoid file I/O
        from pathlib import Path
        composer = WorkflowComposer.__new__(WorkflowComposer)
        composer._execution_history = []  # type: ignore[attr-defined]
        composer._event_handlers = {}  # type: ignore[attr-defined]
        composer._epilogue_hooks = []  # type: ignore[attr-defined]
        composer._template = {"workflow": {"steps": []}}  # type: ignore[attr-defined]
        composer._template_path = Path("dummy.yaml")  # type: ignore[attr-defined]

        steps = composer.compose()
        assert isinstance(steps, list)
