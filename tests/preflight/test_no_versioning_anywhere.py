"""Preflight: No-Versioning-Anywhere Guardrail (phase-126-e, Check #34).

Enforces that production governance YAML files and prompt/agent markdown files
do not contain bare `version:` or `release:` fields at the document top level.
Such fields violate CORTEX's no-versioning-anywhere rule (CORE-002 extension):
all artefacts are date-stamped, not versioned.

Exclusions (intentionally version-like patterns):
  - Python package constraints (ruff>=, pytest>=, etc.) in requirements/pyproject
  - git rev/tag references in CI config
  - D3.js CDN URLs (e.g. d3.v7.min.js — library reference, not CORTEX version)
  - Historical phase-history YAML files under cortex-registry/planning/phases/
  - file-naming-rules.yaml (defines the _v\\d+ forbidden pattern — meta-reference)
  - Descriptions/evidence text that mentions versioning as a concept to prohibit

Gap ref: GAP-126-05
Drift lock: cortex-registry/governance/drift-locks/check-34-no-versioning-lock.yaml
Tier: T0 (preflight) — grep + YAML parse only, no server startup, < 10 s
CORE rules: CORE-008 (TDD), CORE-002 (no report files / no versioning artefacts)
"""
from __future__ import annotations

import pathlib
import re
from typing import List, Tuple

import pytest
import yaml

CORTEX_ROOT = pathlib.Path(__file__).parents[2]

# ---------------------------------------------------------------------------
# Scanned directories — governance + prompts/agents only
# ---------------------------------------------------------------------------
_SCAN_DIRS = [
    CORTEX_ROOT / "cortex-registry" / "governance",
    CORTEX_ROOT / "cortex-registry" / "workflows",
    CORTEX_ROOT / "cortex-registry" / "templates",
    CORTEX_ROOT / "cortex-registry" / "core",
    CORTEX_ROOT / ".github" / "agents",
    CORTEX_ROOT / ".github" / "prompts",
]

# ---------------------------------------------------------------------------
# Files exempt from the version: field check
# ---------------------------------------------------------------------------
_VERSION_FIELD_ALLOWLIST = frozenset({
    # file-naming-rules.yaml contains the _v\d+ REGEX PATTERN (meta-reference to prohibit versioning)
    str(CORTEX_ROOT / "cortex-registry" / "config" / "file-naming-rules.yaml"),
})

# ---------------------------------------------------------------------------
# Directories exempt — historical phase files record completed work
# ---------------------------------------------------------------------------
_EXEMPT_DIR_PREFIXES: Tuple[str, ...] = (
    str(CORTEX_ROOT / "cortex-registry" / "planning" / "phases"),
    str(CORTEX_ROOT / "cortex-registry" / "playbooks"),
    str(CORTEX_ROOT / "cortex-registry" / "artifacts"),
    str(CORTEX_ROOT / "cortex-registry" / "memory"),
    str(CORTEX_ROOT / "cortex-registry" / "metrics"),
    str(CORTEX_ROOT / "cortex-registry" / "config"),  # config yamls may track schema versions
    str(CORTEX_ROOT / "cortex-registry" / "knowledge"),
    str(CORTEX_ROOT / "cortex-registry" / "company"),
)

# Pattern: bare `version:` or `release:` at root YAML level (line starts with it)
_VERSION_FIELD_PATTERN = re.compile(r"^\s*version\s*:\s*\S", re.MULTILINE)
_RELEASE_FIELD_PATTERN = re.compile(r"^\s*release\s*:\s*\S", re.MULTILINE)


def _is_exempt(path: pathlib.Path) -> bool:
    path_str = str(path)
    if path_str in _VERSION_FIELD_ALLOWLIST:
        return True
    return any(path_str.startswith(prefix) for prefix in _EXEMPT_DIR_PREFIXES)


def _scan_for_version_fields(extensions: Tuple[str, ...]) -> List[Tuple[pathlib.Path, int, str]]:
    """Return (file, line_number, line) tuples for version/release fields found."""
    violations: List[Tuple[pathlib.Path, int, str]] = []
    for scan_dir in _SCAN_DIRS:
        if not scan_dir.exists():
            continue
        for f in scan_dir.rglob("*"):
            if f.suffix not in extensions:
                continue
            if _is_exempt(f):
                continue
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for i, line in enumerate(content.splitlines(), 1):
                stripped = line.strip()
                if _VERSION_FIELD_PATTERN.match(line) or _RELEASE_FIELD_PATTERN.match(line):
                    violations.append((f, i, stripped))
    return violations


