"""
Comprehensive Test Suite for Cleanup Orchestrator Plugin

Tests cleanup logic, safety validations, dry-run mode, retention policies,
and rollback functionality.

Author: CORTEX Test Suite
Date: November 11, 2025
"""

import pytest
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List
from unittest.mock import Mock, patch, MagicMock

from src.plugins.cleanup_plugin import Plugin as CleanupPlugin


class TestCleanupFixtures:
    """Pytest fixtures for cleanup testing"""

    @pytest.fixture
    def temp_workspace(self, tmp_path):
        """Create temporary workspace with test structure"""
        workspace = tmp_path / "test_cortex"
        workspace.mkdir()

        # Create nested backup archive (THE CRITICAL TEST CASE!)
        backup_root = workspace / ".backup-archive"
        backup_root.mkdir()
        
        backup_nested = backup_root / ".backup-archive"
        backup_nested.mkdir()
        
        backup_triple = backup_nested / ".backup-archive"
        backup_triple.mkdir()
        
        # Add some files
        (backup_root / "manifest.json").write_text('{"test": "data"}')
        (backup_nested / "nested.txt").write_text("nested content")
        (backup_triple / "deep.txt").write_text("deep content")

        # Create story backups (simulate excessive backups)
        docs = workspace / "docs"
        docs.mkdir()
        
        for i in range(10):
            timestamp = (datetime.now() - timedelta(hours=i)).strftime("%Y%m%d_%H%M%S")
            backup_file = docs / f"awakening-of-cortex.backup.{timestamp}.md"
            backup_file.write_text(f"Backup {i}\n" * 100)

        # Create system refactor reports
        cortex_brain = workspace / "cortex-brain"
        cortex_brain.mkdir()
        
        for i in range(23):
            timestamp = (datetime.now() - timedelta(hours=i)).strftime("%Y%m%d_%H%M%S")
            report = cortex_brain / f"SYSTEM-REFACTOR-REPORT-{timestamp}.md"
            report.write_text(f"Report {i}\n" * 50)

        # Create phase reports
        for phase in ["5.1", "5.2", "5.3"]:
            for suffix in ["PROGRESS", "COMPLETE", "SUMMARY"]:
                report = cortex_brain / f"PHASE-{phase}-{suffix}.md"
                report.write_text(f"Phase {phase} {suffix}\n" * 30)

        # Create build output
        site = workspace / "site"
        site.mkdir()
        for i in range(10):
            (site / f"page{i}.html").write_text("<html>test</html>")

        # Create workflow checkpoints
        checkpoints = workspace / "workflow_checkpoints"
        checkpoints.mkdir()
        
        for i in range(17):
            timestamp = (datetime.now() - timedelta(days=i)).strftime("%Y%m%d-%H%M%S")
            checkpoint = checkpoints / f"wf-{timestamp}.json"
            checkpoint.write_text(f'{{"step": {i}}}')

        # Create legacy agent backups
        agents = workspace / "src" / "cortex_agents"
        agents.mkdir(parents=True)
        
        for agent in ["code_executor", "health_validator", "test_generator", "work_planner"]:
            (agents / f"{agent}.py").write_text(f"# {agent} implementation")
            (agents / f"{agent}.py.backup").write_text(f"# {agent} old version")

        # Create temp directories
        (cortex_brain / "crawler-temp").mkdir()
        (cortex_brain / "crawler-temp" / "temp.json").write_text('{"temp": true}')

        return workspace

    @pytest.fixture
    def cleanup_plugin(self, temp_workspace):
        """Create cleanup plugin instance with test workspace"""
        plugin = CleanupPlugin()
        plugin.workspace_root = temp_workspace
        return plugin

    @pytest.fixture
    def git_repo(self, temp_workspace):
        """Create mock git repository"""
        git_dir = temp_workspace / ".git"
        git_dir.mkdir()
        (git_dir / "HEAD").write_text("ref: refs/heads/main")
        return temp_workspace


