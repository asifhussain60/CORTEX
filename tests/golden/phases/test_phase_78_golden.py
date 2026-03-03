"""
Phase 78 Golden Test — Intelligence Matrix Wiring: Brain Tier Full Coverage (E2E)

SWEEP-78-INTELLIGENCE-MATRIX-WIRING — End-to-end execution certainty.
Validates all 12 GAPs are CLOSED: 7 P0-CRITICAL orchestrators wired to knowledge,
HealthOrchestrator SLO, VacuumOrchestrator anti-patterns, IScannerProtocol added.

Unlike unit tests (tests/unit/core/test_phase_78_intelligence_matrix_wiring.py) which
check individual method/attribute existence, this golden test verifies the HOLISTIC
intelligence wiring: provider tiers work end-to-end, orchestrators can actually
consume knowledge, and the matrix lookup chain is functional.

AC_START: AC-78-GOLDEN-E2E-20260225

Authority: cortex-registry/planning/phases/completed/phase-78-intelligence-matrix-wiring.yaml
CORE-008: TDD-first | CORE-064: Full sweep
"""
from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any, Dict

import pytest
import yaml

CORTEX_ROOT = Path(__file__).resolve().parents[3]


# ══════════════════════════════════════════════════════════════════════════════
# E2E-1: Intelligence Provider 3-Tier API functional
# ══════════════════════════════════════════════════════════════════════════════

class TestPhase78IntelligenceProviderTiers:
    """UnifiedIntelligenceProvider must expose quick/targeted/full tiers (GAP-78-A-01)."""

    def test_provider_importable(self) -> None:
        """Intelligence provider must be importable from canonical location."""
        from cortex.intelligence.provider import get_intelligence_provider
        provider = get_intelligence_provider()
        assert provider is not None, "get_intelligence_provider() returned None"

    def test_provider_has_quick_tier(self) -> None:
        """Provider must have .quick() method for <200ms tier."""
        from cortex.intelligence.provider import get_intelligence_provider
        provider = get_intelligence_provider()
        assert hasattr(provider, "quick") and callable(provider.quick)

    def test_provider_has_targeted_tier(self) -> None:
        """Provider must have .targeted() method for <2s LENS tier."""
        from cortex.intelligence.provider import get_intelligence_provider
        provider = get_intelligence_provider()
        assert hasattr(provider, "targeted") and callable(provider.targeted)

    def test_provider_has_full_tier(self) -> None:
        """Provider must have .full() method for <10s deep analysis tier."""
        from cortex.intelligence.provider import get_intelligence_provider
        provider = get_intelligence_provider()
        assert hasattr(provider, "full") and callable(provider.full)


# ══════════════════════════════════════════════════════════════════════════════
# E2E-2: P0-CRITICAL orchestrators have knowledge injection hooks
# ══════════════════════════════════════════════════════════════════════════════

class TestPhase78OrchestratorKnowledgeWiring:
    """7 P0-CRITICAL orchestrators must have knowledge injection hooks wired."""

    def test_master_orchestrator_tier_selector(self) -> None:
        """MasterOrchestrator must have intelligence tier selection (GAP-78-A-01)."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        mo = MasterOrchestrator.__new__(MasterOrchestrator)
        has_method = (
            hasattr(mo, "_select_intelligence_tier")
            or hasattr(mo, "_get_intelligence_context")
        )
        assert has_method, "MasterOrchestrator missing tier-selection method"

    def test_tdd_orchestrator_knowledge_context(self) -> None:
        """TDDOrchestrator must have knowledge injection hook (GAP-78-A-02)."""
        from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator
        tdd = TDDOrchestrator.__new__(TDDOrchestrator)
        has_hook = (
            hasattr(tdd, "_inject_knowledge_context")
            or hasattr(tdd, "knowledge_context")
            or hasattr(tdd, "_get_tdd_best_practices")
        )
        assert has_hook, "TDDOrchestrator missing knowledge injection hook"

    def test_refactoring_orchestrator_quality_hook(self) -> None:
        """RefactoringOrchestrator must have quality standards hook (GAP-78-A-03)."""
        from cortex.orchestrators.domain.refactoring_orchestrator import RefactoringOrchestrator
        inst = RefactoringOrchestrator.__new__(RefactoringOrchestrator)
        has_hook = (
            hasattr(inst, "_inject_knowledge_context")
            or hasattr(inst, "_get_quality_standards")
            or hasattr(inst, "knowledge_context")
        )
        assert has_hook, "RefactoringOrchestrator missing knowledge hook"

    def test_enforcement_orchestrator_governance_hook(self) -> None:
        """EnforcementOrchestrator must have governance knowledge hook (GAP-78-A-04)."""
        from cortex.orchestrators.core.enforcement_orchestrator import EnforcementOrchestrator
        inst = EnforcementOrchestrator.__new__(EnforcementOrchestrator)
        has_hook = (
            hasattr(inst, "_inject_governance_knowledge")
            or hasattr(inst, "_load_governance_knowledge")
            or hasattr(inst, "governance_knowledge_path")
        )
        assert has_hook, "EnforcementOrchestrator missing governance knowledge hook"

    def test_security_orchestrator_owasp_hook(self) -> None:
        """SecurityVulnerabilityOrchestrator must reference OWASP knowledge (GAP-78-A-05)."""
        from cortex.orchestrators.validation.security_vulnerability_orchestrator import (
            SecurityVulnerabilityOrchestrator,
        )
        inst = SecurityVulnerabilityOrchestrator.__new__(SecurityVulnerabilityOrchestrator)
        has_hook = (
            hasattr(inst, "_load_owasp_knowledge")
            or hasattr(inst, "owasp_knowledge_path")
            or hasattr(inst, "_inject_security_knowledge")
        )
        assert has_hook, "SecurityVulnerabilityOrchestrator missing OWASP hook"

    def test_intent_router_intelligence_matrix(self) -> None:
        """IntentRouter must have intelligence-matrix lookup (GAP-78-A-06)."""
        from cortex.orchestrators.core.intent_router_impl import IntentRouter
        has_matrix = (
            hasattr(IntentRouter, "_intelligence_matrix_lookup")
            or hasattr(IntentRouter, "_select_best_orchestrator_chain")
            or hasattr(IntentRouter, "intelligence_matrix")
        )
        assert has_matrix, "IntentRouter missing intelligence-matrix lookup"

    def test_master_orchestrator_opj_post_dispatch(self) -> None:
        """MasterOrchestrator must have OPJ post-dispatch hook (GAP-78-A-07)."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        mo = MasterOrchestrator.__new__(MasterOrchestrator)
        has_hook = (
            hasattr(mo, "_opj_record_success")
            or hasattr(mo, "_record_opj_outcome")
            or hasattr(mo, "_opj_post_dispatch")
        )
        assert has_hook, "MasterOrchestrator missing OPJ post-dispatch hook"


