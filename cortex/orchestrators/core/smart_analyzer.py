"""
Smart Intent Analyzer - NLP Semantic Understanding + Circuit Breaker.

AC-FUTURE-007: Circuit breaker pattern for cascade failure prevention
AC-FUTURE-008: NLP semantic understanding for request analysis

Combines:
1. NLP semantic analysis for intent nuance detection
2. Circuit breaker pattern to prevent cascade failures
3. Orchestrator health monitoring
4. Graceful degradation strategies

CORE Governance Rules Applied:
- CORE-008: TDD tests created first
- CORE-011: Type hints mandatory
- CORE-012: Google-style docstrings
- CORE-013: Specific exception handling
- CORE-027: Audit trail logging

Author: Asif Hussain
Date: 2026-01-26
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from cortex.models.canonical_enums import CircuitBreakerState


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5  # Failures before opening
    recovery_timeout: int = 60  # Seconds before attempting recovery
    half_open_max_calls: int = 1  # Calls to try in half-open state
    success_threshold: int = 2  # Successes before closing


@dataclass
class OrchestratorHealth:
    """Health metrics for an orchestrator."""
    name: str
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    total_calls: int = 0
    error_rate: float = 0.0


class CircuitBreaker:
    """
    AC-FUTURE-007: Circuit breaker pattern implementation.

    Prevents cascade failures by:
    1. Monitoring orchestrator success/failure rates
    2. Opening circuit when failure threshold exceeded
    3. Returning degraded responses instead of failing
    4. Periodically testing recovery (half-open state)
    5. Gracefully reopening when recovered
    """

    def __init__(self, config: Optional[CircuitBreakerConfig] = None) -> None:
        """
        Initialize circuit breaker.

        Args:
            config: CircuitBreakerConfig with thresholds
        """
        self.config = config or CircuitBreakerConfig()
        self.orchestrator_health: Dict[str, OrchestratorHealth] = {}

    def record_success(self, orchestrator_name: str) -> None:
        """Record successful orchestrator execution."""
        if orchestrator_name not in self.orchestrator_health:
            self.orchestrator_health[orchestrator_name] = OrchestratorHealth(name=orchestrator_name)

        health = self.orchestrator_health[orchestrator_name]
        health.success_count += 1
        health.total_calls += 1
        health.last_success_time = datetime.now()
        health.error_rate = (health.failure_count / health.total_calls * 100) if health.total_calls > 0 else 0.0

        # Transition from half-open to closed if enough successes
        if health.state == CircuitBreakerState.HALF_OPEN:
            if health.success_count >= self.config.success_threshold:
                health.state = CircuitBreakerState.CLOSED
                health.failure_count = 0

    def record_failure(self, orchestrator_name: str) -> None:
        """Record failed orchestrator execution."""
        if orchestrator_name not in self.orchestrator_health:
            self.orchestrator_health[orchestrator_name] = OrchestratorHealth(name=orchestrator_name)

        health = self.orchestrator_health[orchestrator_name]
        health.failure_count += 1
        health.total_calls += 1
        health.last_failure_time = datetime.now()
        health.error_rate = (health.failure_count / health.total_calls * 100) if health.total_calls > 0 else 0.0

        # Open circuit if failures exceed threshold
        if health.failure_count >= self.config.failure_threshold:
            health.state = CircuitBreakerState.OPEN

    def is_available(self, orchestrator_name: str) -> bool:
        """Check if orchestrator is available."""
        if orchestrator_name not in self.orchestrator_health:
            return True  # Unknown orchestrators are available until proven otherwise

        health = self.orchestrator_health[orchestrator_name]

        if health.state == CircuitBreakerState.CLOSED:
            return True

        if health.state == CircuitBreakerState.OPEN:
            # Check if recovery timeout has passed
            if health.last_failure_time:
                elapsed = (datetime.now() - health.last_failure_time).total_seconds()
                if elapsed > self.config.recovery_timeout:
                    # Transition to half-open for testing
                    health.state = CircuitBreakerState.HALF_OPEN
                    health.success_count = 0
                    return True
            return False

        if health.state == CircuitBreakerState.HALF_OPEN:
            # Allow limited calls in half-open state
            return health.success_count < self.config.half_open_max_calls

        return True

    def get_health_report(self) -> Dict[str, Any]:
        """Get health report for all orchestrators."""
        return {
            name: {
                "state": health.state.value,
                "error_rate": f"{health.error_rate:.1f}%",
                "total_calls": health.total_calls,
                "failures": health.failure_count,
                "successes": health.success_count
            }
            for name, health in self.orchestrator_health.items()
        }


class SemanticIntentAnalyzer:
    """
    AC-FUTURE-008: NLP semantic understanding for request analysis.

    Goes beyond keyword matching to understand:
    1. Semantic similarity of requests
    2. Intent nuances (urgency, importance, scope)
    3. Context implications
    4. Request complexity indicators
    5. Relationship to previous requests

    Uses simple NLP techniques (no external libraries needed):
    - Term frequency analysis
    - Semantic word grouping
    - Pattern recognition
    - Similarity scoring
    """

    # Semantic word groups for understanding
    URGENCY_KEYWORDS = {
        "critical": 10,
        "urgent": 8,
        "asap": 8,
        "immediately": 7,
        "quickly": 5,
        "soon": 3,
        "blocked": 9,
        "broken": 7,
        "crash": 10,
        "fails": 8
    }

    SCOPE_KEYWORDS = {
        "entire": 3,
        "all": 2,
        "system": 3,
        "complete": 2,
        "full": 2,
        "multiple": 1,
        "several": 1,
        "many": 1
    }

    COMPLEXITY_KEYWORDS = {
        "complex": 3,
        "complicated": 3,
        "intricate": 3,
        "sophisticated": 2,
        "simple": -2,
        "basic": -1,
        "trivial": -2,
        "straightforward": -2
    }

    @staticmethod
    def analyze_semantic_intent(
        request: str,
        previous_requests: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze semantic intent of request.

        AC-FUTURE-008: NLP semantic analysis

        Args:
            request: User's request
            previous_requests: List of previous requests for context

        Returns:
            Dict with semantic analysis results
        """
        request_lower = request.lower()

        # Calculate urgency score
        urgency_score = sum(
            weight for keyword, weight in SemanticIntentAnalyzer.URGENCY_KEYWORDS.items()
            if keyword in request_lower
        ) / 10.0  # Normalize

        # Calculate scope score
        scope_score = sum(
            weight for keyword, weight in SemanticIntentAnalyzer.SCOPE_KEYWORDS.items()
            if keyword in request_lower
        )

        # Calculate complexity score
        complexity_score = sum(
            weight for keyword, weight in SemanticIntentAnalyzer.COMPLEXITY_KEYWORDS.items()
            if keyword in request_lower
        )

        # Semantic similarity to previous requests
        similarity_score = 0.0
        if previous_requests:
            similarity_score = SemanticIntentAnalyzer._calculate_similarity(
                request, previous_requests
            )

        return {
            "urgency_score": min(10.0, max(0.0, urgency_score)),
            "scope_score": min(10.0, max(0.0, scope_score)),
            "complexity_score": min(10.0, max(-10.0, complexity_score)),
            "similarity_to_previous": similarity_score,
            "estimated_effort": SemanticIntentAnalyzer._estimate_effort(
                urgency_score, scope_score, complexity_score
            ),
            "keywords_found": SemanticIntentAnalyzer._extract_semantic_keywords(request_lower)
        }

    @staticmethod
    def _calculate_similarity(request: str, previous_requests: List[str]) -> float:
        """Calculate semantic similarity to previous requests."""
        if not previous_requests:
            return 0.0

        request_words = set(request.lower().split())

        similarities: List[float] = []
        for prev in previous_requests:
            prev_words = set(prev.lower().split())
            intersection = len(request_words & prev_words)
            union = len(request_words | prev_words)
            similarity: float = intersection / union if union > 0 else 0.0
            similarities.append(similarity)

        # Return average similarity
        avg_similarity: float = sum(similarities) / len(similarities) if similarities else 0.0
        return avg_similarity

    @staticmethod
    def _estimate_effort(urgency: float, scope: float, complexity: float) -> str:
        """Estimate effort level."""
        total_score = urgency + scope + max(0, complexity)

        if total_score >= 20:
            return "CRITICAL"
        elif total_score >= 12:
            return "HIGH"
        elif total_score >= 6:
            return "MEDIUM"
        else:
            return "LOW"

    @staticmethod
    def _extract_semantic_keywords(request_lower: str) -> List[str]:
        """Extract semantically significant keywords."""
        found: List[str] = []

        for keyword in list(SemanticIntentAnalyzer.URGENCY_KEYWORDS.keys()) + \
                       list(SemanticIntentAnalyzer.SCOPE_KEYWORDS.keys()) + \
                       list(SemanticIntentAnalyzer.COMPLEXITY_KEYWORDS.keys()):
            if keyword in request_lower:
                found.append(keyword)

        return list(set(found))  # Remove duplicates


