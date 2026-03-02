"""
ENH-068 Stage 2: Contradiction Resolver
Automated resolution strategies with history tracking and rollback
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid

from cortex.governance.validation.cross_reference_validator import ContradictionReport, ContradictionType


class ResolutionStrategy(Enum):
    """Resolution strategy types"""
    AUTOMATIC = "automatic"
    MANUAL_OVERRIDE = "manual_override"
    CONFIDENCE_BASED = "confidence_based"


class ResolutionStatus(Enum):
    """Resolution status types"""
    RESOLVED = "resolved"
    MANUAL_REVIEW_REQUIRED = "manual_review_required"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"


@dataclass
class Resolution:
    """
    Resolution result for a contradiction

    Attributes:
        resolution_id: Unique resolution identifier
        report: Original contradiction report
        resolution_type: Strategy used for resolution
        status: Resolution status
        changes: Dictionary of changes applied
        confidence: Confidence score (0.0-1.0)
        timestamp: When resolution was created
        rollback_data: Data needed for rollback
    """
    report: ContradictionReport  # Required field
    resolution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    resolution_type: ResolutionStrategy = ResolutionStrategy.AUTOMATIC
    status: ResolutionStatus = ResolutionStatus.RESOLVED
    changes: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    rollback_data: Dict[str, Any] = field(default_factory=dict)


class ContradictionResolver:
    """
    Automated contradiction resolution system

    Features:
    - Multiple resolution strategies
    - Confidence-based decision making
    - Resolution history tracking
    - Rollback capability
    """

    def __init__(self) -> None:
        """Initialize resolver with empty history"""
        self._history: List[Resolution] = []
        self._confidence_threshold = 0.7  # Threshold for auto-resolution

    def resolve(
        self,
        report: ContradictionReport,
        strategy: ResolutionStrategy = ResolutionStrategy.AUTOMATIC,
        manual_changes: Optional[Dict[str, Any]] = None
    ) -> Resolution:
        """
        Resolve a contradiction using specified strategy

        Args:
            report: Contradiction report to resolve
            strategy: Resolution strategy to use
            manual_changes: Manual changes (for MANUAL_OVERRIDE)

        Returns:
            Resolution result
        """
        resolution = Resolution(
            report=report,
            resolution_type=strategy,
            confidence=report.confidence
        )

        if strategy == ResolutionStrategy.MANUAL_OVERRIDE:
            # Manual override - apply provided changes
            if manual_changes:
                resolution.changes = manual_changes
                resolution.status = ResolutionStatus.RESOLVED
                resolution.rollback_data = {"original_changes": manual_changes.copy()}
            else:
                resolution.status = ResolutionStatus.MANUAL_REVIEW_REQUIRED

        elif strategy == ResolutionStrategy.AUTOMATIC:
            # Automatic resolution based on contradiction type
            if report.confidence < self._confidence_threshold:
                # Low confidence - require manual review
                resolution.status = ResolutionStatus.MANUAL_REVIEW_REQUIRED
            else:
                # High confidence - attempt auto-resolution
                resolution = self._auto_resolve(report, resolution)

        elif strategy == ResolutionStrategy.CONFIDENCE_BASED:
            # Confidence-based resolution
            if report.confidence >= self._confidence_threshold:
                resolution = self._auto_resolve(report, resolution)
            else:
                resolution.status = ResolutionStatus.MANUAL_REVIEW_REQUIRED

        # Track in history
        self._history.append(resolution)

        return resolution

    def _auto_resolve(
        self,
        report: ContradictionReport,
        resolution: Resolution
    ) -> Resolution:
        """
        Automatic resolution logic based on contradiction type

        Args:
            report: Contradiction report
            resolution: Resolution object to populate

        Returns:
            Updated resolution
        """
        if report.contradiction_type == ContradictionType.TIMESTAMP:
            # Timestamp contradictions: Update last_updated to completion_date
            resolution.changes = {
                "last_updated": self._extract_date_from_details(report.details, "completion_date")
            }
            resolution.status = ResolutionStatus.RESOLVED
            resolution.rollback_data = {"field": "last_updated", "operation": "update"}

        elif report.contradiction_type == ContradictionType.METRIC:
            # Metric contradictions: More complex, may need manual review
            if "tests_passing" in report.details and "tests_total" in report.details:
                # Try to fix by increasing tests_total
                resolution.changes = {"tests_total": "recalculate"}
                resolution.status = ResolutionStatus.RESOLVED
                resolution.rollback_data = {"field": "tests_total", "operation": "recalculate"}
            else:
                resolution.status = ResolutionStatus.MANUAL_REVIEW_REQUIRED

        elif report.contradiction_type == ContradictionType.STATUS:
            # Status contradictions: Add missing completion_date
            if "no completion_date" in report.details.lower():
                resolution.changes = {
                    "completion_date": datetime.now().strftime("%Y-%m-%d")
                }
                resolution.status = ResolutionStatus.RESOLVED
                resolution.rollback_data = {"field": "completion_date", "operation": "add"}
            else:
                resolution.status = ResolutionStatus.MANUAL_REVIEW_REQUIRED

        elif report.contradiction_type == ContradictionType.DEPENDENCY:
            # Dependency contradictions: Complex, require manual review
            resolution.status = ResolutionStatus.MANUAL_REVIEW_REQUIRED

        return resolution

    def _extract_date_from_details(self, details: str, field_name: str) -> str:
        """
        Extract date value from contradiction details

        Args:
            details: Contradiction details string
            field_name: Field name to extract

        Returns:
            Extracted date string
        """
        # Parse details like "completion_date (2026-02-15) is after last_updated (2026-02-12)"
        import re
        pattern = f"{field_name} \\(([^)]+)\\)"
        match = re.search(pattern, details)
        if match:
            return match.group(1)
        return datetime.now().strftime("%Y-%m-%d")

    def get_history(
        self,
        file_path: Optional[Path] = None,
        contradiction_type: Optional[ContradictionType] = None
    ) -> List[Resolution]:
        """
        Get resolution history with optional filtering

        Args:
            file_path: Filter by file path
            contradiction_type: Filter by contradiction type

        Returns:
            List of resolutions matching filters
        """
        filtered = self._history

        if file_path:
            filtered = [r for r in filtered if r.report.file_path == file_path]

        if contradiction_type:
            filtered = [r for r in filtered if r.report.contradiction_type == contradiction_type]

        return filtered

    def rollback(self, resolution_id: str) -> bool:
        """
        Rollback a resolution by ID

        Args:
            resolution_id: Resolution ID to rollback

        Returns:
            True if rollback succeeded, False otherwise
        """
        # Find resolution in history
        resolution = None
        for r in self._history:
            if r.resolution_id == resolution_id:
                resolution = r
                break

        if not resolution:
            return False

        # Mark as rolled back
        resolution.status = ResolutionStatus.ROLLED_BACK
        resolution.timestamp = datetime.now()

        return True
