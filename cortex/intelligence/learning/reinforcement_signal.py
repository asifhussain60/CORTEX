"""
Unified Reinforcement Signal (URS) — Phase 83 Sub-Phase A.

AC-PHASE83-001: ReinforcementSignal dataclass + SignalType enum
AC-PHASE83-002: ReinforcementEngine emit/apply/history

Provides closed-loop feedback for the CORTEX learning system.
Orchestrators emit reinforcement signals (reward/punishment) for
patterns they encounter, and the engine applies those signals
to update confidence scores in the UniversalLearningLoop.

Scoring Model:
    STRONG_REWARD    → +1.0  (test pass, governance compliance)
    MILD_REWARD      → +0.5  (partial success, acceptable quality)
    NEUTRAL          →  0.0  (no signal, informational only)
    MILD_PUNISHMENT  → -0.5  (partial failure, degraded quality)
    STRONG_PUNISHMENT→ -1.0  (test fail, governance violation)

Confidence Rules:
    - PROMOTE at ≥0.9 confidence with 3+ rewards
    - QUARANTINE at ≤0.3 confidence with 2+ punishments
    - DECAY 0.1 per 30 days of inactivity
    - CROSS-CUTTING BOOST 0.15 when validated by 3+ orchestrators

Author: GitHub Copilot
Date: 2026-02-26
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from cortex.intelligence.learning.universal_learning_loop import (
        UniversalLearningLoop,
    )

logger = logging.getLogger(__name__)


class SignalType(Enum):
    """
    Reinforcement signal type with canonical score.

    Each value maps to a float score used for confidence adjustment.
    """

    STRONG_REWARD = (1.0,)
    MILD_REWARD = (0.5,)
    NEUTRAL = (0.0,)
    MILD_PUNISHMENT = (-0.5,)
    STRONG_PUNISHMENT = (-1.0,)

    def __init__(self, score: float) -> None:
        """Initialize SignalType with score."""
        self._score = score

    @property
    def score(self) -> float:
        """Get the canonical score for this signal type."""
        return self._score


@dataclass
class ReinforcementSignal:
    """
    A single reinforcement signal emitted by an orchestrator.

    Captures the signal type, target pattern, source, and context.
    Auto-generates signal_id and timestamp on creation.
    """

    signal_type: SignalType
    pattern_id: str
    source_orchestrator: str
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    signal_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to serializable dictionary.

        Returns:
            Dictionary representation of the signal.
        """
        return {
            "signal_id": self.signal_id,
            "signal_type": self.signal_type.name,
            "score": self.signal_type.score,
            "pattern_id": self.pattern_id,
            "source_orchestrator": self.source_orchestrator,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
        }


# Confidence adjustment scaling factor.
# A STRONG_REWARD (+1.0) * 0.1 = +0.10 confidence boost.
_CONFIDENCE_SCALE = 0.1


class ReinforcementEngine:
    """
    Core engine for emitting, storing, and applying reinforcement signals.

    Manages signal history and applies confidence adjustments to patterns
    stored in the UniversalLearningLoop's learning cache.
    """

    def __init__(self) -> None:
        """Initialize ReinforcementEngine with empty history."""
        self._signal_history: List[ReinforcementSignal] = []

    def emit_signal(
        self,
        signal_type: SignalType,
        pattern_id: str,
        source_orchestrator: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Emit a reinforcement signal and store it in history.

        Args:
            signal_type: Type of signal (reward/punishment/neutral).
            pattern_id: ID of the pattern being reinforced.
            source_orchestrator: Name of the emitting orchestrator.
            context: Optional additional context.

        Returns:
            The signal_id of the emitted signal.
        """
        signal = ReinforcementSignal(
            signal_type=signal_type,
            pattern_id=pattern_id,
            source_orchestrator=source_orchestrator,
            context=context or {},
        )
        self._signal_history.append(signal)

        logger.debug(
            f"Signal emitted: {signal.signal_type.name} "
            f"for pattern {pattern_id} from {source_orchestrator}"
        )
        return signal.signal_id

    def get_signal_history(
        self,
        pattern_id: Optional[str] = None,
    ) -> List[ReinforcementSignal]:
        """
        Get signal history, optionally filtered by pattern_id.

        Args:
            pattern_id: If provided, filter history to this pattern only.

        Returns:
            List of ReinforcementSignal objects.
        """
        if pattern_id is not None:
            return [
                s for s in self._signal_history if s.pattern_id == pattern_id
            ]
        return list(self._signal_history)

    def apply_to_learning(
        self,
        learning_loop: UniversalLearningLoop,
        pattern_id: str,
        signal_type: SignalType,
    ) -> None:
        """
        Apply a reinforcement signal to a pattern in the learning cache.

        Adjusts the pattern's confidence by (signal_type.score * _CONFIDENCE_SCALE),
        clamped to [0.0, 1.0].

        Also emits the signal to history.

        Args:
            learning_loop: The UniversalLearningLoop containing cached patterns.
            pattern_id: ID of the target pattern (matched via pattern_data["id"]).
            signal_type: Type of reinforcement signal.
        """
        delta = signal_type.score * _CONFIDENCE_SCALE

        # Walk the learning cache and adjust matching patterns
        for captures in learning_loop._learning_cache.values():
            for capture in captures:
                if capture.pattern_data.get("id") == pattern_id:
                    new_confidence = capture.confidence + delta
                    capture.confidence = max(0.0, min(1.0, new_confidence))

        # Record in history
        self.emit_signal(
            signal_type=signal_type,
            pattern_id=pattern_id,
            source_orchestrator="ReinforcementEngine",
        )

        logger.debug(
            f"Applied {signal_type.name} (delta={delta:+.2f}) "
            f"to pattern {pattern_id}"
        )
