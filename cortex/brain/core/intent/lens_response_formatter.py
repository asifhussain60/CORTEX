"""
LENS Response Formatter Module (IR-003-03).

Formats comprehension output for user presentation in multiple formats
(YAML, Markdown, JSON). Provides consistent, readable presentation of
challenges, recommendations, and intent summaries to support user approval gate.

The response formatter is critical to the CORTEX LENS protocol, ensuring
users can easily understand and validate the system's comprehension of
their intent before execution.

Core responsibilities:
1. Format reflection responses in multiple output formats
2. Sort challenges and recommendations by severity/priority
3. Customize output via templates and configuration
4. Convert between formats as needed
5. Ensure readability and clarity for user review
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional

import yaml

# ============================================================================
# ENUMS
# ============================================================================

class ResponseFormat(Enum):
    """Output formats supported by the response formatter."""
    JSON = "json"
    YAML = "yaml"
    MARKDOWN = "markdown"


class SeverityColor(Enum):
    """Color mapping for severity levels (for terminal output)."""
    CRITICAL = "\033[91m"  # Red
    HIGH = "\033[93m"  # Yellow
    MEDIUM = "\033[94m"  # Blue
    LOW = "\033[92m"  # Green
    RESET = "\033[0m"  # Reset


# ============================================================================
# SEVERITY/PRIORITY DEFINITIONS
# ============================================================================

SEVERITY_ORDER = {
    "CRITICAL": 0,
    "HIGH": 1,
    "MEDIUM": 2,
    "LOW": 3,
}

PRIORITY_ORDER = {
    "CRITICAL": 0,
    "HIGH": 1,
    "MEDIUM": 2,
    "LOW": 3,
}


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class FormattedResponse:
    """Represents a formatted response."""

    content: str
    format: ResponseFormat
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_string(self) -> str:
        """Return the formatted content as string."""
        return self.content


# ============================================================================
# MAIN FORMATTER CLASS
# ============================================================================

class LENSResponseFormatter:
    """Formatter for comprehension responses."""

    def __init__(self):
        """Initialize the response formatter."""
        self.sort_challenges_by_severity = True
        self.sort_recommendations_by_priority = True
        self.include_audit_trail = False
        self.include_metadata = True
        self.markdown_severity_emoji = True
        self.max_line_length = 80

    def format(
        self,
        response: Dict[str, Any],
        output_format: ResponseFormat,
        section_order: Optional[List[str]] = None,
    ) -> str:
        """Format a reflection response in the specified format.

        Args:
            response: The reflection response to format
            output_format: Desired output format (JSON, YAML, Markdown)
            section_order: Custom ordering of sections (used for markdown formatting)

        Returns:
            Formatted response as string
        """
        # Prepare response data
        prepared = self._prepare_response(response)

        # Apply sorting if needed
        prepared = self._sort_response(prepared)

        # Format based on requested format
        if output_format == ResponseFormat.JSON:
            return self._format_json(prepared)
        elif output_format == ResponseFormat.YAML:
            return self._format_yaml(prepared)
        elif output_format == ResponseFormat.MARKDOWN:
            return self._format_markdown(prepared, section_order=section_order)
        else:
            raise ValueError(f"Unsupported format: {output_format}")

    def _prepare_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare response data for formatting."""
        prepared = response.copy()

        # Ensure required sections exist
        if "intent" not in prepared:
            prepared["intent"] = {}
        if "challenges" not in prepared:
            prepared["challenges"] = []
        if "recommendations" not in prepared:
            prepared["recommendations"] = []

        # Filter audit trail if not needed
        if not self.include_audit_trail and "audit_trail" in prepared:
            del prepared["audit_trail"]

        return prepared

    def _sort_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Sort challenges and recommendations by severity/priority."""
        if self.sort_challenges_by_severity and "challenges" in response:
            response["challenges"] = sorted(
                response["challenges"],
                key=lambda x: SEVERITY_ORDER.get(x.get("severity", "LOW"), 999)
            )

        if self.sort_recommendations_by_priority and "recommendations" in response:
            response["recommendations"] = sorted(
                response["recommendations"],
                key=lambda x: PRIORITY_ORDER.get(x.get("priority", "LOW"), 999)
            )

        return response

    def _format_json(self, response: Dict[str, Any]) -> str:
        """Format response as JSON."""
        return json.dumps(response, indent=2, default=str)

    def _format_yaml(self, response: Dict[str, Any]) -> str:
        """Format response as YAML."""
        return yaml.dump(
            response,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False
        )

    def _format_markdown(
        self,
        response: Dict[str, Any],
        section_order: Optional[List[str]] = None,
    ) -> str:
        """Format response as Markdown.

        Args:
            response: The response to format
            section_order: Optional custom section ordering

        Returns:
            Formatted markdown string
        """
        lines: List[str] = []

        # Header
        lines.append("# Intent Comprehension Review")
        lines.append("")

        # Metadata section
        if self.include_metadata:
            lines.append("## Metadata")
            if "id" in response:
                lines.append(f"**Reflection ID:** `{response['id']}`")
            if "status" in response:
                lines.append(f"**Status:** {response['status']}")
            if "timestamp" in response:
                lines.append(f"**Generated:** {response['timestamp']}")
            lines.append("")

        # Intent section
        lines.append("## Intent")
        intent = response.get("intent", {})
        if intent:
            if "type" in intent:
                lines.append(f"**Type:** {intent['type']}")
            if "scope" in intent:
                scope = intent["scope"]
                if isinstance(scope, dict):
                    if "target_name" in scope:
                        lines.append(f"**Target:** {scope['target_name']}")
                    if "file_path" in scope:
                        lines.append(f"**File:** `{scope['file_path']}`")
            if "confidence" in intent:
                confidence = intent["confidence"]
                confidence_pct = int(confidence * 100)
                lines.append(f"**Confidence:** {confidence_pct}%")
            if "keywords" in intent:
                keywords = intent.get("keywords", [])
                if keywords:
                    lines.append(f"**Keywords:** {', '.join(keywords)}")
        lines.append("")

        # Challenges section
        lines.append("## Challenges & Risks")
        challenges = response.get("challenges", [])

        if challenges:
            for challenge in challenges:
                # Use emoji for severity if enabled
                severity = challenge.get("severity", "MEDIUM")
                emoji = self._get_severity_emoji(severity)
                category = challenge.get("category", "")

                lines.append(f"### {emoji} {severity} - {category}")

                if "description" in challenge:
                    lines.append(f"{challenge['description']}")

                if "affected_code" in challenge:
                    lines.append(f"**Affected Code:** `{challenge['affected_code']}`")

                if "remediation" in challenge:
                    lines.append(f"**Remediation:** {challenge['remediation']}")

                lines.append("")
        else:
            lines.append("✓ No challenges identified")
            lines.append("")

        # Recommendations section
        lines.append("## Recommendations")
        recommendations = response.get("recommendations", [])

        if recommendations:
            for rec in recommendations:
                category = rec.get("category", "")

                lines.append(f"### 💡 {category}")

                if "description" in rec:
                    lines.append(f"{rec['description']}")

                if "suggestion" in rec:
                    lines.append(f"**Suggestion:** {rec['suggestion']}")

                lines.append("")
        else:
            lines.append("No additional recommendations")
            lines.append("")

        # Approval section
        lines.append("## Next Steps")
        lines.append("- **✅ Approve** - Proceed with execution")
        lines.append("- **❌ Reject** - Cancel and refine request")
        lines.append("- **❓ Clarify** - Ask for more information")
        lines.append("")

        return "\n".join(lines)

    def _get_severity_emoji(self, severity: str) -> str:
        """Get emoji representation of severity."""
        emoji_map = {
            "CRITICAL": "🔴",
            "HIGH": "🟠",
            "MEDIUM": "🟡",
            "LOW": "🟢",
        }
        return emoji_map.get(severity, "⚪")

    def convert_format(
        self,
        content: str,
        from_format: ResponseFormat,
        to_format: ResponseFormat,
    ) -> str:
        """Convert response from one format to another.

        Args:
            content: Content in source format
            from_format: Source format
            to_format: Target format

        Returns:
            Content in target format
        """
        # Parse from source format
        if from_format == ResponseFormat.JSON:
            parsed = json.loads(content)
        elif from_format == ResponseFormat.YAML:
            parsed = yaml.safe_load(content)
        else:
            raise ValueError(f"Cannot parse from {from_format}")

        # Format to target format
        return self.format(parsed, to_format)

    def format_challenge(
        self,
        challenge: Dict[str, Any],
        output_format: ResponseFormat = ResponseFormat.MARKDOWN
    ) -> str:
        """Format a single challenge.

        Args:
            challenge: Challenge data
            output_format: Output format

        Returns:
            Formatted challenge as string
        """
        if output_format == ResponseFormat.MARKDOWN:
            severity = challenge.get("severity", "MEDIUM")
            emoji = self._get_severity_emoji(severity)
            category = challenge.get("category", "")
            description = challenge.get("description", "")

            lines = [
                f"### {emoji} {severity} - {category}",
                f"{description}",
            ]

            if "remediation" in challenge:
                lines.append(f"**Remediation:** {challenge['remediation']}")

            return "\n".join(lines)
        else:
            # For JSON/YAML, just return as-is
            if output_format == ResponseFormat.JSON:
                return json.dumps(challenge, indent=2)
            elif output_format == ResponseFormat.YAML:
                return yaml.dump(challenge)

    def format_recommendation(
        self,
        recommendation: Dict[str, Any],
        output_format: ResponseFormat = ResponseFormat.MARKDOWN
    ) -> str:
        """Format a single recommendation.

        Args:
            recommendation: Recommendation data
            output_format: Output format

        Returns:
            Formatted recommendation as string
        """
        if output_format == ResponseFormat.MARKDOWN:
            category = recommendation.get("category", "")
            description = recommendation.get("description", "")

            lines = [
                f"### 💡 {category}",
                f"{description}",
            ]

            if "suggestion" in recommendation:
                lines.append(f"**Suggestion:** {recommendation['suggestion']}")

            return "\n".join(lines)
        else:
            # For JSON/YAML
            if output_format == ResponseFormat.JSON:
                return json.dumps(recommendation, indent=2)
            elif output_format == ResponseFormat.YAML:
                return yaml.dump(recommendation)

    def format_intent(
        self,
        intent: Dict[str, Any],
        output_format: ResponseFormat = ResponseFormat.MARKDOWN
    ) -> str:
        """Format the intent section.

        Args:
            intent: Intent data
            output_format: Output format

        Returns:
            Formatted intent as string
        """
        if output_format == ResponseFormat.MARKDOWN:
            lines = ["## Intent"]

            if "type" in intent:
                lines.append(f"**Type:** {intent['type']}")

            if "confidence" in intent:
                confidence_pct = int(intent["confidence"] * 100)
                lines.append(f"**Confidence:** {confidence_pct}%")

            if "scope" in intent:
                scope = intent["scope"]
                if isinstance(scope, dict) and "target_name" in scope:
                    lines.append(f"**Target:** {scope['target_name']}")

            return "\n".join(lines)
        else:
            if output_format == ResponseFormat.JSON:
                return json.dumps(intent, indent=2)
            elif output_format == ResponseFormat.YAML:
                return yaml.dump(intent)

    def get_summary(self, response: Dict[str, Any]) -> str:
        """Get a brief text summary of the response.

        Args:
            response: The response to summarize

        Returns:
            One-line summary
        """
        intent_type = response.get("intent", {}).get("type", "UNKNOWN")
        challenge_count = len(response.get("challenges", []))
        rec_count = len(response.get("recommendations", []))

        parts = [f"Intent: {intent_type}"]

        if challenge_count > 0:
            parts.append(f"Challenges: {challenge_count}")

        if rec_count > 0:
            parts.append(f"Recommendations: {rec_count}")

        return " | ".join(parts)

    def get_summary_statistics(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Get summary statistics about the response.

        Args:
            response: The response to analyze

        Returns:
            Dictionary with statistics
        """
        challenges = response.get("challenges", [])
        recommendations = response.get("recommendations", [])

        # Count by severity
        severity_counts = {}
        for challenge in challenges:
            severity = challenge.get("severity", "LOW")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        # Count by category
        category_counts = {}
        for challenge in challenges:
            category = challenge.get("category", "UNKNOWN")
            category_counts[category] = category_counts.get(category, 0) + 1

        return {
            "total_challenges": len(challenges),
            "total_recommendations": len(recommendations),
            "severity_distribution": severity_counts,
            "category_distribution": category_counts,
            "critical_count": severity_counts.get("CRITICAL", 0),
            "high_count": severity_counts.get("HIGH", 0),
        }
