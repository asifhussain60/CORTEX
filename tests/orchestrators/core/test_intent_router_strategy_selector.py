"""
Phase 57-f RED — IntentRouter StrategySelector integration test (standalone).

GAP-57-09: StrategySelector must be wired into IntentRouter routing logic.

AC-ID: AC-PHASE57-F-002
Governance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent


class TestIntentRouterStrategySelectorWiring:
    """Verify StrategySelector is wired into IntentRouter."""

    def test_intent_router_uses_strategy_selector(self) -> None:
        """IntentRouter source must reference StrategySelector."""
        src = REPO_ROOT / "cortex" / "orchestrators" / "core" / "intent_router.py"
        assert "StrategySelector" in src.read_text(), (
            "IntentRouter source does not reference StrategySelector."
        )

    def test_strategy_selector_returns_valid_strategy(self) -> None:
        """StrategySelector.select() must return a non-empty str."""
        from cortex.intelligence.reasoning.strategy_selector import StrategySelector  # noqa: PLC0415
        selector = StrategySelector()
        result = selector.select(intent="IMPLEMENT", context={})
        assert isinstance(result, str) and len(result) > 0
