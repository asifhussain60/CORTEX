"""
Tests for PlanningArtifactsScanner - TDD RED Phase

Tests artifact scanning, relationship detection, and metadata extraction.

Author: GitHub Copilot
Created: 2025-12-14
"""

import pytest
from pathlib import Path
from datetime import datetime

from src.workflows.planning_artifacts_scanner import (
    PlanningArtifactsScanner,
    ArtifactType,
    PlanMetadata,
    PlanDiscovery
)


@pytest.fixture
def scanner(tmp_path):
    """Fixture for PlanningArtifactsScanner with temp directory."""
    return PlanningArtifactsScanner(planning_directory=tmp_path)


class TestPlanningArtifactsScanner:
    """Test basic scanner initialization and directory scanning."""
    
    def test_scanner_initialization(self, tmp_path):
        """Test scanner can be initialized."""
        scanner = PlanningArtifactsScanner(planning_directory=tmp_path)
        assert scanner is not None
        assert scanner.planning_directory == tmp_path
    
    def test_scan_empty_directory(self, scanner):
        """Test scanning empty directory returns empty discovery."""
        results = scanner.scan_directory()
        
        assert isinstance(results, PlanDiscovery)
        assert len(results.all_artifacts) == 0
    
    def test_scan_directory_finds_yaml_plans(self, tmp_path):
        """Test scanner finds YAML plan files."""
        # Create test plan files
        (tmp_path / "PLAN-2025-12-14-test-feature.yaml").write_text("""
plan_id: "PLAN-2025-12-14-test-feature"
title: "Test Feature"
""")
        
        scanner = PlanningArtifactsScanner(planning_directory=tmp_path)
        results = scanner.scan_directory()
        
        assert len(results.all_artifacts) == 1
        assert results.all_artifacts[0].plan_id == "PLAN-2025-12-14-test-feature"
    
    def test_scan_directory_finds_md_plans(self, tmp_path):
        """Test scanner finds Markdown plan files."""
        (tmp_path / "PLAN-2025-12-14-test.md").write_text("# Test Plan")
        
        scanner = PlanningArtifactsScanner(planning_directory=tmp_path)
        results = scanner.scan_directory()
        
        assert len(results.all_artifacts) == 1
    
    def test_scan_directory_recursive(self, tmp_path):
        """Test scanner searches recursively."""
        subdir = tmp_path / "active"
        subdir.mkdir()
        (subdir / "PLAN-2025-12-14-test.yaml").write_text("plan_id: test")
        
        scanner = PlanningArtifactsScanner(planning_directory=tmp_path)
        results = scanner.scan_directory()
        
        assert len(results.all_artifacts) == 1


class TestArtifactClassification:
    """Test artifact type classification."""
    
    def test_classify_master_plan_yaml(self, tmp_path):
        """Test master plan YAML classification."""
        scanner = PlanningArtifactsScanner(planning_directory=tmp_path)
        
        artifact_type = scanner.classify_artifact_type(
            Path("PLAN-2025-12-14-master-plan-feature.yaml"),
            {"plan_id": "test"}
        )
        
        assert artifact_type == ArtifactType.MASTER_PLAN
    
    def test_classify_master_plan_md(self, tmp_path):
        """Test master plan MD classification."""
        scanner = PlanningArtifactsScanner(planning_directory=tmp_path)
        
        artifact_type = scanner.classify_artifact_type(
            Path("PLAN-2025-12-14-master-plan-feature.md"),
            {"plan_id": "test"}
        )
        
        assert artifact_type == ArtifactType.MASTER_PLAN
    
    def test_classify_sub_plan(self, tmp_path):
        """Test sub-plan classification."""
        scanner = PlanningArtifactsScanner(planning_directory=tmp_path)
        
        artifact_type = scanner.classify_artifact_type(
            Path("PLAN-2025-12-14-feature-sub-plan-1.md"),
            {}
        )
        
        assert artifact_type == ArtifactType.SUB_PLAN
    
    def test_classify_tracker(self, tmp_path):
        """Test tracker classification."""
        scanner = PlanningArtifactsScanner(planning_directory=tmp_path)
        
        artifact_type = scanner.classify_artifact_type(
            Path("PLAN-2025-12-14-feature-tracker.md"),
            {}
        )
        
        assert artifact_type == ArtifactType.TRACKER
    
    def test_classify_report(self, tmp_path):
        """Test report classification."""
        scanner = PlanningArtifactsScanner(planning_directory=tmp_path)
        
        artifact_type = scanner.classify_artifact_type(
            Path("PLAN-2025-12-14-status-report.md"),
            {}
        )
        
        assert artifact_type == ArtifactType.REPORT
    
    def test_classify_unknown(self, tmp_path):
        """Test unknown file classification."""
        scanner = PlanningArtifactsScanner(planning_directory=tmp_path)
        
        artifact_type = scanner.classify_artifact_type(
            Path("random-file.md"),
            {}
        )
        
        assert artifact_type == ArtifactType.UNKNOWN


