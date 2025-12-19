# -*- coding: utf-8 -*-
"""
Tests for Plan Migration Utility (Phase 14)

Tests migration of existing plans to unified format with token tracking.
TDD: RED → GREEN → REFACTOR
"""

import pytest
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

from scripts.migrate_existing_plans import PlanMigrationUtility
from src.operations.modules.planning.unified_plan_generator import UnifiedPlanGenerator


class TestPlanMigrationUtility:
    """Test plan migration from old formats to unified format."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        shutil.rmtree(temp_path)
    
    @pytest.fixture
    def sample_old_format_plan(self, temp_dir):
        """Create sample plan in old format."""
        plan_content = """# CORTEX Lens v3.0 - Master Plan

**Version:** 3.0.0
**Date:** December 14, 2025
**Status:** IN PROGRESS

## Goal
Feature parity with admin dashboard.

## Phases

### Phase 1: Setup
- Task 1.1: Initialize
- Task 1.2: Configure

### Phase 2: Implementation
- Task 2.1: Build
- Task 2.2: Test
"""
        plan_file = temp_dir / "old-format-plan.md"
        plan_file.write_text(plan_content, encoding='utf-8')
        return plan_file
    
    @pytest.fixture
    def migration_utility(self):
        """Create migration utility instance."""
        generator = UnifiedPlanGenerator()
        return PlanMigrationUtility(generator)
    
    def test_detects_old_format(self, migration_utility, sample_old_format_plan):
        """Should detect plan is in old format."""
        format_info = migration_utility.detect_plan_format(sample_old_format_plan)
        
        assert format_info['format'] == 'legacy'
        assert format_info['has_visual_tracker'] is False
        assert format_info['has_token_tracking'] is False
        assert format_info['has_continuation_prompt'] is False
    
    def test_detects_unified_format(self, migration_utility, temp_dir):
        """Should detect plan is already in unified format."""
        # Create unified format plan (using string concatenation to avoid encoding issues)
        unified_content = "## 🧠 CORTEX Test Plan\n"
        unified_content += "**Author:** Asif Hussain\n\n"
        unified_content += "## 📊 Visual Progress Tracker\n"
        unified_content += "**Overall Progress:** 50%\n\n"
        unified_content += "| Phase | Name | Status |\n"
        unified_content += "|-------|------|--------|\n"
        unified_content += "| 1 | Setup | ✅ COMPLETE |\n"
        
        plan_file = temp_dir / "unified-plan.md"
        plan_file.write_text(unified_content, encoding='utf-8')
        
        format_info = migration_utility.detect_plan_format(plan_file)
        
        assert format_info['format'] == 'unified'
        assert format_info['has_visual_tracker'] is True
    
    def test_extracts_phases_from_old_format(self, migration_utility, sample_old_format_plan):
        """Should extract phase information from old format."""
        phases = migration_utility.extract_phases(sample_old_format_plan)
        
        assert len(phases) == 2
        assert phases[0]['name'] == 'Setup'
        assert phases[1]['name'] == 'Implementation'
    
    def test_migrates_to_unified_format(self, migration_utility, sample_old_format_plan, temp_dir):
        """Should migrate old format to unified format."""
        output_file = temp_dir / "migrated-plan.md"
        result = migration_utility.migrate_to_unified(
            source=sample_old_format_plan,
            destination=output_file,
            plan_id="cortex-lens-v3"
        )
        
        assert result['success'] is True
        assert output_file.exists()
        
        # Verify unified format markers
        content = output_file.read_text(encoding='utf-8')
        assert '## 📊 Visual Progress Tracker' in content
        assert 'Overall Progress:' in content
        assert '**Author:** Asif Hussain' in content
    
    def test_preserves_content_during_migration(self, migration_utility, sample_old_format_plan, temp_dir):
        """Should preserve phase information during migration."""
        output_file = temp_dir / "migrated-plan.md"
        migration_utility.migrate_to_unified(
            source=sample_old_format_plan,
            destination=output_file,
            plan_id="test-plan"
        )
        
        content = output_file.read_text(encoding='utf-8')
        
        # Check phase names are preserved
        assert 'Setup' in content
        assert 'Implementation' in content
        
        # Check unified format structure
        assert '## 📊 Visual Progress Tracker' in content
    
    def test_adds_token_tracking_baseline(self, migration_utility, sample_old_format_plan, temp_dir):
        """Should add token tracking section."""
        output_file = temp_dir / "migrated-plan.md"
        migration_utility.migrate_to_unified(
            source=sample_old_format_plan,
            destination=output_file,
            plan_id="test-plan"
        )
        
        content = output_file.read_text(encoding='utf-8')
        
        # Token tracking is in the visual progress tracker
        assert 'Token Reduction' in content or 'tokens' in content.lower()
    
    def test_dry_run_mode(self, migration_utility, sample_old_format_plan, temp_dir):
        """Should preview changes without writing files."""
        output_file = temp_dir / "migrated-plan.md"
        result = migration_utility.migrate_to_unified(
            source=sample_old_format_plan,
            destination=output_file,
            plan_id="test-plan",
            dry_run=True
        )
        
        assert result['success'] is True
        assert result['preview'] is not None
        assert not output_file.exists()  # No file created in dry-run
    
    def test_validates_migration(self, migration_utility, temp_dir):
        """Should validate migrated plan has all required elements."""
        # Create valid unified plan
        valid_plan = temp_dir / "valid-plan.md"
        valid_content = "## 🧠 CORTEX Test\n"
        valid_content += "**Author:** Asif Hussain\n\n"
        valid_content += "## 📊 Visual Progress Tracker\n"
        valid_content += "**Overall Progress:** 25%\n\n"
        valid_content += "| Phase | Name | Status |\n"
        valid_content += "|-------|------|--------|\n"
        valid_content += "| 1 | Test | ✅ COMPLETE |\n\n"
        valid_content += "## 🔄 Continuation Prompt\n"
        valid_content += "```markdown\n"
        valid_content += "Continue work...\n"
        valid_content += "```\n"
        
        valid_plan.write_text(valid_content, encoding='utf-8')
        
        validation = migration_utility.validate_migration(valid_plan)
        
        assert validation['valid'] is True
        assert validation['has_visual_tracker'] is True
        assert validation['has_author'] is True
        assert validation['has_continuation_prompt'] is True
    
    def test_batch_migration(self, migration_utility, temp_dir):
        """Should migrate multiple plans in batch."""
        # Create multiple old format plans
        for i in range(3):
            plan = temp_dir / f"plan-{i}.md"
            plan.write_text(f"# Plan {i}\n\n## Phase 1\n- Task", encoding='utf-8')
        
        results = migration_utility.migrate_batch(
            source_dir=temp_dir,
            pattern="plan-*.md",
            output_dir=temp_dir / "migrated"
        )
        
        assert len(results) == 3
        assert all(r['success'] for r in results)
    
    def test_handles_migration_errors_gracefully(self, migration_utility, temp_dir):
        """Should handle errors without crashing."""
        invalid_file = temp_dir / "invalid.md"
        invalid_file.write_text("", encoding='utf-8')  # Empty file
        
        result = migration_utility.migrate_to_unified(
            source=invalid_file,
            destination=temp_dir / "output.md",
            plan_id="test"
        )
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_reports_token_metrics(self, migration_utility, sample_old_format_plan, temp_dir):
        """Should report token count before/after migration."""
        output_file = temp_dir / "migrated-plan.md"
        result = migration_utility.migrate_to_unified(
            source=sample_old_format_plan,
            destination=output_file,
            plan_id="test-plan"
        )
        
        assert 'tokens_before' in result
        assert 'tokens_after' in result
        assert 'tokens_delta' in result


class TestPlanFormatDetection:
    """Test format detection logic."""
    
    @pytest.fixture
    def migration_utility(self):
        """Create migration utility instance."""
        return PlanMigrationUtility()
    
    def test_identifies_planning_system_20_format(self, migration_utility, tmp_path):
        """Should identify Planning System 2.0 format."""
        content = """# Feature: Test
        
