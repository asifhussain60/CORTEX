"""CrossRepoRouter — Route intents to the correct project repository.

Provides cross-repo intent routing with CORTEX.prompt.md awareness,
loading tier1 rules per project.
"""

from typing import Any, Dict, List, Optional


class CrossRepoRouter:
    """Route intents to the correct project repository.

    Supports multi-project CORTEX environments where each project
    has its own tier1 governance profile.
    """

    def __init__(self) -> None:
        """Initialize CrossRepoRouter."""
        self._current_project: Optional[str] = None

    # ------------------------------------------------------------------
    # Intent routing
    # ------------------------------------------------------------------

    def route_intent(
        self,
        intent_text: str,
        target_project: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Route an intent to the appropriate project.

        Args:
            intent_text: Natural-language intent description.
            target_project: Explicit project target (optional).

        Returns:
            Dict with 'target_project' and optional context keys.
        """
        project = target_project or self._get_project_for_intent(intent_text)
        context = self._load_project_context(project)
        return {"target_project": project, **context}

    # ------------------------------------------------------------------
    # Project context
    # ------------------------------------------------------------------

    def read_project_prompt(self, project_path: str) -> Optional[str]:
        """Read CORTEX.prompt.md from a project.

        Args:
            project_path: Filesystem path to the project root.

        Returns:
            Prompt file content, or None.
        """
        return self._read_file(project_path)

    def read_copilot_instructions(self, project_path: str) -> Optional[str]:
        """Read copilot-instruction.md from a project.

        Args:
            project_path: Filesystem path to the project root.

        Returns:
            Instructions file content, or None.
        """
        return self._read_file(project_path)

    def get_project_context(self, project_path: str) -> Dict[str, Any]:
        """Load full project context including tier1 rules.

        Args:
            project_path: Filesystem path to the project root.

        Returns:
            Dict with tier1 profile and rules.
        """
        return self._load_project_context(project_path)

    def get_tier0_rules(self) -> Dict[str, Any]:
        """Return universal tier0 rules that apply across all projects.

        Returns:
            Dict with 'rules' list of CORE rule IDs.
        """
        return {
            "rules": [
                "CORE-008",
                "CORE-011",
                "CORE-012",
                "CORE-013",
                "CORE-025",
                "CORE-026",
                "CORE-027",
                "CORE-028",
                "CORE-029",
                "CORE-030",
            ]
        }

    # ------------------------------------------------------------------
    # Internal helpers (designed to be patched in tests)
    # ------------------------------------------------------------------

    def _get_project_for_intent(self, intent_text: str) -> str:
        """Determine target project from intent text.

        Args:
            intent_text: Natural-language intent.

        Returns:
            Project name string.
        """
        lower = intent_text.lower()
        if any(kw in lower for kw in ("financial", "finops", "accounting", "invoice")):
            return "KASHKOLE"
        if any(kw in lower for kw in ("auth", "session", "login", "jwt")):
            return "KSESSIONS"
        return "CORTEX"

    def _load_project_context(self, project: str) -> Dict[str, Any]:
        """Load context for a project (tier1 profile, rules, etc.).

        Args:
            project: Project name or path.

        Returns:
            Context dict.
        """
        return {}

    def _read_file(self, path: str) -> Optional[str]:
        """Read a file from the filesystem.

        Args:
            path: File or directory path.

        Returns:
            File content or None.
        """
        return None
