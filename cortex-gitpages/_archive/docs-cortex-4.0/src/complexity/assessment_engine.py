"""
Complexity Assessment Engine - Production Implementation.

Aggregates LENS confidence metrics and relationship analysis into a 5-level
complexity scale with reproducible scoring and calibrated thresholds.
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class ComplexityLevel(Enum):
    """5-level complexity scale for operations."""
    TRIVIAL = 1      # Very simple, straightforward
    SIMPLE = 2       # Clear and manageable
    MODERATE = 3     # Standard complexity
    COMPLEX = 4      # Intricate, requires attention
    CRITICAL = 5     # Highly complex, critical


@dataclass
class LENSMetrics:
    """LENS confidence metrics for operation quality assessment."""
    
    logical_confidence: float      # 0-1 (logic soundness)
    evidence_confidence: float     # 0-1 (evidence quality)
    narrative_confidence: float    # 0-1 (narrative clarity)
    semantic_confidence: float     # 0-1 (semantic consistency)
    
    def average_confidence(self) -> float:
        """Calculate average LENS confidence."""
        return (self.logical_confidence + self.evidence_confidence + 
                self.narrative_confidence + self.semantic_confidence) / 4
    
    def validate(self) -> Tuple[bool, str]:
        """Validate LENS metrics are in range [0, 1]."""
        for name, value in [
            ('logical', self.logical_confidence),
            ('evidence', self.evidence_confidence),
            ('narrative', self.narrative_confidence),
            ('semantic', self.semantic_confidence)
        ]:
            if not (0 <= value <= 1):
                return False, f"{name}_confidence out of range: {value}"
        return True, ""


@dataclass
class RelationshipAnalysis:
    """Relationship complexity analysis from orchestrator graph."""
    
    entity_count: int              # Number of entities involved
    relationship_count: int        # Number of relationships
    cycle_count: int               # Detected cycles
    max_depth: int                 # Maximum relationship depth
    average_degree: float          # Average node degree


@dataclass
class ComplexityScore:
    """Complexity assessment result."""
    
    lens_score: float              # 0-100 (from LENS metrics)
    relationship_score: float      # 0-100 (from relationships)
    combined_score: float          # 0-100 (weighted combination)
    complexity_level: ComplexityLevel
    confidence: float              # Assessment confidence (0-1)
    timestamp: datetime = field(default_factory=datetime.now)


class ComplexityAssessmentEngine:
    """
    Engine for assessing operation complexity.
    
    Combines LENS confidence metrics with relationship analysis to produce
    a 5-level complexity scale with reproducible, calibrated scoring.
    """
    
    # Calibrated thresholds for 5-level scale
    LEVEL_THRESHOLDS = {
        ComplexityLevel.TRIVIAL: (0, 20),
        ComplexityLevel.SIMPLE: (20, 40),
        ComplexityLevel.MODERATE: (40, 60),
        ComplexityLevel.COMPLEX: (60, 80),
        ComplexityLevel.CRITICAL: (80, 100),
    }
    
    # Weighting for score combination
    LENS_WEIGHT = 0.6              # LENS metrics contribution (60%)
    RELATIONSHIP_WEIGHT = 0.4      # Relationship metrics contribution (40%)
    
    def __init__(self):
        """Initialize assessment engine."""
        self.assessment_history: List[ComplexityScore] = []
        self.calibration_log: List[Dict] = []
    
    def assess_complexity(
        self,
        lens_metrics: LENSMetrics,
        relationships: RelationshipAnalysis
    ) -> ComplexityScore:
        """
        Assess operation complexity from metrics.
        
        Args:
            lens_metrics: LENS confidence values
            relationships: Relationship graph analysis
        
        Returns:
            ComplexityScore with level and confidence assessment
        """
        # Calculate LENS score (0-100)
        lens_confidence = lens_metrics.average_confidence()
        lens_score = lens_confidence * 100
        
        # Calculate relationship complexity score (0-100)
        relationship_score = self._calculate_relationship_score(relationships)
        
        # Combine scores with configured weights
        combined_score = (
            (lens_score * self.LENS_WEIGHT) +
            (relationship_score * self.RELATIONSHIP_WEIGHT)
        )
        
        # Determine complexity level from combined score
        level = self._score_to_level(combined_score)
        
        # Calculate assessment confidence
        confidence = self._calculate_confidence(lens_metrics, relationships)
        
        score = ComplexityScore(
            lens_score=lens_score,
            relationship_score=relationship_score,
            combined_score=combined_score,
            complexity_level=level,
            confidence=confidence
        )
        
        # Record in history
        self.assessment_history.append(score)
        
        return score
    
    def _calculate_relationship_score(self, rel: RelationshipAnalysis) -> float:
        """
        Calculate relationship complexity score (0-100).
        
        Factors:
        - Entity count (40 points max)
        - Relationship count (30 points max)
        - Cycle count (20 points max)
        - Maximum depth (10 points max)
        """
        entity_factor = min(rel.entity_count * 5, 40)
        relationship_factor = min(rel.relationship_count * 3, 30)
        cycle_factor = min(rel.cycle_count * 10, 20)
        depth_factor = min(rel.max_depth * 5, 10)
        
        return min(entity_factor + relationship_factor + cycle_factor + depth_factor, 100)
    
    def _score_to_level(self, score: float) -> ComplexityLevel:
        """
        Convert numeric score to complexity level.
        
        Uses configured thresholds for all 5 levels.
        """
        for level, (min_val, max_val) in self.LEVEL_THRESHOLDS.items():
            if min_val <= score < max_val:
                return level
        return ComplexityLevel.CRITICAL
    
    def _calculate_confidence(
        self,
        lens: LENSMetrics,
        rel: RelationshipAnalysis
    ) -> float:
        """
        Calculate confidence in complexity assessment (0-1).
        
        Factors:
        - LENS confidence (50%): Higher is better
        - Metric consistency (30%): Lower variance is better
        - Relationship completeness (20%): More complete is better
        """
        # LENS confidence factor
        lens_confidence = lens.average_confidence()
        
        # Consistency factor
        variance = self._calculate_metric_variance(lens)
        consistency = 1.0 - min(variance / 2, 1.0)
        
        # Relationship completeness factor
        completeness = min(rel.relationship_count / max(rel.entity_count * 2, 1), 1.0)
        
        return (lens_confidence * 0.5) + (consistency * 0.3) + (completeness * 0.2)
    
    def _calculate_metric_variance(self, lens: LENSMetrics) -> float:
        """Calculate standard deviation of LENS metrics."""
        values = [
            lens.logical_confidence,
            lens.evidence_confidence,
            lens.narrative_confidence,
            lens.semantic_confidence
        ]
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def calibrate_thresholds(
        self,
        target_level: ComplexityLevel,
        examples: List[float]
    ) -> None:
        """
        Calibrate thresholds for a complexity level using examples.
        
        Args:
            target_level: Level to calibrate
            examples: List of scores that should map to this level
        """
        if not examples:
            return
        
        min_score = min(examples)
        max_score = max(examples)
        center = (min_score + max_score) / 2
        
        # Adjust threshold based on examples
        self.LEVEL_THRESHOLDS[target_level] = (min_score - 1, max_score + 1)
        
        # Record calibration
        self.calibration_log.append({
            'level': target_level,
            'examples': examples,
            'center': center,
            'timestamp': datetime.now()
        })
    
    def get_assessment_statistics(self) -> Dict:
        """
        Get statistics on all assessments performed.
        
        Returns: Dictionary with count, average, and level distribution
        """
        if not self.assessment_history:
            return {}
        
        scores = [s.combined_score for s in self.assessment_history]
        level_counts = {}
        for level in ComplexityLevel:
            level_counts[level.name] = sum(
                1 for s in self.assessment_history if s.complexity_level == level
            )
        
        return {
            'total_assessments': len(self.assessment_history),
            'average_score': sum(scores) / len(scores),
            'min_score': min(scores),
            'max_score': max(scores),
            'level_distribution': level_counts,
            'average_confidence': sum(s.confidence for s in self.assessment_history) / len(self.assessment_history)
        }
    
    def clear_history(self) -> None:
        """Clear assessment history."""
        self.assessment_history = []
        self.calibration_log = []
