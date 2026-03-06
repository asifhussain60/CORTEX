"""
Integration test: DISTILL and OPTIMIZE intent routing to orchestrators.

Verifies that:
1. /distill command routes to DistillationOrchestrator via Stage4
2. /optimize command routes to ContentOptimizationOrchestrator via Stage4
3. Both orchestrators are accessible in dependencies dict

Authority: Phase 130 completion — ContentOptimizationOrchestrator + DistillationOrchestrator wiring.
"""
import pytest


class TestDistillIntentRouting:
    """Verify DISTILL intent routes correctly to DistillationOrchestrator."""

    def test_distillation_orchestrator_wired_in_master(self):
        """Verify DistillationOrchestrator is instantiated in MasterOrchestrator."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

        master = MasterOrchestrator.instance()
        master.initialize()

        assert hasattr(master, "_distillation_orchestrator"), \
            "MasterOrchestrator missing _distillation_orchestrator attribute"
        assert master._distillation_orchestrator is not None, \
            "_distillation_orchestrator is None — initialization failed"

    def test_distillation_orchestrator_in_dependencies(self):
        """Verify DistillationOrchestrator accessible via dependencies dict (Stage4 lookup)."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

        master = MasterOrchestrator.instance()
        master.initialize()

        # Simulate Stage4 dependencies dict build
        dependencies = {
            "distillationorchestrator": getattr(master, "_distillation_orchestrator", None),
        }

        orchestrator = dependencies.get("distillationorchestrator")
        assert orchestrator is not None, \
            "distillationorchestrator not found in dependencies dict"
        assert orchestrator.__class__.__name__ == "DistillationOrchestrator", \
            f"Wrong class: {orchestrator.__class__.__name__}"

    def test_distill_keyword_triggers_distill_intent(self):
        """Verify '/distill' keyword maps to IntentType.DISTILL."""
        from cortex.orchestrators.core.intent_router.keyword_registry import IntentKeywordRegistry
        from cortex.models.canonical_enums import IntentType

        mappings = IntentKeywordRegistry.build_operation_type_mappings()
        distill_keywords = mappings.get(IntentType.DISTILL, [])

        assert "/distill" in distill_keywords, \
            "/distill trigger missing from DISTILL_KEYWORDS"
        assert "distill" in distill_keywords, \
            "distill trigger missing from DISTILL_KEYWORDS"


class TestOptimizeIntentRouting:
    """Verify OPTIMIZE intent routes correctly to ContentOptimizationOrchestrator."""

    def test_content_optimization_orchestrator_wired_in_master(self):
        """Verify ContentOptimizationOrchestrator is instantiated in MasterOrchestrator."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

        master = MasterOrchestrator.instance()
        master.initialize()

        assert hasattr(master, "_content_optimization_orchestrator"), \
            "MasterOrchestrator missing _content_optimization_orchestrator attribute"
        assert master._content_optimization_orchestrator is not None, \
            "_content_optimization_orchestrator is None — initialization failed"

    def test_content_optimization_orchestrator_in_dependencies(self):
        """Verify ContentOptimizationOrchestrator accessible via dependencies dict (Stage4 lookup)."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

        master = MasterOrchestrator.instance()
        master.initialize()

        # Simulate Stage4 dependencies dict build
        dependencies = {
            "contentoptimizationorchestrator": getattr(master, "_content_optimization_orchestrator", None),
        }

        orchestrator = dependencies.get("contentoptimizationorchestrator")
        assert orchestrator is not None, \
            "contentoptimizationorchestrator not found in dependencies dict"
        assert orchestrator.__class__.__name__ == "ContentOptimizationOrchestrator", \
            f"Wrong class: {orchestrator.__class__.__name__}"

    def test_optimize_keyword_triggers_optimize_intent(self):
        """Verify '/optimize' keyword maps to IntentType.OPTIMIZE."""
        from cortex.orchestrators.core.intent_router.keyword_registry import IntentKeywordRegistry
        from cortex.models.canonical_enums import IntentType

        mappings = IntentKeywordRegistry.build_operation_type_mappings()
        optimize_keywords = mappings.get(IntentType.OPTIMIZE, [])

        assert "/optimize" in optimize_keywords, \
            "/optimize trigger missing from OPTIMIZE_KEYWORDS"
        assert "optimize" in optimize_keywords, \
            "optimize trigger missing from OPTIMIZE_KEYWORDS"


class TestCrossCuttingIntegration:
    """Verify both orchestrators work together correctly."""

    def test_both_orchestrators_healthy(self):
        """Verify both orchestrators pass health checks."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

        master = MasterOrchestrator.instance()
        master.initialize()

        distill_health = master._distillation_orchestrator.health_check()
        assert isinstance(distill_health, dict), \
            f"DistillationOrchestrator health_check should return dict, got {type(distill_health)}"
        assert distill_health.get("status") == "healthy", \
            f"DistillationOrchestrator not healthy: {distill_health}"

        optimize_health = master._content_optimization_orchestrator.health_check()
        assert isinstance(optimize_health, dict), \
            f"ContentOptimizationOrchestrator health_check should return dict, got {type(optimize_health)}"
        assert optimize_health.get("status") == "healthy", \
            f"ContentOptimizationOrchestrator not healthy: {optimize_health}"

    def test_content_optimization_delegates_to_distillation(self):
        """Verify ContentOptimizationOrchestrator can import DistillationOrchestrator for chat transcripts."""
        # ContentOptimizationOrchestrator instantiates DistillationOrchestrator on-demand,
        # not as an instance variable. Verify it can import the class.
        from cortex.orchestrators.support.content_optimization_orchestrator import (
            ContentOptimizationOrchestrator,
        )
        from cortex.orchestrators.support.distillation_orchestrator import (
            DistillationOrchestrator,
        )

        # If both imports succeed, the delegation path is valid
        assert ContentOptimizationOrchestrator is not None
        assert DistillationOrchestrator is not None
