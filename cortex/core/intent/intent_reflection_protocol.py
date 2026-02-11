"""Intent Reflection Protocol.

Orchestrates the Master → Interaction delegation pattern for LENS protocol.
Ties together all intelligence sources (AST, git, comments, relationships) and
presents a comprehensive comprehension document to the user for approval.

PHASE-07: Holistic Intent Router Intelligence
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from cortex.brain.core.intent.comprehension_yaml import (
    CanonicalIntentComposer,
    ComprehensionYAML,
)


class ReflectionStatus(Enum):
    """Status of a reflection request."""
    PENDING = "pending"
    PENDING_CONFIRMATION = "pending_confirmation"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_CLARIFICATION = "needs_clarification"
    ERROR = "error"


@dataclass
class ReflectionRequest:
    """Request for intent reflection.

    Attributes:
        user_request: The user's original request text.
        focal_point: The primary file or location of interest.
        target_scope: The scope of the change (file, function, class, etc).
        target_name: Name of the target being modified.
        context: Additional context for the reflection.
        timestamp: ISO timestamp of the request.
    """
    user_request: str
    focal_point: str
    target_scope: str
    target_name: str
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""


@dataclass
class AuditEntry:
    """Audit log entry for tracking intent reflection operations."""

    operation: str
    timestamp: str
    details: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        """Get attribute with dict-like access."""
        if key == "operation":
            return self.operation
        elif key == "timestamp":
            return self.timestamp
        elif key == "details":
            return self.details
        return default

    def __getitem__(self, key: str):
        """Dict-like subscript access."""
        result = self.get(key)
        if result is None:
            raise KeyError(key)
        return result

    def __contains__(self, key: str) -> bool:
        """Dict-like 'in' operator support."""
        return key in ["operation", "timestamp", "details"]

    def __iter__(self):
        """Make iterable over keys."""
        return iter(["operation", "timestamp", "details"])

    def __hash__(self):
        """Make AuditEntry hashable for use in sets/dicts."""
        return hash((self.operation, self.timestamp))


@dataclass
class ReflectionResponse:
    """Response from intent reflection.

    Attributes:
        status: The status of the reflection.
        message: Human-readable message about the result.
        request: Original reflection request
        canonicalized_intent: Canonicalized intent dictionary
        challenges: List of identified challenges
        recommendations: List of recommendations
        comprehension_yaml: YAML string for user approval
        reflected_at: ISO timestamp of reflection completion
        orchestrator_trace: Trace of orchestrator delegation
        focal_point: Focal point from request
        context_sources: Sources of context data
        context_built_at: Timestamp when context was built
        audit_entries: List of audit trail entries
        approved_actions: List of approved actions to take.
        rejected_actions: List of rejected actions with reasons.
        requires_confirmation: Whether user confirmation is needed.
        confidence: Confidence score (0.0 to 1.0).
    """
    status: ReflectionStatus = ReflectionStatus.PENDING
    message: str = ""
    request: Optional[ReflectionRequest] = None
    canonicalized_intent: Optional[Dict[str, Any]] = None
    challenges: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[Dict[str, Any]] = field(default_factory=list)
    comprehension_yaml: str = ""
    reflected_at: Optional[str] = None
    orchestrator_trace: Optional[str] = None
    focal_point: Optional[str] = None
    context_sources: List[str] = field(default_factory=list)
    context_built_at: Optional[str] = None
    audit_entries: List[AuditEntry] = field(default_factory=list)
    approved_actions: List[str] = field(default_factory=list)
    rejected_actions: List[Dict[str, str]] = field(default_factory=list)
    requires_confirmation: bool = False
    confidence: float = 1.0
    ready_for_execution: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "status": self.status.value if isinstance(self.status, Enum) else self.status,
            "message": self.message,
            "approved_actions": self.approved_actions,
            "rejected_actions": self.rejected_actions,
            "requires_confirmation": self.requires_confirmation,
            "confidence": self.confidence,
            "reflected_at": self.reflected_at,
            "focal_point": self.focal_point,
        }


class IntentReflectionEngine:
    """Engine for processing intent reflections.

    Orchestrates Master → Interaction delegation pattern.
    Validates user intents against governance rules.
    """

    def __init__(self) -> None:
        """Initialize the reflection engine."""
        self._pending_requests: Dict[str, ReflectionRequest] = {}
        self._composer = CanonicalIntentComposer()
        self._audit_trail: List[AuditEntry] = []

    def reflect(self, request: ReflectionRequest) -> ReflectionResponse:
        """Process a reflection request.

        Args:
            request: The reflection request to process.

        Raises:
            ValueError: If request validation fails.

        Returns:
            ReflectionResponse with the result.
        """
        # Record reflection start
        start_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        start_audit = AuditEntry(
            operation="REFLECTION_START",
            timestamp=start_time,
            details={"focal_point": request.focal_point}
        )
        audit_entries = [start_audit]

        # Basic validation
        if not request.user_request:
            raise ValueError("Empty user request")

        # Build context (mocked for now - in production would call HolisticContextBuilder)
        context_built_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        context_sources = ["AST", "Git", "Comments", "Relationships"]

        # Canonicalize intent
        canonicalized_intent = {
            "intent_id": f"intent_{request.target_name}_{request.timestamp}",
            "intent_type": "IMPLEMENT",
            "scope": {
                "file": request.focal_point,
                "target": request.target_name,
                "scope_type": request.target_scope,
            },
            "confidence": 0.95,
            "keywords": request.user_request.split(),
            "needs_clarification": False,
        }

        # Generate challenges (mocked - would call ChallengeGenerator)
        challenges = []

        # Generate recommendations (mocked - would call RecommendationEngine)
        recommendations = []

        # Generate comprehension YAML
        yaml_obj = self._composer.compose(
            intent_dict=canonicalized_intent,
            challenges=challenges,
            recommendations=recommendations,
        )
        comprehension_yaml = self._composer.to_yaml_string(yaml_obj)

        # Record reflection complete
        reflected_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        complete_audit = AuditEntry(
            operation="REFLECTION_COMPLETE",
            timestamp=reflected_at,
            details={"status": "PENDING_CONFIRMATION"}
        )
        audit_entries.append(complete_audit)

        # Store pending request
        request_id = f"{request.target_name}_{request.timestamp}"
        self._pending_requests[request_id] = request
        self._audit_trail.extend(audit_entries)

        # Return response pending confirmation
        return ReflectionResponse(
            status=ReflectionStatus.PENDING_CONFIRMATION,
            message="Reflection complete - awaiting user confirmation",
            request=request,
            canonicalized_intent=canonicalized_intent,
            challenges=challenges,
            recommendations=recommendations,
            comprehension_yaml=comprehension_yaml,
            reflected_at=reflected_at,
            orchestrator_trace="MasterOrchestrator → InteractionOrchestrator",
            focal_point=request.focal_point,
            context_sources=context_sources,
            context_built_at=context_built_time,
            audit_entries=audit_entries,
            requires_confirmation=True,
            confidence=0.95,
        )

    def approve(self, response_or_id) -> ReflectionResponse:
        """Manually approve a pending request.

        Args:
            response_or_id: ReflectionResponse object or request ID string.

        Returns:
            ReflectionResponse confirming approval.
        """
        # Support both ReflectionResponse and string ID
        if isinstance(response_or_id, ReflectionResponse):
            request = response_or_id.request
            if not request:
                return ReflectionResponse(
                    status=ReflectionStatus.ERROR,
                    message="No request found in response",
                )
            request_id = f"{request.target_name}_{request.timestamp}"
        else:
            request_id = response_or_id

        if request_id in self._pending_requests:
            request = self._pending_requests.pop(request_id)

            # Record user approval
            approval_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            approval_audit = AuditEntry(
                operation="USER_APPROVAL",
                timestamp=approval_time,
                details={"request_id": request_id}
            )
            self._audit_trail.append(approval_audit)

            return ReflectionResponse(
                status=ReflectionStatus.APPROVED,
                message="Request manually approved",
                approved_actions=[request.user_request],
                request=request,
                reflected_at=approval_time,
                audit_entries=[approval_audit],
                ready_for_execution=True,
            )
        return ReflectionResponse(
            status=ReflectionStatus.ERROR,
            message=f"Request {request_id} not found",
        )

    def reject(self, response_or_id, reason: str = "") -> ReflectionResponse:
        """Manually reject a pending request.

        Args:
            response_or_id: ReflectionResponse object or request ID string.
            reason: Reason for rejection.

        Returns:
            ReflectionResponse confirming rejection.
        """
        # Support both ReflectionResponse and string ID
        if isinstance(response_or_id, ReflectionResponse):
            request = response_or_id.request
            if not request:
                return ReflectionResponse(
                    status=ReflectionStatus.ERROR,
                    message="No request found in response",
                )
            request_id = f"{request.target_name}_{request.timestamp}"
        else:
            request_id = response_or_id

        if request_id in self._pending_requests:
            request = self._pending_requests.pop(request_id)

            # Record user rejection
            rejection_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            rejection_audit = AuditEntry(
                operation="USER_REJECTION",
                timestamp=rejection_time,
                details={"request_id": request_id, "reason": reason}
            )
            self._audit_trail.append(rejection_audit)

            return ReflectionResponse(
                status=ReflectionStatus.REJECTED,
                message=f"Request rejected: {reason}",
                rejected_actions=[{
                    "action": request.user_request,
                    "reason": reason,
                }],
                request=request,
                reflected_at=rejection_time,
                audit_entries=[rejection_audit],
            )
        return ReflectionResponse(
            status=ReflectionStatus.ERROR,
            message=f"Request {request_id} not found",
        )

    def request_clarification(self, response_or_id, question: str) -> ReflectionResponse:
        """Request clarification for a pending request.

        Args:
            response_or_id: ReflectionResponse object or request ID string.
            question: Clarification question to ask user.

        Returns:
            ReflectionResponse with clarification request.
        """
        # Support both ReflectionResponse and string ID
        if isinstance(response_or_id, ReflectionResponse):
            request = response_or_id.request
            if not request:
                return ReflectionResponse(
                    status=ReflectionStatus.ERROR,
                    message="No request found in response",
                )
            request_id = f"{request.target_name}_{request.timestamp}"
        else:
            request_id = response_or_id

        if request_id in self._pending_requests:
            request = self._pending_requests[request_id]

            # Record clarification request
            clarification_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            clarification_audit = AuditEntry(
                operation="CLARIFICATION_REQUESTED",
                timestamp=clarification_time,
                details={"request_id": request_id, "question": question}
            )
            self._audit_trail.append(clarification_audit)

            return ReflectionResponse(
                status=ReflectionStatus.NEEDS_CLARIFICATION,
                message=f"Clarification needed: {question}",
                request=request,
                reflected_at=clarification_time,
                requires_confirmation=True,
                audit_entries=[clarification_audit],
            )
        return ReflectionResponse(
            status=ReflectionStatus.ERROR,
            message=f"Request {request_id} not found",
        )

    def get_audit_trail(self) -> List[AuditEntry]:
        """Get the complete audit trail.

        Returns:
            List of audit entries in chronological order.
        """
        return sorted(self._audit_trail, key=lambda e: e.timestamp)

    def to_yaml(self, response: ReflectionResponse) -> str:
        """Serialize reflection response to YAML.

        Args:
            response: ReflectionResponse to serialize.

        Returns:
            YAML string representation.
        """
        import yaml

        # Convert to serializable dict
        data = {
            "status": response.status.value,
            "message": response.message,
            "reflected_at": response.reflected_at,
            "focal_point": response.focal_point,
            "requires_confirmation": response.requires_confirmation,
            "confidence": response.confidence,
            "ready_for_execution": response.ready_for_execution,
        }

        return yaml.dump(data, default_flow_style=False)

    def from_yaml(self, yaml_string: str) -> ReflectionResponse:
        """Deserialize reflection response from YAML.

        Args:
            yaml_string: YAML string to deserialize.

        Returns:
            ReflectionResponse object.
        """
        import yaml

        data = yaml.safe_load(yaml_string)

        return ReflectionResponse(
            status=ReflectionStatus(data.get("status", "pending")),
            message=data.get("message", ""),
            reflected_at=data.get("reflected_at"),
            focal_point=data.get("focal_point"),
            requires_confirmation=data.get("requires_confirmation", False),
            confidence=data.get("confidence", 1.0),
            ready_for_execution=data.get("ready_for_execution", False),
        )


class IntentReflectionProtocol:
    """Protocol interface for intent reflection.

    Provides a high-level API for intent reflection operations.
    """

    def __init__(self) -> None:
        """Initialize the protocol."""
        self._engine = IntentReflectionEngine()

    def process(self, request: ReflectionRequest) -> ReflectionResponse:
        """Process a reflection request through the protocol.

        Args:
            request: The reflection request to process.

        Returns:
            ReflectionResponse with the result.
        """
        return self._engine.reflect(request)


__all__ = [
    "ReflectionRequest",
    "ReflectionResponse",
    "ReflectionStatus",
    "IntentReflectionEngine",
    "IntentReflectionProtocol",
    "AuditEntry",
]
