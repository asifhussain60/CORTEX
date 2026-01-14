"""
Tests for Repository Structure Validator - feat08-cleanup Phase 2

Tests:
- Root file validation
- Test file location validation
- Source file location validation
- Brain structure validation
- Report generation

Author: Asif Hussain
Version: 1.0.0
Created: 2026-01-08
"""

import pytest
from pathlib import Path
from src.orchestrators.vacuum.structure_validator import (
    RepositoryStructureValidator,
    StructureViolation,
    StructureReport,
    generate_structure_report
)


@pytest.fixture
def valid_workspace(tmp_path):
    """Create a valid repository structure"""
    workspace = tmp_path / "valid_repo"
    workspace.mkdir()
    
    # Create standard structure
    (workspace / "src").mkdir()
    (workspace / "src" / "module.py").write_text("# source")
    
    (workspace / "tests").mkdir()
    (workspace / "tests" / "test_module.py").write_text("# test")
    
    (workspace / "docs").mkdir()
    (workspace / "docs" / "README.md").write_text("# docs")
    
    # Allowed root files
    (workspace / "README.md").write_text("# repo")
    (workspace / "LICENSE").write_text("MIT")
    (workspace / "requirements.txt").write_text("pytest")
    
    # Brain structure
    brain = workspace / "cortex-brain"
    brain.mkdir()
    for dir_name in ["tier0", "tier1", "tier2", "tier3", "manifests", "config", "documents"]:
        (brain / dir_name).mkdir()
    
    return workspace


@pytest.fixture
def invalid_workspace(tmp_path):
    """Create an invalid repository structure"""
    workspace = tmp_path / "invalid_repo"
    workspace.mkdir()
    
    # Create standard structure
    (workspace / "src").mkdir()
    (workspace / "tests").mkdir()
    
    # Orphaned file in root
    (workspace / "orphaned.txt").write_text("orphaned")
    
    # Test file outside tests/
    (workspace / "src" / "test_wrong_location.py").write_text("# test")
    
    # Source file in wrong location
    (workspace / "random_module.py").write_text("# source")
    
    # Orphaned directory
    (workspace / "random_dir").mkdir()
    
    # Incomplete brain structure
    brain = workspace / "cortex-brain"
    brain.mkdir()
    (brain / "tier0").mkdir()  # Missing other required dirs
    
    return workspace


class TestRootFileValidation:
    """Test root file validation"""
    
    def test_valid_structure_passes(self, valid_workspace):
        """Test that valid structure passes validation"""
        validator = RepositoryStructureValidator(valid_workspace)
        report = validator.validate()
        
        # Should have no errors
        errors = [v for v in report.violations if v.severity == "ERROR"]
        assert len(errors) == 0
        assert report.valid is True
    
    def test_orphaned_file_detected(self, invalid_workspace):
        """Test that orphaned files are detected"""
        validator = RepositoryStructureValidator(invalid_workspace)
        report = validator.validate()
        
        # Should find orphaned.txt
        orphaned_violations = [
            v for v in report.violations 
            if v.category == "orphaned_file"
        ]
        assert len(orphaned_violations) > 0
    
    def test_allowed_root_files_ignored(self, tmp_path):
        """Test that allowed root files are not flagged"""
        workspace = tmp_path / "test_repo"
        workspace.mkdir()
        
        # Create allowed files
        (workspace / "README.md").write_text("readme")
        (workspace / "LICENSE").write_text("license")
        (workspace / "requirements.txt").write_text("reqs")
        (workspace / ".gitignore").write_text("ignore")
        
        validator = RepositoryStructureValidator(workspace)
        report = validator.validate()
        
        # No orphaned file violations
        orphaned = [v for v in report.violations if v.category == "orphaned_file"]
        assert len(orphaned) == 0
    
    def test_hidden_files_allowed(self, tmp_path):
        """Test that hidden files are allowed"""
        workspace = tmp_path / "test_repo"
        workspace.mkdir()
        
        (workspace / ".env").write_text("env")
        (workspace / ".custom").write_text("custom")
        
        validator = RepositoryStructureValidator(workspace)
        report = validator.validate()
        
        orphaned = [v for v in report.violations if v.category == "orphaned_file"]
        assert len(orphaned) == 0


class TestTestFileValidation:
    """Test test file location validation"""
    
    def test_misplaced_test_detected(self, invalid_workspace):
        """Test that misplaced test files are detected"""
        validator = RepositoryStructureValidator(invalid_workspace)
        report = validator.validate()
        
        misplaced_tests = [
            v for v in report.violations 
            if v.category == "misplaced_test"
        ]
        assert len(misplaced_tests) > 0
    
    def test_tests_in_tests_dir_valid(self, valid_workspace):
        """Test that tests in tests/ are valid"""
        validator = RepositoryStructureValidator(valid_workspace)
        report = validator.validate()
        
        misplaced_tests = [
            v for v in report.violations 
            if v.category == "misplaced_test"
        ]
        assert len(misplaced_tests) == 0
    
    def test_test_patterns_recognized(self, tmp_path):
        """Test that test patterns are recognized"""
        workspace = tmp_path / "test_repo"
        workspace.mkdir()
        (workspace / "src").mkdir()
        
        # Create misplaced test files with different patterns
        (workspace / "test_something.py").write_text("# test")
        (workspace / "something_test.py").write_text("# test")
        
        validator = RepositoryStructureValidator(workspace)
        report = validator.validate()
        
        misplaced_tests = [
            v for v in report.violations 
            if v.category == "misplaced_test"
        ]
        assert len(misplaced_tests) >= 2


