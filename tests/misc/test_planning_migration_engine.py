"""
Tests for PlanningMigrationEngine - TDD RED Phase

Tests migration from flat structure to hierarchical folders.

Author: GitHub Copilot
Created: 2025-12-14
"""

import pytest
from pathlib import Path
from datetime import datetime

from src.workflows.planning_migration_engine import (
    PlanningMigrationEngine,
    MigrationResult,
    MigrationStatus
)
from src.workflows.planning_artifacts_scanner import (
    PlanningArtifactsScanner,
    PlanDiscovery
)


@pytest.fixture
def migration_engine(tmp_path):
    """Fixture for PlanningMigrationEngine with temp directories."""
    source_dir = tmp_path / "source"
    target_dir = tmp_path / "target"
    source_dir.mkdir()
    target_dir.mkdir()
    return PlanningMigrationEngine(
        source_directory=source_dir,
        target_directory=target_dir
    )


@pytest.fixture
def sample_flat_structure(tmp_path):
    """Create sample flat planning structure for migration testing."""
    planning_dir = tmp_path / "planning"
    planning_dir.mkdir()
    
    # Master plan YAML
    (planning_dir / "PLAN-2025-12-14-master-plan-feature.yaml").write_text("""
plan_id: "PLAN-2025-12-14-feature"
title: "Feature Implementation"
created_date: "2025-12-14"
status: "active"
""")
    
    # Sub-plans
    (planning_dir / "PLAN-2025-12-14-feature-sub-plan-phase-1.md").write_text("""---
parent_plan_id: PLAN-2025-12-14-feature
title: "Phase 1: Foundation"
---
# Phase 1
""")
    
    (planning_dir / "PLAN-2025-12-14-feature-sub-plan-phase-2.md").write_text("""---
parent_plan_id: PLAN-2025-12-14-feature
title: "Phase 2: Implementation"
---
# Phase 2
""")
    
    # Tracker
    (planning_dir / "PLAN-2025-12-14-feature-tracker.md").write_text("""---
plan_id: PLAN-2025-12-14-feature
---
# Visual Tracker
""")
    
    # Report
    (planning_dir / "PLAN-2025-12-14-feature-status-report.md").write_text("""---
plan_id: PLAN-2025-12-14-feature
---
# Status Report
""")
    
    return planning_dir


class TestMigrationEngineInit:
    """Test migration engine initialization."""
    
    def test_engine_initialization(self, migration_engine):
        """Test engine can be initialized."""
        assert migration_engine is not None
        assert migration_engine.source_directory.exists()
        assert migration_engine.target_directory.exists()
    
    def test_engine_validates_directories(self, tmp_path):
        """Test engine validates directory existence."""
        nonexistent = tmp_path / "nonexistent"
        
        with pytest.raises(ValueError):
            PlanningMigrationEngine(
                source_directory=nonexistent,
                target_directory=tmp_path
            )


class TestMigrationDiscovery:
    """Test migration discovery phase."""
    
    def test_discover_plans_to_migrate(self, migration_engine, sample_flat_structure):
        """Test discovering plans in flat structure."""
        migration_engine.source_directory = sample_flat_structure
        
        discovery = migration_engine.discover_plans()
        
        assert isinstance(discovery, PlanDiscovery)
        assert len(discovery.master_plans) >= 1
        assert len(discovery.sub_plans) >= 2
    
    def test_discovery_handles_empty_directory(self, migration_engine):
        """Test discovery handles empty source directory."""
        discovery = migration_engine.discover_plans()
        
        assert isinstance(discovery, PlanDiscovery)
        assert len(discovery.all_artifacts) == 0


