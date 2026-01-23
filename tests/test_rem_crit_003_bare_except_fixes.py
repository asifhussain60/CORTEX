"""Tests for REM-CRIT-003: Bare Except Fixes.

Verifies that bare except clauses have been replaced with specific exception handling.

Test Coverage:
- phase_b3_update.py: OSError, IOError, UnicodeDecodeError handling
- phase_b2_update.py: OSError, IOError, UnicodeDecodeError handling  
- migration-validator.py: OSError, IOError, ValueError handling
"""

import logging
import os
import tempfile
from pathlib import Path
import re

import pytest


class TestPhaseB3UpdateExceptionHandling:
    """Test phase_b3_update.py exception handling."""

    def test_no_bare_except_clauses(self) -> None:
        """Verify no bare except clauses in phase_b3_update.py."""
        script_path = Path(__file__).parent.parent / "cortex" / "scripts-root-archive" / "utilities" / "phase_b3_update.py"
        assert script_path.exists(), f"File not found: {script_path}"
        
        content = script_path.read_text(encoding='utf-8')
        
        # Check for bare except clauses
        bare_except_pattern = r'except\s*:\s*(?:pass|$)'
        matches = re.findall(bare_except_pattern, content)
        
        assert len(matches) == 0, f"Found bare except clauses in phase_b3_update.py: {matches}"

    def test_specific_exception_handling(self) -> None:
        """Verify specific exception types are caught."""
        script_path = Path(__file__).parent.parent / "cortex" / "scripts-root-archive" / "utilities" / "phase_b3_update.py"
        content = script_path.read_text(encoding='utf-8')
        
        # Should have specific exception handling
        assert "except (OSError, IOError, UnicodeDecodeError)" in content
        assert "logging.warning" in content


class TestPhaseB2UpdateExceptionHandling:
    """Test phase_b2_update.py exception handling."""

    def test_no_bare_except_clauses(self) -> None:
        """Verify no bare except clauses in phase_b2_update.py."""
        script_path = Path(__file__).parent.parent / "cortex" / "scripts-root-archive" / "utilities" / "phase_b2_update.py"
        assert script_path.exists(), f"File not found: {script_path}"
        
        content = script_path.read_text(encoding='utf-8')
        
        # Check for bare except clauses
        bare_except_pattern = r'except\s*:\s*(?:pass|$)'
        matches = re.findall(bare_except_pattern, content)
        
        assert len(matches) == 0, f"Found bare except clauses in phase_b2_update.py: {matches}"

    def test_specific_exception_handling(self) -> None:
        """Verify specific exception types are caught."""
        script_path = Path(__file__).parent.parent / "cortex" / "scripts-root-archive" / "utilities" / "phase_b2_update.py"
        content = script_path.read_text(encoding='utf-8')
        
        # Should have specific exception handling
        assert "except (OSError, IOError, UnicodeDecodeError)" in content
        assert "logging.warning" in content


class TestMigrationValidatorExceptionHandling:
    """Test migration-validator.py exception handling."""

    def test_no_bare_except_clauses(self) -> None:
        """Verify no bare except clauses in migration-validator.py."""
        script_path = Path(__file__).parent.parent / "cortex" / "scripts-root-archive" / "migration-validator.py"
        assert script_path.exists(), f"File not found: {script_path}"
        
        content = script_path.read_text(encoding='utf-8')
        
        # Check for bare except clauses
        bare_except_pattern = r'except\s*:\s*(?:pass|$)'
        matches = re.findall(bare_except_pattern, content)
        
        assert len(matches) == 0, f"Found bare except clauses in migration-validator.py: {matches}"

    def test_specific_exception_handling(self) -> None:
        """Verify specific exception types are caught."""
        script_path = Path(__file__).parent.parent / "cortex" / "scripts-root-archive" / "migration-validator.py"
        content = script_path.read_text(encoding='utf-8')
        
        # Should have specific exception handling
        assert "except (OSError, IOError, ValueError)" in content
        assert "logging.warning" in content


class TestCortexWideNoBareBareExcepts:
    """Verify no bare excepts remain in critical cortex files."""

    def test_no_bare_excepts_in_cortex_tools(self) -> None:
        """Scan cortex/tools for bare except clauses."""
        tools_dir = Path(__file__).parent.parent / "cortex" / "tools"
        if not tools_dir.exists():
            pytest.skip("cortex/tools not found")
        
        bare_except_pattern = r'except\s*:\s*(?:pass|$)'
        
        for py_file in tools_dir.rglob("*.py"):
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            matches = re.findall(bare_except_pattern, content)
            assert len(matches) == 0, f"Found bare except in {py_file.relative_to(tools_dir)}"

    def test_no_bare_excepts_in_cortex_testing(self) -> None:
        """Scan cortex/testing for bare except clauses."""
        testing_dir = Path(__file__).parent.parent / "cortex" / "testing"
        if not testing_dir.exists():
            pytest.skip("cortex/testing not found")
        
        bare_except_pattern = r'except\s*:\s*(?:pass|$)'
        
        for py_file in testing_dir.rglob("*.py"):
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            matches = re.findall(bare_except_pattern, content)
            assert len(matches) == 0, f"Found bare except in {py_file.relative_to(testing_dir)}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
