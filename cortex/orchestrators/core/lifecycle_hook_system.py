"""
Lifecycle Hook System for Automatic Cleanup (ENH-092 | Phase 53.3)

Triggers automatic registry cleanup on wave/phase/session completions.
Eliminates manual vacuum triggering (70% commit overhead reduction).

Architecture:
    EventBus → LifecycleHookSystem → VacuumOrchestrator
    Events: wave_complete, phase_complete, session_end

Integration:
    MasterOrchestrator calls register_completion() on completions
    Hooks trigger asynchronously (non-blocking)

Author: Asif Hussain
Governance: CORE-008 (TDD), CORE-041 (event-driven)
"""

import asyncio
from enum import Enum
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CompletionEvent(Enum):
    """Lifecycle completion events that trigger hooks."""
    
    WAVE_COMPLETE = "wave_complete"
    PHASE_COMPLETE = "phase_complete"
    STAGE_COMPLETE = "stage_complete"
    SESSION_END = "session_end"


@dataclass
class CompletionContext:
    """Context for completion events."""
    
    event_type: CompletionEvent
    entity_id: str  # wave-X, phase-Y, stage-Z, session-UUID
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        return f"{self.event_type.value}:{self.entity_id}"


class LifecycleHookSystem:
    """
    Manages lifecycle hooks for automatic cleanup.
    
    Responsibilities:
        - Register completion events from orchestrators
        - Trigger appropriate cleanup hooks
        - Track hook execution history
        - Provide hook registration API
    
    Usage:
        system = LifecycleHookSystem(vacuum_orchestrator)
        system.register_hook(CompletionEvent.WAVE_COMPLETE, cleanup_fn)
        await system.trigger_completion(CompletionEvent.WAVE_COMPLETE, "wave-12")
    """
    
    def __init__(self, vacuum_orchestrator: Optional[Any] = None):
        """
        Initialize lifecycle hook system.
        
        Args:
            vacuum_orchestrator: Optional VacuumOrchestrator instance for cleanup
        """
        self._hooks: Dict[CompletionEvent, List[Callable]] = {
            event: [] for event in CompletionEvent
        }
        self._execution_history: List[CompletionContext] = []
        self._vacuum_orchestrator = vacuum_orchestrator
        
        # Wire default hooks if vacuum orchestrator provided
        if self._vacuum_orchestrator:
            self._register_default_hooks()
    
    def _register_default_hooks(self) -> None:
        """Register default cleanup hooks for wave/phase/session completions."""
        
        # Wave completion → Full vacuum
        self.register_hook(
            CompletionEvent.WAVE_COMPLETE,
            self._trigger_full_vacuum
        )
        
        # Phase completion → Targeted vacuum
        self.register_hook(
            CompletionEvent.PHASE_COMPLETE,
            self._trigger_phase_vacuum
        )
        
        # Session end → Archive cleanup
        self.register_hook(
            CompletionEvent.SESSION_END,
            self._trigger_session_cleanup
        )
    
    def register_hook(
        self,
        event_type: CompletionEvent,
        hook_fn: Callable[[CompletionContext], Any]
    ) -> None:
        """
        Register hook function for specific event type.
        
        Args:
            event_type: Event to trigger hook on
            hook_fn: Callable to execute (async or sync)
        
        Example:
            system.register_hook(
                CompletionEvent.WAVE_COMPLETE,
                lambda ctx: print(f"Wave {ctx.entity_id} complete!")
            )
        """
        if hook_fn not in self._hooks[event_type]:
            self._hooks[event_type].append(hook_fn)
            logger.info(f"Registered hook for {event_type.value}: {hook_fn.__name__}")
    
    def unregister_hook(
        self,
        event_type: CompletionEvent,
        hook_fn: Callable[[CompletionContext], Any]
    ) -> bool:
        """
        Unregister hook function from event type.
        
        Args:
            event_type: Event type to unregister from
            hook_fn: Callable to remove
        
        Returns:
            True if hook was removed, False if not found
        """
        try:
            self._hooks[event_type].remove(hook_fn)
            logger.info(f"Unregistered hook for {event_type.value}: {hook_fn.__name__}")
            return True
        except ValueError:
            return False
    
    async def trigger_completion(
        self,
        event_type: CompletionEvent,
        entity_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Trigger completion event and execute registered hooks.
        
        Args:
            event_type: Type of completion event
            entity_id: ID of completed entity (wave-12, phase-53, etc.)
            metadata: Optional context data
        
        Returns:
            Dictionary with execution results:
                {
                    "event": "wave_complete",
                    "entity_id": "wave-12",
                    "hooks_executed": 3,
                    "hooks_failed": 0,
                    "duration_ms": 245
                }
        """
        start_time = datetime.now()
        
        context = CompletionContext(
            event_type=event_type,
            entity_id=entity_id,
            metadata=metadata or {}
        )
        
        self._execution_history.append(context)
        
        hooks = self._hooks[event_type]
        logger.info(f"Triggering {len(hooks)} hooks for {context}")
        
        executed = 0
        failed = 0
        
        for hook_fn in hooks:
            try:
                # Handle both async and sync callables
                if asyncio.iscoroutinefunction(hook_fn):
                    await hook_fn(context)
                else:
                    hook_fn(context)
                executed += 1
            except Exception as e:
                logger.error(f"Hook {hook_fn.__name__} failed: {e}")
                failed += 1
        
        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        result = {
            "event": event_type.value,
            "entity_id": entity_id,
            "hooks_executed": executed,
            "hooks_failed": failed,
            "duration_ms": duration_ms
        }
        
        logger.info(f"Completion triggered: {result}")
        return result
    
    def get_execution_history(
        self,
        event_type: Optional[CompletionEvent] = None,
        limit: int = 50
    ) -> List[CompletionContext]:
        """
        Get recent execution history.
        
        Args:
            event_type: Optional filter by event type
            limit: Max number of entries to return
        
        Returns:
            List of CompletionContext entries (most recent first)
        """
        history = self._execution_history
        
        if event_type:
            history = [ctx for ctx in history if ctx.event_type == event_type]
        
        return list(reversed(history[-limit:]))
    
    async def _trigger_full_vacuum(self, context: CompletionContext) -> None:
        """Execute full registry vacuum on wave completion."""
        if not self._vacuum_orchestrator:
            logger.warning("VacuumOrchestrator not configured, skipping vacuum")
            return
        
        logger.info(f"Triggering full vacuum for {context.entity_id}")
        
        # Call vacuum with mode=AUTO (skip confirmation)
        result = await self._vacuum_orchestrator.execute_vacuum(
            mode="AUTO",
            trigger_source=f"lifecycle_hook:{context.entity_id}"
        )
        
        logger.info(f"Vacuum result: {result}")
    
    async def _trigger_phase_vacuum(self, context: CompletionContext) -> None:
        """Execute targeted vacuum on phase completion."""
        if not self._vacuum_orchestrator:
            return
        
        logger.info(f"Triggering phase vacuum for {context.entity_id}")
        
        # Targeted cleanup: Only phase-specific artifacts
        result = await self._vacuum_orchestrator.execute_vacuum(
            mode="TARGETED",
            scope=context.entity_id,
            trigger_source=f"lifecycle_hook:{context.entity_id}"
        )
        
        logger.info(f"Phase vacuum result: {result}")
    
    async def _trigger_session_cleanup(self, context: CompletionContext) -> None:
        """Archive session artifacts on session end."""
        if not self._vacuum_orchestrator:
            return
        
        logger.info(f"Triggering session cleanup for {context.entity_id}")
        
        # Session cleanup: Archive conversation logs, temp files
        result = await self._vacuum_orchestrator.archive_session(
            session_id=context.entity_id,
            trigger_source="lifecycle_hook:session_end"
        )
        
        logger.info(f"Session cleanup result: {result}")
