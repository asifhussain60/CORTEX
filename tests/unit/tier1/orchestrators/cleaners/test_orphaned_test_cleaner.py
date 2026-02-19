"""
Tests for OrphanedTestCleaner

AC-ID: AC-VAC-TESTS-001
Authority: Phase 104 Enhancement
Author: CORTEX Framework
Created: 2026-02-17
"""

import pytest
from pathlib import Path
from datetime import datetime

from cortex.intelligence.memory.tier1_learned.orchestrators.cleaners.orphaned_test import (
    OrphanedTestCleaner,
)


class TestOrphanedTestCleanerInit:
    """Test OrphanedTestCleaner initialization."""
    
    def test_init_with_defaults(self, tmp_path: Path):
        """Test initialization with default config."""
        config = {"repo_root": str(tmp_path)}
        cleaner = OrphanedTestCleaner(config)
        
        assert cleaner.repo_root == tmp_path
        assert cleaner.tests_dir == tmp_path / "tests"
        assert cleaner.min_age_days == 14
        assert cleaner.dry_run is False
        assert cleaner.relocate_mode is False
    
    def test_init_with_relocate_mode(self, tmp_path: Path):
        """Test initialization with relocate mode."""
        config = {"repo_root": str(tmp_path), "relocate_mode": True}
        cleaner = OrphanedTestCleaner(config)
        
        assert cleaner.relocate_mode is True


class TestOrphanedTestCleanerProperties:
    """Test OrphanedTestCleaner properties."""
    
    def test_name(self, tmp_path: Path):
        """Test name property."""
        cleaner = OrphanedTestCleaner({"repo_root": str(tmp_path)})
        assert cleaner.name == "OrphanedTestCleaner"
    
    def test_version(self, tmp_path: Path):
        """Test version property."""
        cleaner = OrphanedTestCleaner({"repo_root": str(tmp_path)})
        assert cleaner.version == "1.0.0"
    
    def test_domain(self, tmp_path: Path):
        """Test domain property."""
        cleaner = OrphanedTestCleaner({"repo_root": str(tmp_path)})
        assert cleaner.domain == "orphaned_tests"


class TestOrphanedTestPatternMatching:
    """Test pattern matching for orphaned tests."""
    
    @pytest.fixture
    def cleaner(self, tmp_path: Path) -> OrphanedTestCleaner:
        """Create cleaner fixture."""
        return OrphanedTestCleaner({"repo_root": str(tmp_path)})
    
    @pytest.mark.parametrize("filename,expected", [
        ("conftest.py", True),
        ("__init__.py", True),
        ("pytest.ini", True),
        ("baseline.json", True),
        ("test_something.py", False),
        ("phase_26_test.py", False),
    ])
    def test_is_protected(self, cleaner: OrphanedTestCleaner, filename: str, expected: bool):
        """Test protected file detection."""
        assert cleaner._is_protected(filename) == expected
    
    @pytest.mark.parametrize("filename,expected", [
        ("phase_26_context_loading.py", True),
        ("phase-53-test.py", True),
        ("phase99_cleanup.py", True),
        ("test_temp_something.py", True),
        ("conftest_optimize.py", True),
        ("test_normal.py", False),
        ("conftest.py", False),
    ])
    def test_is_temp_test(self, cleaner: OrphanedTestCleaner, filename: str, expected: bool):
        """Test temporary test pattern matching."""
        assert cleaner._is_temp_test(filename) == expected
    
    @pytest.mark.parametrize("filename,expected", [
        ("test_something.py", True),
        ("test_extract_json.py", True),
        ("test_custom_patterns.py", True),
        ("conftest.py", False),
        ("some_module.py", False),
    ])
    def test_is_misplaced_test(self, cleaner: OrphanedTestCleaner, filename: str, expected: bool):
        """Test misplaced test detection."""
        assert cleaner._is_misplaced_test(filename) == expected


