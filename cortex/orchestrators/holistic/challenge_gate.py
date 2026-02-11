"""Challenge Gate for pre-implementation validation and alternatives.

Phase 48 S3: Mandatory challenge generation before implementation.
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ChallengeType(str, Enum):
    """Types of challenges."""

    ARCHITECTURAL = "architectural"
    PERFORMANCE = "performance"
    SECURITY = "security"
    MAINTAINABILITY = "maintainability"
    DEPENDENCY = "dependency"


@dataclass
class ChallengeAlternative:
    """An alternative approach to the proposed implementation."""

    name: str
    description: str
    pros: List[str]
    cons: List[str]
    roi_score: float  # 0.0 to 1.0
    effort_estimate: str  # "low", "medium", "high"
    implementation_time: str  # e.g., "2 days"
    risk_level: str  # "low", "medium", "high"


@dataclass
class Challenge:
    """A challenge to proposed implementation."""

    type: ChallengeType
    title: str
    description: str
    severity: str  # "info", "warning", "critical"
    current_approach: str
    alternatives: List[ChallengeAlternative]
    recommended_alternative: Optional[int] = None  # Index of recommended alternative
    evidence: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChallengeGateResult:
    """Result of challenge gate evaluation."""

    challenges: List[Challenge]
    has_critical: bool
    has_warnings: bool
    verdict: str  # "PROCEED", "CHALLENGE", "BLOCK"
    approval_required: bool
    user_decision_pending: bool


class ChallengeGateOrchestrator:
    """Orchestrator for pre-implementation challenge generation.

    Analyzes proposed changes and generates mandatory challenges with
    alternative approaches before implementation proceeds.
    """

    def __init__(self):
        """Initialize the challenge gate orchestrator."""
        self.challenges: List[Challenge] = []

    def generate_challenges(
        self,
        operation: str,
        target: str,
        description: str,
        affected_components: List[str],
    ) -> ChallengeGateResult:
        """Generate challenges for a proposed implementation.

        Args:
            operation: Operation type (IMPLEMENT, FIX, REFACTOR)
            target: Target file or component
            description: Description of proposed change
            affected_components: List of affected orchestrators/components

        Returns:
            ChallengeGateResult with all challenges and verdict.
        """
        challenges = []

        # Analyze and generate challenges
        if operation == "IMPLEMENT":
            challenges.extend(self._generate_architectural_challenges(target, description))
            challenges.extend(self._generate_dependency_challenges(affected_components))

        elif operation == "REFACTOR":
            challenges.extend(self._generate_maintainability_challenges(target, description))

        elif operation == "FIX":
            challenges.extend(self._generate_performance_challenges(target))

        # Determine verdict
        has_critical = any(c.severity == "critical" for c in challenges)
        has_warnings = any(c.severity == "warning" for c in challenges)

        if has_critical:
            verdict = "BLOCK"
            approval_required = True
        elif has_warnings:
            verdict = "CHALLENGE"
            approval_required = False  # Can proceed with challenge review
        else:
            verdict = "PROCEED"
            approval_required = False

        return ChallengeGateResult(
            challenges=challenges,
            has_critical=has_critical,
            has_warnings=has_warnings,
            verdict=verdict,
            approval_required=approval_required,
            user_decision_pending=has_critical or has_warnings,
        )

    def _generate_architectural_challenges(
        self, target: str, description: str
    ) -> List[Challenge]:
        """Generate architectural challenges.

        Args:
            target: Target component
            description: Change description

        Returns:
            List of architectural challenges.
        """
        challenges = []

        # Check if adding new orchestrator tier coupling
        if "orchestrator" in target.lower() and "core" not in target.lower():
            challenge = Challenge(
                type=ChallengeType.ARCHITECTURAL,
                title="Potential Tier Coupling Risk",
                description=(
                    "Adding functionality to non-core tier orchestrator. "
                    "Consider whether this should be core tier instead."
                ),
                severity="warning",
                current_approach="Adding to domain/support tier",
                alternatives=[
                    ChallengeAlternative(
                        name="Promote to Core Tier",
                        description="Move functionality to core tier for broader availability",
                        pros=[
                            "Guaranteed availability across all systems",
                            "Better API stability",
                            "Simpler dependency management",
                        ],
                        cons=[
                            "Core tier is slower to change",
                            "Requires broader review process",
                            "Higher bar for inclusion",
                        ],
                        roi_score=0.85,
                        effort_estimate="medium",
                        implementation_time="3 days",
                        risk_level="low",
                    ),
                    ChallengeAlternative(
                        name="Keep in Domain Tier",
                        description="Keep as domain-specific but document dependencies carefully",
                        pros=[
                            "Faster iteration",
                            "Domain-specific optimizations possible",
                            "Easier to refactor later",
                        ],
                        cons=[
                            "May couple with other domain components",
                            "Less stability guarantees",
                            "Documentation burden higher",
                        ],
                        roi_score=0.70,
                        effort_estimate="low",
                        implementation_time="1 day",
                        risk_level="medium",
                    ),
                ],
                recommended_alternative=0,
            )
            challenges.append(challenge)

        return challenges

    def _generate_dependency_challenges(
        self, affected_components: List[str]
    ) -> List[Challenge]:
        """Generate dependency-related challenges.

        Args:
            affected_components: List of affected components

        Returns:
            List of dependency challenges.
        """
        challenges = []

        if len(affected_components) > 3:
            challenge = Challenge(
                type=ChallengeType.DEPENDENCY,
                title="High Dependency Impact",
                description=f"Change affects {len(affected_components)} components. Consider minimizing scope.",
                severity="warning",
                current_approach=f"Affecting {len(affected_components)} components",
                alternatives=[
                    ChallengeAlternative(
                        name="Phased Rollout",
                        description="Break implementation into smaller phases with staged rollout",
                        pros=[
                            "Reduced risk per phase",
                            "Better validation between phases",
                            "Easier to rollback if needed",
                            "Stakeholder confidence higher",
                        ],
                        cons=[
                            "More implementation effort",
                            "Longer overall timeline",
                            "More coordination needed",
                        ],
                        roi_score=0.92,
                        effort_estimate="high",
                        implementation_time="7 days",
                        risk_level="low",
                    ),
                    ChallengeAlternative(
                        name="Monolithic Rollout",
                        description="Implement all changes at once with comprehensive testing",
                        pros=[
                            "Faster overall timeline",
                            "Simpler coordination",
                            "Single test cycle",
                        ],
                        cons=[
                            "Higher risk per failure",
                            "Harder to debug issues",
                            "Rollback more complex",
                            "More stakeholder anxiety",
                        ],
                        roi_score=0.65,
                        effort_estimate="medium",
                        implementation_time="3 days",
                        risk_level="high",
                    ),
                ],
                recommended_alternative=0,
            )
            challenges.append(challenge)

        return challenges

    def _generate_maintainability_challenges(
        self, target: str, description: str
    ) -> List[Challenge]:
        """Generate maintainability challenges for refactoring.

        Args:
            target: Target component
            description: Refactoring description

        Returns:
            List of maintainability challenges.
        """
        challenges = []

        # Check if refactoring changes public API
        if "api" in target.lower() or "interface" in description.lower():
            challenge = Challenge(
                type=ChallengeType.MAINTAINABILITY,
                title="Public API Change Risk",
                description="Refactoring affects public API. Ensure backward compatibility.",
                severity="warning",
                current_approach="Direct API refactoring",
                alternatives=[
                    ChallengeAlternative(
                        name="Deprecation Strategy",
                        description="Add new API, deprecate old, provide migration path",
                        pros=[
                            "Zero breaking changes",
                            "Graceful migration for users",
                            "Time for users to adapt",
                            "Better adoption rate",
                        ],
                        cons=[
                            "More code to maintain",
                            "Longer transition period",
                            "Deprecation warnings overhead",
                        ],
                        roi_score=0.88,
                        effort_estimate="high",
                        implementation_time="5 days",
                        risk_level="low",
                    ),
                    ChallengeAlternative(
                        name="Breaking Change",
                        description="Change API directly, bump major version",
                        pros=[
                            "Cleaner codebase",
                            "No legacy code overhead",
                            "Simpler implementation",
                        ],
                        cons=[
                            "Users must update code",
                            "Adoption friction high",
                            "Relationship damage possible",
                            "Support burden increases",
                        ],
                        roi_score=0.55,
                        effort_estimate="low",
                        implementation_time="2 days",
                        risk_level="high",
                    ),
                ],
                recommended_alternative=0,
            )
            challenges.append(challenge)

        return challenges

    def _generate_performance_challenges(self, target: str) -> List[Challenge]:
        """Generate performance challenges for fixes.

        Args:
            target: Target component being fixed

        Returns:
            List of performance challenges.
        """
        challenges = []

        # Check if fixing in hot path
        if any(x in target.lower() for x in ["orchestrator", "lens", "validation"]):
            challenge = Challenge(
                type=ChallengeType.PERFORMANCE,
                title="Hot Path Modification",
                description=f"Fix targets {target} which may be in hot path. Verify performance impact.",
                severity="info",
                current_approach="Direct fix without performance analysis",
                alternatives=[
                    ChallengeAlternative(
                        name="Performance-Aware Fix",
                        description="Fix implementation with profiling and benchmarking",
                        pros=[
                            "Ensures no regression",
                            "Potential optimization opportunity",
                            "Data-driven approach",
                            "Better stakeholder confidence",
                        ],
                        cons=[
                            "More implementation time",
                            "Requires profiling tools",
                            "More validation needed",
                        ],
                        roi_score=0.90,
                        effort_estimate="medium",
                        implementation_time="4 days",
                        risk_level="low",
                    ),
                    ChallengeAlternative(
                        name="Standard Fix",
                        description="Fix implementation with standard testing only",
                        pros=[
                            "Faster implementation",
                            "Simpler verification",
                            "Quick fix to production",
                        ],
                        cons=[
                            "Risk of performance regression",
                            "May need reverts",
                            "Customer impact possible",
                        ],
                        roi_score=0.72,
                        effort_estimate="low",
                        implementation_time="1 day",
                        risk_level="medium",
                    ),
                ],
                recommended_alternative=0,
            )
            challenges.append(challenge)

        return challenges

    def format_challenge_for_user(self, challenge: Challenge) -> str:
        """Format challenge for user display.

        Args:
            challenge: Challenge to format

        Returns:
            Formatted challenge string.
        """
        lines = []
        lines.append(f"\n### ⚠️  {challenge.title}")
        lines.append(f"**Type:** {challenge.type.value} | **Severity:** {challenge.severity}")
        lines.append(f"\n{challenge.description}")
        lines.append(f"\n**Current Approach:** {challenge.current_approach}")
        lines.append("\n**Alternatives:**")

        for i, alt in enumerate(challenge.alternatives):
            marker = "✅ (Recommended)" if i == challenge.recommended_alternative else ""
            lines.append(f"\n**{i + 1}. {alt.name}** {marker}")
            lines.append(f"   {alt.description}")
            lines.append(f"   - ROI: {alt.roi_score:.2f}")
            lines.append(f"   - Effort: {alt.effort_estimate}")
            lines.append(f"   - Time: {alt.implementation_time}")
            lines.append(f"   - Risk: {alt.risk_level}")
            lines.append(f"   - **Pros:** {', '.join(alt.pros)}")
            lines.append(f"   - **Cons:** {', '.join(alt.cons)}")

        return "\n".join(lines)

    def format_result_for_user(self, result: ChallengeGateResult) -> str:
        """Format challenge gate result for user display.

        Args:
            result: ChallengeGateResult to format

        Returns:
            Formatted result string.
        """
        lines = []
        lines.append("\n## 🛡️  MANDATORY CHALLENGE GATE")
        lines.append(
            f"\n**Verdict:** {result.verdict} | Challenges: {len(result.challenges)}"
        )

        if not result.challenges:
            lines.append("\n✅ No challenges detected - proceed normally.")
            return "\n".join(lines)

        for challenge in result.challenges:
            lines.append(self.format_challenge_for_user(challenge))

        if result.user_decision_pending:
            lines.append("\n" + "=" * 60)
            lines.append("\n**Decision Required:**")
            if result.verdict == "BLOCK":
                lines.append(
                    "❌ Critical challenges detected. Address or override with reason."
                )
            else:
                lines.append(
                    "⚠️  Review alternatives and confirm approach before proceeding."
                )

        return "\n".join(lines)
