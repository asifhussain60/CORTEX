"""Cross-Repo Router - PHASE-DEPLOYMENT-004-multi-repo-gov.

Routes intents across repositories with CORTEX.prompt.md awareness.

Author: CORTEX Framework
"""

from pathlib import Path
from typing import Any, Dict, List, Optional


class CrossRepoRouter:
    """Routes intents across repositories.

    Reads project context (CORTEX.prompt.md, copilot-instruction.md)
    and routes intents to appropriate project with tier1 rules loaded.
    """

    # Intent keywords for project routing
    INTENT_KEYWORDS = {
        "KASHKOLE": ["financial", "payment", "billing", "invoice", "transaction", "finance"],
        "KSESSIONS": ["session", "auth", "login", "logout", "user", "authentication"],
        "CORTEX": ["governance", "orchestrate", "compliance", "audit", "rule"],
    }

    # Tier0 immutable rules
    TIER0_RULES = {
        "rules": ["CORE-008", "CORE-011", "CORE-012", "CORE-017", "CORE-018", "CORE-026"],
        "immutable": True,
    }

    def __init__(self, base_path: str = "D:\\PROJECTS"):
        """Initialize cross-repo router.

        Args:
            base_path: Base path containing projects.
        """
        self.base_path = base_path
        self._current_project: Optional[str] = None

    def route_intent(
        self,
        intent: str,
        target_project: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Route an intent to appropriate project.

        Args:
            intent: Intent text to route.
            target_project: Optional explicit target project.

        Returns:
            Routing result with target project and tier1 rules.
        """
        if target_project:
            project = target_project
        else:
            project = self._get_project_for_intent(intent)

        self._current_project = project

        # Load project context
        context = self._load_project_context(project)

        return {
            "target_project": project,
            "intent": intent,
            "tier1": context.get("tier1_profile"),
            "context": context,
        }

    def _get_project_for_intent(self, intent: str) -> str:
        """Determine target project from intent text.

        Args:
            intent: Intent text.

        Returns:
            Target project name.
        """
        intent_lower = intent.lower()

        for project, keywords in self.INTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in intent_lower:
                    return project

        # Default to CORTEX
        return "CORTEX"

    def _load_project_context(self, project: str) -> Dict[str, Any]:
        """Load context for a project.

        Args:
            project: Project name.

        Returns:
            Project context with tier1 profile.
        """
        project_path = f"{self.base_path}\\{project}"

        # Read project prompt if available
        prompt = self.read_project_prompt(project_path)
        instructions = self.read_copilot_instructions(project_path)

        # Determine tier1 profile
        tier1_profile = self._infer_tier1_profile(project, prompt)

        return {
            "project": project,
            "path": project_path,
            "tier1_profile": tier1_profile,
            "prompt": prompt,
            "instructions": instructions,
        }

    def _infer_tier1_profile(self, project: str, prompt: Optional[str]) -> str:
        """Infer tier1 profile from project.

        Args:
            project: Project name.
            prompt: Project prompt content.

        Returns:
            Tier1 profile name.
        """
        project_lower = project.lower()

        if "kashkole" in project_lower or "finance" in project_lower:
            return "finops"
        elif "ksessions" in project_lower or "session" in project_lower:
            return "auth"
        elif "cortex" in project_lower:
            return "devops"

        # Check prompt content
        if prompt:
            prompt_lower = prompt.lower()
            if "financial" in prompt_lower:
                return "finops"
            elif "authentication" in prompt_lower:
                return "auth"
            elif "machine learning" in prompt_lower or "ml" in prompt_lower:
                return "ml"

        return "general"

    def read_project_prompt(self, project_path: str) -> Optional[str]:
        """Read CORTEX.prompt.md from project.

        Args:
            project_path: Path to project.

        Returns:
            Prompt content or None.
        """
        prompt_paths = [
            Path(project_path) / ".github" / "prompts" / "CORTEX.prompt.md",
            Path(project_path) / ".github" / "CORTEX.prompt.md",
            Path(project_path) / "CORTEX.prompt.md",
        ]

        return self._read_file(prompt_paths)

    def read_copilot_instructions(self, project_path: str) -> Optional[str]:
        """Read copilot-instruction.md from project.

        Args:
            project_path: Path to project.

        Returns:
            Instructions content or None.
        """
        instruction_paths = [
            Path(project_path) / ".github" / "copilot-instruction.md",
            Path(project_path) / ".github" / "copilot-instructions.md",
            Path(project_path) / "copilot-instruction.md",
        ]

        return self._read_file(instruction_paths)

    def _read_file(self, paths: List[Path]) -> Optional[str]:
        """Read first existing file from path list.

        Args:
            paths: List of paths to try.

        Returns:
            File content or None.
        """
        for path in paths:
            if isinstance(path, str):
                path = Path(path)
            if path.exists():
                try:
                    return path.read_text()
                except Exception:
                    continue
        return None

    def get_project_context(self, project_path: str) -> Dict[str, Any]:
        """Get context for a project path.

        Args:
            project_path: Path to project.

        Returns:
            Project context dictionary.
        """
        project_name = Path(project_path).name
        return self._load_project_context(project_name)

    def get_tier0_rules(self) -> Dict[str, Any]:
        """Get immutable tier0 rules.

        Returns:
            Tier0 rules dictionary.
        """
        return self.TIER0_RULES.copy()

    def list_projects(self) -> List[Dict[str, Any]]:
        """List all discovered projects.

        Returns:
            List of project summaries.
        """
        projects = []

        try:
            base = Path(self.base_path)
            if base.exists():
                for path in base.iterdir():
                    if path.is_dir() and not path.name.startswith("."):
                        projects.append({
                            "name": path.name,
                            "path": str(path),
                            "tier1_profile": self._infer_tier1_profile(path.name, None),
                        })
        except Exception:
            pass

        return projects


__all__ = ["CrossRepoRouter"]
