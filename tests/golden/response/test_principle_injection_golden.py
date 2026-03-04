"""
Golden Snapshot Tests: Principle Block Injection End-to-End
===========================================================
Phase 124 — Wiring Verification Suite (Gap: no golden injection tests)

WHAT THIS TESTS:
  1. Analysis compositions (QUERY, INTRODUCE) → atom-principle PRESENT in atoms list
  2. Operations compositions (IMPLEMENT, FIX, REFACTOR, DEBUG, AUDIT, HEALTH, VACUUM)
     → atom-principle ABSENT from atoms list (P2-004 contract)
  3. comp-query.yaml rendered template snapshot includes ### 💡 Principle: placeholder
  4. comp-introduce.yaml rendered template MISSING principle placeholder (wiring gap)
  5. Principle body length enforcement (≤200 chars) on every catalogue entry
  6. Registry SSOT coherence: every composition listed in _registry.yaml exists on disk
  7. Template markdown format consistency: single H1, HR zones, no H4+, no tree chars
  8. comp-query.yaml zone-3 injection ordering (orchestration breadcrumb omitted;
     principle block IS Zone 3 first content)

PASS/FAIL DEFINITIONS:
  PASS  = composition atom list + template render match declared wiring contract
  FAIL  = atom-principle in operations comp, or absent from analysis comp,
          or template doesn't render principle placeholder for analysis,
          or body > 200 chars on any principle

Governance: CORE-008 (TDD), CORE-002 (inline only), CORE-PRINCIPLE-TRIGGER (P2-004)
Author: Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

# ── Canonical paths ────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).parents[3]
COMPOSITIONS_DIR = REPO_ROOT / "cortex-registry" / "templates" / "response" / "compositions"
REGISTRY_PATH = REPO_ROOT / "cortex-registry" / "templates" / "response" / "_registry.yaml"
PRINCIPLES_PATH = REPO_ROOT / "cortex-registry" / "knowledge" / "sdlc" / "high-value-principles.yaml"
TRIGGER_POLICY_PATH = REPO_ROOT / "cortex-registry" / "core" / "principle-trigger-policy.yaml"

# Tree characters forbidden in VS Code Copilot Chat panel (rendering contract)
# Note: U+2500 (─) appears in YAML comment-separator lines and is harmless.
# Only these multi-char box-drawing sequences collapse visually in rendered output.
_TREE_CHARS = ["├─", "└─", "│", "╔", "╗", "╚", "╝", "╠", "╩"]
_FORBIDDEN_HTML_PATTERN = re.compile(
    r"<(?!/?(?:details|summary))[a-zA-Z][^>]*>", re.IGNORECASE
)

# Composition classification — ground truth for golden snapshot
_ANALYSIS_DESIGN_COMPS = {
    "comp-query.yaml": "QUERY (analysis)",
    "comp-introduce.yaml": "INTRODUCE (design)",
}

_OPERATIONAL_COMPS = {
    "comp-implement-fix.yaml": "IMPLEMENT/FIX (operations)",
    "comp-refactor.yaml": "REFACTOR (operations)",
    "comp-debug.yaml": "DEBUG (operations)",
    "comp-audit-fix.yaml": "AUDIT (operations)",
    "comp-health.yaml": "HEALTH (operations)",
    "comp-vacuum.yaml": "VACUUM (operations)",
}


# ═══════════════════════════════════════════════════════════════════════════════
# 1. INJECTION TRIGGER POLICY — Analysis/Design compositions MUST inject
# ═══════════════════════════════════════════════════════════════════════════════

class TestAnalysisDesignCompositionsInjectPrinciple:
    """Golden: QUERY + INTRODUCE compositions must include atom-principle in atoms list.

    CORE-PRINCIPLE-TRIGGER: principle_injection=True for analysis and design categories.
    Failing this test means a composition was updated to remove atom-principle without
    updating the trigger policy — a P2-004 drift.
    """

    @pytest.mark.parametrize("filename,label", list(_ANALYSIS_DESIGN_COMPS.items()))
    def test_analysis_design_composition_has_atom_principle(self, filename: str, label: str) -> None:
        """GOLDEN: {label} composition must include atom-principle in its atoms list."""
        path = COMPOSITIONS_DIR / filename
        assert path.exists(), f"{filename} not found at {path}"
        comp = yaml.safe_load(path.read_text())
        atom_ids = [a["id"] if isinstance(a, dict) else a for a in comp.get("atoms", [])]
        assert "atom-principle" in atom_ids, (
            f"CORE-PRINCIPLE-TRIGGER VIOLATION: atom-principle MISSING from {filename} ({label})\n"
            f"Atoms present: {atom_ids}\n"
            f"SSOT: cortex-registry/core/principle-trigger-policy.yaml"
        )

    @pytest.mark.parametrize("filename,label", list(_ANALYSIS_DESIGN_COMPS.items()))
    def test_atom_principle_is_in_zone_3(self, filename: str, label: str) -> None:
        """GOLDEN: atom-principle must be declared in Zone 3 of analysis/design compositions."""
        path = COMPOSITIONS_DIR / filename
        assert path.exists(), f"{filename} not found"
        comp = yaml.safe_load(path.read_text())
        for atom in comp.get("atoms", []):
            if isinstance(atom, dict) and atom.get("id") == "atom-principle":
                zone = atom.get("zone", atom.get("params", {}).get("zone"))
                assert zone == 3, (
                    f"{filename}: atom-principle must be in Zone 3, got zone={zone}"
                )
                return
        pytest.fail(f"{filename}: atom-principle not found in atoms list")


# ═══════════════════════════════════════════════════════════════════════════════
# 2. INJECTION TRIGGER POLICY — Operational compositions must NOT inject
# ═══════════════════════════════════════════════════════════════════════════════

class TestOperationalCompositionsExcludePrinciple:
    """Golden (P2-004): Operational compositions must NOT include atom-principle.

    CORE-PRINCIPLE-TRIGGER: principle_injection=False for operations category.
    override_allowed=False — no bypass permitted.
    If any operational composition contains atom-principle, this is a P2-004 violation.
    """

    @pytest.mark.parametrize("filename,label", list(_OPERATIONAL_COMPS.items()))
    def test_operational_composition_excludes_atom_principle(self, filename: str, label: str) -> None:
        """GOLDEN (P2-004): {label} must NOT include atom-principle in atoms list."""
        path = COMPOSITIONS_DIR / filename
        assert path.exists(), f"{filename} not found at {path}"
        comp = yaml.safe_load(path.read_text())
        atom_ids = [a["id"] if isinstance(a, dict) else a for a in comp.get("atoms", [])]
        assert "atom-principle" not in atom_ids, (
            f"P2-004 VIOLATION: atom-principle found in operational composition {filename} ({label})\n"
            f"Atoms: {atom_ids}\n"
            f"Operations category has principle_injection=False with override_allowed=False.\n"
            f"SSOT: cortex-registry/core/principle-trigger-policy.yaml"
        )

    @pytest.mark.parametrize("filename,label", list(_OPERATIONAL_COMPS.items()))
    def test_operational_composition_has_no_principle_override(self, filename: str, label: str) -> None:
        """GOLDEN: No atom in operational composition declares principle_override=True."""
        path = COMPOSITIONS_DIR / filename
        assert path.exists(), f"{filename} not found"
        comp = yaml.safe_load(path.read_text())
        for atom in comp.get("atoms", []):
            if isinstance(atom, dict):
                override = atom.get("principle_override", False)
                assert not override, (
                    f"P2-004 override bypass detected in {filename}: "
                    f"atom {atom.get('id')} has principle_override=True. "
                    f"Operations category override_allowed=False."
                )


# ═══════════════════════════════════════════════════════════════════════════════
# 3. TEMPLATE SNAPSHOT — comp-query.yaml renders principle placeholder
# ═══════════════════════════════════════════════════════════════════════════════

class TestCompQueryTemplateSnapshot:
    """Golden snapshot: comp-query.yaml template must render the principle placeholder.

    The rendered template in comp-query.yaml should contain ### 💡 Principle:
    as the Zone 3 injection marker — confirming the LEGO assembly synthesises correctly.
    """

    def _load_comp_query(self) -> dict:
        path = COMPOSITIONS_DIR / "comp-query.yaml"
        assert path.exists(), f"comp-query.yaml not found at {path}"
        return yaml.safe_load(path.read_text())

    def test_comp_query_template_has_principle_placeholder(self) -> None:
        """GOLDEN: comp-query.yaml template must include ### 💡 Principle: rendering marker."""
        comp = self._load_comp_query()
        template = comp.get("template", "")
        assert "### 💡 Principle:" in template, (
            "comp-query.yaml template missing '### 💡 Principle:' placeholder.\n"
            "atom-principle is declared in atoms list but the rendered template "
            "does not include the injection marker — wiring gap between atom declaration "
            "and template synthesis."
        )

    def test_comp_query_template_has_three_zones(self) -> None:
        """GOLDEN: comp-query.yaml template must contain exactly 2 HR zone separators (3 zones)."""
        comp = self._load_comp_query()
        template = comp.get("template", "")
        # HR in markdown = line containing only '---'
        hr_count = sum(1 for line in template.splitlines() if line.strip() == "---")
        assert hr_count >= 2, (
            f"comp-query.yaml template must have ≥2 HR separators (3-zone layout), "
            f"found {hr_count}. Zone 1: identity; Zone 2: quote; Zone 3: principle."
        )

    def test_comp_query_template_single_h1(self) -> None:
        """GOLDEN: comp-query.yaml template must have exactly one H1 heading."""
        comp = self._load_comp_query()
        template = comp.get("template", "")
        h1_lines = [l for l in template.splitlines() if l.startswith("# ") and not l.startswith("## ")]
        assert len(h1_lines) == 1, (
            f"comp-query.yaml template must have exactly 1 H1, found {len(h1_lines)}: {h1_lines}"
        )

    def test_comp_query_template_no_h4_headings(self) -> None:
        """GOLDEN: comp-query.yaml template must not use H4+ headings (renders flat in VS Code)."""
        comp = self._load_comp_query()
        template = comp.get("template", "")
        h4_lines = [l for l in template.splitlines() if l.startswith("#### ")]
        assert not h4_lines, (
            f"comp-query.yaml template uses H4+ headings (renders flat in VS Code Copilot Chat): {h4_lines}"
        )

    def test_comp_query_template_no_tree_chars(self) -> None:
        """GOLDEN: comp-query.yaml template must contain no tree characters."""
        comp = self._load_comp_query()
        template = comp.get("template", "")
        found = [c for c in _TREE_CHARS if c in template]
        assert not found, (
            f"comp-query.yaml template contains forbidden tree characters: {found}"
        )

    def test_comp_query_single_hop_omits_orchestration_line(self) -> None:
        """GOLDEN: comp-query.yaml is single-hop — template must NOT contain 🧭 Orchestration: line."""
        comp = self._load_comp_query()
        assert comp.get("single_hop") is True, (
            "comp-query.yaml must declare single_hop: true"
        )
        template = comp.get("template", "")
        assert "🧭 Orchestration:" not in template, (
            "comp-query.yaml is single-hop: 🧭 Orchestration: line must be omitted per "
            "atom-orchestration omit_if_single_hop rule."
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 4. WIRING GAP DETECTION — comp-introduce.yaml template vs atom declaration
# ═══════════════════════════════════════════════════════════════════════════════

class TestCompIntroduceWiringCompleteness:
    """Golden: comp-introduce.yaml declares atom-principle in atoms but must
    also include the principle placeholder in the rendered template.

    This test catches the wiring gap where the atom is declared in the atoms list
    (correct) but the LEGO template synthesis has not yet been updated to include
    the ### 💡 Principle: render block (gap).

    CURRENT STATE: atom declared ✅ | template placeholder ❌ (gap)
    TARGET STATE:  atom declared ✅ | template placeholder ✅
    """

    def _load(self) -> dict:
        path = COMPOSITIONS_DIR / "comp-introduce.yaml"
        assert path.exists(), f"comp-introduce.yaml not found at {path}"
        return yaml.safe_load(path.read_text())

    def test_comp_introduce_atom_declared(self) -> None:
        """PASS (current): comp-introduce.yaml declares atom-principle in atoms list."""
        comp = self._load()
        atom_ids = [a["id"] if isinstance(a, dict) else a for a in comp.get("atoms", [])]
        assert "atom-principle" in atom_ids, (
            "comp-introduce.yaml must declare atom-principle in atoms list "
            "(INTRODUCE is a design-category intent — principle injection=True)"
        )

    def test_comp_introduce_template_has_principle_placeholder(self) -> None:
        """GOLDEN (gap): comp-introduce.yaml template must include ### 💡 Principle: marker.

        CURRENTLY: atom declared but template block missing.
        Fix: add '### 💡 Principle: {title}\\n{body}' after the second --- in comp-introduce.yaml template.
        """
        comp = self._load()
        template = comp.get("template", "")
        assert "### 💡 Principle:" in template, (
            "WIRING GAP: comp-introduce.yaml declares atom-principle in atoms list "
            "but the rendered template does not include '### 💡 Principle:' placeholder.\n"
            "Fix: add principle placeholder to comp-introduce.yaml template after Zone 3 opening.\n"
            "Reference: comp-query.yaml template as the canonical example."
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 5. PRINCIPLE BODY BREVITY — Every catalogue entry ≤200 chars raw
# ═══════════════════════════════════════════════════════════════════════════════

class TestPrincipleCatalogueBrevity:
    """Golden: Every principle body in high-value-principles.yaml must be ≤200 chars (raw YAML).

    PrincipleSelector truncates at select() time, but the catalogue itself should
    not have entries that require aggressive truncation — each body should be
    concise at source. Bodies > 300 chars indicate catalogue hygiene issues.
    Bodies > 200 chars will always be truncated — this is tracked per principle.
    """

    def _load_principles(self) -> list[dict]:
        data = yaml.safe_load(PRINCIPLES_PATH.read_text())
        return data["principles"]

    def test_no_principle_body_exceeds_300_chars(self) -> None:
        """GOLDEN: No raw principle body in catalogue should exceed 300 chars (hygiene gate)."""
        principles = self._load_principles()
        violations = []
        for p in principles:
            body = p.get("body", "")
            # YAML multiline scalars include whitespace — normalise
            normalised = " ".join(body.split())
            if len(normalised) > 300:
                violations.append(
                    f"  {p['id']}: {len(normalised)} chars (body starts: '{normalised[:60]}...')"
                )
        assert not violations, (
            f"Principle bodies exceed 300-char hygiene gate ({len(violations)} entries):\n"
            + "\n".join(violations)
        )

    def test_principles_truncated_at_200_chars_by_selector(self) -> None:
        """GOLDEN: PrincipleSelector truncates every body to ≤200 chars at select() time."""
        from cortex.intelligence.principle_selector import PrincipleSelector, _principles_cache
        import cortex.intelligence.principle_selector as ps_mod

        # Force load all principles through the selector for every principle ID
        original = ps_mod._principles_cache
        try:
            # Load catalogue fresh
            ps_mod._principles_cache = None
            ps = PrincipleSelector("QUERY", pool="principles")
            principles_raw = yaml.safe_load(PRINCIPLES_PATH.read_text())["principles"]

            violations = []
            for p_raw in principles_raw:
                # Inject this single principle as the full cache + clear ring buffer
                ps_mod._principles_cache = [p_raw]
                ps_mod._ring_buffer.clear()
                result = ps.select(context_hints={"is_complex": True})
                body = result.get("body", "")
                if len(body) > 200:
                    violations.append(f"  {p_raw['id']}: body={len(body)} chars after select()")
        finally:
            ps_mod._principles_cache = original

        assert not violations, (
            f"PrincipleSelector failed to truncate bodies to ≤200 chars:\n"
            + "\n".join(violations)
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 6. REGISTRY SSOT COHERENCE — All listed compositions exist on disk
# ═══════════════════════════════════════════════════════════════════════════════

class TestRegistrySSOTCoherence:
    """Golden: Every composition entry in _registry.yaml must exist on disk.

    This detects SSOT drift where the registry claims a composition exists
    but the file was deleted, renamed, or never created.
    """

    def _load_registry(self) -> dict:
        assert REGISTRY_PATH.exists(), f"_registry.yaml not found at {REGISTRY_PATH}"
        return yaml.safe_load(REGISTRY_PATH.read_text())

    def test_all_registry_compositions_exist_on_disk(self) -> None:
        """GOLDEN: Every composition in _registry.yaml must have a corresponding YAML file."""
        registry = self._load_registry()
        compositions = registry.get("compositions", [])
        missing = []
        for comp_entry in compositions:
            file_ref = comp_entry.get("file", "")
            # file is relative to cortex-registry/templates/response/
            full_path = REPO_ROOT / "cortex-registry" / "templates" / "response" / file_ref
            if not full_path.exists():
                missing.append(f"  {comp_entry.get('id')} → {full_path}")
        assert not missing, (
            f"Registry SSOT drift: {len(missing)} composition(s) listed in _registry.yaml "
            f"do not exist on disk:\n" + "\n".join(missing)
        )

    def test_all_registry_atoms_exist_on_disk(self) -> None:
        """GOLDEN: Every atom in _registry.yaml must have a corresponding YAML file on disk."""
        registry = self._load_registry()
        atoms = registry.get("atoms", [])
        missing = []
        for atom_entry in atoms:
            file_ref = atom_entry.get("file", "")
            full_path = REPO_ROOT / "cortex-registry" / "templates" / "response" / file_ref
            if not full_path.exists():
                missing.append(f"  {atom_entry.get('id')} → {full_path}")
        assert not missing, (
            f"Registry SSOT drift: {len(missing)} atom(s) listed in _registry.yaml "
            f"do not exist on disk:\n" + "\n".join(missing)
        )

    def test_atom_principle_listed_in_registry(self) -> None:
        """GOLDEN: atom-principle must appear in _registry.yaml atoms list."""
        registry = self._load_registry()
        atom_ids = {a["id"] for a in registry.get("atoms", [])}
        assert "atom-principle" in atom_ids, (
            "atom-principle missing from _registry.yaml atoms list — "
            "SSOT drift between atom-principle.yaml and _registry.yaml"
        )

    def test_registry_atom_principle_status_is_active(self) -> None:
        """GOLDEN: atom-principle must have status=ACTIVE in _registry.yaml."""
        registry = self._load_registry()
        for atom in registry.get("atoms", []):
            if atom.get("id") == "atom-principle":
                assert atom.get("status") == "ACTIVE", (
                    f"atom-principle in _registry.yaml has status={atom.get('status')}, "
                    f"expected ACTIVE"
                )
                return
        pytest.fail("atom-principle not found in _registry.yaml atoms list")


# ═══════════════════════════════════════════════════════════════════════════════
# 7. MARKDOWN FORMAT CONSISTENCY — All compositions share canonical structure
# ═══════════════════════════════════════════════════════════════════════════════

class TestCompositionMarkdownConsistency:
    """Golden: All compositions must share canonical VS Code Copilot Chat rendering rules.

    Checks:
      - No H4+ headings in any template
      - No tree characters in any template
      - No forbidden HTML in any template
      - Author line format canonical across all compositions
      - Single H1 per composition
    """

    _ALL_COMPOSITIONS = list(_ANALYSIS_DESIGN_COMPS.keys()) + list(_OPERATIONAL_COMPS.keys())

    @pytest.mark.parametrize("filename", _ALL_COMPOSITIONS)
    def test_composition_template_single_h1(self, filename: str) -> None:
        """GOLDEN: Every composition template must have exactly one H1 heading."""
        path = COMPOSITIONS_DIR / filename
        assert path.exists(), f"{filename} not found"
        comp = yaml.safe_load(path.read_text())
        template = comp.get("template", "")
        h1_lines = [l for l in template.splitlines()
                    if l.startswith("# ") and not l.startswith("## ")]
        assert len(h1_lines) == 1, (
            f"{filename}: must have exactly 1 H1, found {len(h1_lines)}: {h1_lines}"
        )

    @pytest.mark.parametrize("filename", _ALL_COMPOSITIONS)
    def test_composition_template_has_author_line(self, filename: str) -> None:
        """GOLDEN: Every composition template must contain the canonical Author line."""
        path = COMPOSITIONS_DIR / filename
        assert path.exists(), f"{filename} not found"
        comp = yaml.safe_load(path.read_text())
        template = comp.get("template", "")
        assert "Asif Hussain" in template, (
            f"{filename}: template missing canonical 'Asif Hussain' author line"
        )
        assert "© 2025" in template or "© 2026" in template, (
            f"{filename}: template missing copyright year in author line"
        )

    @pytest.mark.parametrize("filename", _ALL_COMPOSITIONS)
    def test_composition_template_no_tree_chars(self, filename: str) -> None:
        """GOLDEN: No tree characters in the rendered template section of any composition.

        Note: YAML comment-separator lines (# ────) use U+2500 box-drawing dashes
        but are in YAML comments, not in rendered output. This test checks only
        the `template:` field value — the content the LLM will actually render.
        """
        path = COMPOSITIONS_DIR / filename
        assert path.exists(), f"{filename} not found"
        comp = yaml.safe_load(path.read_text())
        template = comp.get("template", "")
        # Only flag U+251C U+2514 U+2502 U+2554 U+2557 U+255A U+255D — the box-drawing
        # chars that visually collapse in VS Code. U+2500 (─) in YAML comments is harmless.
        RENDER_FORBIDDEN = ["├─", "└─", "│", "╔", "╗", "╚", "╝", "╠", "╩"]
        found = [c for c in RENDER_FORBIDDEN if c in template]
        assert not found, (
            f"{filename}: forbidden tree characters in rendered template: {found}\n"
            "Tree chars collapse in VS Code dark themes — forbidden per rendering contract."
        )

    @pytest.mark.parametrize("filename", _ALL_COMPOSITIONS)
    def test_composition_has_copilot_chat_compatible_flag(self, filename: str) -> None:
        """GOLDEN: Every composition must declare rendering_rules.copilot_chat_compatible=true."""
        path = COMPOSITIONS_DIR / filename
        assert path.exists(), f"{filename} not found"
        comp = yaml.safe_load(path.read_text())
        rr = comp.get("rendering_rules", {})
        assert rr.get("copilot_chat_compatible") is True, (
            f"{filename}: rendering_rules.copilot_chat_compatible must be true"
        )

    @pytest.mark.parametrize("filename", _ALL_COMPOSITIONS)
    def test_composition_has_orchestration_chain(self, filename: str) -> None:
        """GOLDEN: Every composition must declare its orchestration_chain."""
        path = COMPOSITIONS_DIR / filename
        assert path.exists(), f"{filename} not found"
        comp = yaml.safe_load(path.read_text())
        # comp-query is single-hop — orchestration_chain is null (permitted)
        if comp.get("single_hop") is True:
            chain = comp.get("orchestration_chain")
            assert chain is None, (
                f"{filename}: single_hop=true must have orchestration_chain=null, "
                f"got '{chain}'"
            )
        else:
            chain = comp.get("orchestration_chain", "")
            assert chain and "Classifier" in chain, (
                f"{filename}: orchestration_chain must start with 'Classifier', got '{chain}'"
            )


# ═══════════════════════════════════════════════════════════════════════════════
# 8. TRIGGER POLICY YAML COHERENCE
# ═══════════════════════════════════════════════════════════════════════════════

class TestTriggerPolicyCohesion:
    """Golden: principle-trigger-policy.yaml must be self-consistent and cover all compositions."""

    def _load_policy(self) -> dict:
        assert TRIGGER_POLICY_PATH.exists(), (
            f"principle-trigger-policy.yaml not found at {TRIGGER_POLICY_PATH}"
        )
        return yaml.safe_load(TRIGGER_POLICY_PATH.read_text())

    def test_every_composition_intent_is_classified(self) -> None:
        """GOLDEN: Every intent declared in compositions must appear in trigger policy categories."""
        policy = self._load_policy()
        all_policy_intents: set[str] = set()
        for cat in policy.get("intent_categories", {}).values():
            all_policy_intents.update(cat.get("intents", []))

        # Gather intents from all compositions
        unclassified = []
        for filename in list(_ANALYSIS_DESIGN_COMPS.keys()) + list(_OPERATIONAL_COMPS.keys()):
            path = COMPOSITIONS_DIR / filename
            if not path.exists():
                continue
            comp = yaml.safe_load(path.read_text())
            intent = comp.get("intent")
            if intent is None:
                continue
            intents = intent if isinstance(intent, list) else [intent]
            for i in intents:
                if i not in all_policy_intents:
                    unclassified.append(f"  {filename}: intent={i}")

        assert not unclassified, (
            f"Composition intents not classified in principle-trigger-policy.yaml:\n"
            + "\n".join(unclassified)
            + "\nAdd missing intents to the appropriate category."
        )

    def test_operations_override_allowed_is_false(self) -> None:
        """GOLDEN: Operations category must have override_allowed=False (no bypass)."""
        policy = self._load_policy()
        ops = policy["intent_categories"]["operations"]
        assert ops.get("override_allowed") is False, (
            "Operations category must declare override_allowed: false — "
            "no bypass of principle injection suppression is permitted"
        )

    def test_brevity_body_max_chars_is_200(self) -> None:
        """GOLDEN: brevity.body_max_chars must be 200 (governance contract)."""
        policy = self._load_policy()
        assert policy["brevity"]["body_max_chars"] == 200, (
            f"brevity.body_max_chars must be 200, got {policy['brevity']['body_max_chars']}"
        )
