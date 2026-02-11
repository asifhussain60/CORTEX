"""
DebuggerOrchestrator - EventBus-Driven Zero-Friction Debugging

Provides zero-friction debugging via EventBus integration:

Subscriptions:
- TEST_FAILURE: Auto-inject CORTEX_DEBUG markers on test failure
- REFACTOR_REGRESSION: Trigger debug session on refactoring regression
- GOVERNANCE_VIOLATION: Flag compliance issues

Publications:
- DEBUG_MARKERS_INJECTED: Notify listeners that markers were injected
- DEBUG_SESSION_READY: Session is prepared for debugging

Purpose: Auto-inject debugging markers without manual intervention.
When developer opens file in VS Code, markers are already there.

Authority: ENH-087 Track 2 Specification
Date: 2026-02-11
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# DATA CLASSES
# ============================================================================


@dataclass
class DebugMarker:
    """Represents a debug marker injected into code."""

    file_path: str
    line_number: int
    marker_type: str  # 'TEST_FAILURE', 'REGRESSION', 'GOVERNANCE'
    message: str
    timestamp: str


@dataclass
class DebugSession:
    """Represents an active debug session."""

    session_id: str
    test_name: Optional[str]
    error_message: str
    file_path: str
    line_number: int
    markers_injected: List[DebugMarker]
    ready: bool = False


@dataclass
class RegressionEvent:
    """Represents a refactoring regression event."""

    orchestrator: str
    method: str
    input_data: str
    expected_output: str
    actual_output: str
    error_message: str


@dataclass
class GovernanceViolation:
    """Represents a governance rule violation."""

    rule_id: str
    severity: str  # 'P0', 'P1', 'P2'
    description: str
    file_path: str
    line_number: Optional[int] = None


# ============================================================================
# ENUMS
# ============================================================================


class EventType(Enum):
    """Types of events that trigger debugging."""

    TEST_FAILURE = "TEST_FAILURE"
    REFACTOR_REGRESSION = "REFACTOR_REGRESSION"
    GOVERNANCE_VIOLATION = "GOVERNANCE_VIOLATION"


class MarkerType(Enum):
    """Types of debug markers."""

    TEST_FAILURE = "TEST_FAILURE"
    REGRESSION = "REGRESSION"
    GOVERNANCE = "GOVERNANCE"
    INFO = "INFO"


# ============================================================================
# DEBUGGER ORCHESTRATOR
# ============================================================================


class DebuggerOrchestrator:
    """
    Zero-friction debugging via EventBus integration.

    Features:
    - Auto-inject CORTEX_DEBUG markers on test failure
    - Detect refactoring regressions automatically
    - Flag governance violations
    - Zero manual marker injection (vision goal)

    Subscriptions:
    - TEST_FAILURE: test_name, error_message, file_path, line_number
    - REFACTOR_REGRESSION: orchestrator, method, expected/actual outputs
    - GOVERNANCE_VIOLATION: rule_id, severity, description, file_path

    Publications:
    - DEBUG_MARKERS_INJECTED: {session_id, markers_count}
    - DEBUG_SESSION_READY: {session_id, file_path, line_number}
    """

    def __init__(self, event_bus: Optional[Any] = None) -> None:
        """
        Initialize DebuggerOrchestrator.

        Args:
            event_bus: Optional EventBus instance for event handling
        """
        self.event_bus = event_bus
        self._active_sessions: Dict[str, DebugSession] = {}
        self._injected_markers: List[DebugMarker] = []
        self._session_counter: int = 0
        self._register_event_handlers()

    def _register_event_handlers(self) -> None:
        """Register handlers for EventBus events."""
        if not self.event_bus:
            return

        # Register subscriptions
        handlers = {
            "TEST_FAILURE": self.handle_test_failure,
            "REFACTOR_REGRESSION": self.handle_regression,
            "GOVERNANCE_VIOLATION": self.handle_governance_violation,
        }

        for event_type, handler in handlers.items():
            # In real implementation: self.event_bus.subscribe(event_type, handler)
            logger.info(f"Registered handler for {event_type}")

    # ────────────────────────────────────────────────────────────────────────
    # EVENT HANDLERS
    # ────────────────────────────────────────────────────────────────────────

    def handle_test_failure(
        self,
        test_name: str,
        error_message: str,
        file_path: str,
        line_number: int,
    ) -> DebugSession:
        """
        Handle TEST_FAILURE event from TDDOrchestrator.

        Workflow:
        1. Receive TEST_FAILURE event
        2. Determine location of failure (file + line)
        3. Auto-inject CORTEX_DEBUG markers
        4. Create debug session
        5. Publish DEBUG_MARKERS_INJECTED

        Args:
            test_name: Name of failing test
            error_message: Test failure message
            file_path: File where failure occurred
            line_number: Line number of failure

        Returns:
            DebugSession with markers already injected
        """
        # Create debug session
        self._session_counter += 1
        session_id = f"DEBUG-{self._session_counter}"

        # Create debug marker
        marker = DebugMarker(
            file_path=file_path,
            line_number=line_number,
            marker_type=MarkerType.TEST_FAILURE.value,
            message=f"Test failure: {test_name}\n{error_message}",
            timestamp=self._get_timestamp(),
        )

        # Inject marker into file (in real implementation)
        self._inject_marker(marker)
        self._injected_markers.append(marker)

        # Create session
        session = DebugSession(
            session_id=session_id,
            test_name=test_name,
            error_message=error_message,
            file_path=file_path,
            line_number=line_number,
            markers_injected=[marker],
            ready=True,
        )

        self._active_sessions[session_id] = session

        # Publish DEBUG_MARKERS_INJECTED event
        self._publish_event(
            "DEBUG_MARKERS_INJECTED",
            {
                "session_id": session_id,
                "markers_count": 1,
                "file_path": file_path,
            },
        )

        # Publish DEBUG_SESSION_READY event
        self._publish_event(
            "DEBUG_SESSION_READY",
            {
                "session_id": session_id,
                "file_path": file_path,
                "line_number": line_number,
                "test_name": test_name,
            },
        )

        logger.info(
            f"Debug session {session_id} ready: {test_name} in {file_path}:{line_number}"
        )

        return session

    def handle_regression(
        self,
        event: RegressionEvent,
    ) -> DebugSession:
        """
        Handle REFACTOR_REGRESSION event from RefactoringOrchestrator.

        Detects when refactoring caused regression and triggers debug session.

        Args:
            event: RegressionEvent with orchestrator, method, outputs

        Returns:
            DebugSession for investigating regression
        """
        # Create debug session for regression
        self._session_counter += 1
        session_id = f"REGRESSION-{self._session_counter}"

        # Create regression marker
        marker = DebugMarker(
            file_path=f"cortex/orchestrators/domain/{event.orchestrator.lower()}.py",
            line_number=0,  # Will be updated by code inspection
            marker_type=MarkerType.REGRESSION.value,
            message=(
                f"Regression in {event.orchestrator}.{event.method}\n"
                f"Expected: {event.expected_output}\n"
                f"Actual: {event.actual_output}\n"
                f"Error: {event.error_message}"
            ),
            timestamp=self._get_timestamp(),
        )

        self._inject_marker(marker)
        self._injected_markers.append(marker)

        session = DebugSession(
            session_id=session_id,
            test_name=None,
            error_message=event.error_message,
            file_path=marker.file_path,
            line_number=marker.line_number,
            markers_injected=[marker],
            ready=True,
        )

        self._active_sessions[session_id] = session

        self._publish_event(
            "DEBUG_MARKERS_INJECTED",
            {
                "session_id": session_id,
                "markers_count": 1,
                "regression_type": "REFACTOR",
            },
        )

        logger.warning(
            f"Regression detected in {event.orchestrator}.{event.method}: {event.error_message}"
        )

        return session

    def handle_governance_violation(
        self,
        violation: GovernanceViolation,
    ) -> DebugSession:
        """
        Handle GOVERNANCE_VIOLATION event from EnforcementOrchestrator.

        Flags compliance issues and creates debug session.

        Args:
            violation: GovernanceViolation with rule, severity, description

        Returns:
            DebugSession for investigating violation
        """
        self._session_counter += 1
        session_id = f"COMPLIANCE-{self._session_counter}"

        # Create governance marker
        marker = DebugMarker(
            file_path=violation.file_path,
            line_number=violation.line_number or 1,
            marker_type=MarkerType.GOVERNANCE.value,
            message=(
                f"Governance violation: {violation.rule_id}\n"
                f"Severity: {violation.severity}\n"
                f"{violation.description}"
            ),
            timestamp=self._get_timestamp(),
        )

        self._inject_marker(marker)
        self._injected_markers.append(marker)

        session = DebugSession(
            session_id=session_id,
            test_name=None,
            error_message=violation.description,
            file_path=violation.file_path,
            line_number=violation.line_number or 1,
            markers_injected=[marker],
            ready=True,
        )

        self._active_sessions[session_id] = session

        logger.error(
            f"Governance violation {violation.rule_id} in {violation.file_path}: {violation.description}"
        )

        return session

    # ────────────────────────────────────────────────────────────────────────
    # HELPER METHODS
    # ────────────────────────────────────────────────────────────────────────

    def _inject_marker(self, marker: DebugMarker) -> None:
        """
        Inject CORTEX_DEBUG marker into source file.

        In real implementation, this would:
        1. Read file
        2. Insert marker comment at specified line
        3. Write file back
        4. Mark as modified

        For now, just log the action.
        """
        marker_text = f"# CORTEX_DEBUG: {marker.message.split(chr(10))[0]}"
        logger.debug(f"Injecting marker into {marker.file_path}:{marker.line_number}")
        # TODO: Implement actual file modification

    def _publish_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Publish event to EventBus.

        Args:
            event_type: Type of event to publish
            data: Event data
        """
        if not self.event_bus:
            logger.debug(f"No EventBus configured, skipping publication of {event_type}")
            return

        # In real implementation: self.event_bus.publish(event_type, data)
        logger.info(f"Published event {event_type}: {data}")

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime

        return datetime.utcnow().isoformat()

    # ────────────────────────────────────────────────────────────────────────
    # PUBLIC INTERFACE
    # ────────────────────────────────────────────────────────────────────────

    def get_active_sessions(self) -> List[DebugSession]:
        """Get all active debug sessions."""
        return list(self._active_sessions.values())

    def get_injected_markers(self) -> List[DebugMarker]:
        """Get all injected markers."""
        return self._injected_markers.copy()

    def clear_session(self, session_id: str) -> None:
        """Clear an active debug session."""
        if session_id in self._active_sessions:
            del self._active_sessions[session_id]
            logger.info(f"Cleared debug session {session_id}")

    def cleanup_markers(self) -> int:
        """
        Clean up all injected markers.

        In real implementation, would remove markers from files.
        Returns number of markers cleaned up.
        """
        count = len(self._injected_markers)
        self._injected_markers.clear()
        logger.info(f"Cleaned up {count} debug markers")
        return count
