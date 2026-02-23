"""
DebuggerOrchestrator - EventBus-Driven Debug Marker Injection

Purpose:
    Subscribes to TEST_FAILURE, REFACTOR_REGRESSION, and GOVERNANCE_VIOLATION
    events, injecting debug markers at failure locations without manual intervention.

Authority:
    - ENH-089 (EventBus-Driven Debugger)
    - CORE-041 (Event-Driven Architecture)
    - WAVE-R Execution Plan

Usage:
    orchestrator = DebuggerOrchestrator(event_bus, marker_engine, cleanup_manager)
    # Automatically handles events via subscriptions

AC-ID: AC-WAVE-R-002
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import logging
import time

from cortex.core.event_bus import EventBus, Event
from cortex.models.canonical_enums import IntentType
from cortex.core.interfaces.i_orchestrator import IOrchestrator
from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin
from cortex.core.workflow_template_mixin import WorkflowTemplateMixin


logger = logging.getLogger(__name__)


@dataclass
class DebugSession:
    """Represents an active debug session."""
    session_id: str
    trigger_event: str
    file_paths: List[str]
    created_at: datetime
    status: str  # active | resolved | stale


class DebuggerOrchestrator(IOrchestrator, OrchestratorProtocolMixin, WorkflowTemplateMixin):
    """
    Orchestrates automatic debug marker injection via EventBus.
    
    Subscriptions:
        - TEST_FAILURE: TDDOrchestrator emits on test failures
        - REFACTOR_REGRESSION: EnhancedRefactoringOrchestrator emits on regressions
        - GOVERNANCE_VIOLATION: EnforcementOrchestrator emits on violations
    
    Publications:
        - DEBUG_MARKERS_INJECTED: Emitted after successful marker injection
        - DEBUG_SESSION_READY: Emitted when debug session is ready for developer
    
    Example:
        >>> orchestrator = DebuggerOrchestrator(event_bus)
        >>> # TEST_FAILURE event arrives automatically
        >>> # Markers injected at failure location
        >>> # Developer opens file → markers already present
    """
    
    def __init__(
        self,
        event_bus: EventBus,
        marker_injection_engine: Optional[Any] = None,
        auto_cleanup_manager: Optional[Any] = None
    ) -> None:
        """
        Initialize DebuggerOrchestrator.
        
        Args:
            event_bus: EventBus instance for pub/sub
            marker_injection_engine: Engine for injecting markers (injected for testing)
            auto_cleanup_manager: Manager for auto-cleanup (injected for testing)
        """
        self.event_bus = event_bus
        
        # Initialize engine and manager if not provided
        if marker_injection_engine is None:
            from cortex.orchestrators.support.debugging.marker_injection_engine import MarkerInjectionEngine
            self.marker_injection_engine = MarkerInjectionEngine()
        else:
            self.marker_injection_engine = marker_injection_engine
        
        if auto_cleanup_manager is None:
            from cortex.orchestrators.support.debugging.auto_cleanup_manager import AutoCleanupManager
            self.auto_cleanup_manager = AutoCleanupManager()
        else:
            self.auto_cleanup_manager = auto_cleanup_manager
        
        self.active_sessions: Dict[str, DebugSession] = {}
        
        # Setup EventBus subscriptions
        self._setup_subscriptions()
        
        logger.info("DebuggerOrchestrator initialized with EventBus subscriptions")
    
    def _setup_subscriptions(self) -> None:
        """Subscribe to relevant EventBus topics."""
        self.event_bus.subscribe("TEST_FAILURE", self.handle_test_failure)
        self.event_bus.subscribe("REFACTOR_REGRESSION", self.handle_refactor_regression)
        self.event_bus.subscribe("GOVERNANCE_VIOLATION", self.handle_governance_violation)
        self.event_bus.subscribe("TESTS_PASSED", self.handle_tests_passed)
        
        logger.debug("Subscribed to: TEST_FAILURE, REFACTOR_REGRESSION, GOVERNANCE_VIOLATION, TESTS_PASSED")
    
    # ========================================================================
    # Event Handlers
    # ========================================================================
    
    def handle_test_failure(self, event: Event) -> None:
        """
        Handle TEST_FAILURE event from TDDOrchestrator.
        
        Event Payload:
            - test_name: str
            - file_path: str
            - line_number: int
            - failure_reason: str
        
        Args:
            event: TEST_FAILURE event from TDDOrchestrator
        """
        payload = event.payload
        
        logger.info(f"TEST_FAILURE received: {payload.get('test_name')}")
        logger.debug(f"Failure location: {payload.get('file_path')}:{payload.get('line_number')}")
        
        _ts = int(time.time() * 1000)
        logger.info("AC_START: AC-DEBUGGER-%d", _ts)
        _t0 = time.perf_counter()
        try:
            # Generate session ID
            session_id = self._generate_session_id("test_failure")

            # Extract payload data
            test_name = payload.get("test_name", "unknown")
            file_path = payload.get("file_path", "")
            line_number = payload.get("line_number", 0)
            failure_reason = payload.get("failure_reason", "")

            # Create debug session
            session = DebugSession(
                session_id=session_id,
                trigger_event="TEST_FAILURE",
                file_paths=[file_path],
                created_at=datetime.now(),
                status="active"
            )
            self.active_sessions[session_id] = session

            # Inject markers (if engine available)
            if self.marker_injection_engine:
                self.marker_injection_engine.inject(
                    strategy="test_failure",
                    session_id=session_id,
                    file_path=file_path,
                    line_number=line_number,
                    context={
                        "test_name": test_name,
                        "failure_reason": failure_reason
                    }
                )

            # Emit DEBUG_MARKERS_INJECTED event
            self.event_bus.publish(Event(
                type="DEBUG_MARKERS_INJECTED",
                payload={
                    "session_id": session_id,
                    "file_paths": [file_path],
                    "marker_count": 1,
                    "trigger": "TEST_FAILURE"
                }
            ))

            _elapsed = int((time.perf_counter() - _t0) * 1000)
            logger.info("AC_COMPLETE: AC-DEBUGGER-%d ✅ (%dms)", _ts, _elapsed)
            logger.info(f"Debug session {session_id} created and markers injected")
        except Exception as exc:
            _elapsed = int((time.perf_counter() - _t0) * 1000)
            logger.info("AC_COMPLETE: AC-DEBUGGER-%d ❌ %s (%dms)", _ts, type(exc).__name__, _elapsed)
            raise
    
    def handle_refactor_regression(self, event: Event) -> None:
        """
        Handle REFACTOR_REGRESSION event from EnhancedRefactoringOrchestrator.
        
        Event Payload:
            - refactor_type: str
            - affected_files: List[str]
            - regression_type: str (performance_latency | test_failure | behavior_change)
        
        Args:
            event: REFACTOR_REGRESSION event
        """
        payload = event.payload
        
        logger.info(f"REFACTOR_REGRESSION received: {payload.get('refactor_type')}")
        
        # Generate session ID
        session_id = self._generate_session_id("refactor_regression")
        
        # Extract payload data
        affected_files = payload.get("affected_files", [])
        regression_type = payload.get("regression_type", "unknown")
        
        # Create debug session
        session = DebugSession(
            session_id=session_id,
            trigger_event="REFACTOR_REGRESSION",
            file_paths=affected_files,
            created_at=datetime.now(),
            status="active"
        )
        self.active_sessions[session_id] = session
        
        # Inject markers in affected files (if engine available)
        if self.marker_injection_engine:
            for file_path in affected_files:
                self.marker_injection_engine.inject(
                    strategy="refactor_regression",
                    session_id=session_id,
                    file_path=file_path,
                    context={
                        "regression_type": regression_type,
                        "refactor_type": payload.get("refactor_type", "")
                    }
                )
        
        # Emit event
        self.event_bus.publish(Event(
            type="DEBUG_MARKERS_INJECTED",
            payload={
                "session_id": session_id,
                "file_paths": affected_files,
                "marker_count": len(affected_files),
                "trigger": "REFACTOR_REGRESSION"
            }
        ))
        
        logger.info(f"Debug session {session_id} created for {len(affected_files)} files")
    
    def handle_governance_violation(self, event: Event) -> None:
        """
        Handle GOVERNANCE_VIOLATION event from EnforcementOrchestrator.
        
        Event Payload:
            - rule_id: str (e.g., "CORE-008")
            - file_path: str
            - violation_details: Dict
        
        Args:
            event: GOVERNANCE_VIOLATION event
        """
        payload = event.payload
        
        logger.info(f"GOVERNANCE_VIOLATION received: {payload.get('rule_id')}")
        
        # Generate session ID
        session_id = self._generate_session_id("governance_violation")
        
        # Extract payload data
        rule_id = payload.get("rule_id", "unknown")
        file_path = payload.get("file_path", "")
        violation_details = payload.get("violation_details", {})
        
        # Create debug session
        session = DebugSession(
            session_id=session_id,
            trigger_event="GOVERNANCE_VIOLATION",
            file_paths=[file_path],
            created_at=datetime.now(),
            status="active"
        )
        self.active_sessions[session_id] = session
        
        # Inject markers (if engine available)
        if self.marker_injection_engine:
            self.marker_injection_engine.inject(
                strategy="governance_violation",
                session_id=session_id,
                file_path=file_path,
                context={
                    "rule_id": rule_id,
                    "violation_details": violation_details
                }
            )
        
        # Emit event
        self.event_bus.publish(Event(
            type="DEBUG_MARKERS_INJECTED",
            payload={
                "session_id": session_id,
                "file_paths": [file_path],
                "marker_count": 1,
                "trigger": "GOVERNANCE_VIOLATION"
            }
        ))
        
        logger.info(f"Debug session {session_id} created for rule {rule_id}")
    
    def handle_tests_passed(self, event: Event) -> None:
        """
        Handle TESTS_PASSED event for auto-cleanup.
        
        Event Payload:
            - test_suite: str
            - passed_count: int
        
        Args:
            event: TESTS_PASSED event from test runner
        """
        logger.info("TESTS_PASSED received, triggering auto-cleanup")
        
        # Trigger auto-cleanup (if manager available)
        if self.auto_cleanup_manager:
            resolved_sessions = self.auto_cleanup_manager.cleanup_resolved_sessions(
                self.active_sessions
            )
            
            # Mark sessions as resolved
            for session_id in resolved_sessions:
                if session_id in self.active_sessions:
                    self.active_sessions[session_id].status = "resolved"
            
            logger.info(f"Auto-cleanup resolved {len(resolved_sessions)} sessions")
    
    # ========================================================================
    # Utility Methods
    # ========================================================================
    
    def _generate_session_id(self, trigger: str) -> str:
        """
        Generate unique session ID.
        
        Format: session-{trigger}-{timestamp}
        Example: session-test_failure-20260213-031500-123456
        
        Args:
            trigger: Trigger type (test_failure | refactor_regression | governance_violation)
        
        Returns:
            Unique session ID
        """
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        return f"session-{trigger}-{timestamp}"
    
    def get_active_sessions(self) -> List[DebugSession]:
        """
        Get list of active debug sessions.
        
        Returns:
            List of active DebugSession objects
        """
        return [s for s in self.active_sessions.values() if s.status == "active"]
    
    # ========================================================================
    # IOrchestrator Interface Implementation
    # ========================================================================
    
    def get_name(self) -> str:
        """Get orchestrator name."""
        return "DebuggerOrchestrator"

    def get_recommended_template(self) -> str:
        """Get the recommended workflow template for debug operations."""
        return "quality/dead-code-removal"

    def get_version(self) -> str:
        """Get orchestrator version."""
        return "1.0.0"
    
    def initialize(self) -> Any:
        """Initialize orchestrator (already done in __init__)."""
        from cortex.core.result import Result
        return Result.success("DebuggerOrchestrator initialized")
    
    def get_mode(self) -> Any:
        """Get operation mode."""
        from cortex.core.interfaces.i_orchestrator import OperationMode
        return OperationMode.EXECUTION
    
    def get_mcp_tools(self) -> Any:
        """Get MCP tools exposed by this orchestrator."""
        from cortex.core.result import Result
        return Result.success({
            "cortex_debug_auto_inject": {
                "description": "Auto-inject debug markers on event",
                "parameters": {"event_type": "str", "payload": "dict"}
            },
            "cortex_debug_list_sessions": {
                "description": "List active debug sessions",
                "parameters": {}
            },
            "cortex_debug_cleanup": {
                "description": "Cleanup debug session",
                "parameters": {"session_id": "str"}
            }
        })
    
    def execute_operation(self, operation_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute operation with audit logging."""
        # Phase 58 — cross-cutting hooks
        self._activate_cross_cutting_hooks(
            operation=operation_name,
            orchestrator_context=parameters.get("orchestrator_context"),
            unified_context=parameters.get("unified_context"),
        )
        from cortex.core.result import Result
        result = self.execute(operation_name, parameters)
        return Result.success(result)
    
    def get_audit_trail(self, limit: int = 100) -> Any:
        """Get audit trail."""
        from cortex.core.result import Result
        # EventBus-driven, audit trail tracked via EventBus events
        return Result.success([])
    
    def get_intent_types(self) -> List[IntentType]:
        """Get supported intent types."""
        return []  # EventBus-driven, no direct intent handling
    
    def can_handle(self, intent: IntentType) -> bool:
        """Check if orchestrator can handle intent."""
        return False  # EventBus-driven, no direct intent handling
    
    def execute(self, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute operation (IOrchestrator compliance).
        
        Note: DebuggerOrchestrator is EventBus-driven, so direct execute()
        calls are not the primary usage pattern. However, this method is
        provided for IOrchestrator compliance and MCP tool exposure.
        
        Args:
            operation: Operation name (list_sessions | cleanup_session)
            parameters: Operation parameters
        
        Returns:
            Operation result
        """
        if operation == "list_sessions":
            return {
                "active_sessions": [
                    {
                        "session_id": s.session_id,
                        "trigger": s.trigger_event,
                        "files": s.file_paths,
                        "created_at": s.created_at.isoformat(),
                        "status": s.status
                    }
                    for s in self.get_active_sessions()
                ]
            }
        
        elif operation == "cleanup_session":
            session_id = parameters.get("session_id")
            if session_id in self.active_sessions:
                # Manual cleanup trigger
                if self.auto_cleanup_manager:
                    self.auto_cleanup_manager.cleanup_session(session_id)
                self.active_sessions[session_id].status = "resolved"
                return {"status": "success", "session_id": session_id}
            return {"status": "error", "message": f"Session {session_id} not found"}
        
        return {"status": "error", "message": f"Unknown operation: {operation}"}
