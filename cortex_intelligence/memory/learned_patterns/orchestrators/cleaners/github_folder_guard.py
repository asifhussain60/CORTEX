"""
GithubFolderGuard — Protection rules for .github/ folder contents.

AC-ID: VACUUM-GITHUB-GUARD-001
Governance:
    - CORE-008: TDD (tests defined before this module)
    - CORE-011: Type hints 100%
    - CORE-012: Google-style docstrings
    - CORE-013: Specific exceptions only

Purpose:
    The vacuum orchestrator must exercise caution in .github/ because it
    contains live operational artefacts — AI agent specs, prompt files,
    workflow templates — that must never be deleted by automated cleanup.

    This guard encodes three classification outcomes:

    PROTECTED:
        File must NEVER be proposed for deletion.
        - Any *.prompt.md file (active AI prompts)
        - Any *.md in agents/**/ without a DEPRECATED- prefix (active agents)
        - Any non-.md file in .github/ (scripts, yaml, py — not vacuum targets)
        - Any file under .github/prompts/reference/ (setup references)
        - Active templates (response-format-standards.md, etc.)

    VACUUM_ELIGIBLE:
        File is a legitimate vacuum candidate (informational / deprecated).
        - DEPRECATED-*.md files (explicitly marked obsolete)
        - agents/AGENT-INDEX.md (auto-generated index)
        - agents/README.md (folder-level informational readme)
        - prompts/README.md (folder-level informational readme)

    UNRELATED:
        Path is outside .github/ — this guard has no opinion.
        Callers should not pass unrelated paths to is_protected().

Naming Governance:
    All direct subfolders of .github/ must follow lowercase-kebab naming
    (e.g., agents, prompts, cortex-config). Violations are surfaced by
    find_naming_violations().

Author: CORTEX Architect
Phase: VACUUM-GITHUB-GUARD-001
"""

from __future__ import annotations

import re
from enum import Enum, auto
from pathlib import Path
from typing import List


# =============================================================================
# CLASSIFICATION ENUM
# =============================================================================


class GithubFileClassification(Enum):
    """Classification outcome for a file under .github/."""

    PROTECTED = auto()        # Must not be deleted — active operational artefact
    VACUUM_ELIGIBLE = auto()  # Safe vacuum candidate (deprecated / informational)
    UNRELATED = auto()        # Outside .github/ — guard has no opinion


# =============================================================================
# PROTECTION CONSTANTS
# =============================================================================

# Subpath prefixes (relative to .github/) whose contents are ALWAYS eligible
# regardless of filename — these are root-level informational readmes/indexes.
_ALWAYS_ELIGIBLE_EXACT: frozenset[str] = frozenset(
    {
        "agents/README.md",
        "agents/AGENT-INDEX.md",
        "prompts/README.md",
    }
)

# Subpath prefixes (relative to .github/) where ALL descendants are protected.
_ALWAYS_PROTECTED_PREFIXES: tuple[str, ...] = (
    "prompts/reference/",    # Setup reference docs
    "workflows/",            # GitHub Actions — never touched
    "hooks/",                # Git hooks — never touched
    "scripts/",              # Automation scripts — never touched
)

# Subfolders of agents/ whose non-deprecated .md files are always protected.
_PROTECTED_AGENT_SUBFOLDERS: frozenset[str] = frozenset(
    {"core", "education", "orchestration", "support"}
)

# Template files that are explicitly active (protected).
_PROTECTED_TEMPLATE_FILES: frozenset[str] = frozenset(
    {
        "response-format-standards.md",
        "response-template-blocks-modern.md",
        "chat-vs-terminal-guide.md",
        "chat-vs-terminal-quick-ref.md",  # kept — companion to guide
    }
)

# Valid subfolder name pattern: lowercase, letters/digits, hyphens, starts with letter.
_VALID_SUBFOLDER_RE = re.compile(r"^[a-z][a-z0-9\-]*$")


# =============================================================================
# GUARD
# =============================================================================


