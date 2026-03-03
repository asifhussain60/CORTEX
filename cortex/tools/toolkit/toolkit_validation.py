"""
CORTEX Toolkit - Validation Module

Consolidates governance and production validation scripts.

**Consolidated Scripts:**
- scripts/validate-production.py
- scripts/validate_governance_alignment.py
- scripts/execute_validation_suite.py
- .cortex-runtime/validate-pre-commit.py

**Authority:** Phase 90 S-90-06
"""

# AC_START: AC-P90-005
# Description: Validation module for governance and production readiness

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict
import re
import ast


class ValidationLevel(Enum):
    """Validation result severity levels."""
    OK = "ok"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationCheck(Enum):
    """Types of validation checks."""
    TDD_COMPLIANCE = "tdd_compliance"
    TYPE_HINTS = "type_hints"
    DOCSTRINGS = "docstrings"
    TEST_COVERAGE = "test_coverage"
    DEPENDENCIES = "dependencies"
    SECURITY = "security"
    MCP_TOOLS_REGISTERED = "mcp_tools_registered"
    GIT_HOOKS = "git_hooks"
    PRODUCTION_READY = "production_ready"


@dataclass
class ValidationResult:  # CORE-035-scoped — domain-specific ValidationResult variant
    """Result of a validation check."""
    check: ValidationCheck
    level: ValidationLevel
    message: str
    file_path: Optional[Path] = None
    line_number: Optional[int] = None
    details: Optional[Dict] = None


