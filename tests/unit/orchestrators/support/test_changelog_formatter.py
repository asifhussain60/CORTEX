"""
Unit tests for Changelog Formatter.

Tests for Phase 40 Stage 2:
- AC-PHASE40-006: Tabular output for ≤5 features (4 tests)
- AC-PHASE40-007: Bullet output for >5 features (4 tests)
- AC-PHASE40-008: Icon assignment by category (3 tests)
- AC-PHASE40-009: Impact scoring (4 tests)
- AC-PHASE40-010: Truncation at 20 features (3 tests)

Total: 18 tests

Author: Asif Hussain
Date: 2026-02-07
Phase: 40
"""

import pytest
from typing import List

from cortex.orchestrators.support.upgrade_diff_analyzer import (
    DiffResult,
    PromptChange,
    AgentChange,
    OrchestratorChange,
    MCPToolChange,
)
from cortex.orchestrators.support.changelog_formatter import (
    ChangelogFormatter,
    FormatStyle,
    ImpactLevel,
)


# AC_START: AC-PHASE40-006
# Description: Formatter generates tabular output (≤5 features)
# Author: Asif Hussain
# Date: 2026-02-07


@pytest.fixture
def formatter():
    """Create ChangelogFormatter instance."""
    return ChangelogFormatter()


@pytest.fixture
def small_diff_result():
    """Diff result with ≤5 changes."""
    return DiffResult(
        prompt_changes=[
            PromptChange("new_mode", "QUERY Mode", "Multi-purpose query", "high"),
            PromptChange("new_command", "/debug", "Full debug cycle", "medium"),
        ],
        agent_changes=[
            AgentChange("new_agent", "Debug Agent", "Smart debugging", "1.0"),
        ],
        orchestrator_changes=[
            OrchestratorChange("new_orchestrator", "DigestOrch", "DIGEST automation", 83),
        ],
        mcp_tool_changes=[
            MCPToolChange("cortex_digest", "Auto-analyze sessions"),
        ],
        old_version="14.3",
        new_version="14.4"
    )


class TestTabularOutput:
    """Test tabular output generation."""

    def test_generates_markdown_table_for_small_changes(self, formatter, small_diff_result):
        """Verify table format for ≤5 changes."""
        output = formatter.format(small_diff_result)
        
        assert "| Category | Feature | Description | Impact |" in output
        assert "|----------|---------|-------------|--------|" in output

    def test_table_includes_all_changes(self, formatter, small_diff_result):
        """Verify all changes appear in table."""
        output = formatter.format(small_diff_result)
        
        assert "QUERY Mode" in output
        assert "/debug" in output
        assert "Debug Agent" in output
        assert "DigestOrch" in output
        assert "cortex_digest" in output

    def test_auto_selects_table_format_for_5_or_fewer(self, formatter):
        """Verify automatic format selection."""
        result = DiffResult(prompt_changes=[
            PromptChange("new_mode", f"Mode{i}", f"Desc{i}") for i in range(5)
        ])
        
        format_style = formatter.select_format(result)
        assert format_style == FormatStyle.TABLE

    def test_table_format_is_well_formed(self, formatter, small_diff_result):
        """Verify table has correct structure."""
        output = formatter.format(small_diff_result)
        
        lines = output.split('\n')
        table_lines = [l for l in lines if l.startswith('|')]
        
        # Header + separator + at least 1 data row
        assert len(table_lines) >= 3
        # All rows should have 5 columns (4 separators)
        assert all(line.count('|') == 5 for line in table_lines)


# AC_COMPLETE: AC-PHASE40-006 ✅


# AC_START: AC-PHASE40-007
# Description: Formatter generates bullet output (>5 features)
# Author: Asif Hussain
# Date: 2026-02-07


@pytest.fixture
def large_diff_result():
    """Diff result with >5 changes."""
    return DiffResult(
        prompt_changes=[
            PromptChange("new_mode", f"Mode {i}", f"Description {i}", "high") 
            for i in range(3)
        ],
        agent_changes=[
            AgentChange("new_agent", f"Agent {i}", f"Agent desc {i}", "1.0") 
            for i in range(4)
        ],
        orchestrator_changes=[
            OrchestratorChange("new_orchestrator", "TestOrch", "Test", 90),
        ],
        old_version="14.3",
        new_version="14.4"
    )


class TestBulletOutput:
    """Test bullet list output generation."""

    def test_generates_bullet_list_for_large_changes(self, formatter, large_diff_result):
        """Verify bullet format for >5 changes."""
        output = formatter.format(large_diff_result)
        
        # Should have hierarchical bullets
        assert "**" in output  # Category headers
        assert "-" in output or "•" in output or "1." in output  # Bullets

    def test_bullet_list_groups_by_category(self, formatter, large_diff_result):
        """Verify grouping by category."""
        output = formatter.format(large_diff_result)
        
        assert "Prompts" in output or "Modes" in output
        assert "Agents" in output
        assert "Orchestrators" in output

    def test_auto_selects_bullet_format_for_more_than_5(self, formatter, large_diff_result):
        """Verify automatic format selection for >5 changes."""
        format_style = formatter.select_format(large_diff_result)
        assert format_style == FormatStyle.BULLET

    def test_bullet_format_includes_icons(self, formatter, large_diff_result):
        """Verify bullet format includes category icons."""
        output = formatter.format(large_diff_result)
        
        # Should have at least some emoji icons
        has_icons = any(char in output for char in ['🎯', '🚀', '🔧', '📊', '🤖', '⚙️'])
        assert has_icons


