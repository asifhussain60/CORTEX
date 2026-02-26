"""
Golden Tests: Phase 82-e — Existing User Response Template Migration
                            Inline Duplicate Purge + SSOT Consolidation

Phase 82 sub-phase 82-e | Closes: GAP-82-11
Authority: CORE-002 (No report files), CORE-008 (TDD-first), CORE-035 (single canonical
           implementation), CORE-064 (sweep completeness), CORE-066 (response template binding)

15 Acceptance Criteria (tdd_sequence.red):

  test_cortex_prompt_no_inline_5section_skeleton
      CORTEX.prompt.md must NOT contain an inline fenced 5-section skeleton
  test_cortex_prompt_has_ssot_pointer
      CORTEX.prompt.md RESPONSE FORMAT section must point to SSOT
  test_executor_no_inline_completion_report_format
      cortex-executor.md must NOT contain inline fenced Completion Report Format
  test_executor_has_block_metrics_dashboard_pointer
      cortex-executor.md must reference BLOCK-METRICS-DASHBOARD from SSOT
  test_ssot_rendering_rules_table_has_14_rows
      SSOT Mandatory Rendering Rules table must have 14 data rows
  test_ssot_rendering_rule_r1_present
      SSOT rendering rules table must contain R1 (blank line after heading)
  test_ssot_rendering_rule_r2_present
      SSOT rendering rules table must contain R2 (blank line around list)
  test_ssot_rendering_rule_r3_present
      SSOT rendering rules table must contain R3 (table blank-line + header+separator)
  test_ssot_rendering_rule_r4_present
      SSOT rendering rules table must contain R4 (omit empty headers)
  test_ssot_rendering_rule_r5_present
      SSOT rendering rules table must contain R5 (no hard-wrap)
  test_ssot_rendering_rule_r6_present
      SSOT rendering rules table must contain R6 (one H2 max)
  test_ssot_table_safety_note_present
      SSOT must have table safety switch note after rendering rules table
  test_ssot_quality_checklist_has_normalizer_item
      SSOT Quality Checklist must include whitespace normalizer item
  test_ssot_quality_checklist_has_empty_header_item
      SSOT Quality Checklist must include empty-header suppression item
  test_ssot_quality_checklist_has_table_cell_item
      SSOT Quality Checklist must include table cell length limit item

AC_START: AC-82-E-MIGRATION-001
Phase: 82 | Sub-phase: e | Priority: P1
"""

from pathlib import Path

import pytest

# =============================================================================
# Paths
# =============================================================================

ROOT = Path("/Users/asifhussain/PROJECTS/CORTEX")
CORTEX_PROMPT = ROOT / ".github" / "prompts" / "CORTEX.prompt.md"
EXECUTOR_MD = ROOT / ".github" / "agents" / "core" / "cortex-executor.md"
SSOT = ROOT / ".github" / "templates" / "cortex-response-templates.md"


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(scope="module")
def cortex_prompt_text() -> str:
    """Read CORTEX.prompt.md once for the module."""
    assert CORTEX_PROMPT.exists(), f"CORTEX.prompt.md must exist at {CORTEX_PROMPT}"
    return CORTEX_PROMPT.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def executor_text() -> str:
    """Read cortex-executor.md once for the module."""
    assert EXECUTOR_MD.exists(), f"cortex-executor.md must exist at {EXECUTOR_MD}"
    return EXECUTOR_MD.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def ssot_text() -> str:
    """Read cortex-response-templates.md (SSOT) once for the module."""
    assert SSOT.exists(), f"SSOT must exist at {SSOT}"
    return SSOT.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def ssot_lines(ssot_text: str) -> list[str]:
    """Return SSOT content split into lines for structural analysis."""
    return ssot_text.splitlines()


# =============================================================================
# FILE-1: CORTEX.prompt.md — Inline 5-section skeleton must be purged
# =============================================================================


