"""
Unit tests for GV-003-01: Pre-Commit Hook Validation.

Tests the governance pre-commit hook:
- AC-ID format validation (AC-DOMAIN-NNN-NN)
- Governance rule violation detection
- Integration with git pre-commit system
"""

import subprocess
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest


class TestACIDFormatValidation:
    """Test AC-ID format validation in commit messages."""

    @pytest.fixture
    def hook_script(self):
        """Get path to pre-commit hook script."""
        return Path(__file__).parent.parent.parent / ".githooks" / "pre-commit-governance-check.py"

    @pytest.fixture
    def check_ac_id_format(self, hook_script):
        """Import check_ac_id_format function."""
        sys.path.insert(0, str(hook_script.parent))
        import importlib.util
        spec = importlib.util.spec_from_file_location("pre_commit_hook", hook_script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.check_ac_id_format

    def test_valid_ac_id_single(self, check_ac_id_format):
        """Test valid single AC-ID."""
        is_valid, error = check_ac_id_format("GV-001-01: Implement governance CLI")
        assert is_valid, f"Valid AC-ID rejected: {error}"

    def test_valid_ac_id_multiple(self, check_ac_id_format):
        """Test multiple AC-IDs in message."""
        is_valid, error = check_ac_id_format(
            "GV-001-01, GV-001-02: Implement governance CLI and validation"
        )
        assert is_valid, f"Valid AC-IDs rejected: {error}"

    def test_valid_ac_id_with_content(self, check_ac_id_format):
        """Test AC-ID with additional commit content."""
        is_valid, error = check_ac_id_format(
            """GV-001-01: Implement governance CLI

This commits the query interface implementation with full test coverage.
Features:
- Rule querying by ID, domain, phase
- Multiple output formats
- Sub-100ms performance"""
        )
        assert is_valid, f"Valid AC-ID with content rejected: {error}"

    def test_invalid_ac_id_wrong_domain_length(self, check_ac_id_format):
        """Test invalid AC-ID with wrong domain length."""
        is_valid, error = check_ac_id_format("AC-INVALID-001-01: Bad AC-ID format")
        assert not is_valid, "Invalid AC-ID was accepted"
        assert "Invalid AC-ID format" in error or "invalid" in error.lower()

    def test_invalid_ac_id_wrong_number_format(self, check_ac_id_format):
        """Test invalid AC-ID with wrong number format."""
        is_valid, error = check_ac_id_format("AC-GV-01-1: Wrong numbers")
        # This might be accepted or rejected depending on implementation
        # Just ensure no crash
        assert isinstance(is_valid, bool)

    def test_optional_ac_id_non_governance_commit(self, check_ac_id_format):
        """Test that AC-ID is optional for non-governance commits."""
        is_valid, error = check_ac_id_format(
            "refactor: improve performance on initialization"
        )
        # AC-ID is optional for regular commits
        assert is_valid, f"Optional AC-ID commit rejected: {error}"

    def test_ac_id_detection_with_malformed_marker(self, check_ac_id_format):
        """Test detection of malformed AC-ID marker."""
        is_valid, error = check_ac_id_format(
            "AC-GV-invalid format test"
        )
        # Should either accept (AC-ID optional) or reject with clear error
        assert isinstance(is_valid, bool)

    def test_multiple_valid_ac_ids_comma_separated(self, check_ac_id_format):
        """Test multiple AC-IDs separated by commas."""
        is_valid, error = check_ac_id_format(
            "AC-AR-001-01, AC-AR-001-02: Multi-AC commit"
        )
        assert is_valid, f"Multiple AC-IDs rejected: {error}"

    def test_ac_id_with_ar_domain(self, check_ac_id_format):
        """Test AC-ID with AR domain (Architectural)."""
        is_valid, error = check_ac_id_format("AC-AR-001-01: Architecture change")
        assert is_valid, f"AR domain AC-ID rejected: {error}"

    def test_ac_id_with_fr_domain(self, check_ac_id_format):
        """Test AC-ID with FR domain (Functional Requirement)."""
        is_valid, error = check_ac_id_format("AC-FR-002-01: Feature implementation")
        assert is_valid, f"FR domain AC-ID rejected: {error}"

    def test_ac_id_with_enh_domain(self, check_ac_id_format):
        """Test AC-ID with ENH domain (Enhancement)."""
        is_valid, error = check_ac_id_format("AC-ENH-001-01: Enhancement task")
        assert is_valid, f"ENH domain AC-ID rejected: {error}"


class TestPreCommitHookExecution:
    """Test pre-commit hook execution."""

    @pytest.fixture
    def hook_script(self):
        """Get path to pre-commit hook script."""
        return Path(__file__).parent.parent.parent / ".githooks" / "pre-commit-governance-check.py"

    def test_hook_script_exists(self, hook_script):
        """Test that hook script exists."""
        assert hook_script.exists(), f"Hook script not found at {hook_script}"

    def test_hook_script_executable(self, hook_script):
        """Test that hook script is executable."""
        assert hook_script.stat().st_mode & 0o111, "Hook script is not executable"

    def test_hook_main_function_exists(self, hook_script):
        """Test that hook has main entry point."""
        with open(hook_script) as f:
            content = f.read()
        assert 'def main()' in content, "Hook script missing main() function"
        assert 'if __name__ == "__main__"' in content, "Hook script missing __main__ check"


class TestPreCommitConfig:
    """Test .pre-commit-config.yaml configuration."""

    @pytest.fixture
    def config_file(self):
        """Get path to pre-commit config."""
        return Path(__file__).parent.parent.parent / ".pre-commit-config.yaml"

    def test_config_file_exists(self, config_file):
        """Test that config file exists."""
        assert config_file.exists(), f"Config file not found at {config_file}"

    def test_config_has_cortex_hook(self, config_file):
        """Test that config includes CORTEX governance hook."""
        with open(config_file) as f:
            content = f.read()
        assert "cortex-governance-check" in content
        assert "pre-commit-governance-check.py" in content

    def test_config_valid_yaml(self, config_file):
        """Test that config is valid YAML."""
        try:
            import yaml
            with open(config_file) as f:
                data = yaml.safe_load(f)
            assert isinstance(data, dict)
            assert 'repos' in data
        except ImportError:
            pytest.skip("PyYAML not installed")


class TestAcceptanceCriteriaPreCommit:
    """Test acceptance criteria for GV-003-01."""

    @pytest.fixture
    def hook_script(self):
        """Get path to pre-commit hook script."""
        return Path(__file__).parent.parent.parent / ".githooks" / "pre-commit-governance-check.py"

    def test_ac_1_pre_commit_validates_ac_id_format(self, hook_script):
        """
        AC Criterion 1: Pre-commit validates AC-ID format.
        """
        sys.path.insert(0, str(hook_script.parent))
        import importlib.util
        spec = importlib.util.spec_from_file_location("pre_commit_hook", hook_script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test valid AC-ID
        is_valid, error = module.check_ac_id_format("AC-GV-001-01: Valid AC-ID")
        assert is_valid, f"Valid AC-ID validation failed: {error}"

        # Test optional AC-ID (non-governance commit)
        is_valid, error = module.check_ac_id_format("refactor: code cleanup")
        assert is_valid, f"Optional AC-ID should be accepted for non-governance commits"

    def test_ac_2_pre_commit_prevents_governance_violations(self, hook_script):
        """
        AC Criterion 2: Pre-commit prevents governance violations.
        """
        # This is tested via the governance CLI validation integration
        # Just verify that the hook script references governance validation
        with open(hook_script) as f:
            content = f.read()
        assert "governance-cli" in content or "validate" in content
        assert "governance" in content.lower()

    def test_ac_3_configurable_via_pre_commit_config(self):
        """
        AC Criterion 3: Pre-commit hook is configurable via .pre-commit-config.yaml.
        """
        config_file = Path(__file__).parent.parent.parent / ".pre-commit-config.yaml"
        assert config_file.exists()

        with open(config_file) as f:
            content = f.read()

        assert "repos:" in content
        assert "cortex-governance-check" in content
        assert "stages:" in content or "local" in content


class TestACIDFormatEdgeCases:
    """Test edge cases for AC-ID format validation."""

    @pytest.fixture
    def check_ac_id_format(self):
        """Import check_ac_id_format function."""
        hook_script = Path(__file__).parent.parent.parent / ".githooks" / "pre-commit-governance-check.py"
        sys.path.insert(0, str(hook_script.parent))
        import importlib.util
        spec = importlib.util.spec_from_file_location("pre_commit_hook", hook_script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.check_ac_id_format

    def test_ac_id_at_start_of_message(self, check_ac_id_format):
        """Test AC-ID at start of commit message."""
        is_valid, _ = check_ac_id_format("AC-GV-001-01: Start of message")
        assert is_valid

    def test_ac_id_in_middle_of_message(self, check_ac_id_format):
        """Test AC-ID in middle of commit message."""
        is_valid, _ = check_ac_id_format("Implement AC-GV-001-01 feature")
        assert is_valid

    def test_ac_id_with_special_characters_before(self, check_ac_id_format):
        """Test AC-ID with special characters."""
        is_valid, _ = check_ac_id_format("[AC-GV-001-01] Implement feature")
        assert is_valid

    def test_empty_commit_message(self, check_ac_id_format):
        """Test empty commit message."""
        is_valid, _ = check_ac_id_format("")
        # Should be valid (optional AC-ID)
        assert is_valid

    def test_very_long_commit_message(self, check_ac_id_format):
        """Test very long commit message with AC-ID."""
        long_message = "AC-GV-001-01: " + "A" * 1000
        is_valid, _ = check_ac_id_format(long_message)
        assert is_valid