class TestMetadataExtraction:
    """Test plan metadata extraction."""
    
    def test_extract_metadata_from_yaml(self, tmp_path):
        """Test extracting metadata from YAML plan."""
        plan_file = tmp_path / "PLAN-2025-12-14-test.yaml"
        plan_file.write_text("""
plan_id: "PLAN-2025-12-14-test-feature"
title: "Test Feature Implementation"
created_date: "2025-12-14"
""")
        
        scanner = PlanningArtifactsScanner(planning_directory=tmp_path)
        metadata = scanner.extract_plan_metadata(plan_file)
        
        assert metadata.plan_id == "PLAN-2025-12-14-test-feature"
        assert metadata.title == "Test Feature Implementation"
        assert metadata.created_date == "2025-12-14"
    
    def test_extract_metadata_from_md(self, tmp_path):
        """Test extracting metadata from Markdown plan."""
        plan_file = tmp_path / "PLAN-2025-12-14-test.md"
        plan_file.write_text("""---
plan_id: PLAN-2025-12-14-test-feature
created: 2025-12-14
---
# Test Feature
""")
        
        scanner = PlanningArtifactsScanner(planning_directory=tmp_path)
        metadata = scanner.extract_plan_metadata(plan_file)
        
        assert metadata.plan_id == "PLAN-2025-12-14-test-feature"
        assert metadata.title == "Test Feature"
    
    def test_extract_metadata_handles_missing_fields(self, tmp_path):
        """Test metadata extraction with missing fields."""
        plan_file = tmp_path / "PLAN-2025-12-14-test.yaml"
        plan_file.write_text("plan_id: test")
        
        scanner = PlanningArtifactsScanner(planning_directory=tmp_path)
        metadata = scanner.extract_plan_metadata(plan_file)
        
        assert metadata.plan_id == "test"
        assert metadata.title is None  # Missing fields should be None


class TestRelationshipDetection:
    """Test plan relationship detection."""
    
    def test_detect_relationships_finds_master_and_subs(self, tmp_path):
        """Test detecting master plan with sub-plans."""
        # Create master plan
        master = tmp_path / "PLAN-2025-12-14-master-plan-feature.yaml"
        master.write_text("""
plan_id: "PLAN-2025-12-14-feature"
title: "Feature Plan"
""")
        
        # Create sub-plans
        sub1 = tmp_path / "PLAN-2025-12-14-feature-sub-plan-1.md"
        sub1.write_text("""---
parent_plan_id: PLAN-2025-12-14-feature
---
# Phase 1""")
        
        scanner = PlanningArtifactsScanner(planning_directory=tmp_path)
        discovery = scanner.scan_directory()
        
        assert "PLAN-2025-12-14-feature" in discovery.plan_relationships
        assert len(discovery.plan_relationships["PLAN-2025-12-14-feature"]) >= 1
    
    def test_detect_relationships_finds_orphaned_files(self, tmp_path):
        """Test detecting orphaned files (no master plan)."""
        orphan = tmp_path / "PLAN-2025-12-14-feature-sub-plan-1.md"
        orphan.write_text("""---
parent_plan_id: nonexistent-plan
---
# Phase 1""")
        
        scanner = PlanningArtifactsScanner(planning_directory=tmp_path)
        discovery = scanner.scan_directory()
        
        # Should detect orphaned artifact
        assert len(discovery.orphaned_artifacts) >= 1
    
    def test_detect_relationships_groups_by_plan_id(self, tmp_path):
        """Test that files are grouped by plan ID."""
        # Create multiple master plans
        plan1 = tmp_path / "PLAN-2025-12-14-master-plan-feature-a.yaml"
        plan1.write_text("plan_id: feature-a")
        
        plan2 = tmp_path / "PLAN-2025-12-14-master-plan-feature-b.yaml"
        plan2.write_text("plan_id: feature-b")
        
        scanner = PlanningArtifactsScanner(planning_directory=tmp_path)
        discovery = scanner.scan_directory()
        
        # Should have 2 master plans
        assert len(discovery.master_plans) == 2


