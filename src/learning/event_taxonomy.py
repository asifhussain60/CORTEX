"""
Event Taxonomy for Learning System

Defines 52 event types across 3 tiers:
- Tier 1 (Must-Have): 19 events for MVP
- Tier 2 (Should-Have): 15 events for architectural learning
- Tier 3 (Should-Have): 18 events for system operations

Each event captures a learning milestone with:
- Event type (what happened)
- Component (where it happened)
- Trigger (what caused it)
- Learning value (what can be learned)
- Category (how to organize documentation)

Author: Asif Hussain
Version: 1.0.0 (Phase 1 - 18 must-have events)
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List


class EventTier(Enum):
    """Event priority tiers for phased implementation."""
    MUST_HAVE = "must_have"  # Phase 1-4: Core MVP (18 events)
    SHOULD_HAVE_ARCHITECTURAL = "should_have_arch"  # Phase 5: Architectural (15 events)
    SHOULD_HAVE_OPERATIONAL = "should_have_ops"  # Phase 6: Operations (18 events)


class EventCategory(Enum):
    """Learning categories for documentation organization (15 total)."""
    # Phase 1-4: Must-Have Categories (7)
    CONCEPTS = "concepts"
    PATTERNS = "patterns"
    MILESTONES = "milestones"
    RESOURCES = "resources"
    ADO_WORKFLOWS = "ado_workflows"
    PLANNING_STRATEGIES = "planning_strategies"
    WORKFLOW_CONTEXT = "workflow_context"
    
    # Phase 5-7: Should-Have Categories (8)
    ARCHITECTURAL_PATTERNS = "architectural_patterns"
    CODE_QUALITY = "code_quality"
    DESIGN_DECISIONS = "design_decisions"
    DEBUGGING_PATTERNS = "debugging_patterns"
    PRODUCTIVITY_PATTERNS = "productivity_patterns"
    OPERATIONAL_LEARNINGS = "operational_learnings"
    USER_ONBOARDING = "user_onboarding"
    INTENT_ROUTING = "intent_routing"


class EventType(Enum):
    """
    All 52 learning event types across 3 tiers.
    
    Phase 1-4 implements Tier 1 (19 must-have events).
    Phase 5-7 implements Tiers 2-3 (33 should-have events).
    """
    
    # ==== TIER 1: MUST-HAVE EVENTS (19 events, Phase 1-4) ====
    
    # Planning & Execution (6 events)
    PLAN_CREATED = ("plan_created", EventTier.MUST_HAVE, EventCategory.MILESTONES)
    PLAN_APPROVED = ("plan_approved", EventTier.MUST_HAVE, EventCategory.MILESTONES)
    PLAN_ABANDONED = ("plan_abandoned", EventTier.MUST_HAVE, EventCategory.MILESTONES)
    PHASE_STARTED = ("phase_started", EventTier.MUST_HAVE, EventCategory.MILESTONES)
    PHASE_COMPLETED = ("phase_completed", EventTier.MUST_HAVE, EventCategory.MILESTONES)
    CHECKPOINT_COMMITTED = ("checkpoint_committed", EventTier.MUST_HAVE, EventCategory.MILESTONES)
    
    # ADO Work Management (4 events)
    ADO_STORY_CREATED = ("ado_story_created", EventTier.MUST_HAVE, EventCategory.ADO_WORKFLOWS)
    ADO_FEATURE_CREATED = ("ado_feature_created", EventTier.MUST_HAVE, EventCategory.ADO_WORKFLOWS)
    ADO_WORK_ITEM_COMPLETED = ("ado_work_item_completed", EventTier.MUST_HAVE, EventCategory.ADO_WORKFLOWS)
    ADO_ACCEPTANCE_CRITERIA_VALIDATED = ("ado_acceptance_criteria_validated", EventTier.MUST_HAVE, EventCategory.ADO_WORKFLOWS)
    
    # Workflow Routing (3 events)
    WORKFLOW_STARTED = ("workflow_started", EventTier.MUST_HAVE, EventCategory.WORKFLOW_CONTEXT)
    OPERATION_ROUTED = ("operation_routed", EventTier.MUST_HAVE, EventCategory.WORKFLOW_CONTEXT)
    WORKFLOW_COMPLETED = ("workflow_completed", EventTier.MUST_HAVE, EventCategory.WORKFLOW_CONTEXT)
    
    # Planning Strategy (6 events)
    PLANNING_REQUEST = ("planning_request", EventTier.MUST_HAVE, EventCategory.PLANNING_STRATEGIES)
    PLAN_STRATEGY_SELECTED = ("plan_strategy_selected", EventTier.MUST_HAVE, EventCategory.PLANNING_STRATEGIES)
    PLAN_VALIDATED = ("plan_validated", EventTier.MUST_HAVE, EventCategory.PLANNING_STRATEGIES)
    INTERACTIVE_PLANNING_STARTED = ("interactive_planning_started", EventTier.MUST_HAVE, EventCategory.PLANNING_STRATEGIES)
    CLARIFICATION_REQUESTED = ("clarification_requested", EventTier.MUST_HAVE, EventCategory.PLANNING_STRATEGIES)
    REQUIREMENTS_FINALIZED = ("requirements_finalized", EventTier.MUST_HAVE, EventCategory.PLANNING_STRATEGIES)
    
    # ==== TIER 2: SHOULD-HAVE EVENTS - ARCHITECTURAL (15 events, Phase 5) ====
    
    # Application Health & Architecture (3 events)
    HEALTH_SCAN_STARTED = ("health_scan_started", EventTier.SHOULD_HAVE_ARCHITECTURAL, EventCategory.ARCHITECTURAL_PATTERNS)
    LANGUAGE_ANALYZED = ("language_analyzed", EventTier.SHOULD_HAVE_ARCHITECTURAL, EventCategory.ARCHITECTURAL_PATTERNS)
    ARCHITECTURE_GRAPHED = ("architecture_graphed", EventTier.SHOULD_HAVE_ARCHITECTURAL, EventCategory.ARCHITECTURAL_PATTERNS)
    
    # Code Review & Quality (3 events)
    REVIEW_INITIATED = ("review_initiated", EventTier.SHOULD_HAVE_ARCHITECTURAL, EventCategory.CODE_QUALITY)
    FINDINGS_GENERATED = ("findings_generated", EventTier.SHOULD_HAVE_ARCHITECTURAL, EventCategory.CODE_QUALITY)
    REVIEW_COMPLETED = ("review_completed", EventTier.SHOULD_HAVE_ARCHITECTURAL, EventCategory.CODE_QUALITY)
    
    # Architecture & Design (3 events)
    ARCHITECTURE_ANALYZED = ("architecture_analyzed", EventTier.SHOULD_HAVE_ARCHITECTURAL, EventCategory.DESIGN_DECISIONS)
    DESIGN_DECISION_MADE = ("design_decision_made", EventTier.SHOULD_HAVE_ARCHITECTURAL, EventCategory.DESIGN_DECISIONS)
    ARCHITECTURE_VALIDATED = ("architecture_validated", EventTier.SHOULD_HAVE_ARCHITECTURAL, EventCategory.DESIGN_DECISIONS)
    
    # Governance & Change (2 events)
    CHANGE_PROPOSED = ("change_proposed", EventTier.SHOULD_HAVE_ARCHITECTURAL, EventCategory.DESIGN_DECISIONS)
    GOVERNANCE_CHECK_PASSED = ("governance_check_passed", EventTier.SHOULD_HAVE_ARCHITECTURAL, EventCategory.DESIGN_DECISIONS)
    
    # Error Correction (2 events)
    ERROR_DETECTED = ("error_detected", EventTier.SHOULD_HAVE_ARCHITECTURAL, EventCategory.DEBUGGING_PATTERNS)
    ERROR_RESOLVED = ("error_resolved", EventTier.SHOULD_HAVE_ARCHITECTURAL, EventCategory.DEBUGGING_PATTERNS)
    
    # Test Generation (2 events)
    TESTS_GENERATED = ("tests_generated", EventTier.SHOULD_HAVE_ARCHITECTURAL, EventCategory.CODE_QUALITY)
    TEST_STRATEGY_APPLIED = ("test_strategy_applied", EventTier.SHOULD_HAVE_ARCHITECTURAL, EventCategory.CODE_QUALITY)
    
    # ==== TIER 3: SHOULD-HAVE EVENTS - OPERATIONAL (18 events, Phase 6) ====
    
    # Metrics & Reporting (2 events)
    METRICS_COLLECTED = ("metrics_collected", EventTier.SHOULD_HAVE_OPERATIONAL, EventCategory.PRODUCTIVITY_PATTERNS)
    REPORT_GENERATED = ("report_generated", EventTier.SHOULD_HAVE_OPERATIONAL, EventCategory.PRODUCTIVITY_PATTERNS)
    
    # Git Operations (3 events)
    SYNC_STARTED = ("sync_started", EventTier.SHOULD_HAVE_OPERATIONAL, EventCategory.OPERATIONAL_LEARNINGS)
    CONFLICTS_RESOLVED = ("conflicts_resolved", EventTier.SHOULD_HAVE_OPERATIONAL, EventCategory.OPERATIONAL_LEARNINGS)
    OPTIMIZATION_COMPLETED = ("optimization_completed", EventTier.SHOULD_HAVE_OPERATIONAL, EventCategory.OPERATIONAL_LEARNINGS)
    
    # Onboarding & Demo (4 events)
    ONBOARDING_STARTED = ("onboarding_started", EventTier.SHOULD_HAVE_OPERATIONAL, EventCategory.USER_ONBOARDING)
    RULEBOOK_ACKNOWLEDGED = ("rulebook_acknowledged", EventTier.SHOULD_HAVE_OPERATIONAL, EventCategory.USER_ONBOARDING)
    DEMO_STARTED = ("demo_started", EventTier.SHOULD_HAVE_OPERATIONAL, EventCategory.OPERATIONAL_LEARNINGS)
    DEMO_COMPLETED = ("demo_completed", EventTier.SHOULD_HAVE_OPERATIONAL, EventCategory.OPERATIONAL_LEARNINGS)
    
    # Analytics & Adoption (2 events)
    ANALYTICS_COLLECTED = ("analytics_collected", EventTier.SHOULD_HAVE_OPERATIONAL, EventCategory.PRODUCTIVITY_PATTERNS)
    ADOPTION_METRICS_CALCULATED = ("adoption_metrics_calculated", EventTier.SHOULD_HAVE_OPERATIONAL, EventCategory.PRODUCTIVITY_PATTERNS)
    
    # Code Execution (2 events)
    CODE_EXECUTED = ("code_executed", EventTier.SHOULD_HAVE_OPERATIONAL, EventCategory.OPERATIONAL_LEARNINGS)
    EXECUTION_SUCCEEDED = ("execution_succeeded", EventTier.SHOULD_HAVE_OPERATIONAL, EventCategory.OPERATIONAL_LEARNINGS)
    
    # Intent & Routing (2 events)
    INTENT_CLASSIFIED = ("intent_classified", EventTier.SHOULD_HAVE_OPERATIONAL, EventCategory.INTENT_ROUTING)
    AGENT_SELECTED = ("agent_selected", EventTier.SHOULD_HAVE_OPERATIONAL, EventCategory.INTENT_ROUTING)
    
    # Session Management (1 event)
    SESSION_RESTORED = ("session_restored", EventTier.SHOULD_HAVE_OPERATIONAL, EventCategory.OPERATIONAL_LEARNINGS)
    
    # Vision & Screenshot Analysis (2 events)
    SCREENSHOT_ANALYZED = ("screenshot_analyzed", EventTier.SHOULD_HAVE_OPERATIONAL, EventCategory.PLANNING_STRATEGIES)
    REQUIREMENTS_EXTRACTED = ("requirements_extracted", EventTier.SHOULD_HAVE_OPERATIONAL, EventCategory.PLANNING_STRATEGIES)
    
    def __init__(self, value: str, tier: EventTier, category: EventCategory):
        self._value_ = value
        self.tier = tier
        self.category = category
    
    def is_must_have(self) -> bool:
        """Check if event is in must-have tier (Phase 1-4)."""
        return self.tier == EventTier.MUST_HAVE
    
    def is_should_have(self) -> bool:
        """Check if event is in should-have tiers (Phase 5-7)."""
        return self.tier in (EventTier.SHOULD_HAVE_ARCHITECTURAL, EventTier.SHOULD_HAVE_OPERATIONAL)


@dataclass
class LearningEvent:
    """
    Represents a single learning event captured from an orchestrator or agent.
    
    Attributes:
        event_type: Type of event (from EventType enum)
        component: Source component (e.g., "PlanningOrchestrator")
        metadata: Event-specific data (plan_id, phase, etc.)
        timestamp: When event occurred (auto-set)
        session_id: Optional session identifier
        user_context: Optional user information
    """
    event_type: EventType
    component: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    session_id: Optional[str] = None
    user_context: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for storage."""
        return {
            "event_type": self.event_type.value,
            "component": self.component,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "session_id": self.session_id,
            "user_context": self.user_context,
            "category": self.event_type.category.value,
            "tier": self.event_type.tier.value,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LearningEvent":
        """Reconstruct event from dictionary."""
        # Find EventType by value string
        event_type_value = data["event_type"]
        event_type = next(
            (et for et in EventType if et.value == event_type_value),
            None
        )
        if event_type is None:
            raise ValueError(f"Unknown event type: {event_type_value}")
        
        return cls(
            event_type=event_type,
            component=data["component"],
            metadata=data.get("metadata", {}),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            session_id=data.get("session_id"),
            user_context=data.get("user_context"),
        )
    
    def is_milestone(self) -> bool:
        """
        Determine if this event represents a learning milestone.
        
        Milestones are significant events worth documenting:
        - Plan approved (not plan created)
        - Phase completed (not phase started)
        - Work item completed (not created)
        - Architecture validated (not analyzed)
        
        Returns:
            True if event is a milestone, False otherwise
        """
        milestone_events = {
            EventType.PLAN_APPROVED,
            EventType.PHASE_COMPLETED,
            EventType.CHECKPOINT_COMMITTED,
            EventType.ADO_WORK_ITEM_COMPLETED,
            EventType.ADO_ACCEPTANCE_CRITERIA_VALIDATED,
            EventType.WORKFLOW_COMPLETED,
            EventType.PLAN_VALIDATED,
            EventType.REQUIREMENTS_FINALIZED,
            EventType.ARCHITECTURE_VALIDATED,
            EventType.REVIEW_COMPLETED,
            EventType.ERROR_RESOLVED,
            EventType.GOVERNANCE_CHECK_PASSED,
        }
        return self.event_type in milestone_events


def get_must_have_events() -> List[EventType]:
    """Get list of must-have events for Phase 1-4."""
    return [event for event in EventType if event.is_must_have()]


def get_should_have_events() -> List[EventType]:
    """Get list of should-have events for Phase 5-7."""
    return [event for event in EventType if event.is_should_have()]


def get_events_by_category(category: EventCategory) -> List[EventType]:
    """Get all events for a specific learning category."""
    return [event for event in EventType if event.category == category]


def get_events_by_component(component: str) -> List[EventType]:
    """
    Get likely events for a specific component.
    
    This is a heuristic mapping based on component names.
    Actual event types depend on orchestrator implementation.
    """
    component_mapping = {
        "PlanningOrchestrator": [EventType.PLAN_CREATED, EventType.PLAN_APPROVED, EventType.PLAN_ABANDONED],
        "PlanExecutionOrchestrator": [EventType.PHASE_STARTED, EventType.PHASE_COMPLETED],
        "GitCheckpointOrchestrator": [EventType.CHECKPOINT_COMMITTED],
        "UnifiedEntryPointOrchestrator": [EventType.WORKFLOW_STARTED, EventType.OPERATION_ROUTED, EventType.WORKFLOW_COMPLETED],
        "WorkPlanner": [EventType.PLANNING_REQUEST, EventType.PLAN_STRATEGY_SELECTED, EventType.PLAN_VALIDATED],
        "InteractivePlanner": [EventType.INTERACTIVE_PLANNING_STARTED, EventType.CLARIFICATION_REQUESTED, EventType.REQUIREMENTS_FINALIZED],
        "ADOUtility": [EventType.ADO_STORY_CREATED, EventType.ADO_FEATURE_CREATED, EventType.ADO_WORK_ITEM_COMPLETED, EventType.ADO_ACCEPTANCE_CRITERIA_VALIDATED],
    }
    return component_mapping.get(component, [])
