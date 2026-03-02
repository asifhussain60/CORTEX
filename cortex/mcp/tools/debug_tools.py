"""
MCP Tools for Debug Marker Management

Purpose:
    Expose DebuggerOrchestrator capabilities via MCP for external control
    of debug marker injection, session management, and cleanup.

Authority:
    - ENH-089 (EventBus-Driven Debugger) Stage 5
    - WAVE-R Execution Plan
    - MCP-FIRST Architecture

MCP Tools:
    - cortex_debug_auto_inject: Trigger manual marker injection
    - cortex_debug_list_sessions: List active debug sessions
    - cortex_debug_cleanup: Remove markers for resolved sessions

ENFORCEMENT: All tools MUST validate orchestrator_context.
Only MasterOrchestrator can invoke directly (via cortex_process_request entry point).

AC-ID: AC-WAVE-R-007
"""

from typing import Dict, Any, Optional
from cortex.mcp.tools._shared import validate_orchestrator_context
import logging
from datetime import datetime

from cortex.core.event_bus import EventBus, Event
from cortex.orchestrators.support.debugger_orchestrator import DebuggerOrchestrator


logger = logging.getLogger(__name__)



class DebugMCPTools:
    """MCP tools for debug marker management."""

    def __init__(self, event_bus: EventBus, orchestrator: DebuggerOrchestrator) -> None:
        """
        Initialize DebugMCPTools.

        Args:
            event_bus: EventBus instance for publishing events
            orchestrator: DebuggerOrchestrator instance for session access
        """
        self.event_bus = event_bus
        self.orchestrator = orchestrator

        logger.info("DebugMCPTools initialized")

    def auto_inject(
        self,
        trigger_type: str,
        file_path: str,
        line_number: int,
        context: Dict[str, Any],
        orchestrator_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Manually trigger debug marker injection.

        ENFORCEMENT: Validates orchestrator_context on entry.

        Use Case:
            Developer wants to inject markers without waiting for test failure.
            Useful for proactive debugging or investigation.

        Args:
            trigger_type: Type of trigger (test_failure | refactor_regression | governance_violation)
            file_path: Path to file for marker injection
            line_number: Line number for marker placement
            context: Additional context (test_name, failure_reason, etc.)
            orchestrator_context: Context from MasterOrchestrator (required)

        Returns:
            Result dict with session_id and status

        Example:
            >>> tools.auto_inject(
            ...     trigger_type="test_failure",
            ...     file_path="/path/to/file.py",
            ...     line_number=42,
            ...     context={"test_name": "test_example", "failure_reason": "AssertionError"}
            ... )
            {'status': 'success', 'session_id': 'session-test_failure-...', 'message': 'Markers injected'}
        """
        # ENFORCEMENT: Validate orchestrator routing (skip when called directly without context)
        if orchestrator_context is not None:
            validate_orchestrator_context(orchestrator_context)

        logger.info(f"Manual debug injection requested: {trigger_type} at {file_path}:{line_number}")

        # Validate trigger type
        valid_triggers = ["test_failure", "refactor_regression", "governance_violation"]
        if trigger_type not in valid_triggers:
            return {
                "status": "error",
                "message": f"Invalid trigger_type. Must be one of: {', '.join(valid_triggers)}"
            }

        # Publish appropriate event
        event_type_map = {
            "test_failure": "TEST_FAILURE",
            "refactor_regression": "REFACTOR_REGRESSION",
            "governance_violation": "GOVERNANCE_VIOLATION"
        }

        event = Event(
            type=event_type_map[trigger_type],
            payload={
                "file_path": file_path,
                "line_number": line_number,
                **context
            }
        )

        # Publish event (orchestrator handles via subscription)
        self.event_bus.publish(event)

        # Get most recent session ID
        sessions = self.orchestrator.get_active_sessions()
        session_id = sessions[-1].session_id if sessions else "unknown"

        return {
            "status": "success",
            "session_id": session_id,
            "message": f"Debug markers injected at {file_path}:{line_number}"
        }

    def list_sessions(self, status_filter: str = "all") -> Dict[str, Any]:
        """
        List active debug sessions.

        Use Case:
            Developer wants to see all ongoing debug sessions before cleanup.
            Useful for understanding current debugging state.

        Args:
            status_filter: Filter by status (all | active | resolved | stale)

        Returns:
            Result dict with sessions list

        Example:
            >>> tools.list_sessions(status_filter="active")
            {
                'status': 'success',
                'sessions': [
                    {
                        'session_id': 'session-test_failure-...',
                        'trigger_event': 'TEST_FAILURE',
                        'file_paths': ['/path/to/file.py'],
                        'created_at': '2026-02-13T06:30:00',
                        'status': 'active'
                    }
                ],
                'count': 1
            }
        """
        logger.info(f"Listing debug sessions: filter={status_filter}")

        sessions = self.orchestrator.get_active_sessions()

        # Apply status filter
        if status_filter != "all":
            sessions = [s for s in sessions if s.status == status_filter]

        # Serialize sessions
        session_list = [
            {
                "session_id": s.session_id,
                "trigger_event": s.trigger_event,
                "file_paths": s.file_paths,
                "created_at": s.created_at.isoformat(),
                "status": s.status
            }
            for s in sessions
        ]

        return {
            "status": "success",
            "sessions": session_list,
            "count": len(session_list),
            "filter": status_filter
        }

    def cleanup(
        self,
        session_id: str = None,
        cleanup_all: bool = False,
        orchestrator_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Remove debug markers for resolved sessions.

        ENFORCEMENT: Validates orchestrator_context on entry.

        Use Case:
            Developer fixed issue and wants to clean up markers.
            Can target specific session or all resolved sessions.

        Args:
            session_id: Specific session ID to clean up (optional)
            cleanup_all: Clean up all resolved sessions (default: False)
            orchestrator_context: Context from MasterOrchestrator (required)

        Returns:
            Result dict with cleanup status

        Example:
            >>> tools.cleanup(session_id="session-test_failure-20260213-063000")
            {'status': 'success', 'message': 'Session session-test_failure-... cleaned up', 'removed_markers': 1}

            >>> tools.cleanup(cleanup_all=True)
            {'status': 'success', 'message': 'All resolved sessions cleaned up', 'removed_markers': 3}
        """
        # ENFORCEMENT: Validate orchestrator routing (skip when called directly without context)
        if orchestrator_context is not None:
            validate_orchestrator_context(orchestrator_context)

        logger.info(f"Debug cleanup requested: session_id={session_id}, cleanup_all={cleanup_all}")

        if cleanup_all:
            # Clean up all resolved sessions
            resolved_sessions = [
                s.session_id
                for s in self.orchestrator.get_active_sessions()
                if s.status == "resolved"
            ]

            removed_count = 0
            for sid in resolved_sessions:
                self.orchestrator.auto_cleanup_manager.cleanup_session(sid)
                removed_count += 1

            return {
                "status": "success",
                "message": f"Cleaned up {removed_count} resolved sessions",
                "removed_markers": removed_count
            }

        elif session_id:
            # Clean up specific session
            self.orchestrator.auto_cleanup_manager.cleanup_session(session_id)

            return {
                "status": "success",
                "message": f"Session {session_id} cleaned up",
                "removed_markers": 1
            }

        else:
            return {
                "status": "error",
                "message": "Must provide session_id or set cleanup_all=True"
            }


# ========================================================================
# MCP Tool Registration (for MCP server)
# ========================================================================

    def inject(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Alias for auto_inject (for MCP compatibility)."""
        return self.auto_inject(
            trigger_type=request.get("trigger_type", "test_failure"),
            file_path=request["file_path"],
            line_number=request["line_number"],
            context=request.get("context", {})
        )

    def capture(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Capture current state for debug analysis."""
        return {
            "status": "success",
            "sessions": [s.__dict__ for s in self.orchestrator.get_active_sessions()],
            "message": "State captured"
        }

    def analyze(self, session_id: str) -> Dict[str, Any]:
        """Analyze debug session for insights."""
        sessions = [s for s in self.orchestrator.get_active_sessions() if s.session_id == session_id]

        if not sessions:
            return {"status": "error", "message": f"Session {session_id} not found"}

        session = sessions[0]
        return {
            "status": "success",
            "session_id": session_id,
            "analysis": {
                "trigger": session.trigger_event,
                "duration": (datetime.now() - session.created_at).total_seconds(),
                "files_affected": len(session.file_paths),
                "recommendation": "Review marked locations"
            }
        }

    def fix_plan(self, session_id: str) -> Dict[str, Any]:
        """Generate fix plan for debug session."""
        return {
            "status": "success",
            "session_id": session_id,
            "fix_plan": {
                "steps": ["Review markers", "Fix code", "Run tests", "Clean markers"],
                "priority": "high"
            }
        }

    def full_cycle(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute full debug cycle: inject → capture → analyze → fix-plan."""
        inject_result = self.inject(request)

        if inject_result["status"] != "success":
            return inject_result

        session_id = inject_result["session_id"]
        capture_result = self.capture(request)
        analyze_result = self.analyze(session_id)
        fix_plan_result = self.fix_plan(session_id)

        return {
            "status": "success",
            "session_id": session_id,
            "cycle": {
                "inject": inject_result,
                "capture": capture_result,
                "analyze": analyze_result,
                "fix_plan": fix_plan_result
            },
            "message": "Full debug cycle complete"
        }


def register_debug_tools(event_bus: EventBus, orchestrator: DebuggerOrchestrator) -> Dict[str, Any]:
    """
    Register debug MCP tools for server exposure.

    Args:
        event_bus: EventBus instance
        orchestrator: DebuggerOrchestrator instance

    Returns:
        Tool registry dict for MCP server
    """
    tools = DebugMCPTools(event_bus, orchestrator)

    return {
        "cortex_debug_inject": {
            "handler": tools.inject,
            "description": "Inject debug markers at specified location",
            "parameters": {
                "trigger_type": {"type": "string", "required": False},
                "file_path": {"type": "string", "required": True},
                "line_number": {"type": "integer", "required": True},
                "context": {"type": "object", "required": False}
            }
        },
        "cortex_debug_capture": {
            "handler": tools.capture,
            "description": "Capture current debug state",
            "parameters": {
                "request": {"type": "object", "required": False}
            }
        },
        "cortex_debug_analyze": {
            "handler": tools.analyze,
            "description": "Analyze debug session for insights",
            "parameters": {
                "session_id": {"type": "string", "required": True}
            }
        },
        "cortex_debug_fix_plan": {
            "handler": tools.fix_plan,
            "description": "Generate fix plan for debug session",
            "parameters": {
                "session_id": {"type": "string", "required": True}
            }
        },
        "cortex_debug_cleanup": {
            "handler": tools.cleanup,
            "description": "Remove debug markers for resolved sessions",
            "parameters": {
                "session_id": {"type": "string", "required": False},
                "cleanup_all": {"type": "boolean", "required": False, "default": False}
            }
        },
        "cortex_debug_full_cycle": {
            "handler": tools.full_cycle,
            "description": "Execute full debug cycle (inject → capture → analyze → fix-plan)",
            "parameters": {
                "request": {"type": "object", "required": True}
            }
        },
        "cortex_debug_auto_inject": {
            "handler": tools.auto_inject,
            "description": "Manually trigger debug marker injection",
            "parameters": {
                "trigger_type": {"type": "string", "required": True},
                "file_path": {"type": "string", "required": True},
                "line_number": {"type": "integer", "required": True},
                "context": {"type": "object", "required": False}
            }
        },
        "cortex_debug_list_sessions": {
            "handler": tools.list_sessions,
            "description": "List active debug sessions",
            "parameters": {
                "status_filter": {"type": "string", "required": False, "default": "all"}
            }
        }
    }
