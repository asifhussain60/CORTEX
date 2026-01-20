"""
Agent Confidence Scoring module for HP-003-02.

Scores agent confidence in proposed actions with:
- Multi-factor confidence calculation
- Automatic review trigger for low confidence
- Comprehensive model documentation
- Assessment history and comparison

Part of PHASE-11-HALLUCINATION-PREVENTION.
"""

import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import threading


class ScoringFactor(Enum):
    """Factors contributing to confidence score."""
    
    INTENT_CLARITY = "INTENT_CLARITY"
    """How clear the intent behind the action is."""
    
    BOUNDARY_COMPLIANCE = "BOUNDARY_COMPLIANCE"
    """How well the action complies with behavioral boundaries."""
    
    HISTORICAL_SUCCESS = "HISTORICAL_SUCCESS"
    """Historical success rate for similar actions."""
    
    MODEL_UNCERTAINTY = "MODEL_UNCERTAINTY"
    """Model's uncertainty about the action."""
    
    PRECEDENT_MATCHING = "PRECEDENT_MATCHING"
    """How closely this matches known precedents."""


@dataclass
class ReviewTrigger:
    """Represents a condition triggering review."""
    
    trigger_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    """Unique trigger identifier."""
    
    trigger_type: str = ""
    """Type of trigger (e.g., LOW_CONFIDENCE, UNCERTAIN_BOUNDARY)."""
    
    reason: str = ""
    """Human-readable reason for review trigger."""
    
    recommended_action: str = ""
    """Recommended action to take."""
    
    severity: str = "MEDIUM"
    """Severity level (LOW, MEDIUM, HIGH, CRITICAL)."""
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    """When trigger was created."""


@dataclass
class ConfidenceAssessment:
    """Represents a confidence score assessment."""
    
    assessment_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    """Unique assessment identifier."""
    
    timestamp: datetime = field(default_factory=datetime.utcnow)
    """When assessment was made."""
    
    action: str = ""
    """Action being assessed."""
    
    action_type: str = ""
    """Type/category of action."""
    
    confidence_score: float = 0.0
    """Calculated confidence score (0.0-1.0)."""
    
    factors: Dict[str, float] = field(default_factory=dict)
    """Individual factor scores."""
    
    context: Optional[Dict[str, Any]] = None
    """Context information."""
    
    evidence: Optional[Dict[str, float]] = None
    """Evidence used for calculation."""
    
    requires_review: bool = False
    """Whether review is required."""
    
    review_triggers: List[ReviewTrigger] = field(default_factory=list)
    """Triggers for review."""


@dataclass
class ScoringModel:
    """Documents the scoring model."""
    
    model_version: str = "1.0"
    """Model version."""
    
    factors: Dict[str, str] = field(default_factory=dict)
    """Factor descriptions."""
    
    weights: Dict[str, float] = field(default_factory=dict)
    """Factor weights in scoring."""
    
    algorithm: str = ""
    """Description of scoring algorithm."""
    
    review_threshold: float = 0.5
    """Confidence threshold that triggers review."""
    
    examples: List[Dict[str, Any]] = field(default_factory=list)
    """Example assessments."""


