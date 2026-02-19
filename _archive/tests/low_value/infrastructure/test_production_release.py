"""
Tests for ProductionReleaseManager - CI/CD production release on origin/main.

TDD Tests for generating production releases with fresh CORTEX.prompt.md
and copilot-instruction.md files.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import json
from datetime import datetime


class TestProductionReleaseVersioning:
    """Tests for semantic versioning in production releases."""

    def test_get_current_version_from_pyproject(self, tmp_path):
        """Should read current version from pyproject.toml."""
        from cortex.ci_cd.production_release import ProductionReleaseManager
        
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nversion = "7.2.1"')
        
        manager = ProductionReleaseManager(tmp_path)
        version = manager.get_current_version()
        
        assert version == "7.2.1"

    def test_get_current_version_from_version_file(self, tmp_path):
        """Should read version from VERSION file if pyproject missing."""
        from cortex.ci_cd.production_release import ProductionReleaseManager
        
        version_file = tmp_path / "VERSION"
        version_file.write_text("7.3.0")
        
        manager = ProductionReleaseManager(tmp_path)
        version = manager.get_current_version()
        
        assert version == "7.3.0"

    def test_bump_patch_version(self):
        """Should bump patch version correctly."""
        from cortex.ci_cd.production_release import ProductionReleaseManager
        
        manager = ProductionReleaseManager(Path("."))
        new_version = manager.bump_version("7.2.1", "patch")
        
        assert new_version == "7.2.2"

    def test_bump_minor_version(self):
        """Should bump minor version and reset patch."""
        from cortex.ci_cd.production_release import ProductionReleaseManager
        
        manager = ProductionReleaseManager(Path("."))
        new_version = manager.bump_version("7.2.5", "minor")
        
        assert new_version == "7.3.0"

    def test_bump_major_version(self):
        """Should bump major version and reset minor/patch."""
        from cortex.ci_cd.production_release import ProductionReleaseManager
        
        manager = ProductionReleaseManager(Path("."))
        new_version = manager.bump_version("7.2.5", "major")
        
        assert new_version == "8.0.0"


class TestProductionReleaseInstructionRegeneration:
    """Tests for regenerating CORTEX instruction files."""

    def test_regenerate_cortex_prompt_md(self, tmp_path):
        """Should regenerate CORTEX.prompt.md with fresh content."""
        from cortex.ci_cd.production_release import ProductionReleaseManager
        
        # Create old prompt file
        prompts_dir = tmp_path / ".github" / "prompts"
        prompts_dir.mkdir(parents=True)
        old_prompt = prompts_dir / "CORTEX.prompt.md"
        old_prompt.write_text("# Old CORTEX v6.0\nOutdated content")
        
        manager = ProductionReleaseManager(tmp_path)
        result = manager.regenerate_cortex_prompt(version="7.0.0")
        
        assert result["success"] is True
        
        new_content = old_prompt.read_text()
        assert "7.0.0" in new_content
        assert "Outdated content" not in new_content

    def test_regenerate_copilot_instruction_md(self, tmp_path):
        """Should regenerate copilot-instruction.md with fresh content."""
        from cortex.ci_cd.production_release import ProductionReleaseManager
        
        # Create old instruction file
        github_dir = tmp_path / ".github"
        github_dir.mkdir(parents=True)
        old_instruction = github_dir / "copilot-instruction.md"
        old_instruction.write_text("# Old Instructions\nOutdated stuff")
        
        manager = ProductionReleaseManager(tmp_path)
        result = manager.regenerate_copilot_instructions(version="7.0.0")
        
        assert result["success"] is True
        
        new_content = old_instruction.read_text()
        assert "CORTEX" in new_content
        assert "7.0.0" in new_content

    def test_delete_old_files_before_regeneration(self, tmp_path):
        """Should delete old files before regenerating."""
        from cortex.ci_cd.production_release import ProductionReleaseManager
        
        # Create old files
        github_dir = tmp_path / ".github"
        prompts_dir = github_dir / "prompts"
        prompts_dir.mkdir(parents=True)
        
        old_prompt = prompts_dir / "CORTEX.prompt.md"
        old_prompt.write_text("OLD CONTENT MARKER")
        
        manager = ProductionReleaseManager(tmp_path)
        result = manager.regenerate_instruction_files(version="7.1.0", delete_first=True)
        
        assert result["deleted_files"] >= 1
        
        # Old content should be gone
        new_content = old_prompt.read_text()
        assert "OLD CONTENT MARKER" not in new_content


class TestProductionReleaseGitOperations:
    """Tests for Git operations in production releases."""

    def test_detect_main_branch(self, tmp_path):
        """Should detect if on main/master branch."""
        from cortex.ci_cd.production_release import ProductionReleaseManager
        
        manager = ProductionReleaseManager(tmp_path)
        
        # Mock git command
        with patch.object(manager, '_run_git_command') as mock_git:
            mock_git.return_value = "main"
            
            is_main = manager.is_main_branch()
            
            assert is_main is True

    def test_create_release_tag(self, tmp_path):
        """Should create release tag with version."""
        from cortex.ci_cd.production_release import ProductionReleaseManager
        
        manager = ProductionReleaseManager(tmp_path)
        
        with patch.object(manager, '_run_git_command') as mock_git:
            mock_git.return_value = ""
            
            result = manager.create_release_tag("v7.1.0", "Release 7.1.0")
            
            assert result["success"] is True
            mock_git.assert_called()

    def test_generate_changelog_entry(self, tmp_path):
        """Should generate changelog entry for release."""
        from cortex.ci_cd.production_release import ProductionReleaseManager
        
        manager = ProductionReleaseManager(tmp_path)
        
        changes = [
            "Added CopilotMerger for multi-repo governance",
            "Fixed unicode encoding issues",
            "Improved test coverage"
        ]
        
        changelog = manager.generate_changelog_entry("7.1.0", changes)
        
        assert "7.1.0" in changelog
        assert "CopilotMerger" in changelog
        assert datetime.now().strftime("%Y-%m-%d") in changelog


class TestProductionReleaseWorkflow:
    """Tests for the complete release workflow."""

    def test_full_release_workflow(self, tmp_path):
        """Should execute complete release workflow."""
        from cortex.ci_cd.production_release import ProductionReleaseManager
        
        # Setup project structure
        github_dir = tmp_path / ".github"
        prompts_dir = github_dir / "prompts"
        prompts_dir.mkdir(parents=True)
        
        (tmp_path / "VERSION").write_text("7.0.0")
        (prompts_dir / "CORTEX.prompt.md").write_text("# Old")
        (github_dir / "copilot-instruction.md").write_text("# Old")
        
        manager = ProductionReleaseManager(tmp_path)
        
        with patch.object(manager, '_run_git_command') as mock_git:
            mock_git.return_value = "main"
            
            result = manager.create_release(
                bump_type="patch",
                changes=["Test change"]
            )
            
            assert result["success"] is True
            assert result["new_version"] == "7.0.1"
            assert result["files_regenerated"] >= 2

    def test_release_blocked_on_non_main_branch(self, tmp_path):
        """Should block release on non-main branch."""
        from cortex.ci_cd.production_release import ProductionReleaseManager
        
        manager = ProductionReleaseManager(tmp_path)
        
        with patch.object(manager, '_run_git_command') as mock_git:
            mock_git.return_value = "feature/test"
            
            result = manager.create_release(bump_type="patch")
            
            assert result["success"] is False
            assert "main" in result["error"].lower()

    def test_release_with_custom_version(self, tmp_path):
        """Should allow custom version override."""
        from cortex.ci_cd.production_release import ProductionReleaseManager
        
        github_dir = tmp_path / ".github"
        github_dir.mkdir(parents=True)
        (tmp_path / "VERSION").write_text("7.0.0")
        
        manager = ProductionReleaseManager(tmp_path)
        
        with patch.object(manager, '_run_git_command') as mock_git:
            mock_git.return_value = "main"
            
            result = manager.create_release(custom_version="8.0.0-beta.1")
            
            assert result["success"] is True
            assert result["new_version"] == "8.0.0-beta.1"


class TestProductionReleaseValidation:
    """Tests for pre-release validation."""

    def test_validate_tests_pass(self, tmp_path):
        """Should validate all tests pass before release."""
        from cortex.ci_cd.production_release import ProductionReleaseManager
        
        manager = ProductionReleaseManager(tmp_path)
        
        with patch.object(manager, '_run_pytest') as mock_pytest:
            mock_pytest.return_value = {"passed": 100, "failed": 0}
            
            result = manager.validate_tests()
            
            assert result["valid"] is True
            assert result["passed"] == 100

    def test_block_release_if_tests_fail(self, tmp_path):
        """Should block release if tests fail."""
        from cortex.ci_cd.production_release import ProductionReleaseManager
        
        manager = ProductionReleaseManager(tmp_path)
        
        with patch.object(manager, '_run_pytest') as mock_pytest:
            mock_pytest.return_value = {"passed": 95, "failed": 5}
            
            result = manager.validate_tests()
            
            assert result["valid"] is False

    def test_validate_no_uncommitted_changes(self, tmp_path):
        """Should validate no uncommitted changes exist."""
        from cortex.ci_cd.production_release import ProductionReleaseManager
        
        manager = ProductionReleaseManager(tmp_path)
        
        with patch.object(manager, '_run_git_command') as mock_git:
            mock_git.return_value = ""  # Clean working directory
            
            result = manager.validate_clean_working_directory()
            
            assert result["clean"] is True


class TestProductionReleaseGitHubWorkflow:
    """Tests for GitHub Actions workflow generation."""

    def test_generate_release_workflow_yaml(self, tmp_path):
        """Should generate GitHub Actions release workflow."""
        from cortex.ci_cd.production_release import ProductionReleaseManager
        
        manager = ProductionReleaseManager(tmp_path)
        workflow = manager.generate_release_workflow()
        
        assert "name:" in workflow
        assert "on:" in workflow
        assert "push:" in workflow
        assert "main" in workflow
        assert "release" in workflow.lower()

    def test_workflow_includes_instruction_regeneration(self, tmp_path):
        """Should include instruction file regeneration step."""
        from cortex.ci_cd.production_release import ProductionReleaseManager
        
        manager = ProductionReleaseManager(tmp_path)
        workflow = manager.generate_release_workflow()
        
        assert "CORTEX.prompt.md" in workflow or "regenerate" in workflow.lower()

    def test_save_workflow_to_github_folder(self, tmp_path):
        """Should save workflow to .github/workflows."""
        from cortex.ci_cd.production_release import ProductionReleaseManager
        
        workflows_dir = tmp_path / ".github" / "workflows"
        workflows_dir.mkdir(parents=True)
        
        manager = ProductionReleaseManager(tmp_path)
        result = manager.save_release_workflow()
        
        assert result["success"] is True
        assert (workflows_dir / "release.yml").exists()


class TestProductionReleaseAuditIntegration:
    """Tests for audit trail integration."""

    def test_log_release_to_audit(self, tmp_path):
        """Should log release to audit trail."""
        from cortex.ci_cd.production_release import ProductionReleaseManager
        
        manager = ProductionReleaseManager(tmp_path, audit_enabled=True)
        
        with patch.object(manager, '_audit') as mock_audit:
            mock_audit.log_operation = MagicMock()
            
            manager._log_release_audit("7.1.0", ["change1"])
            
            mock_audit.log_operation.assert_called_once()

    def test_release_includes_ac_id(self, tmp_path):
        """Should include AC-ID in release metadata."""
        from cortex.ci_cd.production_release import ProductionReleaseManager
        
        manager = ProductionReleaseManager(tmp_path)
        
        metadata = manager.generate_release_metadata("7.1.0", ["change"])
        
        assert "ac_id" in metadata
        assert "AC-" in metadata["ac_id"]
