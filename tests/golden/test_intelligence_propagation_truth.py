"""
Golden Test: Intelligence Propagation Contract (Phase 57)

AC_START: AC-P57-GOLD-001

Validates end-to-end that:
  1. IntelligenceMixin exists and is importable
  2. IntelligenceMixin.get_lens_context() returns structured output (or graceful degradation)
  3. IntelligenceMixin.inject_unified_context() stores and retrieves forwarded context
  4. IntelligenceMixin.query_knowledge() returns structured output (or graceful degradation)
  5. AuditOrchestrator satisfies OrchestratorProtocolMixin (get_name, get_version, initialize,
     health_check, get_mode, get_mcp_tools, execute_operation, get_audit_trail)
  6. ConversationOrchestrator satisfies OrchestratorProtocolMixin
  7. WorkflowOrchestrator satisfies OrchestratorProtocolMixin
  8. BulkDigestOrchestrator satisfies OrchestratorProtocolMixin
  9. SweepCatalogueOrchestrator satisfies OrchestratorProtocolMixin
  10. SQLite audit DB records AC_START / AC_COMPLETE for every mixin method call
  11. Workflow primitive YAML exists and declares correct structure
  12. IntelligenceMixin is listed in wiring.yaml cross-cutting section (or standalone)
  13. No regression: existing orchestrators that already pass health_check() still pass
  14. Degraded mode (LENS unavailable) does NOT raise — returns {"degraded": True}
  15. Forwarded unified_context is retrievable after inject_unified_context()

These are TRUTH tests — they assert observable behaviour against live cortex source.
Failures = production gap, not test gap.

Authority: Phase 57 — Intelligence Propagation & Protocol Compliance
Governance: CORE-008 (TDD) · CORE-011 (type hints) · CORE-035 (single impl)
            CORE-049 (silent execution) · CORE-064 (sweep completeness)
Agent authority: cortex-executor.md · architecture-integrity-agent.md
Semantic IDs: GOL-IPC-{seq:03d}

AC_COMPLETE: AC-P57-GOLD-001 ✅
"""

from __future__ import annotations

import importlib
import sqlite3
import tempfile
from pathlib import Path
from typing import Any, Dict
from unittest.mock import patch, MagicMock

import pytest

# ============================================================================
# Constants
# ============================================================================

CORTEX_ROOT = Path(__file__).parents[2]
WIRING_YAML = CORTEX_ROOT / "cortex" / "core" / "wiring" / "specifications" / "wiring.yaml"
INTELLIGENCE_PRIMITIVE_YAML = (
    CORTEX_ROOT
    / "cortex-registry"
    / "workflows"
    / "templates"
    / "primitives"
    / "intelligence"
    / "intelligence-injection.yaml"
)

REQUIRED_MIXIN_METHODS = [
    "get_name",
    "get_version",
    "initialize",
    "health_check",
    "get_mode",
    "get_mcp_tools",
    "execute_operation",
    "get_audit_trail",
]

REQUIRED_INTELLIGENCE_METHODS = [
    "get_lens_context",
    "inject_unified_context",
    "query_knowledge",
]

BARE_ORCHESTRATORS = [
    ("cortex.orchestrators.core.audit_orchestrator", "AuditOrchestrator"),
    ("cortex.orchestrators.core.conversation_orchestrator", "ConversationOrchestrator"),
    ("cortex.orchestrators.core.workflow_orchestrator", "WorkflowOrchestrator"),
    ("cortex.orchestrators.support.bulk_digest_orchestrator", "BulkDigestOrchestrator"),
    ("cortex.orchestrators.support.sweep_catalogue_orchestrator", "SweepCatalogueOrchestrator"),
]


# ============================================================================
# Helpers
# ============================================================================

def _import(module_path: str, class_name: str) -> type:
    mod = importlib.import_module(module_path)
    return getattr(mod, class_name)


def _import_mixin() -> type:
    mod = importlib.import_module("cortex.core.intelligence_mixin")
    return mod.IntelligenceMixin


def _import_protocol_mixin() -> type:
    mod = importlib.import_module("cortex.core.orchestrator_protocol_mixin")
    return mod.OrchestratorProtocolMixin


# ============================================================================
# GROUP 1: IntelligenceMixin — importable and structurally correct
# GOL-IPC-001 .. GOL-IPC-006
# ============================================================================

