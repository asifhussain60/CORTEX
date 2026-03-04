"""
Phase 124-D: Golden drift-lock tests — schema stability + catalogue integrity.

These tests are DRIFT LOCKS: they encode invariants that must hold across all
future modifications to the principles library and atom definitions. If a drift
lock fails, it means an intentional schema change occurred and the lock must be
updated by explicit decision (not by accident).

RED gate: All tests fail before artefacts exist (or pass if artefacts already
          match the locked values — treated as GREEN since 124-A/B/C are complete).

Governance: CORE-008 (TDD), CORE-002 (no .md files), CORE-064 (sweep completeness).
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
