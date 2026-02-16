"""ContextSwitcher — Switch governance context between projects.

Loads tier1 rules per project while preserving tier0 rules.
"""

from typing import Any, Dict, Optional


class ContextSwitcher:
    """Switch governance context between projects."""

    def __init__(self) -> None:
        """Initialize ContextSwitcher."""
        self.current_project: Optional[str] = None

    def switch_context(self, project_path: str) -> Dict[str, Any]:
        """Switch governance context to a project.

        Args:
            project_path: Path to the target project.

        Returns:
            Dict with 'tier1_rules' and 'tier0_rules'.
        """
        self.current_project = project_path
        tier1 = self._load_tier1_rules(project_path)
        tier0 = self._get_tier0_rules()
        return {
            "tier1_rules": tier1,
            "tier0_rules": tier0,
        }

    def _load_tier1_rules(self, project_path: str) -> Dict[str, Any]:
        """Load tier1 rules for a project.

        Args:
            project_path: Project path.

        Returns:
            Tier1 rules dict.
        """
        return {}

    def _get_tier0_rules(self) -> Dict[str, Any]:
        """Get universal tier0 rules.

        Returns:
            Tier0 rules dict.
        """
        return {"rules": ["CORE-008"]}