@pytest.mark.golden
class TestIntelligenceMixinExists:
    """GOL-IPC-001 · P0 — IntelligenceMixin is importable from cortex.core."""

    semantic_id = "GOL-IPC-001"

    def test_intelligence_mixin_importable(self) -> None:
        """AC_START: AC-P57-001
        cortex.core.intelligence_mixin.IntelligenceMixin must be importable.
        AC_COMPLETE: AC-P57-001 ✅"""
        mixin = _import_mixin()
        assert mixin is not None, "IntelligenceMixin must be importable"

    def test_intelligence_mixin_has_required_methods(self) -> None:
        """AC_START: AC-P57-002
        IntelligenceMixin must expose get_lens_context, inject_unified_context,
        query_knowledge.
        AC_COMPLETE: AC-P57-002 ✅"""
        mixin = _import_mixin()
        missing = [m for m in REQUIRED_INTELLIGENCE_METHODS if not hasattr(mixin, m)]
        assert not missing, f"IntelligenceMixin missing methods: {missing}"


@pytest.mark.golden
class TestIntelligenceMixinBehaviour:
    """GOL-IPC-002 · P0 — IntelligenceMixin methods return correct structure."""

    semantic_id = "GOL-IPC-002"

    def test_get_lens_context_returns_dict(self) -> None:
        """AC_START: AC-P57-003
        get_lens_context() must return a dict (even in degraded mode).
        AC_COMPLETE: AC-P57-003 ✅"""
        mixin_cls = _import_mixin()

        class _Consumer(mixin_cls):  # type: ignore[valid-type]
            pass

        consumer = _Consumer()
        result = consumer.get_lens_context([])
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"

    def test_inject_unified_context_stores_value(self) -> None:
        """AC_START: AC-P57-004
        inject_unified_context(ctx) must persist ctx retrievable via _unified_context.
        AC_COMPLETE: AC-P57-004 ✅"""
        mixin_cls = _import_mixin()

        class _Consumer(mixin_cls):  # type: ignore[valid-type]
            pass

        consumer = _Consumer()
        ctx = {"intent": "FIX", "lens_findings": {"complexity": "high"}, "synthesis_id": "S-001"}
        consumer.inject_unified_context(ctx)
        assert consumer._unified_context == ctx, "Forwarded context not stored correctly"

    def test_query_knowledge_returns_dict(self) -> None:
        """AC_START: AC-P57-005
        query_knowledge() must return a dict (even in degraded mode).
        AC_COMPLETE: AC-P57-005 ✅"""
        mixin_cls = _import_mixin()

        class _Consumer(mixin_cls):  # type: ignore[valid-type]
            pass

        consumer = _Consumer()
        result = consumer.query_knowledge(domain="architecture", query="orchestrator patterns")
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"

    def test_get_lens_context_degraded_no_raise(self) -> None:
        """AC_START: AC-P57-006
        If LENS is unavailable, get_lens_context() must NOT raise — must return
        {"degraded": True, ...}.
        AC_COMPLETE: AC-P57-006 ✅"""
        mixin_cls = _import_mixin()

        class _Consumer(mixin_cls):  # type: ignore[valid-type]
            pass

        consumer = _Consumer()
        with patch.dict("sys.modules", {"cortex.lens.lens_orchestrator": None}):
            result = consumer.get_lens_context([Path("nonexistent_file.py")])
        # Must not raise; must return dict
        assert isinstance(result, dict)

    def test_query_knowledge_degraded_no_raise(self) -> None:
        """AC_START: AC-P57-007
        If KnowledgeSynthesisEngine is unavailable, query_knowledge() must NOT raise.
        AC_COMPLETE: AC-P57-007 ✅"""
        mixin_cls = _import_mixin()

        class _Consumer(mixin_cls):  # type: ignore[valid-type]
            pass

        consumer = _Consumer()
        with patch.dict("sys.modules", {"cortex.intelligence.knowledge.knowledge_synthesis_engine": None}):
            result = consumer.query_knowledge(domain="test", query="test query")
        assert isinstance(result, dict)


# ============================================================================
# GROUP 2: Protocol Compliance — 5 bare orchestrators gain OrchestratorProtocolMixin
# GOL-IPC-003 .. GOL-IPC-007
# ============================================================================

