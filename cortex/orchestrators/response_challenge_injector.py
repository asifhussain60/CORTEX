"""Challenge-First Response Formatter and Injector.

AC-ID: REMEDIATION-INTENT-006
Formats execution responses with proactive challenges before output.
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ResponseFormat(Enum):
    """Response format options."""

    JSON = "JSON"
    MARKDOWN = "MARKDOWN"
    PLAIN_TEXT = "PLAIN_TEXT"


@dataclass
class ChallengeResponse:
    """Response structure with challenges."""

    execution_result: str = ""
    challenges: Optional[List[Dict[str, Any]]] = None
    recommendations: Optional[List[Dict[str, Any]]] = None
    format: ResponseFormat = ResponseFormat.JSON
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize defaults."""
        if self.challenges is None:
            self.challenges = []
        if self.recommendations is None:
            self.recommendations = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "execution_result": self.execution_result,
            "challenges": self.challenges,
            "recommendations": self.recommendations,
            "format": self.format.value,
            "metadata": self.metadata,
        }


class ResponseChallengeInjector:
    """Inject challenges into execution responses."""

    def __init__(self) -> None:
        """Initialize injector."""
        self.default_format = ResponseFormat.JSON
        self.priority_order = [
            "CRITICAL",
            "HIGH",
            "MEDIUM",
            "LOW",
        ]
        self.category_order = [
            "BREAKING_CHANGE",
            "SECURITY_RISK",
            "GOVERNANCE_RISK",
            "PERFORMANCE_RISK",
            "TEST_GAP",
            "HISTORICAL_ISSUE",
        ]

    def format_response(self, response: ChallengeResponse) -> str:
        """Format response with challenges.

        Args:
            response: ChallengeResponse to format.

        Returns:
            Formatted response string.
        """
        if response.format == ResponseFormat.JSON:
            return self._format_json(response)
        elif response.format == ResponseFormat.MARKDOWN:
            return self._format_markdown(response)
        else:
            return self._format_plain_text(response)

    def _format_json(self, response: ChallengeResponse) -> str:
        """Format as JSON.

        Args:
            response: Response to format.

        Returns:
            JSON formatted string.
        """
        data = {
            "result": response.execution_result or "Completed",
            "challenges": response.challenges or [],
            "recommendations": response.recommendations or [],
        }
        return json.dumps(data, indent=2)

    def _format_markdown(self, response: ChallengeResponse) -> str:
        """Format as Markdown.

        Args:
            response: Response to format.

        Returns:
            Markdown formatted string.
        """
        lines = []

        # Execution result
        lines.append("## Execution Result\n")
        lines.append(f"{response.execution_result or 'Task completed'}\n")

        # Challenges section
        if response.challenges:
            lines.append("## Challenges\n")
            ordered = self.order_challenges(response.challenges)
            for challenge in ordered:
                formatted = self.format_challenge(challenge)
                lines.append(formatted)
                lines.append("")

        # Recommendations section
        if response.recommendations:
            lines.append("## Recommendations\n")
            for rec in response.recommendations:
                lines.append(f"- **{rec.get('title', 'Recommendation')}**: {rec.get('description', '')}\n")

        return "\n".join(lines)

    def _format_plain_text(self, response: ChallengeResponse) -> str:
        """Format as plain text.

        Args:
            response: Response to format.

        Returns:
            Plain text formatted string.
        """
        lines = []

        # Execution result
        lines.append("EXECUTION RESULT")
        lines.append("-" * 50)
        lines.append(response.execution_result or "Task completed")
        lines.append("")

        # Challenges
        if response.challenges:
            lines.append("CHALLENGES")
            lines.append("-" * 50)
            ordered = self.order_challenges(response.challenges)
            for challenge in ordered:
                lines.append(f"[{challenge.get('severity', 'MEDIUM')}] {challenge.get('category', 'Unknown')}")
                lines.append(f"  {challenge.get('description', '')}")
                if challenge.get("mitigation"):
                    lines.append(f"  Mitigation: {challenge['mitigation']}")
                lines.append("")

        # Recommendations
        if response.recommendations:
            lines.append("RECOMMENDATIONS")
            lines.append("-" * 50)
            for rec in response.recommendations:
                lines.append(f"- {rec.get('title', 'Recommendation')}")
                lines.append(f"  {rec.get('description', '')}")
                lines.append("")

        return "\n".join(lines)

    def inject_challenges(
        self,
        base_response: str,
        challenges: List[Dict[str, Any]],
        format_type: ResponseFormat = ResponseFormat.MARKDOWN,
    ) -> str:
        """Inject challenges into base response.

        Args:
            base_response: Base execution response.
            challenges: List of challenges to inject.
            format_type: Output format.

        Returns:
            Response with injected challenges.
        """
        response = ChallengeResponse(
            execution_result=base_response,
            challenges=challenges,
            format=format_type,
        )
        return self.format_response(response)

    def order_challenges(
        self,
        challenges: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Order challenges by severity and category.

        Args:
            challenges: List of challenges to order.

        Returns:
            Ordered list of challenges.
        """
        severity_order = {
            "CRITICAL": 4,
            "HIGH": 3,
            "MEDIUM": 2,
            "LOW": 1,
        }

        category_order = {
            cat: idx for idx, cat in enumerate(self.category_order)
        }

        def sort_key(challenge: Dict[str, Any]) -> tuple:
            """Generate sort key for challenge."""
            severity = challenge.get("severity", "MEDIUM")
            category = challenge.get("category", "TEST_GAP")
            return (
                -severity_order.get(severity, 0),
                category_order.get(category, 999),
            )

        return sorted(challenges, key=sort_key)

    def format_challenge(
        self,
        challenge: Dict[str, Any],
    ) -> str:
        """Format a single challenge.

        Args:
            challenge: Challenge dictionary.

        Returns:
            Formatted challenge string.
        """
        lines = []
        severity = challenge.get("severity", "MEDIUM")
        category = challenge.get("category", "Unknown")
        description = challenge.get("description", "")

        # Title with severity
        lines.append(f"### [{severity}] {category}")

        # Description
        if description:
            lines.append(f"{description}")

        # Affected scope
        if challenge.get("affected_scope"):
            scope = challenge["affected_scope"]
            if isinstance(scope, list):
                scope_str = ", ".join(scope)
            else:
                scope_str = str(scope)
            lines.append(f"**Affected**: {scope_str}")

        # Evidence
        if challenge.get("evidence"):
            evidence = challenge["evidence"]
            if isinstance(evidence, list):
                for ev in evidence:
                    lines.append(f"- {ev}")
            else:
                lines.append(f"- {evidence}")

        # Mitigation
        if challenge.get("mitigation"):
            lines.append(f"**Mitigation**: {challenge['mitigation']}")

        # Confidence
        if challenge.get("confidence") is not None:
            confidence = challenge["confidence"]
            lines.append(f"**Confidence**: {confidence:.1%}")

        return "\n".join(lines)

    def merge_responses(
        self,
        responses: List[ChallengeResponse],
    ) -> ChallengeResponse:
        """Merge multiple responses into one.

        Args:
            responses: List of responses to merge.

        Returns:
            Merged response.
        """
        merged_result = " | ".join(
            r.execution_result for r in responses if r.execution_result
        )
        merged_challenges = []
        merged_recommendations = []

        for response in responses:
            if response.challenges:
                merged_challenges.extend(response.challenges)
            if response.recommendations:
                merged_recommendations.extend(response.recommendations)

        return ChallengeResponse(
            execution_result=merged_result or "Completed",
            challenges=merged_challenges,
            recommendations=merged_recommendations,
        )
