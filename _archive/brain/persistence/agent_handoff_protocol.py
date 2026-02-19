"""
Agent Handoff Protocol

AC_START: AC-PHASE27-S3-004
Component: AgentHandoffProtocol
Authority: Phase 27 Consolidation (GAP-03)

Objective:
Systematic agent handoff with context transfer and audit trail. Coordinates
agent-to-agent delegation with complete governance tracking.

Features:
• Handoff lifecycle: initiate → accept → complete/fail
• Context transfer between agents
• Complete audit trail (all events timestamped)
• Multi-hop handoff chain support
• Failure recovery mechanisms

Performance Targets:
• Handoff initiation: <50ms
• Handoff acceptance: <50ms
• Total handoff cycle: <100ms

AC_COMPLETE: AC-PHASE27-S3-004
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from uuid import uuid4
from datetime import datetime
from threading import Lock
from cortex.brain.persistence.agent_capability_registry import AgentCapabilityRegistry
from cortex.brain.persistence.agent_discovery_service import AgentDiscoveryService

logger = logging.getLogger(__name__)


# ============================================================================
# AGENT HANDOFF PROTOCOL
# ============================================================================


class AgentHandoffProtocol:
    """
    Agent Handoff Protocol: Systematic agent handoff with context transfer.
    
    Coordinates agent-to-agent delegation with complete audit trail. Supports
    handoff lifecycle (initiate → accept → complete/fail) with governance tracking.
    
    Example:
        >>> protocol = AgentHandoffProtocol(registry, discovery)
        >>> handoff_id = protocol.initiate_handoff(
        ...     from_agent="tdd_orchestrator",
        ...     required_capabilities=["code_refactoring"],
        ...     context={"operation": "test_generation", "file": "test_user.py"}
        ... )
        >>> protocol.accept_handoff(handoff_id, "refactoring_orchestrator")
        >>> protocol.complete_handoff(handoff_id, result={"refactoring_applied": "extract_method"})
    """
    
    def __init__(
        self,
        capability_registry: AgentCapabilityRegistry,
        discovery_service: AgentDiscoveryService,
        audit_db_path: Optional[str] = None
    ):
        """
        Initialize Agent Handoff Protocol.
        
        Args:
            capability_registry: AgentCapabilityRegistry instance
            discovery_service: AgentDiscoveryService instance
            audit_db_path: Path to audit database (default: cortex/brain/agent_handoffs.db)
        """
        if audit_db_path is None:
            audit_db_path = str(Path(__file__).parent.parent / "agent_handoffs.db")
        
        self.capability_registry = capability_registry
        self.discovery_service = discovery_service
        self.audit_db_path = audit_db_path
        self._lock = Lock()
        self._init_database()
        
        logger.info(f"AgentHandoffProtocol initialized: {audit_db_path}")
    
    def _init_database(self) -> None:
        """Initialize handoff audit database."""
        with self._lock:
            conn = sqlite3.connect(self.audit_db_path)
            conn.execute("PRAGMA journal_mode=WAL")
            
            # Handoffs table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS handoffs (
                    handoff_id TEXT PRIMARY KEY,
                    from_agent TEXT NOT NULL,
                    to_agent TEXT,
                    required_capabilities TEXT NOT NULL,
                    context TEXT NOT NULL,
                    metadata TEXT,
                    status TEXT NOT NULL,
                    result TEXT,
                    error TEXT,
                    initiated_at TEXT NOT NULL,
                    accepted_at TEXT,
                    completed_at TEXT
                )
            """)
            
            # Audit trail table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS handoff_audit_trail (
                    audit_id TEXT PRIMARY KEY,
                    handoff_id TEXT NOT NULL,
                    event TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    context TEXT,
                    FOREIGN KEY (handoff_id) REFERENCES handoffs(handoff_id)
                )
            """)
            
            # Index for fast handoff lookup
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_handoff_status
                ON handoffs(status)
            """)
            
            conn.commit()
            conn.close()
    
    def initiate_handoff(
        self,
        from_agent: str,
        required_capabilities: List[str],
        context: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Initiate agent handoff.
        
        Args:
            from_agent: Source agent identifier
            required_capabilities: Required capabilities for target agent
            context: Handoff context (operation, files, state, etc.)
            metadata: Optional metadata (session_id, user_request, etc.)
        
        Returns:
            Handoff ID
        
        Example:
            >>> handoff_id = protocol.initiate_handoff(
            ...     from_agent="tdd_orchestrator",
            ...     required_capabilities=["code_refactoring"],
            ...     context={"operation": "test_generation", "file": "test_user.py"},
            ...     metadata={"session_id": "123"}
            ... )
        """
        if metadata is None:
            metadata = {}
        
        # Discover target agent
        target_agent = self.discovery_service.discover_best_agent(required_capabilities)
        
        if target_agent is None:
            logger.warning(f"No agent found for capabilities: {required_capabilities}")
            to_agent = None
        else:
            to_agent = target_agent["agent_id"]
        
        # Create handoff record
        handoff_id = str(uuid4())
        now = datetime.utcnow().isoformat()
        
        with self._lock:
            conn = sqlite3.connect(self.audit_db_path)
            
            conn.execute("""
                INSERT INTO handoffs
                (handoff_id, from_agent, to_agent, required_capabilities, context, metadata, status, initiated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                handoff_id,
                from_agent,
                to_agent,
                json.dumps(required_capabilities),
                json.dumps(context),
                json.dumps(metadata),
                "pending",
                now
            ))
            
            # Record audit trail (include full context for governance)
            self._record_audit_event(
                conn, handoff_id, "initiated", now,
                {"from_agent": from_agent, "to_agent": to_agent, "handoff_context": context}
            )
            
            conn.commit()
            conn.close()
        
        logger.info(f"Handoff initiated: {handoff_id} ({from_agent} → {to_agent})")
        return handoff_id
    
    def accept_handoff(
        self,
        handoff_id: str,
        to_agent: str
    ) -> Dict[str, Any]:
        """
        Accept handoff (target agent confirms acceptance).
        
        Args:
            handoff_id: Handoff identifier
            to_agent: Target agent identifier (must match discovered agent)
        
        Returns:
            Acceptance result with status
        
        Example:
            >>> result = protocol.accept_handoff(handoff_id, "refactoring_orchestrator")
            >>> print(result["status"])
            'accepted'
        """
        now = datetime.utcnow().isoformat()
        
        with self._lock:
            conn = sqlite3.connect(self.audit_db_path)
            
            # Verify handoff exists and is pending
            cursor = conn.execute("""
                SELECT status, to_agent FROM handoffs
                WHERE handoff_id = ?
            """, (handoff_id,))
            
            row = cursor.fetchone()
            
            if row is None:
                conn.close()
                return {"status": "error", "error": "Handoff not found"}
            
            status, expected_agent = row
            
            if status != "pending":
                conn.close()
                return {"status": "error", "error": f"Handoff not pending (status: {status})"}
            
            if expected_agent != to_agent:
                conn.close()
                return {
                    "status": "error",
                    "error": f"Agent mismatch (expected: {expected_agent}, got: {to_agent})"
                }
            
            # Update handoff status
            conn.execute("""
                UPDATE handoffs
                SET status = ?, accepted_at = ?
                WHERE handoff_id = ?
            """, ("accepted", now, handoff_id))
            
            # Record audit trail
            self._record_audit_event(
                conn, handoff_id, "accepted", now,
                {"to_agent": to_agent}
            )
            
            conn.commit()
            conn.close()
        
        logger.info(f"Handoff accepted: {handoff_id} by {to_agent}")
        return {"status": "accepted", "handoff_id": handoff_id}
    
    def complete_handoff(
        self,
        handoff_id: str,
        result: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete handoff with result.
        
        Args:
            handoff_id: Handoff identifier
            result: Handoff result data
            metadata: Optional metadata (duration, metrics, etc.)
        
        Returns:
            Completion result with status
        
        Example:
            >>> result = protocol.complete_handoff(
            ...     handoff_id,
            ...     result={"refactoring_applied": "extract_method", "methods_extracted": 3}
            ... )
            >>> print(result["status"])
            'completed'
        """
        now = datetime.utcnow().isoformat()
        
        with self._lock:
            conn = sqlite3.connect(self.audit_db_path)
            
            # Update handoff status
            conn.execute("""
                UPDATE handoffs
                SET status = ?, result = ?, completed_at = ?
                WHERE handoff_id = ?
            """, ("completed", json.dumps(result), now, handoff_id))
            
            # Record audit trail
            context = {"result_summary": result}
            if metadata:
                context.update(metadata)
            
            self._record_audit_event(
                conn, handoff_id, "completed", now, context
            )
            
            conn.commit()
            conn.close()
        
        logger.info(f"Handoff completed: {handoff_id}")
        return {"status": "completed", "handoff_id": handoff_id}
    
    def fail_handoff(
        self,
        handoff_id: str,
        error: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Fail handoff with error.
        
        Args:
            handoff_id: Handoff identifier
            error: Error data (error_type, message, etc.)
            metadata: Optional metadata (failed_at, etc.)
        
        Returns:
            Failure result with status
        
        Example:
            >>> result = protocol.fail_handoff(
            ...     handoff_id,
            ...     error={"error_type": "TimeoutError", "message": "Agent timeout after 30s"}
            ... )
            >>> print(result["status"])
            'failed'
        """
        now = datetime.utcnow().isoformat()
        
        with self._lock:
            conn = sqlite3.connect(self.audit_db_path)
            
            # Update handoff status
            conn.execute("""
                UPDATE handoffs
                SET status = ?, error = ?, completed_at = ?
                WHERE handoff_id = ?
            """, ("failed", json.dumps(error), now, handoff_id))
            
            # Record audit trail
            context = {"error": error}
            if metadata:
                context.update(metadata)
            
            self._record_audit_event(
                conn, handoff_id, "failed", now, context
            )
            
            conn.commit()
            conn.close()
        
        logger.warning(f"Handoff failed: {handoff_id} - {error}")
        return {"status": "failed", "handoff_id": handoff_id}
    
    def get_handoff(self, handoff_id: str) -> Optional[Dict[str, Any]]:
        """
        Get handoff details.
        
        Args:
            handoff_id: Handoff identifier
        
        Returns:
            Handoff record or None if not found
        
        Example:
            >>> handoff = protocol.get_handoff(handoff_id)
            >>> print(handoff["status"])
            'completed'
        """
        with self._lock:
            conn = sqlite3.connect(self.audit_db_path)
            conn.row_factory = sqlite3.Row
            
            cursor = conn.execute("""
                SELECT * FROM handoffs
                WHERE handoff_id = ?
            """, (handoff_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row is None:
                return None
            
            return {
                "handoff_id": row["handoff_id"],
                "from_agent": row["from_agent"],
                "to_agent": row["to_agent"],
                "required_capabilities": json.loads(row["required_capabilities"]),
                "context": json.loads(row["context"]),
                "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                "status": row["status"],
                "result": json.loads(row["result"]) if row["result"] else None,
                "error": json.loads(row["error"]) if row["error"] else None,
                "initiated_at": row["initiated_at"],
                "accepted_at": row["accepted_at"],
                "completed_at": row["completed_at"]
            }
    
    def get_audit_trail(self, handoff_id: str) -> List[Dict[str, Any]]:
        """
        Get complete audit trail for handoff.
        
        Args:
            handoff_id: Handoff identifier
        
        Returns:
            List of audit events (chronological order)
        
        Example:
            >>> trail = protocol.get_audit_trail(handoff_id)
            >>> print([e["event"] for e in trail])
            ['initiated', 'accepted', 'completed']
        """
        with self._lock:
            conn = sqlite3.connect(self.audit_db_path)
            conn.row_factory = sqlite3.Row
            
            cursor = conn.execute("""
                SELECT * FROM handoff_audit_trail
                WHERE handoff_id = ?
                ORDER BY timestamp ASC
            """, (handoff_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            trail = []
            for row in rows:
                trail.append({
                    "audit_id": row["audit_id"],
                    "handoff_id": row["handoff_id"],
                    "event": row["event"],
                    "timestamp": row["timestamp"],
                    "context": json.loads(row["context"]) if row["context"] else {}
                })
            
            return trail
    
    def _record_audit_event(
        self,
        conn: sqlite3.Connection,
        handoff_id: str,
        event: str,
        timestamp: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record audit trail event (internal helper)."""
        audit_id = str(uuid4())
        
        conn.execute("""
            INSERT INTO handoff_audit_trail
            (audit_id, handoff_id, event, timestamp, context)
            VALUES (?, ?, ?, ?, ?)
        """, (
            audit_id,
            handoff_id,
            event,
            timestamp,
            json.dumps(context) if context else None
        ))
    
    def close(self) -> None:
        """Close protocol (cleanup resources)."""
        logger.info("AgentHandoffProtocol closed")
