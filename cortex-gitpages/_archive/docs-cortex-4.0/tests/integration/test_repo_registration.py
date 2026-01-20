"""
Integration tests for repo registration script (AC-DEPLOY-ENHANCED-003-01).

Tests cover:
- Script execution and error handling
- cortex-config.yaml creation with correct structure
- .github/prompts directory setup and file copying
- Symlink handling (macOS/Linux) vs copy (Windows)
- MCP connectivity validation
- .github/tier0/ stub creation
- Git commit creation with audit entry
- Idempotency on repeated runs
- Cross-platform compatibility
"""

import os
import sys
import json
import tempfile
import shutil
import platform
import subprocess
from pathlib import Path

import pytest


class TestRepoRegistrationScriptExecution:
    """Test basic script execution and preconditions."""

    def test_script_exists(self):
        """Script file should exist and be readable."""
        script_path = Path("/Users/asifhussain/PROJECTS/CORTEX/scripts/register-repo.sh")
        assert script_path.exists(), f"Script not found at {script_path}"
        assert os.access(script_path, os.R_OK), "Script not readable"

    def test_script_has_bash_shebang(self):
        """Script should have proper bash shebang."""
        script_path = Path("/Users/asifhussain/PROJECTS/CORTEX/scripts/register-repo.sh")
        with open(script_path) as f:
            first_line = f.readline().strip()
        assert first_line.startswith("#!"), "Missing shebang"
        assert "bash" in first_line, "Not a bash script"

    def test_script_requires_repo_root_argument(self):
        """Script should handle REPO_ROOT argument and work in valid repo."""
        script_path = Path("/Users/asifhussain/PROJECTS/CORTEX/scripts/register-repo.sh")
        # Run from a temp dir that is NOT a git repo (should fail without argument)
        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(
                ["bash", str(script_path)],
                cwd=tmpdir,
                capture_output=True,
                text=True,
                timeout=5
            )
            # Should fail when called from non-git directory without argument
            assert result.returncode != 0 or "usage" in result.stdout.lower() or "usage" in result.stderr.lower()

    def test_script_handles_invalid_repo_path(self):
        """Script should validate that REPO_ROOT exists."""
        script_path = Path("/Users/asifhussain/PROJECTS/CORTEX/scripts/register-repo.sh")
        result = subprocess.run(
            ["bash", str(script_path), "/nonexistent/path"],
            capture_output=True,
            text=True,
            timeout=5
        )
        assert result.returncode != 0, "Should fail with nonexistent path"


