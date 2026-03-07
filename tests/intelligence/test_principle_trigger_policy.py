"""Tests for principle-trigger-policy.yaml and atom-proceed-principle.yaml (GAP-130-02).

Validates the canonical SSOT governing when and where principle blocks are injected,
and that the new atom-proceed-principle atom exists and is correctly structured.

AC-ID: AC-PTP-001
GAP-REF: GAP-130-02 (Phase 130-b — Foundation Backport)
Governance: CORE-008 (TDD), CORE-035 (single SSOT), CORE-011 (type hints)
"""
from __future__ import annotations

from pathlib import Path

import pytest

# ─── Paths ────────────────────────────────────────────────────────────────────
REGISTRY = Path(__file__).parent.parent.parent / "cortex-registry"
ATOMS_DIR = REGISTRY / "templates" / "response" / "atoms"
CORE_DIR = REGISTRY / "core"

ATOM_PROCEED_PRINCIPLE = ATOMS_DIR / "atom-proceed-principle.yaml"
PRINCIPLE_TRIGGER_POLICY = CORE_DIR / "principle-trigger-policy.yaml"
ATOM_PRINCIPLE = ATOMS_DIR / "atom-principle.yaml"


# ---------------------------------------------------------------------------
# atom-proceed-principle.yaml existence + structure
# ---------------------------------------------------------------------------

class TestAtomProceedPrinciple:
    """atom-proceed-principle.yaml — new Proceed Gate principle atom."""

    def test_file_exists(self) -> None:
        """atom-proceed-principle.yaml must exist in atoms dir."""
        assert ATOM_PROCEED_PRINCIPLE.exists(), (
            f"atom-proceed-principle.yaml not found at {ATOM_PROCEED_PRINCIPLE}"
        )

    def test_valid_yaml(self) -> None:
        """atom-proceed-principle.yaml must be valid YAML."""
        import yaml
        content = ATOM_PROCEED_PRINCIPLE.read_text(encoding="utf-8")
        parsed = yaml.safe_load(content)
        assert isinstance(parsed, dict), "atom-proceed-principle.yaml must parse as a YAML mapping"

    def test_has_required_fields(self) -> None:
        """atom-proceed-principle.yaml must have id, type, and rendering_rules."""
        import yaml
        parsed = yaml.safe_load(ATOM_PROCEED_PRINCIPLE.read_text(encoding="utf-8"))
        for field in ("id", "type", "rendering_rules"):
            assert field in parsed, f"Missing required field '{field}' in atom-proceed-principle.yaml"

    def test_id_matches_filename(self) -> None:
        """The id field must match the filename stem."""
        import yaml
        parsed = yaml.safe_load(ATOM_PROCEED_PRINCIPLE.read_text(encoding="utf-8"))
        assert parsed.get("id") == "atom-proceed-principle", (
            "id field must be 'atom-proceed-principle'"
        )

    def test_type_is_atom(self) -> None:
        """type field must be 'atom'."""
        import yaml
        parsed = yaml.safe_load(ATOM_PROCEED_PRINCIPLE.read_text(encoding="utf-8"))
        assert parsed.get("type") == "atom"

    def test_copilot_chat_compatible(self) -> None:
        """rendering_rules.copilot_chat_compatible must be True."""
        import yaml
        parsed = yaml.safe_load(ATOM_PROCEED_PRINCIPLE.read_text(encoding="utf-8"))
        rendering = parsed.get("rendering_rules", {})
        assert rendering.get("copilot_chat_compatible") is True

    def test_omit_in_proceed_gate_false(self) -> None:
        """The atom must declare it renders inside the Proceed Gate (not omitted there)."""
        import yaml
        parsed = yaml.safe_load(ATOM_PROCEED_PRINCIPLE.read_text(encoding="utf-8"))
        # atom-proceed-principle must NOT appear in atom-principle's Proceed Gate omit list
        # Validate via its own rendering_rules.position referencing the Proceed Gate
        rendering = parsed.get("rendering_rules", {})
        zone = rendering.get("zone", "")
        assert "proceed" in zone.lower() or "proceed" in str(parsed.get("position", "")).lower(), (
            "atom-proceed-principle must declare its zone references the Proceed Gate section"
        )

    def test_has_template_field(self) -> None:
        """atom-proceed-principle must have a template field."""
        import yaml
        parsed = yaml.safe_load(ATOM_PROCEED_PRINCIPLE.read_text(encoding="utf-8"))
        assert "template" in parsed, "template field missing from atom-proceed-principle.yaml"

    def test_template_contains_principle_placeholder(self) -> None:
        """template must contain {title} and {body} placeholders."""
        import yaml
        parsed = yaml.safe_load(ATOM_PROCEED_PRINCIPLE.read_text(encoding="utf-8"))
        template = parsed.get("template", "")
        assert "{title}" in template, "template must contain {title} placeholder"
        assert "{body}" in template, "template must contain {body} placeholder"


# ---------------------------------------------------------------------------
# principle-trigger-policy.yaml SSOT integrity
# ---------------------------------------------------------------------------

