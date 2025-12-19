"""
Test Planning Document Organization - Phase 2 Implementation
RED Phase: Tests written before implementation

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import pytest
import shutil
from pathlib import Path
from datetime import datetime
import tempfile
import yaml

# Import the module we'll be testing (doesn't exist yet - RED phase)
from src.orchestrators.planning_document_migrator import PlanningDocumentMigrator


class TestPlanningDocumentMigration:
    """Test suite for planning document migration to status-based directories"""
    
    @pytest.fixture
    def temp_cortex_root(self, tmp_path):
        """Create temporary CORTEX directory structure"""
        cortex_root = tmp_path / "CORTEX"
        cortex_root.mkdir()
        
        # Create brain structure
        brain_path = cortex_root / "cortex-brain"
        brain_path.mkdir()
        
        planning_path = brain_path / "documents" / "planning"
        planning_path.mkdir(parents=True)
        
        # Create status directories
        (planning_path / "active").mkdir()
        (planning_path / "approved").mkdir()
        (planning_path / "completed").mkdir()
        (planning_path / "deprecated").mkdir()
        
        return cortex_root
    
    @pytest.fixture
    def sample_plans(self, temp_cortex_root):
        """Create sample planning documents with various statuses"""
        planning_path = temp_cortex_root / "cortex-brain" / "documents" / "planning"
        
        plans = []
        
        # Active plan (in-progress status)
        active_plan = planning_path / "PLAN-2025-11-28-active-feature.md"
        active_plan.write_text("""# CORTEX Feature Plan
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

## Status

**Status:** in-progress  
**Created:** 2025-11-28  
**Priority:** P1

## Overview

This is an active plan that should be moved to active/ directory.
""", encoding='utf-8')
        plans.append(active_plan)
        
        # Approved plan
        approved_plan = planning_path / "PLAN-2025-11-27-approved-feature.md"
        approved_plan.write_text("""# CORTEX Feature Plan
**Author:** Asif Hussain

---

## Status

**Status:** approved  
**Created:** 2025-11-27

## Overview

This plan has been approved.
""", encoding='utf-8')
        plans.append(approved_plan)
        
        # Completed plan
        completed_plan = planning_path / "PLAN-2025-11-26-completed-feature.md"
        completed_plan.write_text("""# CORTEX Feature Plan
**Author:** Asif Hussain

---

## Status

**Status:** completed  
**Created:** 2025-11-26  
**Completed:** 2025-11-28

## Overview

This plan is completed.
""", encoding='utf-8')
        plans.append(completed_plan)
        
        # Deprecated plan
        deprecated_plan = planning_path / "PLAN-2025-11-25-deprecated-feature.md"
        deprecated_plan.write_text("""# CORTEX Feature Plan

---

## Status

**Status:** deprecated  
**Reason:** Superseded by new approach

## Overview

This plan is no longer relevant.
""", encoding='utf-8')
        plans.append(deprecated_plan)
        
        # Plan without status (should default to active)
        no_status_plan = planning_path / "PLAN-2025-11-24-no-status.md"
        no_status_plan.write_text("""# CORTEX Feature Plan

## Overview

