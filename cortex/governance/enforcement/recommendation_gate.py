"""
Recommendation Gate - Agent Architecture Awareness Layer
Authority: CORE-030 (Implementation Truth) + CORE-035 (Single Canonical Implementation)
Purpose: Prevent agents from recommending solutions without consulting existing architecture

This module enforces that all agent recommendations go through validation:
1. LENS analysis (existing implementation check)
2. Registry consultation (feature catalog)
3. ROI analysis (cost vs benefit)
4. Duplicate detection (CORE-035)
5. Complexity scoring (maintainability)
6. Rejection history (learning from past)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import yaml


class RecommendationRisk(Enum):
    """Risk levels for recommendations"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class RecommendationScore:
    """Recommendation validation score"""
    risk_level: RecommendationRisk
    risk_score: float  # 0.0-1.0
    similarity_to_rejected: float  # 0.0-1.0
    complexity_score: float  # 0.0-1.0
    roi_score: float  # 0.0-1.0
    architecture_alignment: float  # 0.0-1.0
    is_blocked: bool
    block_reason: Optional[str]
    recommendations: List[str]


class RecommendationGate:
    """
    Gate for validating agent recommendations before emission.
    
    Workflow:
    1. Agent proposes recommendation
    2. Gate checks LENS analysis (existing implementation)
    3. Gate checks registry (feature catalog)
    4. Gate calculates regression risk
    5. Gate checks rejection history
    6. Gate either: APPROVE, WARN, or BLOCK
    """
    
    def __init__(
        self,
        registry_path: str = "cortex-registry/_cortex-master",
        risk_threshold: float = 0.7
    ):
        """
        Initialize recommendation gate.
        
        Args:
            registry_path: Path to registry master directory
            risk_threshold: Risk score threshold for blocking (0.0-1.0)
        """
        self.registry_path = Path(registry_path)
        self.risk_threshold = risk_threshold
        self.rejection_history = self._load_rejection_history()
    
    def _load_rejection_history(self) -> Dict[str, Any]:
        """Load rejection history from registry"""
        rejection_file = self.registry_path / "rejected_recommendations.yaml"
        
        if not rejection_file.exists():
            return {"rejections": []}
        
        with open(rejection_file, 'r') as f:
            return yaml.safe_load(f)
    
    def validate_recommendation(
        self,
        recommendation: str,
        affected_files: List[str],
        change_type: str,
        agent_name: str
    ) -> RecommendationScore:
        """
        Validate recommendation before emission.
        
        Args:
            recommendation: Recommendation text
            affected_files: List of files that would be modified
            change_type: Type of change (e.g., "refactor", "new_feature", "fix")
            agent_name: Name of agent making recommendation
        
        Returns:
            RecommendationScore with validation results
        """
        # Gate 1: Check rejection history
        similarity = self._check_rejection_similarity(recommendation)
        
        # Gate 2: Calculate regression risk
        regression_risk = self._calculate_regression_risk(affected_files, change_type)
        
        # Gate 3: Check test health
        test_health = self._check_test_health(affected_files)
        
        # Gate 4: Check for duplicates (CORE-035)
        has_duplicates = self._check_duplicates(affected_files)
        
        # Gate 5: Calculate complexity
        complexity = self._calculate_complexity(affected_files, change_type)
        
        # Gate 6: Check architecture alignment
        alignment = self._check_architecture_alignment(
            recommendation,
            affected_files,
            agent_name
        )
        
        # Gate 7: Calculate ROI
        roi = self._calculate_roi(complexity, alignment, regression_risk)
        
        # Aggregate risk score
        risk_score = (
            similarity * 0.25 +
            regression_risk * 0.25 +
            (1.0 - test_health) * 0.15 +
            complexity * 0.15 +
            (1.0 - alignment) * 0.20
        )
        
        # Determine risk level
        if risk_score >= 0.8:
            risk_level = RecommendationRisk.CRITICAL
        elif risk_score >= 0.7:
            risk_level = RecommendationRisk.HIGH
        elif risk_score >= 0.4:
            risk_level = RecommendationRisk.MEDIUM
        else:
            risk_level = RecommendationRisk.LOW
        
        # Blocking conditions
        is_blocked = False
        block_reason = None
        recommendations_list = []
        
        if similarity > 0.3:
            is_blocked = True
            block_reason = f"Similar to rejected recommendation (similarity: {similarity:.2f})"
        elif regression_risk > self.risk_threshold:
            is_blocked = True
            block_reason = f"Regression risk too high ({regression_risk:.2f} > {self.risk_threshold})"
        elif test_health < 0.5:
            is_blocked = True
            block_reason = f"Test health insufficient ({test_health:.2f} < 0.5)"
        elif has_duplicates:
            is_blocked = True
            block_reason = "CORE-035 violation: Duplicate implementations detected"
        
        if not is_blocked:
            if risk_score > 0.5:
                recommendations_list.append(
                    "⚠️  HIGH RISK: Consider smaller incremental changes"
                )
            if alignment < 0.7:
                recommendations_list.append(
                    "⚠️  LOW ALIGNMENT: Consult architecture patterns first"
                )
            if complexity > 0.6:
                recommendations_list.append(
                    "⚠️  HIGH COMPLEXITY: Break into smaller phases"
                )
        
        return RecommendationScore(
            risk_level=risk_level,
            risk_score=risk_score,
            similarity_to_rejected=similarity,
            complexity_score=complexity,
            roi_score=roi,
            architecture_alignment=alignment,
            is_blocked=is_blocked,
            block_reason=block_reason,
            recommendations=recommendations_list
        )
    
    def _check_rejection_similarity(self, recommendation: str) -> float:
        """
        Check similarity to previously rejected recommendations.
        
        Args:
            recommendation: Recommendation text
        
        Returns:
            Similarity score (0.0-1.0)
        """
        # Simple keyword-based similarity for now
        # In production, this would use vector embeddings
        
        rejections = self.rejection_history.get("rejections", [])
        if not rejections:
            return 0.0
        
        max_similarity = 0.0
        rec_words = set(recommendation.lower().split())
        
        for rejection in rejections:
            rej_text = rejection.get("recommendation", "")
            rej_words = set(rej_text.lower().split())
            
            if rec_words and rej_words:
                intersection = rec_words & rej_words
                union = rec_words | rej_words
                similarity = len(intersection) / len(union) if union else 0.0
                max_similarity = max(max_similarity, similarity)
        
        return max_similarity
    
    def _calculate_regression_risk(
        self,
        affected_files: List[str],
        change_type: str
    ) -> float:
        """
        Calculate regression risk based on affected files and change type.
        
        Args:
            affected_files: List of files that would be modified
            change_type: Type of change
        
        Returns:
            Risk score (0.0-1.0)
        """
        risk = 0.0
        
        # Risk factor 1: Number of files
        file_count_risk = min(len(affected_files) / 10.0, 1.0)
        risk += file_count_risk * 0.3
        
        # Risk factor 2: Core files
        core_files = ["__init__.py", "bootstrap.py", "main.py", "wiring.py"]
        core_affected = sum(1 for f in affected_files if any(c in f for c in core_files))
        risk += (core_affected / max(len(affected_files), 1)) * 0.4
        
        # Risk factor 3: Change type
        change_type_risk = {
            "refactor": 0.7,
            "new_feature": 0.4,
            "fix": 0.3,
            "enhancement": 0.5
        }
        risk += change_type_risk.get(change_type, 0.5) * 0.3
        
        return min(risk, 1.0)
    
    def _check_test_health(self, affected_files: List[str]) -> float:
        """
        Check test health for affected areas.
        
        Args:
            affected_files: List of files that would be modified
        
        Returns:
            Health score (0.0-1.0, higher is better)
        """
        # In production, this would check actual test results
        # For now, assume 0.8 health if no critical files affected
        
        critical_patterns = ["orchestrator", "enforcement", "validation"]
        has_critical = any(
            any(p in f for p in critical_patterns)
            for f in affected_files
        )
        
        return 0.6 if has_critical else 0.8
    
    def _check_duplicates(self, affected_files: List[str]) -> bool:
        """
        Check for duplicate implementations (CORE-035).
        
        Args:
            affected_files: List of files that would be modified
        
        Returns:
            True if duplicates detected, False otherwise
        """
        # In production, this would use LENS duplicate detection
        # For now, simple file name check
        
        base_names = [Path(f).stem for f in affected_files]
        return len(base_names) != len(set(base_names))
    
    def _calculate_complexity(
        self,
        affected_files: List[str],
        change_type: str
    ) -> float:
        """
        Calculate complexity score.
        
        Args:
            affected_files: List of files that would be modified
            change_type: Type of change
        
        Returns:
            Complexity score (0.0-1.0)
        """
        complexity = 0.0
        
        # Factor 1: File count
        complexity += min(len(affected_files) / 15.0, 1.0) * 0.5
        
        # Factor 2: Change type
        change_complexity = {
            "refactor": 0.8,
            "new_feature": 0.6,
            "fix": 0.3,
            "enhancement": 0.5
        }
        complexity += change_complexity.get(change_type, 0.5) * 0.5
        
        return min(complexity, 1.0)
    
    def _check_architecture_alignment(
        self,
        recommendation: str,
        affected_files: List[str],
        agent_name: str
    ) -> float:
        """
        Check alignment with existing architecture.
        
        Args:
            recommendation: Recommendation text
            affected_files: List of files that would be modified
            agent_name: Name of agent making recommendation
        
        Returns:
            Alignment score (0.0-1.0, higher is better)
        """
        # In production, this would:
        # 1. Query LENS for existing implementations
        # 2. Check wiring.yaml for integration points
        # 3. Verify compliance with CORE rules
        
        # For now, simple heuristic
        alignment = 0.7  # Base alignment
        
        # Check if recommendation mentions consulting architecture
        architecture_keywords = [
            "lens", "registry", "wiring", "existing",
            "current", "consult", "check", "review"
        ]
        
        if any(keyword in recommendation.lower() for keyword in architecture_keywords):
            alignment += 0.2
        
        return min(alignment, 1.0)
    
    def _calculate_roi(
        self,
        complexity: float,
        alignment: float,
        regression_risk: float
    ) -> float:
        """
        Calculate return on investment.
        
        Args:
            complexity: Complexity score
            alignment: Architecture alignment score
            regression_risk: Regression risk score
        
        Returns:
            ROI score (0.0-1.0, higher is better)
        """
        # ROI = Benefit / Cost
        # Benefit = alignment
        # Cost = complexity + regression_risk
        
        benefit = alignment
        cost = (complexity + regression_risk) / 2.0
        
        if cost == 0:
            return 1.0
        
        roi = benefit / (benefit + cost)
        return roi


# Global instance
_recommendation_gate = RecommendationGate()


def validate_agent_recommendation(
    recommendation: str,
    affected_files: List[str],
    change_type: str,
    agent_name: str
) -> Tuple[bool, RecommendationScore]:
    """
    Public API for recommendation validation.
    
    Args:
        recommendation: Recommendation text
        affected_files: List of files that would be modified
        change_type: Type of change
        agent_name: Name of agent making recommendation
    
    Returns:
        Tuple of (is_approved, score)
    """
    score = _recommendation_gate.validate_recommendation(
        recommendation,
        affected_files,
        change_type,
        agent_name
    )
    
    return (not score.is_blocked, score)
