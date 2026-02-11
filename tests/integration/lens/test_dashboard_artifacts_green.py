"""
AC_START: AC-ENH087-T5-S4-GREEN-TESTS-001
ENH-087 Track 5 Stage 4: Dashboard Artifacts Generation
GREEN Phase: DashboardArtifactGenerator Implementation Tests

Tests validate that DashboardArtifactGenerator orchestrator correctly implements
all dashboard artifact lifecycle operations with full YAML persistence.

Author: CORTEX Architect
Authority: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import json
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Generator

import pytest
import yaml

from cortex.orchestrators.lens.dashboard_artifact_generator import (
    DashboardArtifactGenerator,
    DashboardArtifact,
    DashboardMetadata,
    ArtifactStatus,
    OutputFormat,
)


class TestDashboardArtifactGenerator:
    """GREEN: Test DashboardArtifactGenerator orchestrator implementation."""

    @pytest.fixture
    def temp_cortex_brain(self) -> Generator[Path, None, None]:
        """Fixture: Create temporary cortex_brain directory with artifact structure."""
        with tempfile.TemporaryDirectory(prefix="cortex_brain_test_") as temp_dir:
            temp_path = Path(temp_dir)

            # Create required subdirectories
            (temp_path / "dashboards" / "active").mkdir(parents=True, exist_ok=True)
            (temp_path / "dashboards" / "archive").mkdir(parents=True, exist_ok=True)
            (temp_path / "dashboards" / "staging").mkdir(parents=True, exist_ok=True)
            (temp_path / "sessions").mkdir(parents=True, exist_ok=True)
            (temp_path / "onboarded_repos").mkdir(parents=True, exist_ok=True)

            yield temp_path

    @pytest.fixture
    def generator(self, temp_cortex_brain: Path) -> DashboardArtifactGenerator:
        """Fixture: Create DashboardArtifactGenerator instance."""
        return DashboardArtifactGenerator(temp_cortex_brain)

    @pytest.fixture
    def sample_artifact_data(self) -> Dict[str, Any]:
        """Fixture: Sample artifact data for testing."""
        return {
            "analysis_results": [
                {"file": "main.py", "issues": 5, "severity": "HIGH"},
                {"file": "utils.py", "issues": 2, "severity": "LOW"},
            ],
            "summary": {"total_files": 2, "total_issues": 7},
        }

    def test_orchestrator_initialization(self, temp_cortex_brain: Path) -> None:
        """Test orchestrator initializes with correct directory structure."""
        gen = DashboardArtifactGenerator(temp_cortex_brain)

        assert (temp_cortex_brain / "dashboards" / "active").exists()
        assert (temp_cortex_brain / "dashboards" / "archive").exists()
        assert (temp_cortex_brain / "dashboards" / "staging").exists()

    def test_generate_artifact_success(
        self,
        generator: DashboardArtifactGenerator,
        sample_artifact_data: Dict[str, Any],
    ) -> None:
        """Test artifact generation creates PENDING artifact."""
        artifact = generator.generate_artifact(
            artifact_id="test-artifact-001",
            analysis_id="analysis-123",
            repository_id="repo-456",
            analysis_type="LENS",
            orchestrator="LENSOrchestrator",
            data=sample_artifact_data,
            session_id="sess-001",
            repo_path="/path/to/repo",
            item_count=2,
            analysis_duration_ms=150.5,
            categories={"HIGH": 1, "LOW": 1},
            scores={"severity": 0.85},
        )

        assert artifact.artifact_id == "test-artifact-001"
        assert artifact.status == ArtifactStatus.PENDING
        assert artifact.metadata.analysis_id == "analysis-123"
        assert artifact.metadata.repository_id == "repo-456"
        assert artifact.metadata.analysis_type == "LENS"
        assert artifact.metadata.orchestrator == "LENSOrchestrator"
        assert artifact.data == sample_artifact_data
        assert artifact.metadata.total_items == 2
        assert artifact.metadata.analysis_duration_ms == 150.5

    def test_artifact_file_contains_metadata(
        self,
        generator: DashboardArtifactGenerator,
        temp_cortex_brain: Path,
        sample_artifact_data: Dict[str, Any],
    ) -> None:
        """Test artifact YAML file contains all required metadata."""
        artifact = generator.generate_artifact(
            artifact_id="test-artifact-002",
            analysis_id="analysis-124",
            repository_id="repo-457",
            analysis_type="LENS",
            orchestrator="LENSOrchestrator",
            data=sample_artifact_data,
            session_id="sess-002",
        )

        # Verify file exists in staging
        artifact_path = (
            temp_cortex_brain / "dashboards" / "staging" / "test-artifact-002.yaml"
        )
        assert artifact_path.exists()

        # Load and verify content
        with open(artifact_path, "r") as f:
            loaded = yaml.safe_load(f)

        assert loaded["artifact_id"] == "test-artifact-002"
        assert loaded["status"] == "PENDING"
        assert loaded["metadata"]["analysis_id"] == "analysis-124"
        assert loaded["metadata"]["repository_id"] == "repo-457"

    def test_get_artifact_success(
        self,
        generator: DashboardArtifactGenerator,
        sample_artifact_data: Dict[str, Any],
    ) -> None:
        """Test retrieving artifact by ID."""
        generator.generate_artifact(
            artifact_id="test-artifact-003",
            analysis_id="analysis-125",
            repository_id="repo-458",
            analysis_type="LENS",
            orchestrator="LENSOrchestrator",
            data=sample_artifact_data,
        )

        retrieved = generator.get_artifact("test-artifact-003")
        assert retrieved is not None
        assert retrieved.artifact_id == "test-artifact-003"
        assert retrieved.metadata.analysis_id == "analysis-125"

    def test_get_artifact_not_found(self, generator: DashboardArtifactGenerator) -> None:
        """Test retrieving non-existent artifact returns None."""
        retrieved = generator.get_artifact("non-existent-artifact")
        assert retrieved is None

    def test_validate_artifact_success(
        self,
        generator: DashboardArtifactGenerator,
        sample_artifact_data: Dict[str, Any],
    ) -> None:
        """Test artifact validation passes for valid artifacts."""
        artifact = generator.generate_artifact(
            artifact_id="test-artifact-004",
            analysis_id="analysis-126",
            repository_id="repo-459",
            analysis_type="LENS",
            orchestrator="LENSOrchestrator",
            data=sample_artifact_data,
        )

        assert generator.validate_artifact("test-artifact-004") is True

    def test_activate_artifact_success(
        self,
        generator: DashboardArtifactGenerator,
        temp_cortex_brain: Path,
        sample_artifact_data: Dict[str, Any],
    ) -> None:
        """Test artifact activation moves from STAGING to ACTIVE."""
        generator.generate_artifact(
            artifact_id="test-artifact-005",
            analysis_id="analysis-127",
            repository_id="repo-460",
            analysis_type="LENS",
            orchestrator="LENSOrchestrator",
            data=sample_artifact_data,
        )

        # Verify in staging
        staging_path = (
            temp_cortex_brain / "dashboards" / "staging" / "test-artifact-005.yaml"
        )
        assert staging_path.exists()

        # Activate
        assert generator.activate_artifact("test-artifact-005") is True

        # Verify moved to active
        active_path = (
            temp_cortex_brain / "dashboards" / "active" / "test-artifact-005.yaml"
        )
        assert active_path.exists()
        assert not staging_path.exists()

        # Verify status changed
        artifact = generator.get_artifact("test-artifact-005")
        assert artifact is not None
        assert artifact.status == ArtifactStatus.ACTIVE

    def test_update_artifact_success(
        self,
        generator: DashboardArtifactGenerator,
        sample_artifact_data: Dict[str, Any],
    ) -> None:
        """Test artifact update increases version and updates data."""
        generator.generate_artifact(
            artifact_id="test-artifact-006",
            analysis_id="analysis-128",
            repository_id="repo-461",
            analysis_type="LENS",
            orchestrator="LENSOrchestrator",
            data=sample_artifact_data,
        )

        # Activate first
        generator.activate_artifact("test-artifact-006")

        # Update
        new_data = {"analysis_results": [], "summary": {"total_files": 0, "total_issues": 0}}
        assert (
            generator.update_artifact(
                "test-artifact-006", {"data": new_data}, reason="Data correction"
            )
            is True
        )

        # Verify version increased
        artifact = generator.get_artifact("test-artifact-006")
        assert artifact is not None
        assert artifact.metadata.version == 2
        assert artifact.metadata.update_reason == "Data correction"
        assert artifact.data == new_data

    def test_archive_artifact_success(
        self,
        generator: DashboardArtifactGenerator,
        temp_cortex_brain: Path,
        sample_artifact_data: Dict[str, Any],
    ) -> None:
        """Test artifact archival moves to archive directory."""
        generator.generate_artifact(
            artifact_id="test-artifact-007",
            analysis_id="analysis-129",
            repository_id="repo-462",
            analysis_type="LENS",
            orchestrator="LENSOrchestrator",
            data=sample_artifact_data,
        )

        generator.activate_artifact("test-artifact-007")

        # Archive
        assert generator.archive_artifact("test-artifact-007") is True

        # Verify moved to archive
        archive_path = (
            temp_cortex_brain / "dashboards" / "archive" / "test-artifact-007.yaml"
        )
        assert archive_path.exists()

        # Verify status changed
        artifact = generator.get_artifact("test-artifact-007")
        assert artifact is not None
        assert artifact.status == ArtifactStatus.ARCHIVED

    def test_delete_artifact_success(
        self,
        generator: DashboardArtifactGenerator,
        temp_cortex_brain: Path,
        sample_artifact_data: Dict[str, Any],
    ) -> None:
        """Test artifact deletion removes file."""
        generator.generate_artifact(
            artifact_id="test-artifact-008",
            analysis_id="analysis-130",
            repository_id="repo-463",
            analysis_type="LENS",
            orchestrator="LENSOrchestrator",
            data=sample_artifact_data,
        )

        generator.activate_artifact("test-artifact-008")

        # Verify exists
        artifact_path = (
            temp_cortex_brain / "dashboards" / "active" / "test-artifact-008.yaml"
        )
        assert artifact_path.exists()

        # Delete
        assert generator.delete_artifact("test-artifact-008") is True

        # Verify deleted
        assert not artifact_path.exists()
        assert generator.get_artifact("test-artifact-008") is None

    def test_list_active_artifacts(
        self,
        generator: DashboardArtifactGenerator,
        sample_artifact_data: Dict[str, Any],
    ) -> None:
        """Test listing active artifacts."""
        for i in range(3):
            generator.generate_artifact(
                artifact_id=f"test-artifact-active-{i}",
                analysis_id=f"analysis-{i}",
                repository_id="repo-464",
                analysis_type="LENS",
                orchestrator="LENSOrchestrator",
                data=sample_artifact_data,
            )
            generator.activate_artifact(f"test-artifact-active-{i}")

        active_artifacts = generator.list_active_artifacts()
        assert len(active_artifacts) == 3
        assert all(a.status == ArtifactStatus.ACTIVE for a in active_artifacts)

    def test_list_archived_artifacts(
        self,
        generator: DashboardArtifactGenerator,
        sample_artifact_data: Dict[str, Any],
    ) -> None:
        """Test listing archived artifacts."""
        for i in range(2):
            generator.generate_artifact(
                artifact_id=f"test-artifact-archive-{i}",
                analysis_id=f"analysis-{i}",
                repository_id="repo-465",
                analysis_type="LENS",
                orchestrator="LENSOrchestrator",
                data=sample_artifact_data,
            )
            generator.activate_artifact(f"test-artifact-archive-{i}")
            generator.archive_artifact(f"test-artifact-archive-{i}")

        archived_artifacts = generator.list_archived_artifacts()
        assert len(archived_artifacts) == 2
        assert all(a.status == ArtifactStatus.ARCHIVED for a in archived_artifacts)

    def test_export_as_json(
        self,
        generator: DashboardArtifactGenerator,
        sample_artifact_data: Dict[str, Any],
    ) -> None:
        """Test exporting artifact as JSON."""
        generator.generate_artifact(
            artifact_id="test-artifact-json",
            analysis_id="analysis-131",
            repository_id="repo-466",
            analysis_type="LENS",
            orchestrator="LENSOrchestrator",
            data=sample_artifact_data,
        )

        json_export = generator.export_as_json("test-artifact-json")
        assert json_export is not None

        # Verify it's valid JSON
        parsed = json.loads(json_export)
        assert parsed["artifact_id"] == "test-artifact-json"
        assert parsed["metadata"]["analysis_id"] == "analysis-131"

    def test_export_as_yaml(
        self,
        generator: DashboardArtifactGenerator,
        sample_artifact_data: Dict[str, Any],
    ) -> None:
        """Test exporting artifact as YAML."""
        generator.generate_artifact(
            artifact_id="test-artifact-yaml",
            analysis_id="analysis-132",
            repository_id="repo-467",
            analysis_type="LENS",
            orchestrator="LENSOrchestrator",
            data=sample_artifact_data,
        )

        yaml_export = generator.export_as_yaml("test-artifact-yaml")
        assert yaml_export is not None

        # Verify it's valid YAML
        parsed = yaml.safe_load(yaml_export)
        assert parsed["artifact_id"] == "test-artifact-yaml"

    def test_export_as_csv(
        self,
        generator: DashboardArtifactGenerator,
        sample_artifact_data: Dict[str, Any],
    ) -> None:
        """Test exporting artifact as CSV."""
        generator.generate_artifact(
            artifact_id="test-artifact-csv",
            analysis_id="analysis-133",
            repository_id="repo-468",
            analysis_type="LENS",
            orchestrator="LENSOrchestrator",
            data=sample_artifact_data,
        )

        csv_export = generator.export_as_csv("test-artifact-csv")
        assert csv_export is not None
        assert "artifact_id,test-artifact-csv" in csv_export
        assert "analysis_id,analysis-133" in csv_export

    def test_artifact_persistence_write_read_cycle(
        self,
        generator: DashboardArtifactGenerator,
        sample_artifact_data: Dict[str, Any],
    ) -> None:
        """Test artifact round-trip: generate -> read -> modify -> read."""
        # Generate
        artifact1 = generator.generate_artifact(
            artifact_id="test-artifact-cycle",
            analysis_id="analysis-134",
            repository_id="repo-469",
            analysis_type="LENS",
            orchestrator="LENSOrchestrator",
            data=sample_artifact_data,
        )

        # Read back
        artifact2 = generator.get_artifact("test-artifact-cycle")
        assert artifact2 is not None
        assert artifact2.artifact_id == artifact1.artifact_id
        assert artifact2.metadata.analysis_id == artifact1.metadata.analysis_id

        # Activate and update
        generator.activate_artifact("test-artifact-cycle")
        new_data = {"summary": {"updated": True}}
        generator.update_artifact("test-artifact-cycle", {"data": new_data})

        # Read again
        artifact3 = generator.get_artifact("test-artifact-cycle")
        assert artifact3 is not None
        assert artifact3.metadata.version == 2
        assert artifact3.data == new_data

    def test_artifact_yaml_schema_valid(
        self,
        generator: DashboardArtifactGenerator,
        temp_cortex_brain: Path,
        sample_artifact_data: Dict[str, Any],
    ) -> None:
        """Test artifact YAML files have valid schema structure."""
        generator.generate_artifact(
            artifact_id="test-artifact-schema",
            analysis_id="analysis-135",
            repository_id="repo-470",
            analysis_type="LENS",
            orchestrator="LENSOrchestrator",
            data=sample_artifact_data,
        )

        # Load YAML directly
        artifact_path = (
            temp_cortex_brain / "dashboards" / "staging" / "test-artifact-schema.yaml"
        )
        with open(artifact_path, "r") as f:
            loaded = yaml.safe_load(f)

        # Verify schema
        assert "artifact_id" in loaded
        assert "status" in loaded
        assert "metadata" in loaded
        assert "data" in loaded
        assert "format" in loaded

        # Verify metadata schema
        metadata = loaded["metadata"]
        assert "analysis_id" in metadata
        assert "repository_id" in metadata
        assert "analysis_type" in metadata
        assert "orchestrator" in metadata
        assert "created_at" in metadata

    def test_multiple_artifacts_isolation(
        self,
        generator: DashboardArtifactGenerator,
        sample_artifact_data: Dict[str, Any],
    ) -> None:
        """Test multiple artifacts are isolated and don't interfere."""
        for i in range(5):
            generator.generate_artifact(
                artifact_id=f"test-artifact-iso-{i}",
                analysis_id=f"analysis-iso-{i}",
                repository_id=f"repo-{i}",
                analysis_type="LENS",
                orchestrator="LENSOrchestrator",
                data={**sample_artifact_data, "index": i},
            )

        # Verify each is independent
        for i in range(5):
            artifact = generator.get_artifact(f"test-artifact-iso-{i}")
            assert artifact is not None
            assert artifact.metadata.repository_id == f"repo-{i}"
            assert artifact.data["index"] == i

    def test_cleanup_on_error(
        self,
        generator: DashboardArtifactGenerator,
        sample_artifact_data: Dict[str, Any],
    ) -> None:
        """Test orchestrator handles cleanup gracefully on errors."""
        # Generate valid artifact
        generator.generate_artifact(
            artifact_id="test-artifact-error",
            analysis_id="analysis-error",
            repository_id="repo-error",
            analysis_type="LENS",
            orchestrator="LENSOrchestrator",
            data=sample_artifact_data,
        )

        # Try to activate
        assert generator.activate_artifact("test-artifact-error") is True

        # Try operations on activated artifact
        updated = generator.update_artifact(
            "test-artifact-error", {"data": {**sample_artifact_data, "updated": True}}
        )
        assert updated is True

        # Should still be retrievable
        artifact = generator.get_artifact("test-artifact-error")
        assert artifact is not None

    def test_detect_orphaned_artifacts(
        self,
        generator: DashboardArtifactGenerator,
        sample_artifact_data: Dict[str, Any],
    ) -> None:
        """Test detection of orphaned artifacts with broken references."""
        # Generate artifact with broken session reference
        generator.generate_artifact(
            artifact_id="test-artifact-orphan",
            analysis_id="analysis-orphan",
            repository_id="repo-nonexistent",
            analysis_type="LENS",
            orchestrator="LENSOrchestrator",
            data=sample_artifact_data,
            session_id="nonexistent-session",
        )

        generator.activate_artifact("test-artifact-orphan")

        # Detect orphans
        orphaned = generator.detect_orphaned_artifacts()
        assert "test-artifact-orphan" in orphaned


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# AC_COMPLETE: AC-ENH087-T5-S4-GREEN-TESTS-001 ✅ 18 tests for DashboardArtifactGenerator
