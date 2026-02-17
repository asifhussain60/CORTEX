"""
Tests for TempScriptCleaner

AC-ID: AC-VAC-SCRIPTS-001
Authority: Phase 104 Enhancement
Author: CORTEX Framework
Created: 2026-02-17
"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from cortex_intelligence.memory.tier1_learned.orchestrators.cleaners.temp_script import (
    TempScriptCleaner,
)


class TestTempScriptCleanerInit:
    """Test TempScriptCleaner initialization."""
    
    def test_init_with_defaults(self, tmp_path: Path):
        """Test initialization with default config."""
        config = {"repo_root": str(tmp_path)}
        cleaner = TempScriptCleaner(config)
        
        assert cleaner.repo_root == tmp_path
        assert cleaner.scripts_dir == tmp_path / "scripts"
        assert cleaner.min_age_days == 30
        assert cleaner.dry_run is False
    
    def test_init_with_custom_age(self, tmp_path: Path):
        """Test initialization with custom min_age_days."""
        config = {"repo_root": str(tmp_path), "min_age_days": 7}
        cleaner = TempScriptCleaner(config)
        
        assert cleaner.min_age_days == 7
    
    def test_init_with_dry_run(self, tmp_path: Path):
        """Test initialization with dry_run enabled."""
        config = {"repo_root": str(tmp_path), "dry_run": True}
        cleaner = TempScriptCleaner(config)
        
        assert cleaner.dry_run is True


class TestTempScriptCleanerProperties:
    """Test TempScriptCleaner properties."""
    
    def test_name(self, tmp_path: Path):
        """Test name property."""
        cleaner = TempScriptCleaner({"repo_root": str(tmp_path)})
        assert cleaner.name == "TempScriptCleaner"
    
    def test_version(self, tmp_path: Path):
        """Test version property."""
        cleaner = TempScriptCleaner({"repo_root": str(tmp_path)})
        assert cleaner.version == "1.0.0"
    
    def test_domain(self, tmp_path: Path):
        """Test domain property."""
        cleaner = TempScriptCleaner({"repo_root": str(tmp_path)})
        assert cleaner.domain == "temp_scripts"


class TestTempScriptPatternMatching:
    """Test pattern matching for temporary scripts."""
    
    @pytest.fixture
    def cleaner(self, tmp_path: Path) -> TempScriptCleaner:
        """Create cleaner fixture."""
        return TempScriptCleaner({"repo_root": str(tmp_path)})
    
    @pytest.mark.parametrize("filename,expected", [
        ("phase-81-add-metadata.py", True),
        ("phase25_wiring_audit.py", True),
        ("phase_99_cleanup.py", True),
        ("consolidate_phases.py", True),
        ("restore_cortex_master.py", True),
        ("migrate_data.py", True),
        ("fix_test_imports.py", True),
        ("validate-production.py", True),
        ("execute_validation_suite.py", True),
        ("batch_generate_tests.py", True),
        ("cleanup-nomenclature.py", True),
        ("eliminate_redirect_stubs.py", True),
        ("sanitize-company-refs.py", True),
        ("enforce-test-naming.py", True),
        ("add_cortex_semantic_ids.py", True),
        ("update_archived_paths.py", True),
        # Non-temp patterns
        ("vacuum-runner.py", False),
        ("setup-mcp.py", False),
        ("run-tests.sh", False),
        ("build-docs-site.py", False),
        ("some_normal_script.py", False),
    ])
    def test_is_temp_script(self, cleaner: TempScriptCleaner, filename: str, expected: bool):
        """Test temp script pattern matching."""
        assert cleaner._is_temp_script(filename) == expected
    
    @pytest.mark.parametrize("filename,expected", [
        ("vacuum-runner.py", True),
        ("setup-mcp.py", True),
        ("run-tests.sh", True),
        ("build-docs-site.py", True),
        ("enhanced_cleanup.py", True),
        ("phase-81-something.py", False),
    ])
    def test_is_protected(self, cleaner: TempScriptCleaner, filename: str, expected: bool):
        """Test protected script detection."""
        assert cleaner._is_protected(filename) == expected


class TestTempScriptCleanerAnalyze:
    """Test TempScriptCleaner analysis phase."""
    
    @pytest.fixture
    def setup_scripts(self, tmp_path: Path):
        """Set up test scripts directory."""
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir()
        
        # Create temp script (old)
        old_script = scripts_dir / "phase-81-old.py"
        old_script.write_text("# Old phase script")
        
        # Create protected script
        protected = scripts_dir / "vacuum-runner.py"
        protected.write_text("# Protected")
        
        # Create normal script (not matching temp pattern)
        normal = scripts_dir / "some_utility.py"
        normal.write_text("# Utility script")
        
        return tmp_path
    
    def test_analyze_finds_temp_scripts(self, setup_scripts: Path):
        """Test analysis finds temporary scripts."""
        config = {"repo_root": str(setup_scripts), "min_age_days": 0}
        cleaner = TempScriptCleaner(config)
        
        with patch.object(cleaner, "_has_uncommitted_changes", return_value=False):
            analysis = cleaner.analyze()
        
        assert analysis.cleaner_id == "TempScriptCleaner"
        assert analysis.files_scanned >= 1
        
        # Should find phase-81-old.py in plan
        issues = analysis.plan.get("issues", [])
        temp_issues = [i for i in issues if "phase-81" in i["filename"]]
        assert len(temp_issues) == 1
    
    def test_analyze_skips_protected(self, setup_scripts: Path):
        """Test analysis skips protected scripts."""
        config = {"repo_root": str(setup_scripts), "min_age_days": 0}
        cleaner = TempScriptCleaner(config)
        
        with patch.object(cleaner, "_has_uncommitted_changes", return_value=False):
            analysis = cleaner.analyze()
        
        # Should not include protected scripts
        issues = analysis.plan.get("issues", [])
        protected_issues = [i for i in issues if i["filename"] == "vacuum-runner.py"]
        assert len(protected_issues) == 0
    
    def test_analyze_respects_min_age(self, tmp_path: Path):
        """Test analysis respects minimum age threshold."""
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir()
        
        # Create very recent temp script
        recent = scripts_dir / "phase-99-recent.py"
        recent.write_text("# Just created")
        
        config = {"repo_root": str(tmp_path), "min_age_days": 30}
        cleaner = TempScriptCleaner(config)
        
        analysis = cleaner.analyze()
        
        # Should not find the recent script (too young)
        issues = analysis.plan.get("issues", [])
        assert len(issues) == 0
    
    def test_analyze_missing_scripts_dir(self, tmp_path: Path):
        """Test analysis handles missing scripts directory."""
        config = {"repo_root": str(tmp_path)}
        cleaner = TempScriptCleaner(config)
        
        analysis = cleaner.analyze()
        
        assert analysis.files_scanned == 0
        assert "not found" in analysis.logs[0]


class TestTempScriptCleanerExecute:
    """Test TempScriptCleaner execution phase."""
    
    @pytest.fixture
    def setup_for_execution(self, tmp_path: Path):
        """Set up scripts for execution test."""
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir()
        
        # Create temp script
        temp_script = scripts_dir / "phase-50-old.py"
        temp_script.write_text("# To be deleted")
        
        return tmp_path
    
    def test_execute_dry_run(self, setup_for_execution: Path):
        """Test execution in dry run mode."""
        config = {"repo_root": str(setup_for_execution), "dry_run": True, "min_age_days": 0}
        cleaner = TempScriptCleaner(config)
        
        with patch.object(cleaner, "_has_uncommitted_changes", return_value=False):
            analysis = cleaner.analyze()
            report = cleaner.execute(analysis)
        
        # File should still exist
        assert (setup_for_execution / "scripts" / "phase-50-old.py").exists()
        assert report.status == "SUCCESS"
        assert "[DRY RUN]" in report.logs[0]
    
    def test_execute_deletes_file(self, setup_for_execution: Path):
        """Test execution actually deletes files."""
        config = {"repo_root": str(setup_for_execution), "dry_run": False, "min_age_days": 0}
        cleaner = TempScriptCleaner(config)
        
        with patch.object(cleaner, "_has_uncommitted_changes", return_value=False):
            analysis = cleaner.analyze()
            report = cleaner.execute(analysis)
        
        # File should be deleted
        assert not (setup_for_execution / "scripts" / "phase-50-old.py").exists()
        assert report.status == "SUCCESS"
        assert report.changes.get("deleted", 0) >= 1


class TestTempScriptCleanerRollback:
    """Test TempScriptCleaner rollback."""
    
    def test_rollback_not_supported(self, tmp_path: Path):
        """Test rollback is not supported."""
        config = {"repo_root": str(tmp_path)}
        cleaner = TempScriptCleaner(config)
        
        # Create mock report
        from cortex_intelligence.memory.tier1_learned.orchestrators.cleaners.base import Report
        mock_report = Report(
            cleaner_id="TempScriptCleaner",
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
