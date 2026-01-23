"""Complexity score calculation engine."""

from typing import Any, Dict, Optional
from dataclasses import dataclass


@dataclass
class ComplexityScore:
    """Represents a calculated complexity score."""

    score: float
    category: str  # "simple", "moderate", "complex"
    factors: Optional[Dict[str, float]] = None
    
    def __post_init__(self) -> None:
        """Validate score is in valid range."""
        if not 0 <= self.score <= 100:
            raise ValueError(f"Score must be between 0-100, got {self.score}")


class ComplexityCalculator:
    """Calculates complexity scores for operations."""

    def __init__(self) -> None:
        """Initialize calculator with default thresholds."""
        self.simple_threshold = 30
        self.moderate_threshold = 70

    def calculate(
        self,
        operation_type: str,
        data_size_mb: float = 0,
        dependency_count: int = 0,
        parallel_tasks: int = 1,
        retry_count: int = 0,
        timeout_seconds: int = 300
    ) -> ComplexityScore:
        """Calculate complexity score for an operation.
        
        Args:
            operation_type: Type of operation
            data_size_mb: Data size in megabytes
            dependency_count: Number of dependencies
            parallel_tasks: Number of parallel tasks
            retry_count: Number of retries configured
            timeout_seconds: Operation timeout in seconds
            
        Returns:
            ComplexityScore object with score and category
        """
        from cortex.execution.complexity_metrics import ComplexityMetrics
        
        metrics = ComplexityMetrics()
        
        # Get all factors
        factors = metrics.calculate_factors(
            operation_type=operation_type,
            data_size_mb=data_size_mb,
            dependency_count=dependency_count,
            parallel_tasks=parallel_tasks,
            retry_count=retry_count
        )
        
        # Add timeout factor
        factors["timeout_factor"] = self._get_timeout_factor(timeout_seconds)
        
        # Calculate weighted score
        score = self._calculate_weighted_score(factors)
        
        # Clamp to 0-100
        score = max(0, min(100, score))
        
        # Determine category
        if score < self.simple_threshold:
            category = "simple"
        elif score < self.moderate_threshold:
            category = "moderate"
        else:
            category = "complex"
        
        return ComplexityScore(
            score=score,
            category=category,
            factors=factors
        )

    def _get_timeout_factor(self, timeout_seconds: int) -> float:
        """Get complexity factor for timeout configuration.
        
        Args:
            timeout_seconds: Timeout in seconds
            
        Returns:
            Complexity factor
        """
        if timeout_seconds < 10:
            return 5.0
        elif timeout_seconds < 60:
            return 2.0
        elif timeout_seconds < 300:
            return 1.0
        elif timeout_seconds < 3600:
            return 0.5
        else:
            return 3.0  # Very long timeouts increase complexity

    def _calculate_weighted_score(self, factors: Dict[str, float]) -> float:
        """Calculate weighted complexity score from factors.
        
        Args:
            factors: Dictionary of complexity factors
            
        Returns:
            Calculated complexity score (0-100)
        """
        # Weights for each factor
        weights = {
            "operation_type_factor": 0.40,
            "data_size_factor": 0.20,
            "dependency_factor": 0.20,
            "parallel_factor": 0.10,
            "retry_factor": 0.05,
            "timeout_factor": 0.05
        }
        
        # Factors are already scaled 0-100, normalize timeout
        max_timeout = 5
        
        normalized_factors = {
            "operation_type_factor": min(100, factors.get("operation_type_factor", 0)),
            "data_size_factor": min(100, factors.get("data_size_factor", 0)),
            "dependency_factor": min(100, factors.get("dependency_factor", 0)),
            "parallel_factor": min(100, factors.get("parallel_factor", 0)),
            "retry_factor": min(100, factors.get("retry_factor", 0)),
            "timeout_factor": min(100, (factors.get("timeout_factor", 0) / max_timeout) * 100)
        }
        
        weighted_score = 0.0
        for factor_name, weight in weights.items():
            factor_value = normalized_factors.get(factor_name, 0)
            weighted_score += factor_value * weight
        
        return weighted_score