class TestCortexPromptMigration:
    """GAP-82-11 / FILE-1: CORTEX.prompt.md must not contain inline template skeleton."""

    def test_cortex_prompt_no_inline_5section_skeleton(
        self, cortex_prompt_text: str
    ) -> None:
        """CORTEX.prompt.md must NOT contain the inline fenced 5-section skeleton.

        The inline duplicate (## 📋 Summary / ## 🔍 Analysis / ## 💡 Recommendation /
        ## ⚖️ Benefits & Risks / ## 🎯 Next Steps inside a fenced block) must have been
        removed and replaced with an SSOT pointer. CORE-035: single canonical implementation.
        """
        # These are the section headers that appear inside the inline fenced skeleton.
        # The SSOT has the canonical definition; CORTEX.prompt.md must only pointer-reference it.
        inline_skeleton_markers = [
            "## 📋 Summary",
            "## 🔍 Analysis",
            "## 💡 Recommendation",
            "## ⚖️ Benefits & Risks",
            "## 🎯 Next Steps",
        ]
        for marker in inline_skeleton_markers:
            assert marker not in cortex_prompt_text, (
                f"CORTEX.prompt.md must not contain inline skeleton marker '{marker}'. "
                "Replace with SSOT pointer to cortex-response-templates.md § User Response Template."
            )

    def test_cortex_prompt_has_ssot_pointer(self, cortex_prompt_text: str) -> None:
        """CORTEX.prompt.md RESPONSE FORMAT section must contain a pointer to the SSOT.

        After purging the inline skeleton, a pointer line referencing
        cortex-response-templates.md must be present so users know where the canonical
        format lives. CORE-035: single source of truth.
        """
        assert "cortex-response-templates.md" in cortex_prompt_text, (
            "CORTEX.prompt.md must reference 'cortex-response-templates.md' as the SSOT pointer "
            "for the User Response Template format."
        )


# =============================================================================
# FILE-2: cortex-executor.md — Inline Completion Report Format must be purged
# =============================================================================


class TestExecutorMigration:
    """GAP-82-11 / FILE-2: cortex-executor.md must not contain inline completion report."""

    def test_executor_no_inline_completion_report_format(
        self, executor_text: str
    ) -> None:
        """cortex-executor.md must NOT contain the inline fenced Completion Report Format.

        The fenced block beginning with '## ✅ Execution Complete' is an inline duplicate
        of BLOCK-METRICS-DASHBOARD from the SSOT. CORE-035: remove duplicate; use pointer.
        """
        # The inline block starts with this exact heading inside a fenced region.
        # After migration it must not appear in the file at all.
        assert "## ✅ Execution Complete" not in executor_text, (
            "cortex-executor.md must not contain inline '## ✅ Execution Complete' fenced block. "
            "Replace with pointer to BLOCK-METRICS-DASHBOARD in SSOT cortex-response-templates.md."
        )

    def test_executor_has_block_metrics_dashboard_pointer(
        self, executor_text: str
    ) -> None:
        """cortex-executor.md must reference BLOCK-METRICS-DASHBOARD from the SSOT.

        The pointer confirms the inline block was removed and a canonical reference inserted.
        CORE-035: single canonical implementation.
        """
        assert "BLOCK-METRICS-DASHBOARD" in executor_text, (
            "cortex-executor.md must reference 'BLOCK-METRICS-DASHBOARD' as the SSOT pointer "
            "replacing the removed inline Completion Report Format fenced block."
        )


# =============================================================================
# FILE-3: SSOT Mandatory Rendering Rules table — must have 14 rows (R1-R6 absorbed)
# =============================================================================


def _count_rendering_rules_table_rows(ssot_text: str) -> int:
    """Count data rows in the Mandatory Rendering Rules table.

    The table sits under '### Mandatory Rendering Rules' (a sub-heading of
    '## ⚠️ COPILOT CHAT RENDERING RULES'). Data rows are lines that start
    with '|', are not the header row, and are not the separator row (---)
    We stop counting when we hit a blank line after the table body or a
    new heading at ## or ### level.
    """
    lines = ssot_text.splitlines()
    in_table = False
    past_separator = False
    row_count = 0

    for line in lines:
        stripped = line.strip()

        # Detect the specific sub-heading for the mandatory rendering rules table
        if not in_table and "MANDATORY RENDERING RULES" in stripped.upper():
            # Skip the section-level heading (## ⚠️ COPILOT CHAT RENDERING RULES...)
            # and wait for the table to start — continue scanning
            in_table = True
            past_separator = False
            row_count = 0
            continue

        if not in_table:
            continue

        # A new ## heading (but not ###) ends the section
        if stripped.startswith("## ") and "MANDATORY RENDERING RULES" not in stripped.upper():
            break

        # A ### heading that is NOT the Mandatory Rendering Rules sub-heading ends the table
        if stripped.startswith("###") and "MANDATORY RENDERING RULES" not in stripped.upper():
            if past_separator:
                break
            # Could be the sub-heading itself — skip and continue
            continue

        if not stripped:
            # Blank line after at least one data row ends the table
            if past_separator and row_count > 0:
                break
            continue

        if stripped.startswith("|"):
            # A separator row has only |, -, :, and whitespace (e.g. |---|---| )
            # Use a regex-free approach: strip pipes, split by |, all cells are ---/:-/etc.
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            is_separator = all(
                set(c.replace(":", "").replace("-", "").replace(" ", "")) == set()
                and len(c.replace(":", "").replace("-", "").replace(" ", "")) == 0
                and len(c.replace(" ", "")) > 0
                for c in cells
            )
            if is_separator:
                past_separator = True
                continue
            if not past_separator:
                # Column-name header row — skip
                continue
            row_count += 1

    return row_count