No status specified.
""", encoding='utf-8')
        plans.append(no_status_plan)
        
        return plans
    
    def test_migration_preserves_all_documents(self, temp_cortex_root, sample_plans):
        """Test that migration preserves all planning documents without data loss"""
        migrator = PlanningDocumentMigrator(str(temp_cortex_root))
        
        # Count original files
        planning_path = temp_cortex_root / "cortex-brain" / "documents" / "planning"
        original_count = len(list(planning_path.glob("PLAN-*.md")))
        
        assert original_count == 5, f"Expected 5 plans, found {original_count}"
        
        # Run migration
        result = migrator.migrate_documents(dry_run=False, create_backup=True)
        
        # Verify all documents were migrated
        assert result['success'] is True
        assert result['migrated_count'] == 5
        assert result['failed_count'] == 0
        
        # Verify backup was created
        assert result['backup_path'] is not None
        backup_path = Path(result['backup_path'])
        assert backup_path.exists()
        
        # Verify no documents left in root
        remaining = list(planning_path.glob("PLAN-*.md"))
        assert len(remaining) == 0, f"Found {len(remaining)} documents still in root"
        
        # Verify total count in subdirectories matches original
        total_migrated = (
            len(list((planning_path / "active").glob("*.md"))) +
            len(list((planning_path / "approved").glob("*.md"))) +
            len(list((planning_path / "completed").glob("*.md"))) +
            len(list((planning_path / "deprecated").glob("*.md")))
        )
        assert total_migrated == original_count
    
    def test_active_plans_in_active_directory(self, temp_cortex_root, sample_plans):
        """Test that in-progress plans are moved to active/ directory"""
        migrator = PlanningDocumentMigrator(str(temp_cortex_root))
        
        # Run migration
        result = migrator.migrate_documents(dry_run=False, create_backup=True)
        
        planning_path = temp_cortex_root / "cortex-brain" / "documents" / "planning"
        active_dir = planning_path / "active"
        
        # Find active plan (should be in active/)
        active_plans = list(active_dir.glob("PLAN-2025-11-28-active-feature.md"))
        assert len(active_plans) == 1, f"Expected 1 active plan, found {len(active_plans)}"
        
        # Verify plan without status also went to active/ (default)
        no_status_plans = list(active_dir.glob("PLAN-2025-11-24-no-status.md"))
        assert len(no_status_plans) == 1, "Plans without status should default to active/"
    
    def test_approved_plans_moved_correctly(self, temp_cortex_root, sample_plans):
        """Test that approved plans are moved to approved/ directory"""
        migrator = PlanningDocumentMigrator(str(temp_cortex_root))
        
        # Run migration
        result = migrator.migrate_documents(dry_run=False, create_backup=True)
        
        planning_path = temp_cortex_root / "cortex-brain" / "documents" / "planning"
        approved_dir = planning_path / "approved"
        
        # Find approved plan
        approved_plans = list(approved_dir.glob("PLAN-2025-11-27-approved-feature.md"))
        assert len(approved_plans) == 1
    
    def test_completed_plans_moved_correctly(self, temp_cortex_root, sample_plans):
        """Test that completed plans are moved to completed/ directory"""
        migrator = PlanningDocumentMigrator(str(temp_cortex_root))
        
        result = migrator.migrate_documents(dry_run=False, create_backup=True)
        
        planning_path = temp_cortex_root / "cortex-brain" / "documents" / "planning"
        completed_dir = planning_path / "completed"
        
        # Find completed plan
        completed_plans = list(completed_dir.glob("PLAN-2025-11-26-completed-feature.md"))
        assert len(completed_plans) == 1
    
    def test_deprecated_plans_moved_correctly(self, temp_cortex_root, sample_plans):
        """Test that deprecated plans are moved to deprecated/ directory"""
        migrator = PlanningDocumentMigrator(str(temp_cortex_root))
        
        result = migrator.migrate_documents(dry_run=False, create_backup=True)
        
        planning_path = temp_cortex_root / "cortex-brain" / "documents" / "planning"
        deprecated_dir = planning_path / "deprecated"
        
        # Find deprecated plan
        deprecated_plans = list(deprecated_dir.glob("PLAN-2025-11-25-deprecated-feature.md"))
        assert len(deprecated_plans) == 1
    
    def test_dry_run_does_not_move_files(self, temp_cortex_root, sample_plans):
        """Test that dry_run mode does not actually move files"""
        migrator = PlanningDocumentMigrator(str(temp_cortex_root))
        
        planning_path = temp_cortex_root / "cortex-brain" / "documents" / "planning"
        original_count = len(list(planning_path.glob("PLAN-*.md")))
        
        # Run dry run
        result = migrator.migrate_documents(dry_run=True, create_backup=False)
        
        # Verify report generated but files not moved
        assert result['success'] is True
        assert result['dry_run'] is True
        
        # Files should still be in root
        remaining_count = len(list(planning_path.glob("PLAN-*.md")))
        assert remaining_count == original_count
    
    def test_backup_can_be_restored(self, temp_cortex_root, sample_plans):
        """Test that backup can be used to restore original state"""
        migrator = PlanningDocumentMigrator(str(temp_cortex_root))
        
        planning_path = temp_cortex_root / "cortex-brain" / "documents" / "planning"
        
        # Get original checksums
        original_checksums = {}
        for plan in planning_path.glob("PLAN-*.md"):
            original_checksums[plan.name] = plan.read_text()
        
        # Run migration with backup
        result = migrator.migrate_documents(dry_run=False, create_backup=True)
        backup_path = Path(result['backup_path'])
        
        # Verify backup contains all files
        backed_up_files = list(backup_path.glob("PLAN-*.md"))
        assert len(backed_up_files) == len(original_checksums)
        
        # Verify backup content matches original
        for backup_file in backed_up_files:
            assert backup_file.read_text() == original_checksums[backup_file.name]
    
    def test_migration_handles_subdirectories_correctly(self, temp_cortex_root):
        """Test that existing subdirectories (ado/, features/, enhancements/) are preserved"""
        planning_path = temp_cortex_root / "cortex-brain" / "documents" / "planning"
        
        # Create subdirectories with plans
        ado_dir = planning_path / "ado"
        ado_dir.mkdir()
        ado_plan = ado_dir / "ADO-12345-feature.md"
        ado_plan.write_text("# ADO Plan\n\n**Status:** in-progress")
        
        features_dir = planning_path / "features"
        features_dir.mkdir()
        feature_plan = features_dir / "FEATURE-auth.md"
        feature_plan.write_text("# Feature Plan\n\n**Status:** approved")
        
        migrator = PlanningDocumentMigrator(str(temp_cortex_root))
        
        # Migration should NOT affect subdirectory plans
        result = migrator.migrate_documents(dry_run=False, create_backup=True)
        
        # Verify subdirectory plans are untouched
        assert ado_plan.exists()
        assert feature_plan.exists()
    
    def test_migration_reports_errors_for_unreadable_files(self, temp_cortex_root):
        """Test that migration gracefully handles files that cannot be read"""
        planning_path = temp_cortex_root / "cortex-brain" / "documents" / "planning"
        
        # Create a plan that will cause an error (simulate permission issue)
        bad_plan = planning_path / "PLAN-2025-11-28-bad.md"
        bad_plan.write_text("# Test")
        
        migrator = PlanningDocumentMigrator(str(temp_cortex_root))
        
        # Mock file read error
        original_detect = migrator._detect_plan_status
        def mock_detect(file_path):
            if "bad" in str(file_path):
                raise PermissionError("Cannot read file")
            return original_detect(file_path)
        
        migrator._detect_plan_status = mock_detect
        
        result = migrator.migrate_documents(dry_run=False, create_backup=True)
        
        # Should report error but continue
        assert result['failed_count'] > 0
        assert 'errors' in result
        assert len(result['errors']) > 0


class TestStatusDetection:
    """Test suite for plan status detection logic"""
    
    def test_detect_status_from_frontmatter(self):
        """Test status detection from markdown frontmatter"""
        content = """# Plan Title

