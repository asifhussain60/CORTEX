"""
Phase 123 — Registry Intelligence Engine
TDD Tests for IntelligenceFacade extension:
  - load_governance()   → GAP-123-01
  - load_workflows()    → GAP-123-02
  - load_patterns()     → GAP-123-03
  - load_plans()        → GAP-123-04 (MasterPlanIndex)
  - registry_index()    → GAP-123-05 (RegistryIndexEntry)

CORE Rules: CORE-008 (TDD-first), CORE-011, CORE-012
AC_START: AC-123-REGISTRY-INTELLIGENCE-ENGINE
"""
from __future__ import annotations

import pytest
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────────
# S1 — load_governance (GAP-123-01)
# ─────────────────────────────────────────────────────────────────────────────

class TestLoadGovernance:
    """Tests for IntelligenceFacade.load_governance()."""

    def test_load_governance_returns_rules_list(self):
        """load_governance() must return a non-empty list of governance rule dicts."""
        from cortex.intelligence.facade import IntelligenceFacade
        facade = IntelligenceFacade()
        rules = facade.load_governance()
        assert isinstance(rules, list), "load_governance() must return a list"
        assert len(rules) > 0, "load_governance() must return at least 1 rule"

    def test_load_governance_rule_has_rule_id(self):
        """Every rule dict returned must contain a 'rule_id' key."""
        from cortex.intelligence.facade import IntelligenceFacade
        facade = IntelligenceFacade()
        rules = facade.load_governance()
        for rule in rules:
            assert "rule_id" in rule, f"Rule missing 'rule_id': {rule}"

    def test_load_governance_contains_core_008(self):
        """load_governance() must return a rule with rule_id='CORE-008'."""
        from cortex.intelligence.facade import IntelligenceFacade
        facade = IntelligenceFacade()
        rules = facade.load_governance()
        rule_ids = [r.get("rule_id") for r in rules]
        assert "CORE-008" in rule_ids, (
            f"Expected CORE-008 in governance rules, got: {rule_ids}"
        )

    def test_load_governance_severity_filter(self):
        """load_governance(severity='blocked') must narrow results to blocked rules only."""
        from cortex.intelligence.facade import IntelligenceFacade
        facade = IntelligenceFacade()
        blocked = facade.load_governance(severity="blocked")
        assert isinstance(blocked, list), "Filtered result must be a list"
        for rule in blocked:
            assert rule.get("severity") == "blocked", (
                f"Expected severity='blocked', got: {rule.get('severity')}"
            )


# ─────────────────────────────────────────────────────────────────────────────
# S1 — load_workflows (GAP-123-02)
# ─────────────────────────────────────────────────────────────────────────────

class TestLoadWorkflows:
    """Tests for IntelligenceFacade.load_workflows()."""

    def test_load_workflows_returns_list(self):
        """load_workflows() must return a list."""
        from cortex.intelligence.facade import IntelligenceFacade
        facade = IntelligenceFacade()
        result = facade.load_workflows()
        assert isinstance(result, list), "load_workflows() must return a list"

    def test_load_workflows_category_filter_returns_list(self):
        """load_workflows(category='sdlc') must return a list (possibly empty, but typed)."""
        from cortex.intelligence.facade import IntelligenceFacade
        facade = IntelligenceFacade()
        result = facade.load_workflows(category="sdlc")
        assert isinstance(result, list), "Filtered workflows must be a list"

    def test_load_workflows_category_filter_consistent(self):
        """load_workflows(category='x') must only return templates in that category."""
        from cortex.intelligence.facade import IntelligenceFacade
        facade = IntelligenceFacade()
        all_workflows = facade.load_workflows()
        if not all_workflows:
            pytest.skip("No workflows discovered — cortex-registry empty or inaccessible")
        # If any workflow has a category field, filtering must be consistent
        categorised = [w for w in all_workflows if isinstance(w, dict) and "category" in w]
        if categorised:
            first_cat = categorised[0]["category"]
            filtered = facade.load_workflows(category=first_cat)
            for w in filtered:
                if isinstance(w, dict) and "category" in w:
                    assert w["category"] == first_cat


# ─────────────────────────────────────────────────────────────────────────────
# S1 — load_patterns (GAP-123-03)
# ─────────────────────────────────────────────────────────────────────────────