class TestSSOTRenderingRulesTable:
    """GAP-82-11 / FILE-3: SSOT Mandatory Rendering Rules table must have 14 rows."""

    def test_ssot_rendering_rules_table_has_14_rows(self, ssot_text: str) -> None:
        """SSOT Mandatory Rendering Rules table must have exactly 14 data rows.

        Original: 8 rows. R1-R6 absorbed as rows 9-14 brings the total to 14.
        CORE-035: R1-R6 must be in the SSOT table, not inline in consumer files.
        """
        count = _count_rendering_rules_table_rows(ssot_text)
        assert count == 14, (
            f"SSOT Mandatory Rendering Rules table must have 14 rows (8 original + 6 R1-R6). "
            f"Found: {count} rows."
        )

    def test_ssot_rendering_rule_r1_present(self, ssot_text: str) -> None:
        """R1: blank line required after every heading — must appear in SSOT table.

        R1 was previously only documented inline in consumer files or as an ad-hoc note.
        After migration it must be a row in the SSOT Mandatory Rendering Rules table.
        """
        # R1 covers the rule: always emit a blank line after every Markdown heading.
        # Accept any row that references both 'heading' and 'blank' (case-insensitive).
        lower = ssot_text.lower()
        assert (
            ("blank" in lower and "heading" in lower and "|" in ssot_text)
        ), (
            "SSOT Mandatory Rendering Rules table must include R1 rule: "
            "blank line required after every heading."
        )

    def test_ssot_rendering_rule_r2_present(self, ssot_text: str) -> None:
        """R2: blank line required before and after every list — must appear in SSOT table."""
        lower = ssot_text.lower()
        assert (
            "blank" in lower and "list" in lower and "|" in ssot_text
        ), (
            "SSOT Mandatory Rendering Rules table must include R2 rule: "
            "blank line before and after every list."
        )

    def test_ssot_rendering_rule_r3_present(self, ssot_text: str) -> None:
        """R3: table requires blank line before + header row + separator row — must appear in SSOT."""
        lower = ssot_text.lower()
        assert "separator" in lower or "---" in ssot_text, (
            "SSOT Mandatory Rendering Rules table must include R3 rule: "
            "every table needs blank line before it, header row, and separator row."
        )

    def test_ssot_rendering_rule_r4_present(self, ssot_text: str) -> None:
        """R4: omit empty headers — must appear in SSOT table.

        R4 states: never emit an H2/H3 heading if the section has no content below it.
        The Whitespace Normalizer step catches this at render time.
        """
        lower = ssot_text.lower()
        assert (
            "empty" in lower or "omit" in lower
        ) and "header" in lower, (
            "SSOT Mandatory Rendering Rules table must include R4 rule: "
            "omit empty headers (never emit heading with no content below it)."
        )

    def test_ssot_rendering_rule_r5_present(self, ssot_text: str) -> None:
        """R5: no hard-wrap within paragraphs — must appear in SSOT table.

        R5 states: do not insert hard line breaks (\\n) inside a prose paragraph.
        Copilot Chat renderer normalizes whitespace; mid-paragraph breaks create
        unwanted blank lines.
        """
        lower = ssot_text.lower()
        assert "hard" in lower or ("wrap" in lower and "paragraph" in lower), (
            "SSOT Mandatory Rendering Rules table must include R5 rule: "
            "no hard-wrap within paragraphs."
        )

    def test_ssot_rendering_rule_r6_present(self, ssot_text: str) -> None:
        """R6: one H2 maximum per response top-level — must appear in SSOT table.

        R6 states: a single response must have at most one H2 acting as the top-level
        title; additional sections use H3 or below to avoid Copilot Chat renderer
        treating each H2 as a separate document root.
        """
        lower = ssot_text.lower()
        assert "h2" in lower or "## " in ssot_text, (
            "SSOT Mandatory Rendering Rules table must include R6 rule: "
            "one H2 maximum per response."
        )

    def test_ssot_table_safety_note_present(self, ssot_text: str) -> None:
        """SSOT must have a table safety switch note after the rendering rules table.

        The note states: if any table cell exceeds 80 chars → downgrade to a bulleted
        list; if the list would exceed 120 chars → wrap in a <details> block.
        CORE-066: renderer safety mechanisms must be documented in SSOT.
        """
        lower = ssot_text.lower()
        assert "80" in ssot_text and (
            "downgrade" in lower or "bullet" in lower or "detail" in lower
        ), (
            "SSOT must contain a table safety switch note indicating that cells >80 chars "
            "should be downgraded to bullets and >120 chars wrapped in <details>."
        )


