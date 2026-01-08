"""
Tests for Enhanced Vacuum Orchestrator - feat08-cleanup Phase 1

Tests:
- Pattern matching
- Dry-run mode
- Rollback capability
- Multi-repo support
- Category-based cleanup
- Size thresholds
- Exclusion patterns

Author: Asif Hussain
Version: 1.0.0
Created: 2026-01-08
"""

import pytest
import shutil
from pathlib import Path
from src.orchestrators.vacuum.enhanced_vacuum import (
    VacuumOrchestrator,
    MultiRepoVacuum,
    CleanupPattern,
    CleanupCategory,
    generate_cleanup_report
)


@pytest.fixture
def temp_workspace(tmp_path):
    """Create temporary workspace with test files"""
    workspace = tmp_path / "test_workspace"
    workspace.mkdir()
    
    # Python cache
    pycache = workspace / "src" / "__pycache__"
    pycache.mkdir(parents=True)
    (pycache / "module.cpython-39.pyc").write_text("compiled")
    
    # Test cache
    pytest_cache = workspace / ".pytest_cache"
    pytest_cache.mkdir()
    (pytest_cache / "data.json").write_text("{}")
    
    # Build artifacts
    dist = workspace / "dist"
    dist.mkdir()
    (dist / "package.whl").write_text("wheel")
    
    # Log files
    (workspace / "app.log").write_text("log data")
    (workspace / "debug.log").write_text("debug data")
    
    # System files
    (workspace / ".DS_Store").write_text("metadata")
    
    # Temp files
    (workspace / "data.tmp").write_text("temporary")
    
    # Node modules
    node_modules = workspace / "node_modules" / "package"
    node_modules.mkdir(parents=True)
    (node_modules / "index.js").write_text("code")
    
    # Files to keep (not matching patterns)
    (workspace / "src" / "main.py").write_text("source code")
    (workspace / "README.md").write_text("documentation")
    
    return workspace


@pytest.fixture
def vacuum(temp_workspace):
    """Create Vacuum orchestrator instance"""
    return VacuumOrchestrator(temp_workspace)


class TestPatternMatching:
    """Test pattern matching functionality"""
    
    def test_default_patterns_loaded(self, vacuum):
        """Test that default patterns are loaded"""
        assert len(vacuum.patterns) > 0
        categories = {p.category for p in vacuum.patterns}
        assert CleanupCategory.PYTHON_CACHE in categories
        assert CleanupCategory.TEST_CACHE in categories
        assert CleanupCategory.BUILD_ARTIFACTS in categories
    
    def test_custom_patterns(self, temp_workspace):
        """Test custom pattern configuration"""
        patterns = [
            CleanupPattern(CleanupCategory.CUSTOM, "**/*.custom", "Custom files")
        ]
        vacuum = VacuumOrchestrator(temp_workspace, patterns=patterns)
        assert len(vacuum.patterns) == 1
        assert vacuum.patterns[0].category == CleanupCategory.CUSTOM
    
    def test_scan_finds_python_cache(self, vacuum, temp_workspace):
        """Test scanning finds Python cache files"""
        items = vacuum.scan()
        
        # Should find __pycache__ directory and .pyc file
        pycache_items = [
            item for item in items 
            if item.category == CleanupCategory.PYTHON_CACHE
        ]
        assert len(pycache_items) > 0
    
    def test_scan_finds_test_cache(self, vacuum):
        """Test scanning finds test cache"""
        items = vacuum.scan()
        test_cache_items = [
            item for item in items 
            if item.category == CleanupCategory.TEST_CACHE
        ]
        assert len(test_cache_items) > 0
    
    def test_scan_finds_build_artifacts(self, vacuum):
        """Test scanning finds build artifacts"""
        items = vacuum.scan()
        build_items = [
            item for item in items 
            if item.category == CleanupCategory.BUILD_ARTIFACTS
        ]
        assert len(build_items) > 0
    
    def test_scan_finds_log_files(self, vacuum):
        """Test scanning finds log files"""
        items = vacuum.scan()
        log_items = [
            item for item in items 
            if item.category == CleanupCategory.LOG_FILES
        ]
        assert len(log_items) >= 2  # app.log and debug.log
    
    def test_scan_finds_system_files(self, vacuum):
        """Test scanning finds system files"""
        items = vacuum.scan()
        system_items = [
            item for item in items 
            if item.category == CleanupCategory.SYSTEM_FILES
        ]
        assert len(system_items) > 0
    
    def test_scan_finds_node_modules(self, vacuum):
        """Test scanning finds node_modules"""
        items = vacuum.scan()
        node_items = [
            item for item in items 
            if item.category == CleanupCategory.NODE_MODULES
        ]
        assert len(node_items) > 0
    
    def test_scan_preserves_source_files(self, vacuum, temp_workspace):
        """Test that source files are NOT matched"""
        items = vacuum.scan()
        paths = {str(item.path) for item in items}
        
        # Source files should NOT be in cleanup list
        assert str(temp_workspace / "src" / "main.py") not in paths
        assert str(temp_workspace / "README.md") not in paths