class GithubFolderGuard:
    """Encodes protection rules for .github/ folder vacuum operations.

    Use this guard before any vacuum cleaner proposes a .github/ file for
    deletion.  The guard answers one question:

        guard.is_protected(path) → bool

    For richer decisions, use classify() to get the full classification.

    Example::

        guard = GithubFolderGuard()
        for candidate in proposed_deletions:
            if candidate.is_relative_to(".github"):
                if guard.is_protected(candidate):
                    skip(candidate)
    """

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def classify(self, path: Path) -> GithubFileClassification:
        """Classify a file path relative to the repository root.

        Args:
            path: Path to the file (relative to repo root, e.g.
                  ``Path('.github/agents/core/CORTEX.md')``).

        Returns:
            GithubFileClassification enum value.
        """
        path = Path(path)
        parts = path.parts  # e.g. ('.github', 'agents', 'core', 'CORTEX.md')

        # Only govern .github/ paths.
        if not parts or parts[0] != ".github":
            return GithubFileClassification.UNRELATED

        # Subpath relative to .github/  (e.g. 'agents/core/CORTEX.md')
        sub = "/".join(parts[1:])

        return self._classify_sub(sub, path)

    def is_protected(self, path: Path) -> bool:
        """Return True if the file must not be deleted by vacuum.

        Args:
            path: Path to the file (relative to repo root).

        Returns:
            True if protected, False if vacuum-eligible.

        Raises:
            ValueError: If path is not under .github/ — callers must
                        pre-filter before invoking this method.
        """
        classification = self.classify(path)
        if classification == GithubFileClassification.UNRELATED:
            raise ValueError(
                f"GithubFolderGuard.is_protected() called on a non-.github path: "
                f"'{path}'. Filter to .github/ paths before calling this method."
            )
        return classification == GithubFileClassification.PROTECTED

    def is_valid_subfolder_name(self, name: str) -> bool:
        """Check that a .github/ direct subfolder follows CORTEX naming governance.

        Valid: lowercase-kebab, starts with a letter.
        Invalid: UPPER, Mixed_Case, underscore_names, leading digits.

        Args:
            name: The subfolder name (just the directory name, not a full path).

        Returns:
            True if the name passes governance, False otherwise.
        """
        if not name:
            return False
        return bool(_VALID_SUBFOLDER_RE.match(name))

    def find_naming_violations(self, github_dir: Path) -> List[Path]:
        """Discover direct subfolders of a .github directory that violate naming governance.

        Args:
            github_dir: Path to the .github directory to inspect.

        Returns:
            List of Path objects for non-compliant subfolder names.
        """
        violations: List[Path] = []
        if not github_dir.is_dir():
            return violations

        for child in github_dir.iterdir():
            if child.is_dir() and not self.is_valid_subfolder_name(child.name):
                violations.append(child)

        return violations

    # ------------------------------------------------------------------
    # Internal classification logic
    # ------------------------------------------------------------------

    def _classify_sub(self, sub: str, original_path: Path) -> GithubFileClassification:
        """Classify a subpath relative to .github/.

        Args:
            sub: Subpath string, e.g. 'agents/core/CORTEX.md'
            original_path: Original full path (for non-md detection).

        Returns:
            GithubFileClassification.
        """
        filename = original_path.name

        # 1. Non-markdown files — never vacuum targets.
        if not filename.lower().endswith(".md"):
            return GithubFileClassification.PROTECTED

        # 2. Always-protected subpath prefixes (workflows/, hooks/, etc.).
        for prefix in _ALWAYS_PROTECTED_PREFIXES:
            if sub.startswith(prefix):
                return GithubFileClassification.PROTECTED

        # 3. Exact always-eligible paths.
        if sub in _ALWAYS_ELIGIBLE_EXACT:
            return GithubFileClassification.VACUUM_ELIGIBLE

        # 4. *.prompt.md anywhere under .github/ is always protected.
        if filename.lower().endswith(".prompt.md"):
            return GithubFileClassification.PROTECTED

        # 5. prompts/ directory (excluding reference/ caught above, README.md caught above).
        if sub.startswith("prompts/"):
            # All remaining .md files in prompts/ root are protected active prompts.
            return GithubFileClassification.PROTECTED

        # 6. agents/<subfolder>/*.md — check DEPRECATED- prefix.
        if sub.startswith("agents/"):
            parts_after_agents = sub[len("agents/"):]  # e.g. 'core/CORTEX.md'
            sub_parts = parts_after_agents.split("/")

            if len(sub_parts) >= 2:
                # Nested: agents/<subfolder>/<filename>
                subfolder = sub_parts[0]
                nested_filename = sub_parts[-1]

                if nested_filename.upper().startswith("DEPRECATED-"):
                    return GithubFileClassification.VACUUM_ELIGIBLE

                if subfolder in _PROTECTED_AGENT_SUBFOLDERS:
                    return GithubFileClassification.PROTECTED

            # Depth-1 agents/ file (e.g. agents/AGENT-INDEX.md) — covered above
            # in exact-eligible; any other root-level .md here is treated as eligible.
            return GithubFileClassification.VACUUM_ELIGIBLE

        # 7. templates/ — check against known active file list.
        if sub.startswith("templates/"):
            if filename in _PROTECTED_TEMPLATE_FILES:
                return GithubFileClassification.PROTECTED
            # Unknown template file → protect by default (conservative).
            return GithubFileClassification.PROTECTED

        # 8. Default: unknown location inside .github/ → protect (conservative).
        return GithubFileClassification.PROTECTED


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "GithubFileClassification",
    "GithubFolderGuard",
]