class ConfidenceScorer:
    """
    Scores agent confidence in proposed actions.
    
    Provides:
    - Multi-factor confidence calculation
    - Automatic review triggering for low confidence
    - Comprehensive model documentation
    - Assessment persistence and history
    - Comparison and analysis capabilities
    """
    
    def __init__(self, db_path: str = ":memory:", review_threshold: float = 0.5):
        """
        Initialize confidence scorer.
        
        Args:
            db_path: Path to SQLite database.
            review_threshold: Score threshold for triggering review.
        """
        self.db_path = db_path
        self.review_threshold = review_threshold
        self._lock = threading.RLock()
        self._initialize_database()
        self._model = self._initialize_model()
    
    def _initialize_database(self) -> None:
        """Initialize database schema for assessments."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Assessments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS confidence_assessments (
                assessment_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                action TEXT NOT NULL,
                action_type TEXT NOT NULL,
                confidence_score REAL NOT NULL,
                factors TEXT NOT NULL,
                context TEXT,
                evidence TEXT,
                requires_review INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Review triggers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS review_triggers (
                trigger_id TEXT PRIMARY KEY,
                assessment_id TEXT NOT NULL,
                trigger_type TEXT NOT NULL,
                reason TEXT NOT NULL,
                recommended_action TEXT,
                severity TEXT,
                created_at TEXT,
                FOREIGN KEY (assessment_id) REFERENCES confidence_assessments(assessment_id)
            )
        """)
        
        # Indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_assessment_action 
            ON confidence_assessments(action)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_assessment_timestamp 
            ON confidence_assessments(timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_assessment_score 
            ON confidence_assessments(confidence_score)
        """)
        
        conn.commit()
        conn.close()
    
    def _initialize_model(self) -> ScoringModel:
        """Initialize the scoring model with factors and weights."""
        model = ScoringModel(
            model_version="1.0",
            factors={
                "INTENT_CLARITY": "Clarity of the agent's intent behind the action",
                "BOUNDARY_COMPLIANCE": "Compliance with behavioral boundaries",
                "HISTORICAL_SUCCESS": "Historical success rate for similar actions",
                "MODEL_UNCERTAINTY": "Model's uncertainty about correctness",
                "PRECEDENT_MATCHING": "Similarity to known successful precedents",
            },
            weights={
                "INTENT_CLARITY": 0.30,
                "BOUNDARY_COMPLIANCE": 0.30,
                "HISTORICAL_SUCCESS": 0.20,
                "MODEL_UNCERTAINTY": 0.10,
                "PRECEDENT_MATCHING": 0.10,
            },
            algorithm="Weighted average with uncertainty attenuation. Formula: score = sum(factor_value * weight) - (model_uncertainty * 0.2)",
            review_threshold=self.review_threshold,
            examples=[
                {
                    "action": "database_read",
                    "factors": {
                        "INTENT_CLARITY": 0.95,
                        "BOUNDARY_COMPLIANCE": 0.95,
                        "HISTORICAL_SUCCESS": 0.90,
                        "MODEL_UNCERTAINTY": 0.05,
                        "PRECEDENT_MATCHING": 0.95,
                    },
                    "confidence_score": 0.92,
                    "requires_review": False,
                },
                {
                    "action": "system_modification",
                    "factors": {
                        "INTENT_CLARITY": 0.30,
                        "BOUNDARY_COMPLIANCE": 0.25,
                        "HISTORICAL_SUCCESS": 0.10,
                        "MODEL_UNCERTAINTY": 0.80,
                        "PRECEDENT_MATCHING": 0.20,
                    },
                    "confidence_score": 0.25,
                    "requires_review": True,
                },
            ],
        )
        return model
    
    def calculate_confidence(
        self,
        action: str,
        action_type: str,
        context: Optional[Dict[str, Any]] = None,
        evidence: Optional[Dict[str, float]] = None,
    ) -> ConfidenceAssessment:
        """
        Calculate confidence score for an action.
        
        Args:
            action: Action being assessed.
            action_type: Type/category of action.
            context: Optional context information.
            evidence: Evidence values for factors.
        
        Returns:
            ConfidenceAssessment with calculated score.
        
        Raises:
            TypeError: If arguments have invalid types.
            ValueError: If required fields are missing.
        """
        if not isinstance(action, str) or not action:
            raise TypeError("action must be non-empty string")
        if not isinstance(action_type, str) or not action_type:
            raise TypeError("action_type must be non-empty string")
        
        evidence = evidence or {}
        context = context or {}
        
        with self._lock:
            # Calculate factor scores
            factors = self._calculate_factors(evidence)
            
            # Calculate weighted score
            confidence_score = self._calculate_weighted_score(factors)
            
            # Create assessment
            assessment = ConfidenceAssessment(
                action=action,
                action_type=action_type,
                confidence_score=confidence_score,
                factors=factors,
                context=context,
                evidence=evidence,
            )
            
            # Check for review triggers
            triggers = self.check_review_triggers(assessment)
            assessment.requires_review = len(triggers) > 0
            assessment.review_triggers = triggers
            
            # Persist to database
            self._persist_assessment(assessment)
            
            return assessment
    
    def _calculate_factors(self, evidence: Dict[str, float]) -> Dict[str, float]:
        """Calculate individual factor scores."""
        factors = {}
        
        # Map evidence to factors
        factor_map = {
            "intent_clarity": "INTENT_CLARITY",
            "boundary_compliance": "BOUNDARY_COMPLIANCE",
            "historical_success": "HISTORICAL_SUCCESS",
            "model_uncertainty": "MODEL_UNCERTAINTY",
            "precedent_matching": "PRECEDENT_MATCHING",
        }
        
        for evidence_key, factor_name in factor_map.items():
            value = evidence.get(evidence_key, 0.5)
            # Normalize to 0.0-1.0
            value = max(0.0, min(1.0, value))
            factors[factor_name] = value
        
        return factors
    
    def _calculate_weighted_score(self, factors: Dict[str, float]) -> float:
        """Calculate weighted confidence score."""
        score = 0.0
        
        for factor_name, weight in self._model.weights.items():
            factor_value = factors.get(factor_name, 0.5)
            score += factor_value * weight
        
        # Attenuate for uncertainty
        uncertainty = factors.get("MODEL_UNCERTAINTY", 0.0)
        score = score - (uncertainty * 0.2)
        
        # Clamp to 0.0-1.0
        score = max(0.0, min(1.0, score))
        
        return score
    
    def check_review_triggers(
        self,
        assessment: ConfidenceAssessment,
    ) -> List[ReviewTrigger]:
        """
        Check for conditions that trigger review.
        
        Args:
            assessment: Assessment to check.
        
        Returns:
            List of ReviewTrigger objects.
        """
        triggers = []
        
        # Trigger 1: Low confidence score
        if assessment.confidence_score < self.review_threshold:
            triggers.append(ReviewTrigger(
                trigger_type="LOW_CONFIDENCE",
                reason=f"Confidence score {assessment.confidence_score:.2f} below threshold {self.review_threshold}",
                recommended_action="HUMAN_REVIEW_REQUIRED",
                severity="HIGH" if assessment.confidence_score < 0.3 else "MEDIUM",
            ))
        
        # Trigger 2: High uncertainty
        if assessment.factors.get("MODEL_UNCERTAINTY", 0.0) > 0.6:
            triggers.append(ReviewTrigger(
                trigger_type="HIGH_UNCERTAINTY",
                reason=f"Model uncertainty {assessment.factors.get('MODEL_UNCERTAINTY', 0.0):.2f} is high",
                recommended_action="VERIFY_MODEL_ASSUMPTIONS",
                severity="MEDIUM",
            ))
        
        # Trigger 3: Boundary compliance concern
        if assessment.factors.get("BOUNDARY_COMPLIANCE", 1.0) < 0.5:
            triggers.append(ReviewTrigger(
                trigger_type="BOUNDARY_CONCERN",
                reason="Action may violate behavioral boundaries",
                recommended_action="BOUNDARY_VERIFICATION",
                severity="CRITICAL",
            ))
        
        # Trigger 4: No historical precedent
        if assessment.factors.get("HISTORICAL_SUCCESS", 0.0) < 0.3:
            triggers.append(ReviewTrigger(
                trigger_type="NO_PRECEDENT",
                reason="No strong historical precedent for this action type",
                recommended_action="PRECEDENT_ANALYSIS",
                severity="MEDIUM",
            ))
        
        return triggers
    
    def set_review_threshold(self, threshold: float) -> None:
        """
        Set the confidence threshold for triggering review.
        
        Args:
            threshold: Threshold value (0.0-1.0).
        
        Raises:
            ValueError: If threshold is invalid.
        """
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("threshold must be between 0.0 and 1.0")
        
        self.review_threshold = threshold
        self._model.review_threshold = threshold
    
    def get_model_documentation(self) -> Dict[str, Any]:
        """
        Get comprehensive documentation of scoring model.
        
        Returns:
            Dictionary containing model documentation.
        """
        return {
            "model_version": self._model.model_version,
            "factors": self._model.factors,
            "weights": self._model.weights,
            "algorithm": self._model.algorithm,
            "review_threshold": self._model.review_threshold,
            "examples": [asdict(ex) if hasattr(ex, '__dataclass_fields__') else ex 
                        for ex in self._model.examples],
        }
    
    def get_assessment(self, assessment_id: str) -> Optional[ConfidenceAssessment]:
        """
        Retrieve assessment by ID.
        
        Args:
            assessment_id: Assessment identifier.
        
        Returns:
            ConfidenceAssessment if found, None otherwise.
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT assessment_id, timestamp, action, action_type, confidence_score,
                       factors, context, evidence, requires_review
                FROM confidence_assessments
                WHERE assessment_id = ?
            """, (assessment_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
            
            return self._row_to_assessment(row)
    
    def get_assessment_history(
        self,
        action: str,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get assessment history for a specific action.
        
        Args:
            action: Action to query.
            limit: Maximum results.
        
        Returns:
            List of assessments for action.
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT assessment_id, timestamp, action, action_type, confidence_score,
                       factors, context, evidence, requires_review
                FROM confidence_assessments
                WHERE action = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (action, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [self._row_to_dict(row) for row in rows]
    
    def compare_assessments(
        self,
        assessments: List[ConfidenceAssessment],
    ) -> Dict[str, Any]:
        """
        Compare multiple assessments.
        
        Args:
            assessments: List of assessments to compare.
        
        Returns:
            Comparison analysis.
        """
        if not assessments:
            return {}
        
        scores = [a.confidence_score for a in assessments]
        
        return {
            "count": len(assessments),
            "average_score": sum(scores) / len(scores),
            "min_score": min(scores),
            "max_score": max(scores),
            "assessments": [
                {
                    "action": a.action,
                    "score": a.confidence_score,
                    "requires_review": a.requires_review,
                }
                for a in assessments
            ],
        }
    
    def _persist_assessment(self, assessment: ConfidenceAssessment) -> None:
        """Persist assessment to database."""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO confidence_assessments
                (assessment_id, timestamp, action, action_type, confidence_score,
                 factors, context, evidence, requires_review)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                assessment.assessment_id,
                assessment.timestamp.isoformat(),
                assessment.action,
                assessment.action_type,
                assessment.confidence_score,
                json.dumps(assessment.factors),
                json.dumps(assessment.context) if assessment.context else None,
                json.dumps(assessment.evidence) if assessment.evidence else None,
                1 if assessment.requires_review else 0,
            ))
            
            # Persist triggers
            for trigger in assessment.review_triggers:
                cursor.execute("""
                    INSERT INTO review_triggers
                    (trigger_id, assessment_id, trigger_type, reason,
                     recommended_action, severity, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    trigger.trigger_id,
                    assessment.assessment_id,
                    trigger.trigger_type,
                    trigger.reason,
                    trigger.recommended_action,
                    trigger.severity,
                    trigger.created_at.isoformat(),
                ))
            
            conn.commit()
            conn.close()
    
    def _row_to_assessment(self, row: Tuple) -> ConfidenceAssessment:
        """Convert database row to ConfidenceAssessment."""
        (assessment_id, timestamp, action, action_type, confidence_score,
         factors, context, evidence, requires_review) = row
        
        return ConfidenceAssessment(
            assessment_id=assessment_id,
            timestamp=datetime.fromisoformat(timestamp),
            action=action,
            action_type=action_type,
            confidence_score=confidence_score,
            factors=json.loads(factors) if factors else {},
            context=json.loads(context) if context else None,
            evidence=json.loads(evidence) if evidence else None,
            requires_review=bool(requires_review),
        )
    
    def _row_to_dict(self, row: Tuple) -> Dict[str, Any]:
        """Convert database row to dictionary."""
        (assessment_id, timestamp, action, action_type, confidence_score,
         factors, context, evidence, requires_review) = row
        
        return {
            "assessment_id": assessment_id,
            "timestamp": timestamp,
            "action": action,
            "action_type": action_type,
            "confidence_score": confidence_score,
            "factors": json.loads(factors) if factors else {},
            "context": json.loads(context) if context else None,
            "evidence": json.loads(evidence) if evidence else None,
            "requires_review": bool(requires_review),
        }
