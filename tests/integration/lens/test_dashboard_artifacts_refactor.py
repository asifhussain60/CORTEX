"""
AC_START: AC-ENH087-T5-S4-REFACTOR-001
ENH-087 Track 5 Stage 4: Dashboard Artifacts Generation
REFACTOR Phase: Performance Profiling & Optimization

Tests validate that DashboardArtifactGenerator meets all performance targets
and provides efficient operations for dashboard artifact lifecycle management.

Author: CORTEX Architect
Authority: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import tempfile
import time
from pathlib import Path
from typing import Dict, Any, Generator

import pytest

from cortex.orchestrators.lens.dashboard_artifact_generator import (
    DashboardArtifactGenerator,
)


class TestDashboardArtifactPerformance:
    """REFACTOR: Performance profiling for DashboardArtifactGenerator."""

    @pytest.fixture
    def temp_cortex_brain(self) -> Generator[Path, None, None]:
        """Fixture: Create temporary cortex_brain with artifact structure."""
        with tempfile.TemporaryDirectory(prefix="cortex_perf_test_") as temp_dir:
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
        """Fixture: Large sample artifact data for performance testing."""
        return {
            "analysis_results": [
                {"file": f"file_{i}.py", "issues": i % 10, "severity": "HIGH"}
                for i in range(100)
            ],
            "summary": {"total_files": 100, "total_issues": 450},
            "metadata": {
                "large_field": "x" * 10000,  # Large string to test I/O performance
            },
        }

    def test_artifact_generation_performance_under_500ms(
        self,
        generator: DashboardArtifactGenerator,
        sample_artifact_data: Dict[str, Any],
    ) -> None:
        """
        REFACTOR: Dashboard artifact generation MUST complete in < 500ms.

        Performance target: < 500ms for typical analysis artifact
        Measurement includes: metadata creation + file write + validation setup
        """
        start_time = time.perf_counter()

        artifact = generator.generate_artifact(
            artifact_id="perf-artifact-001",
            analysis_id="analysis-perf-001",
            repository_id="repo-perf-001",
            analysis_type="LENS",
            orchestrator="LENSOrchestrator",
            data=sample_artifact_data,
            session_id="sess-perf-001",
            repo_path="/path/to/repo",
            item_count=100,
            analysis_duration_ms=250.0,
        )

        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000

        assert artifact is not None
        assert duration_ms < 500.0, f"Generation took {duration_ms:.2f}ms (target: <500ms)"
        print(f"✅ Generation performance: {duration_ms:.2f}ms (target: <500ms, margin: {(500-duration_ms)/500*100:.1f}%)")

    def test_artifact_read_performance_under_100ms(
        self,
        generator: DashboardArtifactGenerator,
        sample_artifact_data: Dict[str, Any],
    ) -> None:
        """
        REFACTOR: Dashboard artifact read MUST complete in < 100ms.

        Performance target: < 100ms for reading artifact from disk
        Measurement includes: file read + YAML parsing + object construction
        """
        # Setup: generate and activate artifact
        generator.generate_artifact(
            artifact_id="perf-artifact-002",
            analysis_id="analysis-perf-002",
            repository_id="repo-perf-002",
            analysis_type="LENS",
            orchestrator="LENSOrchestrator",
            data=sample_artifact_data,
        )
        generator.activate_artifact("perf-artifact-002")

        # Measure read performance
        start_time = time.perf_counter()

        artifact = generator.get_artifact("perf-artifact-002")

        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000

        assert artifact is not None
        assert duration_ms < 100.0, f"Read took {duration_ms:.2f}ms (target: <100ms)"
        print(f"✅ Read performance: {duration_ms:.2f}ms (target: <100ms, margin: {(100-duration_ms)/100*100:.1f}%)")

    def test_artifact_validation_performance_under_50ms(
        self,
        generator: DashboardArtifactGenerator,
        sample_artifact_data: Dict[str, Any],
    ) -> None:
        """
        REFACTOR: Artifact validation MUST complete in < 50ms.

        Performance target: < 50ms for schema validation
        Measurement includes: schema checks + reference validation
        """
        # Setup
        generator.generate_artifact(
            artifact_id="perf-artifact-003",
            analysis_id="analysis-perf-003",
            repository_id="repo-perf-003",
            analysis_type="LENS",
            orchestrator="LENSOrchestrator",
            data=sample_artifact_data,
        )

        # Measure validation performance
        start_time = time.perf_counter()

        result = generator.validate_artifact("perf-artifact-003")

        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000

        assert result is True
        assert duration_ms < 50.0, f"Validation took {duration_ms:.2f}ms (target: <50ms)"
        print(f"✅ Validation performance: {duration_ms:.2f}ms (target: <50ms, margin: {(50-duration_ms)/50*100:.1f}%)")

    def test_artifact_activation_performance_under_100ms(
        self,
        generator: DashboardArtifactGenerator,
        sample_artifact_data: Dict[str, Any],
    ) -> None:
        """
        REFACTOR: Artifact activation MUST complete in < 100ms.

        Performance target: < 100ms for validation + status update + file move
        Measurement includes: full activation pipeline
        """
        # Setup
        generator.generate_artifact(
            artifact_id="perf-artifact-004",
            analysis_id="analysis-perf-004",
            repository_id="repo-perf-004",
            analysis_type="LENS",
            orchestrator="LENSOrchestrator",
            data=sample_artifact_data,
        )

        # Measure activation performance
        start_time = time.perf_counter()

        result = generator.activate_artifact("perf-artifact-004")

        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000

        assert result is True
        assert duration_ms < 100.0, f"Activation took {duration_ms:.2f}ms (target: <100ms)"
        print(f"✅ Activation performance: {duration_ms:.2f}ms (target: <100ms, margin: {(100-duration_ms)/100*100:.1f}%)")

    def test_batch_artifact_operations_under_1s(
        self,
        generator: DashboardArtifactGenerator,
        sample_artifact_data: Dict[str, Any],
    ) -> None:
        """
        REFACTOR: Batch operations on 10 artifacts MUST complete in < 1s.

        Performance target: < 1000ms total for generating + activating 10 artifacts
        """
        start_time = time.perf_counter()

        # Generate 10 artifacts
        for i in range(10):
            generator.generate_artifact(
                artifact_id=f"perf-batch-{i}",
                analysis_id=f"analysis-batch-{i}",
                repository_id=f"repo-batch-{i}",
                analysis_type="LENS",
                orchestrator="LENSOrchestrator",
                data=sample_artifact_data,
            )
            generator.activate_artifact(f"perf-batch-{i}")

        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000

        assert duration_ms < 1000.0, f"Batch ops took {duration_ms:.2f}ms (target: <1000ms)"
        print(f"✅ Batch (10 artifacts) performance: {duration_ms:.2f}ms (target: <1000ms, margin: {(1000-duration_ms)/1000*100:.1f}%)")

    def test_artifact_list_performance_under_500ms(
        self,
        generator: DashboardArtifactGenerator,
        sample_artifact_data: Dict[str, Any],
    ) -> None:
        """
        REFACTOR: Listing 20 artifacts MUST complete in < 500ms.

        Performance target: < 500ms for listing active + archived artifacts
        """
        # Setup: create 20 artifacts, 10 active + 10 archived
        for i in range(20):
            generator.generate_artifact(
                artifact_id=f"perf-list-{i}",
                analysis_id=f"analysis-list-{i}",
                repository_id=f"repo-list-{i}",
                analysis_type="LENS",
                orchestrator="LENSOrchestrator",
                data=sample_artifact_data,
            )
            generator.activate_artifact(f"perf-list-{i}")

            if i >= 10:
                generator.archive_artifact(f"perf-list-{i}")

        # Measure listing performance
        start_time = time.perf_counter()

        active = generator.list_active_artifacts()
        archived = generator.list_archived_artifacts()

        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000

        assert len(active) == 10
        assert len(archived) == 10
        assert duration_ms < 500.0, f"List ops took {duration_ms:.2f}ms (target: <500ms)"
        print(f"✅ List (20 artifacts) performance: {duration_ms:.2f}ms (target: <500ms, margin: {(500-duration_ms)/500*100:.1f}%)")

    def test_export_json_performance_under_100ms(
        self,
        generator: DashboardArtifactGenerator,
        sample_artifact_data: Dict[str, Any],
    ) -> None:
        """
        REFACTOR: JSON export MUST complete in < 100ms.

        Performance target: < 100ms for serializing large artifact to JSON
        """
        # Setup
        generator.generate_artifact(
            artifact_id="perf-export-json",
            analysis_id="analysis-export-json",
            repository_id="repo-export-json",
            analysis_type="LENS",
            orchestrator="LENSOrchestrator",
            data=sample_artifact_data,
        )

        # Measure JSON export
        start_time = time.perf_counter()

        json_export = generator.export_as_json("perf-export-json")

        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000

        assert json_export is not None
        assert duration_ms < 100.0, f"JSON export took {duration_ms:.2f}ms (target: <100ms)"
        print(f"✅ JSON export performance: {duration_ms:.2f}ms (target: <100ms, margin: {(100-duration_ms)/100*100:.1f}%)")

    def test_export_yaml_performance_under_100ms(
        self,
        generator: DashboardArtifactGenerator,
        sample_artifact_data: Dict[str, Any],
    ) -> None:
        """
        REFACTOR: YAML export MUST complete in < 100ms.

        Performance target: < 100ms for serializing large artifact to YAML
        """
        # Setup
        generator.generate_artifact(
            artifact_id="perf-export-yaml",
            analysis_id="analysis-export-yaml",
            repository_id="repo-export-yaml",
            analysis_type="LENS",
            orchestrator="LENSOrchestrator",
            data=sample_artifact_data,
        )

        # Measure YAML export
        start_time = time.perf_counter()

        yaml_export = generator.export_as_yaml("perf-export-yaml")

        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000

        assert yaml_export is not None
        assert duration_ms < 100.0, f"YAML export took {duration_ms:.2f}ms (target: <100ms)"
        print(f"✅ YAML export performance: {duration_ms:.2f}ms (target: <100ms, margin: {(100-duration_ms)/100*100:.1f}%)")

    def test_artifact_metadata_efficiency(
        self,
        generator: DashboardArtifactGenerator,
        sample_artifact_data: Dict[str, Any],
        temp_cortex_brain: Path,
    ) -> None:
        """
        REFACTOR: Individual artifact files MUST be < 500KB.

        Performance target: < 500KB per artifact file (on disk)
        Validates efficient storage with large data payloads
        """
        # Setup
        generator.generate_artifact(
            artifact_id="perf-size",
            analysis_id="analysis-size",
            repository_id="repo-size",
            analysis_type="LENS",
            orchestrator="LENSOrchestrator",
            data=sample_artifact_data,
        )
        generator.activate_artifact("perf-size")

        # Check file size
        artifact_path = temp_cortex_brain / "dashboards" / "active" / "perf-size.yaml"
        file_size_kb = artifact_path.stat().st_size / 1024

        assert file_size_kb < 500.0, f"Artifact file is {file_size_kb:.2f}KB (target: <500KB)"
        print(f"✅ Artifact file size: {file_size_kb:.2f}KB (target: <500KB)")

    def test_archive_batch_performance_under_500ms(
        self,
        generator: DashboardArtifactGenerator,
        sample_artifact_data: Dict[str, Any],
    ) -> None:
        """
        REFACTOR: Archiving 10 artifacts MUST complete in < 500ms.

        Performance target: < 500ms for archiving batch of 10
        """
        # Setup: create 10 active artifacts
        for i in range(10):
            generator.generate_artifact(
                artifact_id=f"perf-archive-{i}",
                analysis_id=f"analysis-archive-{i}",
                repository_id=f"repo-archive-{i}",
                analysis_type="LENS",
                orchestrator="LENSOrchestrator",
                data=sample_artifact_data,
            )
            generator.activate_artifact(f"perf-archive-{i}")

        # Measure archival performance
        start_time = time.perf_counter()

        for i in range(10):
            generator.archive_artifact(f"perf-archive-{i}")

        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000

        assert duration_ms < 500.0, f"Archive batch took {duration_ms:.2f}ms (target: <500ms)"
        print(f"✅ Archive batch (10 artifacts) performance: {duration_ms:.2f}ms (target: <500ms, margin: {(500-duration_ms)/500*100:.1f}%)")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# AC_COMPLETE: AC-ENH087-T5-S4-REFACTOR-001 ✅ 10 performance tests for DashboardArtifactGenerator
