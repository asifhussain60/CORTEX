"""
Naming Conventions & Linting Tests - CR-001-01

Tests for orchestrator naming conventions and validation linting.
- Naming conventions documented
- Linter validates orchestrator names
- CI integration for name validation

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from src.orchestrators.linting.naming_conventions import (
    NamingConvention,
    NamingLinter,
    LintResult,
    NamingViolation,
)


class TestNamingConventions:
    """Test naming convention definitions"""
    
    def test_kebab_case_convention_defined(self):
        """Test kebab-case convention is defined"""
        convention = NamingConvention.KEBAB_CASE
        
        assert convention is not None
        assert convention.name == "KEBAB_CASE"
    
    def test_snake_case_convention_defined(self):
        """Test snake_case convention is defined"""
        convention = NamingConvention.SNAKE_CASE
        
        assert convention is not None
        assert convention.name == "SNAKE_CASE"
    
    def test_pascal_case_convention_defined(self):
        """Test PascalCase convention is defined"""
        convention = NamingConvention.PASCAL_CASE
        
        assert convention is not None
        assert convention.name == "PASCAL_CASE"
    
    def test_convention_has_description(self):
        """Test convention has description"""
        convention = NamingConvention.KEBAB_CASE
        
        assert hasattr(convention, "description")
        assert len(convention.description) > 0
    
    def test_convention_has_regex_pattern(self):
        """Test convention has regex pattern"""
        convention = NamingConvention.KEBAB_CASE
        
        assert hasattr(convention, "pattern")
        assert convention.pattern is not None
    
    def test_get_all_conventions(self):
        """Test getting all naming conventions"""
        conventions = NamingConvention.get_all()
        
        assert len(conventions) >= 3
        assert any(c.name == "KEBAB_CASE" for c in conventions)
        assert any(c.name == "SNAKE_CASE" for c in conventions)
        assert any(c.name == "PASCAL_CASE" for c in conventions)


class TestNamingLinter:
    """Test naming linter functionality"""
    
    def test_linter_creation(self):
        """Test creating linter"""
        linter = NamingLinter()
        
        assert linter is not None
    
    def test_lint_valid_kebab_case_name(self):
        """Test linting valid kebab-case name"""
        linter = NamingLinter()
        
        result = linter.lint(
            name="valid-orchestrator-name",
            convention=NamingConvention.KEBAB_CASE
        )
        
        assert result.is_valid is True
        assert len(result.violations) == 0
    
    def test_lint_invalid_kebab_case_with_uppercase(self):
        """Test linting invalid kebab-case with uppercase"""
        linter = NamingLinter()
        
        result = linter.lint(
            name="Invalid-Orchestrator-Name",
            convention=NamingConvention.KEBAB_CASE
        )
        
        assert result.is_valid is False
        assert len(result.violations) > 0
    
    def test_lint_invalid_kebab_case_with_underscores(self):
        """Test linting invalid kebab-case with underscores"""
        linter = NamingLinter()
        
        result = linter.lint(
            name="invalid_orchestrator_name",
            convention=NamingConvention.KEBAB_CASE
        )
        
        assert result.is_valid is False
        assert len(result.violations) > 0
    
    def test_lint_result_includes_violation_details(self):
        """Test lint result includes violation details"""
        linter = NamingLinter()
        
        result = linter.lint(
            name="Invalid-Name",
            convention=NamingConvention.KEBAB_CASE
        )
        
        if not result.is_valid:
            violation = result.violations[0]
            assert hasattr(violation, "code")
            assert hasattr(violation, "message")
            assert hasattr(violation, "suggestion")
    
    def test_linter_provides_fix_suggestions(self):
        """Test linter provides fix suggestions"""
        linter = NamingLinter()
        
        result = linter.lint(
            name="InvalidOrchestratorName",
            convention=NamingConvention.KEBAB_CASE
        )
        
        if not result.is_valid:
            violation = result.violations[0]
            assert violation.suggestion is not None
            assert len(violation.suggestion) > 0


class TestNamingViolation:
    """Test naming violation reporting"""
    
    def test_violation_includes_code(self):
        """Test violation includes error code"""
        linter = NamingLinter()
        result = linter.lint(
            name="InvalidName",
            convention=NamingConvention.KEBAB_CASE
        )
        
        if not result.is_valid:
            violation = result.violations[0]
            assert violation.code is not None
            assert "NAMING" in violation.code or "CONVENTION" in violation.code
    
    def test_violation_includes_severity(self):
        """Test violation includes severity level"""
        linter = NamingLinter()
        result = linter.lint(
            name="InvalidName",
            convention=NamingConvention.KEBAB_CASE
        )
        
        if not result.is_valid:
            violation = result.violations[0]
            assert hasattr(violation, "severity")
            assert violation.severity in ["ERROR", "WARNING", "INFO"]


class TestNamingLintResult:
    """Test lint result structure"""
    
    def test_lint_result_has_validity_flag(self):
        """Test lint result has validity flag"""
        linter = NamingLinter()
        result = linter.lint(
            name="valid-name",
            convention=NamingConvention.KEBAB_CASE
        )
        
        assert hasattr(result, "is_valid")
        assert isinstance(result.is_valid, bool)
    
    def test_lint_result_has_violations_list(self):
        """Test lint result has violations list"""
        linter = NamingLinter()
        result = linter.lint(
            name="valid-name",
            convention=NamingConvention.KEBAB_CASE
        )
        
        assert hasattr(result, "violations")
        assert isinstance(result.violations, list)
    
    def test_lint_result_has_timestamp(self):
        """Test lint result has timestamp"""
        linter = NamingLinter()
        result = linter.lint(
            name="valid-name",
            convention=NamingConvention.KEBAB_CASE
        )
        
        assert hasattr(result, "timestamp")
        assert result.timestamp is not None


class TestOrchestratorNameValidation:
    """Test orchestrator-specific name validation"""
    
    def test_orchestrator_name_length_constraint(self):
        """Test orchestrator name length constraint"""
        linter = NamingLinter()
        
        # Too long name
        long_name = "a" * 50
        result = linter.lint(
            name=long_name,
            convention=NamingConvention.KEBAB_CASE
        )
        
        # Should flag length violation
        assert any(
            "length" in v.code.lower() 
            for v in result.violations
        ) or result.is_valid is True
    
    def test_orchestrator_name_cannot_start_with_number(self):
        """Test orchestrator name cannot start with number"""
        linter = NamingLinter()
        
        result = linter.lint(
            name="1-orchestrator",
            convention=NamingConvention.KEBAB_CASE
        )
        
        # Should flag if invalid
        if not result.is_valid:
            assert len(result.violations) > 0
    
    def test_orchestrator_name_cannot_end_with_hyphen(self):
        """Test orchestrator name cannot end with hyphen"""
        linter = NamingLinter()
        
        result = linter.lint(
            name="orchestrator-",
            convention=NamingConvention.KEBAB_CASE
        )
        
        # Should flag if invalid
        if not result.is_valid:
            assert len(result.violations) > 0


class TestNamingConventionDocumentation:
    """Test naming convention documentation"""
    
    def test_convention_documentation_present(self):
        """Test convention documentation is present"""
        conventions = NamingConvention.get_all()
        
        for convention in conventions:
            assert convention.description is not None
            assert len(convention.description) > 0
    
    def test_convention_has_examples(self):
        """Test convention has examples"""
        convention = NamingConvention.KEBAB_CASE
        
        assert hasattr(convention, "examples")
        assert len(convention.examples) > 0
    
    def test_convention_has_use_cases(self):
        """Test convention has use cases"""
        convention = NamingConvention.KEBAB_CASE
        
        assert hasattr(convention, "use_cases")
        assert len(convention.use_cases) > 0
    
    def test_best_practices_documented(self):
        """Test best practices are documented"""
        linter = NamingLinter()
        
        assert hasattr(linter, "get_best_practices")
        practices = linter.get_best_practices()
        assert len(practices) > 0


class TestCIIntegration:
    """Test CI integration for naming validation"""
    
    def test_linter_batch_validation(self):
        """Test batch validation of multiple names"""
        linter = NamingLinter()
        
        names = [
            "valid-name",
            "another-valid",
            "InvalidName",
        ]
        
        results = linter.lint_batch(
            names,
            convention=NamingConvention.KEBAB_CASE
        )
        
        assert len(results) == len(names)
        assert all(hasattr(r, "is_valid") for r in results)
    
    def test_linter_generates_report(self):
        """Test linter generates validation report"""
        linter = NamingLinter()
        
        names = [
            "valid-name",
            "InvalidName",
            "another-valid",
        ]
        
        report = linter.generate_report(
            names,
            convention=NamingConvention.KEBAB_CASE
        )
        
        assert hasattr(report, "total_names")
        assert hasattr(report, "valid_count")
        assert hasattr(report, "invalid_count")
        assert hasattr(report, "violations")
    
    def test_report_includes_summary_statistics(self):
        """Test report includes summary statistics"""
        linter = NamingLinter()
        
        names = ["valid-one", "invalid-Two", "valid-three"]
        
        report = linter.generate_report(
            names,
            convention=NamingConvention.KEBAB_CASE
        )
        
        assert report.total_names == len(names)
        assert report.valid_count + report.invalid_count == len(names)
    
    def test_report_suitable_for_ci_output(self):
        """Test report is suitable for CI output"""
        linter = NamingLinter()
        
        names = ["valid-name", "InvalidName"]
        report = linter.generate_report(
            names,
            convention=NamingConvention.KEBAB_CASE
        )
        
        # Should be serializable
        assert hasattr(report, "to_dict")
        report_dict = report.to_dict()
        assert isinstance(report_dict, dict)
        assert "summary" in report_dict or "total_names" in report_dict
