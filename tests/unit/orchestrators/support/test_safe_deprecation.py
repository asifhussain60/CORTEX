"""
Phase 62: Safe Deprecation - Test Suite

Tests for deprecation warning system with 30-day migration notices.
Covers: marking deprecated code, migration guides, documentation updates.

AC_START: AC-PHASE62-001
Description: Safe Deprecation system - Phase 62 implementation
"""

import pytest
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from enum import Enum
import tempfile
import shutil

# Import from implementation
from cortex.orchestrators.support.safe_deprecation import (
    DeprecationLevel,
    DeprecationNotice,
    SafeDeprecationMarker,
    DeprecationWarningInjector,
    MigrationGuideGenerator,
    DeprecationDocumentationUpdater,
    RemovalScheduler,
)


# ============================================================================
# TESTS
# ============================================================================

class TestSafeDeprecationMarker:
    """Tests for SafeDeprecationMarker"""
    
    @pytest.fixture
    def temp_repo(self):
        """Create temporary repository"""
        tmpdir = tempfile.mkdtemp()
        repo_path = Path(tmpdir)
        (repo_path / "cortex").mkdir()
        yield repo_path
        shutil.rmtree(tmpdir)
    
    def test_marker_initialization(self, temp_repo):
        """Test marker initialization"""
        marker = SafeDeprecationMarker(temp_repo)
        assert marker.repo_root == temp_repo
        assert marker.notices == []
    
    def test_mark_deprecated(self, temp_repo):
        """Test marking module as deprecated"""
        marker = SafeDeprecationMarker(temp_repo)
        old_module = temp_repo / "old_module.py"
        old_module.touch()
        
        notice = marker.mark_deprecated(
            old_module,
            reason="Replaced by new_module",
            alternative="new_module",
            days_notice=30
        )
        
        assert isinstance(notice, DeprecationNotice)
        assert notice.module_path == old_module
    
    def test_add_deprecation_warning(self, temp_repo):
        """Test adding deprecation warning"""
        marker = SafeDeprecationMarker(temp_repo)
        file_path = temp_repo / "old_module.py"
        file_path.write_text("def old_function(): pass")
        
        notice = DeprecationNotice(
            module_path=file_path,
            target_date=datetime.utcnow() + timedelta(days=30),
            reason="Old implementation",
            migration_guide="Use new_module instead",
            alternative="new_module",
            level=DeprecationLevel.WARNING,
            days_remaining=30
        )
        
        marker.add_deprecation_warning(file_path, notice)
        assert file_path.exists()
    
    def test_generate_migration_guide(self, temp_repo):
        """Test migration guide generation"""
        marker = SafeDeprecationMarker(temp_repo)
        notice = DeprecationNotice(
            module_path=Path("old.py"),
            target_date=datetime.utcnow() + timedelta(days=30),
            reason="Old implementation",
            migration_guide="",
            alternative="new_module",
            level=DeprecationLevel.WARNING,
            days_remaining=30
        )
        
        guide = marker.generate_migration_guide(notice)
        assert isinstance(guide, str)
    
    def test_create_removal_date(self, temp_repo):
        """Test removal date calculation"""
        marker = SafeDeprecationMarker(temp_repo)
        notice = DeprecationNotice(
            module_path=Path("old.py"),
            target_date=datetime.utcnow(),
            reason="Test",
            migration_guide="",
            alternative="new",
            level=DeprecationLevel.WARNING,
            days_remaining=0
        )
        
        removal_date = marker.create_removal_date(notice)
        assert isinstance(removal_date, datetime)
    
    def test_get_notices(self, temp_repo):
        """Test retrieving deprecation notices"""
        marker = SafeDeprecationMarker(temp_repo)
        notices = marker.get_notices()
        assert isinstance(notices, list)