class TestMigrationExecution:
    """Test migration execution."""
    
    def test_migrate_single_plan(self, migration_engine, sample_flat_structure):
        """Test migrating a single plan with all artifacts."""
        migration_engine.source_directory = sample_flat_structure
        
        result = migration_engine.migrate_plan("PLAN-2025-12-14-feature")
        
        assert isinstance(result, MigrationResult)
        assert result.status == MigrationStatus.SUCCESS
        assert result.plan_id == "PLAN-2025-12-14-feature"
        
        # Verify folder structure created
        plan_folder = migration_engine.target_directory / "active" / "PLAN-2025-12-14-feature"
        assert plan_folder.exists()
        assert (plan_folder / "master-plan.yaml").exists()
        assert (plan_folder / "sub-plans").exists()
        assert len(list((plan_folder / "sub-plans").glob("*.md"))) >= 2
    
    def test_migrate_all_plans(self, migration_engine, sample_flat_structure):
        """Test migrating all plans at once."""
        migration_engine.source_directory = sample_flat_structure
        
        results = migration_engine.migrate_all()
        
        assert isinstance(results, list)
        assert len(results) >= 1
        assert all(isinstance(r, MigrationResult) for r in results)
        
        # All should succeed
        assert all(r.status == MigrationStatus.SUCCESS for r in results)
    
    def test_migration_preserves_content(self, migration_engine, sample_flat_structure):
        """Test migration preserves file content."""
        migration_engine.source_directory = sample_flat_structure
        
        # Get original content
        original_file = sample_flat_structure / "PLAN-2025-12-14-master-plan-feature.yaml"
        original_content = original_file.read_text()
        
        migration_engine.migrate_plan("PLAN-2025-12-14-feature")
        
        # Check migrated content
        migrated_file = migration_engine.target_directory / "active" / "PLAN-2025-12-14-feature" / "master-plan.yaml"
        migrated_content = migrated_file.read_text()
        
        assert original_content.strip() == migrated_content.strip()
    
    def test_migration_creates_readme(self, migration_engine, sample_flat_structure):
        """Test migration creates README with file index."""
        migration_engine.source_directory = sample_flat_structure
        
        migration_engine.migrate_plan("PLAN-2025-12-14-feature")
        
        readme_file = migration_engine.target_directory / "active" / "PLAN-2025-12-14-feature" / "README.md"
        assert readme_file.exists()
        
        content = readme_file.read_text()
        assert "PLAN-2025-12-14-feature" in content
        assert "File Index" in content


class TestMigrationRollback:
    """Test migration rollback capabilities."""
    
    def test_rollback_single_migration(self, migration_engine, sample_flat_structure):
        """Test rolling back a single plan migration."""
        migration_engine.source_directory = sample_flat_structure
        
        # Migrate
        result = migration_engine.migrate_plan("PLAN-2025-12-14-feature")
        assert result.status == MigrationStatus.SUCCESS
        
        # Rollback
        rollback_result = migration_engine.rollback_migration("PLAN-2025-12-14-feature")
        
        assert rollback_result.status == MigrationStatus.SUCCESS
        
        # Verify folder removed
        plan_folder = migration_engine.target_directory / "active" / "PLAN-2025-12-14-feature"
        assert not plan_folder.exists()
    
    def test_rollback_all_migrations(self, migration_engine, sample_flat_structure):
        """Test rolling back all migrations."""
        migration_engine.source_directory = sample_flat_structure
        
        # Migrate all
        migration_engine.migrate_all()
        
        # Rollback all
        rollback_results = migration_engine.rollback_all()
        
        assert isinstance(rollback_results, list)
        assert all(r.status == MigrationStatus.SUCCESS for r in rollback_results)


class TestMigrationStatus:
    """Test migration status tracking."""
    
    def test_get_migration_status(self, migration_engine, sample_flat_structure):
        """Test getting migration status."""
        migration_engine.source_directory = sample_flat_structure
        
        # Before migration
        status_before = migration_engine.get_migration_status("PLAN-2025-12-14-feature")
        assert status_before == MigrationStatus.NOT_MIGRATED
        
        # After migration
        migration_engine.migrate_plan("PLAN-2025-12-14-feature")
        status_after = migration_engine.get_migration_status("PLAN-2025-12-14-feature")
        assert status_after == MigrationStatus.SUCCESS
    
    def test_list_migrated_plans(self, migration_engine, sample_flat_structure):
        """Test listing all migrated plans."""
        migration_engine.source_directory = sample_flat_structure
        
        migration_engine.migrate_all()
        
        migrated_plans = migration_engine.list_migrated_plans()
        
        assert isinstance(migrated_plans, list)
        assert len(migrated_plans) >= 1
        assert "PLAN-2025-12-14-feature" in migrated_plans


