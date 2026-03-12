"""
Phase 146: Response Rendering Rules Golden Tests — 14-Rule Template Validation
AC_START: AC-146-RESPONSE-RENDERING-RULES-001

Validates all response composition YAMLs and cortex-response-templates.md against
the 14 Mandatory Rendering Rules defined in:
  .github/templates/cortex-response-templates.md § Mandatory Rendering Rules

Rules validated:
  Rule 1  — No tree characters (├─ └─ │)
  Rule 3  — No long horizontal lines (━━━━)
  Rule 4  — Max 4-5 table columns (≤ 6 pipes in header row)
  R1      — Blank line required after every ## / ### heading
  R2      — Blank line before and after every list
  R3      — Table requires blank line before it
  R4      — No empty headers (H2/H3 with no content below)
  R5      — No hard-wrap within paragraphs
  R6      — Single H1 per composition (all content sections use H2+)
  DECL    — All YAML files declare rendering_rules.forbidden covering key items

Authority: CORE-008 (TDD), CORE-064 (Sweep Completeness)
Covers: GAP-146-01
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

import pytest
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = PROJECT_ROOT / "cortex-registry" / "templates" / "response"
ATOMS_DIR = TEMPLATES_DIR / "atoms"
BLOCKS_DIR = TEMPLATES_DIR / "blocks"
COMPOSITIONS_DIR = TEMPLATES_DIR / "compositions"
REGISTRY_FILE = TEMPLATES_DIR / "_registry.yaml"
RESPONSE_TEMPLATES_MD = PROJECT_ROOT / ".github" / "templates" / "cortex-response-templates.md"

# ─── Tree character codepoints (U+251C ├, U+2514 └, U+2502 │, U+2550 ═, box-drawing)
TREE_CHAR_REGEX = re.compile(r"[├└│╔╗╚╝═╠╣╦╩╪╫]")

# Long horizontal line (━ = U+2501, ─ U+2500 run of 4+)
LONG_HORIZ_LINE_REGEX = re.compile(r"━{4,}|─{8,}")

# Template variable pattern: lines that are ONLY a template variable placeholder
_TMPL_VAR_ONLY_LINE = re.compile(r"^\{[^}]+\}\s*$")

# ─── Helpers ─────────────────────────────────────────────────────────────────


def _load_yaml(path: Path) -> Dict[str, Any]:
    """Load a YAML file safely."""
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _all_string_values(data: Any, _depth: int = 0) -> Iterator[str]:
    """Recursively yield all string values from a YAML structure."""
    if _depth > 20:
        return
    if isinstance(data, str):
        yield data
    elif isinstance(data, dict):
        for v in data.values():
            yield from _all_string_values(v, _depth + 1)
    elif isinstance(data, list):
        for item in data:
            yield from _all_string_values(item, _depth + 1)


def _get_template_str(data: Dict[str, Any]) -> Optional[str]:
    """Return the primary 'template' string value from a YAML dict, if present."""
    return data.get("template") if isinstance(data.get("template"), str) else None


def _strip_code_blocks(md_text: str) -> str:
    """Remove fenced and inline code blocks from markdown before applying linting rules."""
    # Remove fenced code blocks first
    stripped = re.sub(r"```[^`]*?```", "", md_text, flags=re.DOTALL)
    # Remove inline code spans so backtick-quoted examples (e.g. `├─`) are ignored
    stripped = re.sub(r"`[^`\n]+`", "", stripped)
    return stripped


def _is_template_var_line(line: str) -> bool:
    """Return True if the line is purely a template variable placeholder like {summary}."""
    return bool(_TMPL_VAR_ONLY_LINE.match(line))


def _template_lines_without_vars(template: str) -> List[Tuple[int, str]]:
    """Return (line_number, line) pairs for non-placeholder lines."""
    return [
        (i, line)
        for i, line in enumerate(template.splitlines(), 1)
        if not _is_template_var_line(line)
    ]


def _get_atom_files() -> List[Path]:
    return sorted(ATOMS_DIR.glob("*.yaml"))


def _get_block_files() -> List[Path]:
    return sorted(BLOCKS_DIR.glob("*.yaml"))


def _get_composition_files() -> List[Path]:
    return sorted(COMPOSITIONS_DIR.glob("*.yaml"))


def _all_template_yaml_files() -> List[Path]:
    return sorted(TEMPLATES_DIR.rglob("*.yaml"))


# ─────────────────────────────────────────────────────────────────────────────
# Rule 1 — No Tree Characters (Global: all YAML files)
# ─────────────────────────────────────────────────────────────────────────────


class TestNoTreeCharacters:
    """Rule 1: No ├─ └─ │ box-drawing characters in any template YAML."""

    def test_atoms_have_no_tree_characters(self) -> None:
        """Rule 1: Atoms must not contain tree/box-drawing characters."""
        violations: List[str] = []
        for path in _get_atom_files():
            data = _load_yaml(path)
            for value in _all_string_values(data):
                if TREE_CHAR_REGEX.search(value):
                    violations.append(f"{path.name}: contains tree/box chars")
                    break
        assert not violations, (
            f"Tree characters (├└│) found in atoms — Rule 1 violation:\n"
            + "\n".join(violations)
        )

    def test_blocks_have_no_tree_characters(self) -> None:
        """Rule 1: Blocks must not contain tree/box-drawing characters."""
        violations: List[str] = []
        for path in _get_block_files():
            data = _load_yaml(path)
            for value in _all_string_values(data):
                if TREE_CHAR_REGEX.search(value):
                    violations.append(f"{path.name}: contains tree/box chars")
                    break
        assert not violations, (
            f"Tree characters found in blocks — Rule 1 violation:\n"
            + "\n".join(violations)
        )

    def test_compositions_have_no_tree_characters(self) -> None:
        """Rule 1: Compositions must not contain tree/box-drawing characters."""
        violations: List[str] = []
        for path in _get_composition_files():
            data = _load_yaml(path)
            for value in _all_string_values(data):
                if TREE_CHAR_REGEX.search(value):
                    violations.append(f"{path.name}: contains tree/box chars")
                    break
        assert not violations, (
            f"Tree characters found in compositions — Rule 1 violation:\n"
            + "\n".join(violations)
        )

    def test_response_templates_md_has_no_tree_chars_outside_code_blocks(self) -> None:
        """Rule 1: cortex-response-templates.md must not use tree chars outside code blocks."""
        assert RESPONSE_TEMPLATES_MD.exists(), (
            f"cortex-response-templates.md not found at {RESPONSE_TEMPLATES_MD}"
        )
        clean_text = _strip_code_blocks(RESPONSE_TEMPLATES_MD.read_text(encoding="utf-8"))
        match = TREE_CHAR_REGEX.search(clean_text)
        assert match is None, (
            f"Tree/box-drawing characters found outside code blocks in "
            f"cortex-response-templates.md at position {match.start()}: "
            f"'{clean_text[max(0, match.start()-20):match.end()+20]}'"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Rule 3 — No Long Horizontal Lines (━━━━)
# ─────────────────────────────────────────────────────────────────────────────


class TestNoLongHorizontalLines:
    """Rule 3: No long horizontal lines (━━━━ or ─────────) in any template."""

    def test_all_template_yamls_have_no_long_horizontal_lines(self) -> None:
        """Rule 3: No ━━━━ or ─────────(8+) in any YAML template file."""
        violations: List[str] = []
        for path in _all_template_yaml_files():
            data = _load_yaml(path)
            for value in _all_string_values(data):
                if LONG_HORIZ_LINE_REGEX.search(value):
                    violations.append(f"{path.name}: long horizontal line found")
                    break
        assert not violations, (
            f"Long horizontal lines found — Rule 3 violation:\n"
            + "\n".join(violations)
        )

    def test_response_templates_md_has_no_long_horiz_lines_outside_code_blocks(self) -> None:
        """Rule 3: cortex-response-templates.md must not use ━━━━ outside code blocks."""
        assert RESPONSE_TEMPLATES_MD.exists()
        clean_text = _strip_code_blocks(RESPONSE_TEMPLATES_MD.read_text(encoding="utf-8"))
        match = LONG_HORIZ_LINE_REGEX.search(clean_text)
        assert match is None, (
            f"Long horizontal line found in cortex-response-templates.md outside code "
            f"blocks: '{clean_text[max(0, match.start()-10):match.end()+10]}'"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Rule 4 — Max 5 Table Columns
# ─────────────────────────────────────────────────────────────────────────────


class TestMaxFiveTableColumns:
    """Rule 4: Tables must have at most 5 columns (≤ 6 pipe chars in header row)."""

    @staticmethod
    def _max_columns_in_template(template: str) -> int:
        """Return maximum column count from any table header row in the template."""
        max_cols = 0
        lines = template.splitlines()
        for i, line in enumerate(lines):
            # A table header row has | at both ends and is followed by a separator |---|
            if line.startswith("|") and "|" in line[1:]:
                if i + 1 < len(lines) and re.match(r"\|[-: |]+\|", lines[i + 1]):
                    cols = line.count("|") - 1  # pipes - 1 = columns
                    max_cols = max(max_cols, cols)
        return max_cols

    def test_composition_templates_max_5_columns(self) -> None:
        """Rule 4: Composition template strings must not exceed 5 table columns."""
        violations: List[str] = []
        for path in _get_composition_files():
            data = _load_yaml(path)
            for key in ["template", "template_ai_spark_variant"]:
                tmpl = data.get(key)
                if not isinstance(tmpl, str):
                    continue
                max_cols = self._max_columns_in_template(tmpl)
                if max_cols > 5:
                    violations.append(
                        f"{path.name} ({key}): {max_cols} columns in a table"
                    )
        assert not violations, (
            f"Tables exceed 5-column limit — Rule 4 violation:\n"
            + "\n".join(violations)
        )

    def test_block_templates_max_5_columns(self) -> None:
        """Rule 4: Block template strings must not exceed 5 table columns."""
        violations: List[str] = []
        for path in _get_block_files():
            data = _load_yaml(path)
            tmpl = _get_template_str(data)
            if not tmpl:
                continue
            max_cols = self._max_columns_in_template(tmpl)
            if max_cols > 5:
                violations.append(f"{path.name}: {max_cols} columns in a table")
        assert not violations, (
            f"Block templates exceed 5-column limit — Rule 4 violation:\n"
            + "\n".join(violations)
        )


# ─────────────────────────────────────────────────────────────────────────────
# R6 — Single H1 per Composition Template
# ─────────────────────────────────────────────────────────────────────────────


class TestSingleH1PerComposition:
    """R6: Each composition template must contain at most one H1 (# heading)."""

    def test_composition_templates_have_single_h1(self) -> None:
        """R6: Each comp-*.yaml template must have at most one H1 heading."""
        violations: List[str] = []
        for path in _get_composition_files():
            data = _load_yaml(path)
            for key in ["template", "template_ai_spark_variant"]:
                tmpl = data.get(key)
                if not isinstance(tmpl, str):
                    continue
                h1_lines = [
                    line for line in tmpl.splitlines()
                    if re.match(r"^# [^#]", line)
                ]
                if len(h1_lines) > 1:
                    violations.append(
                        f"{path.name} ({key}): {len(h1_lines)} H1 headings found"
                    )
        assert not violations, (
            f"Multiple H1 headings found in composition templates — R6 violation:\n"
            + "\n".join(violations)
        )

    def test_composition_rendering_rules_declare_single_h1(self) -> None:
        """R6: Compositions that declare 'single_h1' must set it to true."""
        violations: List[str] = []
        for path in _get_composition_files():
            data = _load_yaml(path)
            rr = data.get("rendering_rules", {})
            if "single_h1" in rr and rr["single_h1"] is not True:
                violations.append(f"{path.name}: single_h1 is declared but not true")
        assert not violations, (
            f"Compositions declare single_h1:false — R6 violation:\n"
            + "\n".join(violations)
        )


# ─────────────────────────────────────────────────────────────────────────────
# R1 — Blank Line After Headings (composition templates only)
# ─────────────────────────────────────────────────────────────────────────────


class TestBlankLineAfterHeadings:
    """R1: Blank line required after every ## / ### heading in composition templates."""

    def test_composition_templates_r1_blank_line_after_headings(self) -> None:
        """R1: No ## heading immediately followed by non-blank, non-variable content."""
        violations: List[str] = []
        for path in _get_composition_files():
            data = _load_yaml(path)
            for key in ["template", "template_ai_spark_variant"]:
                tmpl = data.get(key)
                if not isinstance(tmpl, str):
                    continue
                lines = tmpl.splitlines()
                for i, line in enumerate(lines):
                    if not re.match(r"^##+ ", line):
                        continue
                    if i + 1 >= len(lines):
                        continue
                    next_line = lines[i + 1]
                    # Blank line or template-variable-only line: both OK
                    if next_line.strip() == "" or _is_template_var_line(next_line):
                        continue
                    violations.append(
                        f"{path.name} ({key}) line {i+1}: heading "
                        f"'{line.strip()[:50]}' not followed by blank line "
                        f"(got '{next_line.strip()[:40]}')"
                    )
        assert not violations, (
            f"Headings not followed by blank line — R1 violation:\n"
            + "\n".join(violations)
        )


# ─────────────────────────────────────────────────────────────────────────────
# R4 — No Empty Headers (composition templates)
# ─────────────────────────────────────────────────────────────────────────────


class TestNoEmptyHeaders:
    """R4: No H2/H3 heading immediately followed by another heading (empty section)."""

    def test_composition_templates_no_empty_headers(self) -> None:
        """R4: A ## / ### heading must not be immediately followed by another heading."""
        violations: List[str] = []
        for path in _get_composition_files():
            data = _load_yaml(path)
            for key in ["template", "template_ai_spark_variant"]:
                tmpl = data.get(key)
                if not isinstance(tmpl, str):
                    continue
                lines = [l for l in tmpl.splitlines()]
                for i, line in enumerate(lines):
                    if not re.match(r"^##+ ", line):
                        continue
                    # Scan forward skipping blank lines
                    j = i + 1
                    while j < len(lines) and lines[j].strip() == "":
                        j += 1
                    if j < len(lines) and re.match(r"^#+ ", lines[j]):
                        violations.append(
                            f"{path.name} ({key}) line {i+1}: heading "
                            f"'{line.strip()[:50]}' immediately followed by "
                            f"another heading '{lines[j].strip()[:40]}' — R4"
                        )
        assert not violations, (
            f"Empty headers found in composition templates — R4 violation:\n"
            + "\n".join(violations)
        )


# ─────────────────────────────────────────────────────────────────────────────
# R5 — No Hard-Wrap Within Paragraphs (composition templates)
# ─────────────────────────────────────────────────────────────────────────────


class TestNoHardWrapParagraphs:
    """R5: Do not insert a newline inside prose (hard-wrap breaks paragraph rendering)."""

    # Pattern: lowercase/comma end of line, then lowercase at start of next line
    _HARD_WRAP_RE = re.compile(r"[a-z,]\n[a-z]")

    def test_composition_templates_no_hard_wrap_in_prose(self) -> None:
        """R5: No hard-wrapped prose lines in composition templates."""
        violations: List[str] = []
        for path in _get_composition_files():
            data = _load_yaml(path)
            for key in ["template", "template_ai_spark_variant"]:
                tmpl = data.get(key)
                if not isinstance(tmpl, str):
                    continue
                match = self._HARD_WRAP_RE.search(tmpl)
                if match:
                    snippet = tmpl[max(0, match.start()-10):match.end()+10]
                    violations.append(
                        f"{path.name} ({key}): hard-wrapped prose detected "
                        f"near '{snippet.strip()[:60]}'"
                    )
        assert not violations, (
            f"Hard-wrapped paragraphs found — R5 violation:\n"
            + "\n".join(violations)
        )


# ─────────────────────────────────────────────────────────────────────────────
# DECL — Rendering Rules Declaration (atoms, blocks, compositions)
# ─────────────────────────────────────────────────────────────────────────────


class TestAllAtomsComply:
    """Atoms must declare copilot_chat_compatible and a forbidden list."""

    def test_all_atoms_declare_copilot_chat_compatible(self) -> None:
        """Atoms must have rendering_rules.copilot_chat_compatible: true."""
        violations: List[str] = []
        for path in _get_atom_files():
            data = _load_yaml(path)
            rr = data.get("rendering_rules", {})
            if rr.get("copilot_chat_compatible") is not True:
                violations.append(f"{path.name}: copilot_chat_compatible not true")
        assert not violations, (
            f"Atoms missing copilot_chat_compatible: true:\n" + "\n".join(violations)
        )

    def test_all_atoms_have_no_raw_tree_characters_in_templates(self) -> None:
        """Atoms must not produce tree characters in their template strings."""
        violations: List[str] = []
        for path in _get_atom_files():
            data = _load_yaml(path)
            tmpl = _get_template_str(data)
            if tmpl and TREE_CHAR_REGEX.search(tmpl):
                violations.append(f"{path.name}: tree chars in template")
        assert not violations, "\n".join(violations)


class TestAllBlocksComply:
    """Blocks must declare copilot_chat_compatible and a forbidden list."""

    def test_all_blocks_declare_copilot_chat_compatible(self) -> None:
        """Blocks must have rendering_rules.copilot_chat_compatible: true."""
        violations: List[str] = []
        for path in _get_block_files():
            data = _load_yaml(path)
            rr = data.get("rendering_rules", {})
            if rr.get("copilot_chat_compatible") is not True:
                violations.append(f"{path.name}: copilot_chat_compatible not true")
        assert not violations, (
            f"Blocks missing copilot_chat_compatible: true:\n" + "\n".join(violations)
        )

    def test_all_blocks_declare_forbidden_tree_characters(self) -> None:
        """Blocks must list tree characters in their rendering_rules.forbidden list."""
        violations: List[str] = []
        for path in _get_block_files():
            data = _load_yaml(path)
            rr = data.get("rendering_rules", {})
            forbidden = rr.get("forbidden", [])
            if not isinstance(forbidden, list):
                violations.append(f"{path.name}: rendering_rules.forbidden not a list")
                continue
            forbidden_str = " ".join(str(f) for f in forbidden)
            if "tree" not in forbidden_str.lower():
                violations.append(
                    f"{path.name}: forbidden list does not mention tree characters"
                )
        assert not violations, "\n".join(violations)


class TestAllCompositionsComply:
    """Compositions must declare the key rendering rules."""

    def test_all_compositions_declare_copilot_chat_compatible(self) -> None:
        """Compositions must have rendering_rules.copilot_chat_compatible: true."""
        violations: List[str] = []
        for path in _get_composition_files():
            data = _load_yaml(path)
            rr = data.get("rendering_rules", {})
            if rr.get("copilot_chat_compatible") is not True:
                violations.append(f"{path.name}: copilot_chat_compatible not true")
        assert not violations, "\n".join(violations)

    def test_all_compositions_declare_forbidden_tree_characters(self) -> None:
        """Compositions must list tree characters in their forbidden list."""
        violations: List[str] = []
        for path in _get_composition_files():
            data = _load_yaml(path)
            rr = data.get("rendering_rules", {})
            forbidden = rr.get("forbidden", [])
            if not isinstance(forbidden, list):
                violations.append(f"{path.name}: forbidden not a list")
                continue
            forbidden_str = " ".join(str(f) for f in forbidden)
            if "tree" not in forbidden_str.lower():
                violations.append(
                    f"{path.name}: forbidden does not mention tree characters"
                )
        assert not violations, "\n".join(violations)

    def test_all_compositions_have_template_field(self) -> None:
        """All composition YAMLs must define at least one 'template' field."""
        violations: List[str] = []
        for path in _get_composition_files():
            data = _load_yaml(path)
            # Accept 'template' or 'template_*' variants
            has_template = any(k.startswith("template") for k in data)
            if not has_template:
                violations.append(f"{path.name}: no template field defined")
        assert not violations, "\n".join(violations)


# ─────────────────────────────────────────────────────────────────────────────
# cortex-response-templates.md — Structural Checks
# ─────────────────────────────────────────────────────────────────────────────


class TestResponseTemplatesMdComplies:
    """cortex-response-templates.md must exist and comply with structural rules."""

    def test_response_templates_md_exists(self) -> None:
        """cortex-response-templates.md must exist at .github/templates/."""
        assert RESPONSE_TEMPLATES_MD.exists(), (
            f"cortex-response-templates.md not found at {RESPONSE_TEMPLATES_MD}"
        )

    def test_response_templates_md_declares_mandatory_rendering_rules_section(self) -> None:
        """cortex-response-templates.md must contain the Mandatory Rendering Rules section."""
        content = RESPONSE_TEMPLATES_MD.read_text(encoding="utf-8")
        assert "Mandatory Rendering Rules" in content, (
            "cortex-response-templates.md missing 'Mandatory Rendering Rules' section"
        )

    def test_response_templates_md_mentions_tree_character_ban(self) -> None:
        """cortex-response-templates.md must document that tree characters are banned."""
        content = RESPONSE_TEMPLATES_MD.read_text(encoding="utf-8")
        has_tree_ban = "tree" in content.lower() and (
            "├" in content or "─" in content or "U+251C" in content
        )
        assert has_tree_ban, (
            "cortex-response-templates.md does not document the tree character ban"
        )

    def test_response_templates_md_mentions_single_h1_rule(self) -> None:
        """cortex-response-templates.md must document the single-H1 rule (R6)."""
        content = RESPONSE_TEMPLATES_MD.read_text(encoding="utf-8")
        assert "R6" in content or "One H1" in content or "single H1" in content.lower(), (
            "cortex-response-templates.md does not document the single-H1 rule (R6)"
        )

    def test_response_templates_md_no_tree_chars_in_prose(self) -> None:
        """Tree characters must not appear outside code blocks in the template doc."""
        clean_text = _strip_code_blocks(
            RESPONSE_TEMPLATES_MD.read_text(encoding="utf-8")
        )
        match = TREE_CHAR_REGEX.search(clean_text)
        assert match is None, (
            f"Tree/box chars in cortex-response-templates.md prose: "
            f"'{clean_text[max(0, match.start()-15):match.end()+15]}'"
        )
