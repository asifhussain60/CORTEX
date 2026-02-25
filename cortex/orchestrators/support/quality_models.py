"""
Shared data models for quality assurance orchestrator.

Consolidates data structures for:
- Recommendation gating (safety checks, rejection history)
- Challenge generation (disagreement detection)
- Meta-audit validation (holistic gates)

CORTEX COMPLIANCE: CORE-011 (type hints), CORE-012 (docstrings)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime


class GateType(Enum):
    """Types of validation gates for quality assurance."""

    REJECTION_HISTORY = "rejection_history"
    REGRESSION_RISK = "regression_risk"
    TEST_HEALTH = "test_health"
    DUPLICATION = "duplication"
    PERFORMANCE = "performance"
    SECURITY = "security"


class RiskLevel(Enum):
    """Risk levels for quality assessment."""

    SAFE = "safe"
    WARNING = "warning"
    CRITICAL = "critical"


class ChallengeType(Enum):
    """Types of challenges generated for disagreement detection."""

    ASSUMPTION = "assumption"
    EDGE_CASE = "edge_case"
    PERFORMANCE = "performance"
    SECURITY = "security"
    BUSINESS_LOGIC = "business_logic"


@dataclass
class RejectionEntry:
    """Historical rejection entry for recommendation safety."""

    rejection_id: str
    """Unique rejection identifier (REJ-* pattern)."""

    timestamp: datetime
    """When rejection occurred."""

    reason: str
    """Reason for rejection."""

    similarity_score: float
    """Similarity to current recommendation (0-1.0)."""

    recommendation_type: str
    """Type of rejected recommendation."""


@dataclass
class GateResult:
    """Result of a single validation gate check."""

    gate_type: GateType
    """Type of gate checked."""

    status: RiskLevel
    """Result status (SAFE, WARNING, CRITICAL)."""

    score: float
    """Numerical score (0-1.0)."""

    message: str
    """Human-readable result message."""

    details: Dict[str, Any] = field(default_factory=dict)
    """Additional details for debugging."""


@dataclass
class RecommendationSafetyResult:
    """Complete safety check result for recommendation gating."""

    is_safe: bool
    """Whether recommendation is safe to emit."""

    gates: List[GateResult]
    """Results from all validation gates."""

    verdict: str
    """Overall verdict: SAFE_TO_RECOMMEND | BLOCKED."""

    blocking_gates: List[GateType] = field(default_factory=list)
    """Which gates caused blocking (if any)."""

    rejection_match: Optional[RejectionEntry] = None
    """Matching rejection entry (if found)."""


@dataclass
class Challenge:
    """Generated challenge for user request disagreement detection."""

    challenge_type: ChallengeType
    """Type of challenge."""

    question: str
    """Challenge question to user."""

    context: str
    """Context for the challenge."""

    severity: RiskLevel
    """Severity level (WARNING, CRITICAL)."""

    suggested_action: str
    """Suggested action if challenge accepted."""

    alternatives: List[str] = field(default_factory=list)
    """Alternative approaches for consideration."""


@dataclass
class MetaAuditResult:
    """Result of holistic meta-audit validation."""

    audit_id: str
    """Unique audit identifier."""

    timestamp: datetime
    """When audit was performed."""

    is_valid: bool
    """Whether audit passed."""

    checks_performed: List[str]
    """List of checks executed."""

    violations: List[str] = field(default_factory=list)
    """Any violations detected."""

    recommendations: List[str] = field(default_factory=list)
    """Recommendations for improvement."""

    coverage_score: float = 0.0
    """Coverage percentage (0-100)."""


@dataclass
class QualityAssuranceReport:
    """Comprehensive quality assurance report."""

    report_id: str
    """Unique report identifier."""

    timestamp: datetime
    """When report was generated."""

    safety_result: RecommendationSafetyResult
    """Recommendation safety check results."""

    challenges: List[Challenge]
    """Generated challenges (if any)."""

    meta_audit_result: MetaAuditResult
    """Holistic meta-audit results."""

    overall_verdict: str
    """Overall quality verdict."""

    is_approved: bool = False
    """Whether quality assurance approved."""