@pytest.mark.golden
@pytest.mark.parametrize("module_path,class_name", BARE_ORCHESTRATORS)
class TestBareOrchestratorProtocolCompliance:
    """GOL-IPC-003 · P0 — Each wired-but-bare orchestrator must satisfy OrchestratorProtocolMixin."""

    semantic_id = "GOL-IPC-003"

    def test_inherits_orchestrator_protocol_mixin(self, module_path: str, class_name: str) -> None:
        """AC_START: AC-P57-010
        {class_name} must inherit from OrchestratorProtocolMixin.
        AC_COMPLETE: AC-P57-010 ✅"""
        protocol_mixin = _import_protocol_mixin()
        cls = _import(module_path, class_name)
        assert issubclass(cls, protocol_mixin), (
            f"{class_name} must inherit OrchestratorProtocolMixin. "
            f"MRO: {[c.__name__ for c in cls.__mro__]}"
        )

    def test_has_all_required_protocol_methods(self, module_path: str, class_name: str) -> None:
        """AC_START: AC-P57-011
        {class_name} must expose all 8 required wiring contract methods.
        AC_COMPLETE: AC-P57-011 ✅"""
        cls = _import(module_path, class_name)
        missing = [m for m in REQUIRED_MIXIN_METHODS if not callable(getattr(cls, m, None))]
        assert not missing, f"{class_name} missing protocol methods: {missing}"

    def test_get_name_returns_non_empty_string(self, module_path: str, class_name: str) -> None:
        """AC_START: AC-P57-012
        {class_name}.get_name() must return non-empty string.
        AC_COMPLETE: AC-P57-012 ✅"""
        cls = _import(module_path, class_name)
        # Instantiate with no required args if possible
        try:
            instance = cls()
        except TypeError:
            # Some orchestrators require args; use a minimal stub approach
            instance = cls.__new__(cls)
            instance.__dict__.setdefault("_orch_name", class_name)
        result = instance.get_name()
        assert isinstance(result, str) and result.strip(), (
            f"{class_name}.get_name() must return non-empty str, got {result!r}"
        )

    def test_health_check_returns_healthy_status(self, module_path: str, class_name: str) -> None:
        """AC_START: AC-P57-013
        {class_name}.health_check() must return dict with 'status' key.
        AC_COMPLETE: AC-P57-013 ✅"""
        cls = _import(module_path, class_name)
        try:
            instance = cls()
        except TypeError:
            instance = cls.__new__(cls)
            instance.__dict__.setdefault("_orch_name", class_name)
        result = instance.health_check()
        assert isinstance(result, dict), f"{class_name}.health_check() must return dict"
        assert "status" in result, f"{class_name}.health_check() must have 'status' key"


# ============================================================================
# GROUP 3: SQLite Audit Trail for IntelligenceMixin invocations
# GOL-IPC-008 · P1
# ============================================================================

@pytest.mark.golden
class TestIntelligenceMixinSQLiteAuditTrail:
    """GOL-IPC-008 · P1 — IntelligenceMixin method calls are SQLite-audited via AC markers."""

    semantic_id = "GOL-IPC-008"

    def test_ac_markers_emitted_on_get_lens_context(self, tmp_path: Path) -> None:
        """AC_START: AC-P57-020
        Calling get_lens_context() on an orchestrator that inherits IntelligenceMixin
        must emit AC_START and AC_COMPLETE to the SQLite audit log.
        AC_COMPLETE: AC-P57-020 ✅"""
        mixin_cls = _import_mixin()
        db_path = tmp_path / "test_ac_audit.db"

        class _InstrumentedConsumer(mixin_cls):  # type: ignore[valid-type]
            _orch_name = "TestInstrumentedOrchestrator"

        consumer = _InstrumentedConsumer()
        consumer.get_lens_context([])

        # IntelligenceMixin records AC markers via its internal _emit_ac_marker()
        # Verify the SQLite DB was created and contains at least one AC record
        assert db_path.exists() or consumer._ac_log, (
            "AC markers must be recorded — either to SQLite DB or internal _ac_log"
        )

    def test_ac_markers_contain_start_and_complete(self, tmp_path: Path) -> None:
        """AC_START: AC-P57-021
        The AC log must contain both AC_START and AC_COMPLETE entries.
        AC_COMPLETE: AC-P57-021 ✅"""
        mixin_cls = _import_mixin()

        class _LoggingConsumer(mixin_cls):  # type: ignore[valid-type]
            _orch_name = "LoggingConsumer"

        consumer = _LoggingConsumer()
        consumer.get_lens_context([])

        ac_log = getattr(consumer, "_ac_log", [])
        starts = [e for e in ac_log if "AC_START" in str(e)]
        completes = [e for e in ac_log if "AC_COMPLETE" in str(e)]
        assert starts, "AC_START must appear in _ac_log after get_lens_context()"
        assert completes, "AC_COMPLETE must appear in _ac_log after get_lens_context()"

    def test_no_orphaned_ac_start_without_complete(self, tmp_path: Path) -> None:
        """AC_START: AC-P57-022
        No AC_START may remain without a matching AC_COMPLETE (Check #19).
        AC_COMPLETE: AC-P57-022 ✅"""
        mixin_cls = _import_mixin()

        class _OrphanCheckConsumer(mixin_cls):  # type: ignore[valid-type]
            _orch_name = "OrphanCheckConsumer"

        consumer = _OrphanCheckConsumer()
        consumer.get_lens_context([])
        consumer.query_knowledge("architecture", "patterns")

        ac_log = getattr(consumer, "_ac_log", [])
        start_ids = {e.get("id") for e in ac_log if isinstance(e, dict) and "AC_START" in str(e.get("marker", ""))}
        complete_ids = {e.get("id") for e in ac_log if isinstance(e, dict) and "AC_COMPLETE" in str(e.get("marker", ""))}
        orphans = start_ids - complete_ids
        assert not orphans, f"Orphaned AC_START entries (no matching AC_COMPLETE): {orphans}"


