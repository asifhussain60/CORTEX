"""Confidence Scoring - Confidence metrics for hallucination detection.

Provides confidence scoring for operations to detect unreliable outputs.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional
import uuid
from typing import Any, Dict, Optional


@dataclass
class ConfidenceScore:
    """Confidence score for an operation.

    Attributes:
        operation_id: Operation identifier.
        overall_score: Overall confidence (0-1).
        input_confidence: Input quality confidence.
        processing_confidence: Processing confidence.
        output_confidence: Output quality confidence.
        factors: Confidence factors.
        timestamp: When score was recorded.
    """

    operation_id: str
    overall_score: float
    input_confidence: float = 0.5
    processing_confidence: float = 0.5
    output_confidence: float = 0.5
    factors: Dict[str, float] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Initialize defaults."""
        if self.factors is None:
            self.factors = {}

    def is_confident(self, threshold: float = 0.8) -> bool:
        """Check if score meets confidence threshold.

        Args:
            threshold: Confidence threshold (0-1).

        Returns:
            True if confident, False otherwise.
        """
        return self.overall_score >= threshold


class ConfidenceScorer:
    """Scores confidence of operations."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        """Initialize scorer.
        
        Args:
            db_path: Optional path to database for persistence.
        """
        self.scores: Dict[str, ConfidenceScore] = {}
        self.db_path = db_path
        self.weights = {
            "input": 0.3,
            "processing": 0.4,
            "output": 0.3,
        }

    def score(
        self,
        operation_id: str,
        input_confidence: float = 0.5,
        processing_confidence: float = 0.5,
        output_confidence: float = 0.5,
        factors: Optional[Dict[str, float]] = None,
    ) -> ConfidenceScore:
        """Score an operation's confidence.

        Args:
            operation_id: Operation ID.
            input_confidence: Input confidence (0-1).
            processing_confidence: Processing confidence (0-1).
            output_confidence: Output confidence (0-1).
            factors: Additional confidence factors.

        Returns:
            ConfidenceScore.
        """
        # Clamp values to 0-1
        input_conf = max(0, min(1, input_confidence))
        proc_conf = max(0, min(1, processing_confidence))
        out_conf = max(0, min(1, output_confidence))

        # Calculate weighted score
        overall = (
            input_conf * self.weights["input"]
            + proc_conf * self.weights["processing"]
            + out_conf * self.weights["output"]
        )

        score = ConfidenceScore(
            operation_id=operation_id,
            overall_score=overall,
            input_confidence=input_conf,
            processing_confidence=proc_conf,
            output_confidence=out_conf,
            factors=factors or {},
        )

        self.scores[operation_id] = score
        return score

    def get_score(self, operation_id: str) -> Optional[ConfidenceScore]:
        """Get confidence score for operation.

        Args:
            operation_id: Operation ID.

        Returns:
            ConfidenceScore or None if not found.
        """
        return self.scores.get(operation_id)

    def get_low_confidence_operations(self, threshold: float = 0.7) -> list:
        """Get operations below confidence threshold.

        Args:
            threshold: Confidence threshold.

        Returns:
            List of low-confidence operation IDs.
        """
        return [
            op_id for op_id, score in self.scores.items()
            if score.overall_score < threshold
        ]

    def average_confidence(self) -> float:
        """Get average confidence across all operations.

        Returns:
            Average confidence score (0-1).
        """
        if not self.scores:
            return 0.0
        total = sum(s.overall_score for s in self.scores.values())
        return total / len(self.scores)

    def clear_scores(self) -> None:
        """Clear all scores."""
        self.scores.clear()

    def calculate_confidence(
        self,
        action: str,
        action_type: str,
        context: Dict = None,
        evidence: Dict = None,
    ) -> "ConfidenceAssessment":
        """Calculate confidence for an action.
        
        Args:
            action: Action being assessed.
            action_type: Type of action.
            context: Context information.
            evidence: Evidence factors.
            
        Returns:
            ConfidenceAssessment.
        """
        if evidence is None:
            evidence = {}
        
        # Calculate weighted confidence from evidence
        score = sum(evidence.values()) / len(evidence) if evidence else 0.5
        
        assessment = ConfidenceAssessment(
            confidence_score=score,
            factors=evidence,
            is_reliable=score >= 0.5,
        )
        
        # Auto-persist
        self.store_assessment(assessment.assessment_id, assessment)
        
        return assessment

    def set_review_threshold(self, threshold: float) -> None:
        """Set review threshold for confidence.
        
        Args:
            threshold: Confidence threshold (0-1).
        """
        self.review_threshold = threshold

    def check_review_triggers(self, assessment: "ConfidenceAssessment") -> list:
        """Check if assessment triggers review.
        
        Args:
            assessment: Confidence assessment.
            
        Returns:
            List of review triggers.
        """
        triggers = []
        threshold = getattr(self, "review_threshold", 0.3)
        
        if assessment.confidence_score < threshold:
            reason = self.get_review_reason(assessment)
            action = self.get_review_action(assessment)
            trigger = ReviewTrigger("low_confidence", reason, action)
            triggers.append(trigger)
        
        # Check for high uncertainty in factors
        if assessment.factors:
            high_uncertainty = sum(1 for f in assessment.factors.values() if f < 0.3)
            if high_uncertainty > 1:  # Multiple low-confidence factors
                triggers.append(ReviewTrigger("high_uncertainty", "Multiple factors below 0.3", "ESCALATE_TO_HUMAN"))
        
        return triggers

    def get_review_reason(self, assessment: "ConfidenceAssessment") -> str:
        """Get reason for review trigger.
        
        Args:
            assessment: Confidence assessment.
            
        Returns:
            Review reason.
        """
        if assessment.confidence_score < 0.3:
            return "Very low confidence score"
        elif assessment.confidence_score < 0.6:
            return "Low confidence score"
        return "Assessment review needed"

    def get_review_action(self, assessment: "ConfidenceAssessment") -> str:
        """Get recommended action for review.
        
        Args:
            assessment: Confidence assessment.
            
        Returns:
            Review action.
        """
        if assessment.confidence_score < 0.2:
            return "ESCALATE_TO_HUMAN"
        elif assessment.confidence_score < 0.5:
            return "REQUIRE_APPROVAL"
        return "MONITOR"

    def get_model_documentation(self) -> Dict:
        """Get documentation for the confidence scoring model.
        
        Returns:
            Model documentation.
        """
        return {
            "model_version": "1.0",
            "model_type": "hybrid",
            "description": "Confidence scoring model based on weighted factors",
            "factors": {
                "intent_clarity": "How clearly the intent is expressed",
                "boundary_compliance": "Compliance with safety boundaries",
                "historical_success": "Success rate in similar contexts",
                "context_alignment": "Alignment with operation context",
                "source_reliability": "Reliability of information sources",
            },
            "weights": self.weights,
            "algorithm": "Weighted average of input, processing, and output confidence",
            "threshold_low": 0.3,
            "threshold_medium": 0.6,
            "threshold_high": 0.8,
            "examples": [
                {
                    "action": "system_modification",
                    "evidence": {"intent_clarity": 0.9, "boundary_compliance": 0.85},
                    "confidence": 0.87,
                    "action": "PROCEED",
                },
                {
                    "action": "data_deletion",
                    "evidence": {"intent_clarity": 0.2, "boundary_compliance": 0.1},
                    "confidence": 0.15,
                    "action": "ESCALATE_TO_HUMAN",
                },
            ],
        }

    def get_assessment(self, assessment_id: str) -> Optional["ConfidenceAssessment"]:
        """Get a stored assessment by ID.
        
        Args:
            assessment_id: Assessment identifier.
            
        Returns:
            Stored assessment or None.
        """
        return getattr(self, "_assessments", {}).get(assessment_id)

    def store_assessment(self, assessment_id: str, assessment: "ConfidenceAssessment") -> None:
        """Store an assessment for later retrieval.
        
        Args:
            assessment_id: Assessment identifier.
            assessment: Assessment to store.
        """
        if not hasattr(self, "_assessments"):
            self._assessments = {}
            self._action_assessments = {}
        self._assessments[assessment_id] = assessment
        
        # Also track by action
        # Try to get action from evidence/context if available
        # For now, use a generic key
        if not hasattr(self, "_action_assessments"):
            self._action_assessments = {}
        if "_default" not in self._action_assessments:
            self._action_assessments["_default"] = []
        self._action_assessments["_default"].append(assessment)

    def get_assessment_history(self, action: str = None) -> list:
        """Get history of all stored assessments.
        
        Args:
            action: Optional action filter.
            
        Returns:
            List of assessments.
        """
        assessments = getattr(self, "_assessments", {})
        return list(assessments.values())

    def compare_assessments(self, assessments: list) -> Dict:
        """Compare multiple assessments.
        
        Args:
            assessments: List of assessments to compare.
            
        Returns:
            Comparison results.
        """
        if len(assessments) < 2:
            return {}
        
        assessment1 = assessments[0]
        assessment2 = assessments[1]
        
        return {
            "score_diff": assessment2.confidence_score - assessment1.confidence_score,
            "score_improvement": assessment2.confidence_score > assessment1.confidence_score,
            "factors_diff": {
                k: assessment2.factors.get(k, 0) - assessment1.factors.get(k, 0)
                for k in set(assessment1.factors.keys()) | set(assessment2.factors.keys())
            },
        }


@dataclass  
class ConfidenceAssessment:
    """Assessment of confidence in a result."""
    confidence_score: float
    factors: Dict[str, float] = field(default_factory=dict)
    is_reliable: bool = True
    assessment_id: str = field(default_factory=lambda: str(uuid.uuid4()))


from enum import Enum

class ScoringFactor(Enum):
    """Factors that influence confidence scoring."""
    CONSISTENCY = "consistency"
    SOURCE_RELIABILITY = "source_reliability"
    CONTEXT_ALIGNMENT = "context_alignment"
    HISTORICAL_ACCURACY = "historical_accuracy"


class ScoringModel(Enum):
    """Scoring models for confidence assessment."""
    RULE_BASED = "rule_based"
    ML_BASED = "ml_based"
    HYBRID = "hybrid"


class ReviewTrigger:
    """Triggers for review based on confidence."""
    
    def __init__(self, trigger_type: str, reason: str = "", recommended_action: str = ""):
        """Initialize review trigger.
        
        Args:
            trigger_type: Type of trigger (low_confidence, high_risk, etc).
            reason: Reason for the trigger.
            recommended_action: Recommended action.
        """
        self.trigger_type = trigger_type
        self.reason = reason
        self.recommended_action = recommended_action
    
    def __repr__(self):
        return f"ReviewTrigger(type={self.trigger_type}, reason={self.reason})"


__all__ = ["ConfidenceScorer", "ConfidenceScore", "ConfidenceAssessment", "ScoringFactor", "ScoringModel", "ReviewTrigger"]
