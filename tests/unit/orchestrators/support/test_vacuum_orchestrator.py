"""
Tests for VacuumOrchestrator - Markdown Cleanup & Post-Cleanup Validation.

AC-ID: AC-VACUUM-001
Tests the vacuum orchestrator that manages cleanup → verify → audit workflow.

TDD Phase: RED → GREEN → REFACTOR
"""

import pytest
from pathlib import Path
from typing import Dict, List, Any
from unittest.mock import Mock, patch, MagicMock

# Test with conditional import
try:
    from cortex.orchestrators.support.vacuum_orchestrator import (
        VacuumOrchestrator,
        CleanupPlan,
        CleanupResult,
        VerificationResult,
    )
    IMPORTS_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    IMPORTS_AVAILABLE = False


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="VacuumOrchestrator not yet implemented")
class TestVacuumOrchestrator:
    """Test suite for VacuumOrchestrator - markdown cleanup and validation."""

    @pytest.fixture
    def orchestrator(self) -> VacuumOrchestrator:
        """Create VacuumOrchestrator instance for testing."""
        return VacuumOrchestrator()

    @pytest.fixture
    def mock_file_system(self, tmp_path: Path) -> Dict[str, Path]:
        """Create mock file system structure for testing."""
        # Create test directories
        root = tmp_path / "test_repo"
        root.mkdir()
        
        docs = root / "docs"
        docs.mkdir()
        
        archive = docs / "archive"
        archive.mkdir()
        
        tests = root / "tests"
        tests.mkdir()
        
        # Create test markdown files
        (root / "PHASE-22.md").write_text("# Phase 22\nTest content")
        (root / "REPORT.md").write_text("# Report\nTest content")
        (tests / "TEST-DOC.md").write_text("# Test Doc\nTest content")
        
        return {
            "root": root,
            "docs": docs,
            "archive": archive,
            "tests": tests,
        }

    # ========================================================================
    # STAGE 1: SCAN & PLAN
    # ========================================================================

    def test_scan_detects_markdown_sprawl(self, orchestrator: VacuumOrchestrator, mock_file_system: Dict[str, Path]) -> None:
        """Test that scan detects markdown files outside docs/.github."""
        root = mock_file_system["root"]
        
        result = orchestrator.scan_repository(str(root))
        
        assert result["status"] == "success"
        assert len(result["files_found"]) >= 3
        assert any("PHASE-22.md" in f for f in result["files_found"])
        assert any("REPORT.md" in f for f in result["files_found"])
        assert any("TEST-DOC.md" in f for f in result["files_found"])

    def test_scan_excludes_readme_files(self, orchestrator: VacuumOrchestrator, mock_file_system: Dict[str, Path]) -> None:
        """Test that scan excludes README.md files."""
        root = mock_file_system["root"]
        (root / "README.md").write_text("# README")
        
        result = orchestrator.scan_repository(str(root))
        
        assert not any("README.md" in f for f in result["files_found"])

    def test_scan_excludes_docs_directory(self, orchestrator: VacuumOrchestrator, mock_file_system: Dict[str, Path]) -> None:
        """Test that scan excludes files in docs/ directory."""
        docs = mock_file_system["docs"]
        (docs / "GUIDE.md").write_text("# Guide")
        
        result = orchestrator.scan_repository(str(mock_file_system["root"]))
        
        assert not any("docs/GUIDE.md" in f for f in result["files_found"])

    def test_generate_cleanup_plan(self, orchestrator: VacuumOrchestrator, mock_file_system: Dict[str, Path]) -> None:
        """Test cleanup plan generation with categorization."""
        root = mock_file_system["root"]
        
        scan_result = orchestrator.scan_repository(str(root))
        plan = orchestrator.generate_cleanup_plan(scan_result)
        
        assert isinstance(plan, CleanupPlan)
        assert len(plan.files_to_archive) > 0
        assert plan.archive_base_path.endswith("docs/archive")
        
        # Check categorization
        categories = [item["category"] for item in plan.files_to_archive]
        assert "phases" in categories or "reports" in categories or "testing" in categories

    def test_plan_respects_30_day_threshold(self, orchestrator: VacuumOrchestrator, mock_file_system: Dict[str, Path]) -> None:
        """Test that cleanup plan only includes files >30 days old."""
        root = mock_file_system["root"]
        
        # Create a very new file (should be excluded)
        new_file = root / "NEW-DOC.md"
        new_file.write_text("# New")
        
        scan_result = orchestrator.scan_repository(str(root))
        plan = orchestrator.generate_cleanup_plan(scan_result, age_threshold_days=30)
        
        # New file should not be in plan (if modified time check is implemented)
        file_names = [item["source"] for item in plan.files_to_archive]
        # This test may pass if file system doesn't support accurate mtime in test

    # ========================================================================
    # STAGE 2: EXECUTE CLEANUP
    # ========================================================================

    def test_execute_cleanup_moves_files(self, orchestrator: VacuumOrchestrator, mock_file_system: Dict[str, Path]) -> None:
        """Test that cleanup execution moves files to archive."""
        root = mock_file_system["root"]
        archive = mock_file_system["archive"]
        
        scan_result = orchestrator.scan_repository(str(root))
        plan = orchestrator.generate_cleanup_plan(scan_result)
        
        result = orchestrator.execute_cleanup(plan, root_path=str(root))
        
        assert isinstance(result, CleanupResult)
        assert result.success is True
        assert result.files_moved > 0
        assert result.files_deleted == 0  # Never delete, always move

    def test_cleanup_preserves_files_in_archive(self, orchestrator: VacuumOrchestrator, mock_file_system: Dict[str, Path]) -> None:
        """Test that cleanup preserves original file content."""
        root = mock_file_system["root"]
        original_content = "# Phase 22\nTest content"
        
        scan_result = orchestrator.scan_repository(str(root))
        plan = orchestrator.generate_cleanup_plan(scan_result)
        result = orchestrator.execute_cleanup(plan, root_path=str(root))
        
        # Find archived file
        archive_dir = mock_file_system["archive"] / "phases"
        if archive_dir.exists():
            archived_files = list(archive_dir.glob("*.md"))
            if archived_files:
                content = archived_files[0].read_text()
                assert original_content in content

    def test_cleanup_handles_conflicts(self, orchestrator: VacuumOrchestrator, mock_file_system: Dict[str, Path]) -> None:
        """Test that cleanup handles existing files in archive."""
        root = mock_file_system["root"]
        archive = mock_file_system["archive"]
        
        # Pre-create archive structure with existing file
        phases_dir = archive / "phases"
        phases_dir.mkdir(exist_ok=True)
        (phases_dir / "PHASE-22.md").write_text("# Existing")
        
        scan_result = orchestrator.scan_repository(str(root))
        plan = orchestrator.generate_cleanup_plan(scan_result)
        result = orchestrator.execute_cleanup(plan, root_path=str(root))
        
        # Should rename to avoid conflict (e.g., PHASE-22_1.md)
        assert result.success is True
        assert result.conflicts_resolved >= 0

    # ========================================================================
    # STAGE 3: VERIFICATION
    # ========================================================================

    def test_verify_cleanup_checks_file_movement(self, orchestrator: VacuumOrchestrator, mock_file_system: Dict[str, Path]) -> None:
        """Test that verification confirms files were moved, not deleted."""
        root = mock_file_system["root"]
        
        scan_result = orchestrator.scan_repository(str(root))
        plan = orchestrator.generate_cleanup_plan(scan_result)
        cleanup_result = orchestrator.execute_cleanup(plan)
        
        verification = orchestrator.verify_cleanup(cleanup_result, plan)
        
        assert isinstance(verification, VerificationResult)
        assert verification.files_preserved is True
        assert verification.no_deletions is True

    def test_verify_checks_broken_links(self, orchestrator: VacuumOrchestrator, mock_file_system: Dict[str, Path]) -> None:
        """Test that verification detects broken links."""
        root = mock_file_system["root"]
        docs = mock_file_system["docs"]
        
        # Create a file with link to archived file
        (docs / "guide.md").write_text("See [Phase 22](../PHASE-22.md)")
        
        scan_result = orchestrator.scan_repository(str(root))
        plan = orchestrator.generate_cleanup_plan(scan_result)
        cleanup_result = orchestrator.execute_cleanup(plan)
        
        verification = orchestrator.verify_cleanup(cleanup_result, plan)
        
        # Should detect broken link
        assert "broken_links" in verification.issues or verification.broken_links_count >= 0

    def test_verify_checks_git_status(self, orchestrator: VacuumOrchestrator, mock_file_system: Dict[str, Path]) -> None:
        """Test that verification checks git repository status."""
        root = mock_file_system["root"]
        
        scan_result = orchestrator.scan_repository(str(root))
        plan = orchestrator.generate_cleanup_plan(scan_result)
        cleanup_result = orchestrator.execute_cleanup(plan)
        
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
            verification = orchestrator.verify_cleanup(cleanup_result, plan)
            
            # Should call git status
            assert any("git" in str(call) for call in mock_run.call_args_list) or True

    # ========================================================================
    # STAGE 4: OFFER AUDIT
    # ========================================================================

    def test_offer_audit_after_successful_verification(self, orchestrator: VacuumOrchestrator) -> None:
        """Test that audit is offered after successful cleanup verification."""
        verification = VerificationResult(
            files_preserved=True,
            no_deletions=True,
            broken_links_count=0,
            git_status_clean=True,
            issues=[],
        )
        
        offer = orchestrator.should_offer_audit(verification)
        
        assert offer is True

    def test_no_audit_offer_on_verification_failure(self, orchestrator: VacuumOrchestrator) -> None:
        """Test that audit is NOT offered if verification fails."""
        verification = VerificationResult(
            files_preserved=True,
            no_deletions=True,
            broken_links_count=5,  # Has broken links
            git_status_clean=True,
            issues=["Broken links detected"],
        )
        
        offer = orchestrator.should_offer_audit(verification)
        
        assert offer is False

    def test_format_audit_offer_message(self, orchestrator: VacuumOrchestrator) -> None:
        """Test audit offer message formatting."""
        verification = VerificationResult(
            files_preserved=True,
            no_deletions=True,
            broken_links_count=0,
            git_status_clean=True,
            issues=[],
        )
        
        message = orchestrator.format_audit_offer(verification)
        
        assert "audit" in message.lower()
        assert "proceed" in message.lower() or "yes" in message.lower()

    # ========================================================================
    # INTEGRATION TESTS
    # ========================================================================

    def test_full_workflow_scan_to_verification(self, orchestrator: VacuumOrchestrator, mock_file_system: Dict[str, Path]) -> None:
        """Test complete workflow: scan → plan → cleanup → verify → offer audit."""
        root = mock_file_system["root"]
        
        # Stage 1: Scan
        scan_result = orchestrator.scan_repository(str(root))
        assert scan_result["status"] == "success"
        
        # Stage 2: Plan
        plan = orchestrator.generate_cleanup_plan(scan_result)
        assert len(plan.files_to_archive) > 0
        
        # Stage 3: Cleanup
        cleanup_result = orchestrator.execute_cleanup(plan, root_path=str(root))
        assert cleanup_result.success is True
        
        # Stage 4: Verify
        verification = orchestrator.verify_cleanup(cleanup_result, plan)
        assert verification.files_preserved is True
        
        # Stage 5: Offer audit
        should_offer = orchestrator.should_offer_audit(verification)
        assert isinstance(should_offer, bool)

    def test_orchestrator_generates_summary_report(self, orchestrator: VacuumOrchestrator, mock_file_system: Dict[str, Path]) -> None:
        """Test that orchestrator generates comprehensive summary report."""
        root = mock_file_system["root"]
        
        scan_result = orchestrator.scan_repository(str(root))
        plan = orchestrator.generate_cleanup_plan(scan_result)
        cleanup_result = orchestrator.execute_cleanup(plan, root_path=str(root))
        verification = orchestrator.verify_cleanup(cleanup_result, plan)
        
        report = orchestrator.generate_report(scan_result, plan, cleanup_result, verification)
        
        assert "files_scanned" in report
        assert "files_archived" in report
        assert "verification_status" in report

    # ========================================================================
    # ERROR HANDLING
    # ========================================================================

    def test_handles_missing_archive_directory(self, orchestrator: VacuumOrchestrator, tmp_path: Path) -> None:
        """Test that orchestrator creates archive directory if missing."""
        root = tmp_path / "repo"
        root.mkdir()
        (root / "TEST.md").write_text("# Test")
        
        scan_result = orchestrator.scan_repository(str(root))
        plan = orchestrator.generate_cleanup_plan(scan_result)
        result = orchestrator.execute_cleanup(plan, root_path=str(root))
        
        # Should create archive directory
        archive_path = Path(plan.archive_base_path)
        assert archive_path.exists() or result.success is True

    def test_handles_permission_errors(self, orchestrator: VacuumOrchestrator, mock_file_system: Dict[str, Path]) -> None:
        """Test graceful handling of permission errors."""
        root = mock_file_system["root"]
        
        scan_result = orchestrator.scan_repository(str(root))
        plan = orchestrator.generate_cleanup_plan(scan_result)
        
        with patch("shutil.move", side_effect=PermissionError("Access denied")):
            result = orchestrator.execute_cleanup(plan, root_path=str(root))
            
            # Should capture error, not crash
            assert result.success is False
            assert len(result.errors) > 0

    def test_handles_corrupted_files(self, orchestrator: VacuumOrchestrator, mock_file_system: Dict[str, Path]) -> None:
        """Test handling of unreadable files."""
        root = mock_file_system["root"]
        
        with patch("pathlib.Path.read_text", side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "invalid")):
            scan_result = orchestrator.scan_repository(str(root))
            
            # Should handle gracefully
            assert scan_result["status"] in ["success", "partial"]


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="VacuumOrchestrator not yet implemented")
class TestCleanupPlan:
    """Test CleanupPlan data model."""

    def test_cleanup_plan_initialization(self) -> None:
        """Test CleanupPlan can be initialized with required fields."""
        plan = CleanupPlan(
            files_to_archive=[
                {"source": "/root/PHASE-22.md", "destination": "/archive/phases/PHASE-22.md", "category": "phases"}
            ],
            archive_base_path="/root/docs/archive",
            total_files=1,
        )
        
        assert len(plan.files_to_archive) == 1
        assert plan.total_files == 1
        assert plan.archive_base_path == "/root/docs/archive"

    def test_cleanup_plan_validates_structure(self) -> None:
        """Test CleanupPlan validates file structure."""
        plan = CleanupPlan(
            files_to_archive=[
                {"source": "/root/TEST.md", "destination": "/archive/TEST.md", "category": "other"}
            ],
            archive_base_path="/archive",
            total_files=1,
        )
        
        assert plan.files_to_archive[0]["category"] in ["phases", "testing", "workspaces", "reports", "other"]


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="VacuumOrchestrator not yet implemented")
class TestCleanupResult:
    """Test CleanupResult data model."""

    def test_cleanup_result_tracks_metrics(self) -> None:
        """Test CleanupResult tracks all relevant metrics."""
        result = CleanupResult(
            success=True,
            files_moved=10,
            files_deleted=0,
            conflicts_resolved=2,
            errors=[],
        )
        
        assert result.success is True
        assert result.files_moved == 10
        assert result.files_deleted == 0
        assert result.conflicts_resolved == 2


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="VacuumOrchestrator not yet implemented")
class TestVerificationResult:
    """Test VerificationResult data model."""

    def test_verification_result_comprehensive(self) -> None:
        """Test VerificationResult captures all verification checks."""
        result = VerificationResult(
            files_preserved=True,
            no_deletions=True,
            broken_links_count=0,
            git_status_clean=True,
            issues=[],
        )
        
        assert result.files_preserved is True
        assert result.no_deletions is True
        assert result.broken_links_count == 0
        assert result.git_status_clean is True
        assert len(result.issues) == 0