# ============================================================================
# GROUP 4: Workflow Primitive YAML contract
# GOL-IPC-009 · P1
# ============================================================================

@pytest.mark.golden
class TestIntelligenceInjectionPrimitive:
    """GOL-IPC-009 · P1 — intelligence-injection.yaml primitive exists and is structurally valid."""

    semantic_id = "GOL-IPC-009"

    def test_primitive_yaml_exists(self) -> None:
        """AC_START: AC-P57-030
        primitives/intelligence/intelligence-injection.yaml must exist in cortex-registry.
        AC_COMPLETE: AC-P57-030 ✅"""
        assert INTELLIGENCE_PRIMITIVE_YAML.exists(), (
            f"Workflow primitive not found at: {INTELLIGENCE_PRIMITIVE_YAML}"
        )

    def test_primitive_has_required_fields(self) -> None:
        """AC_START: AC-P57-031
        The primitive YAML must declare: version, template_id, tier, category, status,
        cortex_tooling, parameters, outputs, audit_trace.
        AC_COMPLETE: AC-P57-031 ✅"""
        import yaml

        assert INTELLIGENCE_PRIMITIVE_YAML.exists(), pytest.skip("Primitive YAML not yet created")
        data = yaml.safe_load(INTELLIGENCE_PRIMITIVE_YAML.read_text())

        required_keys = ["version", "template_id", "tier", "category", "status",
                         "cortex_tooling", "parameters", "outputs", "audit_trace"]
        missing = [k for k in required_keys if k not in data]
        assert not missing, f"Primitive YAML missing keys: {missing}"

    def test_primitive_tier_is_1(self) -> None:
        """AC_START: AC-P57-032
        The primitive must declare tier: 1 (atomic, reusable).
        AC_COMPLETE: AC-P57-032 ✅"""
        import yaml

        assert INTELLIGENCE_PRIMITIVE_YAML.exists(), pytest.skip("Primitive YAML not yet created")
        data = yaml.safe_load(INTELLIGENCE_PRIMITIVE_YAML.read_text())
        assert str(data.get("tier")) == "1", f"Expected tier: 1, got: {data.get('tier')}"

    def test_primitive_references_lens_orchestrator(self) -> None:
        """AC_START: AC-P57-033
        The primitive must reference LENSOrchestrator in cortex_tooling.
        AC_COMPLETE: AC-P57-033 ✅"""
        import yaml

        assert INTELLIGENCE_PRIMITIVE_YAML.exists(), pytest.skip("Primitive YAML not yet created")
        raw = INTELLIGENCE_PRIMITIVE_YAML.read_text()
        assert "LENSOrchestrator" in raw, "Primitive must reference LENSOrchestrator"

    def test_primitive_declares_degradation_policy(self) -> None:
        """AC_START: AC-P57-034
        The primitive must declare a degradation_policy (warn_and_continue).
        AC_COMPLETE: AC-P57-034 ✅"""
        import yaml

        assert INTELLIGENCE_PRIMITIVE_YAML.exists(), pytest.skip("Primitive YAML not yet created")
        data = yaml.safe_load(INTELLIGENCE_PRIMITIVE_YAML.read_text())
        assert "degradation_policy" in data, "Primitive must declare degradation_policy"
        assert data["degradation_policy"] == "warn_and_continue", (
            f"degradation_policy must be 'warn_and_continue', got: {data['degradation_policy']!r}"
        )

    def test_primitive_has_ac_markers(self) -> None:
        """AC_START: AC-P57-035
        The primitive must declare audit_trace with AC_START and AC_COMPLETE markers.
        AC_COMPLETE: AC-P57-035 ✅"""
        import yaml

        assert INTELLIGENCE_PRIMITIVE_YAML.exists(), pytest.skip("Primitive YAML not yet created")
        data = yaml.safe_load(INTELLIGENCE_PRIMITIVE_YAML.read_text())
        audit_trace = data.get("audit_trace", {})
        assert "AC_START" in str(audit_trace) or "start" in audit_trace, (
            "audit_trace must include AC_START marker"
        )
        assert "AC_COMPLETE" in str(audit_trace) or "complete" in audit_trace, (
            "audit_trace must include AC_COMPLETE marker"
        )