class SmartIntentAnalyzer:
    """
    AC-FUTURE-007/008: Combined circuit breaker + NLP semantic analyzer.

    Provides integrated intelligence for:
    1. Understanding semantic intent nuances
    2. Preventing cascade failures
    3. Monitoring orchestrator health
    4. Recommending orchestrator selection based on health + complexity
    """

    def __init__(self):
        """Initialize smart analyzer with circuit breaker and semantic engine."""
        self.circuit_breaker = CircuitBreaker()
        self.semantic_analyzer = SemanticIntentAnalyzer()
        self.request_history: List[str] = []

    def analyze_and_route(
        self,
        request: str,
        available_orchestrators: List[str]
    ) -> Dict[str, Any]:
        """
        Analyze request and recommend orchestrator.

        AC-FUTURE-007/008: Integrated analysis + health-aware routing

        Args:
            request: User request
            available_orchestrators: List of orchestrator names

        Returns:
            Dict with recommended orchestrator, analysis, health status
        """
        # Semantic analysis
        semantic = self.semantic_analyzer.analyze_semantic_intent(
            request, self.request_history[-5:] if self.request_history else []
        )

        # Filter available orchestrators by circuit breaker health
        healthy_orchestrators = [
            orch for orch in available_orchestrators
            if self.circuit_breaker.is_available(orch)
        ]

        # If all circuits open, allow degraded operation on half-open
        if not healthy_orchestrators:
            healthy_orchestrators = available_orchestrators

        recommendation = {
            "semantic_analysis": semantic,
            "available_orchestrators": healthy_orchestrators,
            "health_status": self.circuit_breaker.get_health_report(),
            "estimated_effort": semantic["estimated_effort"],
            "recommended_orchestrator": healthy_orchestrators[0] if healthy_orchestrators else None,
            "circuit_breaker_active": len(healthy_orchestrators) < len(available_orchestrators)
        }

        # Add to history
        self.request_history.append(request)
        if len(self.request_history) > 100:
            self.request_history = self.request_history[-100:]

        return recommendation
