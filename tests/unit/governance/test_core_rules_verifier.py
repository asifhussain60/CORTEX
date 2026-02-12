"""
Tests for CORE Rules Verifier.

AC_START: AC-WAVE-K-003
Description: CORE rules verification tests
"""

import pytest
from pathlib import Path
from datetime import datetime
from cortex.governance.core_rules_verifier import (
    CoreRulesVerifier,
    RuleViolation,
    ComplianceReport,
)


@pytest.fixture
def temp_workspace(tmp_path):
    """Create temporary workspace for testing."""
    cortex_dir = tmp_path / "cortex"
    cortex_dir.mkdir()
    
    tests_dir = tmp_path / "tests" / "unit"
    tests_dir.mkdir(parents=True)
    
    github_dir = tmp_path / ".github"
    (github_dir / "prompts").mkdir(parents=True)
    (github_dir / "agents").mkdir(parents=True)
    
    return tmp_path


@pytest.fixture
def verifier(temp_workspace):
    """Create CORE rules verifier instance."""
    return CoreRulesVerifier(workspace_root=temp_workspace)


class TestCoreRulesVerifier:
    """Tests for CoreRulesVerifier initialization."""
    
    def test_verifier_initialization(self, verifier):
        """CoreRulesVerifier initializes with workspace root."""
        assert verifier is not None
        assert verifier.workspace_root.exists()
        assert verifier.violations == []
        assert verifier.rules_checked == 0
    
    def test_verifier_has_core_rules(self, verifier):
        """CoreRulesVerifier has all CORE rules defined."""
        assert len(verifier.core_rules) >= 15  # At least 15 automated rules
        assert "CORE-002" in verifier.core_rules
        assert "CORE-008" in verifier.core_rules
        assert "CORE-028" in verifier.core_rules


class TestCORE002_MarkdownSuppression:
    """Tests for CORE-002: No markdown file generation."""
    
    def test_forbidden_markdown_summary_detected(self, temp_workspace, verifier):
        """Forbidden *-summary.md files are detected."""
        forbidden_file = temp_workspace / "cortex" / "test-summary.md"
        forbidden_file.write_text("# Summary")
        
        verifier._check_markdown_suppression()
        
        assert len(verifier.violations) == 1
        assert verifier.violations[0].rule_id == "CORE-002"
        assert "test-summary.md" in verifier.violations[0].file_path
    
    def test_allowed_markdown_prompt_ignored(self, temp_workspace, verifier):
        """Allowed markdown in .github/prompts/ is ignored."""
        allowed_file = temp_workspace / ".github" / "prompts" / "test.md"
        allowed_file.write_text("# Prompt")
        
        verifier._check_markdown_suppression()
        
        assert len(verifier.violations) == 0
    
    def test_readme_in_root_allowed(self, temp_workspace, verifier):
        """README.md in root is allowed."""
        readme = temp_workspace / "README.md"
        readme.write_text("# README")
        
        verifier._check_markdown_suppression()
        
        assert len(verifier.violations) == 0


class TestCORE008_TDDMandatory:
    """Tests for CORE-008: Tests BEFORE code."""
    
    def test_missing_test_file_detected(self, temp_workspace, verifier):
        """Missing test file is detected as TDD violation."""
        impl_file = temp_workspace / "cortex" / "example.py"
        impl_file.write_text("def func(): pass")
        
        verifier._check_tdd_mandatory()
        
        assert len(verifier.violations) == 1
        assert verifier.violations[0].rule_id == "CORE-008"
        assert "example.py" in verifier.violations[0].file_path
    
    def test_existing_test_file_passes(self, temp_workspace, verifier):
        """Existing test file passes TDD check."""
        impl_file = temp_workspace / "cortex" / "example.py"
        impl_file.write_text("def func(): pass")
        
        test_file = temp_workspace / "tests" / "unit" / "test_example.py"
        test_file.write_text("def test_func(): pass")
        
        verifier._check_tdd_mandatory()
        
        # Should not find violation for example.py
        violations_for_example = [
            v for v in verifier.violations if "example.py" in v.file_path
        ]
        assert len(violations_for_example) == 0