class TestSourceFileValidation:
    """Test source file location validation"""
    
    def test_misplaced_source_detected(self, invalid_workspace):
        """Test that misplaced source files are detected"""
        validator = RepositoryStructureValidator(invalid_workspace)
        report = validator.validate()
        
        misplaced_source = [
            v for v in report.violations 
            if v.category == "misplaced_source"
        ]
        # random_module.py should be flagged
        assert len(misplaced_source) > 0
    
    def test_source_in_src_valid(self, valid_workspace):
        """Test that source in src/ is valid"""
        validator = RepositoryStructureValidator(valid_workspace)
        report = validator.validate()
        
        misplaced_source = [
            v for v in report.violations 
            if v.category == "misplaced_source"
        ]
        assert len(misplaced_source) == 0
    
    def test_setup_py_allowed(self, tmp_path):
        """Test that setup.py is allowed in root"""
        workspace = tmp_path / "test_repo"
        workspace.mkdir()
        (workspace / "setup.py").write_text("setup")
        
        validator = RepositoryStructureValidator(workspace)
        report = validator.validate()
        
        misplaced_source = [
            v for v in report.violations 
            if v.category == "misplaced_source"
        ]
        assert len(misplaced_source) == 0
    
    def test_scripts_dir_source_allowed(self, tmp_path):
        """Test that source in scripts/ is allowed"""
        workspace = tmp_path / "test_repo"
        workspace.mkdir()
        scripts = workspace / "scripts"
        scripts.mkdir()
        (scripts / "deploy.py").write_text("# deploy script")
        
        validator = RepositoryStructureValidator(workspace)
        report = validator.validate()
        
        misplaced_source = [
            v for v in report.violations 
            if v.category == "misplaced_source"
        ]
        assert len(misplaced_source) == 0


class TestBrainStructureValidation:
    """Test brain structure validation"""
    
    def test_valid_brain_structure(self, valid_workspace):
        """Test that valid brain structure passes"""
        validator = RepositoryStructureValidator(valid_workspace)
        report = validator.validate()
        
        brain_violations = [
            v for v in report.violations 
            if v.category == "invalid_brain"
        ]
        assert len(brain_violations) == 0
    
    def test_missing_brain_dirs_detected(self, invalid_workspace):
        """Test that missing brain directories are detected"""
        validator = RepositoryStructureValidator(invalid_workspace)
        report = validator.validate()
        
        brain_violations = [
            v for v in report.violations 
            if v.category == "invalid_brain"
        ]
        # Missing tier1, tier2, tier3, manifests, config, documents
        assert len(brain_violations) >= 5
    
    def test_missing_brain_allowed(self, tmp_path):
        """Test that missing brain is allowed (optional)"""
        workspace = tmp_path / "test_repo"
        workspace.mkdir()
        (workspace / "src").mkdir()
        (workspace / "tests").mkdir()
        
        validator = RepositoryStructureValidator(workspace)
        report = validator.validate()
        
        # No brain violations if brain doesn't exist
        brain_violations = [
            v for v in report.violations 
            if v.category == "invalid_brain"
        ]
        assert len(brain_violations) == 0


class TestViolationSeverity:
    """Test violation severity levels"""
    
    def test_orphaned_file_is_error(self, invalid_workspace):
        """Test that orphaned files are ERROR severity"""
        validator = RepositoryStructureValidator(invalid_workspace)
        report = validator.validate()
        
        orphaned = [v for v in report.violations if v.category == "orphaned_file"]
        for violation in orphaned:
            assert violation.severity == "ERROR"
    
    def test_misplaced_test_is_error(self, invalid_workspace):
        """Test that misplaced tests are ERROR severity"""
        validator = RepositoryStructureValidator(invalid_workspace)
        report = validator.validate()
        
        misplaced = [v for v in report.violations if v.category == "misplaced_test"]
        for violation in misplaced:
            assert violation.severity == "ERROR"
    
    def test_report_invalid_with_errors(self, invalid_workspace):
        """Test that report is invalid with ERROR violations"""
        validator = RepositoryStructureValidator(invalid_workspace)
        report = validator.validate()
        
        errors = [v for v in report.violations if v.severity == "ERROR"]
        if errors:
            assert report.valid is False


