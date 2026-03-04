"""Preflight test — Check #39: cortex-sync Non-Production Admin Tool Marker Enforcement.

Every .github/prompts/*.prompt.md and .github/agents/**/*.md that is NOT a
production-core file must contain ``scope: non-production-admin`` (anywhere in
the file, typically in YAML frontmatter or a metadata block).

Production-core files are intentionally EXCLUDED from this requirement — they
must NOT carry the non-production marker.

cortex-sync.prompt.md must declare an explicit production_files exclusion list
so the sync tool never excludes production-core files from sync targets.

Gap ref: GAP-126-10
Check: #39
Phase: phase-126-j
"""
from __future__ import annotations

import pathlib
import re

import pytest
import yaml

CORTEX_ROOT = pathlib.Path(__file__).parents[2]
GITHUB_DIR = CORTEX_ROOT / ".github"
PROMPTS_DIR = GITHUB_DIR / "prompts"
AGENTS_DIR = GITHUB_DIR / "agents"
DRIFT_LOCKS_DIR = CORTEX_ROOT / "cortex-registry" / "governance" / "drift-locks"

# Files that ARE production — must NOT carry the non-production marker
_PRODUCTION_FILES: frozenset[pathlib.Path] = frozenset(
    [
        PROMPTS_DIR / "CORTEX.prompt.md",
        PROMPTS_DIR / "cortex-architect.prompt.md",
        AGENTS_DIR / "core" / "CORTEX.md",
        AGENTS_DIR / "core" / "cortex-executor.md",
        AGENTS_DIR / "core" / "cortex-architect.md",
        CORTEX_ROOT / ".github" / "copilot-instructions.md",
    ]
)

# Index/README files are exempt from the marker requirement
_README_EXEMPT: frozenset[str] = frozenset(["README.md", "AGENT-INDEX.md"])

_MARKER = "scope: non-production-admin"
# Pattern that matches the marker NOT inside a markdown table cell (pipes around it)
# i.e. must appear at the start of a line or after whitespace, not surrounded by | chars
_MARKER_PATTERN = re.compile(r"^[ \t]*scope:\s*non-production-admin\s*$", re.MULTILINE)
_PRODUCTION_FILES_HEADER = "production_files:"


def _is_exempt(path: pathlib.Path) -> bool:
    """Return True if the path should be skipped entirely."""
    if path in _PRODUCTION_FILES:
        return True
    if path.name in _README_EXEMPT:
        return True
    # Reference/guide docs are exempt
    if path.parent.name == "reference":
        return True
    return False


def _collect_non_production_prompts() -> list[pathlib.Path]:
    """All .prompt.md and .md files in .github/prompts/ that are non-production."""
    results = []
    for p in PROMPTS_DIR.rglob("*.md"):
        if _is_exempt(p):
            continue
        results.append(p)
    return sorted(results)


def _collect_non_production_agents() -> list[pathlib.Path]:
    """All .md files in .github/agents/ that are non-production."""
    results = []
    for p in AGENTS_DIR.rglob("*.md"):
        if _is_exempt(p):
            continue
        if p.parent.name == "reference":
            continue
        results.append(p)
    return sorted(results)


class TestSyncNonProductionMarkers:
    """Check #39: scope: non-production-admin marker enforcement."""

    def test_non_production_prompts_have_scope_marker(self) -> None:
        """Every non-production prompt file must declare scope: non-production-admin."""
        missing: list[str] = []
        for p in _collect_non_production_prompts():
            content = p.read_text(encoding="utf-8")
            if not _MARKER_PATTERN.search(content):
                missing.append(str(p.relative_to(CORTEX_ROOT)))
        assert not missing, (
            f"These non-production prompt files are missing '{_MARKER}':\n"
            + "\n".join(f"  - {m}" for m in missing)
            + "\n\nAdd the following to each file's YAML frontmatter or metadata block:\n"
            + f"  {_MARKER}"
        )

    def test_non_production_agents_have_scope_marker(self) -> None:
        """Every non-production agent file must declare scope: non-production-admin."""
        missing: list[str] = []
        for p in _collect_non_production_agents():
            content = p.read_text(encoding="utf-8")
            if not _MARKER_PATTERN.search(content):
                missing.append(str(p.relative_to(CORTEX_ROOT)))
        assert not missing, (
            f"These non-production agent files are missing '{_MARKER}':\n"
            + "\n".join(f"  - {m}" for m in missing)
            + "\n\nAdd 'scope: non-production-admin' to each file."
        )

    def test_production_prompts_do_not_have_non_production_marker(self) -> None:
        """Production-core files must NOT carry the non-production marker."""
        violations: list[str] = []
        for p in _PRODUCTION_FILES:
            if not p.exists():
                continue
            content = p.read_text(encoding="utf-8")
            if _MARKER_PATTERN.search(content):
                violations.append(str(p.relative_to(CORTEX_ROOT)))
        assert not violations, (
            f"Production files must NOT have '{_MARKER}':\n"
            + "\n".join(f"  - {v}" for v in violations)
        )

    def test_cortex_sync_has_production_files_exclusion_list(self) -> None:
        """cortex-sync.prompt.md must declare an explicit production_files exclusion list."""
        sync_prompt = PROMPTS_DIR / "cortex-sync.prompt.md"
        assert sync_prompt.exists(), "cortex-sync.prompt.md is missing"
        content = sync_prompt.read_text(encoding="utf-8")
        assert _PRODUCTION_FILES_HEADER in content, (
            "cortex-sync.prompt.md must contain a 'production_files:' exclusion list "
            "to ensure production-core files are never excluded from sync targets."
        )

    def test_non_production_file_list_is_not_empty(self) -> None:
        """Sanity: at least 5 non-production files must be collected."""
        prompts = _collect_non_production_prompts()
        agents = _collect_non_production_agents()
        total = len(prompts) + len(agents)
        assert total >= 5, (
            f"Expected at least 5 non-production files, found {total}. "
            "Check _PRODUCTION_FILES or the directory scan."
        )

    @pytest.mark.skipif(
        not (DRIFT_LOCKS_DIR / "check-39-sync-marker-lock.yaml").exists(),
        reason="Drift lock not yet created (pre-GREEN)",
    )
    def test_drift_lock_check_39_exists_and_valid(self) -> None:
        """Drift lock YAML for Check #39 must exist and be valid."""
        lock = DRIFT_LOCKS_DIR / "check-39-sync-marker-lock.yaml"
        data = yaml.safe_load(lock.read_text(encoding="utf-8"))
        assert data is not None
        assert data.get("check_number") == 39
        assert data.get("status") == "ACTIVE"
