"""
Orchestrator Classification Matrix + Wiring Contract Tests
==========================================================
Phase 124 — Wiring Verification Suite (Gap: no orchestrator-wide audit)

WHAT THIS TESTS:
  1. Orchestrator Inventory: all 8 composition files are present and classified
     (analysis / design / operations / meta)
  2. Classification contract: each composition intent maps to exactly ONE category
     in the trigger policy — no unclassified or multi-classified intents
  3. Operational compositions: must NOT declare atom-principle (P2-004)
     AND must declare a workflow_template reference (WorkflowComposer wiring)
  4. Analysis/design compositions: must declare atom-principle AND single_hop
     or multi-hop orchestration chain
  5. Workflow template references: every operational composition must reference
     an existing workflow template YAML
  6. Composition version absence: compositions must NOT declare a version field
     (version language eliminated per production-readiness hardening)
  7. Intent uniqueness: no two compositions may claim the same intent value

PASS/FAIL DEFINITIONS:
  PASS  = composition has correct classification, wiring, and no version field
  FAIL  = wrong classification, missing workflow_template, version present,
          or duplicate intent claimed by multiple compositions

Governance: CORE-008 (TDD), CORE-002 (inline only), CORE-PRINCIPLE-TRIGGER (P2-004)
Author: Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

# ── Canonical paths ────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).parents[3]
COMPOSITIONS_DIR = REPO_ROOT / "cortex-registry" / "templates" / "response" / "compositions"
TRIGGER_POLICY_PATH = REPO_ROOT / "cortex-registry" / "core" / "principle-trigger-policy.yaml"
WORKFLOWS_TEMPLATES_ROOT = REPO_ROOT / "cortex-registry" / "workflows" / "templates"

# ── Orchestrator Classification Matrix (ground truth) ─────────────────────────
#
# Category    | Composition         | Intent(s)        | atom-principle | workflow_template
# ------------|---------------------|------------------|----------------|------------------
# analysis    | comp-query.yaml     | QUERY            | ✅ required    | ❌ exempt (query)
# design      | comp-introduce.yaml | INTRODUCE        | ✅ required    | ❌ exempt (intro)
# operations  | comp-implement-fix  | IMPLEMENT, FIX   | ❌ blocked     | ✅ required
# operations  | comp-refactor       | REFACTOR         | ❌ blocked     | ✅ required
# operations  | comp-debug          | DEBUG            | ❌ blocked     | ✅ required
# operations  | comp-audit-fix      | AUDIT            | ❌ blocked     | ✅ required
# operations  | comp-health         | HEALTH           | ❌ blocked     | ✅ required (maintenance)
# operations  | comp-vacuum         | VACUUM           | ❌ blocked     | ✅ required (maintenance)

COMPOSITION_MATRIX = {
    "comp-query.yaml": {
        "category": "analysis",
        "intents": ["QUERY"],
        "principle_injection": True,
        "workflow_template_required": False,
        "single_hop": True,
    },
    "comp-introduce.yaml": {
        "category": "design",
        "intents": ["INTRODUCE"],
        "principle_injection": True,
        "workflow_template_required": False,
        "single_hop": False,
    },
    "comp-implement-fix.yaml": {
        "category": "operations",
        "intents": ["IMPLEMENT", "FIX"],
        "principle_injection": False,
        "workflow_template_required": True,
        "single_hop": False,
    },
    "comp-refactor.yaml": {
        "category": "operations",
        "intents": ["REFACTOR"],
        "principle_injection": False,
        "workflow_template_required": True,
        "single_hop": False,
    },
    "comp-debug.yaml": {
        "category": "operations",
        "intents": ["DEBUG"],
        "principle_injection": False,
        "workflow_template_required": True,
        "single_hop": False,
    },
    "comp-audit-fix.yaml": {
        "category": "operations",
        "intents": ["AUDIT"],
        "principle_injection": False,
        "workflow_template_required": True,
        "single_hop": False,
    },
    "comp-health.yaml": {
        "category": "operations",
        "intents": ["HEALTH"],
        "principle_injection": False,
        "workflow_template_required": True,
        "single_hop": False,
    },
    "comp-vacuum.yaml": {
        "category": "operations",
        "intents": ["VACUUM"],
        "principle_injection": False,
        "workflow_template_required": True,
        "single_hop": False,
    },
}


def _load_comp(filename: str) -> dict:
    path = COMPOSITIONS_DIR / filename
    assert path.exists(), f"{filename} not found at {path}"
    return yaml.safe_load(path.read_text())


def _atom_ids(comp: dict) -> list[str]:
    return [a["id"] if isinstance(a, dict) else a for a in comp.get("atoms", [])]


# ═══════════════════════════════════════════════════════════════════════════════
# 1. INVENTORY — All 8 compositions exist on disk
# ═══════════════════════════════════════════════════════════════════════════════

class TestOrchestratorInventory:
    """All 8 composition files must exist — full inventory check."""

    @pytest.mark.parametrize("filename", list(COMPOSITION_MATRIX.keys()))
    def test_composition_file_exists(self, filename: str) -> None:
        """INVENTORY: {filename} must exist on disk."""
        path = COMPOSITIONS_DIR / filename
        assert path.exists(), (
            f"Composition missing: {filename}\n"
            f"Expected at: {path}\n"
            f"Run Phase 120 Sub-Phase B to create missing compositions."
        )

    @pytest.mark.parametrize("filename", list(COMPOSITION_MATRIX.keys()))
    def test_composition_parses_as_valid_yaml(self, filename: str) -> None:
        """INVENTORY: {filename} must parse as valid YAML with a dict root."""
        path = COMPOSITIONS_DIR / filename
        assert path.exists(), f"{filename} not found"
        try:
            data = yaml.safe_load(path.read_text())
        except yaml.YAMLError as e:
            pytest.fail(f"{filename} YAML parse error: {e}")
        assert isinstance(data, dict), f"{filename} must parse to a dict, got {type(data)}"
        assert data.get("id"), f"{filename} must declare an 'id' field"

    def test_no_extra_unregistered_compositions(self) -> None:
        """INVENTORY: No unregistered composition files should exist in the compositions dir."""
        if not COMPOSITIONS_DIR.exists():
            pytest.skip("Compositions directory not found")
        on_disk = {f.name for f in COMPOSITIONS_DIR.glob("comp-*.yaml")}
        registered = set(COMPOSITION_MATRIX.keys())
        unregistered = on_disk - registered
        assert not unregistered, (
            f"Unregistered composition files found in compositions dir: {unregistered}\n"
            f"Add to COMPOSITION_MATRIX or remove the file."
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 2. CLASSIFICATION — Intent correctly maps to trigger policy category
# ═══════════════════════════════════════════════════════════════════════════════

class TestOrchestratorClassification:
    """Every composition intent must map to exactly one trigger policy category."""

    def _load_policy(self) -> dict:
        assert TRIGGER_POLICY_PATH.exists(), (
            f"principle-trigger-policy.yaml not found at {TRIGGER_POLICY_PATH}"
        )
        return yaml.safe_load(TRIGGER_POLICY_PATH.read_text())

    @pytest.mark.parametrize("filename,spec", list(COMPOSITION_MATRIX.items()))
    def test_composition_intents_match_policy_category(
        self, filename: str, spec: dict
    ) -> None:
        """CLASSIFICATION: {filename} intents must be in the correct policy category."""
        policy = self._load_policy()
        expected_category = spec["category"]
        expected_intents = spec["intents"]

        policy_category = policy["intent_categories"].get(expected_category, {})
        policy_intents = set(policy_category.get("intents", []))

        for intent in expected_intents:
            assert intent in policy_intents, (
                f"{filename}: intent '{intent}' not found in policy category '{expected_category}'.\n"
                f"Policy '{expected_category}' intents: {sorted(policy_intents)}\n"
                f"SSOT: cortex-registry/core/principle-trigger-policy.yaml"
            )

    @pytest.mark.parametrize("filename,spec", list(COMPOSITION_MATRIX.items()))
    def test_principle_injection_matches_category_policy(
        self, filename: str, spec: dict
    ) -> None:
        """CLASSIFICATION: {filename} principle_injection setting must match policy category."""
        policy = self._load_policy()
        category = spec["category"]
        policy_injection = policy["intent_categories"][category].get("principle_injection", False)

        # Verify the matrix ground truth matches the policy
        assert policy_injection == spec["principle_injection"], (
            f"{filename}: principle_injection mismatch.\n"
            f"Matrix says {spec['principle_injection']}, "
            f"policy category '{category}' says {policy_injection}.\n"
            f"Update COMPOSITION_MATRIX or fix principle-trigger-policy.yaml."
        )

    def test_no_intent_appears_in_multiple_categories(self) -> None:
        """CLASSIFICATION: No intent may be classified under multiple categories (ambiguous routing)."""
        policy = self._load_policy()
        intent_to_categories: dict[str, list[str]] = {}
        for cat_name, cat_data in policy.get("intent_categories", {}).items():
            for intent in cat_data.get("intents", []):
                intent_to_categories.setdefault(intent, []).append(cat_name)

        multi_classified = {
            intent: cats
            for intent, cats in intent_to_categories.items()
            if len(cats) > 1
        }
        assert not multi_classified, (
            f"Intents classified under multiple categories (ambiguous routing):\n"
            + "\n".join(f"  {intent}: {cats}" for intent, cats in multi_classified.items())
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 3. ATOM-PRINCIPLE WIRING — Per-composition injection contract
# ═══════════════════════════════════════════════════════════════════════════════

class TestCompositionAtomPrincipleWiring:
    """Per-composition: atom-principle presence/absence matches classification matrix."""

    @pytest.mark.parametrize("filename,spec", list(COMPOSITION_MATRIX.items()))
    def test_atom_principle_wiring_matches_matrix(self, filename: str, spec: dict) -> None:
        """WIRING: {filename} atom-principle presence must match classification matrix."""
        comp = _load_comp(filename)
        atoms = _atom_ids(comp)
        has_principle = "atom-principle" in atoms

        if spec["principle_injection"]:
            assert has_principle, (
                f"WIRING GAP: {filename} ({spec['category']}) must include atom-principle "
                f"(principle_injection=True) but it is missing.\n"
                f"Current atoms: {atoms}"
            )
        else:
            assert not has_principle, (
                f"P2-004 VIOLATION: {filename} ({spec['category']}) must NOT include atom-principle "
                f"(principle_injection=False) but atom-principle is present.\n"
                f"Operations/meta categories have override_allowed=False."
            )


# ═══════════════════════════════════════════════════════════════════════════════
# 4. WORKFLOW TEMPLATE WIRING — Operational compositions reference templates
# ═══════════════════════════════════════════════════════════════════════════════

class TestWorkflowTemplateWiring:
    """Operational compositions must declare and reference valid workflow templates.

    WorkflowComposer pattern: every code-touching / execution composition must
    reference a declarative workflow template in cortex-registry/workflows/templates/.
    If workflow_template is missing or the file doesn't exist, this is a wiring gap.
    """

    @pytest.mark.parametrize("filename,spec", [
        (f, s) for f, s in COMPOSITION_MATRIX.items() if s["workflow_template_required"]
    ])
    def test_operational_composition_declares_workflow_template(
        self, filename: str, spec: dict
    ) -> None:
        """WIRING: {filename} must declare workflow_template reference."""
        comp = _load_comp(filename)
        wf_ref = comp.get("workflow_template", "")
        assert wf_ref, (
            f"WIRING GAP: {filename} ({spec['category']}) must declare workflow_template.\n"
            f"WorkflowComposer requires all operational compositions to reference a "
            f"declarative workflow template in cortex-registry/workflows/templates/."
        )

    @pytest.mark.parametrize("filename,spec", [
        (f, s) for f, s in COMPOSITION_MATRIX.items() if s["workflow_template_required"]
    ])
    def test_operational_composition_workflow_template_exists(
        self, filename: str, spec: dict
    ) -> None:
        """WIRING: {filename} workflow_template YAML must exist on disk."""
        comp = _load_comp(filename)
        wf_ref = comp.get("workflow_template", "")
        if not wf_ref:
            pytest.skip(f"{filename} has no workflow_template declared")
        # wf_ref is relative to REPO_ROOT
        wf_path = REPO_ROOT / wf_ref
        assert wf_path.exists(), (
            f"WIRING GAP: {filename} references workflow_template='{wf_ref}' "
            f"but that file does not exist at {wf_path}.\n"
            f"Either create the workflow template YAML or update the reference."
        )

    @pytest.mark.parametrize("filename,spec", [
        (f, s) for f, s in COMPOSITION_MATRIX.items() if not s["workflow_template_required"]
    ])
    def test_non_operational_compositions_exempt_from_workflow_template(
        self, filename: str, spec: dict
    ) -> None:
        """WIRING: {filename} (analysis/design) is exempt from workflow_template requirement."""
        comp = _load_comp(filename)
        # Non-operational compositions may or may not have workflow_template — not required
        # This test confirms the exemption is in place and documents the contract
        category = spec["category"]
        assert category in ("analysis", "design"), (
            f"Unexpected: {filename} is marked workflow_template_required=False "
            f"but has category='{category}' which is not analysis or design."
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 5. VERSION + INTENT UNIQUENESS
# ═══════════════════════════════════════════════════════════════════════════════

class TestCompositionVersionAndIntentUniqueness:
    """All compositions must NOT have a version field; intents must be unique."""

    @pytest.mark.parametrize("filename,spec", list(COMPOSITION_MATRIX.items()))
    def test_composition_has_no_version_field(self, filename: str, spec: dict) -> None:
        """VERSION: {filename} must NOT declare a version field (version language eliminated)."""
        comp = _load_comp(filename)
        assert "version" not in comp, (
            f"{filename}: version field must be absent (production-readiness hardening), "
            f"but found version='{comp.get('version')}'"
        )

    def test_no_two_compositions_claim_same_intent(self) -> None:
        """UNIQUENESS: No intent may be claimed by more than one composition."""
        intent_to_comp: dict[str, list[str]] = {}
        for filename in COMPOSITION_MATRIX:
            comp = _load_comp(filename)
            intent = comp.get("intent")
            if intent is None:
                continue
            intents = intent if isinstance(intent, list) else [intent]
            for i in intents:
                intent_to_comp.setdefault(str(i), []).append(filename)

        duplicates = {
            intent: comps
            for intent, comps in intent_to_comp.items()
            if len(comps) > 1
        }
        assert not duplicates, (
            f"Duplicate intent claims across compositions (ambiguous routing):\n"
            + "\n".join(
                f"  '{intent}' claimed by: {comps}"
                for intent, comps in duplicates.items()
            )
        )

    @pytest.mark.parametrize("filename,spec", list(COMPOSITION_MATRIX.items()))
    def test_composition_id_matches_filename(self, filename: str, spec: dict) -> None:
        """CONSISTENCY: {filename} must declare id matching its filename (without .yaml)."""
        comp = _load_comp(filename)
        expected_id = filename.replace(".yaml", "")
        assert comp.get("id") == expected_id, (
            f"{filename}: id must be '{expected_id}', got '{comp.get('id')}'"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 6. SINGLE-HOP ROUTING CONTRACT
# ═══════════════════════════════════════════════════════════════════════════════

class TestSingleHopRoutingContract:
    """Single-hop compositions must omit 🧭 Orchestration: line; multi-hop must include it."""

    @pytest.mark.parametrize("filename,spec", list(COMPOSITION_MATRIX.items()))
    def test_single_hop_omits_orchestration_in_template(
        self, filename: str, spec: dict
    ) -> None:
        """ROUTING: Single-hop compositions must NOT include 🧭 Orchestration: in template."""
        comp = _load_comp(filename)
        is_single_hop = spec["single_hop"]
        template = comp.get("template", "")
        has_orchestration_line = "🧭 Orchestration:" in template

        if is_single_hop:
            assert not has_orchestration_line, (
                f"{filename} is single_hop=True but template contains '🧭 Orchestration:' line.\n"
                f"Single-hop compositions must omit the orchestration breadcrumb "
                f"per atom-orchestration omit_if_single_hop rule."
            )
        else:
            assert has_orchestration_line, (
                f"{filename} is multi-hop but template is missing '🧭 Orchestration:' line.\n"
                f"Multi-hop compositions must include the orchestration chain in Zone 3."
            )

    @pytest.mark.parametrize("filename,spec", list(COMPOSITION_MATRIX.items()))
    def test_multi_hop_orchestration_chain_starts_with_classifier(
        self, filename: str, spec: dict
    ) -> None:
        """ROUTING: Multi-hop orchestration_chain must start with 'Classifier'."""
        comp = _load_comp(filename)
        if spec["single_hop"]:
            return  # single-hop exempt
        chain = comp.get("orchestration_chain", "")
        if chain is None:
            return  # null chain is correct for single-hop (already tested)
        assert chain.startswith("Classifier"), (
            f"{filename}: orchestration_chain must start with 'Classifier' (IntentRouter display name), "
            f"got '{chain}'"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 7. REQUIRED ATOM BASELINE — Every composition must have identity + quote atoms
# ═══════════════════════════════════════════════════════════════════════════════

class TestRequiredAtomBaseline:
    """Every composition must include the 3 baseline atoms: identity, quote, status-footer."""

    _BASELINE_ATOMS = ["atom-identity", "atom-quote", "atom-status-footer"]

    @pytest.mark.parametrize("filename", list(COMPOSITION_MATRIX.keys()))
    @pytest.mark.parametrize("atom_id", _BASELINE_ATOMS)
    def test_composition_has_baseline_atom(self, filename: str, atom_id: str) -> None:
        """BASELINE: {filename} must include {atom_id} in atoms list."""
        comp = _load_comp(filename)
        atoms = _atom_ids(comp)
        assert atom_id in atoms, (
            f"{filename}: missing baseline atom '{atom_id}'.\n"
            f"All compositions must include identity + quote + status-footer as baseline.\n"
            f"Current atoms: {atoms}"
        )