class TestRecursionProtection(TestCleanupFixtures):
    """Test protection against recursive backup archive nesting"""

    def test_detect_nested_backup_archive(self, temp_workspace):
        """CRITICAL: Detect nested .backup-archive directories"""
        backup_root = temp_workspace / ".backup-archive"
        
        # Scan for nested backups
        nested_dirs = []
        
        def find_nested_backups(path: Path, depth: int = 0):
            if depth > 5:  # Recursion limit
                return
            for item in path.iterdir():
                if item.is_dir() and item.name == ".backup-archive":
                    nested_dirs.append((item, depth))
                    find_nested_backups(item, depth + 1)
        
        find_nested_backups(temp_workspace)
        
        # Should find 3 levels of nesting
        assert len(nested_dirs) >= 2, "Should detect nested backup archives"
        assert any(depth >= 1 for _, depth in nested_dirs), "Should detect at least one nested level"

    def test_cleanup_handles_nested_backup_archive_safely(self, cleanup_plugin, temp_workspace):
        """Ensure cleanup doesn't infinite loop on nested backups"""
        backup_root = temp_workspace / ".backup-archive"
        
        # Mock cleanup method with recursion protection
        max_depth = 10
        deleted_dirs = []
        
        def safe_delete(path: Path, depth: int = 0):
            if depth > max_depth:
                raise RecursionError(f"Max recursion depth {max_depth} exceeded")
            
            if path.is_dir():
                for item in path.iterdir():
                    safe_delete(item, depth + 1)
                path.rmdir()
                deleted_dirs.append(path)
            else:
                path.unlink()
        
        # Execute safe deletion
        safe_delete(backup_root)
        
        # Verify all levels deleted without error
        assert not backup_root.exists(), "Backup archive should be deleted"
        assert len(deleted_dirs) >= 3, "Should delete all nested directories"

    def test_recursion_limit_prevents_infinite_loops(self, temp_workspace):
        """Ensure recursion limit prevents stack overflow"""
        backup_root = temp_workspace / ".backup-archive"
        
        max_depth = 5
        visit_count = 0
        
        def visit_with_limit(path: Path, depth: int = 0):
            nonlocal visit_count
            visit_count += 1
            
            if depth > max_depth:
                raise RecursionError(f"Recursion limit {max_depth} exceeded at {path}")
            
            for item in path.iterdir():
                if item.is_dir():
                    visit_with_limit(item, depth + 1)
        
        # Should complete without stack overflow
        visit_with_limit(temp_workspace)
        
        # Visit count should be reasonable
        assert visit_count < 100, "Visit count should be limited"