class TestStatistics:
    """Test statistics calculation"""
    
    def test_stats_calculated(self, invalid_workspace):
        """Test that statistics are calculated"""
        validator = RepositoryStructureValidator(invalid_workspace)
        report = validator.validate()
        
        assert "total_violations" in report.stats
        assert "errors" in report.stats
        assert "warnings" in report.stats
        assert "by_category" in report.stats
    
    def test_file_counts(self, valid_workspace):
        """Test that file counts are correct"""
        validator = RepositoryStructureValidator(valid_workspace)
        report = validator.validate()
        
        assert report.stats["src_files"] >= 1
        assert report.stats["test_files"] >= 1
    
    def test_brain_detection(self, valid_workspace):
        """Test that brain is detected"""
        validator = RepositoryStructureValidator(valid_workspace)
        report = validator.validate()
        
        assert report.stats["has_brain"] is True


class TestRecommendations:
    """Test recommendation generation"""
    
    def test_recommendations_generated(self, invalid_workspace):
        """Test that recommendations are generated"""
        validator = RepositoryStructureValidator(invalid_workspace)
        report = validator.validate()
        
        assert len(report.recommendations) > 0
    
    def test_error_recommendation(self, invalid_workspace):
        """Test that errors generate recommendations"""
        validator = RepositoryStructureValidator(invalid_workspace)
        report = validator.validate()
        
        errors = [v for v in report.violations if v.severity == "ERROR"]
        if errors:
            # Should recommend fixing errors
            error_recs = [r for r in report.recommendations if "ERROR" in r]
            assert len(error_recs) > 0
    
    def test_valid_structure_recommendation(self, valid_workspace):
        """Test that valid structure gets success recommendation"""
        validator = RepositoryStructureValidator(valid_workspace)
        report = validator.validate()
        
        if report.valid:
            assert any("✅" in r or "valid" in r.lower() for r in report.recommendations)


class TestReportGeneration:
    """Test report generation"""
    
    def test_generate_report_text(self, valid_workspace):
        """Test report text generation"""
        validator = RepositoryStructureValidator(valid_workspace)
        report = validator.validate()
        
        report_text = generate_structure_report(report)
        
        assert "REPOSITORY STRUCTURE VALIDATION REPORT" in report_text
        assert str(valid_workspace) in report_text
    
    def test_report_includes_violations(self, invalid_workspace):
        """Test that report includes violations"""
        validator = RepositoryStructureValidator(invalid_workspace)
        report = validator.validate()
        
        report_text = generate_structure_report(report)
        
        assert "Violations:" in report_text or "ERRORS" in report_text
    
    def test_report_saves_to_file(self, valid_workspace, tmp_path):
        """Test that report can be saved to file"""
        validator = RepositoryStructureValidator(valid_workspace)
        report = validator.validate()
        
        output_file = tmp_path / "report.txt"
        generate_structure_report(report, output_file)
        
        assert output_file.exists()
        content = output_file.read_text()
        assert "REPOSITORY STRUCTURE VALIDATION REPORT" in content


class TestReportSerialization:
    """Test report serialization"""
    
    def test_violation_to_dict(self, invalid_workspace):
        """Test violation serializes to dictionary"""
        validator = RepositoryStructureValidator(invalid_workspace)
        report = validator.validate()
        
        if report.violations:
            violation_dict = report.violations[0].to_dict()
            
            assert "severity" in violation_dict
            assert "category" in violation_dict
            assert "path" in violation_dict
            assert "message" in violation_dict
    
    def test_report_to_dict(self, valid_workspace):
        """Test report serializes to dictionary"""
        validator = RepositoryStructureValidator(valid_workspace)
        report = validator.validate()
        
        report_dict = report.to_dict()
        
        assert "workspace" in report_dict
        assert "valid" in report_dict
        assert "violations" in report_dict
        assert "stats" in report_dict
    
    def test_report_to_json(self, valid_workspace):
        """Test report serializes to JSON"""
        validator = RepositoryStructureValidator(valid_workspace)
        report = validator.validate()
        
        json_str = report.to_json()
        
        import json
        parsed = json.loads(json_str)
        assert "workspace" in parsed
        assert "valid" in parsed


class TestEdgeCases:
    """Test edge cases"""
    
    def test_nonexistent_workspace(self, tmp_path):
        """Test handling of nonexistent workspace"""
        workspace = tmp_path / "nonexistent"
        
        validator = RepositoryStructureValidator(workspace)
        report = validator.validate()
        
        # Should have invalid_workspace violation
        violations = [v for v in report.violations if v.category == "invalid_workspace"]
        assert len(violations) > 0
    
    def test_empty_workspace(self, tmp_path):
        """Test handling of empty workspace"""
        workspace = tmp_path / "empty"
        workspace.mkdir()
        
        validator = RepositoryStructureValidator(workspace)
        report = validator.validate()
        
        # Empty workspace is valid (just no violations)
        assert isinstance(report, StructureReport)
    
    def test_deeply_nested_test_files(self, tmp_path):
        """Test handling of deeply nested test files"""
        workspace = tmp_path / "test_repo"
        workspace.mkdir()
        
        # Create deeply nested test outside tests/
        deep = workspace / "a" / "b" / "c"
        deep.mkdir(parents=True)
        (deep / "test_deep.py").write_text("# test")
        
        validator = RepositoryStructureValidator(workspace)
        report = validator.validate()
        
        misplaced_tests = [
            v for v in report.violations 
            if v.category == "misplaced_test"
        ]
        assert len(misplaced_tests) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