# AC_COMPLETE: AC-PHASE40-007 ✅


# AC_START: AC-PHASE40-008
# Description: Formatter assigns icons by category
# Author: Asif Hussain
# Date: 2026-02-07


class TestIconAssignment:
    """Test category icon assignment."""

    def test_assigns_icons_to_categories(self, formatter):
        """Verify each category gets an appropriate icon."""
        icons = formatter.get_category_icons()
        
        assert "prompt" in icons or "mode" in icons
        assert "agent" in icons
        assert "orchestrator" in icons
        assert "mcp_tool" in icons

    def test_icon_mapping_is_consistent(self, formatter):
        """Verify same category always gets same icon."""
        icon1 = formatter.get_icon_for_category("agent")
        icon2 = formatter.get_icon_for_category("agent")
        
        assert icon1 == icon2

    def test_formats_with_icons(self, formatter, small_diff_result):
        """Verify formatted output includes icons."""
        output = formatter.format(small_diff_result, style=FormatStyle.BULLET)
        
        # Should have emoji icons
        assert any(ord(char) > 127 for char in output)  # Unicode emoji check


# AC_COMPLETE: AC-PHASE40-008 ✅


# AC_START: AC-PHASE40-009
# Description: Formatter scores impact (Critical/Medium/Minor)
# Author: Asif Hussain
# Date: 2026-02-07


class TestImpactScoring:
    """Test impact level scoring and display."""

    def test_calculates_impact_from_change_type(self, formatter):
        """Verify impact calculation based on change type."""
        # New modes should be high impact
        mode_change = PromptChange("new_mode", "TEST", "Test")
        assert formatter.calculate_impact(mode_change) in [ImpactLevel.CRITICAL, ImpactLevel.HIGH]
        
        # Minor documentation changes should be low impact
        doc_change = PromptChange("new_section", "Docs", "Documentation")
        assert formatter.calculate_impact(doc_change) == ImpactLevel.MINOR

    def test_assigns_impact_icons(self, formatter):
        """Verify impact levels get visual indicators."""
        critical = formatter.get_impact_icon(ImpactLevel.CRITICAL)
        high = formatter.get_impact_icon(ImpactLevel.HIGH)
        medium = formatter.get_impact_icon(ImpactLevel.MEDIUM)
        minor = formatter.get_impact_icon(ImpactLevel.MINOR)
        
        assert critical in ['🔴', '❗', '⚠️']
        assert all(icon is not None for icon in [high, medium, minor])

    def test_formats_impact_in_table(self, formatter, small_diff_result):
        """Verify impact appears in table output."""
        output = formatter.format(small_diff_result, style=FormatStyle.TABLE)
        
        # Should have impact indicators
        assert any(indicator in output for indicator in ['🔴', '🟡', '🟢', '🔵'])

    def test_sorts_by_impact_level(self, formatter):
        """Verify changes are sorted by impact."""
        result = DiffResult(
            prompt_changes=[
                PromptChange("new_section", "Minor", "Low priority", "minor"),
                PromptChange("new_mode", "Critical", "High priority", "critical"),
                PromptChange("new_command", "Medium", "Mid priority", "medium"),
            ]
        )
        
        sorted_changes = formatter.sort_by_impact(result)
        
        # Critical should come first
        assert sorted_changes[0].impact in ["critical", "high"]


# AC_COMPLETE: AC-PHASE40-009 ✅


# AC_START: AC-PHASE40-010
# Description: Formatter truncates at 20 features
# Author: Asif Hussain
# Date: 2026-02-07


class TestTruncation:
    """Test feature truncation at 20 items."""

    def test_truncates_at_20_features(self, formatter):
        """Verify output truncates after 20 features."""
        result = DiffResult(
            prompt_changes=[
                PromptChange("new_mode", f"Feature {i}", f"Desc {i}") 
                for i in range(25)
            ]
        )
        
        output = formatter.format(result)
        
        # Should have truncation message
        assert "...and" in output or "more" in output.lower()

    def test_shows_remaining_count(self, formatter):
        """Verify truncation shows how many features remain."""
        result = DiffResult(
            prompt_changes=[
                PromptChange("new_mode", f"Feature {i}", f"Desc {i}") 
                for i in range(25)
            ]
        )
        
        output = formatter.format(result)
        
        # Should show "5 more" or similar
        assert "5" in output and "more" in output.lower()

    def test_no_truncation_for_20_or_fewer(self, formatter):
        """Verify no truncation for ≤20 features."""
        result = DiffResult(
            prompt_changes=[
                PromptChange("new_mode", f"Feature {i}", f"Desc {i}") 
                for i in range(20)
            ]
        )
        
        output = formatter.format(result)
        
        # Should NOT have truncation message
        assert "...and" not in output


# AC_COMPLETE: AC-PHASE40-010 ✅


# Integration test
def test_full_changelog_generation(formatter, small_diff_result):
    """Integration test for complete changelog generation."""
    output = formatter.format(small_diff_result)
    
    assert output is not None
    assert len(output) > 0
    assert "Feature" in output or "Changes" in output
    assert small_diff_result.new_version in output