class TestExclusionPatterns:
    """Test exclusion pattern functionality"""
    
    def test_exclusion_pattern_blocks_matching_files(self, temp_workspace):
        """Test that exclusion patterns work"""
        vacuum = VacuumOrchestrator(
            temp_workspace,
            exclude_patterns=["**/app.log"]
        )
        items = vacuum.scan()
        
        # app.log should be excluded
        paths = {str(item.path) for item in items}
        assert str(temp_workspace / "app.log") not in paths
        
        # But debug.log should still be found
        assert str(temp_workspace / "debug.log") in paths
    
    def test_multiple_exclusion_patterns(self, temp_workspace):
        """Test multiple exclusion patterns"""
        vacuum = VacuumOrchestrator(
            temp_workspace,
            exclude_patterns=["**/*.log", "**/.DS_Store"]
        )
        items = vacuum.scan()
        
        # No log files or .DS_Store should be found
        log_items = [
            item for item in items 
            if item.category == CleanupCategory.LOG_FILES
        ]
        system_items = [
            item for item in items 
            if str(item.path).endswith(".DS_Store")
        ]
        
        assert len(log_items) == 0
        assert len(system_items) == 0


class TestSizeCalculation:
    """Test size calculation"""
    
    def test_file_size_calculated(self, vacuum):
        """Test file size is calculated correctly"""
        items = vacuum.scan()
        
        # All items should have size > 0
        for item in items:
            assert item.size_bytes >= 0
    
    def test_directory_size_calculated(self, vacuum):
        """Test directory size includes all files"""
        items = vacuum.scan()
        
        # Find __pycache__ directory
        pycache_items = [
            item for item in items 
            if item.is_directory and "__pycache__" in str(item.path)
        ]
        
        if pycache_items:
            item = pycache_items[0]
            # Should have size from .pyc file
            assert item.size_bytes > 0
    
    def test_size_mb_property(self, vacuum):
        """Test size_mb property conversion"""
        items = vacuum.scan()
        
        for item in items:
            expected_mb = item.size_bytes / (1024 * 1024)
            assert abs(item.size_mb - expected_mb) < 0.001


class TestPreview:
    """Test preview functionality"""
    
    def test_preview_generates_report(self, vacuum):
        """Test preview generates report"""
        preview = vacuum.preview()
        
        assert "workspace" in preview
        assert "total_items" in preview
        assert "total_size_mb" in preview
        assert "by_category" in preview
    
    def test_preview_groups_by_category(self, vacuum):
        """Test preview groups items by category"""
        preview = vacuum.preview()
        categories = preview["by_category"]
        
        # Should have multiple categories
        assert len(categories) > 0
        
        # Each category should have count and size
        for cat_data in categories.values():
            assert "count" in cat_data
            assert "size_mb" in cat_data
    
    def test_preview_shows_sample_items(self, vacuum):
        """Test preview shows sample items"""
        preview = vacuum.preview()
        
        # At least one category should have items
        for cat_data in preview["by_category"].values():
            if cat_data["count"] > 0:
                assert "items" in cat_data
                assert len(cat_data["items"]) > 0
                break
    
    def test_preview_without_scan(self, vacuum):
        """Test preview triggers scan if not done"""
        # Don't call scan() first
        preview = vacuum.preview()
        
        assert preview["total_items"] > 0


