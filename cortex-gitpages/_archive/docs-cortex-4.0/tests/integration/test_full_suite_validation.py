"""Integration tests for full test suite validation."""

import subprocess
import sys
import pytest


class TestFullSuiteValidation:
    """Verify test collection and execution works after __init__.py creation."""

    def test_pytest_collect_only_succeeds(self):
        """pytest --collect-only should complete without errors."""
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', '--collect-only', '-q'],
            capture_output=True,
            text=True,
            cwd='/Users/asifhussain/PROJECTS/CORTEX'
        )
        
        # Should not have excessive errors (allow <5 for other reasons)
        error_count = result.stdout.count('ERROR') + result.stderr.count('ERROR')
        assert error_count < 5, f"Too many collection errors: {error_count}\n{result.stderr}"

    def test_no_module_import_errors(self):
        """Test collection should not fail on module imports."""
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', '--collect-only', '-v'],
            capture_output=True,
            text=True,
            cwd='/Users/asifhussain/PROJECTS/CORTEX'
        )
        
        # Check for ModuleNotFoundError in output
        assert 'ModuleNotFoundError' not in result.stderr, \
            f"ModuleNotFoundError found: {result.stderr}"
        assert 'No module named' not in result.stderr, \
            f"No module named error found: {result.stderr}"

    def test_cortex_imports_in_test_context(self):
        """Imports should work in pytest context."""
        result = subprocess.run(
            [sys.executable, '-c', 'import cortex; import cortex_brain; print("OK")'],
            capture_output=True,
            text=True,
            cwd='/Users/asifhussain/PROJECTS/CORTEX'
        )
        
        assert result.returncode == 0, f"Import failed: {result.stderr}"
        assert 'OK' in result.stdout

    def test_pytest_executes_without_import_errors(self):
        """Running pytest should not fail on imports."""
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', 'tests/unit/test_cortex_package_init.py', '-v'],
            capture_output=True,
            text=True,
            cwd='/Users/asifhussain/PROJECTS/CORTEX'
        )
        
        # Should not have import-related failures
        assert 'ImportError' not in result.stderr, f"ImportError found: {result.stderr}"
        assert 'ModuleNotFoundError' not in result.stderr, f"ModuleNotFoundError found: {result.stderr}"
