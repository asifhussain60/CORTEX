"""
Phase 53 Extended Orchestration - Track 4 Part B.

Extends Phase 53 with context management, state recovery, and orchestrator adaptation.
Builds on Part A orchestrator lifecycle foundation.

AC_START: AC-WAVE7T4-PB-001
Components: Context manager + State recovery + Orchestrator adaptation
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
import time
import json


class ContextType(Enum):
    """Types of execution contexts."""
    LOCAL = "local"
    DISTRIBUTED = "distributed"
    HYBRID = "hybrid"


class StateRecoveryStrategy(Enum):
    """State recovery strategies."""
    CHECKPOINT = "checkpoint"           # Periodic checkpoints
    EVENT_LOG = "event_log"             # Event-based recovery
    SNAPSHOT = "snapshot"               # Full state snapshots
    HYBRID = "hybrid"                   # Combination of above


class AdaptationMode(Enum):
    """Orchestrator adaptation modes."""
    STATIC = "static"                   # No adaptation
    DYNAMIC = "dynamic"                 # Runtime adaptation
    PREDICTIVE = "predictive"           # ML-based prediction
    REACTIVE = "reactive"               # Reactive adjustment


@dataclass
class ExecutionContext:
    """Phase 53 execution context with state."""
    context_id: str
    context_type: ContextType
    current_phase: str
    execution_state: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    active_orchestrators: Set[str] = field(default_factory=set)
    created_at: float = field(default_factory=time.time)
    last_checkpoint: Optional[float] = None
    
    def add_state(self, key: str, value: Any) -> bool:
        """Add state to context."""
        self.execution_state[key] = value
        return True
    
    def get_state(self, key: str) -> Optional[Any]:
        """Get state from context."""
        return self.execution_state.get(key)
    
    def serialize(self) -> str:
        """Serialize context to JSON."""
        return json.dumps({
            "context_id": self.context_id,
            "context_type": self.context_type.value,
            "current_phase": self.current_phase,
            "execution_state": self.execution_state,
            "metadata": self.metadata,
            "active_orchestrators": list(self.active_orchestrators),
        })


@dataclass
class CheckpointData:
    """Checkpoint for state recovery."""
    checkpoint_id: str
    context_snapshot: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    phase: str = ""
    orchestrator_state: Dict[str, Any] = field(default_factory=dict)
    
    def is_valid(self) -> bool:
        """Check if checkpoint is valid."""
        return bool(self.context_snapshot) and self.timestamp > 0


@dataclass
class AdaptationDecision:
    """Decision for orchestrator adaptation."""
    decision_id: str
    current_mode: AdaptationMode
    recommended_mode: AdaptationMode
    confidence: float  # 0.0-1.0
    reasoning: str
    estimated_improvement: float  # percentage
    
    def should_adapt(self) -> bool:
        """Determine if adaptation should occur."""
        return self.confidence > 0.7 and self.estimated_improvement > 10.0


class Phase53ContextManager:
    """Manages Phase 53 execution contexts."""
    
    def __init__(self, context_type: ContextType = ContextType.LOCAL):
        """Initialize context manager."""
        self.context_type = context_type
        self.active_contexts: Dict[str, ExecutionContext] = {}
        self.context_history: List[ExecutionContext] = []

    def create_context(self, context_id: str, initial_phase: str) -> ExecutionContext:
        """Create new execution context."""
        context = ExecutionContext(
            context_id=context_id,
            context_type=self.context_type,
            current_phase=initial_phase
        )
        self.active_contexts[context_id] = context
        return context

    def get_context(self, context_id: str) -> Optional[ExecutionContext]:
        """Get execution context by ID."""
        return self.active_contexts.get(context_id)

    def update_phase(self, context_id: str, new_phase: str) -> bool:
        """Update phase in context."""
        context = self.get_context(context_id)
        if context:
            context.current_phase = new_phase
            return True
        return False

    def add_orchestrator(self, context_id: str, orchestrator_name: str) -> bool:
        """Add active orchestrator to context."""
        context = self.get_context(context_id)
        if context:
            context.active_orchestrators.add(orchestrator_name)
            return True
        return False

    def remove_orchestrator(self, context_id: str, orchestrator_name: str) -> bool:
        """Remove orchestrator from context."""
        context = self.get_context(context_id)
        if context:
            context.active_orchestrators.discard(orchestrator_name)
            return True
        return False

    def close_context(self, context_id: str) -> bool:
        """Close context and archive."""
        context = self.get_context(context_id)
        if context:
            self.context_history.append(context)
            del self.active_contexts[context_id]
            return True
        return False

    def get_context_summary(self, context_id: str) -> Optional[Dict[str, Any]]:
        """Get summary of context."""
        context = self.get_context(context_id)
        if context:
            return {
                "context_id": context.context_id,
                "type": context.context_type.value,
                "phase": context.current_phase,
                "orchestrators_active": len(context.active_orchestrators),
                "state_keys": len(context.execution_state),
                "uptime_seconds": time.time() - context.created_at,
            }
        return None


class Phase53StateRecovery:
    """Manages state recovery for Phase 53."""
    
    def __init__(self, strategy: StateRecoveryStrategy = StateRecoveryStrategy.HYBRID):
        """Initialize state recovery."""
        self.strategy = strategy
        self.checkpoints: Dict[str, CheckpointData] = {}
        self.event_log: List[Dict[str, Any]] = []

    def create_checkpoint(self, context: ExecutionContext, checkpoint_id: str) -> CheckpointData:
        """Create checkpoint from context."""
        checkpoint = CheckpointData(
            checkpoint_id=checkpoint_id,
            context_snapshot=json.loads(context.serialize()),
            phase=context.current_phase,
            orchestrator_state={o: "active" for o in context.active_orchestrators}
        )
        self.checkpoints[checkpoint_id] = checkpoint
        context.last_checkpoint = checkpoint.timestamp
        return checkpoint

    def restore_from_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """Restore state from checkpoint."""
        checkpoint = self.checkpoints.get(checkpoint_id)
        if checkpoint and checkpoint.is_valid():
            return checkpoint.context_snapshot
        return None

    def log_event(self, event_type: str, context_id: str, details: Dict[str, Any]) -> bool:
        """Log recovery event."""
        event = {
            "event_type": event_type,
            "context_id": context_id,
            "timestamp": time.time(),
            "details": details
        }
        self.event_log.append(event)
        return True

    def get_recovery_status(self) -> Dict[str, Any]:
        """Get recovery status."""
        return {
            "strategy": self.strategy.value,
            "checkpoints_total": len(self.checkpoints),
            "checkpoints_valid": sum(1 for c in self.checkpoints.values() if c.is_valid()),
            "events_logged": len(self.event_log),
            "last_checkpoint": max([c.timestamp for c in self.checkpoints.values()]) if self.checkpoints else None,
        }


class Phase53OrchestratorAdapter:
    """Adapts orchestrator behavior at runtime."""
    
    def __init__(self):
        """Initialize adapter."""
        self.adaptation_mode = AdaptationMode.REACTIVE
        self.adaptation_history: List[AdaptationDecision] = []
        self.performance_metrics: Dict[str, float] = {}
        self.performance_baseline: Dict[str, float] = {}

    def analyze_performance(self, metrics: Dict[str, float]) -> Dict[str, float]:
        """Analyze current performance against baseline."""
        if not self.performance_baseline:
            self.performance_baseline = metrics.copy()
            return {}
        
        delta = {}
        for key, current_value in metrics.items():
            baseline_value = self.performance_baseline.get(key, current_value)
            if baseline_value != 0:
                delta[key] = ((current_value - baseline_value) / baseline_value) * 100
            else:
                delta[key] = 0.0
        
        return delta

    def evaluate_adaptation_need(self, metrics: Dict[str, float]) -> AdaptationDecision:
        """Evaluate if adaptation is needed."""
        delta = self.analyze_performance(metrics)
        
        # Calculate confidence based on performance deltas
        negative_deltas = sum(1 for v in delta.values() if v < -5)  # More than 5% degradation
        total_metrics = len(delta) if delta else 1
        confidence = min(0.95, negative_deltas / max(total_metrics, 1))
        
        # Estimate improvement if we adapt
        estimated_improvement = max(0, sum(abs(v) for v in delta.values() if v < 0) / max(len(delta), 1))
        
        recommended_mode = AdaptationMode.DYNAMIC if confidence > 0.7 else AdaptationMode.STATIC
        
        decision = AdaptationDecision(
            decision_id=f"adapt_{int(time.time())}",
            current_mode=self.adaptation_mode,
            recommended_mode=recommended_mode,
            confidence=confidence,
            reasoning=f"Detected {negative_deltas}/{total_metrics} performance degradations",
            estimated_improvement=estimated_improvement
        )
        
        return decision

    def apply_adaptation(self, decision: AdaptationDecision) -> bool:
        """Apply adaptation decision."""
        if decision.should_adapt():
            self.adaptation_mode = decision.recommended_mode
            self.adaptation_history.append(decision)
            return True
        return False

    def get_adaptation_summary(self) -> Dict[str, Any]:
        """Get adaptation summary."""
        successful_adaptations = sum(1 for d in self.adaptation_history if d.should_adapt())
        
        return {
            "current_mode": self.adaptation_mode.value,
            "total_adaptations": len(self.adaptation_history),
            "successful_adaptations": successful_adaptations,
            "average_confidence": (
                sum(d.confidence for d in self.adaptation_history) / len(self.adaptation_history)
                if self.adaptation_history else 0.0
            ),
            "total_estimated_improvement": (
                sum(d.estimated_improvement for d in self.adaptation_history)
            ),
        }


# AC_COMPLETE: AC-WAVE7T4-PB-001 ✅ Context management + state recovery + adaptation framework