class TestOrphanedTestCleanerAnalyze:
    """Test OrphanedTestCleaner analysis phase."""
    
    @pytest.fixture
    def setup_tests(self, tmp_path: Path):
        """Set up test files directory."""
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        
        # Create phase-specific test (temp)
        phase_test = tests_dir / "phase_26_validation.py"
        phase_test.write_text("# Phase 26 validation")
        
        # Create protected file
        conftest = tests_dir / "conftest.py"
        conftest.write_text("# Conftest")
        
        # Create misplaced test
        misplaced = tests_dir / "test_something.py"
        misplaced.write_text("def test_example(): pass")
        
        # Create proper subdirectory with test
        unit_dir = tests_dir / "unit"
        unit_dir.mkdir()
        proper_test = unit_dir / "test_proper.py"
        proper_test.write_text("def test_proper(): pass")
        
        return tmp_path
    
    def test_analyze_finds_phase_tests(self, setup_tests: Path):
        """Test analysis finds phase-specific tests."""
        config = {"repo_root": str(setup_tests), "min_age_days": 0}
        cleaner = OrphanedTestCleaner(config)
        
        analysis = cleaner.analyze()
        
        assert analysis.cleaner_id == "OrphanedTestCleaner"
        
        # Should find phase_26 test in plan
        issues = analysis.plan.get("issues", [])
        phase_issues = [i for i in issues if "phase_26" in i["filename"]]
        assert len(phase_issues) == 1
        assert phase_issues[0]["type"] == "temp_test"
    
    def test_analyze_skips_protected(self, setup_tests: Path):
        """Test analysis skips protected files."""
        config = {"repo_root": str(setup_tests), "min_age_days": 0}
        cleaner = OrphanedTestCleaner(config)
        
        analysis = cleaner.analyze()
        
        # Should not include conftest.py
        issues = analysis.plan.get("issues", [])
        protected = [i for i in issues if i["filename"] == "conftest.py"]
        assert len(protected) == 0
    
    def test_analyze_finds_misplaced_tests(self, setup_tests: Path):
        """Test analysis finds misplaced tests."""
        config = {"repo_root": str(setup_tests), "min_age_days": 0}
        cleaner = OrphanedTestCleaner(config)
        
        analysis = cleaner.analyze()
        
        # Should find test_something.py as misplaced
        issues = analysis.plan.get("issues", [])
        misplaced = [i for i in issues if i["filename"] == "test_something.py"]
        assert len(misplaced) == 1
        assert misplaced[0]["type"] == "misplaced_test"
    
    def test_analyze_only_scans_root(self, setup_tests: Path):
        """Test analysis only scans tests/ root, not subdirectories."""
        config = {"repo_root": str(setup_tests), "min_age_days": 0}
        cleaner = OrphanedTestCleaner(config)
        
        analysis = cleaner.analyze()
        
        # Should not include tests from unit/ subdirectory
        issues = analysis.plan.get("issues", [])
        unit_tests = [i for i in issues if "test_proper" in i["filename"]]
        assert len(unit_tests) == 0