**Status:** approved  
**Priority:** P1

## Overview
"""
        migrator = PlanningDocumentMigrator(".")
        status = migrator._detect_plan_status_from_content(content)
        assert status == "approved"
    
    def test_detect_status_case_insensitive(self):
        """Test that status detection is case-insensitive"""
        content = """
**STATUS:** COMPLETED  
"""
        migrator = PlanningDocumentMigrator(".")
        status = migrator._detect_plan_status_from_content(content)
        assert status == "completed"
    
    def test_default_status_when_not_found(self):
        """Test that default status is 'active' when status not found"""
        content = """# Plan Without Status

Just a plan with no status field.
"""
        migrator = PlanningDocumentMigrator(".")
        status = migrator._detect_plan_status_from_content(content)
        assert status == "active"
    
    def test_detect_status_with_various_formats(self):
        """Test status detection with different markdown formats"""
        formats = [
            ("**Status:** in-progress", "active"),  # in-progress maps to active
            ("Status: approved", "approved"),
            ("**Status**: completed", "completed"),
            ("status: deprecated", "deprecated"),
        ]
        
        migrator = PlanningDocumentMigrator(".")
        for content, expected in formats:
            status = migrator._detect_plan_status_from_content(content)
            assert status == expected


class TestMigrationValidation:
    """Test suite for migration validation checks"""
    
    def test_validation_detects_missing_files(self, tmp_path):
        """Test that validation detects if files went missing during migration"""
        # This will be implemented in the validator
        pass
    
    def test_validation_detects_content_corruption(self, tmp_path):
        """Test that validation detects content changes during migration"""
        # This will be implemented in the validator
        pass
    
    def test_validation_reports_summary(self, tmp_path):
        """Test that validation generates comprehensive summary report"""
        # This will be implemented in the validator
        pass
