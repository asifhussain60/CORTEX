"""
Architect Prompt Integration for CORTEX Upgrades.

Integrates upgrade detection and changelog generation into
the cortex-architect.prompt.md PRE-FLIGHT mode.

Phase: 40 Stage 4
Author: Asif Hussain
Date: 2026-02-07
"""

import logging
from typing import Any, Dict, Optional

from cortex.orchestrators.support.changelog_formatter import (
    ChangelogFormatter,
)
from cortex.orchestrators.support.upgrade_diff_analyzer import (
    DiffResult,
    UpgradeDiffAnalyzer,
)

logger = logging.getLogger(__name__)


class ArchitectPromptUpgradeHandler:
    """Handles upgrade detection and changelog for architect prompt."""

    def __init__(
        self,
        analyzer: Optional[UpgradeDiffAnalyzer] = None,
        formatter: Optional[ChangelogFormatter] = None
    ):
        """
        Initialize ArchitectPromptUpgradeHandler.

        Args:
            analyzer: UpgradeDiffAnalyzer instance (or creates new)
            formatter: ChangelogFormatter instance (or creates new)
        """
        self.analyzer = analyzer or UpgradeDiffAnalyzer()
        self.formatter = formatter or ChangelogFormatter()

    def handle_preflight_check(self) -> Dict[str, Any]:
        """
        Handle PRE-FLIGHT mode upgrade check.

        Called during cortex-architect.prompt.md PRE-FLIGHT mode to:
        1. Check if CORTEX was upgraded
        2. If upgraded, generate and display changelog
        3. Return results for display

        Returns:
            Dict with upgrade_detected and optional changelog
        """
        try:
            # Check for upgrade
            upgrade_detected = self.check_for_upgrade()

            result = {
                'upgrade_detected': upgrade_detected,
                'changelog': None
            }

            # If upgraded, generate changelog
            if upgrade_detected:
                try:
                    changelog = self.get_upgrade_changelog()
                    result['changelog'] = changelog
                except Exception as e:
                    logger.warning(f"Failed to generate changelog: {e}")
                    # Don't fail PRE-FLIGHT, just skip changelog
                    result['changelog'] = None

            return result

        except Exception as e:
            logger.error(f"PRE-FLIGHT upgrade check failed: {e}")
            return {
                'upgrade_detected': False,
                'changelog': None,
                'error': str(e)
            }

    def check_for_upgrade(self) -> bool:
        """
        Check if CORTEX prompt was upgraded.

        Analyzes git history to detect if cortex-architect.prompt.md
        or related files were updated in recent commits.

        Returns:
            True if upgrade detected, False otherwise
        """
        try:
            # Analyze recent changes
            diff_result = self.analyzer.analyze_upgrade()

            # Check if any changes detected
            has_changes = diff_result.total_changes > 0

            return has_changes

        except Exception as e:
            logger.error(f"Upgrade detection failed: {e}")
            return False

    def get_upgrade_changelog(self) -> str:
        """
        Generate changelog for architect prompt upgrade.

        Returns:
            Formatted changelog string
        """
        try:
            # Analyze upgrade changes
            diff_result = self.analyzer.analyze_upgrade()

            # Format for architect prompt display
            changelog = self.format_for_architect(diff_result)

            return changelog

        except Exception as e:
            logger.error(f"Changelog generation failed: {e}")
            raise

    def format_for_architect(self, diff_result: DiffResult) -> str:
        """
        Format diff result for architect prompt display.

        Creates a clean, informative changelog suitable for
        display in cortex-architect.prompt.md PRE-FLIGHT mode.

        Args:
            diff_result: Analyzed diff result

        Returns:
            Formatted changelog with version info and features
        """
        try:
            # Use standard formatter
            changelog = self.formatter.format(diff_result)

            # Add PRE-FLIGHT specific header if not already present
            if "Prompt Upgrade" not in changelog:
                header = "\n### 📋 Prompt Upgrade: What's New\n\n"
                changelog = header + changelog

            return changelog

        except Exception as e:
            logger.error(f"Architect formatting failed: {e}")
            # Return minimal changelog
            return f"CORTEX upgraded: v{diff_result.old_version} → v{diff_result.new_version}"
