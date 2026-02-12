"""Complexity gate for evaluating operation acceptability."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from cortex.execution.complexity_calculator import ComplexityScore


@dataclass
class GateDecision:
    """Decision from the complexity gate."""

    allowed: bool
    action: str  # "allow", "warn", "block"
    complexity_level: str  # "simple", "moderate", "complex"
    reason: str
    recommendations: Optional[List[str]] = None


class ComplexityGate:
    """Gates operations based on complexity thresholds and resources."""

    def __init__(
        self,
        simple_threshold: float = 30,
        moderate_threshold: float = 70,
        allow_complex: bool = False,
        warn_on_moderate: bool = True
    ) -> None:
        """Initialize complexity gate.

        Args:
            simple_threshold: Score threshold for simple operations
            moderate_threshold: Score threshold for complex operations
            allow_complex: Whether to allow complex operations by default
            warn_on_moderate: Whether to warn on moderate complexity
        """
        self.simple_threshold = simple_threshold
        self.moderate_threshold = moderate_threshold
        self.allow_complex = allow_complex
        self.warn_on_moderate = warn_on_moderate

    def evaluate(
        self,
        score: "ComplexityScore",
        available_resources: Optional[int] = None,
        allow_override: bool = False
    ) -> GateDecision:
        """Evaluate if operation should be allowed.

        Args:
            score: ComplexityScore to evaluate
            available_resources: Available resources (optional)
            allow_override: Whether to allow override of block decision

        Returns:
            GateDecision with allow/block/warn and reasoning
        """
        from cortex.execution.complexity_calculator import ComplexityScore

        complexity_level = score.category
        complexity_score = score.score

        recommendations = []

        # Determine action based on complexity level
        if complexity_score < self.simple_threshold:
            return GateDecision(
                allowed=True,
                action="allow",
                complexity_level="simple",
                reason=f"Operation complexity {complexity_score:.1f} is below simple threshold {self.simple_threshold}"
            )

        elif complexity_score < self.moderate_threshold:
            action = "warn" if self.warn_on_moderate else "allow"
            allowed = True
            reason = f"Operation complexity {complexity_score:.1f} is moderate (threshold: {self.moderate_threshold})"

            recommendations.append("Consider breaking into smaller operations")
            recommendations.append("Monitor resource usage during execution")

            return GateDecision(
                allowed=allowed,
                action=action,
                complexity_level="moderate",
                reason=reason,
                recommendations=recommendations
            )

        else:  # Complex operation
            if self.allow_complex or allow_override:
                allowed = True
                action = "allow"
                reason = f"Complex operation (score: {complexity_score:.1f}) allowed with override"
            else:
                allowed = False
                action = "block"
                reason = f"Complex operation (score: {complexity_score:.1f}) blocked. Complexity exceeds threshold {self.moderate_threshold}"

            recommendations.append("Reduce operation scope or break into smaller tasks")
            recommendations.append("Increase retry thresholds if fault tolerance needed")
            recommendations.append("Ensure sufficient resources are available")

            return GateDecision(
                allowed=allowed,
                action=action,
                complexity_level="complex",
                reason=reason,
                recommendations=recommendations
            )


class ComplexityReporter:
    """Generates complexity analysis reports."""

    def distribution_report(self, scores: List["ComplexityScore"]) -> Dict[str, Any]:
        """Generate complexity distribution report.

        Args:
            scores: List of ComplexityScore objects

        Returns:
            Report dictionary with distribution statistics
        """
        simple_count = sum(1 for s in scores if s.category == "simple")
        moderate_count = sum(1 for s in scores if s.category == "moderate")
        complex_count = sum(1 for s in scores if s.category == "complex")

        total = len(scores)
        avg_score = sum(s.score for s in scores) / total if total > 0 else 0

        return {
            "total_operations": total,
            "simple_count": simple_count,
            "moderate_count": moderate_count,
            "complex_count": complex_count,
            "average_complexity": avg_score,
            "simple_percentage": (simple_count / total * 100) if total > 0 else 0,
            "moderate_percentage": (moderate_count / total * 100) if total > 0 else 0,
            "complex_percentage": (complex_count / total * 100) if total > 0 else 0
        }

    def identify_high_complexity(
        self,
        scores: List["ComplexityScore"],
        threshold: float = 75
    ) -> List["ComplexityScore"]:
        """Identify operations exceeding complexity threshold.

        Args:
            scores: List of ComplexityScore objects
            threshold: Complexity threshold

        Returns:
            List of high-complexity scores
        """
        return [s for s in scores if s.score >= threshold]

    def average_complexity(self, scores: List["ComplexityScore"]) -> float:
        """Calculate average complexity.

        Args:
            scores: List of ComplexityScore objects

        Returns:
            Average complexity score
        """
        if not scores:
            return 0.0
        return sum(s.score for s in scores) / len(scores)


class RuleEngine:
    """Manages complexity business rules."""

    def __init__(self) -> None:
        """Initialize rule engine with default rules."""
        self.rules: List[Dict[str, Any]] = self._initialize_default_rules()

    def _initialize_default_rules(self) -> List[Dict[str, Any]]:
        """Initialize default complexity rules.

        Returns:
            List of default business rules
        """
        return [
            {
                "name": "critical_operations",
                "condition": "operation_type == 'critical'",
                "adjustment": -10,
                "description": "Critical operations receive priority"
            },
            {
                "name": "monitoring_operations",
                "condition": "operation_type == 'monitoring'",
                "adjustment": 0,
                "description": "Monitoring operations have standard complexity"
            },
            {
                "name": "read_operations",
                "condition": "operation_type == 'read'",
                "adjustment": -5,
                "description": "Read operations are simpler"
            },
            {
                "name": "large_batch_operations",
                "condition": "data_size_mb > 1000",
                "adjustment": 15,
                "description": "Large batch operations increase complexity"
            }
        ]

    def load_rules(self) -> List[Dict[str, Any]]:
        """Load all complexity rules.

        Returns:
            List of business rules
        """
        return self.rules

    def add_rule(self, rule: Dict[str, Any]) -> None:
        """Add a custom business rule.

        Args:
            rule: Rule dictionary with name, condition, adjustment
        """
        if "name" not in rule or "condition" not in rule or "adjustment" not in rule:
            raise ValueError("Rule must have name, condition, and adjustment")

        self.rules.append(rule)

    def get_rules(self) -> List[Dict[str, Any]]:
        """Get all rules.

        Returns:
            List of rules
        """
        return self.rules

    def apply_adjustments(
        self,
        base_score: float,
        operation_type: str = "",
        data_size_mb: float = 0
    ) -> float:
        """Apply business rule adjustments to complexity score.

        Args:
            base_score: Base complexity score
            operation_type: Type of operation
            data_size_mb: Data size in MB

        Returns:
            Adjusted complexity score
        """
        adjusted_score = base_score

        # Apply adjustments based on rules
        if operation_type == "critical":
            adjusted_score -= 10
        elif operation_type == "read":
            adjusted_score -= 5

        if data_size_mb > 1000:
            adjusted_score += 15

        # Clamp between 0-100
        return max(0, min(100, adjusted_score))
