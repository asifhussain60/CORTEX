"""
Phase 57-f RED — Memory tier wiring + reasoning engine activation tests.

GAP-57-08: VacuumOrchestrator must import and use tier1_learned cleaners.
GAP-57-09: StrategySelector must be imported and invoked by IntentRouter.

AC-ID: AC-PHASE57-F-001
Governance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""
from __future__ import annotations

import inspect
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent


# ---------------------------------------------------------------------------
# GAP-57-08: VacuumOrchestrator uses tier1_learned cleaners
# ---------------------------------------------------------------------------


class TestVacuumTier1Wiring:
    """Verify VacuumOrchestrator consumes tier1_learned cleaners."""

    def test_vacuum_orchestrator_uses_tier1_cleaners(self) -> None:
        """VacuumOrchestrator source must import at least 2 tier1_learned cleaners."""
        vacuum_src = (
            REPO_ROOT / "cortex" / "orchestrators" / "health" / "vacuum_orchestrator.py"
        )
        content = vacuum_src.read_text()
        # Count imports from cortex.intelligence.memory.tier1_learned
        tier1_imports = [
            line.strip()
            for line in content.splitlines()
            if "tier1_learned" in line and ("import" in line or "from" in line)
        ]
        assert len(tier1_imports) >= 2, (
            f"VacuumOrchestrator imports only {len(tier1_imports)} tier1_learned cleaners. "
            "Expected ≥2 (e.g. markdown_sprawl + root_artifacts).\n"
            f"Found: {tier1_imports}"
        )

    def test_tier1_root_artifacts_cleaner_invoked(self) -> None:
        """VacuumOrchestrator must reference root_artifacts cleaner in its logic."""
        vacuum_src = (
            REPO_ROOT / "cortex" / "orchestrators" / "health" / "vacuum_orchestrator.py"
        )
        content = vacuum_src.read_text()
        assert "root_artifacts" in content or "RootArtifacts" in content, (
            "VacuumOrchestrator does not reference root_artifacts tier1 cleaner."
        )


# ---------------------------------------------------------------------------
# GAP-57-09: IntentRouter uses StrategySelector
# ---------------------------------------------------------------------------


class TestIntentRouterStrategySelector:
    """Verify IntentRouter imports and uses StrategySelector from reasoning/."""

    def test_intent_router_uses_strategy_selector(self) -> None:
        """IntentRouter source must import StrategySelector."""
        intent_router_src = (
            REPO_ROOT / "cortex" / "orchestrators" / "core" / "intent_router.py"
        )
        content = intent_router_src.read_text()
        assert "StrategySelector" in content, (
            "IntentRouter does not reference StrategySelector — GAP-57-09 not fixed."
        )

    def test_strategy_selector_returns_valid_strategy(self) -> None:
        """StrategySelector.select() must return a non-empty string."""
        from cortex.intelligence.reasoning.strategy_selector import StrategySelector  # noqa: PLC0415
        selector = StrategySelector()
        result = selector.select(intent="IMPLEMENT", context={})
        assert isinstance(result, str) and len(result) > 0, (
            f"StrategySelector.select() returned invalid strategy: {result!r}"
        )


# ---------------------------------------------------------------------------
# tier3_scratch connectivity
# ---------------------------------------------------------------------------


class TestTier3ScratchConnector:
    """Verify tier3_scratch __init__.py exposes a scratch_space path connector."""

    def test_tier3_scratch_has_scratch_space(self) -> None:
        """tier3_scratch package must expose scratch_space path connector."""
        from cortex.intelligence.memory import tier3_scratch  # noqa: PLC0415
        assert hasattr(tier3_scratch, "scratch_space") or hasattr(
            tier3_scratch, "SCRATCH_PATH"
        ), (
            "cortex.intelligence.memory.tier3_scratch does not expose "
            "scratch_space or SCRATCH_PATH."
        )