class TestMigrationValidation:
    """Test migration validation."""
    
    def test_validate_migration(self, migration_engine, sample_flat_structure):
        """Test validating a migration."""
        migration_engine.source_directory = sample_flat_structure
        
        migration_engine.migrate_plan("PLAN-2025-12-14-feature")
        
        is_valid = migration_engine.validate_migration("PLAN-2025-12-14-feature")
        
        assert is_valid is True
    
    def test_validate_all_migrations(self, migration_engine, sample_flat_structure):
        """Test validating all migrations."""
        migration_engine.source_directory = sample_flat_structure
        
        migration_engine.migrate_all()
        
        validation_results = migration_engine.validate_all_migrations()
        
        assert isinstance(validation_results, dict)
        assert all(v is True for v in validation_results.values())


class TestMigrationEdgeCases:
    """Test edge cases and error handling."""
    
    def test_migrate_nonexistent_plan(self, migration_engine):
        """Test migrating nonexistent plan."""
        result = migration_engine.migrate_plan("nonexistent-plan")
        
        assert result.status == MigrationStatus.FAILED
        assert "not found" in result.message.lower()
    
    def test_migrate_orphaned_sub_plan(self, tmp_path):
        """Test migrating orphaned sub-plan (no master)."""
        source_dir = tmp_path / "orphan_source"
        target_dir = tmp_path / "orphan_target"
        source_dir.mkdir()
        target_dir.mkdir()
        
        # Orphaned sub-plan
        (source_dir / "PLAN-2025-12-14-orphan-sub-plan.md").write_text("""---
parent_plan_id: nonexistent-plan
---
# Orphan
""")
        
        migration_engine = PlanningMigrationEngine(
            source_directory=source_dir,
            target_directory=target_dir
        )
        
        result = migration_engine.migrate_plan("nonexistent-plan")
        
        # Should handle gracefully
        assert result.status in [MigrationStatus.FAILED, MigrationStatus.PARTIAL]
    
    def test_migrate_duplicate_plan(self, migration_engine, sample_flat_structure):
        """Test migrating same plan twice."""
        migration_engine.source_directory = sample_flat_structure
        
        # First migration
        result1 = migration_engine.migrate_plan("PLAN-2025-12-14-feature")
        assert result1.status == MigrationStatus.SUCCESS
        
        # Second migration (should skip or update)
        result2 = migration_engine.migrate_plan("PLAN-2025-12-14-feature")
        assert result2.status in [MigrationStatus.SUCCESS, MigrationStatus.SKIPPED]


class TestMigrationIntegration:
    """Integration tests for full migration workflow."""
    
    def test_full_migration_workflow(self, migration_engine, sample_flat_structure):
        """Test complete migration workflow."""
        migration_engine.source_directory = sample_flat_structure
        
        # 1. Discover
        discovery = migration_engine.discover_plans()
        assert len(discovery.master_plans) >= 1
        
        # 2. Migrate
        results = migration_engine.migrate_all()
        assert all(r.status == MigrationStatus.SUCCESS for r in results)
        
        # 3. Validate
        validation_results = migration_engine.validate_all_migrations()
        assert all(v is True for v in validation_results.values())
        
        # 4. Check status
        migrated_plans = migration_engine.list_migrated_plans()
        assert len(migrated_plans) >= 1
    
    def test_migration_with_scanner_integration(self, migration_engine, sample_flat_structure):
        """Test migration engine works with scanner."""
        migration_engine.source_directory = sample_flat_structure
        
        # Use scanner to discover
        scanner = PlanningArtifactsScanner(planning_directory=sample_flat_structure)
        discovery = scanner.scan_directory()
        
        # Migrate discovered plans
        for master_plan in discovery.master_plans:
            result = migration_engine.migrate_plan(master_plan.plan_id)
            assert result.status == MigrationStatus.SUCCESS