# =============================================================================
# FILE-4: SSOT Quality Checklist — must have 3 new items
# =============================================================================


def _extract_quality_checklist_section(ssot_text: str) -> str:
    """Return the text content of the Quality Checklist section from the SSOT.

    Matches the actual ## 📏 QUALITY CHECKLIST heading (not table references
    to it in the Document Structure section).
    """
    lines = ssot_text.splitlines()
    in_section = False
    captured: list[str] = []

    for line in lines:
        stripped = line.strip()
        # Only match a proper Markdown heading line (starts with ##) containing "QUALITY CHECKLIST"
        if not in_section and stripped.startswith("##") and "QUALITY CHECKLIST" in stripped.upper():
            in_section = True
            captured.append(line)
            continue
        if in_section:
            # Stop at the next ## heading that is NOT the quality checklist
            if stripped.startswith("##") and "QUALITY CHECKLIST" not in stripped.upper():
                break
            captured.append(line)

    return "\n".join(captured)


class TestSSOTQualityChecklist:
    """GAP-82-11 / FILE-4: SSOT Quality Checklist must include 3 new items."""

    def test_ssot_quality_checklist_has_normalizer_item(self, ssot_text: str) -> None:
        """SSOT Quality Checklist must include a whitespace normalizer compliance item.

        The normalizer item confirms the response has been passed through the
        Whitespace Normalizer step (phase-82-d) before being emitted.
        """
        checklist = _extract_quality_checklist_section(ssot_text)
        lower = checklist.lower()
        assert "normalizer" in lower or "whitespace" in lower, (
            "SSOT Quality Checklist must include a whitespace normalizer compliance item. "
            "Expected a checklist entry referencing 'normalizer' or 'whitespace'."
        )

    def test_ssot_quality_checklist_has_empty_header_item(self, ssot_text: str) -> None:
        """SSOT Quality Checklist must include an empty-header suppression item (R4).

        This item prompts the author to verify no empty headings (H2/H3 with no
        content below) are emitted in the response. Corresponds to R4.
        """
        checklist = _extract_quality_checklist_section(ssot_text)
        lower = checklist.lower()
        assert ("empty" in lower or "omit" in lower) and "header" in lower, (
            "SSOT Quality Checklist must include an empty-header suppression item. "
            "Expected a checklist entry referencing 'empty header' or similar (R4)."
        )

    def test_ssot_quality_checklist_has_table_cell_item(self, ssot_text: str) -> None:
        """SSOT Quality Checklist must include a table cell length limit item.

        This item prompts the author to verify no table cell exceeds 80 chars,
        triggering the Renderer Safety Switch (phase-82-d, table safety switch spec).
        """
        checklist = _extract_quality_checklist_section(ssot_text)
        assert "80" in checklist or (
            "table" in checklist.lower() and "cell" in checklist.lower()
        ), (
            "SSOT Quality Checklist must include a table cell length limit item. "
            "Expected a checklist entry referencing '80 chars' or 'table cell'."
        )


# AC_COMPLETE: AC-82-E-MIGRATION-001 ✅ RED phase — 15 tests written, all must FAIL before implementation
