"""
Orchestrator Audit Mixin - Universal audit logging for orchestrators.

Authority: AC-GOLDEN-E2E-004
Pattern: Composition over inheritance (mixin pattern)

Usage:
    class MyOrchestrator(IOrchestrator, OrchestratorAuditMixin):
        def orchestrate(self, context):
            correlation_id = self.audit_start(
                "ORCHESTRATE",
                {"intent": context.get("intent")}
            )
            
            # ... perform work ...
            
            self.audit_complete(
                correlation_id,
                "ORCHESTRATE",
                {"status": "success"}
            )
"""

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from contextlib import contextmanager
import time


class OrchestratorAuditMixin:
    """
    Mixin providing structured audit logging for orchestrators.
    
    Features:
    - Automatic correlation ID generation
    - Start/complete event pairs
    - SQLite persistence to governance.db
    - Query support for golden tests
    - Performance tracking (duration_ms)
    
    Requirements:
    - Orchestrator must have `self.__class__.__name__` (standard Python)
    - Optional: `self.session_id` for session tracking
    """
    
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize audit mixin."""
        super().__init__(*args, **kwargs)
        self._audit_db_path: Optional[Path] = None
        self._audit_session_id: Optional[str] = None
    
    def _get_audit_db_path(self) -> Path:
        """Get path to audit database (governance.db)."""
        if self._audit_db_path is None:
            # Default to cortex_intelligence/governance.db
            project_root = Path(__file__).parent.parent.parent.parent
            self._audit_db_path = project_root / "cortex_intelligence" / "governance.db"
        return self._audit_db_path
    
    def _get_session_id(self) -> str:
        """Get or create session ID for audit tracking."""
        if self._audit_session_id is None:
            # Try to get from orchestrator instance
            if hasattr(self, 'session_id'):
                self._audit_session_id = getattr(self, 'session_id')
            else:
                self._audit_session_id = f"session-{uuid.uuid4().hex[:8]}"
        return self._audit_session_id
    
    @contextmanager
    def _get_audit_connection(self) -> sqlite3.Connection:
        """Get database connection for audit logging."""
        db_path = self._get_audit_db_path()
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def audit_start(
        self,
        activity: str,
        input_parameters: Optional[Dict[str, Any]] = None,
        workflow_stage: str = "EXECUTION",
        parent_trace_id: Optional[str] = None,
    ) -> str:
        """
        Log orchestrator activity start.
        
        Args:
            activity: Activity name (e.g., "CLASSIFY_INTENT", "GENERATE_TESTS")
            input_parameters: Input parameters as dict
            workflow_stage: One of INTERACTION, INTENT, INTELLIGENCE, EXECUTION
            parent_trace_id: Parent trace ID for hierarchical tracking
        
        Returns:
            correlation_id: Unique ID for this activity (use in audit_complete)
        """
        correlation_id = f"corr-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.now(timezone.utc).isoformat()
        orchestrator_name = self.__class__.__name__
        session_id = self._get_session_id()
        
        # Serialize input parameters
        input_params_json = json.dumps(input_parameters) if input_parameters else None
        
        try:
            with self._get_audit_connection() as conn:
                conn.execute("""
                    INSERT INTO orchestrator_audit_events (
                        timestamp, orchestrator_name, workflow_stage, activity,
                        correlation_id, parent_trace_id, session_id,
                        input_parameters, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    timestamp,
                    orchestrator_name,
                    workflow_stage,
                    activity,
                    correlation_id,
                    parent_trace_id,
                    session_id,
                    input_params_json,
                    'STARTED'
                ))
                conn.commit()
        except sqlite3.OperationalError:
            # Table doesn't exist yet - fail silently in development
            # Production should have schema applied
            pass
        
        return correlation_id
    
    def audit_complete(
        self,
        correlation_id: str,
        activity: str,
        output_results: Optional[Dict[str, Any]] = None,
        status: str = "COMPLETED",
        reasoning: Optional[str] = None,
        decision_point: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log orchestrator activity completion.
        
        Args:
            correlation_id: Correlation ID from audit_start
            activity: Activity name (must match audit_start)
            output_results: Output results as dict
            status: One of COMPLETED, FAILED, SKIPPED
            reasoning: Human-readable reasoning for decision
            decision_point: Key decision data as dict
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        orchestrator_name = self.__class__.__name__
        
        # Serialize output
        output_json = json.dumps(output_results) if output_results else None
        decision_json = json.dumps(decision_point) if decision_point else None
        
        # Calculate duration by finding start event
        duration_ms = None
        try:
            with self._get_audit_connection() as conn:
                cursor = conn.execute("""
                    SELECT timestamp FROM orchestrator_audit_events
                    WHERE correlation_id = ? AND status = 'STARTED'
                    ORDER BY id DESC LIMIT 1
                """, (correlation_id,))
                row = cursor.fetchone()
                if row:
                    start_time = datetime.fromisoformat(row['timestamp'])
                    end_time = datetime.now(timezone.utc)
                    duration_ms = int((end_time - start_time).total_seconds() * 1000)
                
                # Insert completion event
                conn.execute("""
                    INSERT INTO orchestrator_audit_events (
                        timestamp, orchestrator_name, workflow_stage, activity,
                        correlation_id, session_id, output_results, status,
                        reasoning, decision_point, duration_ms
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    timestamp,
                    orchestrator_name,
                    'EXECUTION',  # Default workflow stage for completion
                    activity,
                    correlation_id,
                    self._get_session_id(),
                    output_json,
                    status,
                    reasoning,
                    decision_json,
                    duration_ms
                ))
                conn.commit()
        except sqlite3.OperationalError:
            # Table doesn't exist yet - fail silently
            pass
    
    def get_audit_events(
        self,
        correlation_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve audit events for this orchestrator.
        
        Args:
            correlation_id: Filter by correlation ID
            session_id: Filter by session ID
        
        Returns:
            List of audit events as dicts
        """
        try:
            with self._get_audit_connection() as conn:
                query = "SELECT * FROM v_golden_test_audit_trail WHERE orchestrator_name = ?"
                params = [self.__class__.__name__]
                
                if correlation_id:
                    query += " AND correlation_id = ?"
                    params.append(correlation_id)
                
                if session_id:
                    query += " AND session_id = ?"
                    params.append(session_id)
                
                query += " ORDER BY timestamp ASC"
                
                cursor = conn.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.OperationalError:
            # Table or view doesn't exist
            return []
    
    @contextmanager
    def audit_activity(
        self,
        activity: str,
        input_parameters: Optional[Dict[str, Any]] = None,
        workflow_stage: str = "EXECUTION",
    ):
        """
        Context manager for automatic start/complete logging.
        
        Usage:
            with self.audit_activity("CLASSIFY_INTENT", {"text": utterance}):
                result = self._do_classification(utterance)
                return result
        
        Args:
            activity: Activity name
            input_parameters: Input parameters
            workflow_stage: Workflow stage
        
        Yields:
            correlation_id: Correlation ID for this activity
        """
        correlation_id = self.audit_start(activity, input_parameters, workflow_stage)
        start_time = time.time()
        
        try:
            yield correlation_id
            # Success - log completion
            duration_ms = int((time.time() - start_time) * 1000)
            self.audit_complete(
                correlation_id,
                activity,
                status="COMPLETED",
                output_results={"duration_ms": duration_ms}
            )
        except Exception as e:
            # Failure - log error
            duration_ms = int((time.time() - start_time) * 1000)
            self.audit_complete(
                correlation_id,
                activity,
                status="FAILED",
                output_results={
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "duration_ms": duration_ms
                }
            )
            raise
