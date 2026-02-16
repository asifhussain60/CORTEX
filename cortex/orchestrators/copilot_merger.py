"""CopilotMerger — CORTEX instructions merger.

Merges CORTEX intelligence with existing repository copilot instructions,
preserving user-defined sections while updating CORTEX-managed sections.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import re
import shutil
from datetime import datetime

import yaml


# Patterns that identify CORTEX-managed sections
_CORTEX_SECTION_PATTERNS = [
    "CORTEX",
    "TIER 0",
    "TIER0",
    "Governance",
    "Architecture",
    "MCP",
]


class CopilotMerger:
    """Merge CORTEX instructions with existing repo instructions.

    Args:
        audit_enabled: When True, log merge operations to SharedAuditTrail.
    """

    def __init__(self, audit_enabled: bool = False) -> None:
        """Initialize CopilotMerger.

        Args:
            audit_enabled: Enable audit trail logging.
        """
        self.audit_enabled = audit_enabled
        self._audit: Any = None
        if audit_enabled:
            try:
                from cortex.orchestrators.shared_audit_trail import SharedAuditTrail
                self._audit = SharedAuditTrail()
            except ImportError:
                pass

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def find_existing_instructions(self, repo_path: Path) -> Optional[Dict[str, Any]]:
        """Find existing copilot-instruction.md in a repository.

        Args:
            repo_path: Root path of the repository.

        Returns:
            Dict with 'path' and 'content' keys, or None.
        """
        candidates = [
            repo_path / ".github" / "copilot-instruction.md",
            repo_path / ".github" / "prompts" / "copilot-instruction.md",
            repo_path / ".github" / "copilot-instructions.md",
        ]
        for candidate in candidates:
            if candidate.exists():
                return {
                    "path": candidate,
                    "content": candidate.read_text(encoding="utf-8"),
                }
        return None

    def find_cortex_prompt(self, repo_path: Path) -> Optional[Dict[str, Any]]:
        """Find CORTEX.prompt.md in a repository.

        Args:
            repo_path: Root path of the repository.

        Returns:
            Dict with 'path' and 'content' keys, or None.
        """
        candidates = [
            repo_path / ".github" / "prompts" / "CORTEX.prompt.md",
            repo_path / ".github" / "CORTEX.prompt.md",
        ]
        for candidate in candidates:
            if candidate.exists():
                return {
                    "path": candidate,
                    "content": candidate.read_text(encoding="utf-8"),
                }
        return None

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------

    def parse_sections(self, content: str) -> Dict[str, str]:
        """Parse markdown content into named sections.

        Args:
            content: Markdown text.

        Returns:
            Dict mapping section title → section body.
        """
        sections: Dict[str, str] = {}
        current_title: Optional[str] = None
        current_body: List[str] = []

        for line in content.splitlines():
            heading_match = re.match(r"^##\s+(.+)", line)
            if heading_match:
                if current_title is not None:
                    sections[current_title] = "\n".join(current_body).strip()
                current_title = heading_match.group(1).strip()
                current_body = []
            else:
                current_body.append(line)

        if current_title is not None:
            sections[current_title] = "\n".join(current_body).strip()
        return sections

    def extract_project_rules(self, content: str) -> List[str]:
        """Extract project-specific rules from instructions.

        Args:
            content: Markdown instructions text.

        Returns:
            List of rule strings.
        """
        rules: List[str] = []
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("- "):
                rules.append(stripped[2:].strip())
        return rules

    def identify_section_origins(
        self, content: str
    ) -> Tuple[List[str], List[str]]:
        """Identify which sections came from CORTEX vs user.

        Args:
            content: Markdown text.

        Returns:
            Tuple of (cortex_sections, user_sections) title lists.
        """
        sections = self.parse_sections(content)
        cortex: List[str] = []
        user: List[str] = []
        for title in sections:
            if any(p.lower() in title.lower() for p in _CORTEX_SECTION_PATTERNS):
                cortex.append(title)
            else:
                user.append(title)
        return cortex, user

    # ------------------------------------------------------------------
    # Merging
    # ------------------------------------------------------------------

    def merge_instructions(
        self,
        existing_content: Optional[str],
        cortex_content: str,
    ) -> str:
        """Merge existing instructions with CORTEX template.

        User sections are preserved; CORTEX sections are replaced.

        Args:
            existing_content: Current instructions (may be None).
            cortex_content: CORTEX template content.

        Returns:
            Merged markdown string.
        """
        if not existing_content:
            header = f"<!-- CORTEX Version: {datetime.utcnow().strftime('%Y-%m-%d')} -->\n\n"
            return header + cortex_content

        cortex_sections = self.parse_sections(cortex_content)
        existing_sections = self.parse_sections(existing_content)

        _, user_section_titles = self.identify_section_origins(existing_content)

        merged_parts: List[str] = [
            f"<!-- CORTEX Version: {datetime.utcnow().strftime('%Y-%m-%d')} -->\n",
            "# CORTEX Enhanced Instructions\n",
        ]

        # Preserve user sections
        for title in user_section_titles:
            merged_parts.append(f"\n## {title}\n{existing_sections[title]}\n")

        # Add/update CORTEX sections
        for title, body in cortex_sections.items():
            merged_parts.append(f"\n## {title}\n{body}\n")

        return "\n".join(merged_parts)

    # ------------------------------------------------------------------
    # Conflict detection
    # ------------------------------------------------------------------

    def detect_conflicts(
        self, existing: str, cortex: str
    ) -> List[Dict[str, str]]:
        """Detect conflicting rules between existing and CORTEX instructions.

        Args:
            existing: Existing instructions text.
            cortex: CORTEX instructions text.

        Returns:
            List of conflict dicts with 'topic', 'existing', 'cortex' keys.
        """
        conflicts: List[Dict[str, str]] = []
        conflict_topics = {
            "indent": ["tabs", "spaces", "indentation"],
            "line_length": ["chars per line", "line length", "max line"],
        }
        for topic, keywords in conflict_topics.items():
            existing_matches = [
                k for k in keywords if k.lower() in existing.lower()
            ]
            cortex_matches = [
                k for k in keywords if k.lower() in cortex.lower()
            ]
            if existing_matches and cortex_matches:
                conflicts.append(
                    {
                        "topic": topic,
                        "existing": ", ".join(existing_matches),
                        "cortex": ", ".join(cortex_matches),
                    }
                )
        return conflicts

    def get_resolution_strategies(
        self, conflicts: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """Recommend resolution strategies for conflicts.

        Args:
            conflicts: List of conflict dicts.

        Returns:
            List of strategy dicts.
        """
        strategies: List[Dict[str, str]] = []
        for conflict in conflicts:
            strategies.append(
                {
                    "topic": conflict["topic"],
                    "strategy": "prefer_user",
                    "description": f"Keep user setting for {conflict['topic']}",
                }
            )
        return strategies

    # ------------------------------------------------------------------
    # File generation
    # ------------------------------------------------------------------

    def generate_merged_file(
        self,
        repo_path: Path,
        cortex_template: str = "",
        backup: bool = False,
    ) -> Dict[str, Any]:
        """Generate merged instruction file in the repo.

        Args:
            repo_path: Repository root path.
            cortex_template: CORTEX template content.
            backup: Create backup of existing file.

        Returns:
            Result dict with 'success', 'merged_path', optional 'backup_path',
            'preserved_sections'.
        """
        github_dir = repo_path / ".github"
        github_dir.mkdir(parents=True, exist_ok=True)

        existing_file = github_dir / "copilot-instruction.md"
        existing_content: Optional[str] = None
        backup_path: Optional[Path] = None
        preserved: List[str] = []

        if existing_file.exists():
            existing_content = existing_file.read_text(encoding="utf-8")
            _, user_titles = self.identify_section_origins(existing_content)
            preserved = list(user_titles)
            if backup:
                backup_path = github_dir / "copilot-instruction.md.bak"
                shutil.copy2(existing_file, backup_path)

        merged = self.merge_instructions(existing_content, cortex_template)
        existing_file.write_text(merged, encoding="utf-8")

        result: Dict[str, Any] = {
            "success": True,
            "merged_path": existing_file,
            "backup_path": backup_path,
            "preserved_sections": preserved,
        }

        if self._audit:
            self._audit.log_operation(
                "merge",
                details={
                    "repo": str(repo_path),
                    "preserved": preserved,
                },
            )

        return result

    # ------------------------------------------------------------------
    # CORTEX prompt generation
    # ------------------------------------------------------------------

    def generate_cortex_prompt(
        self,
        repo_path: Path,
        project_type: str = "general",
        regenerate: bool = False,
    ) -> Dict[str, Any]:
        """Generate CORTEX.prompt.md for a repository.

        Args:
            repo_path: Repository root path.
            project_type: Project type for template selection.
            regenerate: Delete existing before generating.

        Returns:
            Result dict with 'success' and 'prompt_path'.
        """
        prompts_dir = repo_path / ".github" / "prompts"
        prompts_dir.mkdir(parents=True, exist_ok=True)
        prompt_path = prompts_dir / "CORTEX.prompt.md"

        if regenerate and prompt_path.exists():
            prompt_path.unlink()

        content = (
            f"# CORTEX Prompt — {project_type}\n\n"
            f"Version: {datetime.utcnow().strftime('%Y-%m-%d')}\n\n"
            f"## {project_type.capitalize()} Governance\n\n"
            "TIER 0 rules apply.\n\n"
            "## Architecture\n\n"
            "Standard CORTEX architecture.\n"
        )
        prompt_path.write_text(content, encoding="utf-8")
        return {"success": True, "prompt_path": prompt_path}

    # ------------------------------------------------------------------
    # Multi-repo
    # ------------------------------------------------------------------

    def process_repos(
        self, repos: List[Path], cortex_template: str = ""
    ) -> List[Dict[str, Any]]:
        """Process instructions for multiple repositories.

        Args:
            repos: List of repo root paths.
            cortex_template: CORTEX template to merge.

        Returns:
            List of result dicts (one per repo).
        """
        results: List[Dict[str, Any]] = []
        for repo in repos:
            result = self.generate_merged_file(repo, cortex_template=cortex_template)
            results.append(result)
        return results

    def load_repo_overrides(self, repo_path: Path) -> Dict[str, Any]:
        """Load repo-specific cortex-override.yaml.

        Args:
            repo_path: Repository root path.

        Returns:
            Override configuration dict.
        """
        override_file = repo_path / ".github" / "cortex-override.yaml"
        if override_file.exists():
            return yaml.safe_load(override_file.read_text(encoding="utf-8")) or {}
        return {}
