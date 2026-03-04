"""
Phase 124-D: Golden drift-lock tests — schema stability + catalogue integrity.

These tests are DRIFT LOCKS: they encode invariants that must hold across all
future modifications to the principles library and atom definitions. If a drift
lock fails, it means an intentional schema change occurred and the lock must be
updated by explicit decision (not by accident).

RED gate: All tests fail before artefacts exist (or pass if artefacts already
          match the locked values — treated as GREEN since 124-A/B/C are complete).

Governance: CORE-008 (TDD), CORE-002 (no .md files), CORE-064 (sweep completeness).
CORE-PRINCIPLE-TRIGGER: Principle injection only in analysis/design compositions.
  SSOT: cortex-registry/core/principle-trigger-policy.yaml
  Audit check: P2-004 (audit-checklist.yaml)
"""
from __future__ import annotations

from pathlib import Path

import yaml

# ── File paths ──────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).parent.parent.parent

PRINCIPLES_PATH = REPO_ROOT / "cortex-registry" / "knowledge" / "sdlc" / "high-value-principles.yaml"
ATOM_PRINCIPLE_PATH = REPO_ROOT / "cortex-registry" / "templates" / "response" / "atoms" / "atom-principle.yaml"
ATOM_QUOTE_PATH = REPO_ROOT / "cortex-registry" / "templates" / "response" / "atoms" / "atom-quote.yaml"
COMP_QUERY_PATH = REPO_ROOT / "cortex-registry" / "templates" / "response" / "compositions" / "comp-query.yaml"
REGISTRY_PATH = REPO_ROOT / "cortex-registry" / "templates" / "response" / "_registry.yaml"
PRINCIPLE_SELECTOR_PATH = REPO_ROOT / "cortex" / "intelligence" / "principle_selector.py"
TRIGGER_POLICY_PATH = REPO_ROOT / "cortex-registry" / "core" / "principle-trigger-policy.yaml"
COMPOSITIONS_DIR = REPO_ROOT / "cortex-registry" / "templates" / "response" / "compositions"

# Operational compositions that MUST NOT contain atom-principle (CORE-PRINCIPLE-TRIGGER)
_OPERATIONAL_COMPOSITIONS = {
    "comp-implement-fix.yaml",
    "comp-refactor.yaml",
    "comp-debug.yaml",
    "comp-audit-fix.yaml",
    "comp-health.yaml",
    "comp-vacuum.yaml",
}


class TestDriftLockPrinciplesCatalogue:
    """Drift locks for high-value-principles.yaml catalogue invariants."""

    def _load(self) -> dict:
        return yaml.safe_load(PRINCIPLES_PATH.read_text())

    def test_lock_catalogue_count_is_30(self):
        """DRIFT LOCK: Catalogue must have exactly 30 principles (Phase 124 baseline)."""
        data = self._load()
        assert len(data["principles"]) == 30

    def test_lock_all_domains_present(self):
        """DRIFT LOCK: All 10 canonical domains must be represented."""
        expected = {
            "tdd", "refactoring", "architecture", "security",
            "api_design", "testing", "observability", "code_quality",
            "documentation", "devops",
        }
        data = self._load()
        actual = {p["domain"] for p in data["principles"]}
        assert actual == expected, f"Domain set changed. Expected: {expected}, Got: {actual}"

    def test_lock_ids_are_stable(self):
        """DRIFT LOCK: Principle IDs from Phase 124 baseline must not be renamed/deleted."""
        phase_124_ids = {
            "tdd-001", "tdd-002", "tdd-003",
            "refactoring-001", "refactoring-002", "refactoring-003",
            "architecture-001", "architecture-002", "architecture-003", "architecture-004",
            "security-001", "security-002", "security-003",
            "api_design-001", "api_design-002", "api_design-003",
            "testing-001", "testing-002", "testing-003",
            "observability-001", "observability-002", "observability-003",
            "code_quality-001", "code_quality-002", "code_quality-003",
            "documentation-001", "documentation-002",
            "devops-001", "devops-002", "devops-003",
        }
        data = self._load()
        actual_ids = {p["id"] for p in data["principles"]}
        missing = phase_124_ids - actual_ids
        assert not missing, f"Phase 124 baseline IDs were removed: {missing}"

    def test_lock_version_is_string(self):
        """DRIFT LOCK: version field must exist and be a string."""
        data = self._load()
        assert isinstance(data.get("version"), str), "version field must be a string"


