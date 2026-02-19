"""Golden Tests — HealthVacuumPipeline (GP-001 .. GP-004)

End-to-end pipeline: Preflight → Scan → Review → Execute → Verify.

Phase: PHASE-51
CORE: CORE-008 (TDD), CORE-055 (golden test tier contract)
"""

from pathlib import Path

import pytest
import yaml

from cortex.orchestrators.health.models import PipelineReport


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    """Workspace with issues for pipeline to process."""
    (tmp_path / "cortex").mkdir()
    (tmp_path / "cortex" / "__init__.py").write_text("")
    (tmp_path / "cortex" / "good_module.py").write_text("x = 1\n")
    (tmp_path / "AUDIT_REPORT.txt").write_text("old report\n")
    (tmp_path / "empty.txt").write_text("")
    (tmp_path / "orphaned_dir").mkdir()
    (tmp_path / "README.md").write_text("# Project\n")
    (tmp_path / "pyproject.toml").write_text("[project]\nname='test'\n")
    (tmp_path / ".gitignore").write_text("__pycache__/\n")
    return tmp_path


class TestGP001FullPipeline:
    """GP-001: Full pipeline — all 5 stages complete."""

    def test_full_pipeline_runs(self, workspace: Path) -> None:
        from cortex.orchestrators.health.pipeline import HealthVacuumPipeline

        pipe = HealthVacuumPipeline(workspace)
        report = pipe.run()

        assert isinstance(report, PipelineReport)
        assert report.scan_result is not None
        assert report.vacuum_report is not None
        assert report.cycles >= 1


class TestGP002DryRunPipeline:
    """GP-002: Dry-run pipeline — scan runs, vacuum previews."""

    def test_dry_run_pipeline(self, workspace: Path) -> None:
        from cortex.orchestrators.health.pipeline import HealthVacuumPipeline

        pipe = HealthVacuumPipeline(workspace)
        report = pipe.run(dry_run=True)

        assert isinstance(report, PipelineReport)
        assert report.scan_result is not None
        assert report.vacuum_report is not None
        assert report.vacuum_report.dry_run is True
        # Files should NOT have changed
        assert (workspace / "AUDIT_REPORT.txt").exists()
        assert (workspace / "empty.txt").exists()


class TestGP003HandoffContract:
    """GP-003: Handoff contract — health-issues.yaml schema validated."""

    def test_handoff_written_and_consumed(self, workspace: Path) -> None:
        from cortex.orchestrators.health.pipeline import HealthVacuumPipeline
        from cortex.orchestrators.health.constants import RUNTIME_DIR, HANDOFF_FILENAME

        pipe = HealthVacuumPipeline(workspace)
        report = pipe.run()

        handoff = workspace / RUNTIME_DIR / HANDOFF_FILENAME
        assert handoff.exists()
        data = yaml.safe_load(handoff.read_text())
        assert "health_score" in data
        assert "issues" in data


class TestGP004ConvergenceGate:
    """GP-004: Convergence gate — retries on partial, exits on max_cycles."""

    def test_max_cycles_respected(self, workspace: Path) -> None:
        from cortex.orchestrators.health.pipeline import HealthVacuumPipeline

        pipe = HealthVacuumPipeline(workspace, max_cycles=1)
        report = pipe.run()

        assert report.cycles <= 1