class TestPrincipleTriggerPolicy:
    """principle-trigger-policy.yaml — canonical trigger SSOT."""

    def test_file_exists(self) -> None:
        """principle-trigger-policy.yaml must exist in cortex-registry/core/."""
        assert PRINCIPLE_TRIGGER_POLICY.exists(), (
            f"principle-trigger-policy.yaml not found at {PRINCIPLE_TRIGGER_POLICY}"
        )

    def test_valid_yaml(self) -> None:
        """principle-trigger-policy.yaml must be valid YAML."""
        import yaml
        content = PRINCIPLE_TRIGGER_POLICY.read_text(encoding="utf-8")
        parsed = yaml.safe_load(content)
        assert isinstance(parsed, dict)

    def test_has_id_field(self) -> None:
        """Must have a top-level 'id' field."""
        import yaml
        parsed = yaml.safe_load(PRINCIPLE_TRIGGER_POLICY.read_text(encoding="utf-8"))
        assert "id" in parsed

    def test_has_intent_categories(self) -> None:
        """Must define intent_categories mapping."""
        import yaml
        parsed = yaml.safe_load(PRINCIPLE_TRIGGER_POLICY.read_text(encoding="utf-8"))
        assert "intent_categories" in parsed

    def test_analysis_category_enables_injection(self) -> None:
        """The 'analysis' category must have principle_injection: true."""
        import yaml
        parsed = yaml.safe_load(PRINCIPLE_TRIGGER_POLICY.read_text(encoding="utf-8"))
        analysis = parsed["intent_categories"].get("analysis", {})
        assert analysis.get("principle_injection") is True

    def test_operations_category_disables_injection(self) -> None:
        """The 'operations' category must have principle_injection: false."""
        import yaml
        parsed = yaml.safe_load(PRINCIPLE_TRIGGER_POLICY.read_text(encoding="utf-8"))
        ops = parsed["intent_categories"].get("operations", {})
        assert ops.get("principle_injection") is False

    def test_design_category_enables_injection(self) -> None:
        """The 'design' category must have principle_injection: true."""
        import yaml
        parsed = yaml.safe_load(PRINCIPLE_TRIGGER_POLICY.read_text(encoding="utf-8"))
        design = parsed["intent_categories"].get("design", {})
        assert design.get("principle_injection") is True

    def test_operational_intents_do_not_inject(self) -> None:
        """IMPLEMENT, FIX, REFACTOR, DEBUG, AUDIT must not be in injection-enabled categories."""
        import yaml
        parsed = yaml.safe_load(PRINCIPLE_TRIGGER_POLICY.read_text(encoding="utf-8"))
        injection_enabled_intents: set = set()
        for cat_data in parsed["intent_categories"].values():
            if cat_data.get("principle_injection") is True:
                injection_enabled_intents.update(cat_data.get("intents", []))
        forbidden_in_injection = {"IMPLEMENT", "FIX", "REFACTOR", "DEBUG", "AUDIT"}
        overlap = forbidden_in_injection & injection_enabled_intents
        assert not overlap, (
            f"These operational intents must NOT be in injection-enabled categories: {overlap}"
        )

    def test_has_complexity_gate_config(self) -> None:
        """Must declare a complexity gate — either 'brevity' or a 'complexity_gate' key."""
        import yaml
        parsed = yaml.safe_load(PRINCIPLE_TRIGGER_POLICY.read_text(encoding="utf-8"))
        has_brevity = "brevity" in parsed
        has_complexity = "complex_query_min_words" in str(parsed)  # nested anywhere
        assert has_brevity or has_complexity, (
            "principle-trigger-policy.yaml must define a complexity gate"
        )

    def test_has_audit_contract(self) -> None:
        """Must declare an audit_contract section with a check_id."""
        import yaml
        parsed = yaml.safe_load(PRINCIPLE_TRIGGER_POLICY.read_text(encoding="utf-8"))
        audit = parsed.get("audit_contract", {})
        assert audit.get("check_id"), "audit_contract must have a non-empty check_id"


# ---------------------------------------------------------------------------
# atom-principle.yaml — separation contract
# ---------------------------------------------------------------------------

class TestAtomPrincipleSeparation:
    """atom-principle.yaml must not claim ownership of the Proceed Gate zone."""

    def test_atom_principle_zone_is_analysis_section(self) -> None:
        """atom-principle.yaml zone must be 'analysis_section', not proceed_gate."""
        import yaml
        parsed = yaml.safe_load(ATOM_PRINCIPLE.read_text(encoding="utf-8"))
        rendering = parsed.get("rendering_rules", {})
        zone = rendering.get("zone", "")
        assert zone == "analysis_section", (
            f"atom-principle.yaml zone must be 'analysis_section'; got '{zone}'"
        )

    def test_atom_principle_has_copilot_chat_compatible(self) -> None:
        """atom-principle.yaml must declare copilot_chat_compatible: true."""
        import yaml
        parsed = yaml.safe_load(ATOM_PRINCIPLE.read_text(encoding="utf-8"))
        rendering = parsed.get("rendering_rules", {})
        assert rendering.get("copilot_chat_compatible") is True