class TestPlanDiscovery:
    """Test PlanDiscovery result object."""
    
    def test_plan_discovery_creation(self):
        """Test creating PlanDiscovery object."""
        discovery = PlanDiscovery()
        
        assert isinstance(discovery.all_artifacts, list)
        assert isinstance(discovery.master_plans, list)
        assert isinstance(discovery.sub_plans, list)
        assert isinstance(discovery.trackers, list)
        assert isinstance(discovery.reports, list)
        assert isinstance(discovery.unknown, list)
        assert isinstance(discovery.plan_relationships, dict)
        assert isinstance(discovery.orphaned_artifacts, list)


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_scan_nonexistent_directory(self):
        """Test scanning nonexistent directory."""
        scanner = PlanningArtifactsScanner(planning_directory=Path("/nonexistent/path"))
        
        # Should return empty discovery, not raise
        discovery = scanner.scan_directory()
        assert len(discovery.all_artifacts) == 0
    
    def test_extract_metadata_from_corrupted_yaml(self, tmp_path):
        """Test handling corrupted YAML file."""
        plan_file = tmp_path / "corrupted.yaml"
        plan_file.write_text("metadata: [invalid yaml")
        
        scanner = PlanningArtifactsScanner(planning_directory=tmp_path)
        metadata = scanner.extract_plan_metadata(plan_file)
        
        # Should handle gracefully
        assert metadata is not None
    
    def test_classify_file_without_extension(self, tmp_path):
        """Test classifying file without extension."""
        scanner = PlanningArtifactsScanner(planning_directory=tmp_path)
        
        artifact_type = scanner.classify_artifact_type(
            Path("PLAN-2025-12-14-feature"),
            {}
        )
        
        assert artifact_type == ArtifactType.UNKNOWN
    
    def test_scan_directory_ignores_non_planning_files(self, tmp_path):
        """Test scanner ignores non-planning files."""
        (tmp_path / "README.md").write_text("# README")
        (tmp_path / "config.json").write_text("{}")
        (tmp_path / "PLAN-2025-12-14-master-plan-test.yaml").write_text("plan_id: test")
        
        scanner = PlanningArtifactsScanner(planning_directory=tmp_path)
        results = scanner.scan_directory()
        
        # Should find plan file plus potentially README.md (it's still .md)
        assert len(results.master_plans) == 1


@pytest.fixture
def sample_plans_directory(tmp_path):
    """Create sample directory structure with multiple plans."""
    # Active plans
    active = tmp_path / "active"
    active.mkdir()
    
    (active / "PLAN-2025-12-14-master-plan-feature-a.yaml").write_text("""
plan_id: "PLAN-2025-12-14-feature-a"
title: "Feature A"
""")
    
    (active / "PLAN-2025-12-14-feature-a-sub-plan-1.md").write_text("""---
parent_plan_id: PLAN-2025-12-14-feature-a
---
# Phase 1""")
    
    # Completed plans
    completed = tmp_path / "completed"
    completed.mkdir()
    
    (completed / "PLAN-2025-12-13-master-plan-feature-b.yaml").write_text("""
plan_id: "PLAN-2025-12-13-feature-b"
title: "Feature B"
""")
    
    return tmp_path


class TestIntegration:
    """Integration tests with realistic directory structures."""
    
    def test_scan_realistic_structure(self, sample_plans_directory):
        """Test scanning realistic directory structure."""
        scanner = PlanningArtifactsScanner(planning_directory=sample_plans_directory)
        discovery = scanner.scan_directory()
        
        # Should find both master plans
        assert len(discovery.master_plans) == 2
        
        plan_ids = [p.plan_id for p in discovery.master_plans]
        assert "PLAN-2025-12-14-feature-a" in plan_ids
        assert "PLAN-2025-12-13-feature-b" in plan_ids
    
    def test_full_workflow_scan_classify_extract(self, sample_plans_directory):
        """Test complete workflow: scan → classify → extract."""
        scanner = PlanningArtifactsScanner(planning_directory=sample_plans_directory)
        
        # Step 1: Scan
        discovery = scanner.scan_directory()
        
        # Step 2: Verify classification
        assert len(discovery.master_plans) == 2
        assert len(discovery.sub_plans) >= 1
        
        # Step 3: Verify metadata extraction
        for artifact in discovery.all_artifacts:
            assert artifact.file_path is not None
            assert artifact.artifact_type is not None