## 🎯 Overview
...

## 📋 Definition of Ready (DoR)
...
"""
        plan_file = tmp_path / "ps20-plan.md"
        plan_file.write_text(content, encoding='utf-8')
        
        format_info = migration_utility.detect_plan_format(plan_file)
        assert format_info['format'] == 'planning_system_2.0'
    
    def test_identifies_legacy_format(self, migration_utility, tmp_path):
        """Should identify legacy format."""
        content = """# Master Plan

## Goal
Test goal

## Phases
...
"""
        plan_file = tmp_path / "legacy-plan.md"
        plan_file.write_text(content, encoding='utf-8')
        
        format_info = migration_utility.detect_plan_format(plan_file)
        assert format_info['format'] == 'legacy'
    
    def test_identifies_unified_format(self, migration_utility, tmp_path):
        """Should identify unified format (Phase 13)."""
        content = "## 🧠 CORTEX Test Plan\n"
        content += "**Author:** Asif Hussain\n\n"
        content += "## 📊 Visual Progress Tracker\n"
        content += "...\n"
        
        plan_file = tmp_path / "unified-plan.md"
        plan_file.write_text(content, encoding='utf-8')
        
        format_info = migration_utility.detect_plan_format(plan_file)
        assert format_info['format'] == 'unified'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
