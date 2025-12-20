"""
Tests for PlanningArtifactsScanner, PlanningMigrationEngine, and CLI - TDD RED Phase

Tests scanning, migration, and CLI functionality for planning artifacts reorganization.

Author: GitHub Copilot
Created: 2025-12-14
"""

import pytest
from pathlib import Path
import tempfile
import shutil

# Imports will fail initially (RED phase) - expected
from src.workflows.planning_artifacts_scanner import (
    PlanningArtifactsScanner,
    PlanDiscovery,
    PlanMetadata,
    ArtifactType
)
from src.workflows.planning_migration_engine import (
    PlanningMigrationEngine,
    MigrationResult,
    MigrationReport,
    ValidationResult
)


class TestPlanningArtifactsScanner:
    """Test PlanningArtifactsScanner functionality."""
    
    def test_scan_directory_finds_planning_files(self, tmp_path):
        """Test scanner finds planning files in directory."""
        # Create test files
        planning_dir = tmp_path / "planning" / "features" / "active"
        planning_dir.mkdir(parents=True)
        
        (planning_dir / "PLAN-2025-12-01-feature-a.yaml").write_text("---\nplan_id: test")
        (planning_dir / "PLAN-2025-12-02-feature-b.md").write_text("# Plan B")
        (planning_dir / "random-file.txt").write_text("not a plan")
        
        scanner = PlanningArtifactsScanner()
        discoveries = scanner.scan_directory(planning_dir)
        
        assert len(discoveries) == 2  # Only planning files
        assert all(d.file_path.name.startswith("PLAN-") for d in discoveries)
    
    def test_classify_artifact_type_master_plan(self, tmp_path):
        """Test classifying master plan files."""
        plan_file = tmp_path / "PLAN-2025-12-01-test.yaml"
        plan_file.write_text("---\nmetadata:\n  plan_id: test\nphases:\n  - phase_number: 1")
        
        scanner = PlanningArtifactsScanner()
        artifact_type = scanner.classify_artifact_type(plan_file)
        
        assert artifact_type == ArtifactType.MASTER_PLAN
    
    def test_classify_artifact_type_sub_plan(self, tmp_path):
        """Test classifying sub-plan files."""
        sub_plan = tmp_path / "PLAN-2025-12-01-test-phase-1.md"
        sub_plan.write_text("# Phase 1: Implementation")
        
        scanner = PlanningArtifactsScanner()
        artifact_type = scanner.classify_artifact_type(sub_plan)
        
        assert artifact_type == ArtifactType.SUB_PLAN
    
    def test_extract_plan_metadata(self, tmp_path):
        """Test extracting metadata from plan file."""
        plan_file = tmp_path / "PLAN-2025-12-01-test.yaml"
        content = """---
metadata:
  plan_id: "PLAN-2025-12-01-test-feature"
  title: "Test Feature"
  created_date: "2025-12-01"
  author: "Test User"
phases:
  - phase_number: 1
"""
        plan_file.write_text(content)
        
        scanner = PlanningArtifactsScanner()
        metadata = scanner.extract_plan_metadata(plan_file)
        
        assert metadata.plan_id == "PLAN-2025-12-01-test-feature"
        assert metadata.title == "Test Feature"
        assert metadata.created_date == "2025-12-01"
    
    def test_detect_plan_relationships(self, tmp_path):
        """Test detecting relationships between planning files."""
        planning_dir = tmp_path / "planning"
        planning_dir.mkdir()
        
        # Create master plan
        master = planning_dir / "PLAN-2025-12-01-test.yaml"
        master.write_text("plan_id: PLAN-2025-12-01-test\nphases: []")
        
        # Create sub-plans
        sub1 = planning_dir / "PLAN-2025-12-01-test-phase-1.md"
        sub1.write_text("# Phase 1\nPart of PLAN-2025-12-01-test")
        
        files = [master, sub1]
        
        scanner = PlanningArtifactsScanner()
        relationships = scanner.detect_plan_relationships(files)
        
        assert "PLAN-2025-12-01-test" in relationships
        assert len(relationships["PLAN-2025-12-01-test"]) >= 1


