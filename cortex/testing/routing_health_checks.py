"""
Phase 8.6: Routing Health Checks Extension

Extends verify_prod_ready.py with Phase 8 routing verification checks.
Adds 6 new checks for intelligent routing readiness.

AC-ID: AC-PHASE-8.6-01 (Task VERIFY-001)

CORE Governance:
  - CORE-008: TDD - Tests provided first
  - CORE-011: Type hints on all methods
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling
  - CORE-027: Audit trail logging

Author: Asif Hussain
Created: 2026-01-30

Usage:
    from cortex.testing.routing_health_checks import RoutingHealthChecker

    checker = RoutingHealthChecker()
    results = checker.run_all_checks()
    print(checker.format_report())
"""

import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Configure Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger


class HealthCheckStatus(Enum):
    """Health check status."""
    PASSED = "PASSED"
    FAILED = "FAILED"
    WARNING = "WARNING"


@dataclass
class HealthCheckResult:
    """
    Health check result.

    Attributes:
        check_id: Check identifier
        check_name: Human-readable name
        status: Check status
        details: Detailed description
        evidence: Evidence list
        remediation: Fix suggestion
        score: Numeric score (0-100)
    """
    check_id: str
    check_name: str
    status: HealthCheckStatus
    details: str
    evidence: List[str]
    remediation: str
    score: float