class TestLoadPatterns:
    """Tests for IntelligenceFacade.load_patterns()."""

    def test_load_patterns_returns_list(self):
        """load_patterns() must return a list."""
        from cortex.intelligence.facade import IntelligenceFacade
        facade = IntelligenceFacade()
        result = facade.load_patterns()
        assert isinstance(result, list), "load_patterns() must return a list"

    def test_load_patterns_tag_filter_returns_list(self):
        """load_patterns(tag='tdd') must return a list (possibly empty)."""
        from cortex.intelligence.facade import IntelligenceFacade
        facade = IntelligenceFacade()
        result = facade.load_patterns(tag="tdd")
        assert isinstance(result, list), "Tag-filtered patterns must be a list"

    def test_load_patterns_tag_filter_consistent(self):
        """load_patterns(tag='x') must only return patterns containing that tag."""
        from cortex.intelligence.facade import IntelligenceFacade
        facade = IntelligenceFacade()
        result = facade.load_patterns(tag="tdd")
        for p in result:
            if isinstance(p, dict):
                assert "tdd" in p.get("tags", []), (
                    f"Pattern returned by tag='tdd' filter does not have 'tdd' in tags: {p}"
                )


# ─────────────────────────────────────────────────────────────────────────────
# Singleton contract (all sub-phases)
# ─────────────────────────────────────────────────────────────────────────────

class TestFacadeSingletonContract:
    """Singleton must be preserved across new delegation methods."""

    def test_facade_singleton_shared_state(self):
        """Two IntelligenceFacade() calls must return the same object."""
        from cortex.intelligence.facade import IntelligenceFacade
        f1 = IntelligenceFacade()
        f2 = IntelligenceFacade()
        assert f1 is f2, "IntelligenceFacade must be a singleton"

    def test_get_intelligence_facade_returns_same_instance(self):
        """get_intelligence_facade() must return the same singleton."""
        from cortex.intelligence.facade import IntelligenceFacade, get_intelligence_facade
        direct = IntelligenceFacade()
        via_helper = get_intelligence_facade()
        assert direct is via_helper, "get_intelligence_facade() must return the singleton"


# ─────────────────────────────────────────────────────────────────────────────
# S2 — load_plans / MasterPlanIndex (GAP-123-04)
# ─────────────────────────────────────────────────────────────────────────────

class TestLoadPlans:
    """Tests for IntelligenceFacade.load_plans() and MasterPlanIndex."""

    def test_load_plans_returns_master_plan_index(self):
        """load_plans() must return a MasterPlanIndex with a phases attribute."""
        from cortex.intelligence.facade import IntelligenceFacade
        from cortex.intelligence.models.master_plan_index import MasterPlanIndex
        facade = IntelligenceFacade()
        result = facade.load_plans()
        assert isinstance(result, MasterPlanIndex), (
            f"Expected MasterPlanIndex, got {type(result)}"
        )
        assert hasattr(result, "phases"), "MasterPlanIndex must have 'phases' attribute"

    def test_master_plan_index_has_phases_list(self):
        """MasterPlanIndex.phases must be a non-empty list."""
        from cortex.intelligence.facade import IntelligenceFacade
        facade = IntelligenceFacade()
        index = facade.load_plans()
        assert isinstance(index.phases, list), "phases must be a list"
        assert len(index.phases) > 0, "phases list must not be empty"

    def test_master_plan_index_has_completed_phases(self):
        """MasterPlanIndex.phases must contain at least 1 COMPLETE entry."""
        from cortex.intelligence.facade import IntelligenceFacade
        facade = IntelligenceFacade()
        index = facade.load_plans()
        completed = [p for p in index.phases if getattr(p, "status", None) == "COMPLETE"]
        assert len(completed) >= 1, (
            f"Expected at least 1 COMPLETE phase, got {len(completed)}"
        )

    def test_master_plan_index_has_planned_phases(self):
        """MasterPlanIndex.phases must contain at least 1 PLANNED entry (phase-123)."""
        from cortex.intelligence.facade import IntelligenceFacade
        facade = IntelligenceFacade()
        index = facade.load_plans()
        planned = [p for p in index.phases if getattr(p, "status", None) == "PLANNED"]
        assert len(planned) >= 1, (
            f"Expected at least 1 PLANNED phase, got {len(planned)}"
        )

    def test_load_plans_filter_by_status(self):
        """load_plans(status='PLANNED') must return only PLANNED phases."""
        from cortex.intelligence.facade import IntelligenceFacade
        facade = IntelligenceFacade()
        index = facade.load_plans(status="PLANNED")
        for phase in index.phases:
            assert getattr(phase, "status", None) == "PLANNED", (
                f"Expected PLANNED, got {phase.status!r}"
            )

    def test_master_plan_index_line_count_within_contract(self):
        """MasterPlanIndex.source_line_count must be ≤500 (THIN INDEX CONTRACT)."""
        from cortex.intelligence.facade import IntelligenceFacade
        facade = IntelligenceFacade()
        index = facade.load_plans()
        assert hasattr(index, "source_line_count"), (
            "MasterPlanIndex must expose source_line_count"
        )
        assert index.source_line_count <= 500, (
            f"cortex-master.yaml exceeds 500-line contract: {index.source_line_count} lines"
        )

    def test_phase_entry_has_required_fields(self):
        """Each PhaseEntry must have id, title, status, priority fields."""
        from cortex.intelligence.facade import IntelligenceFacade
        facade = IntelligenceFacade()
        index = facade.load_plans()
        for phase in index.phases[:3]:  # check first 3 only for speed
            assert hasattr(phase, "id"), f"PhaseEntry missing 'id': {phase}"
            assert hasattr(phase, "title"), f"PhaseEntry missing 'title': {phase}"
            assert hasattr(phase, "status"), f"PhaseEntry missing 'status': {phase}"
            assert hasattr(phase, "priority"), f"PhaseEntry missing 'priority': {phase}"


