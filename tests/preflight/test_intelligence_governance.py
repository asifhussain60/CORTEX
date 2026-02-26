"""Preflight: Intelligence layer + LENS + governance import tests.

Validates the intelligence pipeline, LENS analyzers, CORE rule loading,
and key cross-cutting modules are importable.

Tier: T0 (preflight) — runs in < 10s parallel.
"""
import pytest
from pathlib import Path


class TestIntelligenceLayerImports:
    """Validate intelligence layer imports."""

    def test_intelligence_matrix_builder_importable(self) -> None:
        """IntelligenceMatrixBuilder — capability cross-check matrix."""
        from cortex.intelligence.cross_cutting.intelligence_matrix_builder import IntelligenceMatrixBuilder
        assert IntelligenceMatrixBuilder is not None

    def test_domain_brain_importable(self) -> None:
        """DomainBrainAPI — domain intelligence."""
        from cortex.intelligence.domain_brain import DomainBrainAPI
        assert DomainBrainAPI is not None

    def test_intelligence_provider_importable(self) -> None:
        """UnifiedIntelligenceProvider — tiered intelligence."""
        from cortex.intelligence.provider import UnifiedIntelligenceProvider
        assert UnifiedIntelligenceProvider is not None

    def test_knowledge_synthesis_importable(self) -> None:
        """KnowledgeSynthesisEngine — knowledge synthesis."""
        from cortex.intelligence.knowledge.knowledge_synthesis_engine import KnowledgeSynthesisEngine
        assert KnowledgeSynthesisEngine is not None

    def test_opj_mixin_importable(self) -> None:
        """OPJMixin — Observation-Prediction-Judgement learning."""
        from cortex.intelligence.learning.opj_mixin import OPJMixin
        assert OPJMixin is not None


class TestLENSImports:
    """Validate LENS analysis pipeline imports."""

    def test_lens_module_importable(self) -> None:
        """LENS module root."""
        import cortex.lens
        assert cortex.lens is not None

    def test_lens_orchestrator_importable(self) -> None:
        """LENSOrchestrator — analysis pipeline coordinator."""
        from cortex.lens import LENSOrchestrator
        assert LENSOrchestrator is not None


class TestGovernanceImports:
    """Validate governance and CORE rule infrastructure."""

    def test_governance_module_importable(self) -> None:
        """Governance module root."""
        import cortex.governance
        assert cortex.governance is not None

    def test_core_rules_yaml_exists(self) -> None:
        """CORE rules YAML registry exists on disk."""
        rules_dir = Path("cortex-registry/core/tier0-skull")
        assert rules_dir.exists() or Path("cortex-registry/core").exists()

    def test_orchestrator_protocol_mixin_importable(self) -> None:
        """OrchestratorProtocolMixin — primary base class (Phase 58)."""
        from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin
        assert OrchestratorProtocolMixin is not None

    def test_workflow_engine_importable(self) -> None:
        """WorkflowEngine — FSM-based workflow execution."""
        from cortex.core.workflow_engine import WorkflowEngine
        assert WorkflowEngine is not None

    def test_result_monad_importable(self) -> None:
        """Result monad — Ok/Err for safe error handling."""
        from cortex.core.result import Result, Ok, Err
        assert Ok is not None
        assert Err is not None


class TestCorePackageImport:
    """Validate the canonical cortex package is importable."""

    def test_cortex_root_importable(self) -> None:
        """cortex package root."""
        import cortex
        assert cortex is not None

    def test_no_stale_package_imports(self) -> None:
        """Stale packages (cortex_intelligence, cortex_lens) must not exist."""
        import importlib
        for stale in ["cortex_intelligence", "cortex_lens"]:
            spec = importlib.util.find_spec(stale)
            assert spec is None, f"Stale package {stale} still importable"
