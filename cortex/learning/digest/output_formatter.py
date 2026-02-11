"""
Output Formatter for DIGEST Results.

Formats DigestResult into JSON and Markdown.

AC_START: AC-PHASE41-003
Author: Asif Hussain
Date: 2026-02-07
Phase: 41 Stage 1 (ENH-053)
"""

import json
from typing import Any

from cortex.learning.digest.models import DigestResult


class OutputFormatter:
    """
    Format DIGEST results for output.

    Supports:
    - JSON serialization
    - Markdown summary generation

    Usage:
        formatter = OutputFormatter()
        json_str = formatter.to_json(result)
        markdown = formatter.to_markdown(result)
    """

    def to_json(self, result: DigestResult) -> str:
        """
        Serialize DigestResult to JSON string.

        Args:
            result: DigestResult to serialize

        Returns:
            JSON string
        """
        # Use Pydantic's model_dump for clean serialization
        data = result.model_dump(mode="json")
        return json.dumps(data, indent=2, default=str)

    def to_markdown(self, result: DigestResult) -> str:
        """
        Generate Markdown summary of DigestResult.

        Args:
            result: DigestResult to summarize

        Returns:
            Markdown formatted string
        """
        lines = [
            "# DIGEST Result",
            "",
            f"**File:** `{result.file_path}`",
            f"**Chat Session:** {'✅ Yes' if result.is_chat_session else '❌ No'}",
            f"**Detection Score:** {result.chat_score}/10",
            f"**Analyzed:** {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            ""
        ]

        if not result.is_chat_session:
            lines.append("❌ **Not a chat session** (score < 5)")
            return "\n".join(lines)

        # Extract categories
        extractions = result.extractions

        # Drifts
        drifts = extractions.get("drifts", [])
        lines.extend([
            "## 🔴 Drifts Detected",
            ""
        ])
        if drifts:
            for drift in drifts:
                lines.append(f"- {drift}")
        else:
            lines.append("*No drifts detected*")
        lines.append("")

        # Patterns
        patterns = extractions.get("patterns", [])
        lines.extend([
            "## 🟢 Successful Patterns",
            ""
        ])
        if patterns:
            for pattern in patterns:
                lines.append(f"- {pattern}")
        else:
            lines.append("*No patterns identified*")
        lines.append("")

        # Tools
        tools = extractions.get("tools", [])
        lines.extend([
            "## 🛠️ Tool Usage",
            ""
        ])
        if tools:
            for tool in tools:
                lines.append(f"- `{tool}`")
        else:
            lines.append("*No tool invocations*")
        lines.append("")

        # Efficiency
        efficiency = extractions.get("efficiency", {})
        lines.extend([
            "## ⚡ Efficiency",
            ""
        ])
        if efficiency:
            score = efficiency.get("score", 0)
            actual = efficiency.get("actual_turns", "?")
            expected = efficiency.get("expected_turns", "?")
            lines.append(f"**Score:** {score}% ({actual}/{expected} turns)")
        else:
            lines.append("*No efficiency data*")
        lines.append("")

        # Accuracy
        accuracy = extractions.get("accuracy", {})
        lines.extend([
            "## 🎯 Accuracy",
            ""
        ])
        if accuracy:
            score = accuracy.get("score", 0)
            corrections = accuracy.get("corrections", 0)
            total = accuracy.get("total_turns", 0)
            lines.append(f"**Score:** {score}% ({total - corrections}/{total} correct)")
        else:
            lines.append("*No accuracy data*")
        lines.append("")

        # Governance Violations
        violations = extractions.get("governance_violations", [])
        lines.extend([
            "## 🚨 Governance Violations",
            ""
        ])
        if violations:
            for violation in violations:
                lines.append(f"- ⚠️ {violation}")
        else:
            lines.append("*No violations detected*")
        lines.append("")

        return "\n".join(lines)


# AC_COMPLETE: AC-PHASE41-003 ✅ Structured JSON output with Pydantic models
