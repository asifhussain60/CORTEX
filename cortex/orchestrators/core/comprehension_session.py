"""
ComprehensionSession - Multi-turn conversation state machine.

AC-ID: AC-INTENT-001-01, AC-INTENT-001-02, AC-INTENT-001-03
Phase: REMEDIATION-INTENT-001-COMPREHENSION-SESSION
Purpose: Track comprehension approvals, revisions, and state across turns

Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class ApprovalStatus(Enum):
    """Status of comprehension in approval process."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_CLARIFICATION = "needs_clarification"


class BrainTier(Enum):
    """Target brain tier for comprehension storage."""
    TIER0 = "tier0"
    TIER1 = "tier1"
    TIER2 = "tier2"
    TIER3 = "tier3"


@dataclass
class ComprehensionSession:
    """
    Session tracking for multi-turn comprehension with approval workflows.

    Attributes:
        session_id: Unique session identifier
        created_at: ISO timestamp when session created
        knowledge_graph: Reference to knowledge graph (optional)
        current_comprehension: Latest comprehension state
        approval_status: Current approval state
        revision_count: Number of revisions recorded
        revision_history: List of comprehension revisions
        target_tier: Brain tier for knowledge storage
        temp_files: Temporary files to cleanup
        approval_timestamp: When comprehension was approved
        rejection_reason: Reason for rejection (if any)
    """

    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    knowledge_graph: Optional[Any] = None
    current_comprehension: Optional[Any] = None
    approval_status: ApprovalStatus = ApprovalStatus.PENDING
    revision_count: int = 0
    revision_history: List[Dict[str, Any]] = field(default_factory=list)
    target_tier: Optional[BrainTier] = None
    temp_files: List[str] = field(default_factory=list)
    approval_timestamp: Optional[str] = None
    rejection_reason: Optional[str] = None

    def record_revision(
        self,
        comprehension: Any,
        notes: str = ""
    ) -> None:
        """
        Record a comprehension revision.

        Args:
            comprehension: ComprehensionYAML object to record
            notes: Optional notes about this revision

        Raises:
            ValueError: If comprehension is None
        """
        if comprehension is None:
            raise ValueError("Comprehension cannot be None")

        # Increment revision count
        self.revision_count += 1

        # Store revision in history
        revision_entry: Dict[str, Any] = {
            "revision_number": self.revision_count,
            "timestamp": datetime.now().isoformat(),
            "notes": notes,
            "comprehension": asdict(comprehension) if hasattr(comprehension, '__dataclass_fields__') else comprehension,
        }
        self.revision_history.append(revision_entry)

        # Update current comprehension
        self.current_comprehension = comprehension

    def set_approval_status(
        self,
        status: ApprovalStatus,
        reason: Optional[str] = None
    ) -> None:
        """
        Set approval status with optional reason.

        Args:
            status: New approval status
            reason: Reason for rejection (if applicable)
        """
        self.approval_status = status

        if status == ApprovalStatus.APPROVED:
            self.approval_timestamp = datetime.now().isoformat()
            self.rejection_reason = None
        elif status == ApprovalStatus.REJECTED:
            self.rejection_reason = reason
            self.approval_timestamp = None
        else:
            self.rejection_reason = None
            self.approval_timestamp = None

    def set_target_tier(self, tier: BrainTier) -> None:
        """
        Set target brain tier for knowledge storage.

        Args:
            tier: Target tier (TIER0-TIER3)
        """
        self.target_tier = tier

    def add_temp_file(self, file_path: str) -> None:
        """
        Register a temporary file for cleanup.

        Args:
            file_path: Path to temporary file
        """
        if file_path not in self.temp_files:
            self.temp_files.append(file_path)

    def cleanup_temp_files(self) -> None:
        """
        Delete all registered temporary files.

        Errors are silently ignored (graceful degradation).
        """
        for file_path in self.temp_files:
            try:
                path = Path(file_path)
                if path.exists():
                    path.unlink()
            except (OSError, Exception):
                # Gracefully ignore cleanup errors
                pass

        self.temp_files.clear()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert session to dictionary for YAML serialization.

        Returns:
            Dictionary representation of session
        """
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "approval_status": self.approval_status.value,
            "revision_count": self.revision_count,
            "revision_history": self.revision_history,
            "target_tier": self.target_tier.value if self.target_tier else None,
            "approval_timestamp": self.approval_timestamp,
            "rejection_reason": self.rejection_reason,
        }

    def to_json(self) -> str:
        """
        Convert session to JSON string.

        Returns:
            JSON representation of session
        """
        return json.dumps(self.to_dict(), indent=2)
