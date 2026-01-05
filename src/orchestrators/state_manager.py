"""
State Manager - Cross-Orchestrator State Coordination.

Enables orchestrators to share state via PlanningStateDB, track execution lifecycle,
and coordinate dependencies.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum

from src.database.planning_state_db import PlanningStateDB


class ExecutionStatus(str, Enum):
    """Orchestrator execution status."""
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ExecutionLogEntry:
    """Execution log entry for orchestrator lifecycle tracking."""
    log_id: int
    orchestrator_id: str
    status: ExecutionStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    result: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'log_id': self.log_id,
            'orchestrator_id': self.orchestrator_id,
            'status': self.status.value,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration_seconds': self.duration_seconds,
            'parameters': self.parameters,
            'result': self.result,
            'error': self.error
        }


@dataclass
class SharedState:
    """Shared state between orchestrators."""
    state_id: str
    from_orchestrator: str
    to_orchestrator: str
    data: Dict[str, Any]
    created_at: datetime
    consumed: bool = False
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'state_id': self.state_id,
            'from_orchestrator': self.from_orchestrator,
            'to_orchestrator': self.to_orchestrator,
            'data': self.data,
            'created_at': self.created_at.isoformat(),
            'consumed': self.consumed
        }


class StateManager:
    """
    Cross-orchestrator state coordination via PlanningStateDB.
    
    Provides:
    - Execution lifecycle tracking (start/complete/fail)
    - State sharing between orchestrators
    - Dependency coordination
    - Execution history queries
    
    Features:
    - ACID transactions via SQLite
    - Structured execution logs
    - Key-value state sharing
    - Automatic timestamp tracking
    
    Usage:
        state_mgr = StateManager(db)
        
        # Track execution
        log_id = state_mgr.begin_execution('planning_v5', {...})
        state_mgr.complete_execution('planning_v5', {...})
        
        # Share state
        state_mgr.share_state('planning_v5', 'ado_v2', {'plan_id': 'xyz'})
        shared = state_mgr.get_shared_state('ado_v2')
    """
    
    def __init__(self, db: PlanningStateDB):
        """
        Initialize state manager with database.
        
        Args:
            db: PlanningStateDB instance
        """
        self.db = db
        self.logger = logging.getLogger("cortex.orchestrators.state_manager")
        
        # Execution tracking
        self._active_executions: Dict[str, int] = {}  # orchestrator_id -> log_id
        
        self.logger.info("StateManager initialized")
    
    def begin_execution(
        self,
        orchestrator_id: str,
        parameters: Dict[str, Any]
    ) -> int:
        """
        Create execution log entry for orchestrator start.
        
        Args:
            orchestrator_id: Unique orchestrator identifier
            parameters: Execution parameters
        
        Returns:
            Log ID for tracking
        """
        log_id = self.db.log_execution(
            orchestrator_id=orchestrator_id,
            status='started',
            parameters=parameters
        )
        
        self._active_executions[orchestrator_id] = log_id
        
        self.logger.info(
            f"Execution started: {orchestrator_id} (log_id={log_id})"
        )
        
        return log_id
    
    def update_execution_status(
        self,
        orchestrator_id: str,
        status: str,
        result: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Update execution status for running orchestrator.
        
        Args:
            orchestrator_id: Orchestrator identifier
            status: New status ('in_progress', 'completed', 'failed')
            result: Optional result data
        """
        log_id = self._active_executions.get(orchestrator_id)
        if not log_id:
            self.logger.warning(
                f"No active execution found for: {orchestrator_id}"
            )
            return
        
        self.db.update_execution_log(
            log_id=log_id,
            status=status,
            result=result or {}
        )
        
        self.logger.debug(
            f"Updated execution: {orchestrator_id} → {status}"
        )
    
    def log_execution(
        self,
        orchestrator: str,
        phase: str,
        status: str,
        metrics: Dict[str, Any]
    ) -> None:
        """
        Log execution event to database.
        
        Wrapper around PlanningStateDB.log_execution() for convenience.
        Provides simpler interface for orchestrators to log phase execution.
        
        Args:
            orchestrator: Orchestrator name
            phase: Phase identifier
            status: Execution status (started/completed/failed)
            metrics: Execution metrics dictionary
        """
        self.db.log_execution(
            orchestrator_id=orchestrator,
            status=status,
            parameters={
                'phase': phase,
                'metrics': metrics
            }
        )
        
        self.logger.info(
            f"Logged execution: {orchestrator}/{phase} - {status}"
        )
    
    def complete_execution(
        self,
        orchestrator_id: str,
        result: Dict[str, Any]
    ) -> None:
        """
        Mark execution as completed successfully.
        
        Args:
            orchestrator_id: Orchestrator identifier
            result: Execution result data
        """
        self.update_execution_status(orchestrator_id, 'completed', result)
        
        # Remove from active tracking
        if orchestrator_id in self._active_executions:
            log_id = self._active_executions.pop(orchestrator_id)
            self.logger.info(
                f"Execution completed: {orchestrator_id} (log_id={log_id})"
            )
    
    def fail_execution(
        self,
        orchestrator_id: str,
        error: str
    ) -> None:
        """
        Mark execution as failed with error.
        
        Args:
            orchestrator_id: Orchestrator identifier
            error: Error message/stack trace
        """
        log_id = self._active_executions.get(orchestrator_id)
        if log_id:
            self.db.update_execution_log(
                log_id=log_id,
                status='failed',
                result={'error': error}
            )
            
            self._active_executions.pop(orchestrator_id)
            
            self.logger.error(
                f"Execution failed: {orchestrator_id} (log_id={log_id}) - {error}"
            )
    
    def share_state(
        self,
        from_orchestrator: str,
        to_orchestrator: str,
        data: Dict[str, Any]
    ) -> str:
        """
        Share state from one orchestrator to another.
        
        Args:
            from_orchestrator: Source orchestrator ID
            to_orchestrator: Destination orchestrator ID
            data: State data to share
        
        Returns:
            State ID for tracking
        """
        # Store as artifact with special type
        state_id = self.db.save_shared_state(
            from_orchestrator=from_orchestrator,
            to_orchestrator=to_orchestrator,
            data=data
        )
        
        self.logger.info(
            f"State shared: {from_orchestrator} → {to_orchestrator} "
            f"(state_id={state_id})"
        )
        
        return state_id
    
    def get_shared_state(
        self,
        orchestrator_id: str,
        from_orchestrator: Optional[str] = None,
        consume: bool = True
    ) -> List[SharedState]:
        """
        Retrieve state shared with this orchestrator.
        
        Args:
            orchestrator_id: Receiving orchestrator ID
            from_orchestrator: Optional filter by sender
            consume: Mark state as consumed after retrieval
        
        Returns:
            List of shared state entries
        """
        states = self.db.get_shared_state(
            to_orchestrator=orchestrator_id,
            from_orchestrator=from_orchestrator
        )
        
        # Mark as consumed if requested
        if consume:
            for state in states:
                self.db.mark_state_consumed(state['state_id'])
        
        self.logger.debug(
            f"Retrieved {len(states)} shared state(s) for {orchestrator_id}"
        )
        
        return [
            SharedState(
                state_id=s['state_id'],
                from_orchestrator=s['from_orchestrator'],
                to_orchestrator=s['to_orchestrator'],
                data=json.loads(s['data']) if isinstance(s['data'], str) else s['data'],
                created_at=datetime.fromisoformat(s['created_at']),
                consumed=s.get('consumed', False)
            )
            for s in states
        ]
    
    def get_execution_history(
        self,
        orchestrator_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[ExecutionLogEntry]:
        """
        Query execution history.
        
        Args:
            orchestrator_id: Optional filter by orchestrator
            status: Optional filter by status
            limit: Maximum results to return
        
        Returns:
            List of execution log entries
        """
        logs = self.db.get_execution_logs(
            orchestrator_id=orchestrator_id,
            status=status,
            limit=limit
        )
        
        return [
            ExecutionLogEntry(
                log_id=log['log_id'],
                orchestrator_id=log['orchestrator_id'],
                status=ExecutionStatus(log['status']),
                started_at=datetime.fromisoformat(log['started_at']),
                completed_at=datetime.fromisoformat(log['completed_at']) if log.get('completed_at') else None,
                duration_seconds=log.get('duration_seconds'),
                parameters=json.loads(log['parameters']) if isinstance(log['parameters'], str) else log.get('parameters', {}),
                result=json.loads(log['result']) if isinstance(log['result'], str) else log.get('result', {}),
                error=log.get('error')
            )
            for log in logs
        ]
    
    def is_orchestrator_running(self, orchestrator_id: str) -> bool:
        """
        Check if orchestrator is currently executing.
        
        Args:
            orchestrator_id: Orchestrator identifier
        
        Returns:
            True if execution is active
        """
        return orchestrator_id in self._active_executions
    
    def get_active_executions(self) -> List[str]:
        """
        Get list of currently executing orchestrators.
        
        Returns:
            List of orchestrator IDs
        """
        return list(self._active_executions.keys())
    
    def cancel_execution(self, orchestrator_id: str) -> bool:
        """
        Cancel running orchestrator execution.
        
        Args:
            orchestrator_id: Orchestrator identifier
        
        Returns:
            True if cancelled successfully
        """
        if orchestrator_id not in self._active_executions:
            return False
        
        self.update_execution_status(orchestrator_id, 'cancelled')
        self._active_executions.pop(orchestrator_id)
        
        self.logger.warning(f"Execution cancelled: {orchestrator_id}")
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get state manager statistics.
        
        Returns:
            Dictionary with metrics
        """
        return {
            'active_executions': len(self._active_executions),
            'orchestrators': list(self._active_executions.keys()),
            'total_executions': self.db.count_execution_logs(),
            'failed_executions': self.db.count_execution_logs(status='failed'),
            'completed_executions': self.db.count_execution_logs(status='completed')
        }
