"""Context Switcher MCP Tool - PHASE-DEPLOYMENT-003-mcp-expansion.

Load tier1 rules per project.

Author: CORTEX Framework
"""

from pathlib import Path
from typing import Any, Dict, Optional


class ContextSwitcher:
    """MCP tool for switching project context.

    Loads tier1 rules specific to each project while preserving tier0.
    """

    def __init__(self):
        """Initialize context switcher."""
        self.current_project: Optional[str] = None
        self._tier0_rules: Dict[str, Any] = {}
        self._tier1_rules: Dict[str, Any] = {}

    def switch_context(self, project_path: str) -> Dict[str, Any]:
        """Switch to a different project context.

        Args:
            project_path: Path to project to switch to.

        Returns:
            New context with tier0 and tier1 rules.
        """
        self.current_project = project_path

        tier0 = self._get_tier0_rules()
        tier1 = self._load_tier1_rules(project_path)

        self._tier0_rules = tier0
        self._tier1_rules = tier1

        return {
            "project": project_path,
            "tier0_rules": tier0,
            "tier1_rules": tier1,
            "context_active": True,
        }

    def _get_tier0_rules(self) -> Dict[str, Any]:
        """Get immutable tier0 rules.

        Returns:
            Tier0 governance rules.
        """
        return {
            "rules": [
                "CORE-008",  # Test-first
                "CORE-011",  # Type hints
                "CORE-012",  # Docstrings
                "CORE-017",  # Strict enforcement
                "CORE-018",  # Audit logging
            ],
            "immutable": True,
        }

    def _load_tier1_rules(self, project_path: str) -> Dict[str, Any]:
        """Load tier1 rules for project.

        Args:
            project_path: Path to project.

        Returns:
            Project-specific tier1 rules.
        """
        # Try to load from project's tier1 directory
        tier1_path = Path(project_path) / "cortex_brain" / "tier1"

        if tier1_path.exists():
            # In real implementation, would parse YAML files
            return {
                "domain": self._detect_domain(project_path),
                "rules": [],
                "path": str(tier1_path),
            }

        return {
            "domain": "default",
            "rules": [],
            "path": None,
        }

    def _detect_domain(self, project_path: str) -> str:
        """Detect project domain from structure.

        Args:
            project_path: Path to project.

        Returns:
            Detected domain name.
        """
        path = Path(project_path)
        name = path.name.lower()

        if "web" in name:
            return "web"
        elif "api" in name:
            return "api"
        elif "ml" in name or "ai" in name:
            return "ml"
        elif "data" in name:
            return "data"
        else:
            return "general"

    def get_current_context(self) -> Dict[str, Any]:
        """Get current context information.

        Returns:
            Current context state.
        """
        return {
            "project": self.current_project,
            "tier0_rules": self._tier0_rules,
            "tier1_rules": self._tier1_rules,
        }


__all__ = ["ContextSwitcher"]
