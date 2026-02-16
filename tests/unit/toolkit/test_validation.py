"""
Tests for cortex.toolkit.validation module (Phase 90 S5).

Authority: Phase 90 S-90-06
"""

from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from cortex.toolkit.validation import (
    ValidationManager,
    ValidationResult,
    ValidationLevel,
)

# Import the new ValidationCheck enum from validation.py
try:
    import sys
    from pathlib import Path as PathLib
    
    # Import from validation.py to get the correct ValidationCheck
    validation_file = PathLib(__file__).parent.parent.parent.parent / "cortex" / "toolkit" / "validation.py"
    if validation_file.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("validation_module", validation_file)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            ValidationCheck = module.ValidationCheck
    else:
        from cortex.toolkit.validation import ValidationCheck
except Exception:
    from cortex.toolkit.validation import ValidationCheck


class TestValidationManager:
    """Test ValidationManager initialization and basic operations."""

    def test_init_with_workspace_root(self, tmp_path):
        """Test initialization with workspace root."""
        manager = ValidationManager(workspace_root=tmp_path)
        assert manager.workspace_root == tmp_path
        assert manager.strict_mode is False

    def test_init_strict_mode(self, tmp_path):
        """Test initialization in strict mode."""
        manager = ValidationManager(workspace_root=tmp_path, strict_mode=True)
        assert manager.strict_mode is True

    def test_validate_governance_alignment(self, tmp_path):
        """Test governance alignment validation."""
        # Create test Python file
        test_file = tmp_path / "test_module.py"
        test_file.write_text(
            "def test_function():\n"
            "    \"\"\"Test function.\"\"\"\n"
            "    pass\n"
        )

        manager = ValidationManager(workspace_root=tmp_path)
        results = manager.validate_governance_alignment()

        assert len(results) > 0
        assert all(isinstance(r, ValidationResult) for r in results)

    def test_validate_production_readiness(self, tmp_path):
        """Test production readiness validation."""
        manager = ValidationManager(workspace_root=tmp_path)
        results = manager.validate_production_readiness()

        assert len(results) > 0
        # Should check for tests, dependencies, etc.

    def test_validate_test_coverage(self, tmp_path):
        """Test coverage validation."""
        # Create test structure
        (tmp_path / "cortex").mkdir()
        (tmp_path / "cortex" / "module.py").write_text("def func(): pass")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test_module.py").write_text("def test_func(): pass")

        manager = ValidationManager(workspace_root=tmp_path)
        result = manager.validate_test_coverage()

        assert isinstance(result, ValidationResult)
        # Check the enum value, not identity
        assert result.check.value == "test_coverage"


class TestGovernanceValidation:
    """Test governance-specific validation."""

    def test_check_tdd_compliance(self, tmp_path):
        """Test TDD compliance checking."""
        manager = ValidationManager(workspace_root=tmp_path)
        
        # Create module without tests
        (tmp_path / "cortex").mkdir()
        (tmp_path / "cortex" / "new_module.py").write_text("def func(): pass")

        result = manager.check_tdd_compliance()
        
        assert isinstance(result, ValidationResult)
        assert result.check.value == "tdd_compliance"

    def test_check_type_hints(self, tmp_path):
        """Test type hints validation."""
        test_file = tmp_path / "test_module.py"
        test_file.write_text(
            "def func(x, y):\n"  # No type hints
            "    return x + y\n"
        )

        manager = ValidationManager(workspace_root=tmp_path)
        result = manager.check_type_hints(test_file)

        assert isinstance(result, ValidationResult)
        assert result.level == ValidationLevel.WARNING

    def test_check_docstrings(self, tmp_path):
        """Test docstring validation."""
        test_file = tmp_path / "test_module.py"
        test_file.write_text(
            "def func(x: int) -> int:\n"  # No docstring
            "    return x + 1\n"
        )

        manager = ValidationManager(workspace_root=tmp_path)
        result = manager.check_docstrings(test_file)

        assert isinstance(result, ValidationResult)
        assert result.level == ValidationLevel.WARNING


class TestProductionValidation:
    """Test production readiness validation."""

    def test_check_dependencies_locked(self, tmp_path):
        """Test dependency lock file validation."""
        # Create requirements.txt
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("pytest==7.4.3\npyyaml>=6.0\n")

        manager = ValidationManager(workspace_root=tmp_path)
        result = manager.check_dependencies_locked()

        assert isinstance(result, ValidationResult)
        # Should warn about unpinned pyyaml

    def test_check_security_issues(self, tmp_path):
        """Test security issue detection."""
        test_file = tmp_path / "test_module.py"
        test_file.write_text(
            "import os\n"
            "password = 'hardcoded123'\n"  # Security issue
            "os.system('rm -rf /')\n"  # Dangerous command
        )

        manager = ValidationManager(workspace_root=tmp_path)
        result = manager.check_security_issues(test_file)

        assert isinstance(result, ValidationResult)
        assert result.level in [ValidationLevel.ERROR, ValidationLevel.CRITICAL]

    def test_check_mcp_tools_registered(self, tmp_path):
        """Test MCP tools registration validation."""
        manager = ValidationManager(workspace_root=tmp_path)
        result = manager.check_mcp_tools_registered()

        assert isinstance(result, ValidationResult)
        assert result.check.value == "mcp_tools_registered"


class TestValidationReporting:
    """Test validation reporting functionality."""

    def test_generate_validation_report(self, tmp_path):
        """Test generating validation summary report."""
        manager = ValidationManager(workspace_root=tmp_path)
        
        # Create mock results
        results = [
            ValidationResult(
                check=ValidationCheck.TDD_COMPLIANCE,
                level=ValidationLevel.OK,
                message="TDD compliance validated",
                file_path=None
            ),
            ValidationResult(
                check=ValidationCheck.TYPE_HINTS,
                level=ValidationLevel.WARNING,
                message="Missing type hints in 3 functions",
                file_path=tmp_path / "test.py"
            ),
        ]

        report = manager.generate_report(results)
        assert "total checks: 2" in report.lower()
        assert "tdd" in report.lower()
        assert "type" in report.lower()

    def test_report_includes_critical_issues(self, tmp_path):
        """Test report highlights critical issues."""
        manager = ValidationManager(workspace_root=tmp_path)
        
        results = [
            ValidationResult(
                check=ValidationCheck.SECURITY,
                level=ValidationLevel.CRITICAL,
                message="Hardcoded credentials detected",
                file_path=tmp_path / "config.py"
            ),
        ]

        report = manager.generate_report(results)
        assert "critical" in report.lower()

    def test_strict_mode_fails_on_warnings(self, tmp_path):
        """Test strict mode treats warnings as failures."""
        manager = ValidationManager(workspace_root=tmp_path, strict_mode=True)
        
        results = [
            ValidationResult(
                check=ValidationCheck.TYPE_HINTS,
                level=ValidationLevel.WARNING,
                message="Missing type hints",
                file_path=None
            ),
        ]

        # In strict mode, should indicate failure
        report = manager.generate_report(results)
        assert manager.has_failures(results) is True
