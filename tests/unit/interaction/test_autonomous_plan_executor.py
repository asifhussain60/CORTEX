"""Tests for AutonomousPlanExecutor - Continuation Detection.

Authority: Phase 35 R1
"""

import tempfile
from pathlib import Path

import pytest
import yaml

from cortex.interaction.autonomous_plan_executor import (
    AutonomousPlanExecutor,
    Phase,
)


class TestAutonomousPlanExecutor:
    """Test suite for AutonomousPlanExecutor."""

    def test_detect_continuation_proceed(self):
        """Test detection of 'proceed' keyword."""
        executor = AutonomousPlanExecutor()
        assert executor.detect_continuation("proceed")
        assert executor.is_autonomous_mode()
        assert "proceed" in executor.get_continuation_reason().lower()

    def test_detect_continuation_continue(self):
        """Test detection of 'continue' keyword."""
        executor = AutonomousPlanExecutor()
        assert executor.detect_continuation("continue with implementation")
        assert executor.is_autonomous_mode()

    def test_detect_continuation_yes(self):
        """Test detection of 'yes' approval."""
        executor = AutonomousPlanExecutor()
        assert executor.detect_continuation("yes")
        assert executor.is_autonomous_mode()

    def test_detect_continuation_approve(self):
        """Test detection of 'approve' keyword."""
        executor = AutonomousPlanExecutor()
        assert executor.detect_continuation("approve")
        assert executor.is_autonomous_mode()

    def test_detect_continuation_phase_number(self):
        """Test detection of phase number references."""
        executor = AutonomousPlanExecutor()
        assert executor.detect_continuation("phase 3")
        assert executor.detect_continuation("phase-3")
        assert executor.is_autonomous_mode()

    def test_detect_continuation_autonomous(self):
        """Test detection of 'autonomous' keyword."""
        executor = AutonomousPlanExecutor()
        assert executor.detect_continuation("execute autonomously")
        assert executor.is_autonomous_mode()

    def test_detect_continuation_bypass_challenge(self):
        """Test detection of 'bypass challenge' phrase."""
        executor = AutonomousPlanExecutor()
        assert executor.detect_continuation("bypass challenge")
        assert executor.is_autonomous_mode()

    def test_no_continuation_detected(self):
        """Test non-continuation input."""
        executor = AutonomousPlanExecutor()
        assert not executor.detect_continuation("what is the next step?")
        assert not executor.is_autonomous_mode()

    def test_reset(self):
        """Test reset functionality."""
        executor = AutonomousPlanExecutor()
        executor.detect_continuation("proceed")
        assert executor.is_autonomous_mode()

        executor.reset()
        assert not executor.is_autonomous_mode()

    def test_should_skip_dor_autonomous(self):
        """Test DoR skip in autonomous mode."""
        executor = AutonomousPlanExecutor()
        executor.detect_continuation("proceed")
        assert executor.should_skip_dor()

    def test_should_skip_dor_not_autonomous(self):
        """Test DoR not skipped when not autonomous."""
        executor = AutonomousPlanExecutor()
        assert not executor.should_skip_dor()


class TestLoadNextPhase:
    """Test suite for load_next_phase functionality."""

    @pytest.fixture
    def mock_registry(self):
        """Create mock registry file."""
        registry_data = {
            "active_phases": [
                {
                    "id": "phase-35",
                    "name": "Autonomous Execution Enhancement",
                    "status": "in-progress",
                    "priority": "P0",
                    "execution_order": 2,
                    "file": "phases/active/phase-35.yaml",
                },
                {
                    "id": "phase-32",
                    "name": "Glassmorphism Dashboard Fix",
                    "status": "planned",
                    "priority": "P0",
                    "execution_order": 1,
                    "file": "phases/active/phase-32.yaml",
                },
            ]
        }

        # Create temporary registry file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump(registry_data, f)
            return Path(f.name)

    def test_load_next_phase_in_progress(self, mock_registry):
        """Test loading in-progress phase."""
        executor = AutonomousPlanExecutor(registry_path=mock_registry)
        phase = executor.load_next_phase()

        assert phase is not None
        assert phase.id == "phase-35"
        assert phase.status == "in-progress"
        assert phase.name == "Autonomous Execution Enhancement"

        # Cleanup
        mock_registry.unlink()

    def test_load_next_phase_planned(self):
        """Test loading planned phase when no in-progress."""
        registry_data = {
            "active_phases": [
                {
                    "id": "phase-32",
                    "name": "Glassmorphism Dashboard Fix",
                    "status": "planned",
                    "priority": "P0",
                    "execution_order": 1,
                    "file": "phases/active/phase-32.yaml",
                }
            ]
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump(registry_data, f)
            registry_path = Path(f.name)

        executor = AutonomousPlanExecutor(registry_path=registry_path)
        phase = executor.load_next_phase()

        assert phase is not None
        assert phase.id == "phase-32"
        assert phase.status == "planned"

        # Cleanup
        registry_path.unlink()

    def test_load_next_phase_no_phases(self):
        """Test behavior when no phases available."""
        registry_data = {"active_phases": []}

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump(registry_data, f)
            registry_path = Path(f.name)

        executor = AutonomousPlanExecutor(registry_path=registry_path)
        phase = executor.load_next_phase()

        assert phase is None

        # Cleanup
        registry_path.unlink()

    def test_load_next_phase_nonexistent_registry(self):
        """Test behavior when registry file doesn't exist."""
        executor = AutonomousPlanExecutor(
            registry_path=Path("/nonexistent/path.yaml")
        )
        phase = executor.load_next_phase()
        assert phase is None


class TestGetContinuationReason:
    """Test suite for get_continuation_reason."""

    def test_reason_proceed(self):
        """Test reason for 'proceed'."""
        executor = AutonomousPlanExecutor()
        executor.detect_continuation("proceed")
        reason = executor.get_continuation_reason()
        assert "proceed" in reason.lower()

    def test_reason_phase_number(self):
        """Test reason for phase number."""
        executor = AutonomousPlanExecutor()
        executor.detect_continuation("phase 3")
        reason = executor.get_continuation_reason()
        assert "phase" in reason.lower() and "3" in reason

    def test_reason_autonomous(self):
        """Test reason for 'autonomous'."""
        executor = AutonomousPlanExecutor()
        executor.detect_continuation("execute autonomously")
        reason = executor.get_continuation_reason()
        assert "autonomous" in reason.lower()
