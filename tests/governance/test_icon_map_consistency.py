"""
GAP-128-C-02: Icon usage in prompts and agents must map to the approved icon system.

The approved icon system is defined in .github/templates/cortex-response-templates.md
(section: ## 🎨 ICON SYSTEM). Prompts and agents must not use tree-drawing characters
(├─ └─ │ ╔ ╗ ╚ ╝) which collapse in VS Code Copilot Chat.

Drift lock: check-44-response-template-compliance-lock.yaml
"""

import re
from pathlib import Path
from typing import List, Tuple
import pytest

REPO_ROOT = Path(__file__).parents[2]
PROMPTS_DIR = REPO_ROOT / ".github/prompts"
AGENTS_DIR = REPO_ROOT / ".github/agents"

# Box-drawing / tree characters that collapse in VS Code Copilot Chat dark themes
# Sourced from cortex-response-templates.md § Mandatory Rendering Rules (Rule 1)
FORBIDDEN_TREE_CHARS = [
    "\u251c",  # ├
    "\u2514",  # └
    "\u2502",  # │
    "\u2554",  # ╔
    "\u2557",  # ╗
    "\u255a",  # ╚
    "\u255d",  # ╝
    "\u2550",  # ═
    "\u2560",  # ╠
    "\u2563",  # ╣
    "\u2566",  # ╦
    "\u2569",  # ╩
    "\u256c",  # ╬
]
FORBIDDEN_PATTERN = re.compile("[" + "".join(FORBIDDEN_TREE_CHARS) + "]")

# Long horizontal lines like ━━━━ — Rule 3 in rendering rules
LONG_HORIZ_PATTERN = re.compile(r"[━─]{5,}")

# Multiple H1 headings — Rule R6 (only one H1 per response)
H1_PATTERN = re.compile(r"^# ", re.MULTILINE)


def _scan_files(base_dir: Path) -> List[Path]:
    """Collect all .md files under a directory, excluding README and reference docs."""
    if not base_dir.exists():
        return []
    # README files legitimately use tree chars for structural display
    # Reference/doc prompt files contain code block examples showing forbidden patterns
    EXCLUDED_NAMES = {"README.MD", "README.md"}
    EXCLUDED_SUFFIXES = {"-doc.prompt.md"}
    result = []
    for p in base_dir.rglob("*.md"):
        if p.name.upper() == "README.MD":
            continue
        if any(str(p).endswith(suf) for suf in EXCLUDED_SUFFIXES):
            continue
        result.append(p)
    return result


def _find_violations(content: str, pattern: re.Pattern) -> List[int]:
    """Return line numbers (1-based) where pattern matches OUTSIDE fenced code blocks."""
    lines = content.splitlines()
    hits = []
    in_fence = False
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        # Toggle fenced code block state (``` or ~~~)
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
        if in_fence:
            continue  # skip code block content
        if pattern.search(line):
            hits.append(i)
    return hits


class TestIconMapConsistency:
    """GAP-128-C-02: Icon usage consistency — no forbidden tree chars in prompts/agents."""

    def test_no_tree_chars_in_prompts(self):
        """Prompts must not use box-drawing tree characters (├─ └─ │ ╔ etc.)."""
        prompt_files = _scan_files(PROMPTS_DIR)
        violations: List[str] = []
        for path in sorted(prompt_files):
            content = path.read_text(encoding="utf-8", errors="replace")
            lines_with_hits = _find_violations(content, FORBIDDEN_PATTERN)
            for lineno in lines_with_hits:
                rel = path.relative_to(REPO_ROOT)
                violations.append(f"{rel}:{lineno}")
        assert violations == [], (
            f"Box-drawing tree characters found in prompts (collapse in VS Code Chat):\n"
            + "\n".join(f"  {v}" for v in violations[:30])
        )

    def test_no_tree_chars_in_agents(self):
        """Agents must not use box-drawing tree characters (outside code blocks)."""
        # These agent files legitimately contain tree chars inside code block examples
        # (documenting patterns to avoid or showing old API diagrams)
        KNOWN_EXEMPT_AGENTS = {
            "cortex-phase-resolver.md",  # contains code block diagrams of request flow
        }
        agent_files = [
            p for p in _scan_files(AGENTS_DIR)
            if p.name not in KNOWN_EXEMPT_AGENTS
        ]
        violations: List[str] = []
        for path in sorted(agent_files):
            content = path.read_text(encoding="utf-8", errors="replace")
            lines_with_hits = _find_violations(content, FORBIDDEN_PATTERN)
            for lineno in lines_with_hits:
                rel = path.relative_to(REPO_ROOT)
                violations.append(f"{rel}:{lineno}")
        assert violations == [], (
            f"Box-drawing tree characters found in agents (collapse in VS Code Chat):\n"
            + "\n".join(f"  {v}" for v in violations[:30])
        )

    def test_no_long_horizontal_lines_in_prompts(self):
        """Prompts must not use long horizontal lines (━━━━) — they wrap badly in narrow panels."""
        prompt_files = _scan_files(PROMPTS_DIR)
        violations: List[str] = []
        for path in sorted(prompt_files):
            content = path.read_text(encoding="utf-8", errors="replace")
            hits = _find_violations(content, LONG_HORIZ_PATTERN)
            for lineno in hits:
                rel = path.relative_to(REPO_ROOT)
                violations.append(f"{rel}:{lineno}")
        assert violations == [], (
            f"Long horizontal line characters found in prompts (Rule 3 violation):\n"
            + "\n".join(f"  {v}" for v in violations[:30])
        )

    def test_prompts_dir_exists(self):
        """The .github/prompts directory must exist."""
        assert PROMPTS_DIR.exists(), f"Prompts directory not found: {PROMPTS_DIR}"

    def test_agents_dir_exists(self):
        """The .github/agents directory must exist."""
        assert AGENTS_DIR.exists(), f"Agents directory not found: {AGENTS_DIR}"