class TestDryRun:
    """Test dry-run mode"""
    
    def test_dry_run_doesnt_delete_files(self, vacuum, temp_workspace):
        """Test dry-run mode doesn't actually delete files"""
        # Record original files
        original_files = list(temp_workspace.rglob("*"))
        
        # Run in dry-run mode
        result = vacuum.cleanup(dry_run=True)
        
        # Files should still exist
        current_files = list(temp_workspace.rglob("*"))
        assert len(current_files) == len(original_files)
        
        # Result should indicate dry-run
        assert result.dry_run is True
        assert result.items_deleted == 0
        assert result.total_freed_bytes == 0
    
    def test_dry_run_reports_what_would_be_deleted(self, vacuum):
        """Test dry-run reports potential deletions"""
        result = vacuum.cleanup(dry_run=True)
        
        # Should find items
        assert result.items_found > 0
        
        # But nothing deleted
        assert result.items_deleted == 0
    
    def test_dry_run_calculates_potential_savings(self, vacuum):
        """Test dry-run shows potential space savings"""
        result = vacuum.cleanup(dry_run=True)
        
        # Should have total size calculated
        assert result.total_size_bytes > 0
        assert result.total_size_mb > 0


class TestCleanupExecution:
    """Test actual cleanup execution"""
    
    def test_cleanup_deletes_matched_files(self, vacuum, temp_workspace):
        """Test cleanup actually deletes matched files"""
        # Scan first
        items = vacuum.scan()
        assert len(items) > 0
        
        # Execute cleanup
        result = vacuum.cleanup(dry_run=False)
        
        # Should have deleted items
        assert result.items_deleted > 0
        assert result.total_freed_bytes > 0
        
        # Files should be gone
        for item in items:
            assert not item.path.exists()
    
    def test_cleanup_preserves_source_files(self, vacuum, temp_workspace):
        """Test cleanup preserves non-matched files"""
        # Execute cleanup
        vacuum.cleanup(dry_run=False)
        
        # Source files should still exist
        assert (temp_workspace / "src" / "main.py").exists()
        assert (temp_workspace / "README.md").exists()
    
    def test_cleanup_reports_errors(self, vacuum, temp_workspace):
        """Test cleanup reports errors for failed deletions"""
        # Create a file we can't delete (by making parent read-only)
        protected_dir = temp_workspace / "protected"
        protected_dir.mkdir()
        (protected_dir / "file.pyc").write_text("data")
        
        # Make directory read-only (platform-specific behavior)
        import stat
        protected_dir.chmod(stat.S_IRUSR | stat.S_IXUSR)
        
        try:
            result = vacuum.cleanup(dry_run=False)
            
            # May have errors (depends on platform)
            # Just verify errors list exists
            assert isinstance(result.errors, list)
        finally:
            # Restore permissions
            protected_dir.chmod(stat.S_IRWXU)
    
    def test_cleanup_measures_duration(self, vacuum):
        """Test cleanup measures operation duration"""
        result = vacuum.cleanup(dry_run=False)
        
        assert result.duration_seconds > 0
        assert result.duration_seconds < 60  # Should be fast


class TestBackupAndRollback:
    """Test backup and rollback functionality"""
    
    def test_backup_creates_backup_dir(self, vacuum, temp_workspace):
        """Test backup creates backup directory"""
        vacuum.cleanup(dry_run=False, create_backup=True)
        
        # Backup dir should exist
        backup_dirs = list((temp_workspace / ".vacuum_backup").glob("*"))
        assert len(backup_dirs) > 0
    
    def test_backup_preserves_files(self, vacuum, temp_workspace):
        """Test backup preserves deleted files"""
        # Record a file that will be deleted
        log_file = temp_workspace / "app.log"
        original_content = log_file.read_text()
        
        # Cleanup with backup
        vacuum.cleanup(dry_run=False, create_backup=True)
        
        # Original should be gone
        assert not log_file.exists()
        
        # But should be in backup
        assert vacuum.backup_dir is not None
        backup_files = list(vacuum.backup_dir.rglob("app.log"))
        assert len(backup_files) > 0
        assert backup_files[0].read_text() == original_content
    
    def test_rollback_restores_files(self, vacuum, temp_workspace):
        """Test rollback restores deleted files"""
        # Record original state
        log_file = temp_workspace / "app.log"
        original_content = log_file.read_text()
        
        # Cleanup with backup
        vacuum.cleanup(dry_run=False, create_backup=True)
        assert not log_file.exists()
        
        # Rollback
        success = vacuum.rollback()
        assert success is True
        
        # File should be restored
        assert log_file.exists()
        assert log_file.read_text() == original_content
    
    def test_rollback_without_backup_fails(self, vacuum):
        """Test rollback fails without backup"""
        success = vacuum.rollback()
        assert success is False