class TestNoVersioningAnywhereYAML:
    """Governance YAML and workflow templates must not contain bare version: fields."""

    def test_no_version_fields_in_governance_yamls(self) -> None:
        """No version: or release: field at root level in governance/workflow YAML files."""
        violations = _scan_for_version_fields((".yaml", ".yml"))
        if violations:
            lines = [
                f"  {v[0].relative_to(CORTEX_ROOT)}:{v[1]}: {v[2]}"
                for v in violations
            ]
            pytest.fail(
                f"Found {len(violations)} version/release field(s) in governance YAMLs "
                f"(Check #34 — no-versioning-anywhere):\n" + "\n".join(lines)
            )

    def test_no_version_fields_in_github_agents(self) -> None:
        """Agent markdown files must not use YAML frontmatter version: fields."""
        agents_dir = CORTEX_ROOT / ".github" / "agents"
        if not agents_dir.exists():
            pytest.skip("No .github/agents directory")
        violations: List[str] = []
        for md_file in agents_dir.rglob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            # Only check frontmatter (first 30 lines)
            frontmatter_lines = content.splitlines()[:30]
            for i, line in enumerate(frontmatter_lines, 1):
                if _VERSION_FIELD_PATTERN.match(line) or _RELEASE_FIELD_PATTERN.match(line):
                    violations.append(
                        f"  {md_file.relative_to(CORTEX_ROOT)}:{i}: {line.strip()}"
                    )
        assert not violations, (
            f"version: field in agent frontmatter:\n" + "\n".join(violations)
        )

    def test_no_version_fields_in_github_prompts(self) -> None:
        """Prompt markdown files must not use YAML frontmatter version: fields."""
        prompts_dir = CORTEX_ROOT / ".github" / "prompts"
        if not prompts_dir.exists():
            pytest.skip("No .github/prompts directory")
        violations: List[str] = []
        for md_file in prompts_dir.rglob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            frontmatter_lines = content.splitlines()[:30]
            for i, line in enumerate(frontmatter_lines, 1):
                if _VERSION_FIELD_PATTERN.match(line) or _RELEASE_FIELD_PATTERN.match(line):
                    violations.append(
                        f"  {md_file.relative_to(CORTEX_ROOT)}:{i}: {line.strip()}"
                    )
        assert not violations, (
            f"version: field in prompt frontmatter:\n" + "\n".join(violations)
        )

    def test_atom_principle_yaml_has_no_version_field(self) -> None:
        """atom-principle.yaml must not contain a version: field (fixed GAP-126-05)."""
        atom = (
            CORTEX_ROOT
            / "cortex-registry"
            / "templates"
            / "response"
            / "atoms"
            / "atom-principle.yaml"
        )
        if not atom.exists():
            pytest.skip("atom-principle.yaml not found")
        content = atom.read_text(encoding="utf-8")
        assert not _VERSION_FIELD_PATTERN.search(content), (
            "atom-principle.yaml still contains a version: field. Remove it."
        )

    def test_no_v1_v2_markers_in_workflow_template_ids(self) -> None:
        """Workflow template id: fields must not end with _v1, _v2, -v1, -v2 suffixes."""
        workflows_dir = CORTEX_ROOT / "cortex-registry" / "workflows"
        if not workflows_dir.exists():
            pytest.skip("No workflows directory")
        violations: List[str] = []
        versioned_id = re.compile(r"^\s*id\s*:.*[-_]v\d+\s*$", re.IGNORECASE)
        for yaml_file in workflows_dir.rglob("*.yaml"):
            try:
                content = yaml_file.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for i, line in enumerate(content.splitlines(), 1):
                if versioned_id.match(line):
                    violations.append(
                        f"  {yaml_file.relative_to(CORTEX_ROOT)}:{i}: {line.strip()}"
                    )
        assert not violations, (
            "Workflow template IDs must not carry _v1/_v2 version suffixes:\n"
            + "\n".join(violations)
        )


class TestNoVersioningDriftLock:
    """Permanent CI drift lock — Check #34 invariants."""

    def test_drift_lock_yaml_exists(self) -> None:
        lock = (
            CORTEX_ROOT
            / "cortex-registry"
            / "governance"
            / "drift-locks"
            / "check-34-no-versioning-lock.yaml"
        )
        assert lock.exists(), (
            "Drift lock YAML check-34-no-versioning-lock.yaml not found."
        )

    def test_drift_lock_yaml_is_valid(self) -> None:
        lock = (
            CORTEX_ROOT
            / "cortex-registry"
            / "governance"
            / "drift-locks"
            / "check-34-no-versioning-lock.yaml"
        )
        if not lock.exists():
            pytest.skip("Lock file missing")
        data = yaml.safe_load(lock.read_text(encoding="utf-8"))
        assert data is not None
        assert data.get("check_number") == 34
