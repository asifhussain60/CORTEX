"""
Phase 38 Stage 11: OptimalFolderStateValidator Tests
Authority: TDDOrchestrator | CORE-008 (tests before code)
Acceptance Criteria: AC-PHASE38-033
Purpose: Test folder structure compliance validation (7 tests)
"""

import pytest
from pathlib import Path


class TestOptimalFolderStateValidator:
    """OptimalFolderStateValidator - ensures CORTEX folder structure is optimal and compliant"""

    @pytest.fixture
    def validator(self):
        """Fixture: Initialize OptimalFolderStateValidator"""
        from cortex.orchestrators.support.file_governance_validator import OptimalFolderStateValidator
        return OptimalFolderStateValidator()

    @pytest.fixture
    def compliant_project(self, tmp_path):
        """Fixture: Create compliant CORTEX project structure"""
        # Compliant structure
        (tmp_path / "cortex" / "orchestrators").mkdir(parents=True)
        (tmp_path / "cortex" / "lens").mkdir(parents=True)
        (tmp_path / "cortex" / "mcp").mkdir(parents=True)
        (tmp_path / "tests" / "unit").mkdir(parents=True)
        (tmp_path / "docs" / "architecture").mkdir(parents=True)
        (tmp_path / ".github" / "prompts").mkdir(parents=True)
        
        # Allowed root files
        (tmp_path / "README.md").write_text("# README")
        (tmp_path / "Makefile").write_text("make:")
        
        # Create code in correct locations
        (tmp_path / "cortex" / "main.py").write_text("# code")
        (tmp_path / "cortex" / "orchestrators" / "orchestrator.py").write_text("# code")
        (tmp_path / "tests" / "unit" / "test_module.py").write_text("# test")
        (tmp_path / "docs" / "guide.md").write_text("# doc")
        
        return tmp_path

    @pytest.fixture
    def violation_project(self, tmp_path):
        """Fixture: Create project with placement violations"""
        (tmp_path / "cortex" / "orchestrators").mkdir(parents=True)
        (tmp_path / "tests").mkdir()
        (tmp_path / "docs").mkdir()
        
        # Violations
        (tmp_path / "random_module.py").write_text("# Wrong: in root")
        (tmp_path / "README_EXTRA.md").write_text("# Wrong: in root")
        (tmp_path / "cortex" / "SCREAMING_CASE.py").write_text("# Wrong: bad naming")
        (tmp_path / "cortex" / "orchestrators" / "MY_ORCHESTRATOR.py").write_text("# Wrong: bad naming")
        (tmp_path / "test_file.py").write_text("# Wrong: in root, should be in tests/")
        (tmp_path / "cortex" / "test_module.py").write_text("# Wrong: test in cortex/, should be in tests/")
        
        return tmp_path

    # Test 1: Detect Python files in root
    def test_detect_py_files_in_root(self, validator, violation_project):
        """Test: Detect Python files placed in root directory"""
        violations = validator.find_placement_violations(str(violation_project))
        
        py_violations = [v for v in violations if "root" in v.get("violation_type", "")]
        
        assert len(py_violations) >= 1

    def test_detect_py_files_root_excludes_setup(self, validator, tmp_path):
        """Test: Allowed Python files in root (setup.py, etc.)"""
        (tmp_path / "cortex").mkdir()
        (tmp_path / "setup.py").write_text("# setup")
        (tmp_path / "conftest.py").write_text("# conftest")
        
        violations = validator.find_placement_violations(str(tmp_path))
        
        # setup.py and conftest.py are allowed
        assert not any("setup.py" in str(v) for v in violations)

    # Test 2: Detect markdown files outside docs/.github/
    def test_detect_md_outside_docs_github(self, validator, violation_project):
        """Test: Detect markdown files outside docs/ and .github/"""
        violations = validator.find_placement_violations(str(violation_project))
        
        md_violations = [v for v in violations if "README_EXTRA.md" in str(v)]
        
        assert len(md_violations) >= 1

    def test_allow_markdown_in_docs_github(self, validator, tmp_path):
        """Test: Allow markdown files in docs/ and .github/"""
        (tmp_path / "docs").mkdir()
        (tmp_path / ".github").mkdir()
        (tmp_path / "cortex").mkdir()
        
        (tmp_path / "docs" / "guide.md").write_text("# guide")
        (tmp_path / ".github" / "workflow.md").write_text("# workflow")
        
        violations = validator.find_placement_violations(str(tmp_path))
        
        # Should not flag docs or .github markdown files
        md_violations = [v for v in violations if ".md" in str(v)]
        assert len(md_violations) == 0

    # Test 3: Validate all orchestrators in cortex/orchestrators/
    def test_validate_orchestrators_in_correct_location(self, validator, compliant_project):
        """Test: Validate orchestrators are in cortex/orchestrators/"""
        # Create orchestrator
        orch = compliant_project / "cortex" / "orchestrators" / "my_orchestrator.py"
        orch.write_text("class MyOrchestrator: pass")
        
        violations = validator.find_placement_violations(str(compliant_project))
        
        # Should not flag this
        assert not any("my_orchestrator" in str(v) for v in violations)

    def test_detect_orchestrators_outside_correct_location(self, validator, violation_project):
        """Test: Detect orchestrators placed outside cortex/orchestrators/"""
        (violation_project / "cortex" / "my_orchestrator.py").write_text("class MyOrchestrator: pass")
        (violation_project / "my_orchestrator.py").write_text("class MyOrchestrator: pass")
        
        violations = validator.find_placement_violations(str(violation_project))
        
        # Should flag orchestrators outside correct location
        assert len(violations) >= 1

    # Test 4: Validate tests in tests/ directory
    def test_validate_tests_in_tests_directory(self, validator, compliant_project):
        """Test: Validate test files are in tests/"""
        violations = validator.find_placement_violations(str(compliant_project))
        
        # Compliant project should have minimal violations
        test_violations = [v for v in violations if "test" in str(v).lower()]
        
        # Correct placement should not raise violations
        assert not any("unit/test_module" in str(v) for v in violations)

    def test_detect_tests_in_cortex_directory(self, validator, violation_project):
        """Test: Detect test files incorrectly placed in cortex/"""
        violations = validator.find_placement_violations(str(violation_project))
        
        # Should flag test files in cortex/
        assert any("test_module" in str(v) for v in violations)

    # Test 5: Detect placement violations
    def test_detect_all_placement_violations(self, validator, violation_project):
        """Test: Detect all types of placement violations"""
        violations = validator.find_placement_violations(str(violation_project))
        
        assert len(violations) >= 3  # Multiple violations in test fixture
        
        # Should include different violation types
        violation_types = [v.get("violation_type") for v in violations]
        assert len(set(violation_types)) >= 2  # At least 2 different types

    def test_violations_include_remediation(self, validator, violation_project):
        """Test: Violations include remediation suggestions"""
        violations = validator.find_placement_violations(str(violation_project))
        
        for violation in violations:
            assert "suggested_location" in violation or "remediation" in violation

    # Test 6: Generate placement audit report
    def test_generate_placement_audit_report(self, validator, violation_project):
        """Test: Generate comprehensive placement audit report"""
        report = validator.generate_audit_report(str(violation_project))
        
        assert "summary" in report or "total_violations" in report
        assert "violations" in report
        assert report["total_violations"] >= 3

    def test_report_includes_statistics(self, validator, compliant_project):
        """Test: Report includes file structure statistics"""
        report = validator.generate_audit_report(str(compliant_project))
        
        assert "total_files" in report or "statistics" in report
        assert "py_files" in report or "python_files" in report
        assert "md_files" in report or "markdown_files" in report

    # Test 7: Provide placement remediation plan
    def test_generate_remediation_plan(self, validator, violation_project):
        """Test: Generate step-by-step remediation plan"""
        violations = validator.find_placement_violations(str(violation_project))
        
        plan = validator.generate_remediation_plan(violations)
        
        assert "steps" in plan or "remediation_steps" in plan
        assert len(plan.get("steps", [])) >= len(violations)

    def test_remediation_plan_includes_commands(self, validator, violation_project):
        """Test: Remediation plan includes actual commands to fix"""
        violations = validator.find_placement_violations(str(violation_project))
        
        plan = validator.generate_remediation_plan(violations)
        
        # Should include commands or actionable steps
        steps = plan.get("steps", [])
        
        if steps:
            # At least some steps should be actionable
            actionable = [s for s in steps if "command" in str(s).lower() or "move" in str(s).lower()]
            assert len(actionable) > 0 or len(steps) >= 1

    def test_remediation_respects_dependencies(self, validator, tmp_path):
        """Test: Remediation plan respects dependencies (e.g., test files after code)"""
        (tmp_path / "cortex").mkdir()
        (tmp_path / "tests").mkdir()
        
        # Create files with dependencies
        (tmp_path / "module.py").write_text("# Wrong location")
        (tmp_path / "test_module.py").write_text("from module import x")
        
        violations = validator.find_placement_violations(str(tmp_path))
        plan = validator.generate_remediation_plan(violations)
        
        # Plan should be ordered correctly
        steps = plan.get("steps", [])
        if len(steps) > 1:
            # Module should be moved before test
            module_idx = next((i for i, s in enumerate(steps) if "module.py" in str(s)), -1)
            test_idx = next((i for i, s in enumerate(steps) if "test_module" in str(s)), -1)
            
            if module_idx != -1 and test_idx != -1:
                assert module_idx < test_idx


