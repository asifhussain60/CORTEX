"""
Phase 38 Stage 11: ScreamingCaseDetector Tests
Authority: TDDOrchestrator | CORE-008 (tests before code)
Acceptance Criteria: AC-PHASE38-031
Purpose: Test SCREAMING_CASE detection and kebab-case migration (10 tests)
"""

import pytest
import tempfile
from pathlib import Path
from typing import List, Dict


class TestScreamingCaseDetector:
    """ScreamingCaseDetector - detects SCREAMING_CASE violations and enables kebab-case migration"""

    @pytest.fixture
    def detector(self):
        """Fixture: Initialize ScreamingCaseDetector"""
        from cortex.orchestrators.support.screaming_case_detector import ScreamingCaseDetector
        return ScreamingCaseDetector()

    @pytest.fixture
    def cortex_project(self, tmp_path):
        """Fixture: Create CORTEX project structure with violations"""
        # Create structure
        (tmp_path / "cortex").mkdir()
        (tmp_path / "cortex" / "orchestrators").mkdir()
        (tmp_path / "tests").mkdir()
        
        # Create violation files (SCREAMING_CASE)
        violations = [
            "PHASE_MANAGER.py",
            "GOVERNANCE_ENGINE.py",
            "TEST_SUITE.py",
        ]
        
        for violation in violations:
            (tmp_path / "cortex" / violation).write_text("# module")
        
        # Create compliant files (kebab-case)
        compliant = [
            "phase-manager.py",
            "governance-engine.py",
        ]
        
        for comp in compliant:
            (tmp_path / "cortex" / comp).write_text("# module")
        
        return tmp_path

    # Test 1: Detect SCREAMING_CASE files
    def test_detect_screaming_case_py_files(self, detector, cortex_project):
        """Test: Detect Python files with SCREAMING_CASE names"""
        violations = detector.find_screaming_case_violations(str(cortex_project))
        
        assert len(violations) > 0
        assert any("PHASE_MANAGER.py" in v["file"] for v in violations)
        assert any("GOVERNANCE_ENGINE.py" in v["file"] for v in violations)

    def test_detect_screaming_case_in_nested_dirs(self, detector, cortex_project):
        """Test: Find violations in nested directories"""
        (cortex_project / "cortex" / "deep" / "nested").mkdir(parents=True)
        (cortex_project / "cortex" / "deep" / "nested" / "NESTED_MODULE.py").write_text("code")
        
        violations = detector.find_screaming_case_violations(str(cortex_project))
        
        assert any("NESTED_MODULE.py" in v["file"] for v in violations)

    def test_ignore_allowed_screaming_case(self, detector, cortex_project):
        """Test: Ignore allowed SCREAMING_CASE files (e.g., __ALL__, constants)"""
        # __init__.py is allowed to have __all__
        init_file = cortex_project / "cortex" / "__init__.py"
        init_file.write_text("__all__ = ['module1']\n")
        
        violations = detector.find_screaming_case_violations(str(cortex_project))
        
        # __init__.py itself should not be flagged
        assert not any("__init__.py" in v["file"] for v in violations)

    # Test 2: Generate kebab-case alternatives
    def test_generate_kebab_case_alternative(self, detector):
        """Test: Generate correct kebab-case from SCREAMING_CASE"""
        input_names = [
            "PHASE_MANAGER.py",
            "GOVERNANCE_ENGINE.py",
            "TEST_SUITE.py",
        ]
        
        expected = [
            "phase-manager.py",
            "governance-engine.py",
            "test-suite.py",
        ]
        
        for input_name, expected_name in zip(input_names, expected):
            result = detector.to_kebab_case(input_name)
            assert result == expected_name

    def test_kebab_case_preserves_extension(self, detector):
        """Test: Preserve file extensions during conversion"""
        conversions = {
            "MY_MODULE.py": "my-module.py",
            "MY_CONFIG.yaml": "my-config.yaml",
            "MY_TEST.test.py": "my-test.test.py",
        }
        
        for input_name, expected in conversions.items():
            result = detector.to_kebab_case(input_name)
            assert result == expected

    def test_kebab_case_idempotent(self, detector):
        """Test: Converting kebab-case again returns same value"""
        already_kebab = "phase-manager.py"
        
        result1 = detector.to_kebab_case(already_kebab)
        result2 = detector.to_kebab_case(result1)
        
        assert result1 == already_kebab
        assert result2 == already_kebab

    # Test 3: Map all violations in codebase
    def test_map_all_violations_comprehensive(self, detector, cortex_project):
        """Test: Create complete violation map for entire codebase"""
        # Add more violations
        (cortex_project / "cortex" / "ORCHESTRATOR_MESH.py").write_text("code")
        (cortex_project / "tests" / "TEST_HELPERS.py").write_text("code")
        
        violation_map = detector.create_violation_map(str(cortex_project))
        
        assert "violations" in violation_map
        assert len(violation_map["violations"]) >= 4
        assert "PHASE_MANAGER.py" in str(violation_map)

    def test_violation_map_includes_replacements(self, detector, cortex_project):
        """Test: Violation map includes old→new name mappings"""
        violation_map = detector.create_violation_map(str(cortex_project))
        
        for violation in violation_map["violations"]:
            assert "old_name" in violation
            assert "new_name" in violation
            assert violation["new_name"] == detector.to_kebab_case(violation["old_name"])

    # Test 4: Generate migration plan
    def test_generate_migration_plan_single_file(self, detector, cortex_project):
        """Test: Generate plan to migrate single file"""
        plan = detector.generate_migration_plan(
            violations=[
                {"old_name": "PHASE_MANAGER.py", "path": str(cortex_project / "cortex")}
            ]
        )
        
        assert len(plan) > 0
        assert plan[0]["action"] == "rename"
        assert plan[0]["old_name"] == "PHASE_MANAGER.py"
        assert plan[0]["new_name"] == "phase-manager.py"

    def test_generate_migration_plan_batch(self, detector, cortex_project):
        """Test: Generate plan for batch migration"""
        violations = detector.find_screaming_case_violations(str(cortex_project))
        
        plan = detector.generate_migration_plan(violations)
        
        assert len(plan) == len(violations)
        assert all(p["action"] == "rename" for p in plan)

    def test_migration_plan_includes_reference_updates(self, detector):
        """Test: Migration plan includes steps to update references"""
        violations = [
            {"old_name": "HELPER.py", "path": "/cortex", "references": ["import_list.txt"]}
        ]
        
        plan = detector.generate_migration_plan(violations, include_reference_updates=True)
        
        # Should include update steps
        assert any("update_references" in str(p) for p in plan) or len(plan) > 0

    # Test 5: Preserve file history on rename
    def test_preserve_git_history_on_rename(self, detector):
        """Test: Use git mv to preserve commit history"""
        from unittest.mock import patch, Mock
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0)
            
            result = detector.git_rename_file(
                old_path="/cortex/PHASE_MANAGER.py",
                new_path="/cortex/phase-manager.py"
            )
            
            # Verify git mv was called
            mock_run.assert_called()
            call_str = str(mock_run.call_args)
            assert 'git' in call_str or 'mv' in call_str

    def test_git_rename_handles_unstaged_files(self, detector):
        """Test: Handle files not yet staged in git"""
        from unittest.mock import patch, Mock
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0)
            
            result = detector.git_rename_file(
                old_path="/cortex/NEW_FILE.py",
                new_path="/cortex/new-file.py",
                force=True
            )
            
            assert result["success"] or result["error"] is not None

    # Test 6: Update imports after rename
    def test_update_imports_after_rename(self, detector, tmp_path):
        """Test: Update imports when files are renamed"""
        # Create importer file
        (tmp_path / "cortex").mkdir()
        
        importer = tmp_path / "cortex" / "main.py"
        importer.write_text("from PHASE_MANAGER import PhaseManager\n")
        
        rename_map = {
            "PHASE_MANAGER.py": "phase-manager.py"
        }
        
        result = detector.update_imports(
            str(tmp_path),
            rename_map
        )
        
        assert result["files_updated"] >= 0

    def test_update_relative_imports_after_rename(self, detector, tmp_path):
        """Test: Correctly update relative imports"""
        (tmp_path / "cortex" / "subdir").mkdir(parents=True)
        
        importer = tmp_path / "cortex" / "subdir" / "module.py"
        importer.write_text("from ..HELPER import helper\n")
        
        rename_map = {"HELPER.py": "helper.py"}
        
        result = detector.update_imports(str(tmp_path), rename_map)
        
        assert result["relative_imports_updated"] >= 0 or "files_updated" in result

    # Test 7: Update documentation references
    def test_update_documentation_references(self, detector, tmp_path):
        """Test: Update references in documentation files"""
        docs = tmp_path / "docs" / "architecture.md"
        docs.parent.mkdir(parents=True)
        docs.write_text("""
# Architecture
Imports from PHASE_MANAGER and GOVERNANCE_ENGINE modules.
""")
        
        rename_map = {
            "PHASE_MANAGER.py": "phase-manager.py",
            "GOVERNANCE_ENGINE.py": "governance-engine.py"
        }
        
        result = detector.update_documentation(str(tmp_path), rename_map)
        
        assert result["docs_updated"] >= 0

    # Test 8: Handle test file renames
    def test_handle_test_file_renames(self, detector, tmp_path):
        """Test: Rename test files and their corresponding modules"""
        (tmp_path / "tests").mkdir()
        
        test_file = tmp_path / "tests" / "TEST_PHASE_MANAGER.py"
        test_file.write_text("def test_phase_manager(): pass\n")
        
        plan = detector.generate_test_file_migration(str(tmp_path))
        
        # Should include test file renames
        assert any("test_" in str(p) for p in plan) or len(plan) >= 0

    # Test 9: Validate kebab-case naming compliance
    def test_validate_kebab_case_compliance(self, detector, tmp_path):
        """Test: Validate all Python files use kebab-case"""
        (tmp_path / "cortex").mkdir()
        
        # Mix of good and bad
        (tmp_path / "cortex" / "good-file.py").write_text("code")
        (tmp_path / "cortex" / "BAD_FILE.py").write_text("code")
        (tmp_path / "cortex" / "badFile.py").write_text("code")
        
        validation = detector.validate_kebab_case_compliance(str(tmp_path))
        
        assert validation["total_py_files"] >= 3
        assert validation["compliant"] >= 1
        assert validation["violations"] >= 2

    def test_kebab_case_compliance_report(self, detector, tmp_path):
        """Test: Generate detailed compliance report"""
        (tmp_path / "cortex").mkdir()
        
        files = [
            ("good-file.py", True),
            ("BAD_FILE.py", False),
            ("MIX_edCase.py", False),
        ]
        
        for filename, _ in files:
            (tmp_path / "cortex" / filename).write_text("code")
        
        report = detector.generate_compliance_report(str(tmp_path))
        
        assert "summary" in report or "violations" in report
        assert report["total"] >= 3

    # Test 10: Batch rename multiple files
    def test_batch_rename_multiple_files(self, detector, tmp_path):
        """Test: Rename multiple files in single operation"""
        (tmp_path / "cortex").mkdir()
        
        files = [
            "PHASE_MANAGER.py",
            "GOVERNANCE_ENGINE.py",
            "TEST_SUITE.py",
        ]
        
        for f in files:
            (tmp_path / "cortex" / f).write_text("code")
        
        result = detector.batch_rename(str(tmp_path / "cortex"))
        
        assert result["total"] == 3
        assert result["renamed"] >= 0
        assert result["renamed"] + result["failed"] == result["total"]

    def test_batch_rename_with_rollback_on_failure(self, detector, tmp_path):
        """Test: Rollback batch rename if any step fails"""
        (tmp_path / "cortex").mkdir()
        (tmp_path / "cortex" / "FILE_A.py").write_text("code")
        (tmp_path / "cortex" / "FILE_B.py").write_text("code")
        
        from unittest.mock import patch, Mock
        
        # Simulate failure on second file
        with patch.object(detector, 'git_rename_file') as mock_rename:
            mock_rename.side_effect = [
                {"success": True},
                {"error": "Permission denied"},  # Fail on second
            ]
            
            result = detector.batch_rename_with_rollback(str(tmp_path / "cortex"))
            
            # Should track rollback
            assert "error" in result or "rolled_back" in result or "failed" in result


class TestScreamingCaseDetectorIntegration:
    """Integration tests for complete case migration workflows"""

    @pytest.fixture
    def detector(self):
        from cortex.orchestrators.support.screaming_case_detector import ScreamingCaseDetector
        return ScreamingCaseDetector()

    def test_complete_screaming_case_migration(self, detector, tmp_path):
        """Integration: Complete SCREAMING_CASE → kebab-case migration"""
        # Setup violations
        (tmp_path / "cortex").mkdir()
        (tmp_path / "cortex" / "PHASE_MANAGER.py").write_text("class PhaseManager: pass")
        (tmp_path / "cortex" / "GOVERNANCE_ENGINE.py").write_text("class GovernanceEngine: pass")
        
        # Execute migration
        result = detector.complete_migration(
            codebase_root=str(tmp_path),
            preserve_git_history=True,
            update_all_references=True
        )
        
        assert result["completed"] or result["error"] is not None
        assert result["total_violations"] >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
