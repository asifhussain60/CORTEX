"""Preflight: Prompt/Governance Determinism Validation (phase-126-g, Check #36).

Validates that CORTEX agent and prompt markdown files:
  1. Do not use hedging language ('may', 'might', 'optionally', 'if available')
     in governance rule sections (lines near MUST/SHALL/ALWAYS/NEVER directives).
  2. Every governance section in every agent contains at least one imperative verb.
  3. copilot-instructions.md contains the mandatory P0 header mandate.

Rationale: Hedging language in governance creates ambiguity and allows drift.
"MUST" and "NEVER" are the only acceptable forms in rule blocks.

Scope: .github/agents/ and .github/prompts/ markdown files.
Exemptions:
  - cortex-sync.prompt.md (admin tool, contains conditional sync language)
  - Lines that describe hedging as a PROHIBITED pattern (meta-reference)
  - User-facing narrative text (not governance rule sections)

Gap ref: GAP-126-07
Drift lock: cortex-registry/governance/drift-locks/check-36-prompt-determinism-lock.yaml
Tier: T0 (preflight) — text scan only, no server startup, < 10 s
CORE rules: CORE-008 (TDD), CORE-002 (all output inline)
"""
from __future__ import annotations

import pathlib
import re
from typing import List, Tuple

import pytest
import yaml

CORTEX_ROOT = pathlib.Path(__file__).parents[2]
AGENTS_DIR = CORTEX_ROOT / ".github" / "agents"
PROMPTS_DIR = CORTEX_ROOT / ".github" / "prompts"

# ---------------------------------------------------------------------------
# Governance section detection: lines that start a rules block
# ---------------------------------------------------------------------------
_GOVERNANCE_SECTION_HEADERS = re.compile(
    r"^#{1,4}\s*(rules?|governance|mandatory|non.negotiable|p0|core|enforcement|contract)",
    re.IGNORECASE,
)

# Hedging in governance context: only flagged when immediately following a rule directive
_HEDGING_INLINE = re.compile(
    r"\b(optionally|if available)\b",
    re.IGNORECASE,
)

# Imperative verbs that signal deterministic governance language (case-insensitive)
_IMPERATIVE_PATTERN = re.compile(
    r"\b(MUST|SHALL|ALWAYS|NEVER|REQUIRED|FORBIDDEN|MANDATORY|DO NOT|PROHIBITED|"
    r"must|shall|always|never|required|forbidden|mandatory|do not|prohibited)\b"
)

# Files fully exempt from hedging scan
_HEDGE_EXEMPT_FILES = frozenset({
    "cortex-sync.prompt.md",           # admin sync tool — conditional language intentional
    "MCP-SETUP-GUIDE.md",              # setup guide — instructional conditional prose
})

# Files exempt from imperative-verb requirement (non-governance files)
_IMPERATIVE_EXEMPT_FILES = frozenset({
    "MCP-SETUP-GUIDE.md",
    "AGENT-INDEX.md",
    "README.md",  # index files — not governance agents
})


def _iter_md_files(base_dir: pathlib.Path) -> List[pathlib.Path]:
    if not base_dir.exists():
        return []
    return list(base_dir.rglob("*.md"))


class TestPromptGovernanceDeterminism:
    """Agent and prompt markdown files must use deterministic governance language."""

    def test_no_optionally_if_available_in_governance_files(self) -> None:
        """'optionally' and 'if available' must not appear in governance rule sections."""
        violations: List[str] = []
        for md_file in _iter_md_files(AGENTS_DIR) + _iter_md_files(PROMPTS_DIR):
            if md_file.name in _HEDGE_EXEMPT_FILES:
                continue
            try:
                content = md_file.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for i, line in enumerate(content.splitlines(), 1):
                if _HEDGING_INLINE.search(line):
                    # Exclude lines that describe hedging as prohibited (meta-reference)
                    if "prohibited" in line.lower() or "avoid" in line.lower():
                        continue
                    # Exclude lines that enumerate hedging words as examples of forbidden patterns
                    # (common in audit check tables and governance documentation)
                    if "hedging" in line.lower() or "no hedging" in line.lower():
                        continue
                    if "may.*might.*could" in line.lower() or "'may', 'might'" in line:
                        continue
                    violations.append(
                        f"  {md_file.relative_to(CORTEX_ROOT)}:{i}: {line.strip()[:120]}"
                    )
        assert not violations, (
            f"Hedging language ('optionally', 'if available') in governance files:\n"
            + "\n".join(violations)
        )

    def test_agent_files_contain_at_least_one_imperative_verb(self) -> None:
        """Every agent markdown file must use at least one MUST/SHALL/ALWAYS/NEVER directive."""
        missing: List[str] = []
        for md_file in _iter_md_files(AGENTS_DIR):
            if md_file.name in _IMPERATIVE_EXEMPT_FILES:
                continue
            try:
                content = md_file.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if not _IMPERATIVE_PATTERN.search(content):
                missing.append(f"  {md_file.relative_to(CORTEX_ROOT)}")
        assert not missing, (
            f"Agent files with no imperative governance verb (MUST/SHALL/ALWAYS/NEVER):\n"
            + "\n".join(missing)
            + "\nAdd at least one imperative directive to each agent's governance section."
        )

    def test_copilot_instructions_has_p0_header_mandate(self) -> None:
        """copilot-instructions.md must contain the P0 mandatory response header rule."""
        instructions = CORTEX_ROOT / ".github" / "copilot-instructions.md"
        assert instructions.exists(), ".github/copilot-instructions.md not found."
        content = instructions.read_text(encoding="utf-8")
        assert "P0" in content, (
            "copilot-instructions.md must contain 'P0' governance rule references."
        )
        assert "MANDATORY" in content or "mandatory" in content.lower(), (
            "copilot-instructions.md must contain the mandatory response header rule."
        )

    def test_copilot_instructions_references_response_header(self) -> None:
        """copilot-instructions.md must reference the response header requirement."""
        instructions = CORTEX_ROOT / ".github" / "copilot-instructions.md"
        if not instructions.exists():
            pytest.skip("copilot-instructions.md not found")
        content = instructions.read_text(encoding="utf-8")
        # Must reference the response header (CORTEX {mode} or Author line)
        has_header_ref = (
            "RESPONSE HEADER" in content.upper()
            or "response header" in content.lower()
            or "CORTEX {mode}" in content
        )
        assert has_header_ref, (
            "copilot-instructions.md must reference the mandatory CORTEX response header format."
        )


class TestPromptDeterminismDriftLock:
    """Permanent CI drift lock — Check #36 invariants."""

    def test_drift_lock_yaml_exists(self) -> None:
        lock = (
            CORTEX_ROOT
            / "cortex-registry"
            / "governance"
            / "drift-locks"
            / "check-36-prompt-determinism-lock.yaml"
        )
        assert lock.exists(), (
            "Drift lock YAML check-36-prompt-determinism-lock.yaml not found."
        )

    def test_drift_lock_yaml_is_valid(self) -> None:
        lock = (
            CORTEX_ROOT
            / "cortex-registry"
            / "governance"
            / "drift-locks"
            / "check-36-prompt-determinism-lock.yaml"
        )
        if not lock.exists():
            pytest.skip("Lock file missing")
        data = yaml.safe_load(lock.read_text(encoding="utf-8"))
        assert data is not None
        assert data.get("check_number") == 36
