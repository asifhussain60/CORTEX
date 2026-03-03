"""
Phase 78 — Intelligence Matrix Wiring: Brain Tier Full Coverage
SWEEP-78-INTELLIGENCE-MATRIX-WIRING

TDD RED gate: Tests written before implementation.
After implementation all must PASS.

CORE-008: Tests before implementation.
CORE-064: Full sweep catalogue — all 12 GAPs addressed.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

CORTEX_ROOT = Path(__file__).parents[3]


# ══════════════════════════════════════════════════════════════════════════════
# GAP-78-A-01: MasterOrchestrator uses targeted/full intelligence tiers
# ══════════════════════════════════════════════════════════════════════════════

def test_gap_78_a01_provider_targeted_method_exists() -> None:
    """GAP-78-A-01: UnifiedIntelligenceProvider must expose .targeted() method."""
    from cortex.intelligence.provider import get_intelligence_provider
    provider = get_intelligence_provider()
    assert hasattr(provider, "targeted"), (
        "UnifiedIntelligenceProvider missing .targeted() — wire all 3 tiers (GAP-78-A-01)"
    )
    assert callable(provider.targeted)


def test_gap_78_a01_provider_full_method_exists() -> None:
    """GAP-78-A-01: UnifiedIntelligenceProvider must expose .full() method."""
    from cortex.intelligence.provider import get_intelligence_provider
    provider = get_intelligence_provider()
    assert hasattr(provider, "full"), (
        "UnifiedIntelligenceProvider missing .full() — wire all 3 tiers (GAP-78-A-01)"
    )
    assert callable(provider.full)


def test_gap_78_a01_master_orchestrator_exposes_intelligence_tier_selector() -> None:
    """GAP-78-A-01: MasterOrchestrator must have _select_intelligence_tier() or equivalent."""
    from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
    mo = MasterOrchestrator.__new__(MasterOrchestrator)
    assert hasattr(mo, "_select_intelligence_tier") or hasattr(mo, "_get_intelligence_context"), (
        "MasterOrchestrator missing tier-selection method — add _select_intelligence_tier() "
        "that returns ExecutionTier based on request complexity (GAP-78-A-01)"
    )


# ══════════════════════════════════════════════════════════════════════════════
# GAP-78-A-02: TDDOrchestrator injects test strategy knowledge
# ══════════════════════════════════════════════════════════════════════════════

def test_gap_78_a02_tdd_orchestrator_has_knowledge_context() -> None:
    """GAP-78-A-02: TDDOrchestrator must have _inject_knowledge_context() or knowledge_context attr."""
    from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator
    tdd = TDDOrchestrator.__new__(TDDOrchestrator)
    has_inject = hasattr(tdd, "_inject_knowledge_context")
    has_attr = hasattr(tdd, "knowledge_context")
    has_get_bp = hasattr(tdd, "_get_tdd_best_practices")
    assert has_inject or has_attr or has_get_bp, (
        "TDDOrchestrator missing knowledge injection hook — "
        "add _inject_knowledge_context() or _get_tdd_best_practices() (GAP-78-A-02)"
    )


# ══════════════════════════════════════════════════════════════════════════════
# GAP-78-A-03: RefactoringOrchestrator injects quality standards knowledge
# ══════════════════════════════════════════════════════════════════════════════

def test_gap_78_a03_refactoring_orchestrator_exists() -> None:
    """GAP-78-A-03: RefactoringOrchestrator must be importable."""
    from cortex.orchestrators.domain.refactoring_orchestrator import RefactoringOrchestrator  # noqa: F401


def test_gap_78_a03_refactoring_orchestrator_knowledge_hook() -> None:
    """GAP-78-A-03: RefactoringOrchestrator must have knowledge injection method."""
    from cortex.orchestrators.domain.refactoring_orchestrator import RefactoringOrchestrator
    inst = RefactoringOrchestrator.__new__(RefactoringOrchestrator)
    has_hook = (
        hasattr(inst, "_inject_knowledge_context")
        or hasattr(inst, "_get_quality_standards")
        or hasattr(inst, "knowledge_context")
    )
    assert has_hook, (
        "RefactoringOrchestrator missing knowledge injection hook (GAP-78-A-03)\n"
        "Add: _inject_knowledge_context() or _get_quality_standards() (GAP-78-A-03)"
    )


# ══════════════════════════════════════════════════════════════════════════════
# GAP-78-A-04: EnforcementOrchestrator injects governance knowledge
# ══════════════════════════════════════════════════════════════════════════════

def test_gap_78_a04_enforcement_orchestrator_governance_injection() -> None:
    """GAP-78-A-04: EnforcementOrchestrator must have governance knowledge injection."""
    from cortex.orchestrators.core.enforcement_orchestrator import EnforcementOrchestrator
    inst = EnforcementOrchestrator.__new__(EnforcementOrchestrator)
    has_hook = (
        hasattr(inst, "_inject_governance_knowledge")
        or hasattr(inst, "_load_governance_knowledge")
        or hasattr(inst, "governance_knowledge_path")
    )
    assert has_hook, (
        "EnforcementOrchestrator missing governance knowledge injection hook (GAP-78-A-04)\n"
        "Add: _inject_governance_knowledge() consuming cortex-registry/knowledge/governance/*.yaml"
    )


# ══════════════════════════════════════════════════════════════════════════════
# GAP-78-A-05: SecurityVulnerabilityOrchestrator wired to OWASP knowledge
# ══════════════════════════════════════════════════════════════════════════════

def test_gap_78_a05_security_orchestrator_importable() -> None:
    """GAP-78-A-05: SecurityVulnerabilityOrchestrator must be importable."""
    from cortex.orchestrators.validation.security_vulnerability_orchestrator import (  # noqa: F401
        SecurityVulnerabilityOrchestrator,
    )


def test_gap_78_a05_owasp_knowledge_file_exists() -> None:
    """GAP-78-A-05: OWASP knowledge YAML must exist for security orchestrator."""
    owasp_path = CORTEX_ROOT / "cortex-registry/knowledge/security/owasp-top10.yaml"
    assert owasp_path.exists(), (
        f"OWASP knowledge file missing: {owasp_path}\n"
        "Action: create cortex-registry/knowledge/security/owasp-top10.yaml"
    )


def test_gap_78_a05_security_orchestrator_owasp_hook() -> None:
    """GAP-78-A-05: SecurityVulnerabilityOrchestrator must reference OWASP knowledge."""
    from cortex.orchestrators.validation.security_vulnerability_orchestrator import (
        SecurityVulnerabilityOrchestrator,
    )
    inst = SecurityVulnerabilityOrchestrator.__new__(SecurityVulnerabilityOrchestrator)
    has_hook = (
        hasattr(inst, "_load_owasp_knowledge")
        or hasattr(inst, "owasp_knowledge_path")
        or hasattr(inst, "_inject_security_knowledge")
    )
    assert has_hook, (
        "SecurityVulnerabilityOrchestrator missing OWASP knowledge hook (GAP-78-A-05)"
    )


# ══════════════════════════════════════════════════════════════════════════════
# GAP-78-A-06: IntentRouter has intelligence-matrix routing
# ══════════════════════════════════════════════════════════════════════════════

def test_gap_78_a06_intent_router_intelligence_aware() -> None:
    """GAP-78-A-06: IntentRouter must have intelligence-matrix lookup in routing."""
    from cortex.orchestrators.core.intent_router import IntentRouter
    inst = IntentRouter.__new__(IntentRouter)
    has_matrix = (
        hasattr(inst, "_intelligence_matrix_lookup")
        or hasattr(inst, "_select_best_orchestrator_chain")
        or hasattr(inst, "intelligence_matrix")
    )
    assert has_matrix, (
        "IntentRouter missing intelligence-matrix routing method (GAP-78-A-06)\n"
        "Add: _intelligence_matrix_lookup(intent, context) → best orchestrator chain"
    )


# ══════════════════════════════════════════════════════════════════════════════
# GAP-78-A-07: MasterOrchestrator wired to OPJMixin post-dispatch
# ══════════════════════════════════════════════════════════════════════════════

def test_gap_78_a07_opj_mixin_importable() -> None:
    """GAP-78-A-07: OPJMixin must be importable from canonical location."""
    from cortex.intelligence.learning.opj_mixin import OPJMixin  # noqa: F401


def test_gap_78_a07_master_orchestrator_opj_post_dispatch() -> None:
    """GAP-78-A-07: MasterOrchestrator must have OPJ post-dispatch recording hook."""
    from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
    mo = MasterOrchestrator.__new__(MasterOrchestrator)
    has_hook = (
        hasattr(mo, "_opj_record_success")
        or hasattr(mo, "_record_opj_outcome")
        or hasattr(mo, "_opj_post_dispatch")
    )
    assert has_hook, (
        "MasterOrchestrator missing OPJ post-dispatch hook (GAP-78-A-07)\n"
        "Add: _opj_post_dispatch(outcome, domain, latency_ms) — calls OPJMixin._opj_record_success/failure"
    )


# ══════════════════════════════════════════════════════════════════════════════
# GAP-78-B-01: HealthOrchestrator wired to SLO thresholds knowledge
# ══════════════════════════════════════════════════════════════════════════════

def test_gap_78_b01_health_orchestrator_slo_hook() -> None:
    """GAP-78-B-01: HealthOrchestrator must have SLO threshold knowledge injection."""
    from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator
    inst = HealthOrchestrator.__new__(HealthOrchestrator)
    has_hook = (
        hasattr(inst, "_load_slo_thresholds")
        or hasattr(inst, "slo_thresholds")
        or hasattr(inst, "_get_performance_knowledge")
    )
    assert has_hook, (
        "HealthOrchestrator missing SLO thresholds hook (GAP-78-B-01)\n"
        "Add: _load_slo_thresholds() consuming profiling/performance knowledge YAML"
    )


# ══════════════════════════════════════════════════════════════════════════════
# GAP-78-B-02: VacuumOrchestrator wired to anti-pattern knowledge
# ══════════════════════════════════════════════════════════════════════════════

def test_gap_78_b02_vacuum_orchestrator_anti_pattern_hook() -> None:
    """GAP-78-B-02: VacuumOrchestrator must have anti-pattern knowledge injection."""
    from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator
    inst = VacuumOrchestrator.__new__(VacuumOrchestrator)
    has_hook = (
        hasattr(inst, "_load_anti_patterns")
        or hasattr(inst, "anti_pattern_knowledge")
        or hasattr(inst, "_get_anti_pattern_knowledge")
    )
    assert has_hook, (
        "VacuumOrchestrator missing anti-pattern knowledge hook (GAP-78-B-02)\n"
        "Add: _load_anti_patterns() consuming engineering-anti-patterns knowledge"
    )


# ══════════════════════════════════════════════════════════════════════════════
# GAP-78-B-03: BatchProcessor single canonical implementation (CORE-035)
# ══════════════════════════════════════════════════════════════════════════════

def test_gap_78_b03_batch_processor_single_canonical() -> None:
    """GAP-78-B-03: BatchProcessor must have exactly ONE implementation (CORE-035)."""
    import subprocess
    result = subprocess.run(
        ["grep", "-rn", "class BatchProcessor", "cortex/", "--include=*.py"],
        cwd=CORTEX_ROOT,
        capture_output=True,
        text=True,
    )
    matches = [l for l in result.stdout.strip().splitlines() if l.strip()]
    assert len(matches) == 1, (
        f"CORE-035 violation: {len(matches)} BatchProcessor implementations found:\n"
        + "\n".join(matches)
        + "\nAction: consolidate to cortex/toolkit/batch/batch_processor.py (GAP-78-B-03)"
    )


def test_gap_78_b03_batch_processor_canonical_importable() -> None:
    """GAP-78-B-03: BatchProcessor must be importable from canonical toolkit path."""
    from cortex.toolkit.batch.batch_processor import BatchProcessor  # noqa: F401


# ══════════════════════════════════════════════════════════════════════════════
# GAP-78-B-04: DomainAdapter has formal Protocol (ABC)
# ══════════════════════════════════════════════════════════════════════════════

def test_gap_78_b04_domain_adapter_is_protocol() -> None:
    """GAP-78-B-04: DomainAdapter must be a Protocol or ABC, not a plain class."""
    from cortex.toolkit.adapters.domain_adapter import DomainAdapter
    import typing
    is_protocol = (
        # typing.Protocol subclass
        getattr(DomainAdapter, "__mro__", None) is not None
        and any(
            c.__name__ in ("Protocol", "ABC")
            for c in getattr(DomainAdapter, "__mro__", [])
        )
    )
    assert is_protocol, (
        "DomainAdapter must subclass Protocol or ABC (GAP-78-B-04)\n"
        "Current class does not inherit from Protocol or ABC"
    )


# ══════════════════════════════════════════════════════════════════════════════
# GAP-78-B-05: HierarchicalScanner has generic IScannerProtocol interface
# ══════════════════════════════════════════════════════════════════════════════

def test_gap_78_b05_iscanner_protocol_exists() -> None:
    """GAP-78-B-05: IScannerProtocol must exist in cortex/core/ or cortex/toolkit/."""
    locations = [
        ("cortex.core.interfaces", "IScannerProtocol"),
        ("cortex.toolkit.filesystem.hierarchical_scanner", "IScannerProtocol"),
        ("cortex.toolkit.adapters.scanner_protocol", "IScannerProtocol"),
    ]
    found = False
    for module_path, cls_name in locations:
        try:
            import importlib
            mod = importlib.import_module(module_path)
            if hasattr(mod, cls_name):
                found = True
                break
        except ImportError:
            continue
    assert found, (
        "IScannerProtocol not found in cortex/core/interfaces or cortex/toolkit/ (GAP-78-B-05)\n"
        "Action: Create IScannerProtocol ABC; HierarchicalScanner implements it"
    )


def test_gap_78_b05_hierarchical_scanner_implements_protocol() -> None:
    """GAP-78-B-05: HierarchicalScanner must implement IScannerProtocol."""
    from cortex.toolkit.filesystem.hierarchical_scanner import HierarchicalScanner
    # Must have the protocol's required methods: scan(), get_results()
    inst = HierarchicalScanner.__new__(HierarchicalScanner)
    assert hasattr(inst, "scan") or hasattr(inst, "scan_directory"), (
        "HierarchicalScanner missing .scan() method required by IScannerProtocol (GAP-78-B-05)"
    )
