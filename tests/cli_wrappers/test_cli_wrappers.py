"""
Pytest tests for CLI wrapper implementations

Tests all 7 CLI wrappers:
- align_wrapper.py
- healthcheck_wrapper.py
- optimize_wrapper.py
- review_wrapper.py
- cleanup_wrapper.py
- deploy_wrapper.py
- regenerate_prompts_wrapper.py

Author: Asif Hussain
Phase: 4 - Testing
"""

import pytest
import subprocess
import sys
from pathlib import Path

# CORTEX root directory
CORTEX_ROOT = Path(__file__).parent.parent.parent
CLI_WRAPPERS_DIR = CORTEX_ROOT / "scripts" / "cli_wrappers"


class TestCLIWrappers:
    """Test suite for all CLI wrappers"""
    
    def _run_cli_wrapper(self, wrapper_name: str, *args):
        """Helper to run CLI wrapper and capture output"""
        wrapper_path = CLI_WRAPPERS_DIR / wrapper_name
        assert wrapper_path.exists(), f"CLI wrapper not found: {wrapper_path}"
        
        cmd = [sys.executable, str(wrapper_path)] + list(args)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(CORTEX_ROOT)
        )
        return result
    
    # ========================================
    # Help Message Tests
    # ========================================
    
    def test_align_wrapper_help(self):
        """Test align_wrapper --help output"""
        result = self._run_cli_wrapper("align_wrapper.py", "--help")
        assert result.returncode == 0
        assert "System Alignment CLI" in result.stdout
        assert "--auto-fix" in result.stdout
        assert "--dry-run" in result.stdout
    
    def test_healthcheck_wrapper_help(self):
        """Test healthcheck_wrapper --help output"""
        result = self._run_cli_wrapper("healthcheck_wrapper.py", "--help")
        assert result.returncode == 0
        assert "Health Check CLI" in result.stdout
        assert "--output" in result.stdout
        assert "--verbose" in result.stdout
    
    def test_optimize_wrapper_help(self):
        """Test optimize_wrapper --help output"""
        result = self._run_cli_wrapper("optimize_wrapper.py", "--help")
        assert result.returncode == 0
        assert "System Optimization CLI" in result.stdout
        assert "--output" in result.stdout
    
    def test_review_wrapper_help(self):
        """Test review_wrapper --help output"""
        result = self._run_cli_wrapper("review_wrapper.py", "--help")
        assert result.returncode == 0
        assert "Architectural Review CLI" in result.stdout
        assert "--scope" in result.stdout
        assert "--context" in result.stdout
    
    def test_cleanup_wrapper_help(self):
        """Test cleanup_wrapper --help output"""
        result = self._run_cli_wrapper("cleanup_wrapper.py", "--help")
        assert result.returncode == 0
        assert "Holistic Cleanup CLI" in result.stdout
        assert "--dry-run" in result.stdout
    
    def test_deploy_wrapper_help(self):
        """Test deploy_wrapper --help output"""
        result = self._run_cli_wrapper("deploy_wrapper.py", "--help")
        assert result.returncode == 0
        assert "Production Deployment CLI" in result.stdout
        assert "--dry-run" in result.stdout
    
    def test_regenerate_prompts_wrapper_help(self):
        """Test regenerate_prompts_wrapper --help output"""
        result = self._run_cli_wrapper("regenerate_prompts_wrapper.py", "--help")
        assert result.returncode == 0
        assert "Regenerate Prompts CLI" in result.stdout
        assert "--dry-run" in result.stdout
        assert "--force" in result.stdout
    
    # ========================================
    # JSON Output Tests
    # ========================================
    
    def test_align_wrapper_json_output(self):
        """Test align_wrapper --output json"""
        result = self._run_cli_wrapper(
            "align_wrapper.py",
            "--output", "json",
            "--dry-run",
            "--project-root", str(CORTEX_ROOT)
        )
        # JSON output should parse successfully
        import json
        try:
            data = json.loads(result.stdout)
            assert "operation_name" in data or "success" in data or "status" in data
        except json.JSONDecodeError:
            pytest.fail(f"Invalid JSON output: {result.stdout[:200]}")
    
    def test_healthcheck_wrapper_json_output(self):
        """Test healthcheck_wrapper --output json"""
        result = self._run_cli_wrapper(
            "healthcheck_wrapper.py",
            "--output", "json",
            "--project-root", str(CORTEX_ROOT)
        )
        import json
        try:
            data = json.loads(result.stdout)
            assert "operation_name" in data or "health_score" in data
        except json.JSONDecodeError:
            pytest.fail(f"Invalid JSON output: {result.stdout[:200]}")
    
    # ========================================
    # Exit Code Tests
    # ========================================
    
    def test_align_wrapper_dry_run_exit_code(self):
        """Test align_wrapper --dry-run returns success exit code"""
        result = self._run_cli_wrapper(
            "align_wrapper.py",
            "--dry-run",
            "--project-root", str(CORTEX_ROOT)
        )
        # Dry-run should succeed (exit code 0)
        assert result.returncode == 0, f"Dry-run failed with stderr: {result.stderr}"
    
    def test_cleanup_wrapper_dry_run_exit_code(self):
        """Test cleanup_wrapper --dry-run returns success exit code"""
        result = self._run_cli_wrapper(
            "cleanup_wrapper.py",
            "--dry-run",
            "--project-root", str(CORTEX_ROOT)
        )
        # Dry-run should succeed (exit code 0)
        assert result.returncode == 0, f"Dry-run failed with stderr: {result.stderr}"
    
    def test_deploy_wrapper_dry_run_exit_code(self):
        """Test deploy_wrapper --dry-run returns success exit code"""
        result = self._run_cli_wrapper(
            "deploy_wrapper.py",
            "--dry-run",
            "--project-root", str(CORTEX_ROOT)
        )
        # Dry-run should succeed (exit code 0)
        assert result.returncode == 0, f"Dry-run failed with stderr: {result.stderr}"
    
    def test_regenerate_prompts_wrapper_dry_run_exit_code(self):
        """Test regenerate_prompts_wrapper --dry-run returns success exit code"""
        result = self._run_cli_wrapper(
            "regenerate_prompts_wrapper.py",
            "--dry-run",
            "--project-root", str(CORTEX_ROOT)
        )
        # Dry-run should succeed (exit code 0)
        assert result.returncode == 0, f"Dry-run failed with stderr: {result.stderr}"
    
    # ========================================
    # Custom Argument Tests
    # ========================================
    
    def test_review_wrapper_custom_arguments(self):
        """Test review_wrapper with custom --scope and --context"""
        result = self._run_cli_wrapper(
            "review_wrapper.py",
            "--scope", "auth",
            "--context", "test context",
            "--output", "json",
            "--project-root", str(CORTEX_ROOT)
        )
        # Should accept custom arguments without error
        assert result.returncode == 0 or "error" not in result.stderr.lower()
    
    def test_regenerate_prompts_wrapper_force_flag(self):
        """Test regenerate_prompts_wrapper --force flag"""
        result = self._run_cli_wrapper(
            "regenerate_prompts_wrapper.py",
            "--force",
            "--dry-run",
            "--project-root", str(CORTEX_ROOT)
        )
        # Should accept --force flag
        assert result.returncode == 0
    
    # ========================================
    # Base Class Pattern Tests
    # ========================================
    
    def test_all_wrappers_have_output_arg(self):
        """Test all wrappers support --output argument"""
        wrappers = [
            "align_wrapper.py",
            "healthcheck_wrapper.py",
            "optimize_wrapper.py",
            "review_wrapper.py",
            "cleanup_wrapper.py",
            "deploy_wrapper.py",
            "regenerate_prompts_wrapper.py"
        ]
        
        for wrapper_name in wrappers:
            result = self._run_cli_wrapper(wrapper_name, "--help")
            assert "--output" in result.stdout, f"{wrapper_name} missing --output argument"
    
    def test_all_wrappers_have_verbose_arg(self):
        """Test all wrappers support --verbose argument"""
        wrappers = [
            "align_wrapper.py",
            "healthcheck_wrapper.py",
            "optimize_wrapper.py",
            "review_wrapper.py",
            "cleanup_wrapper.py",
            "deploy_wrapper.py",
            "regenerate_prompts_wrapper.py"
        ]
        
        for wrapper_name in wrappers:
            result = self._run_cli_wrapper(wrapper_name, "--help")
            assert "--verbose" in result.stdout, f"{wrapper_name} missing --verbose argument"
    
    def test_all_wrappers_have_project_root_arg(self):
        """Test all wrappers support --project-root argument"""
        wrappers = [
            "align_wrapper.py",
            "healthcheck_wrapper.py",
            "optimize_wrapper.py",
            "review_wrapper.py",
            "cleanup_wrapper.py",
            "deploy_wrapper.py",
            "regenerate_prompts_wrapper.py"
        ]
        
        for wrapper_name in wrappers:
            result = self._run_cli_wrapper(wrapper_name, "--help")
            assert "--project-root" in result.stdout, f"{wrapper_name} missing --project-root argument"


# ========================================
# CLI Wrapper Discovery Test
# ========================================

def test_all_wrappers_exist():
    """Test all expected CLI wrappers exist in scripts/cli_wrappers/"""
    expected_wrappers = [
        "base_wrapper.py",
        "__init__.py",
        "align_wrapper.py",
        "healthcheck_wrapper.py",
        "optimize_wrapper.py",
        "review_wrapper.py",
        "cleanup_wrapper.py",
        "deploy_wrapper.py",
        "regenerate_prompts_wrapper.py"
    ]
    
    for wrapper_name in expected_wrappers:
        wrapper_path = CLI_WRAPPERS_DIR / wrapper_name
        assert wrapper_path.exists(), f"Expected CLI wrapper not found: {wrapper_name}"
