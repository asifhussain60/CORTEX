"""
Review models for post-phase and final implementation review.

Purpose: Data models for ReviewOrchestrator verification workflow
Authority: CORTEX-SELF-IMPROVEMENT-SDLC.yaml Phase 0
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any


class ReviewStatus(str, Enum):
    """Status of a phase review."""
    PASS = "PASS"
    FAIL = "FAIL"
    PENDING = "PENDING"


class ReviewOutcome(str, Enum):
    """Final review outcome classification."""
    PASS = "PASS"
    CONDITIONAL_PASS = "CONDITIONAL_PASS"
    FAIL = "FAIL"


@dataclass
class ReviewIssue:
    """An issue found during review.
    
    Attributes:
        issue_type: Category of issue (TEST_FAILURE, COHERENCE_ISSUE, etc.)
        description: Human-readable description
        severity: HIGH, MEDIUM, LOW
        blocking: Whether this issue blocks progression
    """
    issue_type: str
    description: str
    severity: str
    blocking: bool = False


@dataclass
class PhaseReviewResult:
    """Result of reviewing a completed phase.
    
    Attributes:
        phase_id: Identifier of the reviewed phase
        status: Overall review status (PASS, FAIL, PENDING)
        tests_run: Number of tests executed
        tests_passed: Number of tests that passed
        issues_found: List of issues discovered during review
        review_timestamp: When the review was performed
    """
    phase_id: str
    status: ReviewStatus
    tests_run: int
    tests_passed: int
    issues_found: List[ReviewIssue]
    review_timestamp: datetime


@dataclass
class GateDecision:
    """Decision about whether to proceed to next phase.
    
    Attributes:
        current_phase: The phase just completed
        next_phase: The phase to proceed to (if approved)
        approved: Whether progression is approved
        conditions_met: List of conditions that passed
        conditions_failed: List of conditions that failed
        decision_timestamp: When decision was made
    """
    current_phase: str
    next_phase: str
    approved: bool
    conditions_met: List[str]
    conditions_failed: List[str]
    decision_timestamp: datetime


@dataclass
class Deviation:
    """A deviation from the original plan.
    
    Attributes:
        spec_type: Type of spec that deviated (FileSpec, FunctionSpec, etc.)
        spec_id: Identifier of the spec
        expected: What the plan specified
        actual: What was actually implemented
        impact: Severity of deviation (HIGH, MEDIUM, LOW)
    """
    spec_type: str
    spec_id: str
    expected: str
    actual: str
    impact: str


@dataclass
class PlanFidelityReport:
    """Report measuring how closely implementation followed the plan.
    
    Attributes:
        score: 0-100 fidelity score
        missing_specs: Specs in plan that weren't implemented
        extra_artifacts: Files/functions not in plan
        deviations: List of deviations from spec
    """
    score: int
    missing_specs: List[str]
    extra_artifacts: List[str]
    deviations: List[Deviation] = field(default_factory=list)


@dataclass
class CommitAnalysis:
    """Analysis of git commits for a task.
    
    Attributes:
        total_commits: Number of commits for this task
        commits_with_task_reference: Commits that mention task ID
        atomic_commits: Whether commits are atomic (single purpose)
        commit_sequence_matches_plan: Whether commit order follows plan
        unrelated_changes_detected: Whether unrelated changes found
    """
    total_commits: int
    commits_with_task_reference: int
    atomic_commits: bool
    commit_sequence_matches_plan: bool
    unrelated_changes_detected: bool


@dataclass
class FinalReviewResult:
    """Final review result for a completed implementation.
    
    Attributes:
        task_id: The task being reviewed
        outcome: Final outcome (PASS, CONDITIONAL_PASS, FAIL)
        plan_fidelity: How closely plan was followed
        commit_analysis: Git commit analysis (dict or CommitAnalysis)
        coherence_status: Cross-layer coherence status
        review_duration_seconds: How long review took
        recommendations: Optional list of recommendations
    """
    task_id: str
    outcome: ReviewOutcome
    plan_fidelity: PlanFidelityReport
    commit_analysis: Dict[str, Any]  # Flexible dict for commit data
    coherence_status: str
    review_duration_seconds: float
    recommendations: List[str] = field(default_factory=list)
