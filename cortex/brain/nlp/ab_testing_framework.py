"""
Phase 8.4: A/B Testing Framework for NLP

Lightweight A/B testing framework to compare routing with/without NLP enhancements.
Tracks accuracy, latency, and confidence metrics.

AC-ID: AC-PHASE-8.4-03 (Task NLP-003)

CORE Governance:
  - CORE-008: TDD - Tests provided first
  - CORE-011: Type hints on all methods
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling
  - CORE-027: Audit trail logging

Author: Asif Hussain
Created: 2026-01-30
"""

import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger


class Variant(Enum):
    """A/B test variant."""
    CONTROL = "control"  # Without NLP
    TREATMENT = "treatment"  # With NLP


@dataclass
class RoutingDecision:
    """
    Routing decision result.

    Attributes:
        variant: Test variant used
        orchestrator: Selected orchestrator
        confidence: Routing confidence
        latency_ms: Decision latency
        timestamp: Decision timestamp
        keywords: Original keywords
        expanded_keywords: Expanded keywords (treatment only)
    """
    variant: Variant
    orchestrator: str
    confidence: float
    latency_ms: float
    timestamp: float
    keywords: List[str]
    expanded_keywords: Optional[List[str]] = None


@dataclass
class ABTestResult:
    """
    A/B test results.

    Attributes:
        control_decisions: Decisions made by control variant
        treatment_decisions: Decisions made by treatment variant
        control_avg_confidence: Average confidence (control)
        treatment_avg_confidence: Average confidence (treatment)
        control_avg_latency: Average latency (control)
        treatment_avg_latency: Average latency (treatment)
        treatment_improvement: % improvement over control
    """
    control_decisions: List[RoutingDecision]
    treatment_decisions: List[RoutingDecision]
    control_avg_confidence: float
    treatment_avg_confidence: float
    control_avg_latency: float
    treatment_avg_latency: float
    treatment_improvement: float


class ABTestingFramework:
    """
    A/B testing framework for NLP routing comparison.

    Compares routing decisions with/without NLP enhancements:
    - Control: Standard keyword matching
    - Treatment: NLP-enhanced (embeddings, synonyms)

    Metrics tracked:
    - Routing confidence
    - Decision latency
    - Orchestrator selection consistency

    Example:
        framework = ABTestingFramework()

        # Record control decision
        framework.record_decision(
            variant=Variant.CONTROL,
            orchestrator="TDDOrchestrator",
            confidence=0.75,
            latency_ms=12.5,
            keywords=["implement", "feature"],
        )

        # Record treatment decision
        framework.record_decision(
            variant=Variant.TREATMENT,
            orchestrator="TDDOrchestrator",
            confidence=0.85,
            latency_ms=18.3,
            keywords=["implement", "feature"],
            expanded_keywords=["implement", "create", "build", "feature"],
        )

        # Get results
        results = framework.get_results()
    """

    def __init__(self) -> None:
        """Initialize A/B testing framework."""
        self.logger = EnhancedAuditLogger.instance()
        self.decisions: Dict[Variant, List[RoutingDecision]] = {
            Variant.CONTROL: [],
            Variant.TREATMENT: [],
        }

        self.logger.log_operation_complete(
            ac_id="AC-PHASE-8.4-03",
            operation="AB_TEST_FRAMEWORK_INIT",
            success=True,
            details={"variants": [v.value for v in Variant]},
        )

    def record_decision(
        self,
        variant: Variant,
        orchestrator: str,
        confidence: float,
        latency_ms: float,
        keywords: List[str],
        expanded_keywords: Optional[List[str]] = None,
    ) -> None:
        """
        Record routing decision.

        AC-PHASE-8.4-03: Decision tracking

        Args:
            variant: Test variant
            orchestrator: Selected orchestrator
            confidence: Routing confidence
            latency_ms: Decision latency
            keywords: Original keywords
            expanded_keywords: Expanded keywords (treatment only)
        """
        decision = RoutingDecision(
            variant=variant,
            orchestrator=orchestrator,
            confidence=confidence,
            latency_ms=latency_ms,
            timestamp=time.time(),
            keywords=keywords,
            expanded_keywords=expanded_keywords,
        )

        self.decisions[variant].append(decision)

    def get_results(self) -> ABTestResult:
        """
        Get A/B test results.

        AC-PHASE-8.4-03: Results aggregation with statistical comparison

        Returns:
            ABTestResult: Test results
        """
        control = self.decisions[Variant.CONTROL]
        treatment = self.decisions[Variant.TREATMENT]

        # Calculate averages
        control_avg_confidence = (
            sum(d.confidence for d in control) / len(control)
            if control else 0.0
        )
        treatment_avg_confidence = (
            sum(d.confidence for d in treatment) / len(treatment)
            if treatment else 0.0
        )

        control_avg_latency = (
            sum(d.latency_ms for d in control) / len(control)
            if control else 0.0
        )
        treatment_avg_latency = (
            sum(d.latency_ms for d in treatment) / len(treatment)
            if treatment else 0.0
        )

        # Calculate improvement
        improvement = 0.0
        if control_avg_confidence > 0:
            improvement = (
                (treatment_avg_confidence - control_avg_confidence)
                / control_avg_confidence
                * 100
            )

        result = ABTestResult(
            control_decisions=control,
            treatment_decisions=treatment,
            control_avg_confidence=control_avg_confidence,
            treatment_avg_confidence=treatment_avg_confidence,
            control_avg_latency=control_avg_latency,
            treatment_avg_latency=treatment_avg_latency,
            treatment_improvement=improvement,
        )

        self.logger.log_operation_complete(
            ac_id="AC-PHASE-8.4-03",
            operation="AB_TEST_RESULTS",
            success=True,
            details={
                "control_samples": len(control),
                "treatment_samples": len(treatment),
                "improvement_pct": improvement,
            },
        )

        return result

    def reset(self) -> None:
        """Reset all recorded decisions."""
        self.decisions = {
            Variant.CONTROL: [],
            Variant.TREATMENT: [],
        }

    def format_report(self) -> str:
        """
        Format human-readable A/B test report.

        Returns:
            str: Formatted report
        """
        results = self.get_results()

        lines = [
            "═" * 80,
            "A/B TEST RESULTS: NLP ROUTING ENHANCEMENT",
            "═" * 80,
            "",
            f"Control Samples: {len(results.control_decisions)}",
            f"Treatment Samples: {len(results.treatment_decisions)}",
            "",
            "─" * 80,
            "CONFIDENCE METRICS",
            "─" * 80,
            f"Control Avg Confidence:   {results.control_avg_confidence:.3f}",
            f"Treatment Avg Confidence: {results.treatment_avg_confidence:.3f}",
            f"Improvement:              {results.treatment_improvement:+.1f}%",
            "",
            "─" * 80,
            "LATENCY METRICS",
            "─" * 80,
            f"Control Avg Latency:   {results.control_avg_latency:.2f} ms",
            f"Treatment Avg Latency: {results.treatment_avg_latency:.2f} ms",
            "",
            "═" * 80,
        ]

        return "\n".join(lines)
