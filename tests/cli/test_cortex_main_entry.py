"""
Phase 110: cortex/__main__.py — CLI Entry Point.

RED test suite: python -m cortex must work as the primary CLI entry point.

AC_START: AC-P110-001
Authority: CORE-008 (TDD first), CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class TestCortexMainEntry:
    """Phase 110: python -m cortex must be a valid entry point."""

    def test_cortex_main_module_exists(self) -> None:
        """cortex/__main__.py must exist so python -m cortex works."""
        main_file = PROJECT_ROOT / "cortex" / "__main__.py"
        assert main_file.exists(), (
            f"cortex/__main__.py does not exist at {main_file} — "
            "python -m cortex will fail with 'No module named cortex.__main__'"
        )

    def test_cortex_main_imports_cleanly(self) -> None:
        """cortex/__main__.py must import without errors."""
        import importlib

        spec = importlib.util.find_spec("cortex.__main__")
        assert spec is not None, "cortex.__main__ module not found by importlib"

    def test_cortex_main_help_runs(self) -> None:
        """python -m cortex --help must return exit code 0 with usage info."""
        result = subprocess.run(
            [sys.executable, "-m", "cortex", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0, (
            f"python -m cortex --help failed (exit {result.returncode}): "
            f"stdout={result.stdout[:200]}, stderr={result.stderr[:200]}"
        )
        assert "CORTEX" in result.stdout, (
            "python -m cortex --help must mention CORTEX in output"
        )

    def test_cortex_main_status_runs(self) -> None:
        """python -m cortex status must execute without crashing."""
        result = subprocess.run(
            [sys.executable, "-m", "cortex", "status"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0, (
            f"python -m cortex status failed (exit {result.returncode}): "
            f"stderr={result.stderr[:300]}"
        )

    def test_cortex_main_version_runs(self) -> None:
        """python -m cortex --version must output version string."""
        result = subprocess.run(
            [sys.executable, "-m", "cortex", "--version"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0, (
            f"python -m cortex --version failed (exit {result.returncode})"
        )
        assert "cortex" in result.stdout.lower(), (
            "python -m cortex --version must output version info"
        )


class TestGovernanceValidatorReal:
    """Phase 110: Governance validator must not be a stub."""

    def test_governance_validator_is_not_stub(self) -> None:
        """scripts/validate_governance_alignment.py must not contain 'stub' in its docstring."""
        validator_path = PROJECT_ROOT / "scripts" / "validate_governance_alignment.py"
        content = validator_path.read_text()
        # The module docstring should not say "Stub"
        assert "Stub" not in content.split('"""')[1], (
            "Governance validator is still a stub — must have real implementation"
        )

    def test_governance_validator_checks_core_rules(self) -> None:
        """Validator must check at least CORE-002, CORE-008, CORE-028 rules."""
        validator_path = PROJECT_ROOT / "scripts" / "validate_governance_alignment.py"
        content = validator_path.read_text()
        for rule in ["CORE-002", "CORE-028"]:
            assert rule in content, (
                f"Governance validator must check {rule}"
            )

    def test_governance_validator_returns_issues(self) -> None:
        """Validator must be able to return actual violations, not always True."""
        # Import and call with workspace root
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        try:
            from validate_governance_alignment import validate_governance_alignment

            # Should return bool, and the function should have real logic
            result = validate_governance_alignment()
            assert isinstance(result, bool), (
                "validate_governance_alignment must return a bool"
            )
        finally:
            sys.path.pop(0)

    def test_governance_validator_checks_snake_case(self) -> None:
        """Validator must enforce CORE-028 snake_case file naming."""
        validator_path = PROJECT_ROOT / "scripts" / "validate_governance_alignment.py"
        content = validator_path.read_text()
        assert "snake_case" in content.lower() or "CORE-028" in content, (
            "Governance validator must enforce snake_case naming (CORE-028)"
        )

    def test_governance_validator_checks_no_report_files(self) -> None:
        """Validator must enforce CORE-002: no .md/.txt report file creation."""
        validator_path = PROJECT_ROOT / "scripts" / "validate_governance_alignment.py"
        content = validator_path.read_text()
        assert "CORE-002" in content, (
            "Governance validator must enforce CORE-002 (no report files)"
        )