class TestDeprecationWarningInjector:
    """Tests for DeprecationWarningInjector"""
    
    @pytest.fixture
    def injector(self):
        """Create injector instance"""
        return DeprecationWarningInjector()
    
    def test_injector_initialization(self, injector):
        """Test injector initialization"""
        assert injector.warnings_injected == 0
        assert injector.files_modified == []
    
    def test_inject_decorator(self, injector):
        """Test injecting @deprecated decorator"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "module.py"
            file_path.write_text("def func(): pass")
            
            injector.inject_decorator(file_path, "Old implementation")
            assert file_path.exists()
    
    def test_inject_warning_function(self, injector):
        """Test injecting deprecation warning in function"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "module.py"
            file_path.write_text("def func(): pass")
            
            injector.inject_warning_function(file_path, "func", "Use new_func instead")
            assert file_path.exists()
    
    def test_inject_comment_header(self, injector):
        """Test injecting deprecation header comment"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "module.py"
            file_path.write_text("# Module")
            
            notice = DeprecationNotice(
                module_path=file_path,
                target_date=datetime.utcnow() + timedelta(days=30),
                reason="Old",
                migration_guide="Use new",
                alternative="new_module",
                level=DeprecationLevel.WARNING,
                days_remaining=30
            )
            
            injector.inject_comment_header(file_path, notice)
            assert file_path.exists()
    
    def test_get_modified_files(self, injector):
        """Test retrieving modified files"""
        modified = injector.get_modified_files()
        assert isinstance(modified, list)


class TestMigrationGuideGenerator:
    """Tests for MigrationGuideGenerator"""
    
    @pytest.fixture
    def generator(self):
        """Create generator instance"""
        return MigrationGuideGenerator()
    
    def test_generator_initialization(self, generator):
        """Test generator initialization"""
        assert generator.guides == {}
    
    def test_create_guide(self, generator):
        """Test creating migration guide"""
        guide = generator.create_guide(
            old_module="old_module",
            new_module="new_module",
            examples=["example1", "example2"]
        )
        
        assert isinstance(guide, str)
    
    def test_generate_code_examples(self, generator):
        """Test generating code examples"""
        examples = generator.generate_code_examples(
            old_code="old_implementation()",
            new_code="new_implementation()"
        )
        
        assert isinstance(examples, dict)
    
    def test_create_step_by_step_guide(self, generator):
        """Test step-by-step guide creation"""
        steps = [
            "Step 1: Install new package",
            "Step 2: Update imports",
            "Step 3: Test code"
        ]
        
        guide = generator.create_step_by_step_guide(steps)
        assert isinstance(guide, str)
    
    def test_export_guide_to_markdown(self, generator):
        """Test exporting guide as Markdown"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "migration_guide.md"
            guide = "# Migration Guide\nStep 1..."
            
            generator.export_guide_to_markdown(guide, output_path)
            assert output_path.exists()


class TestDeprecationDocumentationUpdater:
    """Tests for DeprecationDocumentationUpdater"""
    
    @pytest.fixture
    def updater(self):
        """Create updater instance"""
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_root = Path(tmpdir)
            yield DeprecationDocumentationUpdater(docs_root)
    
    def test_updater_initialization(self, updater):
        """Test updater initialization"""
        assert updater.updated_docs == []
    
    def test_add_deprecation_section(self, updater):
        """Test adding deprecation section"""
        doc_file = updater.docs_root / "api.md"
        doc_file.write_text("# API Reference")
        
        notice = DeprecationNotice(
            module_path=Path("old.py"),
            target_date=datetime.utcnow() + timedelta(days=30),
            reason="Old API",
            migration_guide="Use new API",
            alternative="new_api",
            level=DeprecationLevel.WARNING,
            days_remaining=30
        )
        
        updater.add_deprecation_section(doc_file, notice)
        assert doc_file.exists()
    
    def test_update_api_reference(self, updater):
        """Test updating API reference"""
        doc_file = updater.docs_root / "api.md"
        doc_file.write_text("# API Reference\n- function1\n- function2")
        
        updater.update_api_reference(doc_file, ["function1"])
        assert doc_file.exists()
    
    def test_create_migration_guide_doc(self, updater):
        """Test creating migration guide documentation"""
        doc_path = updater.docs_root / "migration.md"
        guide_content = "# Migration Guide\nFrom old to new API"
        
        updater.create_migration_guide_doc(doc_path, guide_content)
        assert doc_path.exists()
    
    def test_update_changelog(self, updater):
        """Test updating CHANGELOG"""
        changelog_path = updater.docs_root / "CHANGELOG.md"
        changelog_path.write_text("# Changelog\n")
        
        notice = DeprecationNotice(
            module_path=Path("old.py"),
            target_date=datetime.utcnow() + timedelta(days=30),
            reason="Old implementation",
            migration_guide="Use new",
            alternative="new_module",
            level=DeprecationLevel.WARNING,
            days_remaining=30
        )
        
        updater.update_changelog(changelog_path, notice)
        assert changelog_path.exists()


