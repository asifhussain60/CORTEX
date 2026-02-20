"""
CrossRepoRouter — routes intents to the correct multi-repo project.

Authority: CORE-035 (single canonical implementation)
AC-ID: AC-DEP-004-03
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional


_TIER0_RULES: Dict[str, List[str]] = {
    "rules": [
        "CORE-002", "CORE-008", "CORE-011", "CORE-012",
        "CORE-028", "CORE-035",
    ]
}

_INTENT_KEYWORDS: Dict[str, str] = {
    "financial": "KASHKOLE",
    "payment": "KASHKOLE",
    "transaction": "KASHKOLE",
    "finops": "KASHKOLE",
    "session": "KSESSIONS",
    "auth": "KSESSIONS",
    "login": "KSESSIONS",
    "token": "KSESSIONS",
}


class CrossRepoRouter:
    """Routes natural-language intents to the correct target project.

    Reads ``CORTEX.prompt.md`` and ``copilot-instructions.md`` from each
    project to enrich routing context.
    """

    def __init__(self) -> None:
        """Initialise the router."""
        self._project_cache: Dict[str, Any] = {}

    # ── Public API ───────────────────────────────────────────────────

    def route_intent(
        self,
        intent: str,
        target_project: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Route an intent string to the appropriate project.

        Args:
            intent: Natural-language intent description.
            target_project: Explicit target project override.

        Returns:
            Dict with at least ``target_project`` key.
        """
        if target_project is None:
            target_project = self._get_project_for_intent(intent)

        context = self._load_project_context(target_project)
        return {
            "target_project": target_project,
            "intent": intent,
            "tier1": context.get("tier1_profile"),
            "context": context,
        }

    def read_project_prompt(self, project_path: str) -> Optional[str]:
        """Read ``CORTEX.prompt.md`` from a project directory.

        Args:
            project_path: Absolute or relative path to the project root.

        Returns:
            File contents, or *None* if absent.
        """
        return self._read_file(str(Path(project_path) / "CORTEX.prompt.md"))

    def read_copilot_instructions(self, project_path: str) -> Optional[str]:
        """Read copilot instruction file from a project directory.

        Args:
            project_path: Path to the project root.

        Returns:
            File contents, or *None* if absent.
        """
        candidates = [
            Path(project_path) / ".github" / "copilot-instructions.md",
            Path(project_path) / ".github" / "copilot-instruction.md",
        ]
        for candidate in candidates:
            content = self._read_file(str(candidate))
            if content is not None:
                return content
        return None

    def get_project_context(self, project_path: str) -> Dict[str, Any]:
        """Load tier1 context for a project.

        Args:
            project_path: Path to the project root.

        Returns:
            Context dict with ``tier1_profile`` and ``rules``.
        """
        return self._load_project_context(project_path)

    def get_tier0_rules(self) -> Dict[str, List[str]]:
        """Return global tier-0 (CORE) rules.

        Returns:
            Dict with ``rules`` list containing CORE rule IDs.
        """
        return dict(_TIER0_RULES)

    # ── Internal helpers ─────────────────────────────────────────────

    def _get_project_for_intent(self, intent: str) -> str:
        """Resolve project name from intent text via keyword lookup.

        Args:
            intent: Natural-language intent string.

        Returns:
            Target project name (default: ``"CORTEX"``).
        """
        lower = intent.lower()
        for keyword, project in _INTENT_KEYWORDS.items():
            if keyword in lower:
                return project
        return "CORTEX"

    def _load_project_context(self, project_path: str) -> Dict[str, Any]:
        """Load project context from cache or derive defaults.

        Args:
            project_path: Project path or name.

        Returns:
            Context dict.
        """
        if project_path in self._project_cache:
            return self._project_cache[project_path]
        # Derive a sensible default
        name = Path(project_path).name.upper()
        context: Dict[str, Any] = {
            "project": name,
            "tier1_profile": "general",
            "rules": [],
        }
        self._project_cache[project_path] = context
        return context

    def _read_file(self, path: str) -> Optional[str]:
        """Read a file returning its text content or *None*.

        Args:
            path: Absolute or relative file path.

        Returns:
            File text or *None* if the file does not exist.
        """
        try:
            return Path(path).read_text(encoding="utf-8")
        except (FileNotFoundError, OSError):
            return None
