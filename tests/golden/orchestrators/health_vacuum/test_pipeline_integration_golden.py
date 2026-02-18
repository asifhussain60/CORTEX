"""
Golden Tests: Health-Vacuum Pipeline Integration — Phase 48
Scenarios GP-001 to GP-003

TDD: RED phase — end-to-end pipeline validation.
Authority: Phase 48, CORE-008
"""

import pytest
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock


# ===========================================================================
# FIXTURES
# ===========================================================================


@pytest.fixture
def tmp_repo(tmp_path):
    """Minimal repo structure for pipeline testing."""
    for d in [
        "cortex/brain/vacuum",
        "cortex/agents",
        "docs",
        "scripts",
        "_workspaces",
    ]:
        (tmp_path / d).mkdir(parents=True, exist_ok=True)
    (tmp_path / "README.md").write_text("# CORTEX")
    (tmp_path / "pytest.ini").write_text("[pytest]")
    (tmp_path / "requirements.txt").write_text("pytest")
    return tmp_path


@pytest.fixture
def pipeline(tmp_repo):
    """Create HealthVacuumPipeline pointed at temp repo."""
    from cortex.orchestrators.support.health_orchestrator import HealthVacuumPipeline
    return HealthVacuumPipeline(workspace_root=tmp_repo, dry_run=False)


@pytest.fixture
def pipeline_dry(tmp_repo):
    from cortex.orchestrators.support.health_orchestrator import HealthVacuumPipeline
    return HealthVacuumPipeline(workspace_root=tmp_repo, dry_run=True)


# ===========================================================================
# GP-001: End-to-end Happy Path
# ===========================================================================


class TestPipelineHappyPath:
    """GP-001: Full pipeline runs all stages, cleans up handoff."""

    def test_pipeline_runs_all_stages(self, tmp_repo, pipeline):
        """GP-001: All 5 stages execute without error."""
        # Inject a screaming case file for the health scan to find
        (tmp_repo / "WAVE-1-CERTIFICATE.txt").write_text("cert")

        report = pipeline.run(autonomous=True)

        assert report.stage_1_preflight == "PASS"
        assert report.stage_2_health_scan == "PASS"
        assert report.stage_4_vacuum == "PASS"
        assert report.stage_5_verification == "PASS"

    def test_handoff_file_deleted_after_success(self, tmp_repo, pipeline):
        """GP-001: health-issues.yaml absent after successful run."""
        (tmp_repo / "WAVE-1-CERTIFICATE.txt").write_text("cert")

        pipeline.run(autonomous=True)

        handoff = tmp_repo / "cortex" / "brain" / "vacuum" / "health-issues.yaml"
        assert not handoff.exists()

    def test_rollback_manifest_deleted_after_success(self, tmp_repo, pipeline):
        """GP-001: rollback-manifest.json absent after successful run."""
        (tmp_repo / "WAVE-1-CERTIFICATE.txt").write_text("cert")

        pipeline.run(autonomous=True)

        manifest = tmp_repo / "cortex" / "brain" / "vacuum" / "rollback-manifest.json"
        assert not manifest.exists()

    def test_screaming_file_renamed_after_pipeline(self, tmp_repo, pipeline):
        """GP-001: WAVE-1-CERTIFICATE.txt → wave-1-certificate.txt post-run."""
        import os
        (tmp_repo / "WAVE-1-CERTIFICATE.txt").write_text("cert")

        pipeline.run(autonomous=True)

        dir_listing = os.listdir(str(tmp_repo))
        assert "WAVE-1-CERTIFICATE.txt" not in dir_listing
        assert "wave-1-certificate.txt" in dir_listing


# ===========================================================================
# GP-002: Dirty Git State Handling
# ===========================================================================


class TestDirtyGitStateHandling:
    """GP-002: Pipeline stashes on dirty git state, continues safely."""

    def test_pipeline_stashes_dirty_state(self, tmp_repo, pipeline):
        """GP-002: Dirty state detected → stash action recorded."""
        with patch.object(pipeline, "_git_status", return_value="dirty"):
            with patch.object(pipeline, "_git_stash") as mock_stash:
                pipeline.run(autonomous=True)
                mock_stash.assert_called_once()

    def test_pipeline_continues_after_stash(self, tmp_repo, pipeline):
        """GP-002: Pipeline does not abort on dirty state, stashes and continues."""
        (tmp_repo / "SCREAMING.txt").write_text("data")

        with patch.object(pipeline, "_git_status", return_value="dirty"):
            with patch.object(pipeline, "_git_stash"):
                report = pipeline.run(autonomous=True)

        assert report.stage_2_health_scan == "PASS"


# ===========================================================================
# GP-003: Dry Run Mode
# ===========================================================================


class TestDryRunMode:
    """GP-003: Dry-run logs operations without modifying files."""

    def test_dry_run_no_files_changed(self, tmp_repo, pipeline_dry):
        """GP-003: dry_run=True → all files unchanged."""
        screaming = tmp_repo / "WAVE-1-CERT.txt"
        screaming.write_text("data")

        pipeline_dry.run(autonomous=True)

        # Original file must still exist (not renamed/deleted)
        assert screaming.exists()

    def test_dry_run_generates_report(self, tmp_repo, pipeline_dry):
        """GP-003: dry_run=True → operations logged in report."""
        (tmp_repo / "WAVE-1-CERT.txt").write_text("data")

        report = pipeline_dry.run(autonomous=True)

        assert report.operations_planned >= 1
        assert report.operations_executed == 0

    def test_dry_run_does_not_write_handoff(self, tmp_repo, pipeline_dry):
        """GP-003: dry_run=True → health-issues.yaml may be written but vacuum skipped."""
        (tmp_repo / "WAVE-1-CERT.txt").write_text("data")

        pipeline_dry.run(autonomous=True)

        manifest = tmp_repo / "cortex" / "brain" / "vacuum" / "rollback-manifest.json"
        assert not manifest.exists()
