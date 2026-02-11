"""
LearningTrigger: Detects when CORTEX needs to acquire new knowledge.

Monitors readiness scores and triggers learning actions when knowledge
gaps are detected (score < threshold).

Features:
- Threshold-based trigger detection
- ReadinessEngine integration
- Notification system
- Trigger history tracking
- Configurable thresholds and actions

Author: Asif Hussain (CORTEX Phase 34B)
"""

import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from cortex.orchestrators.intelligence.readiness_engine import ReadinessEngine
from cortex.orchestrators.intelligence.types import ReadinessScore, TechStack

# Configure logging
logger = logging.getLogger(__name__)


class TriggerReason(Enum):
    """Reasons for triggering learning."""
    LOW_SCORE = "low_score"  # Overall score below threshold
    MISSING_KNOWLEDGE = "missing_knowledge"  # Critical knowledge gaps
    NEW_TECH = "new_tech"  # New technology detected


class TriggerAction(Enum):
    """Recommended actions when trigger fires."""
    SYNTHESIZE_KNOWLEDGE = "synthesize_knowledge"  # Generate new knowledge
    ACQUIRE_BEST_PRACTICES = "acquire_best_practices"  # Fetch best practices
    GENERATE_TDD_PATTERNS = "generate_tdd_patterns"  # Create TDD templates
    UPDATE_SECURITY_RULES = "update_security_rules"  # Update security rules


@dataclass
class TriggerEvent:
    """
    Learning trigger event.

    Represents a detected need for knowledge acquisition.
    """
    triggered: bool
    tech_stack: Optional[TechStack]
    score: Optional[ReadinessScore]
    reason: Optional[TriggerReason]
    recommended_action: Optional[TriggerAction]
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class LearningTrigger:
    """
    Detects when CORTEX needs to acquire new knowledge.

    Monitors readiness scores and triggers learning when:
    - Overall score < threshold (default 0.5)
    - Critical knowledge components missing
    - New/unknown technologies detected
    """

    DEFAULT_THRESHOLD = 0.5  # Default trigger threshold
    DEFAULT_HISTORY_LIMIT = 100  # Max trigger events to keep

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize LearningTrigger.

        Args:
            config: Optional configuration dictionary
                - threshold: Score threshold for triggering (default 0.5)
                - notification_enabled: Enable notifications (default True)
                - history_limit: Max history entries (default 100)
        """
        config = config or {}
        self.threshold = config.get("threshold", self.DEFAULT_THRESHOLD)
        self.notification_enabled = config.get("notification_enabled", True)
        self.history_limit = config.get("history_limit", self.DEFAULT_HISTORY_LIMIT)

        # Initialize ReadinessEngine
        self._readiness_engine = ReadinessEngine()

        # Thread-safe history tracking
        self._history: List[TriggerEvent] = []
        self._history_lock = threading.Lock()

    def check_readiness(self, tech_stack: Optional[TechStack]) -> TriggerEvent:
        """
        Check if tech stack readiness triggers learning.

        Args:
            tech_stack: Technology stack to check

        Returns:
            TriggerEvent with trigger status and details
        """
        # Handle invalid input
        if tech_stack is None or not tech_stack.language:
            return self._create_trigger_event(
                triggered=True,
                tech_stack=tech_stack,
                score=None,
                reason=TriggerReason.MISSING_KNOWLEDGE,
                action=TriggerAction.SYNTHESIZE_KNOWLEDGE,
            )

        # Get readiness score
        try:
            score = self._get_readiness_score(tech_stack)
        except Exception as e:
            logger.error(f"Error calculating readiness score: {e}")
            return self._create_trigger_event(
                triggered=True,
                tech_stack=tech_stack,
                score=None,
                reason=TriggerReason.MISSING_KNOWLEDGE,
                action=TriggerAction.SYNTHESIZE_KNOWLEDGE,
            )

        # Check if score triggers learning
        if score.overall < self.threshold:
            reason = TriggerReason.LOW_SCORE
            action = self._determine_action(score)

            event = self._create_trigger_event(
                triggered=True,
                tech_stack=tech_stack,
                score=score,
                reason=reason,
                action=action,
            )

            # Record in history
            self._record_trigger(event)

            # Send notification if enabled
            if self.notification_enabled:
                self._send_notification(event)

            return event
        else:
            # No trigger - score above threshold
            return self._create_trigger_event(
                triggered=False,
                tech_stack=tech_stack,
                score=score,
                reason=None,
                action=None,
            )

    def get_trigger_history(self) -> List[TriggerEvent]:
        """
        Get trigger event history.

        Returns:
            List of trigger events (most recent first)
        """
        with self._history_lock:
            return list(self._history)

    def clear_history(self):
        """Clear trigger event history."""
        with self._history_lock:
            self._history.clear()

    # Private helper methods

    def _get_readiness_score(self, tech_stack: TechStack) -> ReadinessScore:
        """
        Get readiness score from ReadinessEngine.

        Args:
            tech_stack: Technology stack to score

        Returns:
            ReadinessScore with overall and component scores
        """
        return self._readiness_engine.calculate_readiness_score(tech_stack)

    def _determine_action(self, score: ReadinessScore) -> TriggerAction:
        """
        Determine recommended action based on score breakdown.

        Args:
            score: ReadinessScore with component breakdown

        Returns:
            Recommended TriggerAction
        """
        # Find weakest component
        components = {
            "best_practices": score.best_practices,
            "tdd_support": score.tdd_support,
            "security": score.security,
        }

        weakest = min(components.keys(), key=lambda k: components[k])

        # Map to action
        action_map = {
            "best_practices": TriggerAction.ACQUIRE_BEST_PRACTICES,
            "tdd_support": TriggerAction.GENERATE_TDD_PATTERNS,
            "security_tooling": TriggerAction.UPDATE_SECURITY_RULES,
        }

        return action_map.get(weakest, TriggerAction.SYNTHESIZE_KNOWLEDGE)

    def _create_trigger_event(
        self,
        triggered: bool,
        tech_stack: Optional[TechStack],
        score: Optional[ReadinessScore],
        reason: Optional[TriggerReason],
        action: Optional[TriggerAction],
    ) -> TriggerEvent:
        """Create trigger event with metadata."""
        return TriggerEvent(
            triggered=triggered,
            tech_stack=tech_stack,
            score=score,
            reason=reason,
            recommended_action=action,
            timestamp=datetime.now(),
            metadata={
                "threshold": self.threshold,
                "overall_score": score.overall if score else None,
            }
        )

    def _record_trigger(self, event: TriggerEvent):
        """
        Record trigger event in history.

        Args:
            event: TriggerEvent to record
        """
        with self._history_lock:
            self._history.append(event)

            # Enforce history limit (keep most recent)
            if len(self._history) > self.history_limit:
                self._history = self._history[-self.history_limit:]

    def _send_notification(self, event: TriggerEvent):
        """
        Send notification about trigger event.

        Args:
            event: TriggerEvent to notify about
        """
        logger.info(
            f"Learning trigger fired: {event.reason.value if event.reason else 'unknown'} "
            f"for {event.tech_stack.language if event.tech_stack else 'unknown'} "
            f"(score: {event.score.overall if event.score else 'N/A'})"
        )

        if event.recommended_action:
            logger.info(f"Recommended action: {event.recommended_action.value}")
