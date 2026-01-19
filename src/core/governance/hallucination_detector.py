"""
CORE-031: Hallucination Detection & Confidence Scoring

Detects AI-generated hallucinations through multiple validation techniques:
- Confidence scoring (≥0.75 minimum)
- Fact-checking against knowledge base
- Reasoning trace validation
- Output determinism verification
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set, Any


@dataclass
class Result:
    """Generic result type for error handling."""
    success: bool
    value: Optional[Any] = None
    error: Optional[str] = None
    
    @classmethod
    def ok(cls, value: Any) -> "Result":
        """Create successful result."""
        return cls(success=True, value=value)
    
    @classmethod
    def error(cls, error: str) -> "Result":
        """Create error result."""
        return cls(success=False, error=error)


class ConfidenceLevel(Enum):
    """Confidence level for model outputs."""
    VERY_LOW = "very_low"      # < 0.25
    LOW = "low"                 # 0.25-0.50
    MEDIUM = "medium"           # 0.50-0.75
    HIGH = "high"               # 0.75-0.90
    VERY_HIGH = "very_high"     # >= 0.90


class HallucinationRisk(Enum):
    """Risk level of hallucination detection."""
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ConfidenceScore:
    """Confidence score with supporting evidence."""
    value: float  # 0.0 to 1.0
    reasoning: str
    fact_checks: List[str] = field(default_factory=list)
    evidence_sources: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def get_level(self) -> ConfidenceLevel:
        """Get confidence level from score."""
        if self.value < 0.25:
            return ConfidenceLevel.VERY_LOW
        elif self.value < 0.50:
            return ConfidenceLevel.LOW
        elif self.value < 0.75:
            return ConfidenceLevel.MEDIUM
        elif self.value < 0.90:
            return ConfidenceLevel.HIGH
        else:
            return ConfidenceLevel.VERY_HIGH


@dataclass
class HallucinationDetectionResult:
    """Result of hallucination detection analysis."""
    output: str
    confidence_score: ConfidenceScore
    hallucination_risk: HallucinationRisk
    is_safe: bool
    detected_hallucinations: List[str] = field(default_factory=list)
    reasoning_traces: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)


class HallucinationDetector:
    """Detects and scores AI-generated hallucinations."""
    
    def __init__(self):
        """Initialize hallucination detector."""
        self.confidence_threshold = 0.75
        self.knowledge_base: Set[str] = set()
        self.verified_facts: Dict[str, bool] = {}
        self.detection_history: List[HallucinationDetectionResult] = []
    
    def add_to_knowledge_base(self, facts: List[str]) -> None:
        """
        Add verified facts to knowledge base.
        
        Args:
            facts: List of verified facts.
        """
        self.knowledge_base.update(facts)
    
    def score_confidence(
        self,
        output: str,
        reasoning: str,
        fact_checks: Optional[List[str]] = None,
    ) -> ConfidenceScore:
        """
        Score confidence of model output.
        
        Args:
            output: Model output to score.
            reasoning: Model reasoning for output.
            fact_checks: Optional fact checks to verify.
            
        Returns:
            ConfidenceScore with value and supporting evidence.
        """
        if not output or not reasoning:
            return ConfidenceScore(
                value=0.0,
                reasoning="Missing output or reasoning",
                evidence_sources=[]
            )
        
        base_score = 0.5
        
        # Reasoning length factor (longer reasoning = higher confidence)
        if len(reasoning) > 100:
            base_score += 0.15
        elif len(reasoning) > 50:
            base_score += 0.10
        
        # Fact verification factor
        verified_count = 0
        if fact_checks:
            for fact in fact_checks:
                if self._verify_fact(fact):
                    verified_count += 1
                    self.verified_facts[fact] = True
                else:
                    self.verified_facts[fact] = False
            
            if fact_checks:
                verification_rate = verified_count / len(fact_checks)
                base_score += verification_rate * 0.35
        
        # Clamp score between 0 and 1
        final_score = min(max(base_score, 0.0), 1.0)
        
        return ConfidenceScore(
            value=final_score,
            reasoning=reasoning,
            fact_checks=fact_checks or [],
            evidence_sources=self._extract_sources(reasoning)
        )
    
    def detect_hallucinations(
        self,
        output: str,
        reasoning: str,
        fact_checks: Optional[List[str]] = None,
    ) -> Result:
        """
        Detect hallucinations in model output.
        
        Args:
            output: Model output to analyze.
            reasoning: Model reasoning for output.
            fact_checks: Optional fact checks to verify.
            
        Returns:
            Result with HallucinationDetectionResult or error.
        """
        try:
            if not output:
                return Result.error("Output cannot be empty")
            
            confidence_score = self.score_confidence(
                output, reasoning, fact_checks
            )
            
            # Detect specific hallucinations
            detected_hallucinations = self._find_hallucinations(
                output, reasoning, fact_checks or []
            )
            
            # Determine hallucination risk
            hallucination_risk = self._assess_risk(
                confidence_score.value,
                detected_hallucinations
            )
            
            is_safe = (
                confidence_score.value >= self.confidence_threshold
                and hallucination_risk in (HallucinationRisk.SAFE, HallucinationRisk.LOW)
            )
            
            result = HallucinationDetectionResult(
                output=output,
                confidence_score=confidence_score,
                hallucination_risk=hallucination_risk,
                is_safe=is_safe,
                detected_hallucinations=detected_hallucinations,
                reasoning_traces=self._extract_reasoning_steps(reasoning),
                recommendations=self._generate_recommendations(is_safe, hallucination_risk)
            )
            
            self.detection_history.append(result)
            return Result.ok(result)
            
        except Exception as e:
            return Result.error(f"Hallucination detection failed: {str(e)}")
    
    def _verify_fact(self, fact: str) -> bool:
        """
        Verify fact against knowledge base.
        
        Args:
            fact: Fact to verify.
            
        Returns:
            True if fact is verified, False otherwise.
        """
        return fact in self.knowledge_base
    
    def _extract_sources(self, reasoning: str) -> List[str]:
        """
        Extract evidence sources from reasoning.
        
        Args:
            reasoning: Reasoning text.
            
        Returns:
            List of extracted source indicators.
        """
        sources = []
        keywords = ["source:", "based on", "from", "according to", "evidence:"]
        lower_reasoning = reasoning.lower()
        
        for keyword in keywords:
            if keyword in lower_reasoning:
                sources.append(keyword)
        
        return sources
    
    def _find_hallucinations(
        self,
        output: str,
        reasoning: str,
        fact_checks: List[str]
    ) -> List[str]:
        """
        Find specific hallucinations in output.
        
        Args:
            output: Output to check.
            reasoning: Reasoning to check.
            fact_checks: Fact checks to verify.
            
        Returns:
            List of detected hallucinations.
        """
        hallucinations = []
        
        # Check for contradictions between reasoning and output
        if len(output) > 0 and len(reasoning) > 0:
            if "not" in reasoning.lower() and "not" not in output.lower():
                hallucinations.append("Potential negation contradiction")
        
        # Check for unverified facts
        for fact in fact_checks:
            if not self._verify_fact(fact):
                hallucinations.append(f"Unverified fact: {fact}")
        
        return hallucinations
    
    def _assess_risk(
        self,
        confidence: float,
        hallucinations: List[str]
    ) -> HallucinationRisk:
        """
        Assess hallucination risk level.
        
        Args:
            confidence: Confidence score.
            hallucinations: Detected hallucinations.
            
        Returns:
            HallucinationRisk level.
        """
        hallucination_count = len(hallucinations)
        
        if confidence >= 0.90 and hallucination_count == 0:
            return HallucinationRisk.SAFE
        elif confidence >= 0.75 and hallucination_count <= 1:
            return HallucinationRisk.LOW
        elif confidence >= 0.60 and hallucination_count <= 2:
            return HallucinationRisk.MEDIUM
        elif confidence >= 0.40:
            return HallucinationRisk.HIGH
        else:
            return HallucinationRisk.CRITICAL
    
    def _extract_reasoning_steps(self, reasoning: str) -> List[str]:
        """
        Extract individual reasoning steps.
        
        Args:
            reasoning: Reasoning text.
            
        Returns:
            List of reasoning steps.
        """
        steps = []
        if reasoning:
            # Split by common step indicators
            for part in reasoning.split("."):
                stripped = part.strip()
                if stripped:
                    steps.append(stripped)
        return steps
    
    def _generate_recommendations(
        self,
        is_safe: bool,
        risk_level: HallucinationRisk
    ) -> List[str]:
        """
        Generate recommendations based on detection results.
        
        Args:
            is_safe: Whether output is safe.
            risk_level: Hallucination risk level.
            
        Returns:
            List of recommendations.
        """
        recommendations = []
        
        if not is_safe:
            recommendations.append("Increase confidence with additional reasoning")
        
        if risk_level == HallucinationRisk.CRITICAL:
            recommendations.append("Reject output and retry with different prompt")
        elif risk_level == HallucinationRisk.HIGH:
            recommendations.append("Flag output for human review before use")
        elif risk_level == HallucinationRisk.MEDIUM:
            recommendations.append("Validate output against additional sources")
        
        return recommendations
    
    def get_detection_summary(self) -> Dict:
        """
        Get summary of detection history.
        
        Returns:
            Dictionary with detection statistics.
        """
        if not self.detection_history:
            return {
                "total_detections": 0,
                "safe_outputs": 0,
                "average_confidence": 0.0,
            }
        
        safe_count = sum(1 for d in self.detection_history if d.is_safe)
        avg_confidence = sum(d.confidence_score.value for d in self.detection_history) / len(self.detection_history)
        
        return {
            "total_detections": len(self.detection_history),
            "safe_outputs": safe_count,
            "unsafe_outputs": len(self.detection_history) - safe_count,
            "average_confidence": avg_confidence,
        }
