"""
Confidence Scorer (Phase 48 Stage 3)

Multi-factor confidence scoring for validation results with 0.7 threshold gating.
Blocks execution when confidence < 0.7 with actionable improvement suggestions.

Author: Asif Hussain
Authority: PHASE-48-IMPLEMENTATION-PLAN.yaml Stage 3
Priority: P0-CRITICAL
AC-ID: AC-PHASE48-S3-IMPL-001
"""

from dataclasses import dataclass
from typing import Dict, List, Any
import logging


logger = logging.getLogger(__name__)


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class ConfidenceFactor:
    """A single factor contributing to overall confidence.
    
    Attributes:
        name: Factor name (e.g., "security", "clarity", "performance")
        score: Factor score from 0.0 (low) to 1.0 (high)
        weight: Importance weight (0.0-1.0)
        description: What this factor measures
    """
    name: str
    score: float
    weight: float
    description: str = ""


@dataclass
class ConfidenceResult:
    """Result of confidence scoring with gating decision.
    
    Attributes:
        score: Overall confidence score (0.0-1.0)
        passed: True if score >= 0.7 (gate passes)
        factors: List of contributing factors with individual scores
        explanation: Human-readable explanation (especially for low scores)
        recommendations: List of actionable improvement suggestions
    """
    score: float
    passed: bool
    factors: List[ConfidenceFactor]
    explanation: str
    recommendations: List[str]


# ============================================================================
# CONFIDENCE SCORER
# ============================================================================

