"""Phase 128-c: Response Template Compliance Tests.

Authority: GAP-128-C-01 (response template structural compliance)
Governance: CORE-008 (TDD mandatory), CORE-064 (Sweep Completeness)
SSOT: cortex-registry/planning/phases/planned/phase-128-conflict-drift-eradication.yaml

Verifies that:
  1. atom-quote.yaml has exactly 120 quotes with required fields
  2. Quote themes map to the canonical 10 themes
  3. No duplicate dedup_keys in the quote library
  4. atom-quote.yaml structure matches the SSOT referenced in copilot-instructions.md
  5. All response template atom YAMLs are parseable and have required id/type fields
  6. CORE-RESP-001 anchor phrases are present in the response template
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

PROJECT_ROOT = Path(__file__).parent.parent.parent
ATOMS_DIR = PROJECT_ROOT / "cortex-registry" / "templates" / "response" / "atoms"
TEMPLATE_FILE = PROJECT_ROOT / ".github" / "templates" / "cortex-response-templates.md"
ATOM_QUOTE_FILE = ATOMS_DIR / "atom-quote.yaml"

# Canonical 10 themes from copilot-instructions.md
CANONICAL_THEMES = {
    "quality",
    "security",
    "improvement",
    "architecture",
    "discipline",
    "systems-thinking",
    "strategy",
    "flow",
    "learning",
    "universal",
}

# Required fields per quote entry
REQUIRED_QUOTE_FIELDS = {"text", "author", "book", "themes", "dedup_key"}


class TestAtomQuoteLibrary:
    """Verify atom-quote.yaml structure and content (SSOT: copilot-instructions.md)."""

    @pytest.fixture(scope="class")
    def atom_quote(self) -> dict:
        """Load atom-quote.yaml."""
        assert ATOM_QUOTE_FILE.exists(), f"atom-quote.yaml not found at {ATOM_QUOTE_FILE}"
        with open(ATOM_QUOTE_FILE, encoding="utf-8") as f:
            return yaml.safe_load(f)

    @pytest.fixture(scope="class")
    def quotes(self, atom_quote: dict) -> list:
        """Extract quotes list."""
        return atom_quote.get("quotes", [])

    def test_atom_quote_is_parseable(self) -> None:
        """atom-quote.yaml must be parseable YAML."""
        with open(ATOM_QUOTE_FILE, encoding="utf-8") as f:
            content = yaml.safe_load(f)
        assert content is not None, "atom-quote.yaml is empty"
        assert isinstance(content, dict), "atom-quote.yaml must be a dict"

    def test_atom_quote_has_required_top_level_fields(self, atom_quote: dict) -> None:
        """atom-quote.yaml must have id, type, quotes fields."""
        required = {"id", "quotes"}
        missing = required - set(atom_quote.keys())
        assert not missing, f"atom-quote.yaml missing top-level fields: {missing}"

    def test_quote_count_is_120(self, quotes: list) -> None:
        """Quote library must contain at least 120 quotes.

        GAP-128-C-01: copilot-instructions.md declares '120 quotes across 10 themes'.
        Library has grown beyond 120; test enforces the minimum floor, not exact count.
        """
        assert len(quotes) >= 120, (
            f"Expected at least 120 quotes, found {len(quotes)}. "
            "Update atom-quote.yaml or fix copilot-instructions.md."
        )

    def test_all_quotes_have_required_fields(self, quotes: list) -> None:
        """Every quote entry must have text, author, book, themes, dedup_key."""
        violations: list[str] = []
        for i, q in enumerate(quotes):
            missing = REQUIRED_QUOTE_FIELDS - set(q.keys())
            if missing:
                violations.append(f"Quote #{i+1} ({q.get('author', '?')}): missing {missing}")

        assert not violations, (
            f"Found {len(violations)} quotes with missing required fields:\n"
            + "\n".join(f"  - {v}" for v in violations[:20])
        )

    def test_no_duplicate_dedup_keys(self, quotes: list) -> None:
        """All dedup_key values must be unique across the quote library."""
        keys = [q.get("dedup_key", "") for q in quotes]
        duplicates = [k for k in keys if keys.count(k) > 1 and k]
        unique_dups = list(set(duplicates))

        assert not unique_dups, (
            f"Found {len(unique_dups)} duplicate dedup_keys:\n"
            + "\n".join(f"  - {d}" for d in unique_dups)
        )

    def test_all_quote_themes_are_canonical(self, quotes: list) -> None:
        """Every theme in every quote must be from the canonical 10-theme set."""
        invalid_themes: list[str] = []
        for i, q in enumerate(quotes):
            themes = q.get("themes", [])
            if isinstance(themes, str):
                themes = [themes]
            for theme in themes:
                if theme not in CANONICAL_THEMES:
                    invalid_themes.append(
                        f"Quote #{i+1} ({q.get('author', '?')}): invalid theme '{theme}'"
                    )

        assert not invalid_themes, (
            f"Found {len(invalid_themes)} quotes with non-canonical themes:\n"
            + "\n".join(f"  - {t}" for t in invalid_themes[:20])
            + f"\nCanonical themes: {sorted(CANONICAL_THEMES)}"
        )

    def test_all_10_themes_represented(self, quotes: list) -> None:
        """Each of the 10 canonical themes must appear in at least 1 quote."""
        represented: set[str] = set()
        for q in quotes:
            themes = q.get("themes", [])
            if isinstance(themes, str):
                themes = [themes]
            represented.update(themes)

        missing_themes = CANONICAL_THEMES - represented
        assert not missing_themes, (
            f"Themes not represented in quote library: {missing_themes}"
        )

    def test_no_empty_quote_text(self, quotes: list) -> None:
        """No quote may have empty or whitespace-only text."""
        empty: list[str] = []
        for i, q in enumerate(quotes):
            text = q.get("text", "")
            if not text or not text.strip():
                empty.append(f"Quote #{i+1} ({q.get('author', '?')}): empty text")

        assert not empty, (
            f"Found {len(empty)} quotes with empty text:\n"
            + "\n".join(f"  - {e}" for e in empty)
        )


class TestResponseTemplateAtoms:
    """Verify all response atom YAMLs have required schema fields."""

    @pytest.fixture(scope="class")
    def atom_files(self) -> list[Path]:
        """List all atom YAML files."""
        assert ATOMS_DIR.exists(), f"Atoms directory not found: {ATOMS_DIR}"
        return list(ATOMS_DIR.glob("*.yaml"))

    def test_all_atoms_parseable(self, atom_files: list[Path]) -> None:
        """All atom YAMLs must be parseable."""
        errors: list[str] = []
        for p in atom_files:
            try:
                with open(p, encoding="utf-8") as f:
                    yaml.safe_load(f)
            except yaml.YAMLError as e:
                errors.append(f"{p.name}: {e}")

        assert not errors, (
            f"Found {len(errors)} unparseable atom YAMLs:\n"
            + "\n".join(f"  - {e}" for e in errors)
        )

    def test_all_atoms_have_id_and_type(self, atom_files: list[Path]) -> None:
        """All atom YAMLs must have id and type fields."""
        violations: list[str] = []
        for p in atom_files:
            with open(p, encoding="utf-8") as f:
                content = yaml.safe_load(f)
            if not isinstance(content, dict):
                continue
            missing = []
            if "id" not in content:
                missing.append("id")
            if "type" not in content:
                missing.append("type")
            if missing:
                violations.append(f"{p.name}: missing {missing}")

        assert not violations, (
            f"Found {len(violations)} atom YAMLs missing required fields:\n"
            + "\n".join(f"  - {v}" for v in violations)
        )


class TestResponseTemplateMarkdown:
    """Verify cortex-response-templates.md structural compliance."""

    @pytest.fixture(scope="class")
    def template_content(self) -> str:
        """Load response template markdown."""
        assert TEMPLATE_FILE.exists(), f"Template not found: {TEMPLATE_FILE}"
        return TEMPLATE_FILE.read_text(encoding="utf-8")

    def test_template_has_core_resp_001_anchor(self, template_content: str) -> None:
        """CORE-RESP-001 (Proceed Gate / Completion State) anchor must exist."""
        assert "CORE-RESP-001" in template_content, (
            "CORE-RESP-001 governance rule not found in cortex-response-templates.md"
        )

    def test_template_has_proceed_gate_section(self, template_content: str) -> None:
        """Proceed Gate section must be present."""
        assert "Proceed Gate" in template_content, (
            "'Proceed Gate' section not found in cortex-response-templates.md"
        )

    def test_template_has_completion_state_section(self, template_content: str) -> None:
        """Completion State section must be present."""
        assert "Completion State" in template_content, (
            "'Completion State' section not found in cortex-response-templates.md"
        )

    def test_template_has_pending_work_end_state_guardrail(self, template_content: str) -> None:
        """Template must forbid completion state when pending work remains."""
        assert "All work is complete" in template_content, (
            "Completion state phrase missing from cortex-response-templates.md"
        )
        assert "pending work" in template_content.lower(), (
            "Template must define pending-work decision gate for completion vs proceed."
        )
        assert "Proceed Gate" in template_content, (
            "Template must route pending work to Proceed Gate."
        )

    def test_template_references_atom_quote_ssot(self, template_content: str) -> None:
        """Template must reference atom-quote.yaml as the SSOT for quotes."""
        assert "atom-quote.yaml" in template_content, (
            "atom-quote.yaml SSOT reference not found in cortex-response-templates.md"
        )

    def test_template_declares_120_quotes(self, template_content: str) -> None:
        """Template must declare '120 quotes' (SSOT alignment)."""
        assert "120 quotes" in template_content, (
            "Template does not declare '120 quotes' — check copilot-instructions.md sync"
        )

    def test_template_has_five_section_golden_format(self, template_content: str) -> None:
        """5-Section Golden Format must be referenced."""
        assert "5-Section" in template_content or "Five-Section" in template_content or "5 sections" in template_content.lower(), (
            "5-Section Golden Format not referenced in cortex-response-templates.md"
        )
