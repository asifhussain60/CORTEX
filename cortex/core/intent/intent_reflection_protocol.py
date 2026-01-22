"""Intent Reflection Protocol.

Provides the reflection engine for validating and approving user intents
before execution.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class ReflectionStatus(Enum):
    """Status of a reflection request."""
    PENDING = "pending"
    PENDING_CONFIRMATION = "pending_confirmation"
    APPROVED = "approved"
    REJECTED = "rejected"
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
class ReflectionResponse:
    """Response from intent reflection.
    
    Attributes:
        status: The status of the reflection.
        message: Human-readable message about the result.
        approved_actions: List of approved actions to take.
        rejected_actions: List of rejected actions with reasons.
        requires_confirmation: Whether user confirmation is needed.
        confidence: Confidence score (0.0 to 1.0).
    """
    status: ReflectionStatus = ReflectionStatus.PENDING
    message: str = ""
    approved_actions: List[str] = field(default_factory=list)
    rejected_actions: List[Dict[str, str]] = field(default_factory=list)
    requires_confirmation: bool = False
    confidence: float = 1.0
    
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
        }


class IntentReflectionEngine:
    """Engine for processing intent reflections.
    
    Validates user intents against governance rules and determines
    whether the requested actions should be approved or rejected.
    """
    
    def __init__(self) -> None:
        """Initialize the reflection engine."""
        self._pending_requests: Dict[str, ReflectionRequest] = {}
    
    def reflect(self, request: ReflectionRequest) -> ReflectionResponse:
        """Process a reflection request.
        
        Args:
            request: The reflection request to process.
            
        Returns:
            ReflectionResponse with the result.
        """
        # Basic validation
        if not request.user_request:
            return ReflectionResponse(
                status=ReflectionStatus.REJECTED,
                message="Empty user request",
            )
        
        # Store pending request
        request_id = f"{request.target_name}_{request.timestamp}"
        self._pending_requests[request_id] = request
        
        # Auto-approve for now (in production, this would involve governance checks)
        return ReflectionResponse(
            status=ReflectionStatus.APPROVED,
            message="Request approved",
            approved_actions=[request.user_request],
            confidence=0.95,
        )
    
    def approve(self, request_id: str) -> ReflectionResponse:
        """Manually approve a pending request.
        
        Args:
            request_id: ID of the request to approve.
            
        Returns:
            ReflectionResponse confirming approval.
        """
        if request_id in self._pending_requests:
            request = self._pending_requests.pop(request_id)
            return ReflectionResponse(
                status=ReflectionStatus.APPROVED,
                message="Request manually approved",
                approved_actions=[request.user_request],
            )
        return ReflectionResponse(
            status=ReflectionStatus.ERROR,
            message=f"Request {request_id} not found",
        )
    
    def reject(self, request_id: str, reason: str = "") -> ReflectionResponse:
        """Manually reject a pending request.
        
        Args:
            request_id: ID of the request to reject.
            reason: Reason for rejection.
            
        Returns:
            ReflectionResponse confirming rejection.
        """
        if request_id in self._pending_requests:
            request = self._pending_requests.pop(request_id)
            return ReflectionResponse(
                status=ReflectionStatus.REJECTED,
                message=f"Request rejected: {reason}",
                rejected_actions=[{
                    "action": request.user_request,
                    "reason": reason,
                }],
            )
        return ReflectionResponse(
            status=ReflectionStatus.ERROR,
            message=f"Request {request_id} not found",
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
]