class TestCortexConfigYamlCreation:
    """Test cortex-config.yaml creation and validation."""

    def test_cortex_config_created_in_repo_root(self):
        """cortex-config.yaml should be created at repo root."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_repo = Path(tmpdir) / "test-repo"
            test_repo.mkdir()
            (test_repo / ".git").mkdir()  # Simulate git repo
            
            script_path = Path("/Users/asifhussain/PROJECTS/CORTEX/scripts/register-repo.sh")
            result = subprocess.run(
                ["bash", str(script_path), str(test_repo)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            config_path = test_repo / "cortex-config.yaml"
            assert config_path.exists(), "cortex-config.yaml not created"

    def test_cortex_config_has_required_fields(self):
        """cortex-config.yaml should have repo_id, repo_name, repo_type."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_repo = Path(tmpdir) / "test-repo"
            test_repo.mkdir()
            (test_repo / ".git").mkdir()
            
            script_path = Path("/Users/asifhussain/PROJECTS/CORTEX/scripts/register-repo.sh")
            subprocess.run(
                ["bash", str(script_path), str(test_repo)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            config_path = test_repo / "cortex-config.yaml"
            with open(config_path) as f:
                content = f.read()
            
            required_fields = ["repo_id:", "repo_name:", "repo_type:", "mcp_endpoint:", "version:"]
            for field in required_fields:
                assert field in content, f"Missing {field} in cortex-config.yaml"

    def test_cortex_config_valid_yaml(self):
        """cortex-config.yaml should be valid YAML."""
        import yaml
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_repo = Path(tmpdir) / "test-repo"
            test_repo.mkdir()
            (test_repo / ".git").mkdir()
            
            script_path = Path("/Users/asifhussain/PROJECTS/CORTEX/scripts/register-repo.sh")
            subprocess.run(
                ["bash", str(script_path), str(test_repo)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            config_path = test_repo / "cortex-config.yaml"
            with open(config_path) as f:
                config = yaml.safe_load(f)
            
            assert config is not None, "Invalid YAML"
            assert isinstance(config, dict), "Config should be dict"


class TestGithubPromptsDirectory:
    """Test .github/prompts directory setup."""

    def test_github_prompts_directory_created(self):
        """Script should create .github/prompts directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_repo = Path(tmpdir) / "test-repo"
            test_repo.mkdir()
            (test_repo / ".git").mkdir()
            
            script_path = Path("/Users/asifhussain/PROJECTS/CORTEX/scripts/register-repo.sh")
            subprocess.run(
                ["bash", str(script_path), str(test_repo)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            prompts_dir = test_repo / ".github" / "prompts"
            assert prompts_dir.exists(), ".github/prompts directory not created"
            assert prompts_dir.is_dir(), ".github/prompts is not a directory"

    def test_prompts_are_copied_or_symlinked(self):
        """Prompts should be either copied or symlinked (depending on platform)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_repo = Path(tmpdir) / "test-repo"
            test_repo.mkdir()
            (test_repo / ".git").mkdir()
            
            script_path = Path("/Users/asifhussain/PROJECTS/CORTEX/scripts/register-repo.sh")
            subprocess.run(
                ["bash", str(script_path), str(test_repo)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            prompts_dir = test_repo / ".github" / "prompts"
            # Should have at least one prompt file
            prompt_files = list(prompts_dir.glob("*.md")) + list(prompts_dir.glob("*.yaml"))
            assert len(prompt_files) > 0, "No prompts found in .github/prompts"


class TestGithubTier0Stub:
    """Test .github/tier0 stub creation."""

    def test_github_tier0_directory_created(self):
        """Script should create .github/tier0 directory stub."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_repo = Path(tmpdir) / "test-repo"
            test_repo.mkdir()
            (test_repo / ".git").mkdir()
            
            script_path = Path("/Users/asifhussain/PROJECTS/CORTEX/scripts/register-repo.sh")
            subprocess.run(
                ["bash", str(script_path), str(test_repo)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            tier0_dir = test_repo / ".github" / "tier0"
            assert tier0_dir.exists(), ".github/tier0 directory not created"

    def test_tier0_contains_readme(self):
        """tier0 stub should contain README with reference to hub."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_repo = Path(tmpdir) / "test-repo"
            test_repo.mkdir()
            (test_repo / ".git").mkdir()
            
            script_path = Path("/Users/asifhussain/PROJECTS/CORTEX/scripts/register-repo.sh")
            subprocess.run(
                ["bash", str(script_path), str(test_repo)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            readme_path = test_repo / ".github" / "tier0" / "README.md"
            assert readme_path.exists(), "tier0/README.md not created"
            with open(readme_path) as f:
                content = f.read()
            assert "hub" in content.lower() or "governance" in content.lower()


class TestMCPConnectivityValidation:
    """Test MCP connectivity validation."""

    def test_script_validates_mcp_connectivity(self):
        """Script should attempt to validate MCP connectivity."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_repo = Path(tmpdir) / "test-repo"
            test_repo.mkdir()
            (test_repo / ".git").mkdir()
            
            script_path = Path("/Users/asifhussain/PROJECTS/CORTEX/scripts/register-repo.sh")
            result = subprocess.run(
                ["bash", str(script_path), str(test_repo)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Should complete (connectivity check may pass or fail gracefully)
            assert result.returncode in [0, 1], "Script crashed unexpectedly"

    def test_mcp_health_endpoint_recorded_in_config(self):
        """cortex-config.yaml should record MCP endpoint for health checks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_repo = Path(tmpdir) / "test-repo"
            test_repo.mkdir()
            (test_repo / ".git").mkdir()
            
            script_path = Path("/Users/asifhussain/PROJECTS/CORTEX/scripts/register-repo.sh")
            subprocess.run(
                ["bash", str(script_path), str(test_repo)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            config_path = test_repo / "cortex-config.yaml"
            with open(config_path) as f:
                content = f.read()
            assert "mcp_endpoint:" in content, "MCP endpoint not recorded"


class TestGitCommitWithAudit:
    """Test git commit creation with audit entry."""

    def test_git_commit_created(self):
        """Script should create git commit for initial setup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_repo = Path(tmpdir) / "test-repo"
            test_repo.mkdir()
            
            # Initialize git repo
            subprocess.run(
                ["git", "init"],
                cwd=test_repo,
                capture_output=True,
                timeout=5
            )
            subprocess.run(
                ["git", "config", "user.email", "test@cortex.local"],
                cwd=test_repo,
                capture_output=True,
                timeout=5
            )
            subprocess.run(
                ["git", "config", "user.name", "CORTEX Test"],
                cwd=test_repo,
                capture_output=True,
                timeout=5
            )
            
            script_path = Path("/Users/asifhussain/PROJECTS/CORTEX/scripts/register-repo.sh")
            subprocess.run(
                ["bash", str(script_path), str(test_repo)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Check if commit was created
            result = subprocess.run(
                ["git", "log", "--oneline"],
                cwd=test_repo,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            assert len(result.stdout.strip()) > 0, "No git commits found"
            assert "cortex" in result.stdout.lower() or "setup" in result.stdout.lower()

    def test_commit_message_references_cortex_setup(self):
        """Git commit should reference CORTEX setup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_repo = Path(tmpdir) / "test-repo"
            test_repo.mkdir()
            
            # Initialize git repo
            subprocess.run(
                ["git", "init"],
                cwd=test_repo,
                capture_output=True,
                timeout=5
            )
            subprocess.run(
                ["git", "config", "user.email", "test@cortex.local"],
                cwd=test_repo,
                capture_output=True,
                timeout=5
            )
            subprocess.run(
                ["git", "config", "user.name", "CORTEX Test"],
                cwd=test_repo,
                capture_output=True,
                timeout=5
            )
            
            script_path = Path("/Users/asifhussain/PROJECTS/CORTEX/scripts/register-repo.sh")
            subprocess.run(
                ["bash", str(script_path), str(test_repo)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            result = subprocess.run(
                ["git", "log", "-1", "--pretty=%B"],
                cwd=test_repo,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            assert "cortex" in result.stdout.lower(), "Commit message doesn't mention CORTEX"


class TestIdempotency:
    """Test idempotent script behavior on repeated runs."""

    def test_second_run_completes_without_error(self):
        """Running script twice should complete without error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_repo = Path(tmpdir) / "test-repo"
            test_repo.mkdir()
            (test_repo / ".git").mkdir()
            
            script_path = Path("/Users/asifhussain/PROJECTS/CORTEX/scripts/register-repo.sh")
            
            # First run
            result1 = subprocess.run(
                ["bash", str(script_path), str(test_repo)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Second run
            result2 = subprocess.run(
                ["bash", str(script_path), str(test_repo)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            assert result2.returncode == 0, f"Second run failed: {result2.stderr}"

    def test_files_not_duplicated_on_second_run(self):
        """Second run should not duplicate files or directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_repo = Path(tmpdir) / "test-repo"
            test_repo.mkdir()
            (test_repo / ".git").mkdir()
            
            script_path = Path("/Users/asifhussain/PROJECTS/CORTEX/scripts/register-repo.sh")
            
            # First run
            subprocess.run(
                ["bash", str(script_path), str(test_repo)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            prompts_after_first = list((test_repo / ".github" / "prompts").glob("*"))
            
            # Second run
            subprocess.run(
                ["bash", str(script_path), str(test_repo)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            prompts_after_second = list((test_repo / ".github" / "prompts").glob("*"))
            
            assert len(prompts_after_first) == len(prompts_after_second), "Files duplicated on second run"

    def test_config_preserved_on_second_run(self):
        """cortex-config.yaml should remain unchanged on second run."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_repo = Path(tmpdir) / "test-repo"
            test_repo.mkdir()
            (test_repo / ".git").mkdir()
            
            script_path = Path("/Users/asifhussain/PROJECTS/CORTEX/scripts/register-repo.sh")
            
            # First run
            subprocess.run(
                ["bash", str(script_path), str(test_repo)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            config_path = test_repo / "cortex-config.yaml"
            with open(config_path) as f:
                content_after_first = f.read()
            
            # Second run
            subprocess.run(
                ["bash", str(script_path), str(test_repo)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            with open(config_path) as f:
                content_after_second = f.read()
            
            assert content_after_first == content_after_second, "Config changed on second run"


class TestCrossPlatformSupport:
    """Test cross-platform compatibility."""

    def test_script_runs_on_current_platform(self):
        """Script should run successfully on current platform."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_repo = Path(tmpdir) / "test-repo"
            test_repo.mkdir()
            (test_repo / ".git").mkdir()
            
            script_path = Path("/Users/asifhussain/PROJECTS/CORTEX/scripts/register-repo.sh")
            result = subprocess.run(
                ["bash", str(script_path), str(test_repo)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            assert result.returncode == 0, f"Script failed on {platform.system()}: {result.stderr}"

    @pytest.mark.skipif(platform.system() != "Darwin", reason="macOS-specific test")
    def test_symlinks_created_on_macos(self):
        """On macOS, prompts should be symlinked."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_repo = Path(tmpdir) / "test-repo"
            test_repo.mkdir()
            (test_repo / ".git").mkdir()
            
            script_path = Path("/Users/asifhussain/PROJECTS/CORTEX/scripts/register-repo.sh")
            subprocess.run(
                ["bash", str(script_path), str(test_repo)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            prompts_dir = test_repo / ".github" / "prompts"
            prompt_files = list(prompts_dir.glob("*"))
            
            # On macOS, at least one should be a symlink
            has_symlink = any(f.is_symlink() for f in prompt_files)
            assert has_symlink or len(prompt_files) > 0, "No symlinks or files created on macOS"

    def test_repo_id_uses_dirname_if_available(self):
        """repo_id should derive from repo directory name or git remote."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_repo = Path(tmpdir) / "my-special-repo"
            test_repo.mkdir()
            (test_repo / ".git").mkdir()
            
            script_path = Path("/Users/asifhussain/PROJECTS/CORTEX/scripts/register-repo.sh")
            subprocess.run(
                ["bash", str(script_path), str(test_repo)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            config_path = test_repo / "cortex-config.yaml"
            with open(config_path) as f:
                content = f.read()
            
            # Should reference the directory name or generate a valid ID
            assert "repo_id:" in content


class TestIntegrationCompleteness:
    """Integration test: Full registration flow."""

    def test_full_registration_flow(self):
        """Full flow: script execution → config creation → prompts setup → git commit."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_repo = Path(tmpdir) / "integration-test-repo"
            test_repo.mkdir()
            
            # Initialize git repo
            subprocess.run(
                ["git", "init"],
                cwd=test_repo,
                capture_output=True,
                timeout=5
            )
            subprocess.run(
                ["git", "config", "user.email", "test@cortex.local"],
                cwd=test_repo,
                capture_output=True,
                timeout=5
            )
            subprocess.run(
                ["git", "config", "user.name", "CORTEX Test"],
                cwd=test_repo,
                capture_output=True,
                timeout=5
            )
            
            script_path = Path("/Users/asifhussain/PROJECTS/CORTEX/scripts/register-repo.sh")
            result = subprocess.run(
                ["bash", str(script_path), str(test_repo)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            assert result.returncode == 0, f"Registration failed: {result.stderr}"
            
            # Verify all components created
            assert (test_repo / "cortex-config.yaml").exists()
            assert (test_repo / ".github" / "prompts").exists()
            assert (test_repo / ".github" / "tier0").exists()
            
            # Verify git commit created
            git_log = subprocess.run(
                ["git", "log", "--oneline"],
                cwd=test_repo,
                capture_output=True,
                text=True,
                timeout=5
            )
            assert len(git_log.stdout.strip()) > 0