class TestPlanningMigrationEngine:
    """Test PlanningMigrationEngine functionality."""
    
    def test_init_with_dry_run_default(self, tmp_path):
        """Test engine initializes with dry_run=True by default."""
        engine = PlanningMigrationEngine(cortex_root=tmp_path)
        
        assert engine.dry_run is True
    
    def test_migrate_plan_creates_folder_structure(self, tmp_path):
        """Test migrating single plan creates folder structure."""
        # Setup source files
        source_dir = tmp_path / "source" / "active"
        source_dir.mkdir(parents=True)
        
        plan_file = source_dir / "PLAN-2025-12-01-test.yaml"
        plan_file.write_text("metadata:\n  plan_id: PLAN-2025-12-01-test")
        
        # Setup cortex structure
        cortex_root = tmp_path / "cortex"
        (cortex_root / "cortex-brain").mkdir(parents=True)
        
        engine = PlanningMigrationEngine(cortex_root=cortex_root, dry_run=False)
        
        result = engine.migrate_plan("PLAN-2025-12-01-test", [plan_file])
        
        assert result.success is True
        assert result.files_moved > 0
        # Verify folder structure created
        plan_folder = cortex_root / "cortex-brain" / "documents" / "planning" / "features" / "active" / "PLAN-2025-12-01-test"
        assert plan_folder.exists()
    
    def test_migrate_plan_dry_run_no_changes(self, tmp_path):
        """Test dry-run mode makes no actual changes."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        
        plan_file = source_dir / "PLAN-2025-12-01-test.yaml"
        plan_file.write_text("metadata:\n  plan_id: test")
        
        cortex_root = tmp_path / "cortex"
        (cortex_root / "cortex-brain").mkdir(parents=True)
        
        engine = PlanningMigrationEngine(cortex_root=cortex_root, dry_run=True)
        
        result = engine.migrate_plan("PLAN-2025-12-01-test", [plan_file])
        
        # Dry run reports what would happen but doesn't move files
        assert result.success is True
        assert plan_file.exists()  # Original still exists
    
    def test_migrate_all_processes_multiple_plans(self, tmp_path):
        """Test migrating all plans processes multiple plans."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        
        # Create multiple plans
        for i in range(3):
            plan_file = source_dir / f"PLAN-2025-12-0{i+1}-test-{i}.yaml"
            plan_file.write_text(f"metadata:\n  plan_id: PLAN-2025-12-0{i+1}-test-{i}")
        
        cortex_root = tmp_path / "cortex"
        (cortex_root / "cortex-brain").mkdir(parents=True)
        
        engine = PlanningMigrationEngine(cortex_root=cortex_root, dry_run=False)
        
        report = engine.migrate_all(source_dir)
        
        assert report.total_plans >= 3
        assert report.successful_migrations >= 0
    
    def test_validate_migration_checks_completeness(self, tmp_path):
        """Test validation verifies migration completeness."""
        cortex_root = tmp_path / "cortex"
        (cortex_root / "cortex-brain").mkdir(parents=True)
        
        engine = PlanningMigrationEngine(cortex_root=cortex_root)
        
        # Create migrated structure
        from src.workflows.plan_folder_manager import PlanFolderManager
        folder_mgr = PlanFolderManager(cortex_root)
        folder_mgr.create_plan_structure("PLAN-2025-12-01-test")
        
        validation = engine.validate_migration("PLAN-2025-12-01-test")
        
        assert isinstance(validation, ValidationResult)
        assert validation.plan_id == "PLAN-2025-12-01-test"
    
    def test_handles_orphaned_files(self, tmp_path):
        """Test engine handles orphaned files gracefully."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        
        # Create orphaned file (no clear plan association)
        orphan = source_dir / "random-notes.md"
        orphan.write_text("Some random notes")
        
        cortex_root = tmp_path / "cortex"
        (cortex_root / "cortex-brain").mkdir(parents=True)
        
        engine = PlanningMigrationEngine(cortex_root=cortex_root, dry_run=False)
        
        report = engine.migrate_all(source_dir)
        
        # Should track orphaned files
        assert hasattr(report, 'orphaned_files')


class TestMigrationCLI:
    """Test migration CLI functionality."""
    
    def test_cli_dry_run_preview(self, tmp_path):
        """Test CLI dry-run generates preview."""
        from src.workflows.planning_migration_cli import MigrationCLI
        
        cli = MigrationCLI(cortex_root=tmp_path)
        
        # Should not raise exception
        preview = cli.dry_run()
        
        assert preview is not None
        assert 'plans_to_migrate' in preview or hasattr(preview, 'total_plans')
    
    def test_cli_execute_migration(self, tmp_path):
        """Test CLI executes migration."""
        from src.workflows.planning_migration_cli import MigrationCLI
        
        cortex_root = tmp_path / "cortex"
        (cortex_root / "cortex-brain").mkdir(parents=True)
        
        cli = MigrationCLI(cortex_root=cortex_root)
        
        # Should execute without error
        result = cli.execute(scope="active")
        
        assert result is not None
    
    def test_cli_validates_after_migration(self, tmp_path):
        """Test CLI validates migration results."""
        from src.workflows.planning_migration_cli import MigrationCLI
        
        cortex_root = tmp_path / "cortex"
        (cortex_root / "cortex-brain").mkdir(parents=True)
        
        cli = MigrationCLI(cortex_root=cortex_root)
        
        validation = cli.validate()
        
        assert validation is not None


# Fixtures
@pytest.fixture
def sample_planning_files(tmp_path):
    """Create sample planning files for testing."""
    planning_dir = tmp_path / "planning" / "features" / "active"
    planning_dir.mkdir(parents=True)
    
    # Master plan
    master = planning_dir / "PLAN-2025-12-01-feature.yaml"
    master.write_text("""---
metadata:
  plan_id: "PLAN-2025-12-01-feature"
  title: "Test Feature"
  created_date: "2025-12-01"
phases:
  - phase_number: 1
    name: "Implementation"
""")
    
    # Sub-plan
    sub = planning_dir / "PLAN-2025-12-01-feature-phase-1.md"
    sub.write_text("# Phase 1: Implementation\nPart of PLAN-2025-12-01-feature")
    
    # Tracker
    tracker = planning_dir / "PLAN-2025-12-01-feature-tracker.md"
    tracker.write_text("# Feature Tracker\nFor PLAN-2025-12-01-feature")
    
    return {
        'dir': planning_dir,
        'master': master,
        'sub': sub,
        'tracker': tracker
    }
