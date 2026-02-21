"""
CopilotMerger — Merges CORTEX intelligence with existing repo Copilot instructions.

Authority: CORE-035 (single canonical implementation)
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import yaml  # type: ignore[import]
except ImportError:
    yaml = None  # type: ignore[assignment]


class CopilotMerger:
    """Discovers, parses, and merges Copilot instruction files across repos.

    Args:
        audit_enabled: Whether to write operations to SharedAuditTrail.
    """

    # Candidate paths searched by find_existing_instructions
    _CANDIDATE_PATHS = [
        ".github/copilot-instruction.md",
        ".github/prompts/copilot-instruction.md",
        ".github/copilot-instructions.md",
        ".github/prompts/copilot-instructions.md",
    ]

    # Section names that are considered CORTEX-owned
    _CORTEX_SECTION_KEYWORDS = {"CORTEX", "TIER 0", "TIER 1", "Governance", "CORE"}

    def __init__(self, audit_enabled: bool = False) -> None:
        """Initialize instance."""
        self.audit_enabled = audit_enabled
        self._audit: Optional[Any] = None
        if audit_enabled:
            try:
                from cortex.orchestrators.shared_audit_trail import SharedAuditTrail
                self._audit = SharedAuditTrail()
            except Exception:
                pass

    # ── Discovery ────────────────────────────────────────────────────

    def find_existing_instructions(self, repo_path: Path) -> Optional[Dict[str, Any]]:
        """Search for an existing copilot instruction file under repo_path.

        Returns:
            Dict with ``path`` and ``content`` keys, or ``None`` if not found.
        """
        repo_path = Path(repo_path)
        for rel in self._CANDIDATE_PATHS:
            candidate = repo_path / rel
            if candidate.exists():
                return {"path": candidate, "content": candidate.read_text()}
        return None

    def find_cortex_prompt(self, repo_path: Path) -> Optional[Dict[str, Any]]:
        """Find CORTEX.prompt.md under .github/prompts/.

        Returns:
            Dict with ``path`` and ``content``, or ``None``.
        """
        repo_path = Path(repo_path)
        target = repo_path / ".github" / "prompts" / "CORTEX.prompt.md"
        if target.exists():
            return {"path": target, "content": target.read_text()}
        return None

    # ── Parsing ──────────────────────────────────────────────────────

    def parse_sections(self, content: str) -> Dict[str, str]:
        """Parse markdown content into ``{section_title: body}`` dict."""
        sections: Dict[str, str] = {}
        current_title: Optional[str] = None
        current_body: List[str] = []
        for line in content.splitlines():
            m = re.match(r"^#{1,3}\s+(.+)$", line)
            if m:
                if current_title:
                    sections[current_title] = "\n".join(current_body).strip()
                current_title = m.group(1).strip()
                current_body = []
            else:
                if current_title:
                    current_body.append(line)
        if current_title:
            sections[current_title] = "\n".join(current_body).strip()
        return sections

    def extract_project_rules(self, content: str) -> List[str]:
        """Extract bullet-point rules from content.

        Returns list of rule strings.
        """
        rules: List[str] = []
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("-") or stripped.startswith("*"):
                rule = re.sub(r"^[-*]\s*", "", stripped).strip()
                if rule:
                    rules.append(rule)
        return rules

    def identify_section_origins(
        self, content: str
    ) -> Tuple[List[str], List[str]]:
        """Split section titles into CORTEX-owned and user-owned.

        Returns:
            Tuple of (cortex_sections, user_sections).
        """
        sections = self.parse_sections(content)
        cortex: List[str] = []
        user: List[str] = []
        for title in sections:
            if any(kw in title for kw in self._CORTEX_SECTION_KEYWORDS):
                cortex.append(title)
            else:
                user.append(title)
        return cortex, user

    # ── Merging ──────────────────────────────────────────────────────

    def merge_instructions(
        self,
        existing: Optional[str],
        cortex_content: str,
    ) -> str:
        """Merge existing and CORTEX instruction content.

        User-owned sections are preserved; CORTEX-owned sections are
        updated from cortex_content.  A version header is always added.

        Args:
            existing: Existing instruction text (may be ``None``).
            cortex_content: Fresh CORTEX instruction text.

        Returns:
            Merged markdown string.
        """
        header = "<!-- CORTEX version: managed -->\n"

        if existing is None:
            return header + cortex_content

        existing_text: str = existing if isinstance(existing, str) else existing.get("content", "")

        # Parse sections
        existing_sections = self.parse_sections(existing_text)
        cortex_sections_map = self.parse_sections(cortex_content)

        cortex_owned, user_owned = self.identify_section_origins(existing_text)

        lines = [header]

        # 1. Add CORTEX sections (updated from new cortex_content)
        for title, body in cortex_sections_map.items():
            lines.append(f"## {title}")
            lines.append(body)
            lines.append("")

        # 2. Preserve user sections (not in CORTEX sections)
        for title in user_owned:
            body = existing_sections.get(title, "")
            lines.append(f"## {title}")
            lines.append(body)
            lines.append("")

        return "\n".join(lines)

    # ── Conflict Detection ───────────────────────────────────────────

    _CONFLICT_PAIRS = [
        ("indent", ["spaces", "tabs"]),
        ("line.?length", [r"\d{2,3}"]),
        ("quote", ["single", "double"]),
    ]

    def detect_conflicts(self, existing: str, cortex: str) -> List[Dict[str, str]]:
        """Detect conflicting rules between existing and CORTEX content.

        Returns list of conflict dicts with ``topic``, ``existing``,
        ``cortex`` keys.
        """
        conflicts: List[Dict[str, str]] = []
        ex_lower = existing.lower()
        ct_lower = cortex.lower()

        for topic, variants in self._CONFLICT_PAIRS:
            ex_matches = [v for v in variants if re.search(v, ex_lower)]
            ct_matches = [v for v in variants if re.search(v, ct_lower)]
            if ex_matches and ct_matches and set(ex_matches) != set(ct_matches):
                conflicts.append({
                    "topic": topic,
                    "existing": ex_matches[0],
                    "cortex": ct_matches[0],
                })

        return conflicts

    def get_resolution_strategies(
        self, conflicts: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """Return recommended resolution strategy for each conflict.

        Args:
            conflicts: List of conflict dicts from detect_conflicts.

        Returns:
            List of dicts with ``topic`` and ``strategy`` keys.
        """
        return [
            {"topic": c["topic"], "strategy": "prefer_cortex"}
            for c in conflicts
        ]

    # ── File Generation ──────────────────────────────────────────────

    def generate_merged_file(
        self,
        repo_path: Path,
        cortex_template: str = "",
        output_path: Optional[Path] = None,
        backup: bool = False,
    ) -> Dict[str, Any]:
        """Generate (or overwrite) the merged instruction file.

        Args:
            repo_path: Repository root.
            cortex_template: CORTEX template string to merge.
            output_path: Override output path; defaults to
                ``.github/copilot-instruction.md``.
            backup: If True, backup existing file before overwriting.

        Returns:
            Dict with ``success``, ``merged_path``, ``backup_path``
            (None when not backed up), and ``preserved_sections``.
        """
        repo_path = Path(repo_path)
        github_dir = repo_path / ".github"
        github_dir.mkdir(parents=True, exist_ok=True)

        merged_path = output_path or github_dir / "copilot-instruction.md"

        existing = self.find_existing_instructions(repo_path)
        backup_path: Optional[Path] = None

        if existing and backup:
            backup_path = existing["path"].with_suffix(".md.bak")
            shutil.copy2(existing["path"], backup_path)

        existing_text = existing["content"] if existing else None
        _, user_sections = self.identify_section_origins(existing_text or "")
        preserved_sections = user_sections

        merged = self.merge_instructions(existing_text, cortex_template)
        merged_path.write_text(merged)

        if self._audit:
            try:
                self._audit.log_operation(
                    str(repo_path), "copilot_merge", "merge_instructions"
                )
            except Exception:
                pass

        return {
            "success": True,
            "merged_path": merged_path,
            "backup_path": backup_path,
            "preserved_sections": preserved_sections,
        }

    def generate_cortex_prompt(
        self,
        repo_path: Path,
        project_type: str = "generic",
        regenerate: bool = False,
    ) -> Dict[str, Any]:
        """Generate CORTEX.prompt.md under .github/prompts/.

        Args:
            repo_path: Repository root.
            project_type: Project type string (e.g. 'finops', 'auth').
            regenerate: If True, delete existing prompt before regenerating.

        Returns:
            Dict with ``success`` and ``prompt_path`` keys.
        """
        repo_path = Path(repo_path)
        prompts_dir = repo_path / ".github" / "prompts"
        prompts_dir.mkdir(parents=True, exist_ok=True)

        prompt_path = prompts_dir / "CORTEX.prompt.md"

        if regenerate and prompt_path.exists():
            prompt_path.unlink()

        content = (
            f"# CORTEX Master Prompt\n\n"
            f"Project Type: {project_type}\n\n"
            f"## CORTEX Governance\n\nFollow all CORE governance rules.\n\n"
            f"## {project_type.upper()} Rules\n\nApply {project_type}-specific standards.\n"
        )
        prompt_path.write_text(content)

        return {"success": True, "prompt_path": prompt_path}

    # ── Multi-Repo ───────────────────────────────────────────────────

    def load_repo_overrides(self, repo_path: Path) -> Dict[str, Any]:
        """Load cortex-override.yaml from .github/ if it exists.

        Returns:
            Dict of override settings, empty dict if not found.
        """
        repo_path = Path(repo_path)
        override_file = repo_path / ".github" / "cortex-override.yaml"
        if not override_file.exists():
            return {}
        if yaml is None:
            return {}
        try:
            data = yaml.safe_load(override_file.read_text()) or {}
            return data
        except Exception:
            return {}

    def process_repos(
        self, repos: List[Path], cortex_template: str = ""
    ) -> List[Dict[str, Any]]:
        """Process Copilot instructions for multiple repositories.

        Args:
            repos: List of repository root paths.
            cortex_template: CORTEX template string to apply.

        Returns:
            List of result dicts from generate_merged_file.
        """
        results = []
        for repo in repos:
            try:
                result = self.generate_merged_file(repo, cortex_template=cortex_template)
                results.append(result)
            except Exception as exc:
                results.append({"success": False, "error": str(exc)})
        return results

    def log_merge_operation(
        self, repo_path: Path, preserved_sections: List[str]
    ) -> None:
        """Log a merge operation to the audit trail."""
        if self._audit:
            try:
                self._audit.log_operation(
                    str(repo_path),
                    "copilot_merge",
                    f"preserved={preserved_sections}",
                )
            except Exception:
                pass
