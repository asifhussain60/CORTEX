"""Tier2 Governance: Hallucination Detector

Implements CORE-031: Hallucination Detection & Confidence Scoring.
Detects potential hallucinations and scores confidence with minimum 0.75 threshold.

Author: CORTEX Framework
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class ConfidenceLevel(Enum):
    """Confidence levels."""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class HallucinationRisk(Enum):
    """Hallucination risk levels."""
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ConfidenceScore:
    """Confidence score for hallucination detection."""
    value: float
    reasoning: str
    fact_checks: List[str] = field(default_factory=list)
    evidence_sources: List[str] = field(default_factory=list)
    
    def get_level(self) -> ConfidenceLevel:
        """Get confidence level based on value.
        
        Returns:
            ConfidenceLevel enum
        """
        if self.value >= 0.9:
            return ConfidenceLevel.VERY_HIGH
        elif self.value >= 0.75:
            return ConfidenceLevel.HIGH
        elif self.value >= 0.5:
            return ConfidenceLevel.MEDIUM
        elif self.value >= 0.25:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW


@dataclass
class HallucinationDetectionResult:
    """Result of hallucination detection."""
    is_safe: bool
    confidence_score: ConfidenceScore
    hallucination_risk: HallucinationRisk
    detected_hallucinations: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    reasoning_steps: List[str] = field(default_factory=list)


@dataclass
class Result:
    """Generic result wrapper."""
    success: bool
    value: Any = None
    error: Optional[str] = None


class HallucinationDetector:
    """Detect hallucinations in outputs.
    
    Analyzes outputs for potential hallucinations based on:
    - Fact verification against knowledge base
    - Reasoning quality and length
    - Confidence scoring
    """
    
    def __init__(self, confidence_threshold: float = 0.75):
        """Initialize the detector.
        
        Args:
            confidence_threshold: Minimum confidence threshold (default 0.75)
        """
        self.confidence_threshold = confidence_threshold
        self.knowledge_base: Set[str] = set()
        self.detection_history: List[HallucinationDetectionResult] = []
    
    def add_to_knowledge_base(self, facts: List[str]) -> None:
        """Add facts to knowledge base.
        
        Args:
            facts: List of verified facts to add
        """
        self.knowledge_base.update(facts)
    
    def score_confidence(
        self,
        output: str,
        reasoning: str,
        fact_checks: Optional[List[str]] = None
    ) -> ConfidenceScore:
        """Score confidence for an output.
        
        Args:
            output: The output to score
            reasoning: Reasoning provided for the output
            fact_checks: Optional list of facts to verify
            
        Returns:
            ConfidenceScore object
        """
        if fact_checks is None:
            fact_checks = []
        
        # Empty output or reasoning = 0 confidence
        if not output or not reasoning:
            return ConfidenceScore(
                value=0.0,
                reasoning=reasoning,
                fact_checks=fact_checks
            )
        
        # Calculate confidence based on multiple factors
        confidence = 0.0
        
        # Factor 1: Reasoning length (longer = more confidence, max 0.4)
        reasoning_score = min(len(reasoning) / 200.0, 0.4)
        confidence += reasoning_score
        
        # Factor 2: Fact verification (verified facts = more confidence, max 0.6)
        if fact_checks:
            verified_count = sum(1 for fact in fact_checks if fact in self.knowledge_base)
            fact_score = (verified_count / len(fact_checks)) * 0.6
            confidence += fact_score
        else:
            # No fact checks provided, give partial credit based on reasoning
            confidence += 0.3
        
        # Ensure confidence is between 0 and 1
        confidence = max(0.0, min(1.0, confidence))
        
        return ConfidenceScore(
            value=confidence,
            reasoning=reasoning,
            fact_checks=fact_checks
        )
    
    def detect_hallucinations(
        self,
        output: str,
        reasoning: str,
        fact_checks: Optional[List[str]] = None
    ) -> Result:
        """Detect hallucinations in an output.
        
        Args:
            output: The output to analyze
            reasoning: Reasoning provided for the output
            fact_checks: Optional list of facts to verify
            
        Returns:
            Result with HallucinationDetectionResult
        """
        if not output:
            return Result(success=False, error="Output cannot be empty")
        
        if fact_checks is None:
            fact_checks = []
        
        # Score confidence
        confidence_score = self.score_confidence(output, reasoning, fact_checks)
        
        # Identify unverified facts
        detected_hallucinations = [
            fact for fact in fact_checks
            if fact not in self.knowledge_base
        ]
        
        # Assess risk
        risk = self._assess_risk(confidence_score.value, detected_hallucinations)
        
        # Determine if output is safe
        is_safe = risk in [HallucinationRisk.SAFE, HallucinationRisk.LOW]
        
        # Generate recommendations
        recommendations = self._generate_recommendations(is_safe, risk)
        
        # Extract reasoning steps
        reasoning_steps = self._extract_reasoning_steps(reasoning)
        
        result = HallucinationDetectionResult(
            is_safe=is_safe,
            confidence_score=confidence_score,
            hallucination_risk=risk,
            detected_hallucinations=detected_hallucinations,
            recommendations=recommendations,
            reasoning_steps=reasoning_steps
        )
        
        # Track in history
        self.detection_history.append(result)
        
        return Result(success=True, value=result)
    
    def _assess_risk(
        self,
        confidence: float,
        hallucinations: List[str]
    ) -> HallucinationRisk:
        """Assess hallucination risk.
        
        Args:
            confidence: Confidence score
            hallucinations: List of detected hallucinations
            
        Returns:
            HallucinationRisk enum
        """
        hallucination_count = len(hallucinations)
        
        if confidence >= 0.9 and hallucination_count == 0:
            return HallucinationRisk.SAFE
        elif confidence >= 0.75 and hallucination_count == 0:
            return HallucinationRisk.LOW
        elif confidence >= 0.5 and hallucination_count <= 1:
            return HallucinationRisk.MEDIUM
        elif confidence < 0.3 and hallucination_count >= 2:
            return HallucinationRisk.CRITICAL
        elif confidence >= 0.3:
            return HallucinationRisk.HIGH
        else:
            return HallucinationRisk.CRITICAL
    
    def _extract_reasoning_steps(self, reasoning: str) -> List[str]:
        """Extract reasoning steps from reasoning text.
        
        Args:
            reasoning: Reasoning text
            
        Returns:
            List of reasoning steps
        """
        if not reasoning:
            return []
        
        # Split on sentence boundaries
        steps = [s.strip() for s in reasoning.split('.') if s.strip()]
        return steps
    
    def _extract_sources(self, reasoning: str) -> List[str]:
        """Extract evidence sources from reasoning.
        
        Args:
            reasoning: Reasoning text
            
        Returns:
            List of sources
        """
        sources = []
        keywords = ['based on', 'from', 'according to', 'source', 'knowledge base']
        
        for keyword in keywords:
            if keyword.lower() in reasoning.lower():
                sources.append(f"Mentioned: {keyword}")
        
        return sources
    
    def _generate_recommendations(
        self,
        is_safe: bool,
        risk_level: HallucinationRisk
    ) -> List[str]:
        """Generate recommendations based on risk.
        
        Args:
            is_safe: Whether output is safe
            risk_level: Risk level
            
        Returns:
            List of recommendations
        """
        if is_safe:
            return []
        
        recommendations = []
        
        if risk_level == HallucinationRisk.CRITICAL:
            recommendations.append("CRITICAL: Retry the operation with verified inputs")
            recommendations.append("Verify all facts before proceeding")
            recommendations.append("Consider manual review")
        elif risk_level == HallucinationRisk.HIGH:
            recommendations.append("Review the output carefully before use")
            recommendations.append("Verify key facts against trusted sources")
        elif risk_level == HallucinationRisk.MEDIUM:
            recommendations.append("Validate output against knowledge base")
            recommendations.append("Consider additional verification")
        
        return recommendations
    
    def get_detection_summary(self) -> Dict[str, Any]:
        """Get detection summary statistics.
        
        Returns:
            Summary dictionary
        """
        if not self.detection_history:
            return {
                "total_detections": 0,
                "safe_outputs": 0,
                "average_confidence": 0.0
            }
        
        safe_count = sum(1 for d in self.detection_history if d.is_safe)
        avg_confidence = sum(d.confidence_score.value for d in self.detection_history) / len(self.detection_history)
        
        return {
            "total_detections": len(self.detection_history),
            "safe_outputs": safe_count,
            "unsafe_outputs": len(self.detection_history) - safe_count,
            "average_confidence": avg_confidence
        }


__all__ = [
    "ConfidenceLevel",
    "ConfidenceScore",
    "HallucinationDetector",
    "HallucinationDetectionResult",
    "HallucinationRisk",
    "Result"
]