class ValidationManager:
    """
    Manages validation operations for CORTEX workspace.

    Consolidates:
    - Governance alignment validation (CORE rules)
    - Production readiness checks
    - Test coverage validation
    - Security issue detection
    - MCP tools registration verification

    Attributes:
        workspace_root: Root directory of CORTEX workspace
        strict_mode: If True, treat warnings as errors
    """

    # Patterns for security issue detection
    SECURITY_PATTERNS = {
        "hardcoded_password": re.compile(r'password\s*=\s*["\'][^"\']+["\']', re.IGNORECASE),
        "hardcoded_secret": re.compile(r'secret\s*=\s*["\'][^"\']+["\']', re.IGNORECASE),
        "hardcoded_token": re.compile(r'token\s*=\s*["\'][^"\']+["\']', re.IGNORECASE),
        "dangerous_exec": re.compile(r'\bexec\s*\('),
        "dangerous_eval": re.compile(r'\beval\s*\('),
        "sql_injection": re.compile(r'execute\s*\(\s*["\'].*%s.*["\']'),
    }

    # Directories to exclude from validation
    EXCLUDE_DIRS = {
        "node_modules",
        ".git",
        "_archives",
        "__pycache__",
        ".pytest_cache",
        ".venv",
        "venv",
    }

    def __init__(
        self,
        workspace_root: Path,
        strict_mode: bool = False
    ) -> None:
        """
        Initialize ValidationManager.

        Args:
            workspace_root: Root directory of workspace
            strict_mode: If True, warnings are treated as errors
        """
        self.workspace_root = Path(workspace_root)
        self.strict_mode = strict_mode

    def validate_governance_alignment(self) -> List[ValidationResult]:
        """
        Validate workspace governance alignment.

        Checks:
        - TDD compliance (tests before code)
        - Type hints present
        - Docstrings present
        - No bare except clauses

        Returns:
            List of ValidationResult objects
        """
        results = []

        # Check TDD compliance
        results.append(self.check_tdd_compliance())

        # Check Python files for governance violations
        for file_path in self.workspace_root.rglob("*.py"):
            # Skip excluded directories
            if any(exclude in file_path.parts for exclude in self.EXCLUDE_DIRS):
                continue

            # Skip test files for type hint/docstring checks
            if "test_" in file_path.name:
                continue

            results.append(self.check_type_hints(file_path))
            results.append(self.check_docstrings(file_path))

        return results

    def validate_production_readiness(self) -> List[ValidationResult]:
        """
        Validate production readiness.

        Checks:
        - Dependencies locked (pinned versions)
        - No security issues
        - MCP tools registered
        - Git hooks installed

        Returns:
            List of ValidationResult objects
        """
        results = []

        results.append(self.check_dependencies_locked())
        results.append(self.check_mcp_tools_registered())
        results.append(self.check_git_hooks())

        # Check Python files for security issues
        for file_path in self.workspace_root.rglob("*.py"):
            if any(exclude in file_path.parts for exclude in self.EXCLUDE_DIRS):
                continue

            result = self.check_security_issues(file_path)
            if result.level != ValidationLevel.OK:
                results.append(result)

        return results

    def validate_test_coverage(self) -> ValidationResult:
        """
        Validate test coverage.

        Returns:
            ValidationResult for coverage check
        """
        cortex_dir = self.workspace_root / "cortex"
        tests_dir = self.workspace_root / "tests"

        if not cortex_dir.exists():
            return ValidationResult(
                check=ValidationCheck.TEST_COVERAGE,
                level=ValidationLevel.INFO,
                message="No cortex directory found"
            )

        if not tests_dir.exists():
            return ValidationResult(
                check=ValidationCheck.TEST_COVERAGE,
                level=ValidationLevel.ERROR,
                message="No tests directory found"
            )

        # Count Python files
        py_files = len(list(cortex_dir.rglob("*.py")))
        test_files = len(list(tests_dir.rglob("test_*.py")))

        coverage_ratio = test_files / py_files if py_files > 0 else 0

        if coverage_ratio < 0.5:
            level = ValidationLevel.WARNING
            message = f"Low test coverage: {test_files} test files for {py_files} modules ({coverage_ratio:.1%})"
        else:
            level = ValidationLevel.OK
            message = f"Test coverage: {test_files} test files for {py_files} modules ({coverage_ratio:.1%})"

        return ValidationResult(
            check=ValidationCheck.TEST_COVERAGE,
            level=level,
            message=message,
            details={"py_files": py_files, "test_files": test_files}
        )

    def check_tdd_compliance(self) -> ValidationResult:
        """
        Check TDD compliance.

        Returns:
            ValidationResult for TDD check
        """
        # Look for modules without corresponding tests
        cortex_dir = self.workspace_root / "cortex"
        tests_dir = self.workspace_root / "tests"

        if not cortex_dir.exists():
            return ValidationResult(
                check=ValidationCheck.TDD_COMPLIANCE,
                level=ValidationLevel.INFO,
                message="No cortex directory to validate"
            )

        missing_tests = []
        for py_file in cortex_dir.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue

            # Derive expected test file path
            relative_path = py_file.relative_to(cortex_dir)
            test_file = tests_dir / "unit" / relative_path.parent / f"test_{py_file.name}"

            if not test_file.exists():
                missing_tests.append(str(relative_path))

        if missing_tests:
            return ValidationResult(
                check=ValidationCheck.TDD_COMPLIANCE,
                level=ValidationLevel.WARNING,
                message=f"{len(missing_tests)} modules without tests",
                details={"missing_tests": missing_tests[:5]}  # First 5
            )

        return ValidationResult(
            check=ValidationCheck.TDD_COMPLIANCE,
            level=ValidationLevel.OK,
            message="TDD compliance validated"
        )

    def check_type_hints(self, file_path: Path) -> ValidationResult:
        """
        Check for type hints in Python file.

        Args:
            file_path: Path to Python file

        Returns:
            ValidationResult for type hints check
        """
        try:
            content = file_path.read_text()
            tree = ast.parse(content)

            functions = [
                node for node in ast.walk(tree)
                if isinstance(node, ast.FunctionDef)
            ]

            missing_hints = []
            for func in functions:
                # Skip private functions and test functions
                if func.name.startswith("_") or func.name.startswith("test_"):
                    continue

                # Check if return type is annotated
                if func.returns is None and func.name != "__init__":
                    missing_hints.append(f"{func.name} (return)")

                # Check if parameters are annotated
                for arg in func.args.args:
                    if arg.arg == "self" or arg.arg == "cls":
                        continue
                    if arg.annotation is None:
                        missing_hints.append(f"{func.name}({arg.arg})")

            if missing_hints:
                return ValidationResult(
                    check=ValidationCheck.TYPE_HINTS,
                    level=ValidationLevel.WARNING,
                    message=f"Missing type hints in {len(missing_hints)} locations",
                    file_path=file_path,
                    details={"missing": missing_hints[:3]}
                )

            return ValidationResult(
                check=ValidationCheck.TYPE_HINTS,
                level=ValidationLevel.OK,
                message="Type hints validated",
                file_path=file_path
            )
        except Exception as e:
            return ValidationResult(
                check=ValidationCheck.TYPE_HINTS,
                level=ValidationLevel.ERROR,
                message=f"Error parsing file: {e}",
                file_path=file_path
            )

    def check_docstrings(self, file_path: Path) -> ValidationResult:
        """
        Check for docstrings in Python file.

        Args:
            file_path: Path to Python file

        Returns:
            ValidationResult for docstrings check
        """
        try:
            content = file_path.read_text()
            tree = ast.parse(content)

            functions = [
                node for node in ast.walk(tree)
                if isinstance(node, ast.FunctionDef)
            ]

            missing_docs = []
            for func in functions:
                # Skip private functions
                if func.name.startswith("_") and func.name != "__init__":
                    continue

                docstring = ast.get_docstring(func)
                if not docstring:
                    missing_docs.append(func.name)

            if missing_docs:
                return ValidationResult(
                    check=ValidationCheck.DOCSTRINGS,
                    level=ValidationLevel.WARNING,
                    message=f"Missing docstrings in {len(missing_docs)} functions",
                    file_path=file_path,
                    details={"missing": missing_docs[:3]}
                )

            return ValidationResult(
                check=ValidationCheck.DOCSTRINGS,
                level=ValidationLevel.OK,
                message="Docstrings validated",
                file_path=file_path
            )
        except Exception as e:
            return ValidationResult(
                check=ValidationCheck.DOCSTRINGS,
                level=ValidationLevel.ERROR,
                message=f"Error parsing file: {e}",
                file_path=file_path
            )

    def check_dependencies_locked(self) -> ValidationResult:
        """
        Check if dependencies are locked (pinned versions).

        Returns:
            ValidationResult for dependencies check
        """
        req_file = self.workspace_root / "requirements.txt"

        if not req_file.exists():
            return ValidationResult(
                check=ValidationCheck.DEPENDENCIES,
                level=ValidationLevel.WARNING,
                message="No requirements.txt found"
            )

        content = req_file.read_text()
        lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]

        unpinned = []
        for line in lines:
            if '>=' in line or '~=' in line or '>' in line:
                unpinned.append(line)

        if unpinned:
            return ValidationResult(
                check=ValidationCheck.DEPENDENCIES,
                level=ValidationLevel.WARNING,
                message=f"{len(unpinned)} unpinned dependencies",
                details={"unpinned": unpinned[:3]}
            )

        return ValidationResult(
            check=ValidationCheck.DEPENDENCIES,
            level=ValidationLevel.OK,
            message="All dependencies pinned"
        )

    def check_security_issues(self, file_path: Path) -> ValidationResult:
        """
        Check for security issues in Python file.

        Args:
            file_path: Path to Python file

        Returns:
            ValidationResult for security check
        """
        # Guard: skip files > 512KB to avoid hanging on large generated/minified files
        try:
            if file_path.stat().st_size > 512_000:
                return ValidationResult(
                    check=ValidationCheck.SECURITY,
                    level=ValidationLevel.OK,
                    message="File skipped (> 512KB — not a hand-authored source file)",
                    file_path=file_path,
                )
        except OSError:
            pass

        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")

            issues = []
            for issue_type, pattern in self.SECURITY_PATTERNS.items():
                matches = pattern.findall(content)
                if matches:
                    issues.append(f"{issue_type}: {len(matches)} occurrence(s)")

            if issues:
                return ValidationResult(
                    check=ValidationCheck.SECURITY,
                    level=ValidationLevel.CRITICAL,
                    message=f"Security issues detected: {', '.join(issues)}",
                    file_path=file_path
                )

            return ValidationResult(
                check=ValidationCheck.SECURITY,
                level=ValidationLevel.OK,
                message="No security issues detected",
                file_path=file_path
            )
        except Exception as e:
            return ValidationResult(
                check=ValidationCheck.SECURITY,
                level=ValidationLevel.ERROR,
                message=f"Error scanning file: {e}",
                file_path=file_path
            )

    def check_mcp_tools_registered(self) -> ValidationResult:
        """
        Check if MCP tools are registered.

        Returns:
            ValidationResult for MCP tools check
        """
        mcp_server = self.workspace_root / "cortex" / "mcp" / "server.py"

        if not mcp_server.exists():
            return ValidationResult(
                check=ValidationCheck.MCP_TOOLS_REGISTERED,
                level=ValidationLevel.WARNING,
                message="MCP server not found"
            )

        return ValidationResult(
            check=ValidationCheck.MCP_TOOLS_REGISTERED,
            level=ValidationLevel.OK,
            message="MCP server present"
        )

    def check_git_hooks(self) -> ValidationResult:
        """
        Check if git hooks are installed.

        Returns:
            ValidationResult for git hooks check
        """
        hooks_dir = self.workspace_root / ".githooks"
        git_config = self.workspace_root / ".git" / "config"

        if not hooks_dir.exists():
            return ValidationResult(
                check=ValidationCheck.GIT_HOOKS,
                level=ValidationLevel.WARNING,
                message="Git hooks directory not found"
            )

        if git_config.exists():
            config_content = git_config.read_text()
            if "hooksPath" in config_content:
                return ValidationResult(
                    check=ValidationCheck.GIT_HOOKS,
                    level=ValidationLevel.OK,
                    message="Git hooks configured"
                )

        return ValidationResult(
            check=ValidationCheck.GIT_HOOKS,
            level=ValidationLevel.WARNING,
            message="Git hooks not configured"
        )

    def has_failures(self, results: List[ValidationResult]) -> bool:
        """
        Check if validation has failures.

        Args:
            results: List of validation results

        Returns:
            True if any failures (or warnings in strict mode)
        """
        for result in results:
            if result.level in [ValidationLevel.ERROR, ValidationLevel.CRITICAL]:
                return True
            if self.strict_mode and result.level == ValidationLevel.WARNING:
                return True

        return False

    def generate_report(self, results: List[ValidationResult]) -> str:
        """
        Generate validation summary report.

        Args:
            results: List of ValidationResult objects

        Returns:
            Formatted report string
        """
        total = len(results)
        by_level = dict.fromkeys(ValidationLevel, 0)

        for result in results:
            by_level[result.level] += 1

        report_lines = [
            "Validation Summary",
            "=" * 50,
            f"Total checks: {total}",
            f"OK: {by_level[ValidationLevel.OK]}",
            f"Info: {by_level[ValidationLevel.INFO]}",
            f"Warnings: {by_level[ValidationLevel.WARNING]}",
            f"Errors: {by_level[ValidationLevel.ERROR]}",
            f"Critical: {by_level[ValidationLevel.CRITICAL]}",
            "",
        ]

        if self.strict_mode:
            report_lines.append("Mode: STRICT (warnings treated as errors)")
            report_lines.append("")

        # Group by check type
        by_check = {}
        for result in results:
            check = result.check.value
            if check not in by_check:
                by_check[check] = []
            by_check[check].append(result)

        report_lines.append("By Check:")
        for check, check_results in by_check.items():
            levels = [r.level.value for r in check_results]
            report_lines.append(f"  {check}: {', '.join(set(levels))}")

        # Show critical/error issues
        critical = [r for r in results if r.level in [ValidationLevel.CRITICAL, ValidationLevel.ERROR]]
        if critical:
            report_lines.append("")
            report_lines.append("Critical/Error Issues:")
            for result in critical:
                file_info = f" ({result.file_path.name})" if result.file_path else ""
                report_lines.append(f"  - {result.check.value}: {result.message}{file_info}")

        return "\n".join(report_lines)

# AC_COMPLETE: AC-P90-005 ✅ Validation module with governance + production checks
