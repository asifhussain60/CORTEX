"""
Unit tests for Environment Setup Integration.

Tests for Phase 40 Stage 3:
- AC-PHASE40-011: Integration with /check-env command (3 tests)
- AC-PHASE40-012: Upgrade detection flow (3 tests)
- AC-PHASE40-013: Changelog display in environment check (2 tests)

Total: 8 tests

Author: Asif Hussain
Date: 2026-02-07
Phase: 40
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from cortex.orchestrators.support.upgrade_diff_analyzer import (
    UpgradeDiffAnalyzer,
    DiffResult,
    PromptChange,
)
from cortex.orchestrators.support.changelog_formatter import (
    ChangelogFormatter,
)
from cortex.orchestrators.support.environment_upgrade_integration import (
    EnvironmentUpgradeChecker,
    UpgradeStatus,
)


# AC_START: AC-PHASE40-011
# Description: Integration with /check-env command
# Author: Asif Hussain
# Date: 2026-02-07


@pytest.fixture
def upgrade_checker():
    """Create EnvironmentUpgradeChecker instance."""
    return EnvironmentUpgradeChecker()


@pytest.fixture
def mock_repo_path(tmp_path):
    """Create temporary repo path."""
    return tmp_path / "cortex"


class TestCheckEnvIntegration:
    """Test integration with /check-env command."""

    def test_check_env_includes_upgrade_detection(self, upgrade_checker, mock_repo_path):
        """Verify /check-env runs upgrade detection."""
        with patch.object(upgrade_checker, 'detect_upgrade') as mock_detect:
            mock_detect.return_value = UpgradeStatus.NO_UPGRADE
            
            result = upgrade_checker.check_environment(mock_repo_path)
            
            assert mock_detect.called
            assert 'upgrade_status' in result

    def test_check_env_shows_changelog_when_upgraded(self, upgrade_checker, mock_repo_path):
        """Verify /check-env displays changelog after upgrade."""
        with patch.object(upgrade_checker, 'detect_upgrade') as mock_detect, \
             patch.object(upgrade_checker, 'get_changelog') as mock_changelog:
            
            mock_detect.return_value = UpgradeStatus.UPGRADED
            mock_changelog.return_value = "## Changelog\n- Feature 1"
            
            result = upgrade_checker.check_environment(mock_repo_path)
            
            assert result['upgrade_status'] == UpgradeStatus.UPGRADED
            assert result['changelog'] is not None
            assert 'Feature 1' in result['changelog']

    def test_check_env_skips_changelog_when_no_upgrade(self, upgrade_checker, mock_repo_path):
        """Verify /check-env skips changelog when no upgrade."""
        with patch.object(upgrade_checker, 'detect_upgrade') as mock_detect:
            mock_detect.return_value = UpgradeStatus.NO_UPGRADE
            
            result = upgrade_checker.check_environment(mock_repo_path)
            
            assert result['upgrade_status'] == UpgradeStatus.NO_UPGRADE
            assert result.get('changelog') is None


# AC_COMPLETE: AC-PHASE40-011 ✅


# AC_START: AC-PHASE40-012
# Description: Upgrade detection flow
# Author: Asif Hussain
# Date: 2026-02-07


class TestUpgradeDetection:
    """Test upgrade detection workflow."""

    def test_detects_upgrade_from_git_pull(self, upgrade_checker, mock_repo_path):
        """Verify upgrade detection after git pull."""
        # Use the helper method that parses git output
        git_output = "Updating abc123..def456\nFast-forward\n .github/prompts/CORTEX.prompt.md | 10 ++++++++++\n"
        
        status = upgrade_checker.detect_upgrade_from_output(git_output)
        
        assert status == UpgradeStatus.UPGRADED

    def test_detects_no_upgrade_when_already_up_to_date(self, upgrade_checker, mock_repo_path):
        """Verify no upgrade when already up to date."""
        # Use the helper method that parses git output
        git_output = "Already up to date."
        
        status = upgrade_checker.detect_upgrade_from_output(git_output)
        
        assert status == UpgradeStatus.NO_UPGRADE

    def test_handles_git_errors_gracefully(self, upgrade_checker, mock_repo_path):
        """Verify graceful handling of git errors."""
        # Use the helper method that parses git output
        git_output = "error: failed to fetch\nfatal: unable to access repository"
        
        status = upgrade_checker.detect_upgrade_from_output(git_output)
        
        assert status == UpgradeStatus.ERROR


# AC_COMPLETE: AC-PHASE40-012 ✅


# AC_START: AC-PHASE40-013
# Description: Changelog display in environment check
# Author: Asif Hussain
# Date: 2026-02-07


class TestChangelogDisplay:
    """Test changelog display in environment check."""

    def test_formats_changelog_for_display(self, upgrade_checker):
        """Verify changelog is properly formatted for display."""
        diff_result = DiffResult(
            prompt_changes=[
                PromptChange("new_mode", "QUERY", "Multi-purpose query", "high"),
            ],
            old_version="14.3",
            new_version="14.4"
        )
        
        with patch.object(upgrade_checker.analyzer, 'analyze_upgrade') as mock_analyze:
            mock_analyze.return_value = diff_result
            
            changelog = upgrade_checker.get_changelog()
            
            assert "QUERY" in changelog
            assert "14.3" in changelog
            assert "14.4" in changelog

    def test_changelog_includes_all_categories(self, upgrade_checker):
        """Verify changelog includes prompts, agents, orchestrators, MCP tools."""
        from cortex.orchestrators.support.upgrade_diff_analyzer import (
            AgentChange,
            OrchestratorChange,
            MCPToolChange,
        )
        
        diff_result = DiffResult(
            prompt_changes=[PromptChange("new_mode", "Mode1", "Desc1")],
            agent_changes=[AgentChange("new_agent", "Agent1", "Desc1", "1.0")],
            orchestrator_changes=[OrchestratorChange("new_orchestrator", "Orch1", "Desc1", 90)],
            mcp_tool_changes=[MCPToolChange("tool1", "Desc1")],
            old_version="14.3",
            new_version="14.4"
        )
        
        with patch.object(upgrade_checker.analyzer, 'analyze_upgrade') as mock_analyze:
            mock_analyze.return_value = diff_result
            
            changelog = upgrade_checker.get_changelog()
            
            # Should have multiple categories
            assert "Mode1" in changelog
            assert "Agent1" in changelog
            assert "Orch1" in changelog
            assert "tool1" in changelog


# AC_COMPLETE: AC-PHASE40-013 ✅


# Integration test
def test_full_environment_check_workflow(upgrade_checker, mock_repo_path):
    """Integration test for complete environment check with upgrade."""
    with patch.object(upgrade_checker, 'detect_upgrade') as mock_detect, \
         patch.object(upgrade_checker.analyzer, 'analyze_upgrade') as mock_analyze:
        
        # Simulate upgrade detected
        mock_detect.return_value = UpgradeStatus.UPGRADED
        
        # Simulate changes detected
        mock_analyze.return_value = DiffResult(
            prompt_changes=[
                PromptChange("new_mode", "TEST", "Test mode", "high"),
            ],
            old_version="14.3",
            new_version="14.4"
        )
        
        result = upgrade_checker.check_environment(mock_repo_path)
        
        assert result['upgrade_status'] == UpgradeStatus.UPGRADED
        assert result['changelog'] is not None
        assert 'TEST' in result['changelog']
        assert '14.4' in result['changelog']
