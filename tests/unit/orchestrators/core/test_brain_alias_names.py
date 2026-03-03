"""
Phase 102-a: Brain Naming Cleanup — TDD RED tests.

Asserts that domain-appropriate alias names are importable alongside
the original brain-prefixed names. No caller breaks; new aliases
provide the canonical forward path.

CORE-008: Tests written before aliases implemented (TDD RED gate).
SWEEP-102-SUBSYSTEM-BOUNDARIES / GAP-102-04
"""
import pytest


# ── IntelligenceStateManager (was BrainStateManager) ─────────────────────────

class TestIntelligenceStateManagerAlias:
    """Alias: BrainStateManager → IntelligenceStateManager."""

    def test_intelligence_state_manager_importable(self) -> None:
        """IntelligenceStateManager must be importable from brain_state_manager module."""
        from cortex.core.brain_state_manager import IntelligenceStateManager  # noqa: F401
        assert IntelligenceStateManager is not None

    def test_intelligence_state_manager_is_brain_state_manager(self) -> None:
        """Alias must resolve to the same class object."""
        from cortex.core.brain_state_manager import BrainStateManager, IntelligenceStateManager
        assert IntelligenceStateManager is BrainStateManager

    def test_original_brain_state_manager_still_importable(self) -> None:
        """Original name must remain importable (no breakage)."""
        from cortex.core.brain_state_manager import BrainStateManager  # noqa: F401
        assert BrainStateManager is not None


# ── CollaborationOrchestrator (was CentralBrainOrchestrator) ─────────────────

class TestCollaborationOrchestratorAlias:
    """Alias: CentralBrainOrchestrator → CollaborationOrchestrator."""

    def test_collaboration_orchestrator_importable(self) -> None:
        """CollaborationOrchestrator must be importable."""
        from cortex.orchestrators.core.central_brain_orchestrator import CollaborationOrchestrator  # noqa: F401
        assert CollaborationOrchestrator is not None

    def test_collaboration_orchestrator_is_central_brain(self) -> None:
        """Alias must resolve to the same class."""
        from cortex.orchestrators.core.central_brain_orchestrator import (
            CentralBrainOrchestrator,
            CollaborationOrchestrator,
        )
        assert CollaborationOrchestrator is CentralBrainOrchestrator

    def test_original_central_brain_orchestrator_still_importable(self) -> None:
        """Original name must remain importable."""
        from cortex.orchestrators.core.central_brain_orchestrator import CentralBrainOrchestrator  # noqa: F401
        assert CentralBrainOrchestrator is not None


# ── IntelligenceHealthOrchestrator (was BrainHealthOrchestrator) ─────────────

class TestIntelligenceHealthOrchestratorAlias:
    """Alias: BrainHealthOrchestrator → IntelligenceHealthOrchestrator."""

    def test_intelligence_health_orchestrator_importable(self) -> None:
        """IntelligenceHealthOrchestrator must be importable."""
        from cortex.orchestrators.core.brain_health_orchestrator import IntelligenceHealthOrchestrator  # noqa: F401
        assert IntelligenceHealthOrchestrator is not None

    def test_intelligence_health_orchestrator_is_brain_health(self) -> None:
        """Alias must resolve to the same class."""
        from cortex.orchestrators.core.brain_health_orchestrator import (
            BrainHealthOrchestrator,
            IntelligenceHealthOrchestrator,
        )
        assert IntelligenceHealthOrchestrator is BrainHealthOrchestrator

    def test_original_brain_health_orchestrator_still_importable(self) -> None:
        """Original name must remain importable."""
        from cortex.orchestrators.core.brain_health_orchestrator import BrainHealthOrchestrator  # noqa: F401
        assert BrainHealthOrchestrator is not None


# ── IntelligenceHealthMetrics (was BrainHealthMetrics) ───────────────────────

class TestIntelligenceHealthMetricsAlias:
    """Alias: BrainHealthMetrics → IntelligenceHealthMetrics."""

    def test_intelligence_health_metrics_importable(self) -> None:
        """IntelligenceHealthMetrics must be importable."""
        from cortex.infrastructure.brain_health_metrics import IntelligenceHealthMetrics  # noqa: F401
        assert IntelligenceHealthMetrics is not None

    def test_intelligence_health_metrics_is_brain_health_metrics(self) -> None:
        """Alias must resolve to the same class."""
        from cortex.infrastructure.brain_health_metrics import (
            BrainHealthMetrics,
            IntelligenceHealthMetrics,
        )
        assert IntelligenceHealthMetrics is BrainHealthMetrics

    def test_original_brain_health_metrics_still_importable(self) -> None:
        """Original name must remain importable."""
        from cortex.infrastructure.brain_health_metrics import BrainHealthMetrics  # noqa: F401
        assert BrainHealthMetrics is not None


# ── CollaborationStore (was SharedBrainStore) ─────────────────────────────────

class TestCollaborationStoreAlias:
    """Alias: SharedBrainStore → CollaborationStore."""

    def test_collaboration_store_importable(self) -> None:
        """CollaborationStore must be importable."""
        from cortex.infrastructure.shared_brain_store import CollaborationStore  # noqa: F401
        assert CollaborationStore is not None

    def test_collaboration_store_is_shared_brain_store(self) -> None:
        """Alias must resolve to the same class."""
        from cortex.infrastructure.shared_brain_store import CollaborationStore, SharedBrainStore
        assert CollaborationStore is SharedBrainStore

    def test_original_shared_brain_store_still_importable(self) -> None:
        """Original name must remain importable."""
        from cortex.infrastructure.shared_brain_store import SharedBrainStore  # noqa: F401
        assert SharedBrainStore is not None
