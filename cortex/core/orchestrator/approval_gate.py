"""Approval Gate - Gate for approval workflows.

Manages approval gates in processing pipelines.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional, List
from enum import Enum


class ApprovalStatus(Enum):
    """Approval statuses."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CONDITIONAL = "conditional"
    ESCALATED = "escalated"


@dataclass
class ApprovalRequest:
    """Approval request.

    Attributes:
        request_id: Unique request identifier.
        content: Content for approval.
        requestor: Who requested approval.
        deadline: Deadline for approval.
        metadata: Additional metadata.
    """

    request_id: str
    content: Dict[str, Any]
    requestor: str
    deadline: str = ""
    metadata: Dict[str, Any] = None

    def __post_init__(self) -> None:
        """Initialize defaults."""
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ApprovalDecision:
    """Approval decision.

    Attributes:
        decision_id: Unique decision identifier.
        request_id: Associated request ID.
        status: Approval status.
        approver: Who approved/rejected.
        reason: Decision reason.
        conditions: Optional conditions for conditional approval.
    """

    decision_id: str
    request_id: str
    status: ApprovalStatus
    approver: str
    reason: str = ""
    conditions: List[str] = None

    def __post_init__(self) -> None:
        """Initialize defaults."""
        if self.conditions is None:
            self.conditions = []


class ApprovalGate:
    """Manages approval workflows."""

    def __init__(self) -> None:
        """Initialize approval gate."""
        self.requests: Dict[str, ApprovalRequest] = {}
        self.decisions: Dict[str, ApprovalDecision] = {}

    def create_request(
        self,
        request_id: str,
        content: Dict[str, Any],
        requestor: str,
        deadline: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ApprovalRequest:
        """Create an approval request.

        Args:
            request_id: Request ID.
            content: Content for approval.
            requestor: Requestor name.
            deadline: Optional deadline.
            metadata: Optional metadata.

        Returns:
            ApprovalRequest.
        """
        request = ApprovalRequest(
            request_id=request_id,
            content=content,
            requestor=requestor,
            deadline=deadline,
            metadata=metadata or {},
        )
        self.requests[request_id] = request
        return request

    def approve(
        self,
        decision_id: str,
        request_id: str,
        approver: str,
        reason: str = "",
        conditions: Optional[List[str]] = None,
    ) -> ApprovalDecision:
        """Approve a request.

        Args:
            decision_id: Decision ID.
            request_id: Request ID.
            approver: Approver name.
            reason: Approval reason.
            conditions: Optional conditions.

        Returns:
            ApprovalDecision.
        """
        decision = ApprovalDecision(
            decision_id=decision_id,
            request_id=request_id,
            status=ApprovalStatus.APPROVED,
            approver=approver,
            reason=reason,
            conditions=conditions or [],
        )
        self.decisions[decision_id] = decision
        return decision

    def reject(
        self, decision_id: str, request_id: str, approver: str, reason: str = ""
    ) -> ApprovalDecision:
        """Reject a request.

        Args:
            decision_id: Decision ID.
            request_id: Request ID.
            approver: Approver name.
            reason: Rejection reason.

        Returns:
            ApprovalDecision.
        """
        decision = ApprovalDecision(
            decision_id=decision_id,
            request_id=request_id,
            status=ApprovalStatus.REJECTED,
            approver=approver,
            reason=reason,
        )
        self.decisions[decision_id] = decision
        return decision

    def get_pending_requests(self) -> List[ApprovalRequest]:
        """Get pending approval requests.

        Returns:
            List of ApprovalRequest.
        """
        pending_ids = set(self.requests.keys())
        for decision in self.decisions.values():
            if decision.request_id in pending_ids:
                pending_ids.discard(decision.request_id)
        return [self.requests[rid] for rid in pending_ids]


__all__ = [
    "ApprovalGate",
    "ApprovalRequest",
    "ApprovalDecision",
    "ApprovalStatus",
]