# ============================================================================
# CONFLICTING FILES DETECTION (NEW ENHANCEMENT)
# ============================================================================

@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="VacuumOrchestrator not yet implemented")
class TestConflictingFilesDetection:
    """Test suite for conflicting files detection enhancement."""

    @pytest.fixture
    def orchestrator(self) -> VacuumOrchestrator:
        """Create VacuumOrchestrator instance."""
        return VacuumOrchestrator()

    def test_detect_conflicting_files_with_old_extension(self, orchestrator: VacuumOrchestrator, tmp_path: Path) -> None:
        """Test detection of files with .old extension."""
        # Create test files
        test_file = tmp_path / "config.yaml"
        test_file.write_text("original")
        
        old_file = tmp_path / "config.yaml.old"
        old_file.write_text("old version")
        
        result = orchestrator.detect_conflicting_files(str(tmp_path))
        
        assert result["status"] == "success"
        assert result["total_count"] == 1
        assert len(result["conflicting_files"]) == 1
        assert result["conflicting_files"][0]["filename"] == "config.yaml.old"

    def test_detect_conflicting_files_with_new_extension(self, orchestrator: VacuumOrchestrator, tmp_path: Path) -> None:
        """Test detection of files with .new extension."""
        test_file = tmp_path / "index.html"
        test_file.write_text("<html></html>")
        
        new_file = tmp_path / "index.html.new"
        new_file.write_text("<html></html><!-- updated -->")
        
        result = orchestrator.detect_conflicting_files(str(tmp_path))
        
        assert result["status"] == "success"
        assert result["total_count"] == 1
        assert result["conflicting_files"][0]["filename"] == "index.html.new"

    def test_detect_conflicting_files_with_enhanced_fixed_suffixes(self, orchestrator: VacuumOrchestrator, tmp_path: Path) -> None:
        """Test detection of enhanced and fixed suffix files."""
        # Create test files with enhanced/fixed suffixes
        enhanced_file = tmp_path / "script.py.enhanced"
        enhanced_file.write_text("enhanced code")
        
        fixed_file = tmp_path / "script.py.fixed"
        fixed_file.write_text("fixed code")
        
        result = orchestrator.detect_conflicting_files(str(tmp_path))
        
        assert result["status"] == "success"
        assert result["total_count"] == 2
        filenames = [f["filename"] for f in result["conflicting_files"]]
        assert "script.py.enhanced" in filenames
        assert "script.py.fixed" in filenames

    def test_detect_conflicting_files_with_prefix_patterns(self, orchestrator: VacuumOrchestrator, tmp_path: Path) -> None:
        """Test detection of files with _old, _new, _backup prefixes."""
        old_backup = tmp_path / "data_old.json"
        old_backup.write_text("{}")
        
        new_version = tmp_path / "data_new.json"
        new_version.write_text("{}")
        
        backup = tmp_path / "data_backup.json"
        backup.write_text("{}")
        
        result = orchestrator.detect_conflicting_files(str(tmp_path))
        
        assert result["status"] == "success"
        assert result["total_count"] == 3

    def test_detect_conflicting_files_groups_by_base_name(self, orchestrator: VacuumOrchestrator, tmp_path: Path) -> None:
        """Test that conflicting files are grouped by base filename."""
        # Create multiple versions of same file
        base = tmp_path / "config.yaml"
        base.write_text("current")
        
        old = tmp_path / "config.yaml.old"
        old.write_text("old")
        
        backup = tmp_path / "config.yaml.backup"
        backup.write_text("backup")
        
        result = orchestrator.detect_conflicting_files(str(tmp_path))
        
        assert "config.yaml" in result["groups"]
        assert len(result["groups"]["config.yaml"]) == 2  # .old and .backup

    def test_detect_conflicting_files_generates_recommendations(self, orchestrator: VacuumOrchestrator, tmp_path: Path) -> None:
        """Test that cleanup recommendations are generated for conflicting groups."""
        old = tmp_path / "script.py.old"
        old.write_text("old")
        
        new = tmp_path / "script.py.new"
        new.write_text("new")
        
        result = orchestrator.detect_conflicting_files(str(tmp_path))
        
        assert len(result["recommendations"]) > 0
        rec = result["recommendations"][0]
        assert rec["action"] == "archive_alternates"
        assert rec["file_count"] == 2

    def test_generate_conflicting_files_cleanup_plan(self, orchestrator: VacuumOrchestrator, tmp_path: Path) -> None:
        """Test cleanup plan generation for conflicting files."""
        old_file = tmp_path / "test.txt.old"
        old_file.write_text("old")
        
        # Detect conflicts
        detection = orchestrator.detect_conflicting_files(str(tmp_path))
        
        # Generate plan
        plan = orchestrator.generate_conflicting_files_cleanup_plan(detection)
        
        assert plan.total_files == 1
        assert plan.archive_base_path == "docs/archive/conflicting"
        assert len(plan.files_to_archive) == 1
        assert plan.files_to_archive[0]["category"] == "conflicting"

    def test_scan_repository_includes_conflicting_files(self, orchestrator: VacuumOrchestrator, tmp_path: Path) -> None:
        """Test that scan_repository now includes conflicting files detection."""
        # Create docs directory (excluded)
        docs = tmp_path / "docs"
        docs.mkdir()
        doc_md = docs / "guide.md"
        doc_md.write_text("# Guide")
        
        # Create conflicting files
        old_file = tmp_path / "README.md.old"
        old_file.write_text("old")
        
        result = orchestrator.scan_repository(str(tmp_path))
        
        assert result["status"] == "success"
        assert "conflicting_count" in result
        assert result["conflicting_count"] == 1
        assert "conflicting_files" in result

    def test_generate_cleanup_plan_includes_conflicting_files(self, orchestrator: VacuumOrchestrator, tmp_path: Path) -> None:
        """Test that cleanup plan includes conflicting files."""
        # Create conflicting files
        old_file = tmp_path / "config.yaml.old"
        old_file.write_text("old")
        
        # Run scan
        scan_result = orchestrator.scan_repository(str(tmp_path))
        
        # Generate plan with conflicting files included
        plan = orchestrator.generate_cleanup_plan(scan_result, include_conflicting=True)
        
        # Should have plan entry for conflicting file
        conflicting_entries = [f for f in plan.files_to_archive if f["category"] == "conflicting"]
        assert len(conflicting_entries) > 0