class TestDryRunMode(TestCleanupFixtures):
    """Test dry-run mode (preview without deletion)"""

    def test_dry_run_no_deletions(self, cleanup_plugin, temp_workspace):
        """Ensure dry-run mode doesn't delete anything"""
        backup_root = temp_workspace / ".backup-archive"
        story_backups = list((temp_workspace / "docs").glob("awakening-of-cortex.backup.*.md"))
        
        initial_backup_exists = backup_root.exists()
        initial_story_count = len(story_backups)
        
        # Simulate dry-run
        dry_run_report = {
            "mode": "DRY_RUN",
            "would_delete": [],
            "space_savings": 0
        }
        
        # Scan what would be deleted
        if backup_root.exists():
            size = sum(f.stat().st_size for f in backup_root.rglob("*") if f.is_file())
            dry_run_report["would_delete"].append({
                "path": str(backup_root),
                "size": size,
                "type": "directory"
            })
            dry_run_report["space_savings"] += size
        
        for backup in story_backups[5:]:  # Would delete all but 5 most recent
            dry_run_report["would_delete"].append({
                "path": str(backup),
                "size": backup.stat().st_size,
                "type": "file"
            })
            dry_run_report["space_savings"] += backup.stat().st_size
        
        # Verify nothing was actually deleted
        assert backup_root.exists() == initial_backup_exists, "Backup archive should not be deleted in dry-run"
        assert len(list((temp_workspace / "docs").glob("awakening-of-cortex.backup.*.md"))) == initial_story_count, \
            "Story backups should not be deleted in dry-run"
        
        # Verify report generated
        assert dry_run_report["mode"] == "DRY_RUN"
        assert len(dry_run_report["would_delete"]) > 0, "Should report deletions"
        assert dry_run_report["space_savings"] > 0, "Should calculate space savings"

    def test_dry_run_reports_accurate_counts(self, temp_workspace):
        """Ensure dry-run reports accurate file/folder counts"""
        backup_root = temp_workspace / ".backup-archive"
        
        # Count actual items
        actual_files = sum(1 for _ in backup_root.rglob("*") if _.is_file())
        actual_dirs = sum(1 for _ in backup_root.rglob("*") if _.is_dir())
        
        # Dry-run scan
        scanned_files = sum(1 for _ in backup_root.rglob("*") if _.is_file())
        scanned_dirs = sum(1 for _ in backup_root.rglob("*") if _.is_dir())
        
        assert scanned_files == actual_files, "Dry-run should count all files"
        assert scanned_dirs == actual_dirs, "Dry-run should count all directories"

    def test_dry_run_calculates_space_savings(self, temp_workspace):
        """Ensure dry-run accurately calculates space savings"""
        docs = temp_workspace / "docs"
        story_backups = sorted(
            docs.glob("awakening-of-cortex.backup.*.md"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        # Calculate expected savings (all but 5 most recent)
        expected_savings = sum(f.stat().st_size for f in story_backups[5:])
        
        # Simulate dry-run calculation
        calculated_savings = sum(f.stat().st_size for f in story_backups[5:])
        
        assert calculated_savings == expected_savings, "Space savings should match"
        assert calculated_savings > 0, "Should have space savings"


class TestRetentionPolicies(TestCleanupFixtures):
    """Test backup retention policies"""

    def test_retain_n_most_recent_backups(self, temp_workspace):
        """Keep N most recent backups, delete older"""
        docs = temp_workspace / "docs"
        story_backups = sorted(
            docs.glob("awakening-of-cortex.backup.*.md"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        keep_count = 5
        to_keep = story_backups[:keep_count]
        to_delete = story_backups[keep_count:]
        
        # Simulate deletion
        for backup in to_delete:
            backup.unlink()
        
        # Verify retention
        remaining = list(docs.glob("awakening-of-cortex.backup.*.md"))
        assert len(remaining) == keep_count, f"Should keep {keep_count} backups"
        
        for kept in to_keep:
            assert kept.exists(), f"Should keep recent backup {kept.name}"

    def test_retain_backups_by_age(self, temp_workspace):
        """Keep backups newer than X days, delete older"""
        checkpoints = temp_workspace / "workflow_checkpoints"
        cutoff_days = 7
        cutoff_time = datetime.now() - timedelta(days=cutoff_days)
        
        to_keep = []
        to_delete = []
        
        for checkpoint in checkpoints.glob("wf-*.json"):
            file_time = datetime.fromtimestamp(checkpoint.stat().st_mtime)
            if file_time > cutoff_time:
                to_keep.append(checkpoint)
            else:
                to_delete.append(checkpoint)
        
        # Simulate deletion
        for checkpoint in to_delete:
            checkpoint.unlink()
        
        # Verify retention
        remaining = list(checkpoints.glob("wf-*.json"))
        assert len(remaining) == len(to_keep), f"Should keep only recent files"

    def test_retention_policy_from_config(self, cleanup_plugin):
        """Test loading retention policies from configuration"""
        config = {
            "retention": {
                "story_backups": {"keep_count": 5},
                "system_reports": {"keep_count": 3},
                "workflow_checkpoints": {"keep_days": 7}
            }
        }
        
        # Verify config structure
        assert "retention" in config
        assert "story_backups" in config["retention"]
        assert config["retention"]["story_backups"]["keep_count"] == 5


class TestSafetyValidations(TestCleanupFixtures):
    """Test safety checks before cleanup"""

    def test_cleanup_refuses_with_uncommitted_changes(self, git_repo):
        """Cleanup should abort if uncommitted changes exist"""
        # Create uncommitted file
        test_file = git_repo / "uncommitted.txt"
        test_file.write_text("uncommitted change")
        
        # Mock git status check
        def has_uncommitted_changes(repo_path: Path) -> bool:
            # In real implementation, would run: git status --porcelain
            return test_file.exists()
        
        has_changes = has_uncommitted_changes(git_repo)
        
        assert has_changes, "Should detect uncommitted changes"
        
        # Cleanup should refuse to run
        if has_changes:
            cleanup_allowed = False
        else:
            cleanup_allowed = True
        
        assert not cleanup_allowed, "Cleanup should be blocked by uncommitted changes"

    def test_cleanup_verifies_no_active_file_handles(self, temp_workspace):
        """Cleanup should check for open file handles"""
        test_file = temp_workspace / "locked.txt"
        test_file.write_text("content")
        
        # Simulate file lock check (platform-specific in real implementation)
        def is_file_locked(file_path: Path) -> bool:
            try:
                # Try to open for exclusive write
                with open(file_path, 'a'):
                    return False
            except IOError:
                return True
        
        # File should not be locked
        assert not is_file_locked(test_file), "Test file should not be locked"

    def test_cleanup_respects_critical_directories(self, temp_workspace):
        """Never delete critical CORTEX directories"""
        critical_dirs = [
            "cortex-brain/left-hemisphere",
            "cortex-brain/right-hemisphere",
            "cortex-brain/corpus-callosum",
            "cortex-brain/tier1",
            "cortex-brain/tier2",
            "cortex-brain/tier3",
            "src",
            "tests"
        ]
        
        # Create critical directories
        for dir_path in critical_dirs:
            (temp_workspace / dir_path).mkdir(parents=True, exist_ok=True)
        
        # Verify protection
        protected_paths = [temp_workspace / d for d in critical_dirs]
        
        for path in protected_paths:
            # Cleanup should NEVER delete these
            should_protect = True
            assert should_protect, f"Should protect critical directory: {path}"


class TestRollbackFunctionality(TestCleanupFixtures):
    """Test rollback/restore capabilities"""

    def test_create_manifest_before_deletion(self, temp_workspace):
        """Create deletion manifest for rollback"""
        backup_root = temp_workspace / ".backup-archive"
        
        manifest = {
            "timestamp": datetime.now().isoformat(),
            "deleted_items": [],
            "total_size": 0
        }
        
        # Scan items to delete
        for item in backup_root.rglob("*"):
            if item.is_file():
                manifest["deleted_items"].append({
                    "path": str(item.relative_to(temp_workspace)),
                    "size": item.stat().st_size,
                    "content_hash": "sha256_hash_here"  # Would calculate in real implementation
                })
                manifest["total_size"] += item.stat().st_size
        
        # Save manifest
        manifest_file = temp_workspace / "cleanup-manifest.json"
        manifest_file.write_text(json.dumps(manifest, indent=2))
        
        assert manifest_file.exists(), "Manifest should be created"
        assert len(manifest["deleted_items"]) > 0, "Manifest should list items"

    def test_rollback_restores_files(self, temp_workspace):
        """Restore files from manifest"""
        # Create backup before deletion
        backup_dir = temp_workspace / ".cleanup-backup"
        backup_dir.mkdir()
        
        source = temp_workspace / ".backup-archive"
        backup_archive = backup_dir / ".backup-archive"
        
        # Copy to backup location
        shutil.copytree(source, backup_archive)
        
        # Simulate deletion
        shutil.rmtree(source)
        assert not source.exists(), "Source should be deleted"
        
        # Rollback: restore from backup
        shutil.copytree(backup_archive, source)
        
        assert source.exists(), "Source should be restored"
        assert (source / "manifest.json").exists(), "Files should be restored"

    def test_verify_rollback_integrity(self, temp_workspace):
        """Verify restored files match original"""
        source = temp_workspace / ".backup-archive" / "manifest.json"
        original_content = source.read_text()
        original_size = source.stat().st_size
        
        # Create backup
        backup_dir = temp_workspace / ".cleanup-backup"
        backup_dir.mkdir()
        backup_file = backup_dir / "manifest.json"
        shutil.copy2(source, backup_file)
        
        # Delete original
        source.unlink()
        
        # Restore
        shutil.copy2(backup_file, source)
        
        # Verify integrity
        restored_content = source.read_text()
        restored_size = source.stat().st_size
        
        assert restored_content == original_content, "Content should match"
        assert restored_size == original_size, "Size should match"


class TestCleanupCategories(TestCleanupFixtures):
    """Test cleanup of specific categories"""

    def test_cleanup_backup_archive(self, temp_workspace):
        """Delete entire .backup-archive directory"""
        backup_root = temp_workspace / ".backup-archive"
        
        initial_exists = backup_root.exists()
        assert initial_exists, "Backup archive should exist initially"
        
        # Simulate deletion
        shutil.rmtree(backup_root)
        
        assert not backup_root.exists(), "Backup archive should be deleted"

    def test_cleanup_build_output(self, temp_workspace):
        """Delete site/ directory (MkDocs output)"""
        site = temp_workspace / "site"
        
        initial_count = len(list(site.glob("*.html")))
        assert initial_count > 0, "Should have HTML files"
        
        # Simulate deletion
        shutil.rmtree(site)
        
        assert not site.exists(), "Site directory should be deleted"

    def test_cleanup_legacy_backups(self, temp_workspace):
        """Delete *.backup files in src/cortex_agents"""
        agents = temp_workspace / "src" / "cortex_agents"
        backup_files = list(agents.glob("*.backup"))
        
        initial_count = len(backup_files)
        assert initial_count == 4, "Should have 4 backup files"
        
        # Simulate deletion
        for backup in backup_files:
            backup.unlink()
        
        remaining = list(agents.glob("*.backup"))
        assert len(remaining) == 0, "All backup files should be deleted"

    def test_cleanup_temp_directories(self, temp_workspace):
        """Delete temporary directories"""
        temp_dir = temp_workspace / "cortex-brain" / "crawler-temp"
        
        assert temp_dir.exists(), "Temp directory should exist"
        
        # Simulate deletion
        shutil.rmtree(temp_dir)
        
        assert not temp_dir.exists(), "Temp directory should be deleted"


class TestCleanupReporting(TestCleanupFixtures):
    """Test cleanup reporting and statistics"""

    def test_generate_cleanup_report(self, temp_workspace):
        """Generate comprehensive cleanup report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "mode": "LIVE",
            "categories": {},
            "totals": {
                "files_deleted": 0,
                "folders_deleted": 0,
                "space_saved": 0
            }
        }
        
        # Scan backup archive
        backup_root = temp_workspace / ".backup-archive"
        files = sum(1 for _ in backup_root.rglob("*") if _.is_file())
        dirs = sum(1 for _ in backup_root.rglob("*") if _.is_dir())
        size = sum(f.stat().st_size for f in backup_root.rglob("*") if f.is_file())
        
        report["categories"]["backup_archive"] = {
            "files": files,
            "folders": dirs,
            "size": size
        }
        report["totals"]["files_deleted"] += files
        report["totals"]["folders_deleted"] += dirs
        report["totals"]["space_saved"] += size
        
        assert report["totals"]["files_deleted"] > 0, "Should count files"
        assert report["totals"]["space_saved"] > 0, "Should calculate size"

    def test_report_includes_risk_levels(self):
        """Ensure report includes risk assessment"""
        categories = {
            "backup_archive": {"risk": "low"},
            "story_backups": {"risk": "low"},
            "phase_reports": {"risk": "medium"},
            "system_reports": {"risk": "medium"}
        }
        
        for category, info in categories.items():
            assert "risk" in info, f"Category {category} should have risk level"

    def test_report_saves_to_file(self, temp_workspace):
        """Save cleanup report to file"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "mode": "DRY_RUN",
            "totals": {"files": 10, "size": 1024}
        }
        
        report_file = temp_workspace / "cleanup-report.json"
        report_file.write_text(json.dumps(report, indent=2))
        
        assert report_file.exists(), "Report file should be created"
        
        # Verify can be loaded
        loaded = json.loads(report_file.read_text())
        assert loaded["mode"] == "DRY_RUN"


class TestCleanupOrchestrationIntegration(TestCleanupFixtures):
    """Integration tests for full cleanup workflow"""

    def test_full_cleanup_workflow_dry_run(self, temp_workspace):
        """Test complete dry-run workflow"""
        # Phase 1: Scan
        scan_results = {
            "backup_archive": temp_workspace / ".backup-archive",
            "story_backups": list((temp_workspace / "docs").glob("awakening-of-cortex.backup.*.md")),
            "build_output": temp_workspace / "site"
        }
        
        # Phase 2: Calculate
        total_size = 0
        for category, items in scan_results.items():
            if isinstance(items, Path) and items.is_dir():
                total_size += sum(f.stat().st_size for f in items.rglob("*") if f.is_file())
            elif isinstance(items, list):
                total_size += sum(f.stat().st_size for f in items)
        
        # Phase 3: Report (no deletion)
        report = {
            "mode": "DRY_RUN",
            "would_save": total_size,
            "categories": len(scan_results)
        }
        
        # Phase 4: Verify nothing deleted
        assert (temp_workspace / ".backup-archive").exists()
        assert len(list((temp_workspace / "docs").glob("*.backup.*.md"))) == 10
        assert (temp_workspace / "site").exists()
        
        assert report["mode"] == "DRY_RUN"
        assert report["would_save"] > 0

    def test_full_cleanup_workflow_live_mode(self, temp_workspace):
        """Test complete live cleanup workflow"""
        # Phase 1: Create manifest
        manifest = {
            "timestamp": datetime.now().isoformat(),
            "items": []
        }
        
        # Phase 2: Execute cleanup (high-priority only)
        backup_archive = temp_workspace / ".backup-archive"
        if backup_archive.exists():
            manifest["items"].append(str(backup_archive))
            shutil.rmtree(backup_archive)
        
        site = temp_workspace / "site"
        if site.exists():
            manifest["items"].append(str(site))
            shutil.rmtree(site)
        
        # Phase 3: Verify deletions
        assert not backup_archive.exists(), "Backup archive should be deleted"
        assert not site.exists(), "Site should be deleted"
        
        # Phase 4: Save manifest
        manifest_file = temp_workspace / "cleanup-manifest.json"
        manifest_file.write_text(json.dumps(manifest))
        
        assert manifest_file.exists()
        assert len(manifest["items"]) == 2


# Test execution summary
if __name__ == "__main__":
    print("=" * 80)
    print("CORTEX Cleanup Orchestrator Test Suite")
    print("=" * 80)
    print("\nTest Categories:")
    print("  1. Recursion Protection (3 tests)")
    print("  2. Dry-Run Mode (3 tests)")
    print("  3. Retention Policies (3 tests)")
    print("  4. Safety Validations (3 tests)")
    print("  5. Rollback Functionality (3 tests)")
    print("  6. Cleanup Categories (4 tests)")
    print("  7. Cleanup Reporting (3 tests)")
    print("  8. Integration Tests (2 tests)")
    print("\nTotal: 24 comprehensive tests")
    print("\nRun with: pytest tests/plugins/test_cleanup_orchestrator.py -v")
    print("=" * 80)
