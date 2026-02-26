"""
CortexLearning MCP Tool — Phase 83 Sub-Phase C.

AC-83-MCP-LEARNING-001: CortexLearning class-based MCP tool
AC-83-MCP-LEARNING-002: Supports emit, history, decay, promote, quarantine, metrics

Exposes the Unified Reinforcement Signal (URS) system via MCP so
Copilot Chat and any MCP client can:
- Emit reinforcement signals for patterns
- Query signal history
- Run lifecycle operations (decay, promote, quarantine)
- Retrieve learning metrics

Author: GitHub Copilot
Date: 2026-02-26
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from cortex.mcp.mcp_tool_base import (
    Tool,
    ToolCategory,
    ToolDefinition,
    ToolParameter,
    ToolResult,
)

logger = logging.getLogger(__name__)


class CortexLearning(Tool):
    """
    MCP tool for the Unified Reinforcement Signal (URS) system.

    Operations:
    - emit: Emit a reinforcement signal for a pattern
    - history: Query signal history (optionally filtered by pattern_id)
    - decay: Decay confidence of stale patterns
    - promote: Identify high-confidence patterns for promotion
    - quarantine: Identify low-confidence patterns for quarantine
    - metrics: Return learning and reinforcement statistics
    """

    _PARAMETERS: List[ToolParameter] = [
        ToolParameter(
            name="op",
            type="string",
            description=(
                "Operation: 'emit' (signal), 'history' (query), "
                "'decay' (stale patterns), 'promote' (high confidence), "
                "'quarantine' (low confidence), 'metrics' (statistics)"
            ),
            required=True,
            enum=["emit", "history", "decay", "promote", "quarantine", "metrics"],
        ),
        ToolParameter(
            name="signal_type",
            type="string",
            description=(
                "Signal type for emit operation. One of: "
                "STRONG_REWARD, MILD_REWARD, NEUTRAL, MILD_PUNISHMENT, STRONG_PUNISHMENT"
            ),
            required=False,
            enum=[
                "STRONG_REWARD",
                "MILD_REWARD",
                "NEUTRAL",
                "MILD_PUNISHMENT",
                "STRONG_PUNISHMENT",
            ],
        ),
        ToolParameter(
            name="pattern_id",
            type="string",
            description="Pattern ID to target (required for emit, optional filter for history)",
            required=False,
        ),
        ToolParameter(
            name="source_orchestrator",
            type="string",
            description="Name of the orchestrator emitting the signal (required for emit)",
            required=False,
        ),
        ToolParameter(
            name="max_age_days",
            type="integer",
            description="Max inactivity days for decay operation (default: 30)",
            required=False,
        ),
        ToolParameter(
            name="threshold",
            type="number",
            description="Confidence threshold for promote/quarantine (default: 0.9/0.3)",
            required=False,
        ),
    ]

    def __init__(self) -> None:
        """Initialize CortexLearning with private engine and analyzer."""
        # Lazy-init engine and analyzer on first use
        self._engine: Optional[Any] = None
        self._analyzer: Optional[Any] = None

    @property
    def definition(self) -> ToolDefinition:
        """MCP-compliant tool definition."""
        return ToolDefinition(
            name="cortex_learning",
            description=(
                "Unified Reinforcement Signal (URS) system for CORTEX learning. "
                "Emit reward/punishment signals for patterns, query signal history, "
                "run lifecycle operations (decay stale patterns, promote high-confidence, "
                "quarantine low-confidence), and retrieve learning metrics. "
                "Closed-loop feedback makes CORTEX self-improving."
            ),
            category=ToolCategory.INTELLIGENCE,
            parameters=self._PARAMETERS,
        )

    @property
    def name(self) -> str:
        """Tool name exposed to MCP clients."""
        return self.definition.name

    @property
    def description(self) -> str:
        """Human-readable tool description."""
        return self.definition.description

    @property
    def category(self) -> ToolCategory:
        """Tool category for MCP routing."""
        return self.definition.category

    def _get_engine(self) -> Any:
        """Lazy-load ReinforcementEngine."""
        if self._engine is None:
            from cortex.intelligence.learning.reinforcement_signal import (
                ReinforcementEngine,
            )
            self._engine = ReinforcementEngine()
        return self._engine

    def _get_analyzer(self) -> Any:
        """Lazy-load EffectivenessAnalyzer."""
        if self._analyzer is None:
            from cortex.intelligence.learning.effectiveness_analyzer import (
                EffectivenessAnalyzer,
            )
            self._analyzer = EffectivenessAnalyzer()
        return self._analyzer

    def execute(self, **kwargs: Any) -> ToolResult:
        """
        Execute a learning operation.

        Args:
            **kwargs: Operation parameters including 'op'.

        Returns:
            ToolResult with operation outcome.
        """
        op = kwargs.get("op", "")

        try:
            if op == "emit":
                return self._op_emit(kwargs)
            elif op == "history":
                return self._op_history(kwargs)
            elif op == "decay":
                return self._op_decay(kwargs)
            elif op == "promote":
                return self._op_promote(kwargs)
            elif op == "quarantine":
                return self._op_quarantine(kwargs)
            elif op == "metrics":
                return self._op_metrics(kwargs)
            else:
                return ToolResult(
                    success=False,
                    error=f"Unknown operation: {op}",
                    data={"supported_operations": [
                        "emit", "history", "decay", "promote", "quarantine", "metrics",
                    ]},
                )
        except Exception as e:
            logger.error(f"CortexLearning.{op} failed: {e}", exc_info=True)
            return ToolResult(success=False, error=str(e))

    # ─── Operations ──────────────────────────────────────────────────────

    def _op_emit(self, params: Dict[str, Any]) -> ToolResult:
        """Emit a reinforcement signal."""
        from cortex.intelligence.learning.reinforcement_signal import SignalType

        signal_type_name = params.get("signal_type", "")
        pattern_id = params.get("pattern_id", "")
        source_orchestrator = params.get("source_orchestrator", "unknown")

        # Validate signal_type
        try:
            signal_type = SignalType[signal_type_name]
        except KeyError:
            return ToolResult(
                success=False,
                error=f"Invalid signal_type: {signal_type_name}. "
                f"Must be one of: {[s.name for s in SignalType]}",
            )

        engine = self._get_engine()
        signal_id = engine.emit_signal(
            signal_type=signal_type,
            pattern_id=pattern_id,
            source_orchestrator=source_orchestrator,
            context=params.get("context", {}),
        )

        return ToolResult(
            success=True,
            data={
                "signal_id": signal_id,
                "signal_type": signal_type_name,
                "pattern_id": pattern_id,
                "score": signal_type.score,
            },
        )

    def _op_history(self, params: Dict[str, Any]) -> ToolResult:
        """Query signal history."""
        engine = self._get_engine()
        pattern_id = params.get("pattern_id")

        history = engine.get_signal_history(pattern_id=pattern_id)

        return ToolResult(
            success=True,
            data={
                "signals": [s.to_dict() for s in history],
                "count": len(history),
            },
        )

    def _op_decay(self, params: Dict[str, Any]) -> ToolResult:
        """Decay stale patterns."""
        analyzer = self._get_analyzer()
        max_age_days = int(params.get("max_age_days", 30))

        decayed = analyzer.decay_stale_patterns(max_age_days=max_age_days)

        return ToolResult(
            success=True,
            data={
                "decayed": decayed,
                "count": len(decayed),
                "max_age_days": max_age_days,
            },
        )

    def _op_promote(self, params: Dict[str, Any]) -> ToolResult:
        """Promote high-confidence patterns."""
        analyzer = self._get_analyzer()
        threshold = float(params.get("threshold", 0.9))

        promoted = analyzer.promote_high_confidence(threshold=threshold)

        return ToolResult(
            success=True,
            data={
                "promoted": promoted,
                "count": len(promoted),
                "threshold": threshold,
            },
        )

    def _op_quarantine(self, params: Dict[str, Any]) -> ToolResult:
        """Quarantine low-confidence patterns."""
        analyzer = self._get_analyzer()
        threshold = float(params.get("threshold", 0.3))

        quarantined = analyzer.quarantine_low_confidence(threshold=threshold)

        return ToolResult(
            success=True,
            data={
                "quarantined": quarantined,
                "count": len(quarantined),
                "threshold": threshold,
            },
        )

    def _op_metrics(self, params: Dict[str, Any]) -> ToolResult:
        """Return learning and reinforcement metrics."""
        engine = self._get_engine()
        analyzer = self._get_analyzer()

        all_history = engine.get_signal_history()
        all_metrics = analyzer.get_all_metrics()

        return ToolResult(
            success=True,
            data={
                "signal_count": len(all_history),
                "total_learnings": len(all_metrics),
                "patterns_tracked": list(all_metrics.keys()),
                "signals_by_type": self._count_by_type(all_history),
            },
        )

    @staticmethod
    def _count_by_type(history: list) -> Dict[str, int]:
        """Count signals grouped by type."""
        counts: Dict[str, int] = {}
        for signal in history:
            name = signal.signal_type.name
            counts[name] = counts.get(name, 0) + 1
        return counts
