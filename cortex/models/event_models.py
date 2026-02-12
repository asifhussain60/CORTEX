"""
Event models for orchestrator event-driven communication.

Purpose: Data models for OrchestratorEventBus pub/sub messaging
Authority: CORTEX-SELF-IMPROVEMENT-SDLC.yaml Phase 0
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


class EventType(str, Enum):
    """Types of events in orchestrator communication.

    These events enable decoupled communication between orchestrators
    without direct imports or function calls.
    """
    REQUEST_RECEIVED = "REQUEST_RECEIVED"
    INTENT_CLASSIFIED = "INTENT_CLASSIFIED"
    PLANNING_REQUIRED = "PLANNING_REQUIRED"
    PLAN_GENERATED = "PLAN_GENERATED"
    PLAN_APPROVED = "PLAN_APPROVED"
    PHASE_STARTED = "PHASE_STARTED"
    PHASE_COMPLETE = "PHASE_COMPLETE"
    PHASE_REVIEW_COMPLETE = "PHASE_REVIEW_COMPLETE"
    IMPLEMENTATION_COMPLETE = "IMPLEMENTATION_COMPLETE"
    FINAL_REVIEW_COMPLETE = "FINAL_REVIEW_COMPLETE"
    GATE_DECISION_MADE = "GATE_DECISION_MADE"
    ERROR_OCCURRED = "ERROR_OCCURRED"
    # Phase 45: Plan-specific events (Phase 45 § Stage 2)
    PLAN_INTENT_DETECTED = "PLAN_INTENT_DETECTED"
    PLAN_CREATED = "PLAN_CREATED"
    PLAN_ENRICHED = "PLAN_ENRICHED"
    PLAN_STATE_CHANGED = "PLAN_STATE_CHANGED"
    PLAN_ARCHIVED = "PLAN_ARCHIVED"


@dataclass
class OrchestratorEvent:
    """An event in the orchestrator communication mesh.

    Attributes:
        event_type: Type of event (from EventType enum)
        source_orchestrator: Orchestrator that emitted the event
        payload: Event-specific data dictionary
        target_orchestrator: Optional specific target (broadcast if None)
        correlation_id: ID linking related events in a chain
        event_id: Unique identifier for this event instance
        timestamp: When the event was created
    """
    event_type: EventType
    source_orchestrator: str
    payload: Dict[str, Any]
    target_orchestrator: Optional[str] = None
    correlation_id: Optional[str] = None
    event_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class EventChain:
    """A chain of related events linked by correlation_id.

    Enables tracking the full lifecycle of a task across orchestrators.

    Attributes:
        correlation_id: Shared ID for all events in chain
        event_ids: Ordered list of event IDs in the chain
        started_at: When the chain began
        completed: Whether the chain has finished
        completed_at: When the chain completed (if applicable)
    """
    correlation_id: str
    event_ids: List[str]
    started_at: datetime
    completed: bool = False
    completed_at: Optional[datetime] = None


@dataclass
class EventSubscription:
    """A subscription to orchestrator events.

    Orchestrators register subscriptions to receive specific event types.

    Attributes:
        subscriber_id: ID of the subscribing orchestrator
        event_types: List of event types to subscribe to
        filter_source: Optional source filter (receive from specific source only)
    """
    subscriber_id: str
    event_types: List[EventType]
    filter_source: Optional[str] = None


# ============================================================================
# Common Event Payloads (typed structures for specific events)
# ============================================================================


@dataclass
class IntentClassifiedPayload:
    """Payload for INTENT_CLASSIFIED events.

    Emitted by IntentRouter when user intent is classified.

    Attributes:
        intent: Classified intent type (IMPLEMENT, FIX, REFACTOR, etc.)
        confidence: Classification confidence (0.0-1.0)
        complexity: Complexity classification (TRIVIAL, SIMPLE, MODERATE, COMPLEX, CRITICAL)
        suggested_orchestrator: Recommended orchestrator to handle request
    """
    intent: str
    confidence: float
    complexity: str
    suggested_orchestrator: str


@dataclass
class PhaseCompletePayload:
    """Payload for PHASE_COMPLETE events.

    Emitted by WorkflowOrchestrator when a phase finishes.

    Attributes:
        phase_id: Identifier of the completed phase
        success: Whether phase completed successfully
        artifacts_created: List of files/resources created
        duration_seconds: How long the phase took
    """
    phase_id: str
    success: bool
    artifacts_created: List[str]
    duration_seconds: float


# ============================================================================
# Plan-Specific Event Payloads (Phase 45 § Stage 2)
# ============================================================================


@dataclass
class PlanEventPayload:
    """Payload for plan-related events.

    Common structure for all plan events with plan context.

    Attributes:
        plan_id: Unique plan identifier
        plan_spec: Full plan specification (when applicable)
        changes: Dict describing what changed (for state changes)
        metadata: Additional context (timestamps, user info, etc.)
    """
    plan_id: str
    plan_spec: Optional[Dict[str, Any]] = None
    changes: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class PlanIntentDetectedPayload:
    """Payload for PLAN_INTENT_DETECTED events.

    Emitted by InteractionOrchestrator when plan intent is detected.

    Attributes:
        plan_id: Plan identifier (if creating from existing)
        user_context: The user's original request/context
        detected_type: Type of plan intent (IMPLEMENT, FIX, REFACTOR, etc.)
        confidence: Confidence in plan intent detection (0.0-1.0)
    """
    plan_id: Optional[str] = None
    user_context: str = ""
    detected_type: str = ""
    confidence: float = 0.0


@dataclass
class PlanCreatedPayload:
    """Payload for PLAN_CREATED events.

    Emitted by PlanOrchestrator when a plan is created.

    Attributes:
        plan_id: Unique plan identifier
        title: Plan title
        status: Initial plan status
        created_at: Timestamp of creation
    """
    plan_id: str
    title: str
    status: str = "pending"
    created_at: Optional[datetime] = None


@dataclass
class PlanEnrichedPayload:
    """Payload for PLAN_ENRICHED events.

    Emitted by EnhancedPlanningOrchestrator after enrichment.

    Attributes:
        plan_id: Plan identifier
        enrichment_sources: List of enrichers that ran
        enrichment_data: Merged enrichment results
        quality_score: DoR quality score post-enrichment (0.0-1.0)
    """
    plan_id: str
    enrichment_sources: List[str] = field(default_factory=list)
    enrichment_data: Dict[str, Any] = field(default_factory=dict)
    quality_score: float = 0.0


@dataclass
class PlanStateChangedPayload:
    """Payload for PLAN_STATE_CHANGED events.

    Emitted when plan transitions between lifecycle states.

    Attributes:
        plan_id: Plan identifier
        old_status: Previous status
        new_status: Current status
        reason: Why the state changed
        changed_at: Timestamp of change
    """
    plan_id: str
    old_status: str
    new_status: str
    reason: str = ""
    changed_at: Optional[datetime] = None


@dataclass
class PlanArchivedPayload:
    """Payload for PLAN_ARCHIVED events.

    Emitted when plan is archived (moved to completed/).

    Attributes:
        plan_id: Plan identifier
        archive_path: Path where plan was archived
        completion_status: Final status (completed, cancelled, deferred)
        archived_at: Timestamp of archival
    """
    plan_id: str
    archive_path: str
    completion_status: str
    archived_at: Optional[datetime] = None