class ConfidenceScorer:
    """Calculates confidence scores for validation results with threshold gating.
    
    Multi-factor scoring considers:
    1. Checklist results (security, performance, maintainability, etc.)
    2. Request clarity (specificity, completeness)
    3. Implementation risk assessment
    
    Flow:
    1. Calculate individual factor scores
    2. Apply weights to each factor
    3. Aggregate into overall confidence score
    4. Gate: PASS if score >= 0.7, BLOCK otherwise
    5. Generate explanation and recommendations
    
    Example:
        >>> scorer = ConfidenceScorer()
        >>> result = scorer.calculate_confidence(
        ...     request="Implement JWT authentication",
        ...     checklist_result={"security": 0.9, "performance": 0.8}
        ... )
        >>> print(result.score)
        0.85
        >>> print(result.passed)
        True
    """
    
    # Threshold for gating (must be >= 0.7 to pass)
    CONFIDENCE_THRESHOLD = 0.7
    
    # Factor weights (must sum to 1.0)
    WEIGHTS = {
        "checklist_aggregate": 0.5,   # 50% from checklist results
        "request_clarity": 0.25,       # 25% from request clarity
        "implementation_risk": 0.25,   # 25% from risk assessment
    }
    
    def __init__(self) -> None:
        """Initialize confidence scorer."""
        self.threshold = self.CONFIDENCE_THRESHOLD
    
    def calculate_confidence(
        self,
        request: str,
        checklist_result: Dict[str, float],
        **kwargs
    ) -> ConfidenceResult:
        """Calculate confidence score for validation result.
        
        Args:
            request: User's implementation request
            checklist_result: Dict of checklist category scores (0.0-1.0)
            **kwargs: Additional context (intent, challenges, etc.)
        
        Returns:
            ConfidenceResult with score, gating decision, and explanation
        """
        # Calculate individual factors
        factors = []
        
        # Factor 1: Checklist aggregate score
        checklist_factor = self._calculate_checklist_factor(checklist_result)
        factors.append(checklist_factor)
        
        # Factor 2: Request clarity score
        clarity_factor = self._calculate_clarity_factor(request)
        factors.append(clarity_factor)
        
        # Factor 3: Implementation risk score
        risk_factor = self._calculate_risk_factor(request, checklist_result)
        factors.append(risk_factor)
        
        # Calculate weighted overall score
        overall_score = sum(
            factor.score * factor.weight
            for factor in factors
        )
        
        # Clamp to [0.0, 1.0]
        overall_score = max(0.0, min(1.0, overall_score))
        
        # Gating decision
        passed = overall_score >= self.threshold
        
        # Generate explanation
        explanation = self._generate_explanation(overall_score, factors, passed)
        
        # Generate recommendations (especially for low scores)
        recommendations = self._generate_recommendations(factors, passed)
        
        return ConfidenceResult(
            score=overall_score,
            passed=passed,
            factors=factors,
            explanation=explanation,
            recommendations=recommendations
        )
    
    # ========================================================================
    # FACTOR CALCULATORS
    # ========================================================================
    
    def _calculate_checklist_factor(self, checklist_result: Dict[str, float]) -> ConfidenceFactor:
        """Calculate checklist aggregate factor.
        
        Args:
            checklist_result: Dict of category scores (e.g., {"security": 0.9})
        
        Returns:
            ConfidenceFactor for checklist aggregate
        """
        if not checklist_result:
            # No checklist data = low confidence
            return ConfidenceFactor(
                name="checklist_aggregate",
                score=0.3,
                weight=self.WEIGHTS["checklist_aggregate"],
                description="Pre-implementation checklist results"
            )
        
        # Average of all checklist scores
        scores = list(checklist_result.values())
        avg_score = sum(scores) / len(scores)
        
        return ConfidenceFactor(
            name="checklist_aggregate",
            score=avg_score,
            weight=self.WEIGHTS["checklist_aggregate"],
            description=f"Pre-implementation checklist ({len(scores)} categories)"
        )
    
    def _calculate_clarity_factor(self, request: str) -> ConfidenceFactor:
        """Calculate request clarity factor.
        
        Clear, specific requests score higher than vague ones.
        
        Args:
            request: User's request string
        
        Returns:
            ConfidenceFactor for request clarity
        """
        request_lower = request.lower()
        
        # Base score - start higher for reasonable requests
        score = 0.6
        
        # Bonus for length (more specific)
        word_count = len(request.split())
        if word_count >= 10:
            score += 0.25
        elif word_count >= 5:
            score += 0.15
        
        # Bonus for technical terms (indicates specificity)
        technical_terms = [
            "jwt", "oauth", "redis", "postgres", "elasticsearch",
            "websocket", "api", "authentication", "encryption",
            "microservice", "database", "cache", "queue", "async",
            "implement", "add", "create", "security", "performance"
        ]
        tech_term_count = sum(1 for term in technical_terms if term in request_lower)
        if tech_term_count >= 3:
            score += 0.2
        elif tech_term_count >= 1:
            score += 0.1
        
        # Penalty for vague terms
        vague_terms = ["something", "anything", "stuff", "thing"]
        if any(term in request_lower for term in vague_terms):
            score -= 0.3
        
        # Penalty for very short requests
        if word_count < 3:
            score -= 0.2
        
        # Clamp to [0.0, 1.0]
        score = max(0.0, min(1.0, score))
        
        return ConfidenceFactor(
            name="request_clarity",
            score=score,
            weight=self.WEIGHTS["request_clarity"],
            description="Clarity and specificity of request"
        )
    
    def _calculate_risk_factor(
        self,
        request: str,
        checklist_result: Dict[str, float]
    ) -> ConfidenceFactor:
        """Calculate implementation risk factor.
        
        Lower risk = higher confidence.
        
        Args:
            request: User's request
            checklist_result: Checklist results
        
        Returns:
            ConfidenceFactor for implementation risk (inverted - high score = low risk)
        """
        request_lower = request.lower()
        
        # Start with moderate risk
        risk_score = 0.6
        
        # Security-sensitive operations have higher risk
        if any(term in request_lower for term in ["auth", "password", "secret", "payment", "encryption"]):
            # If security checklist is high, risk is lower
            security_score = checklist_result.get("security", 0.5)
            if security_score >= 0.8:
                risk_score += 0.2  # Security handled well
            else:
                risk_score -= 0.2  # Security concerns
        
        # Performance-critical operations have higher risk
        if any(term in request_lower for term in ["performance", "optimize", "scale", "throughput"]):
            perf_score = checklist_result.get("performance", 0.5)
            if perf_score >= 0.8:
                risk_score += 0.1
            else:
                risk_score -= 0.1
        
        # Refactoring/rewrite operations have inherent risk
        if any(term in request_lower for term in ["refactor", "rewrite", "migrate", "replace"]):
            risk_score -= 0.1
        
        # Well-tested patterns reduce risk
        if any(term in request_lower for term in ["standard", "best practice", "proven", "established"]):
            risk_score += 0.1
        
        # Clamp to [0.0, 1.0]
        risk_score = max(0.0, min(1.0, risk_score))
        
        return ConfidenceFactor(
            name="implementation_risk",
            score=risk_score,
            weight=self.WEIGHTS["implementation_risk"],
            description="Risk assessment (higher = lower risk)"
        )
    
    # ========================================================================
    # EXPLANATION GENERATION
    # ========================================================================
    
    def _generate_explanation(
        self,
        overall_score: float,
        factors: List[ConfidenceFactor],
        passed: bool
    ) -> str:
        """Generate human-readable explanation of confidence score.
        
        Args:
            overall_score: Overall confidence score
            factors: List of contributing factors
            passed: Whether gate passed
        
        Returns:
            Human-readable explanation
        """
        if passed:
            return (
                f"Confidence score: {overall_score:.2f} (PASSED)\n\n"
                f"The validation has sufficient confidence to proceed. "
                f"All key factors meet minimum thresholds."
            )
        
        # Low confidence - detailed explanation
        explanation = f"Confidence score: {overall_score:.2f} (BLOCKED - threshold: {self.threshold})\n\n"
        explanation += "Validation is blocked due to low confidence. "
        explanation += "Address the following concerns:\n\n"
        
        # Identify weak factors (below 0.6)
        weak_factors = [f for f in factors if f.score < 0.6]
        
        for factor in weak_factors:
            factor_display_name = factor.name.replace('_', ' ').title()
            explanation += f"- **{factor_display_name}**: "
            explanation += f"{factor.score:.2f}/1.00 (weight: {factor.weight:.0%})\n"
            explanation += f"  {factor.description}\n"
            
            # Add specific improvement guidance
            if factor.name == "checklist_aggregate":
                explanation += "  Improve: security, maintainability, performance scores\n"
            elif factor.name == "request_clarity":
                explanation += "  Improve: Add more technical details and specificity\n"
            elif factor.name == "implementation_risk":
                explanation += "  Improve: Break into smaller increments, use proven patterns\n"
        
        return explanation
    
    def _generate_recommendations(
        self,
        factors: List[ConfidenceFactor],
        passed: bool
    ) -> List[str]:
        """Generate actionable recommendations for improvement.
        
        Args:
            factors: List of confidence factors
            passed: Whether gate passed
        
        Returns:
            List of recommendation strings
        """
        if passed:
            return ["Validation passed - proceed with implementation"]
        
        recommendations = []
        
        # Analyze each factor for recommendations
        for factor in factors:
            if factor.name == "checklist_aggregate" and factor.score < 0.6:
                recommendations.append(
                    "Improve pre-implementation checklist scores by addressing "
                    "security, performance, and maintainability concerns"
                )
            
            elif factor.name == "request_clarity" and factor.score < 0.6:
                recommendations.append(
                    "Clarify your request with more specific technical details: "
                    "technologies, architecture, acceptance criteria"
                )
            
            elif factor.name == "implementation_risk" and factor.score < 0.6:
                recommendations.append(
                    "Reduce implementation risk by: "
                    "(1) Breaking into smaller increments, "
                    "(2) Using proven patterns, "
                    "(3) Adding comprehensive tests"
                )
        
        # General recommendation
        if not recommendations:
            recommendations.append(
                "Improve overall confidence by providing more context and "
                "addressing validation concerns"
            )
        
        return recommendations

    def score_learnings(self, learnings: List[Any]) -> List[Any]:
        """Score learnings by confidence (frequency-based).
        
        This method is used by UniversalLearningLoop to score learning
        captures before merging to knowledge repositories.
        
        Note: This method preserves existing confidence scores. It only
        calculates frequency-based scores for learnings that don't have
        a confidence value set yet.
        
        Args:
            learnings: List of LearningCapture objects
            
        Returns:
            List of learnings (confidence preserved or calculated)
        """
        from collections import Counter
        
        # Count pattern occurrences using orchestrator+operation as key
        pattern_counts = Counter(
            f"{learning.orchestrator}:{learning.operation}" 
            for learning in learnings
        )
        
        total_occurrences = sum(pattern_counts.values())
        
        # Only calculate confidence if not already explicitly set
        for learning in learnings:
            # Check if confidence was explicitly set (not the default 0.0)
            # If confidence > 0, preserve it (whether high or low)
            if hasattr(learning, 'confidence') and learning.confidence > 0:
                continue
                
            pattern_key = f"{learning.orchestrator}:{learning.operation}"
            frequency = pattern_counts[pattern_key]
            # Normalize: more frequent patterns get higher confidence
            # Range: 0.5 (single occurrence) to 1.0 (very frequent)
            learning.confidence = min(
                1.0,
                0.5 + (0.5 * frequency / max(1, total_occurrences))
            )
        
        return learnings
