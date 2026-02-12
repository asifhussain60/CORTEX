"""
DoR Tracker - Definition of Ready Per-Turn Confidence Tracking.

Tracks Definition of Ready (DoR) metrics on a per-turn basis:
- Initial DoR (before challenge)
- Challenges offered
- User response (proceed, modify, cancel)
- Final DoR (after decision)
- Execution results

Enables RCA (Root Cause Analysis) to identify patterns:
- Why DoR improved/degraded
- Challenge effectiveness
- Threshold adjustment recommendations

Authority: CORE-008 (TDD), CORE-027 (Audit), CORE-030 (Implementation Truth)
Phase: 8.0 - Challenge Orchestrator Foundation
"""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.core.result import Err, Ok, Result
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger

logger = logging.getLogger(__name__)


class UserResponse(Enum):
    """User's response to a challenge."""
    ACCEPTED = "accepted"  # User accepted CORTEX recommendation
    MODIFIED = "modified"  # User modified request and retried
    BYPASSED = "bypassed"  # User acknowledged risk and proceeded
    CANCELLED = "cancelled"  # User cancelled operation


@dataclass
class Challenge:
    """Challenge offered to user during turn."""
    challenge_id: str
    challenge_type: str  # "security", "harmful", "srp", "architecture", etc.
    confidence_threshold: float  # Threshold that triggered challenge
    gate_type: str  # "hard", "soft", "context"
    description: str
    alternatives: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DoRTurn:
    """Definition of Ready tracking for single turn."""

    turn_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    orchestrator: str = ""  # Which orchestrator executed this turn
    timestamp: datetime = field(default_factory=datetime.now)

    # Input request
    user_request: str = ""

    # Initial DoR (before challenge)
    initial_dor: float = 0.0  # 0.0-1.0
    initial_dor_factors: Dict[str, float] = field(default_factory=dict)

    # Challenges offered
    challenges_offered: List[Challenge] = field(default_factory=list)

    # User decision
    user_response: Optional[UserResponse] = None
    response_timestamp: Optional[datetime] = None

    # Final DoR (after challenge/decision)
    final_dor: float = 0.0  # 0.0-1.0
    final_dor_factors: Dict[str, float] = field(default_factory=dict)
    dor_improvement: float = 0.0  # final - initial

    # Execution result
    execution_success: Optional[bool] = None
    execution_result: Optional[str] = None
    execution_time_ms: float = 0.0

    # RCA data
    rca_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/serialization."""
        return {
            "turn_id": self.turn_id,
            "orchestrator": self.orchestrator,
            "timestamp": self.timestamp.isoformat(),
            "user_request": self.user_request[:100],  # Truncate for logs
            "initial_dor": round(self.initial_dor, 3),
            "final_dor": round(self.final_dor, 3),
            "dor_improvement": round(self.dor_improvement, 3),
            "challenges_offered": len(self.challenges_offered),
            "user_response": self.user_response.value if self.user_response else None,
            "execution_success": self.execution_success,
            "execution_time_ms": round(self.execution_time_ms, 1),
        }


class DoRTracker:
    """
    Tracks Definition of Ready (DoR) across turns.

    Maintains history of:
    - Per-turn DoR scores (initial/final)
    - Challenge effectiveness
    - User responses
    - Execution outcomes

    Generates statistics for RCA analysis.
    """

    def __init__(self, session_id: Optional[str] = None):
        """Initialize DoR tracker for session."""
        self.session_id = session_id or str(uuid.uuid4())[:12]
        self.turns: List[DoRTurn] = []
        self.logger = EnhancedAuditLogger.instance()
        logger.info(f"DoRTracker initialized for session {self.session_id}")

    def start_turn(
        self,
        orchestrator: str,
        user_request: str,
        initial_dor: float,
        dor_factors: Dict[str, float]
    ) -> DoRTurn:
        """
        Start tracking a new turn.

        Args:
            orchestrator: Orchestrator handling this turn
            user_request: User's request
            initial_dor: Initial DoR before challenges (0.0-1.0)
            dor_factors: Dict of factors contributing to DoR

        Returns:
            DoRTurn object to track through completion
        """
        turn = DoRTurn(
            orchestrator=orchestrator,
            user_request=user_request,
            initial_dor=initial_dor,
            initial_dor_factors=dor_factors.copy()
        )

        self.turns.append(turn)
        logger.debug(f"Turn started: {turn.turn_id} (initial_dor={initial_dor:.2f})")

        return turn

    def add_challenge(
        self,
        turn: DoRTurn,
        challenge_type: str,
        confidence_threshold: float,
        gate_type: str,
        description: str,
        alternatives: List[str] = None
    ) -> None:
        """
        Record challenge offered during turn.

        Args:
            turn: DoRTurn object
            challenge_type: Type of challenge ("srp", "security", etc.)
            confidence_threshold: Threshold that triggered challenge
            gate_type: Gate type ("hard", "soft", "context")
            description: Challenge description
            alternatives: List of alternatives offered
        """
        challenge = Challenge(
            challenge_id=str(uuid.uuid4())[:8],
            challenge_type=challenge_type,
            confidence_threshold=confidence_threshold,
            gate_type=gate_type,
            description=description,
            alternatives=alternatives or []
        )

        turn.challenges_offered.append(challenge)
        logger.debug(f"Challenge added: {challenge_type} (gate={gate_type})")

    def record_response(
        self,
        turn: DoRTurn,
        response: UserResponse
    ) -> None:
        """
        Record user's response to challenges.

        Args:
            turn: DoRTurn object
            response: UserResponse enum value
        """
        turn.user_response = response
        turn.response_timestamp = datetime.now()
        logger.debug(f"User response recorded: {response.value}")

    def complete_turn(
        self,
        turn: DoRTurn,
        final_dor: float,
        dor_factors: Dict[str, float],
        execution_success: bool,
        execution_result: str,
        execution_time_ms: float,
        rca_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Complete turn tracking with results.

        Args:
            turn: DoRTurn object
            final_dor: Final DoR after challenges (0.0-1.0)
            dor_factors: Dict of factors contributing to final DoR
            execution_success: Whether execution succeeded
            execution_result: Result/status message
            execution_time_ms: Time spent executing
            rca_data: Optional RCA analysis data
        """
        turn.final_dor = final_dor
        turn.final_dor_factors = dor_factors.copy()
        turn.dor_improvement = final_dor - turn.initial_dor
        turn.execution_success = execution_success
        turn.execution_result = execution_result
        turn.execution_time_ms = execution_time_ms
        turn.rca_data = rca_data or {}

        logger.info(
            f"Turn completed: {turn.turn_id} "
            f"(initial_dor={turn.initial_dor:.2f} → final_dor={final_dor:.2f}, "
            f"improvement={turn.dor_improvement:+.2f}, success={execution_success})"
        )

        # Log to audit trail
        self.logger.log_operation_complete(
            ac_id="AC-DOR-TRACKING",
            operation="TURN_COMPLETE",
            success=True,
            details=turn.to_dict()
        )

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get aggregate statistics across all turns.

        Returns:
            Dict with statistics
        """
        if not self.turns:
            return {}

        completed_turns = [t for t in self.turns if t.execution_success is not None]
        if not completed_turns:
            return {}

        initial_dors = [t.initial_dor for t in completed_turns]
        final_dors = [t.final_dor for t in completed_turns]
        improvements = [t.dor_improvement for t in completed_turns]

        successful_turns = [t for t in completed_turns if t.execution_success]
        bypassed_challenges = [t for t in completed_turns if t.user_response == UserResponse.BYPASSED]

        return {
            "total_turns": len(self.turns),
            "completed_turns": len(completed_turns),
            "successful_turns": len(successful_turns),
            "success_rate": len(successful_turns) / len(completed_turns) if completed_turns else 0.0,

            "avg_initial_dor": sum(initial_dors) / len(initial_dors) if initial_dors else 0.0,
            "avg_final_dor": sum(final_dors) / len(final_dors) if final_dors else 0.0,
            "avg_dor_improvement": sum(improvements) / len(improvements) if improvements else 0.0,

            "challenges_offered": sum(len(t.challenges_offered) for t in completed_turns),
            "bypassed_challenges": len(bypassed_challenges),
            "bypass_rate": len(bypassed_challenges) / len(completed_turns) if completed_turns else 0.0,

            "min_dor": min(initial_dors) if initial_dors else 0.0,
            "max_dor": max(final_dors) if final_dors else 1.0,
        }

    def get_turn_history(self) -> List[Dict[str, Any]]:
        """
        Get history of all turns in this session.

        Returns:
            List of turn dictionaries
        """
        return [t.to_dict() for t in self.turns]