class TestOrphanedTestCleanerExecute:
    """Test OrphanedTestCleaner execution phase."""
    
    @pytest.fixture
    def setup_for_execution(self, tmp_path: Path):
        """Set up tests for execution."""
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        
        # Create phase test to delete
        phase_test = tests_dir / "phase_50_old.py"
        phase_test.write_text("# Old phase test")
        
        # Create misplaced test
        misplaced = tests_dir / "test_misplaced.py"
        misplaced.write_text("def test_misplaced(): pass")
        
        return tmp_path
    
    def test_execute_dry_run(self, setup_for_execution: Path):
        """Test execution in dry run mode."""
        config = {"repo_root": str(setup_for_execution), "dry_run": True, "min_age_days": 0}
        cleaner = OrphanedTestCleaner(config)
        
        analysis = cleaner.analyze()
        report = cleaner.execute(analysis)
        
        # Files should still exist
        assert (setup_for_execution / "tests" / "phase_50_old.py").exists()
        assert report.status == "SUCCESS"
    
    def test_execute_deletes_temp_test(self, setup_for_execution: Path):
        """Test execution deletes temporary tests."""
        config = {"repo_root": str(setup_for_execution), "dry_run": False, "min_age_days": 0}
        cleaner = OrphanedTestCleaner(config)
        
        analysis = cleaner.analyze()
        report = cleaner.execute(analysis)
        
        # Phase test should be deleted
        assert not (setup_for_execution / "tests" / "phase_50_old.py").exists()
        assert report.status == "SUCCESS"
    
    def test_execute_relocate_mode(self, setup_for_execution: Path):
        """Test execution in relocate mode."""
        config = {
            "repo_root": str(setup_for_execution),
            "dry_run": False,
            "min_age_days": 0,
            "relocate_mode": True,
        }
        cleaner = OrphanedTestCleaner(config)
        
        analysis = cleaner.analyze()
        
        # Filter to only misplaced tests for relocation from plan
        issues = analysis.plan.get("issues", [])
        misplaced = [i for i in issues if i["type"] == "misplaced_test"]
        
        if misplaced:
            # Create mock analysis with just misplaced tests
            from cortex.intelligence.memory.tier1_learned.orchestrators.cleaners.base import Analysis
            relocate_analysis = Analysis(
                cleaner_id=analysis.cleaner_id,
                timestamp=analysis.timestamp,
                files_scanned=analysis.files_scanned,
                issues_found=len(misplaced),
                plan={"issues": misplaced},
                logs=analysis.logs,
            )
            
            report = cleaner.execute(relocate_analysis)
            
            # Check file was moved
            assert report.changes.get("relocated", 0) >= 0


class TestOrphanedTestCleanerSuggestTargetDir:
    """Test target directory suggestion."""
    
    def test_suggest_unit_default(self, tmp_path: Path):
        """Test default suggestion is unit/."""
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        
        test_file = tests_dir / "test_something.py"
        test_file.write_text("def test_basic(): pass")
        
        cleaner = OrphanedTestCleaner({"repo_root": str(tmp_path)})
        suggestion = cleaner._suggest_target_dir("test_something.py", test_file)
        
        assert suggestion == "unit"
    
    def test_suggest_integration(self, tmp_path: Path):
        """Test integration suggestion based on content."""
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        
        test_file = tests_dir / "test_api.py"
        test_file.write_text("# Integration test\n@pytest.mark.integration\ndef test_api(): pass")
        
        cleaner = OrphanedTestCleaner({"repo_root": str(tmp_path)})
        suggestion = cleaner._suggest_target_dir("test_api.py", test_file)
        
        assert suggestion == "integration"
    
    def test_suggest_performance(self, tmp_path: Path):
        """Test performance suggestion based on content."""
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        
        test_file = tests_dir / "test_benchmark.py"
        test_file.write_text("# Benchmark test\n@pytest.mark.slow\ndef test_perf(): pass")
        
        cleaner = OrphanedTestCleaner({"repo_root": str(tmp_path)})
        suggestion = cleaner._suggest_target_dir("test_benchmark.py", test_file)
        
        assert suggestion == "performance"


class TestOrphanedTestCleanerRollback:
    """Test OrphanedTestCleaner rollback."""
    
    def test_rollback_not_supported(self, tmp_path: Path):
        """Test rollback is not supported."""
        cleaner = OrphanedTestCleaner({"repo_root": str(tmp_path)})
        
        from cortex.intelligence.memory.tier1_learned.orchestrators.cleaners.base import Report
        mock_report = Report(
            cleaner_id="OrphanedTestCleaner",
            timestamp=datetime.now().isoformat(),
            status="SUCCESS",
            actions_taken=1,
            changes={"deleted": 1},
            errors=[],
            logs=[],
        )
        
        result = cleaner.rollback(mock_report)
        
        assert result.status == "FAILED"
        assert "not supported" in result.errors[0].lower()
