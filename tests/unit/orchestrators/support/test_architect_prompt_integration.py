"""
Unit tests for Architect Prompt Integration.

Tests for Phase 40 Stage 4:
- AC-PHASE40-014: PRE-FLIGHT mode auto-upgrade with changelog (2 tests)
- AC-PHASE40-015: Changelog display in architect prompt (2 tests)

Total: 4 tests

Author: Asif Hussain
Date: 2026-02-07
Phase: 40
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from cortex.orchestrators.support.upgrade_diff_analyzer import (
    DiffResult,
    PromptChange,
    AgentChange,
)
from cortex.orchestrators.support.changelog_formatter import (
    ChangelogFormatter,
)
from cortex.orchestrators.support.architect_prompt_integration import (
    ArchitectPromptUpgradeHandler,
)


# AC_START: AC-PHASE40-014
# Description: PRE-FLIGHT mode auto-upgrade with changelog
# Author: Asif Hussain
# Date: 2026-02-07


@pytest.fixture
def prompt_handler():
    """Create ArchitectPromptUpgradeHandler instance."""
    return ArchitectPromptUpgradeHandler()


@pytest.fixture
def sample_diff_result():
    """Sample diff result with changes."""
    return DiffResult(
        prompt_changes=[
            PromptChange("new_mode", "QUERY", "Multi-purpose query", "high"),
            PromptChange("new_command", "/debug", "Full debug cycle", "medium"),
        ],
        agent_changes=[
            AgentChange("new_agent", "Debug Agent", "Smart debugging", "1.0"),
        ],
        old_version="14.3",
        new_version="14.4"
    )


class TestPreFlightAutoUpgrade:
    """Test PRE-FLIGHT mode auto-upgrade."""

    def test_detects_prompt_upgrade_in_preflight(self, prompt_handler):
        """Verify PRE-FLIGHT detects prompt upgrades."""
        with patch.object(prompt_handler, 'check_for_upgrade') as mock_check:
            mock_check.return_value = True
            
            result = prompt_handler.handle_preflight_check()
            
            assert result['upgrade_detected'] is True
            assert mock_check.called

    def test_displays_changelog_during_preflight(self, prompt_handler, sample_diff_result):
        """Verify PRE-FLIGHT shows changelog when upgrade detected."""
        with patch.object(prompt_handler, 'check_for_upgrade') as mock_check, \
             patch.object(prompt_handler, 'get_upgrade_changelog') as mock_changelog:
            
            mock_check.return_value = True
            mock_changelog.return_value = "## What's New\n- QUERY Mode\n- /debug command"
            
            result = prompt_handler.handle_preflight_check()
            
            assert result['upgrade_detected'] is True
            assert result['changelog'] is not None
            assert "QUERY Mode" in result['changelog']


# AC_COMPLETE: AC-PHASE40-014 ✅


# AC_START: AC-PHASE40-015
# Description: Changelog display in architect prompt
# Author: Asif Hussain
# Date: 2026-02-07


class TestArchitectPromptChangelogDisplay:
    """Test changelog display in architect prompt."""

    def test_formats_changelog_for_architect_prompt(self, prompt_handler, sample_diff_result):
        """Verify changelog is formatted for architect prompt display."""
        with patch.object(prompt_handler.formatter, 'format') as mock_format:
            mock_format.return_value = "## 🎉 CORTEX Upgraded\n| Feature | Desc |"
            
            changelog = prompt_handler.format_for_architect(sample_diff_result)
            
            assert "CORTEX Upgraded" in changelog
            assert mock_format.called

    def test_includes_version_upgrade_notice(self, prompt_handler, sample_diff_result):
        """Verify changelog includes version upgrade notice."""
        changelog = prompt_handler.format_for_architect(sample_diff_result)
        
        assert "14.3" in changelog
        assert "14.4" in changelog
        # Should show version progression
        assert "→" in changelog or "to" in changelog.lower()


# AC_COMPLETE: AC-PHASE40-015 ✅


# Integration tests
def test_full_preflight_upgrade_workflow(prompt_handler, sample_diff_result):
    """Integration test for complete PRE-FLIGHT upgrade workflow."""
    with patch.object(prompt_handler, 'check_for_upgrade') as mock_check, \
         patch.object(prompt_handler.analyzer, 'analyze_upgrade') as mock_analyze:
        
        mock_check.return_value = True
        mock_analyze.return_value = sample_diff_result
        
        result = prompt_handler.handle_preflight_check()
        
        assert result['upgrade_detected'] is True
        assert result['changelog'] is not None
        assert 'QUERY' in result['changelog']
        assert 'Debug Agent' in result['changelog']
        assert '14.4' in result['changelog']


def test_no_changelog_when_no_upgrade(prompt_handler):
    """Verify no changelog shown when no upgrade detected."""
    with patch.object(prompt_handler, 'check_for_upgrade') as mock_check:
        mock_check.return_value = False
        
        result = prompt_handler.handle_preflight_check()
        
        assert result['upgrade_detected'] is False
        assert result.get('changelog') is None
