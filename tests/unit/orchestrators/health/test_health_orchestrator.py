"""Unit Tests — HealthOrchestrator

Phase: PHASE-51
CORE: CORE-008 (TDD)
"""

from pathlib import Path

import pytest


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    """Minimal workspace for unit-level health tests."""
    (tmp_path / "cortex").mkdir()
    (tmp_path / "cortex" / "__init__.py").write_text("")
    (tmp_path / "cortex" / "module.py").write_text("x = 1\n")
    (tmp_path / "README.md").write_text("# Hi\n")
    return tmp_path


class TestHealthOrchestratorInit:
    """Construction and basic configuration."""

    def test_init(self, workspace: Path) -> None:
        from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator

        orch = HealthOrchestrator(workspace)
        assert orch.workspace_root == workspace

    def test_init_nonexistent_raises(self, tmp_path: Path) -> None:
        from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator

        with pytest.raises(ValueError, match="does not exist"):
            HealthOrchestrator(tmp_path / "nonexistent")

    def test_scan_returns_scan_result(self, workspace: Path) -> None:
        from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator
        from cortex.orchestrators.health.models import ScanResult

        orch = HealthOrchestrator(workspace)
        result = orch.scan()
        assert isinstance(result, ScanResult)

    def test_scan_files_scanned_positive(self, workspace: Path) -> None:
        from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator

        orch = HealthOrchestrator(workspace)
        result = orch.scan()
        assert result.files_scanned > 0


class TestHealthOrchestratorHandoff:
    """write_handoff() — YAML handoff for VacuumOrchestrator."""

    def test_write_handoff_creates_file(self, workspace: Path) -> None:
        from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator
        from cortex.orchestrators.health.constants import HANDOFF_FILENAME, RUNTIME_DIR

        orch = HealthOrchestrator(workspace)
        result = orch.scan()
        handoff_path = workspace / RUNTIME_DIR / HANDOFF_FILENAME
        orch.write_handoff(result, handoff_path)
        assert handoff_path.exists()

    def test_handoff_is_valid_yaml(self, workspace: Path) -> None:
        import yaml
        from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator
        from cortex.orchestrators.health.constants import HANDOFF_FILENAME, RUNTIME_DIR

        orch = HealthOrchestrator(workspace)
        result = orch.scan()
        handoff_path = workspace / RUNTIME_DIR / HANDOFF_FILENAME
        orch.write_handoff(result, handoff_path)

        data = yaml.safe_load(handoff_path.read_text())
        assert "health_score" in data
        assert "issues" in data


class TestHealthOrchestratorDoD:
    """check_definition_of_done() — DoD gate."""

    def test_clean_workspace_passes(self, workspace: Path) -> None:
        from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator

        orch = HealthOrchestrator(workspace)
        result = orch.scan()
        passes = orch.check_definition_of_done(result, min_score=0.0)
        assert passes is True

    def test_strict_gate_fails_on_issues(self, workspace: Path) -> None:
        from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator

        (workspace / "SCREAMING.txt").write_text("bad\n")
        orch = HealthOrchestrator(workspace)
        result = orch.scan()
        passes = orch.check_definition_of_done(result, min_score=100.0)
        assert passes is False