# ─────────────────────────────────────────────────────────────────────────────
# S3 — registry_index / RegistryIndexEntry (GAP-123-05)
# ─────────────────────────────────────────────────────────────────────────────

class TestRegistryIndex:
    """Tests for IntelligenceFacade.registry_index() and RegistryIndexEntry."""

    def test_registry_index_returns_list(self):
        """registry_index() must return a non-empty list of RegistryIndexEntry."""
        from cortex.intelligence.facade import IntelligenceFacade
        from cortex.intelligence.models.registry_index import RegistryIndexEntry
        facade = IntelligenceFacade()
        result = facade.registry_index()
        assert isinstance(result, list), "registry_index() must return a list"
        assert len(result) > 0, "registry_index() must return at least 1 entry"
        assert isinstance(result[0], RegistryIndexEntry), (
            f"Expected RegistryIndexEntry, got {type(result[0])}"
        )

    def test_registry_index_has_governance_domain(self):
        """registry_index() result must contain entries with domain='governance'."""
        from cortex.intelligence.facade import IntelligenceFacade
        facade = IntelligenceFacade()
        result = facade.registry_index()
        domains = [e.domain for e in result]
        assert "governance" in domains, (
            f"Expected 'governance' domain in index, got domains: {set(domains)}"
        )

    def test_registry_index_has_workflows_domain(self):
        """registry_index() result must contain entries with domain='workflows'."""
        from cortex.intelligence.facade import IntelligenceFacade
        facade = IntelligenceFacade()
        result = facade.registry_index()
        domains = [e.domain for e in result]
        assert "workflows" in domains, (
            f"Expected 'workflows' domain in index, got domains: {set(domains)}"
        )

    def test_registry_index_has_knowledge_domain(self):
        """registry_index() result must contain entries with domain='knowledge'."""
        from cortex.intelligence.facade import IntelligenceFacade
        facade = IntelligenceFacade()
        result = facade.registry_index()
        domains = [e.domain for e in result]
        assert "knowledge" in domains, (
            f"Expected 'knowledge' domain in index, got domains: {set(domains)}"
        )

    def test_registry_index_entry_has_required_fields(self):
        """Every RegistryIndexEntry must have path, domain, schema_type, file_name."""
        from cortex.intelligence.facade import IntelligenceFacade
        facade = IntelligenceFacade()
        result = facade.registry_index()
        for entry in result[:5]:  # check first 5 for speed
            assert hasattr(entry, "path"), f"RegistryIndexEntry missing 'path': {entry}"
            assert hasattr(entry, "domain"), f"RegistryIndexEntry missing 'domain': {entry}"
            assert hasattr(entry, "schema_type"), f"RegistryIndexEntry missing 'schema_type': {entry}"
            assert hasattr(entry, "file_name"), f"RegistryIndexEntry missing 'file_name': {entry}"

    def test_registry_index_cached(self):
        """Two consecutive registry_index() calls must return the same list object."""
        from cortex.intelligence.facade import IntelligenceFacade
        facade = IntelligenceFacade()
        first = facade.registry_index()
        second = facade.registry_index()
        assert first is second, (
            "registry_index() must return cached result on second call"
        )

    def test_registry_index_domain_filter(self):
        """registry_index(domain='governance') must only return governance entries."""
        from cortex.intelligence.facade import IntelligenceFacade
        facade = IntelligenceFacade()
        result = facade.registry_index(domain="governance")
        assert isinstance(result, list), "Filtered result must be a list"
        for entry in result:
            assert entry.domain == "governance", (
                f"Expected domain='governance', got '{entry.domain}'"
            )