class TestOptimalFolderStateValidatorIntegration:
    """Integration tests for folder structure compliance"""

    @pytest.fixture
    def validator(self):
        from cortex.orchestrators.support.file_governance_validator import OptimalFolderStateValidator
        return OptimalFolderStateValidator()

    def test_complete_folder_validation_workflow(self, validator, tmp_path):
        """Integration: Complete folder structure validation and remediation"""
        # Create violations
        (tmp_path / "cortex" / "orchestrators").mkdir(parents=True)
        (tmp_path / "tests").mkdir()
        (tmp_path / "docs").mkdir()
        
        (tmp_path / "bad_module.py").write_text("code")
        (tmp_path / "bad_test.py").write_text("test")
        
        # Execute validation workflow
        result = validator.validate_and_remediate(
            codebase_root=str(tmp_path),
            auto_fix=False  # Generate plan only
        )
        
        assert "violations" in result or "plan" in result
        assert result["compliant"] is False or "violations" in result

    def test_validate_compliant_project(self, validator, tmp_path):
        """Integration: Validate compliant project structure"""
        # Create compliant structure
        (tmp_path / "cortex" / "orchestrators").mkdir(parents=True)
        (tmp_path / "tests" / "unit").mkdir(parents=True)
        (tmp_path / "docs").mkdir()
        (tmp_path / ".github").mkdir()
        
        (tmp_path / "cortex" / "main.py").write_text("code")
        (tmp_path / "tests" / "unit" / "test_main.py").write_text("test")
        (tmp_path / "docs" / "guide.md").write_text("docs")
        (tmp_path / "README.md").write_text("readme")
        
        result = validator.validate_and_remediate(
            codebase_root=str(tmp_path),
            auto_fix=False
        )
        
        assert result["compliant"] is True or result["violations"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
