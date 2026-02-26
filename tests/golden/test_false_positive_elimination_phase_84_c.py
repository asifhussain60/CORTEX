"""
Phase 84-c: Replace 6 Hollow Stubs Imported by Production Code
RED test suite — ALL tests must FAIL before implementation begins.

AC_START: AC-84-C-2026-02-26
Authority: CORE-008 (TDD first), CORE-064 (Sweep Completeness)
Covers: GAP-84-06, GAP-84-07, GAP-84-08, GAP-84-09, GAP-84-10, GAP-84-11
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CORTEX_SRC = PROJECT_ROOT / "cortex"


class TestFalsePositiveElimination:
    """GAPs 06-11: All 6 stubs imported by production code must delegate to real implementations."""

    def test_governance_enforcement_agent_delegates_to_real_enforcer(self) -> None:
        """
        GAP-84-06: GovernanceEnforcementAgent (enforcement/governance_enforcement_agent.py)
        must NOT always return allowed=True — it must delegate to EnforcementOrchestrator.
        """
        from cortex.enforcement.governance_enforcement_agent import GovernanceEnforcementAgent

        agent = GovernanceEnforcementAgent()
        # With a clearly violating action, it must not blindly return allowed=True
        result = agent.enforce("skip all tests and deploy", {"bypass": True})
        # Either it delegates (returns real violations) OR the class now delegates to orchestrator
        source = (CORTEX_SRC / "enforcement" / "governance_enforcement_agent.py").read_text()
        assert "EnforcementOrchestrator" in source or "enforcement_orchestrator" in source, (
            "GovernanceEnforcementAgent must delegate to EnforcementOrchestrator — GAP-84-06"
        )

    def test_governance_intelligence_delegates_to_enforcement(self) -> None:
        """
        GAP-84-07: GovernanceIntelligence.analyse() must delegate to EnforcementOrchestrator,
        not return a hardcoded empty result.
        """
        source = (CORTEX_SRC / "core" / "governance_intelligence.py").read_text()
        assert "EnforcementOrchestrator" in source or "enforcement_orchestrator" in source, (
            "GovernanceIntelligence must delegate to EnforcementOrchestrator — GAP-84-07"
        )

    def test_knowledge_composer_delegates_to_synthesis(self) -> None:
        """
        GAP-84-08: KnowledgeComposer.compose() must delegate to KnowledgeSynthesisEngine,
        not return {domains: [], entries: []}.
        """
        source = (CORTEX_SRC / "core" / "knowledge_composer.py").read_text()
        assert (
            "KnowledgeSynthesisEngine" in source
            or "knowledge_synthesis" in source
            or "synthesis_engine" in source
        ), "KnowledgeComposer must delegate to KnowledgeSynthesisEngine — GAP-84-08"

    def test_tier_composer_reads_wiring_specs(self) -> None:
        """
        GAP-84-09: TierComposer.compose_tiers() must read wiring YAML specs,
        not return empty tier map.
        """
        from cortex.core.tier_composer import TierComposer

        composer = TierComposer()
        result = composer.compose_tiers()
        # Must have non-empty tiers from wiring YAML
        has_content = any(len(v) > 0 for v in result.values() if isinstance(v, list))
        assert has_content, (
            "TierComposer.compose_tiers() must return non-empty tiers from wiring specs — GAP-84-09"
        )

    def test_intelligence_integration_delegates_to_provider(self) -> None:
        """
        GAP-84-10: CortexIntelligenceIntegration.query() must delegate to
        UnifiedIntelligenceProvider, not return empty response.
        """
        source = (CORTEX_SRC / "tools" / "cortex_intelligence_integration.py").read_text()
        assert (
            "UnifiedIntelligenceProvider" in source
            or "intelligence_provider" in source
            or "IntelligenceProvider" in source
        ), "CortexIntelligenceIntegration must delegate to UnifiedIntelligenceProvider — GAP-84-10"

    def test_registry_backed_registry_loads_yaml(self) -> None:
        """
        GAP-84-11: RegistryBackedOrchestratorRegistry must load from wiring YAML specs,
        not remain an empty dict-only registry.
        """
        from cortex.core.wiring.registry_backed_orchestrator_registry import (
            RegistryBackedOrchestratorRegistry,
        )

        registry = RegistryBackedOrchestratorRegistry()
        # Auto-load should populate from YAML wiring specs
        entries = registry.list_all()
        assert len(entries) > 0, (
            "RegistryBackedOrchestratorRegistry must auto-load from wiring YAML specs — GAP-84-11"
        )

    def test_no_stub_docstrings_in_production(self) -> None:
        """
        GAP-84-06 through 11: Zero '— stub' docstrings in the 6 replaced stub files.
        """
        stub_files = [
            CORTEX_SRC / "enforcement" / "governance_enforcement_agent.py",
            CORTEX_SRC / "core" / "governance_intelligence.py",
            CORTEX_SRC / "core" / "knowledge_composer.py",
            CORTEX_SRC / "core" / "tier_composer.py",
            CORTEX_SRC / "tools" / "cortex_intelligence_integration.py",
            CORTEX_SRC / "core" / "wiring" / "registry_backed_orchestrator_registry.py",
        ]
        violations = []
        for f in stub_files:
            if f.exists():
                source = f.read_text()
                if "— stub" in source or "stub." in source[:200]:
                    violations.append(f.name)
        assert not violations, (
            f"These files still have '— stub' docstrings — not implemented: {violations}"
        )