class TestDriftLockAtomPrinciple:
    """Drift locks for atom-principle.yaml structural invariants."""

    def _load(self) -> dict:
        return yaml.safe_load(ATOM_PRINCIPLE_PATH.read_text())

    def test_lock_atom_id(self):
        """DRIFT LOCK: atom id must remain 'atom-principle'."""
        assert self._load()["id"] == "atom-principle"

    def test_lock_atom_zone(self):
        """DRIFT LOCK: atom must remain in Zone 3."""
        assert self._load()["rendering_rules"]["zone"] == 3

    def test_lock_atom_phase(self):
        """DRIFT LOCK: phase must remain '124'."""
        assert self._load()["phase"] == "124"

    def test_lock_template_format(self):
        """DRIFT LOCK: template must begin with '### 💡 Principle:' prefix."""
        template = self._load().get("template", "")
        assert "### 💡 Principle:" in template, (
            "atom-principle template heading format changed — update drift lock if intentional"
        )


class TestDriftLockCompQuery:
    """Drift locks for comp-query.yaml injection invariants."""

    def _load(self) -> dict:
        return yaml.safe_load(COMP_QUERY_PATH.read_text())

    def test_lock_atom_principle_in_atoms(self):
        """DRIFT LOCK: comp-query.yaml must include atom-principle in atoms list."""
        atoms = self._load().get("atoms", [])
        assert any(a["id"] == "atom-principle" for a in atoms)

    def test_lock_atom_count_is_4(self):
        """DRIFT LOCK: comp-query.yaml must have exactly 4 atoms (Phase 124 baseline)."""
        atoms = self._load().get("atoms", [])
        assert len(atoms) == 4, (
            f"comp-query atom count changed from 4 to {len(atoms)} — update lock if intentional"
        )


class TestDriftLockPrincipleSelector:
    """Drift locks for PrincipleSelector implementation invariants."""

    def test_lock_pool_parameter_exists(self):
        """DRIFT LOCK: PrincipleSelector must accept pool parameter."""
        from cortex.intelligence.principle_selector import PrincipleSelector
        ps = PrincipleSelector("QUERY", pool="principles")
        assert ps._pool == "principles"

    def test_lock_valid_pools_are_quotes_and_principles(self):
        """DRIFT LOCK: Valid pool values must be exactly {'quotes', 'principles'}."""
        from cortex.intelligence.principle_selector import _VALID_POOLS
        assert _VALID_POOLS == frozenset({"quotes", "principles"})

    def test_lock_ring_buffer_maxlen_is_10(self):
        """DRIFT LOCK: ring buffer maxlen must remain 10."""
        from cortex.intelligence.principle_selector import _ring_buffer
        assert _ring_buffer.maxlen == 10

    def test_lock_body_truncated_to_200_chars(self):
        """DRIFT LOCK: PrincipleSelector must truncate principle body to ≤200 chars.

        Governance: atom-principle.yaml body_max_chars=200, CORE-PRINCIPLE-TRIGGER brevity rule.
        """
        from cortex.intelligence.principle_selector import PrincipleSelector, _principles_cache
        import cortex.intelligence.principle_selector as ps_module

        # Inject a long-body principle into the cache directly to test truncation
        original_cache = ps_module._principles_cache
        long_body = "A" * 300  # 300 chars — must be truncated to ≤200
        ps_module._principles_cache = [{
            "id": "test-truncation",
            "title": "Truncation Test",
            "body": long_body,
            "domain": "universal",
            "tags": [],
            "intent_types": ["QUERY"],
            "relevance_weight": 1.0,
        }]
        try:
            ps = PrincipleSelector("QUERY", pool="principles")
            result = ps.select()
            assert len(result["body"]) <= 200, (
                f"body length {len(result['body'])} exceeds 200 char limit"
            )
            assert result["body"].endswith("…"), "truncated body must end with ellipsis"
        finally:
            ps_module._principles_cache = original_cache