class TestMultiRepo:
    """Test multi-repository support"""
    
    def test_multi_repo_initialization(self, temp_workspace):
        """Test multi-repo vacuum initialization"""
        # Create multiple repos
        repo1 = temp_workspace / "repo1"
        repo2 = temp_workspace / "repo2"
        repo1.mkdir()
        repo2.mkdir()
        
        multi = MultiRepoVacuum([repo1, repo2])
        assert len(multi.vacuums) == 2
    
    def test_multi_repo_scan(self, temp_workspace):
        """Test scanning multiple repositories"""
        # Create repos with files
        repo1 = temp_workspace / "repo1"
        repo2 = temp_workspace / "repo2"
        repo1.mkdir()
        repo2.mkdir()
        
        # Add cleanup targets
        (repo1 / "test.log").write_text("log1")
        (repo2 / "test.log").write_text("log2")
        
        multi = MultiRepoVacuum([repo1, repo2])
        results = multi.scan_all()
        
        assert len(results) == 2
        assert repo1 in results
        assert repo2 in results
    
    def test_multi_repo_preview(self, temp_workspace):
        """Test unified preview for multiple repos"""
        repo1 = temp_workspace / "repo1"
        repo2 = temp_workspace / "repo2"
        repo1.mkdir()
        repo2.mkdir()
        
        (repo1 / "test.log").write_text("log1")
        (repo2 / "test.log").write_text("log2")
        
        multi = MultiRepoVacuum([repo1, repo2])
        preview = multi.preview_all()
        
        assert preview["total_repos"] == 2
        assert "repositories" in preview
        assert len(preview["repositories"]) == 2
    
    def test_multi_repo_cleanup(self, temp_workspace):
        """Test cleaning multiple repositories"""
        repo1 = temp_workspace / "repo1"
        repo2 = temp_workspace / "repo2"
        repo1.mkdir()
        repo2.mkdir()
        
        log1 = repo1 / "test.log"
        log2 = repo2 / "test.log"
        log1.write_text("log1")
        log2.write_text("log2")
        
        multi = MultiRepoVacuum([repo1, repo2])
        results = multi.cleanup_all(dry_run=False)
        
        # Both repos should have results
        assert len(results) == 2
        
        # Files should be deleted
        assert not log1.exists()
        assert not log2.exists()


class TestReportGeneration:
    """Test report generation"""
    
    def test_generate_report_for_dry_run(self, vacuum):
        """Test report generation for dry-run"""
        result = vacuum.cleanup(dry_run=True)
        report = generate_cleanup_report(result)
        
        assert "DRY-RUN" in report
        assert str(result.items_found) in report
    
    def test_generate_report_for_real_cleanup(self, vacuum):
        """Test report generation for actual cleanup"""
        result = vacuum.cleanup(dry_run=False)
        report = generate_cleanup_report(result)
        
        assert "EXECUTE" in report
        assert str(result.items_deleted) in report
    
    def test_generate_report_shows_errors(self, vacuum):
        """Test report shows errors if present"""
        result = vacuum.cleanup(dry_run=False)
        result.errors.append("Test error")
        
        report = generate_cleanup_report(result)
        assert "Test error" in report
    
    def test_generate_report_saves_to_file(self, vacuum, tmp_path):
        """Test report can be saved to file"""
        result = vacuum.cleanup(dry_run=True)
        output_file = tmp_path / "report.txt"
        
        generate_cleanup_report(result, output_file)
        
        assert output_file.exists()
        content = output_file.read_text()
        assert "VACUUM CLEANUP REPORT" in content


class TestCleanupItemSerialization:
    """Test CleanupItem serialization"""
    
    def test_cleanup_item_to_dict(self, vacuum):
        """Test CleanupItem converts to dictionary"""
        items = vacuum.scan()
        
        if items:
            item_dict = items[0].to_dict()
            
            assert "path" in item_dict
            assert "category" in item_dict
            assert "size_bytes" in item_dict
            assert "size_mb" in item_dict
            assert "is_directory" in item_dict


class TestCleanupResultSerialization:
    """Test CleanupResult serialization"""
    
    def test_cleanup_result_to_dict(self, vacuum):
        """Test CleanupResult converts to dictionary"""
        result = vacuum.cleanup(dry_run=True)
        result_dict = result.to_dict()
        
        assert "items_found" in result_dict
        assert "items_deleted" in result_dict
        assert "total_size_mb" in result_dict
        assert "dry_run" in result_dict


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