class TestCORE011_TypeHints:
    """Tests for CORE-011: Type hints mandatory."""
    
    def test_missing_type_hints_detected(self, temp_workspace, verifier):
        """Functions without type hints are detected."""
        py_file = temp_workspace / "cortex" / "notypes.py"
        py_file.write_text("""
def func_without_types(x):
    return x + 1
""")
        
        verifier._check_type_hints()
        
        assert len(verifier.violations) == 1
        assert verifier.violations[0].rule_id == "CORE-011"
        assert "notypes.py" in verifier.violations[0].file_path
    
    def test_complete_type_hints_passes(self, temp_workspace, verifier):
        """Functions with complete type hints pass."""
        py_file = temp_workspace / "cortex" / "typed.py"
        py_file.write_text("""
def func_with_types(x: int) -> int:
    return x + 1
""")
        
        verifier._check_type_hints()
        
        violations_for_typed = [
            v for v in verifier.violations if "typed.py" in v.file_path
        ]
        assert len(violations_for_typed) == 0


class TestCORE013_NoBareExcept:
    """Tests for CORE-013: No bare except clauses."""
    
    def test_bare_except_detected(self, temp_workspace, verifier):
        """Bare except clauses are detected."""
        py_file = temp_workspace / "cortex" / "bare_except.py"
        py_file.write_text("""
try:
    risky_operation()
except:
    pass
""")
        
        verifier._check_no_bare_except()
        
        assert len(verifier.violations) == 1
        assert verifier.violations[0].rule_id == "CORE-013"
        assert "bare_except.py" in verifier.violations[0].file_path
    
    def test_specific_except_passes(self, temp_workspace, verifier):
        """Specific exception types pass."""
        py_file = temp_workspace / "cortex" / "specific_except.py"
        py_file.write_text("""
try:
    risky_operation()
except ValueError:
    pass
""")
        
        verifier._check_no_bare_except()
        
        violations = [v for v in verifier.violations if "specific_except.py" in v.file_path]
        assert len(violations) == 0


class TestCORE028_FileNaming:
    """Tests for CORE-028: File naming conventions."""
    
    def test_screaming_case_detected(self, temp_workspace, verifier):
        """SCREAMING_CASE filenames are detected."""
        py_file = temp_workspace / "cortex" / "BAD_NAME.py"
        py_file.write_text("# Bad file name")
        
        verifier._check_file_naming()
        
        assert len(verifier.violations) == 1
        assert verifier.violations[0].rule_id == "CORE-028"
        assert "BAD_NAME.py" in verifier.violations[0].file_path
    
    def test_kebab_case_passes(self, temp_workspace, verifier):
        """kebab-case filenames pass."""
        py_file = temp_workspace / "cortex" / "good_name.py"
        py_file.write_text("# Good file name")
        
        verifier._check_file_naming()
        
        violations = [v for v in verifier.violations if "good_name.py" in v.file_path]
        assert len(violations) == 0


class TestComplianceReport:
    """Tests for ComplianceReport."""
    
    def test_compliance_report_creation(self):
        """ComplianceReport can be created."""
        report = ComplianceReport(
            total_rules=30,
            rules_checked=15,
            violations=[],
            compliance_rate=100.0,
            timestamp=datetime.now()
        )
        
        assert report.total_rules == 30
        assert report.rules_checked == 15
        assert report.is_compliant() is True
    
    def test_compliance_report_with_violations(self):
        """ComplianceReport with violations is not compliant."""
        violation = RuleViolation(
            rule_id="CORE-002",
            file_path="test.md",
            line_number=0,
            description="Test violation",
            severity="P0",
            detected_at=datetime.now()
        )
        
        report = ComplianceReport(
            total_rules=30,
            rules_checked=15,
            violations=[violation],
            compliance_rate=93.3,
            timestamp=datetime.now()
        )
        
        assert report.is_compliant() is False
        assert len(report.violations) == 1


class TestVerifyAll:
    """Tests for verify_all() method."""
    
    def test_verify_all_runs_checks(self, verifier):
        """verify_all() runs all registered checks."""
        report = verifier.verify_all()
        
        assert report.rules_checked >= 15
        assert report.total_rules == 30
        assert isinstance(report.compliance_rate, float)
    
    def test_verify_all_returns_report(self, verifier):
        """verify_all() returns ComplianceReport."""
        report = verifier.verify_all()
        
        assert isinstance(report, ComplianceReport)
        assert report.timestamp is not None


# AC_COMPLETE: AC-WAVE-K-003 ✅