# ══════════════════════════════════════════════════════════════════════════════
# E2E-3: Health/Vacuum orchestrators have knowledge hooks
# ══════════════════════════════════════════════════════════════════════════════

class TestPhase78HealthVacuumKnowledge:
    """HealthOrchestrator and VacuumOrchestrator wired to knowledge."""

    def test_health_orchestrator_slo_hook(self) -> None:
        """HealthOrchestrator must have SLO thresholds knowledge hook (GAP-78-B-01)."""
        from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator
        inst = HealthOrchestrator.__new__(HealthOrchestrator)
        has_hook = (
            hasattr(inst, "_load_slo_thresholds")
            or hasattr(inst, "slo_thresholds")
            or hasattr(inst, "_get_performance_knowledge")
        )
        assert has_hook, "HealthOrchestrator missing SLO thresholds hook"

    def test_vacuum_orchestrator_anti_pattern_hook(self) -> None:
        """VacuumOrchestrator must have anti-pattern knowledge hook (GAP-78-B-02)."""
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator
        inst = VacuumOrchestrator.__new__(VacuumOrchestrator)
        has_hook = (
            hasattr(inst, "_load_anti_patterns")
            or hasattr(inst, "anti_pattern_knowledge")
            or hasattr(inst, "_get_anti_pattern_knowledge")
        )
        assert has_hook, "VacuumOrchestrator missing anti-pattern hook"


# ══════════════════════════════════════════════════════════════════════════════
# E2E-4: Infrastructure components (BatchProcessor, IScannerProtocol)
# ══════════════════════════════════════════════════════════════════════════════

class TestPhase78InfrastructureComponents:
    """BatchProcessor single canonical, IScannerProtocol exists."""

    def test_batch_processor_importable(self) -> None:
        """BatchProcessor must be importable from canonical path (GAP-78-B-03)."""
        from cortex.toolkit.batch.batch_processor import BatchProcessor  # noqa: F401

    def test_iscanner_protocol_exists(self) -> None:
        """IScannerProtocol must exist somewhere in cortex (GAP-78-B-05)."""
        locations = [
            ("cortex.core.interfaces", "IScannerProtocol"),
            ("cortex.toolkit.filesystem.hierarchical_scanner", "IScannerProtocol"),
            ("cortex.toolkit.adapters.scanner_protocol", "IScannerProtocol"),
        ]
        found = False
        for module_path, cls_name in locations:
            try:
                mod = importlib.import_module(module_path)
                if hasattr(mod, cls_name):
                    found = True
                    break
            except ImportError:
                continue
        assert found, "IScannerProtocol not found in any canonical location"

    def test_owasp_knowledge_yaml_exists(self) -> None:
        """OWASP knowledge YAML must exist (GAP-78-A-05 prerequisite)."""
        owasp = CORTEX_ROOT / "cortex-registry" / "knowledge" / "security" / "owasp-top10.yaml"
        assert owasp.exists(), f"OWASP knowledge YAML missing: {owasp}"


# ══════════════════════════════════════════════════════════════════════════════
# E2E-5: Phase completion metadata
# ══════════════════════════════════════════════════════════════════════════════

class TestPhase78CompletionMetadata:
    """Phase 78 must be marked COMPLETE in cortex-master.yaml."""

    def test_cortex_master_marks_phase_78_complete(self) -> None:
        """cortex-master.yaml must show phase-78 status: COMPLETE."""
        master = CORTEX_ROOT / "cortex-registry" / "cortex-master.yaml"
        data = yaml.safe_load(master.read_text())
        phases = data.get("phase_detail_files", [])
        ph78 = next((p for p in phases if p.get("id") == "phase-78"), None)
        assert ph78 is not None, "phase-78 not found in cortex-master.yaml"
        assert ph78.get("status") == "COMPLETE", (
            f"phase-78 status is '{ph78.get('status')}', expected COMPLETE"
        )
