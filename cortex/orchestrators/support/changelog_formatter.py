"""
Changelog Formatter for CORTEX Upgrades.

Formats DiffResult into user-friendly changelogs with:
- Tabular output (≤5 features)
- Bullet output (>5 features)
- Category icons
- Impact scoring
- Truncation at 20 features

Phase: 40 Stage 2
Author: Asif Hussain
Date: 2026-02-07
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Union

from cortex.orchestrators.support.upgrade_diff_analyzer import (
    AgentChange,
    DiffResult,
    MCPToolChange,
    OrchestratorChange,
    PromptChange,
)


class FormatStyle(Enum):
    """Output format style."""
    TABLE = "table"
    BULLET = "bullet"


class ImpactLevel(Enum):
    """Change impact levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    MINOR = "minor"


@dataclass
class FormattedChange:
    """Formatted change for display."""
    category: str
    feature: str
    description: str
    impact: ImpactLevel


class ChangelogFormatter:
    """Formats DiffResult into elegant changelogs."""

    # Category icons
    CATEGORY_ICONS = {
        "prompt": "🎯",
        "mode": "🎯",
        "command": "🚀",
        "agent": "🤖",
        "orchestrator": "⚙️",
        "mcp_tool": "🔧",
    }

    # Impact icons
    IMPACT_ICONS = {
        ImpactLevel.CRITICAL: "🔴",
        ImpactLevel.HIGH: "🟡",
        ImpactLevel.MEDIUM: "🟢",
        ImpactLevel.MINOR: "🔵",
    }

    # Impact calculation rules
    IMPACT_RULES = {
        "new_mode": ImpactLevel.CRITICAL,
        "new_command": ImpactLevel.HIGH,
        "new_agent": ImpactLevel.HIGH,
        "new_orchestrator": ImpactLevel.MEDIUM,
        "new_mcp_tool": ImpactLevel.MEDIUM,
        "new_section": ImpactLevel.MINOR,
    }

    def __init__(self, max_features: int = 20):
        """
        Initialize ChangelogFormatter.

        Args:
            max_features: Maximum features to display before truncation
        """
        self.max_features = max_features

    def format(
        self,
        diff_result: DiffResult,
        style: Optional[FormatStyle] = None
    ) -> str:
        """
        Format DiffResult into changelog.

        Args:
            diff_result: Analyzed diff result
            style: Output style (auto-selected if None)

        Returns:
            Formatted changelog string
        """
        # Auto-select format if not specified
        if style is None:
            style = self.select_format(diff_result)

        # Convert all changes to FormattedChange objects
        formatted_changes = self._convert_to_formatted_changes(diff_result)

        # Sort by impact
        sorted_changes = self.sort_by_impact_objects(formatted_changes)

        # Truncate if needed
        display_changes, remaining = self._truncate_features(sorted_changes)

        # Generate output
        if style == FormatStyle.TABLE:
            output = self._generate_table(display_changes, diff_result)
        else:
            output = self._generate_bullets(display_changes, diff_result)

        # Add truncation notice
        if remaining > 0:
            output += f"\n\n*...and {remaining} more features*"

        return output

    def select_format(self, diff_result: DiffResult) -> FormatStyle:
        """
        Auto-select format based on change count.

        Args:
            diff_result: Diff result to analyze

        Returns:
            Appropriate format style
        """
        total_changes = (
            len(diff_result.prompt_changes) +
            len(diff_result.agent_changes) +
            len(diff_result.orchestrator_changes) +
            len(diff_result.mcp_tool_changes)
        )

        return FormatStyle.TABLE if total_changes <= 5 else FormatStyle.BULLET

    def get_category_icons(self) -> Dict[str, str]:
        """Get category icon mapping."""
        return self.CATEGORY_ICONS.copy()

    def get_icon_for_category(self, category: str) -> str:
        """
        Get icon for category.

        Args:
            category: Category name

        Returns:
            Category icon
        """
        return self.CATEGORY_ICONS.get(category.lower(), "📊")

    def calculate_impact(
        self,
        change: Union[PromptChange, AgentChange, OrchestratorChange, MCPToolChange]
    ) -> ImpactLevel:
        """
        Calculate impact level for change.

        Args:
            change: Change object

        Returns:
            Impact level
        """
        # Use change type for impact calculation
        change_type = change.change_type

        # Prioritize rules-based impact by change type
        if change_type in self.IMPACT_RULES:
            return self.IMPACT_RULES[change_type]

        # Fall back to explicit impact if available (only PromptChange has this)
        if isinstance(change, PromptChange) and change.impact and change.impact != "medium":
            impact_map = {
                "critical": ImpactLevel.CRITICAL,
                "high": ImpactLevel.HIGH,
                "medium": ImpactLevel.MEDIUM,
                "minor": ImpactLevel.MINOR,
            }
            return impact_map.get(change.impact.lower(), ImpactLevel.MEDIUM)

        # Default to medium
        return ImpactLevel.MEDIUM

    def get_impact_icon(self, impact: ImpactLevel) -> str:
        """
        Get icon for impact level.

        Args:
            impact: Impact level

        Returns:
            Impact icon
        """
        return self.IMPACT_ICONS.get(impact, "⚪")

    def sort_by_impact(self, diff_result: DiffResult) -> List[Union[
        PromptChange, AgentChange, OrchestratorChange, MCPToolChange
    ]]:
        """
        Sort all changes by impact level.

        Args:
            diff_result: Diff result to sort

        Returns:
            Sorted list of all changes
        """
        all_changes = []
        all_changes.extend(diff_result.prompt_changes)
        all_changes.extend(diff_result.agent_changes)
        all_changes.extend(diff_result.orchestrator_changes)
        all_changes.extend(diff_result.mcp_tool_changes)

        # Sort by impact (critical first)
        impact_order = {
            ImpactLevel.CRITICAL: 0,
            ImpactLevel.HIGH: 1,
            ImpactLevel.MEDIUM: 2,
            ImpactLevel.MINOR: 3,
        }

        return sorted(
            all_changes,
            key=lambda c: impact_order.get(self.calculate_impact(c), 999)
        )

    def sort_by_impact_objects(self, changes: List[FormattedChange]) -> List[FormattedChange]:
        """Sort FormattedChange objects by impact."""
        impact_order = {
            ImpactLevel.CRITICAL: 0,
            ImpactLevel.HIGH: 1,
            ImpactLevel.MEDIUM: 2,
            ImpactLevel.MINOR: 3,
        }

        return sorted(changes, key=lambda c: impact_order.get(c.impact, 999))

    def _convert_to_formatted_changes(self, diff_result: DiffResult) -> List[FormattedChange]:
        """Convert DiffResult to FormattedChange objects."""
        formatted = []

        # Prompt changes
        for change in diff_result.prompt_changes:
            category = "Mode" if "mode" in change.change_type else "Command"
            formatted.append(FormattedChange(
                category=category,
                feature=change.name,
                description=change.description,
                impact=self.calculate_impact(change)
            ))

        # Agent changes
        for change in diff_result.agent_changes:
            formatted.append(FormattedChange(
                category="Agent",
                feature=change.name,
                description=change.description,
                impact=self.calculate_impact(change)
            ))

        # Orchestrator changes
        for change in diff_result.orchestrator_changes:
            formatted.append(FormattedChange(
                category="Orchestrator",
                feature=change.name,
                description=change.description,
                impact=self.calculate_impact(change)
            ))

        # MCP tool changes
        for change in diff_result.mcp_tool_changes:
            formatted.append(FormattedChange(
                category="MCP Tool",
                feature=change.name,  # MCPToolChange uses 'name', not 'tool_name'
                description=change.description,
                impact=self.calculate_impact(change)
            ))

        return formatted

    def _truncate_features(
        self,
        changes: List[FormattedChange]
    ) -> tuple[List[FormattedChange], int]:
        """
        Truncate features at max_features limit.

        Args:
            changes: List of formatted changes

        Returns:
            Tuple of (display_changes, remaining_count)
        """
        if len(changes) <= self.max_features:
            return changes, 0

        return changes[:self.max_features], len(changes) - self.max_features

    def _generate_table(
        self,
        changes: List[FormattedChange],
        diff_result: DiffResult
    ) -> str:
        """Generate tabular output."""
        lines = []

        # Header
        lines.append(f"## 🎉 CORTEX Upgraded: v{diff_result.old_version} → v{diff_result.new_version}\n")
        lines.append("| Category | Feature | Description | Impact |")
        lines.append("|----------|---------|-------------|--------|")

        # Rows
        for change in changes:
            category_icon = self.get_icon_for_category(change.category)
            impact_icon = self.get_impact_icon(change.impact)

            lines.append(
                f"| {category_icon} {change.category} | "
                f"`{change.feature}` | "
                f"{change.description} | "
                f"{impact_icon} |"
            )

        return "\n".join(lines)

    def _generate_bullets(
        self,
        changes: List[FormattedChange],
        diff_result: DiffResult
    ) -> str:
        """Generate bullet list output."""
        lines = []

        # Header
        lines.append(f"## 🎉 CORTEX Upgraded: v{diff_result.old_version} → v{diff_result.new_version}\n")

        # Group by category
        grouped: Dict[str, List[FormattedChange]] = {}
        for change in changes:
            if change.category not in grouped:
                grouped[change.category] = []
            grouped[change.category].append(change)

        # Output by category
        for category, category_changes in grouped.items():
            category_icon = self.get_icon_for_category(category)
            lines.append(f"### {category_icon} **{category}s**\n")

            for change in category_changes:
                impact_icon = self.get_impact_icon(change.impact)
                lines.append(
                    f"- {impact_icon} **`{change.feature}`**: {change.description}"
                )

            lines.append("")  # Blank line between categories

        return "\n".join(lines)
