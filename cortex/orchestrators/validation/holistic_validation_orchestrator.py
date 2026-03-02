"""
Holistic Validation Orchestrator

Pre-implementation validation gate for IMPLEMENT/FIX/REFACTOR intents.
Coordinates checklist validation, challenge generation, and confidence scoring.

Author: Asif Hussain
Authority: PHASE-48-IMPLEMENTATION-PLAN.yaml
Priority: P0-CRITICAL

Flow:
1. Run pre-implementation checklist (12 categories)
2. Generate 3 alternative approaches
3. Calculate confidence score (0-1.0)
4. Gate execution if confidence < 0.7

AC-ID: AC-PHASE48-S1-IMPL-002
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin
from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin  # Phase 94d


logger = logging.getLogger(__name__)


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class ValidationResult:
    """Result of holistic validation with gating decision.

    Attributes:
        passed: True if validation passed (confidence >= 0.7)
        confidence_score: Overall confidence score (0.0-1.0)
        checklist_result: Results from 12-category pre-implementation checklist
        challenges: List of 3 alternative approaches with pros/cons
        explanation: Human-readable explanation of validation decision
        timestamp: ISO 8601 timestamp of validation
    """
    passed: bool
    confidence_score: float
    checklist_result: Dict[str, Any]
    challenges: List[Dict[str, Any]]
    explanation: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self):
        """Validate score range."""
        if not 0.0 <= self.confidence_score <= 1.0:
            raise ValueError(f"Confidence score must be 0-1, got {self.confidence_score}")


# ============================================================================
# HOLISTIC VALIDATION ORCHESTRATOR
# ============================================================================

class HolisticValidationOrchestrator(OrchestratorProtocolMixin, WorkflowEnforcementMixin):
    """Orchestrate pre-implementation validation gate.

    Coordinates:
    - PreImplementationChecklist (12-category systematic review)
    - ChallengeEngine (3 alternative approaches)
    - ConfidenceScorer (multi-factor scoring)

    Gating Logic:
    - Confidence >= 0.7: PASS (allow execution)
    - Confidence < 0.7: BLOCK (require revision)

    Example:
        >>> orchestrator = HolisticValidationOrchestrator()
        >>> result = orchestrator.validate(
        ...     request="Add user authentication with JWT",
        ...     intent="IMPLEMENT",
        ...     context={"existing_code": "..."}
        ... )
        >>> if result.passed:
        ...     proceed_with_implementation()
        ... else:
        ...     display_challenges_and_block()
    """

    # Phase 94d — must remain False: this IS the CORE-048 pre-execution gate;
    # self-gating would create a circular dependency through WorkflowGateway.
    PHASE90_GATEWAY_EXEMPT: bool = True

    def __init__(
        self,
        challenge_engine: Optional[Any] = None,
        confidence_scorer: Optional[Any] = None,
        checklist: Optional[Any] = None,
        confidence_threshold: float = 0.7
    ) -> None:
        """Initialize validation orchestrator.

        Args:
            challenge_engine: ChallengeEngine instance (optional, will create if None)
            confidence_scorer: ConfidenceScorer instance (optional, will create if None)
            checklist: PreImplementationChecklist instance (optional, will create if None)
            confidence_threshold: Minimum confidence score to pass (default: 0.7)
        """
        # Lazy imports to avoid circular dependencies
        from cortex.orchestrators.validation.pre_implementation_checklist import PreImplementationChecklist

        self.challenge_engine = challenge_engine
        self.confidence_scorer = confidence_scorer
        self.checklist = checklist or PreImplementationChecklist()
        self.confidence_threshold = confidence_threshold

        logger.info(
            f"HolisticValidationOrchestrator initialized "
            f"(threshold={confidence_threshold})"
        )

    def validate(
        self,
        request: str,
        intent: str,
        context: Dict[str, Any]
    ) -> ValidationResult:
        """Execute holistic validation for request.

        Stages:
        1. Run pre-implementation checklist (12 categories)
        2. Generate 3 alternative approaches (if challenge_engine available)
        3. Calculate confidence score (if confidence_scorer available)
        4. Determine pass/fail based on threshold

        Args:
            request: User's implementation request
            intent: Intent type (IMPLEMENT, FIX, REFACTOR)
            context: Request context (existing_code, dependencies, etc.)

        Returns:
            ValidationResult with pass/fail decision and explanation

        Raises:
            ValueError: If intent not in [IMPLEMENT, FIX, REFACTOR]
        """
        if intent not in ["IMPLEMENT", "FIX", "REFACTOR"]:
            raise ValueError(
                f"Validation only applies to IMPLEMENT/FIX/REFACTOR, got {intent}"
            )

        # Phase 58 — cross-cutting hooks
        self._activate_cross_cutting_hooks(
            operation=intent,
            orchestrator_context=context,
        )

        logger.info(f"Starting validation for {intent} request: {request[:50]}...")

        # Stage 1: Run checklist
        checklist_result = self.run_checklist(context)
        logger.debug(f"Checklist complete: {len(checklist_result)} categories checked")

        # Stage 2: Generate challenges
        challenges = self.generate_challenges(request) if self.challenge_engine else []
        logger.debug(f"Generated {len(challenges)} alternative approaches")

        # Stage 3: Calculate confidence score
        confidence_score = self.score_confidence(
            request, challenges, checklist_result
        ) if self.confidence_scorer else self._default_confidence_score(checklist_result)
        logger.debug(f"Confidence score: {confidence_score:.2f}")

        # Stage 4: Determine pass/fail
        passed = confidence_score >= self.confidence_threshold

        # Stage 5: Generate explanation
        explanation = self._generate_explanation(
            passed, confidence_score, checklist_result, challenges
        )

        result = ValidationResult(
            passed=passed,
            confidence_score=confidence_score,
            checklist_result=checklist_result,
            challenges=challenges,
            explanation=explanation
        )

        logger.info(
            f"Validation {'PASSED' if passed else 'BLOCKED'} "
            f"(confidence={confidence_score:.2f}, threshold={self.confidence_threshold})"
        )

        return result

    def run_checklist(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run pre-implementation checklist.

        Args:
            context: Request context with code, dependencies, etc.

        Returns:
            Dict mapping category name to CheckResult
        """
        return self.checklist.run_all_checks(context)

    def generate_challenges(self, request: str) -> List[Dict[str, Any]]:
        """Generate 3 alternative approaches.

        Args:
            request: User's implementation request

        Returns:
            List of 3 alternatives with pros, cons, effort, risk
        """
        if not self.challenge_engine:
            return []

        return self.challenge_engine.generate_alternatives(request, {})

    def score_confidence(
        self,
        request: str,
        alternatives: List[Dict[str, Any]],
        checklist_result: Dict[str, Any]
    ) -> float:
        """Calculate confidence score.

        Args:
            request: User's implementation request
            alternatives: Generated alternative approaches
            checklist_result: Checklist validation results

        Returns:
            Confidence score between 0.0 and 1.0
        """
        if not self.confidence_scorer:
            return self._default_confidence_score(checklist_result)

        return self.confidence_scorer.score(request, alternatives, checklist_result)

    def _default_confidence_score(self, checklist_result: Dict[str, Any]) -> float:
        """Calculate default confidence from checklist results.

        Simple heuristic: 1.0 if all pass, 0.5 if any fail, 0.3 if multiple fail.

        Args:
            checklist_result: Dict of category -> CheckResult

        Returns:
            Confidence score between 0.0 and 1.0
        """
        if not checklist_result:
            return 0.5  # No data, medium confidence

        failed_categories = [
            cat for cat, result in checklist_result.items()
            if hasattr(result, 'passed') and not result.passed
        ]

        if len(failed_categories) == 0:
            return 1.0  # All pass
        elif len(failed_categories) == 1:
            return 0.65  # One failure (might still pass threshold)
        elif len(failed_categories) <= 3:
            return 0.50  # Multiple failures (below threshold)
        else:
            return 0.30  # Many failures (well below threshold)

    def _generate_explanation(
        self,
        passed: bool,
        confidence_score: float,
        checklist_result: Dict[str, Any],
        challenges: List[Dict[str, Any]]
    ) -> str:
        """Generate human-readable explanation.

        Args:
            passed: Validation passed or failed
            confidence_score: Calculated confidence score
            checklist_result: Checklist validation results
            challenges: Generated alternative approaches

        Returns:
            Multi-line explanation string
        """
        lines = []

        # Header
        if passed:
            lines.append(f"✅ Validation PASSED (confidence: {confidence_score:.2f})")
        else:
            lines.append(f"❌ Validation BLOCKED (confidence: {confidence_score:.2f} < {self.confidence_threshold})")

        lines.append("")

        # Checklist summary
        failed_categories = [
            cat for cat, result in checklist_result.items()
            if hasattr(result, 'passed') and not result.passed
        ]

        if failed_categories:
            lines.append("⚠️ Checklist Issues:")
            for cat in failed_categories[:3]:  # Show first 3
                result = checklist_result[cat]
                if hasattr(result, 'issues') and result.issues:
                    lines.append(f"  • {cat}: {result.issues[0]}")
            if len(failed_categories) > 3:
                lines.append(f"  • ... and {len(failed_categories) - 3} more")
            lines.append("")
        else:
            lines.append("✅ All checklist categories passed")
            lines.append("")

        # Challenges summary
        if challenges:
            lines.append(f"💡 {len(challenges)} Alternative Approaches:")
            for i, challenge in enumerate(challenges[:3], 1):
                approach = challenge.get("approach", f"Approach {i}")
                risk = challenge.get("risk", "UNKNOWN")
                lines.append(f"  {i}. {approach} (Risk: {risk})")
            lines.append("")

        # Recommendation
        if not passed:
            lines.append("📋 Recommendations:")
            lines.append("  1. Address checklist issues before proceeding")
            lines.append("  2. Review alternative approaches")
            lines.append("  3. Revise request to improve confidence score")

        return "\n".join(lines)

    def format_result(self, result: ValidationResult) -> str:
        """Format validation result for display.

        Args:
            result: ValidationResult to format

        Returns:
            Formatted string for Copilot Chat display
        """
        return result.explanation


# AC_COMPLETE: AC-PHASE48-S1-IMPL-002 ✅ HolisticValidationOrchestrator implemented