class TestDriftLockPrincipleTriggerPolicy:
    """Drift locks for CORE-PRINCIPLE-TRIGGER policy (P2-004 audit contract).

    These locks enforce that operational compositions NEVER include atom-principle,
    and that the trigger policy YAML exists with the correct structure.
    SSOT: cortex-registry/core/principle-trigger-policy.yaml
    """

    def _load_policy(self) -> dict:
        return yaml.safe_load(TRIGGER_POLICY_PATH.read_text())

    def test_lock_trigger_policy_yaml_exists(self):
        """DRIFT LOCK: principle-trigger-policy.yaml must exist in cortex-registry/core/."""
        assert TRIGGER_POLICY_PATH.exists(), (
            "cortex-registry/core/principle-trigger-policy.yaml missing — "
            "CORE-PRINCIPLE-TRIGGER policy SSOT deleted"
        )

    def test_lock_policy_has_analysis_category(self):
        """DRIFT LOCK: policy must define 'analysis' category with principle_injection=True."""
        policy = self._load_policy()
        analysis = policy["intent_categories"]["analysis"]
        assert analysis["principle_injection"] is True

    def test_lock_policy_has_operations_category_blocked(self):
        """DRIFT LOCK: policy must define 'operations' category with principle_injection=False."""
        policy = self._load_policy()
        ops = policy["intent_categories"]["operations"]
        assert ops["principle_injection"] is False
        assert ops.get("override_allowed") is False

    def test_lock_operations_intents_cover_all_operational_comps(self):
        """DRIFT LOCK: operations category must include intents for all operational compositions."""
        policy = self._load_policy()
        ops_intents = set(policy["intent_categories"]["operations"]["intents"])
        # These are the core operational intents that must be blocked
        required = {"IMPLEMENT", "FIX", "REFACTOR", "DEBUG", "AUDIT", "HEALTH", "VACUUM"}
        missing = required - ops_intents
        assert not missing, f"Operations intent category missing: {missing}"

    def test_lock_brevity_policy_is_200_chars(self):
        """DRIFT LOCK: brevity.body_max_chars must be 200 (governance contract)."""
        policy = self._load_policy()
        assert policy["brevity"]["body_max_chars"] == 200

    def test_lock_no_operational_composition_includes_atom_principle(self):
        """DRIFT LOCK (P2-004): Operational compositions must NOT include atom-principle.

        This is the automated equivalent of audit check P2-004.
        If this test fails, an operational composition has drifted to include
        atom-principle — a CORE-PRINCIPLE-TRIGGER violation.
        """
        violations = []
        for filename in _OPERATIONAL_COMPOSITIONS:
            comp_path = COMPOSITIONS_DIR / filename
            if not comp_path.exists():
                continue  # composition not yet created — not a violation
            comp = yaml.safe_load(comp_path.read_text())
            atoms = [a["id"] for a in comp.get("atoms", [])]
            if "atom-principle" in atoms:
                violations.append(filename)

        assert not violations, (
            f"CORE-PRINCIPLE-TRIGGER violation (P2-004): atom-principle found in "
            f"operational composition(s): {violations}. "
            f"SSOT: cortex-registry/core/principle-trigger-policy.yaml"
        )

    def test_lock_atom_principle_omit_if_covers_operational_intents(self):
        """DRIFT LOCK: atom-principle.yaml omit_if must mention all operational intents."""
        atom = yaml.safe_load(ATOM_PRINCIPLE_PATH.read_text())
        omit_text = " ".join(atom["rendering_rules"].get("omit_if", []))
        required_mentions = ["IMPLEMENT", "FIX", "REFACTOR", "TDD", "DEBUG", "AUDIT", "HEALTH", "VACUUM"]
        missing = [intent for intent in required_mentions if intent not in omit_text]
        assert not missing, (
            f"atom-principle omit_if missing operational intent coverage: {missing}"
        )