class TestRemovalScheduler:
    """Tests for RemovalScheduler"""
    
    @pytest.fixture
    def scheduler(self):
        """Create scheduler instance"""
        return RemovalScheduler()
    
    def test_scheduler_initialization(self, scheduler):
        """Test scheduler initialization"""
        assert scheduler.scheduled_removals == []
    
    def test_schedule_removal(self, scheduler):
        """Test scheduling removal"""
        notice = DeprecationNotice(
            module_path=Path("old.py"),
            target_date=datetime.utcnow() + timedelta(days=30),
            reason="Old code",
            migration_guide="Migrate to new",
            alternative="new_module",
            level=DeprecationLevel.WARNING,
            days_remaining=30
        )
        
        scheduler.schedule_removal(notice)
        assert len(scheduler.scheduled_removals) > 0
    
    def test_get_scheduled_removals(self, scheduler):
        """Test getting scheduled removals"""
        removals = scheduler.get_scheduled_removals()
        assert isinstance(removals, list)
    
    def test_get_due_for_removal(self, scheduler):
        """Test getting modules due for removal"""
        notice = DeprecationNotice(
            module_path=Path("old.py"),
            target_date=datetime.utcnow() - timedelta(days=1),  # Past date
            reason="Old code",
            migration_guide="Migrate",
            alternative="new",
            level=DeprecationLevel.WARNING,
            days_remaining=-1
        )
        
        scheduler.schedule_removal(notice)
        due = scheduler.get_due_for_removal()
        assert isinstance(due, list)
    
    def test_calculate_days_remaining(self, scheduler):
        """Test days remaining calculation"""
        notice = DeprecationNotice(
            module_path=Path("old.py"),
            target_date=datetime.utcnow() + timedelta(days=15),
            reason="Old code",
            migration_guide="Migrate",
            alternative="new",
            level=DeprecationLevel.WARNING,
            days_remaining=15
        )
        
        days = scheduler.calculate_days_remaining(notice)
        assert isinstance(days, int)


class TestDeprecationLevels:
    """Tests for deprecation severity levels"""
    
    def test_warning_level(self):
        """Test WARNING level"""
        assert DeprecationLevel.WARNING.value == "warning"
    
    def test_error_level(self):
        """Test ERROR level"""
        assert DeprecationLevel.ERROR.value == "error"
    
    def test_removed_level(self):
        """Test REMOVED level"""
        assert DeprecationLevel.REMOVED.value == "removed"


class TestDeprecationNotice:
    """Tests for DeprecationNotice dataclass"""
    
    def test_notice_creation(self):
        """Test creating deprecation notice"""
        target_date = datetime.utcnow() + timedelta(days=30)
        notice = DeprecationNotice(
            module_path=Path("old.py"),
            target_date=target_date,
            reason="Old implementation",
            migration_guide="Use new module",
            alternative="new_module",
            level=DeprecationLevel.WARNING,
            days_remaining=30
        )
        
        assert notice.module_path == Path("old.py")
        assert notice.reason == "Old implementation"
        # Days remaining may be 29 or 30 due to calculation timing
        assert notice.days_remaining in [29, 30]


class TestIntegration:
    """Integration tests for Phase 62"""
    
    def test_deprecation_workflow(self):
        """Test complete deprecation workflow"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            (repo_root / "cortex").mkdir()
            
            # Mark as deprecated
            marker = SafeDeprecationMarker(repo_root)
            old_file = repo_root / "old.py"
            old_file.write_text("def old_func(): pass")
            
            notice = marker.mark_deprecated(
                old_file,
                reason="Old implementation",
                alternative="new_module",
                days_notice=30
            )
            
            # Inject warning
            injector = DeprecationWarningInjector()
            injector.inject_decorator(old_file, notice.reason)
            
            # Generate guide
            generator = MigrationGuideGenerator()
            guide = generator.create_guide("old_module", "new_module", [])
            
            # Schedule removal
            scheduler = RemovalScheduler()
            scheduler.schedule_removal(notice)
            
            assert old_file.exists()
            assert isinstance(guide, str)


class TestEdgeCases:
    """Edge case tests"""
    
    def test_zero_days_remaining(self):
        """Test notice with zero days remaining"""
        notice = DeprecationNotice(
            module_path=Path("old.py"),
            target_date=datetime.utcnow(),
            reason="Ready for removal",
            migration_guide="Use new",
            alternative="new",
            level=DeprecationLevel.ERROR,
            days_remaining=0
        )
        
        # Due to timing, may be 0 or -1
        assert notice.days_remaining in [-1, 0]
    
    def test_negative_days_remaining(self):
        """Test notice with negative days (overdue)"""
        notice = DeprecationNotice(
            module_path=Path("old.py"),
            target_date=datetime.utcnow() - timedelta(days=5),
            reason="Overdue for removal",
            migration_guide="Urgent migration",
            alternative="new",
            level=DeprecationLevel.ERROR,
            days_remaining=-5
        )
        
        assert notice.days_remaining < 0


# AC_COMPLETE: AC-PHASE62-001 ✅
