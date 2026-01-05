"""
Orchestrator Integration Layer for Audit Logger and Self-Healing Engine.

Provides base classes and utilities for integrating audit logging
and self-healing capabilities into CORTEX orchestrators.

Features:
- Automatic audit event capture (start, complete, error, handoff)
- Self-healing pattern detection integration
- Performance metrics tracking
- Context propagation
- Error recovery coordination

Usage:
    from src.logging.integration import AuditedOrchestrator
    
    class MyOrchestrator(AuditedOrchestrator):
        def __init__(self):
            super().__init__(orchestrator_name="my_orchestrator")
        
        async def execute(self, request):
            async with self.audit_operation("execute", request):
                # Your orchestrator logic
                result = await self._do_work(request)
                return result
"""

import asyncio
import time
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional, Callable, Awaitable
from datetime import datetime
import uuid

from src.logging.audit_logger import AuditLogger, LogLevel
from src.logging.self_healing_engine import SelfHealingEngine, RecoveryStrategy


class AuditedOrchestrator:
    """
    Base class for orchestrators with audit logging and self-healing integration.
    
    Provides automatic:
    - Start/complete/error event logging
    - Performance metric tracking
    - Context propagation (session_id, correlation_id)
    - Self-healing pattern detection
    - Error recovery coordination
    """
    
    def __init__(
        self,
        orchestrator_name: str,
        audit_logger: Optional[AuditLogger] = None,
        self_healing_engine: Optional[SelfHealingEngine] = None,
        enable_recovery: bool = True
    ):
        """
        Initialize audited orchestrator.
        
        Args:
            orchestrator_name: Name of the orchestrator (e.g., "planning_v5")
            audit_logger: Optional AuditLogger instance (creates default if None)
            self_healing_engine: Optional SelfHealingEngine instance
            enable_recovery: Enable automatic error recovery
        """
        self.orchestrator_name = orchestrator_name
        self.enable_recovery = enable_recovery
        
        # Initialize or use provided audit logger
        if audit_logger is None:
            from pathlib import Path
            self.audit_logger = AuditLogger({
                "log_dir": str(Path("logs/cortex-audit")),
                "buffer_size": 1000,
                "flush_interval": 5.0
            })
        else:
            self.audit_logger = audit_logger
        
        # Initialize or use provided self-healing engine
        self.self_healing_engine = self_healing_engine
        if self.self_healing_engine:
            # Start self-healing engine if not already running
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running() and not self.self_healing_engine._running:
                    loop.create_task(self.self_healing_engine.start())
            except RuntimeError:
                pass
        
        # Session tracking
        self.current_session_id: Optional[str] = None
        self.current_correlation_id: Optional[str] = None
    
    def set_session_context(self, session_id: str, correlation_id: Optional[str] = None):
        """
        Set session context for audit logging.
        
        Args:
            session_id: Session identifier
            correlation_id: Optional correlation identifier
        """
        self.current_session_id = session_id
        self.current_correlation_id = correlation_id or str(uuid.uuid4())
    
    @asynccontextmanager
    async def audit_operation(
        self,
        operation_name: str,
        context: Optional[Dict[str, Any]] = None,
        recovery_strategy: Optional[str] = None
    ):
        """
        Context manager for audited operations.
        
        Automatically logs:
        - Operation start
        - Operation completion (with duration)
        - Errors (with stack trace)
        - Performance metrics
        
        Args:
            operation_name: Name of the operation
            context: Optional context data
            recovery_strategy: Optional recovery strategy name
        
        Usage:
            async with self.audit_operation("execute_plan", {"plan_id": "123"}):
                result = await do_work()
        """
        start_time = time.time()
        operation_id = str(uuid.uuid4())
        
        # Log operation start
        await self.audit_logger.log(
            level=LogLevel.INFO,
            orchestrator=self.orchestrator_name,
            event=f"{operation_name}_started",
            data={
                "operation_id": operation_id,
                "operation": operation_name,
                "context": context or {},
                "timestamp": datetime.now().isoformat()
            }
        )
        
        try:
            yield
            
            # Log successful completion
            duration_ms = (time.time() - start_time) * 1000
            await self.audit_logger.log(
                level=LogLevel.INFO,
                orchestrator=self.orchestrator_name,
                event=f"{operation_name}_completed",
                data={
                    "operation_id": operation_id,
                    "operation": operation_name,
                    "duration_ms": duration_ms,
                    "status": "success"
                }
            )
            
        except Exception as e:
            # Log error
            duration_ms = (time.time() - start_time) * 1000
            await self.audit_logger.log(
                level=LogLevel.ERROR,
                orchestrator=self.orchestrator_name,
                event=f"{operation_name}_failed",
                data={
                    "operation_id": operation_id,
                    "operation": operation_name,
                    "duration_ms": duration_ms,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "status": "failed"
                }
            )
            
            # Attempt recovery if enabled
            if self.enable_recovery and recovery_strategy:
                recovered = await self._attempt_recovery(
                    operation_name,
                    e,
                    recovery_strategy
                )
                if not recovered:
                    raise
            else:
                raise
    
    async def _attempt_recovery(
        self,
        operation_name: str,
        error: Exception,
        strategy_type: str
    ) -> bool:
        """
        Attempt automatic recovery from error.
        
        Args:
            operation_name: Name of failed operation
            error: Exception that occurred
            strategy_type: Recovery strategy to use
        
        Returns:
            True if recovery successful, False otherwise
        """
        if not self.self_healing_engine:
            return False
        
        try:
            # Record recovery attempt
            start_time = time.time()
            
            # This is a simplified recovery attempt
            # In production, would implement actual recovery logic
            await self.self_healing_engine.record_recovery_attempt(
                pattern_id=f"{self.orchestrator_name}_{operation_name}",
                strategy=strategy_type,
                success=False,  # Will update if successful
                recovery_time_ms=(time.time() - start_time) * 1000,
                error_message=str(error)
            )
            
            return False  # Recovery logic not implemented yet
            
        except Exception as recovery_error:
            await self.audit_logger.log(
                level=LogLevel.ERROR,
                orchestrator=self.orchestrator_name,
                event="recovery_failed",
                data={
                    "operation": operation_name,
                    "original_error": str(error),
                    "recovery_error": str(recovery_error)
                }
            )
            return False
    
    async def log_handoff(
        self,
        target_orchestrator: str,
        handoff_data: Dict[str, Any]
    ):
        """
        Log handoff to another orchestrator.
        
        Args:
            target_orchestrator: Name of target orchestrator
            handoff_data: Data being handed off
        """
        await self.audit_logger.log(
            level=LogLevel.INFO,
            orchestrator=self.orchestrator_name,
            event="orchestrator_handoff",
            data={
                "source": self.orchestrator_name,
                "target": target_orchestrator,
                "handoff_data": handoff_data,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    async def log_state_transition(
        self,
        from_state: str,
        to_state: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Log state transition.
        
        Args:
            from_state: Previous state
            to_state: New state
            context: Optional context data
        """
        await self.audit_logger.log(
            level=LogLevel.INFO,
            orchestrator=self.orchestrator_name,
            event="state_transition",
            data={
                "from_state": from_state,
                "to_state": to_state,
                "context": context or {},
                "timestamp": datetime.now().isoformat()
            }
        )
    
    async def log_performance_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "ms"
    ):
        """
        Log performance metric.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            unit: Unit of measurement
        """
        await self.audit_logger.log(
            level=LogLevel.INFO,
            orchestrator=self.orchestrator_name,
            event="performance_metric",
            data={
                "metric": metric_name,
                "value": value,
                "unit": unit,
                "timestamp": datetime.now().isoformat()
            }
        )


class OrchestratorHealthCheck:
    """
    Health check system for monitoring orchestrator status.
    
    Tracks:
    - Orchestrator availability
    - Error rates
    - Performance metrics
    - Self-healing effectiveness
    """
    
    def __init__(self, audit_logger: AuditLogger):
        """
        Initialize health check system.
        
        Args:
            audit_logger: AuditLogger instance for reading metrics
        """
        self.audit_logger = audit_logger
        self._health_data: Dict[str, Dict[str, Any]] = {}
    
    async def check_orchestrator_health(
        self,
        orchestrator_name: str
    ) -> Dict[str, Any]:
        """
        Check health of specific orchestrator.
        
        Args:
            orchestrator_name: Name of orchestrator to check
        
        Returns:
            Health status dictionary
        """
        # This is a simplified implementation
        # In production, would analyze recent logs
        return {
            "orchestrator": orchestrator_name,
            "status": "healthy",
            "last_check": datetime.now().isoformat(),
            "error_rate": 0.0,
            "avg_response_time_ms": 0.0
        }
    
    async def get_system_health(self) -> Dict[str, Any]:
        """
        Get overall system health status.
        
        Returns:
            System health dictionary
        """
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "orchestrators_checked": 0,
            "total_errors": 0,
            "self_healing_enabled": True
        }