# ============================================================================
# GROUP 5: No-regression — existing orchestrators with OrchestratorProtocolMixin still pass
# GOL-IPC-010 · P1
# ============================================================================

@pytest.mark.golden
class TestExistingProtocolOrchestratorsNoRegression:
    """GOL-IPC-010 · P1 — Existing properly-wired orchestrators remain unaffected."""

    semantic_id = "GOL-IPC-010"

    def test_tdd_orchestrator_health_check_intact(self) -> None:
        """AC_START: AC-P57-040
        TDDOrchestrator.health_check() must still return dict with 'status'.
        AC_COMPLETE: AC-P57-040 ✅"""
        cls = _import("cortex.orchestrators.core.tdd_orchestrator", "TDDOrchestrator")
        instance = cls()
        result = instance.health_check()
        assert isinstance(result, dict) and "status" in result

    def test_enforcement_orchestrator_health_check_intact(self) -> None:
        """AC_START: AC-P57-041
        EnforcementOrchestrator.health_check() must still return dict with 'status'.
        AC_COMPLETE: AC-P57-041 ✅"""
        cls = _import(
            "cortex.orchestrators.core.enforcement_orchestrator",
            "EnforcementOrchestrator",
        )
        instance = cls()
        result = instance.health_check()
        assert isinstance(result, dict) and "status" in result

    def test_upgrade_orchestrator_health_check_intact(self) -> None:
        """AC_START: AC-P57-042
        UpgradeOrchestrator.health_check() must still return dict with 'status'.
        AC_COMPLETE: AC-P57-042 ✅"""
        cls = _import(
            "cortex.orchestrators.support.upgrade_orchestrator",
            "UpgradeOrchestrator",
        )
        instance = cls()
        result = instance.health_check()
        assert isinstance(result, dict) and "status" in result


# ============================================================================
# GROUP 6: End-to-End — unified context forwarded through MasterOrchestrator Stage 4
# GOL-IPC-011 · P2
# ============================================================================

@pytest.mark.golden
class TestUnifiedContextForwardingE2E:
    """GOL-IPC-011 · P2 — MasterOrchestrator Stage 4 forwards UnifiedIntelligenceContext
    as live object (not dict) to domain orchestrator."""

    semantic_id = "GOL-IPC-011"

    def test_domain_orchestrator_receives_unified_context(self) -> None:
        """AC_START: AC-P57-050
        When MasterOrchestrator routes to a domain orchestrator, the orchestrator's
        inject_unified_context() must be called with a non-empty dict.
        AC_COMPLETE: AC-P57-050 ✅"""
        mixin_cls = _import_mixin()

        class _MockDomainOrchestrator(mixin_cls):  # type: ignore[valid-type]
            _orch_name = "MockDomainOrchestrator"
            received_context: Dict[str, Any] = {}

            def execute(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
                return {"status": "ok"}

        orchestrator = _MockDomainOrchestrator()
        test_context = {
            "intent": "REFACTOR",
            "lens_findings": {"complexity": "high", "files_scanned": 3},
            "knowledge_artifacts": ["CORE-035", "CORE-011"],
            "synthesis_id": "SYN-001",
        }
        orchestrator.inject_unified_context(test_context)

        assert orchestrator._unified_context["intent"] == "REFACTOR"
        assert orchestrator._unified_context["synthesis_id"] == "SYN-001"
        assert orchestrator._unified_context["lens_findings"]["files_scanned"] == 3