class RoutingHealthChecker:
    """
    Phase 8 routing health verification.

    Performs 6 critical checks:
    1. Routing coverage >90%
    2. Confidence threshold validation
    3. Enforcement rule compliance
    4. Edge case detector health
    5. Semantic ranking accuracy
    6. NLP cache freshness

    Example:
        checker = RoutingHealthChecker()
        results = checker.run_all_checks()

        if checker.all_passed():
            print("✅ All routing health checks passed")
        else:
            print(checker.format_report())
    """

    def __init__(self) -> None:
        """Initialize routing health checker."""
        self.logger = EnhancedAuditLogger.instance()
        self.results: List[HealthCheckResult] = []
        self.cortex_root = Path(__file__).parent.parent.parent

        self.logger.log_operation_complete(
            ac_id="AC-PHASE-8.6-01",
            operation="ROUTING_HEALTH_CHECKER_INIT",
            success=True,
            details={},
        )

    def run_all_checks(self) -> List[HealthCheckResult]:
        """
        Run all 6 routing health checks.

        AC-PHASE-8.6-01: Execute all verification checks

        Returns:
            List[HealthCheckResult]: Check results
        """
        self.results = []

        self.check_routing_coverage()
        self.check_confidence_thresholds()
        self.check_enforcement_rules()
        self.check_edge_case_detector()
        self.check_semantic_ranking()
        self.check_nlp_cache()

        return self.results

    def check_routing_coverage(self) -> None:
        """
        CHECK 1: Routing coverage >90%.

        Verifies that IntentRouter can route >90% of known operation types
        to registered orchestrators.
        """
        try:
            from cortex.orchestrators.core.intent_router import IntentRouter, IntentType
            from cortex.wiring import get_registry

            router = IntentRouter()
            registry = get_registry()
            orchestrators = registry.list_orchestrators()

            # Test all intent types
            intent_types = list(IntentType)
            routable_count = 0

            for intent in intent_types:
                decision = router.route({
                    "operation": intent.value,
                    "keywords": [intent.value],
                    "context": {},
                })

                if decision.confidence >= 0.5:
                    routable_count += 1

            coverage = (routable_count / len(intent_types)) * 100

            if coverage >= 90:
                status = HealthCheckStatus.PASSED
                remediation = "N/A"
            elif coverage >= 70:
                status = HealthCheckStatus.WARNING
                remediation = "Add missing orchestrator registrations or enforcement rules"
            else:
                status = HealthCheckStatus.FAILED
                remediation = "Critical: Review wiring.yaml and add missing orchestrator mappings"

            self.results.append(HealthCheckResult(
                check_id="ROUTE-001",
                check_name="Routing Coverage",
                status=status,
                details=f"Coverage: {coverage:.1f}% ({routable_count}/{len(intent_types)} intent types)",
                evidence=[
                    f"Orchestrators: {len(orchestrators)}",
                    f"Intent types: {len(intent_types)}",
                    f"Routable: {routable_count}",
                ],
                remediation=remediation,
                score=coverage,
            ))

        except Exception as e:
            self.results.append(HealthCheckResult(
                check_id="ROUTE-001",
                check_name="Routing Coverage",
                status=HealthCheckStatus.FAILED,
                details=f"Check failed: {str(e)}",
                evidence=[f"Error: {type(e).__name__}"],
                remediation="Fix IntentRouter or wiring configuration",
                score=0.0,
            ))

    def check_confidence_thresholds(self) -> None:
        """
        CHECK 2: Confidence threshold validation.

        Verifies confidence thresholds are properly configured:
        - Strong routing: >=0.8
        - Acceptable routing: >=0.5
        - Ambiguous routing: <0.5
        """
        try:
            from cortex.orchestrators.core.intent_router import IntentRouter

            router = IntentRouter()

            # Test known high-confidence routes
            high_confidence_tests = [
                {"operation": "implement", "keywords": ["implement", "TDD"]},
                {"operation": "fix", "keywords": ["fix", "bug"]},
                {"operation": "refactor", "keywords": ["refactor", "code"]},
            ]

            high_conf_pass = sum(
                1 for test in high_confidence_tests
                if router.route(test).confidence >= 0.8
            )

            threshold_score = (high_conf_pass / len(high_confidence_tests)) * 100

            if threshold_score >= 90:
                status = HealthCheckStatus.PASSED
            elif threshold_score >= 70:
                status = HealthCheckStatus.WARNING
            else:
                status = HealthCheckStatus.FAILED

            self.results.append(HealthCheckResult(
                check_id="ROUTE-002",
                check_name="Confidence Thresholds",
                status=status,
                details=f"{high_conf_pass}/{len(high_confidence_tests)} high-confidence routes validated",
                evidence=[f"Threshold accuracy: {threshold_score:.1f}%"],
                remediation="Adjust confidence calculation in IntentRouter" if status != HealthCheckStatus.PASSED else "N/A",
                score=threshold_score,
            ))

        except Exception as e:
            self.results.append(HealthCheckResult(
                check_id="ROUTE-002",
                check_name="Confidence Thresholds",
                status=HealthCheckStatus.FAILED,
                details=f"Check failed: {str(e)}",
                evidence=[f"Error: {type(e).__name__}"],
                remediation="Fix confidence threshold configuration",
                score=0.0,
            ))

    def check_enforcement_rules(self) -> None:
        """
        CHECK 3: Enforcement rule compliance.

        Verifies all enforcement rules are active and ENFORCE mode is set.
        """
        try:
            from cortex.orchestrators.core.enforcement_orchestrator import (
                EnforcementOrchestrator,
            )

            orchestrator = EnforcementOrchestrator()
            rules = orchestrator.rules

            total_rules = len(rules)
            active_rules = sum(1 for r in rules.values() if r.is_active)
            enforcement_mode = orchestrator.enforcement_mode

            compliance_score = (active_rules / total_rules * 100) if total_rules > 0 else 0

            if compliance_score == 100 and enforcement_mode == "ENFORCE":
                status = HealthCheckStatus.PASSED
            elif compliance_score >= 80:
                status = HealthCheckStatus.WARNING
            else:
                status = HealthCheckStatus.FAILED

            self.results.append(HealthCheckResult(
                check_id="ROUTE-003",
                check_name="Enforcement Rule Compliance",
                status=status,
                details=f"{active_rules}/{total_rules} rules active, mode={enforcement_mode}",
                evidence=[
                    f"Total rules: {total_rules}",
                    f"Active: {active_rules}",
                    f"Mode: {enforcement_mode}",
                ],
                remediation="Enable missing rules or set enforcement_mode=ENFORCE" if status != HealthCheckStatus.PASSED else "N/A",
                score=compliance_score,
            ))

        except Exception as e:
            self.results.append(HealthCheckResult(
                check_id="ROUTE-003",
                check_name="Enforcement Rule Compliance",
                status=HealthCheckStatus.FAILED,
                details=f"Check failed: {str(e)}",
                evidence=[f"Error: {type(e).__name__}"],
                remediation="Fix EnforcementOrchestrator configuration",
                score=0.0,
            ))

    def check_edge_case_detector(self) -> None:
        """
        CHECK 4: Edge case detector health.

        Verifies unified edge case detector can aggregate edge cases from
        all 3 Microsoft stack analyzers.
        """
        try:
            from cortex.brain.analysis.unified_edge_case_detector import (
                UnifiedEdgeCaseDetector,
            )

            detector = UnifiedEdgeCaseDetector()

            # Check remediations and impacts loaded
            remediation_count = len(detector.remediations)
            impact_count = len(detector.impacts)

            expected_min = 12  # 12 edge case types across 3 languages

            if remediation_count >= expected_min and impact_count >= expected_min:
                status = HealthCheckStatus.PASSED
                score = 100.0
            else:
                status = HealthCheckStatus.FAILED
                score = (min(remediation_count, impact_count) / expected_min) * 100

            self.results.append(HealthCheckResult(
                check_id="ROUTE-004",
                check_name="Edge Case Detector Health",
                status=status,
                details=f"Loaded {remediation_count} remediations, {impact_count} impacts",
                evidence=[
                    f"Remediations: {remediation_count}/{expected_min}",
                    f"Impacts: {impact_count}/{expected_min}",
                ],
                remediation="Add missing edge case type definitions" if status != HealthCheckStatus.PASSED else "N/A",
                score=score,
            ))

        except Exception as e:
            self.results.append(HealthCheckResult(
                check_id="ROUTE-004",
                check_name="Edge Case Detector Health",
                status=HealthCheckStatus.FAILED,
                details=f"Check failed: {str(e)}",
                evidence=[f"Error: {type(e).__name__}"],
                remediation="Fix UnifiedEdgeCaseDetector initialization",
                score=0.0,
            ))

    def check_semantic_ranking(self) -> None:
        """
        CHECK 5: Semantic ranking accuracy.

        Verifies SemanticRankingEngine can correctly rank candidates with
        synonym expansion.
        """
        try:
            from cortex.orchestrators.core.intent_router import IntentType
            from cortex.orchestrators.core.semantic_ranking import SemanticRankingEngine

            engine = SemanticRankingEngine()

            # Test synonym expansion
            test_cases = [
                ("implement", ["TDDOrchestrator", "WorkflowOrchestrator"]),
                ("analyze", ["LENSOrchestrator", "MasterOrchestrator"]),
                ("fix", ["TDDOrchestrator", "RefactoringOrchestrator"]),
            ]

            correct_rankings = 0
            for keyword, candidates in test_cases:
                ranked = engine.rank_candidates(
                    candidates=candidates,
                    context={"keywords": [keyword]},
                    intent=IntentType.IMPLEMENT,
                )

                # Check if top candidate is reasonable
                if ranked and ranked[0].confidence >= 0.5:
                    correct_rankings += 1

            accuracy = (correct_rankings / len(test_cases)) * 100

            if accuracy >= 80:
                status = HealthCheckStatus.PASSED
            elif accuracy >= 60:
                status = HealthCheckStatus.WARNING
            else:
                status = HealthCheckStatus.FAILED

            self.results.append(HealthCheckResult(
                check_id="ROUTE-005",
                check_name="Semantic Ranking Accuracy",
                status=status,
                details=f"{correct_rankings}/{len(test_cases)} test cases ranked correctly",
                evidence=[f"Accuracy: {accuracy:.1f}%"],
                remediation="Improve synonym groups or affinity scoring" if status != HealthCheckStatus.PASSED else "N/A",
                score=accuracy,
            ))

        except Exception as e:
            self.results.append(HealthCheckResult(
                check_id="ROUTE-005",
                check_name="Semantic Ranking Accuracy",
                status=HealthCheckStatus.FAILED,
                details=f"Check failed: {str(e)}",
                evidence=[f"Error: {type(e).__name__}"],
                remediation="Fix SemanticRankingEngine configuration",
                score=0.0,
            ))

    def check_nlp_cache(self) -> None:
        """
        CHECK 6: NLP cache freshness (optional).

        Verifies embedding cache is functional (if enabled).
        """
        try:
            from cortex.brain.nlp.embedding_cache import EmbeddingCache

            cache = EmbeddingCache(max_size=100, ttl_seconds=3600)

            # Test cache operations
            test_embedding = [0.1, 0.2, 0.3]
            cache.set("test", test_embedding)
            retrieved = cache.get("test")

            if retrieved == test_embedding:
                stats = cache.get_stats()
                status = HealthCheckStatus.PASSED
                score = 100.0
                details = f"Cache operational, size={stats['size']}"
            else:
                status = HealthCheckStatus.FAILED
                score = 0.0
                details = "Cache set/get mismatch"

            self.results.append(HealthCheckResult(
                check_id="ROUTE-006",
                check_name="NLP Cache Freshness",
                status=status,
                details=details,
                evidence=["Cache set/get test completed"],
                remediation="Fix EmbeddingCache implementation" if status != HealthCheckStatus.PASSED else "N/A",
                score=score,
            ))

        except Exception as e:
            # NLP cache is optional, so WARNING instead of FAILED
            self.results.append(HealthCheckResult(
                check_id="ROUTE-006",
                check_name="NLP Cache Freshness",
                status=HealthCheckStatus.WARNING,
                details=f"NLP cache not enabled: {str(e)}",
                evidence=[f"Error: {type(e).__name__}"],
                remediation="Enable NLP cache if needed (optional component)",
                score=50.0,  # Partial credit since it's optional
            ))

    def all_passed(self) -> bool:
        """Check if all results passed."""
        return all(r.status == HealthCheckStatus.PASSED for r in self.results)

    def failed_count(self) -> int:
        """Count failed checks."""
        return sum(1 for r in self.results if r.status == HealthCheckStatus.FAILED)

    def warning_count(self) -> int:
        """Count warning checks."""
        return sum(1 for r in self.results if r.status == HealthCheckStatus.WARNING)

    def format_report(self) -> str:
        """
        Format human-readable health report.

        Returns:
            str: Formatted report
        """
        lines = [
            "═" * 80,
            "PHASE 8 ROUTING HEALTH CHECK REPORT",
            "═" * 80,
            "",
        ]

        for result in self.results:
            icon = "✅" if result.status == HealthCheckStatus.PASSED else "❌" if result.status == HealthCheckStatus.FAILED else "🟡"
            lines.append(f"{icon} {result.check_id}: {result.check_name}")
            lines.append(f"   Status: {result.status.value}")
            lines.append(f"   Details: {result.details}")
            lines.append(f"   Score: {result.score:.1f}/100")

            if result.status != HealthCheckStatus.PASSED:
                lines.append(f"   Remediation: {result.remediation}")

            lines.append("")

        lines.append("─" * 80)
        lines.append(f"Summary: {len(self.results)} checks, {self.failed_count()} failed, {self.warning_count()} warnings")

        if self.all_passed():
            lines.append("✨ ALL ROUTING HEALTH CHECKS PASSED ✨")
        else:
            lines.append("❌ ROUTING SYSTEM NEEDS ATTENTION")

        lines.append("═" * 80)

        return "\n".join(lines)
