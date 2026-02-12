"""
Extraction Engine for DIGEST Mode.

Extracts insights from chat sessions across 6 categories:
- Drifts, Patterns, Tools, Efficiency, Accuracy, Governance Violations

AC_START: AC-PHASE41-002, AC-PHASE41-005
Author: Asif Hussain
Date: 2026-02-07
Phase: 41 Stage 1 (ENH-053)
"""

import re
from typing import Any, Dict, List


class ExtractionEngine:
    """
    Extract insights from chat session content.

    Categories:
    1. Drifts - Deviations from best practices
    2. Patterns - Successful workflows
    3. Tools - MCP tool usage
    4. Efficiency - Turn optimization
    5. Accuracy - Correction tracking
    6. Governance Violations - CORE rule violations

    Usage:
        engine = ExtractionEngine()
        extractions = engine.extract_all(content)
        print(extractions["drifts"])
    """

    def extract_all(self, content: str) -> Dict[str, Any]:
        """
        Extract all 6 categories from content.

        Args:
            content: Chat session text

        Returns:
            Dict with keys: drifts, patterns, tools, efficiency, accuracy, governance_violations
        """
        return {
            "drifts": self._extract_drifts(content),
            "patterns": self._extract_patterns(content),
            "tools": self._extract_tools(content),
            "efficiency": self._extract_efficiency(content),
            "accuracy": self._extract_accuracy(content),
            "governance_violations": self._extract_governance_violations(content)
        }

    def _extract_drifts(self, content: str) -> List[str]:
        """Extract drift observations from comments."""
        drifts = []

        # Look for explicit drift comments
        drift_pattern = r"# Drift[:\s]+(.+?)(?:\n|$)"
        matches = re.findall(drift_pattern, content, re.IGNORECASE)
        drifts.extend([m.strip() for m in matches])

        # Look for "instead of" patterns (common in drifts)
        instead_pattern = r"(.+?instead of.+?)(?:\n|$)"
        matches = re.findall(instead_pattern, content, re.IGNORECASE)
        drifts.extend([m.strip() for m in matches if "drift" in m.lower() or "#" in m])

        return list(set(drifts))  # Remove duplicates

    def _extract_patterns(self, content: str) -> List[str]:
        """Extract successful pattern observations."""
        patterns = []

        # Look for explicit pattern comments
        pattern_pattern = r"# Pattern[:\s]+(.+?)(?:\n|$)"
        matches = re.findall(pattern_pattern, content, re.IGNORECASE)
        patterns.extend([m.strip() for m in matches])

        # Look for "successful" or "workflow" mentions
        success_keywords = ["successful", "workflow", "tdd", "test-first"]
        for keyword in success_keywords:
            keyword_pattern = rf"#[^\n]*{keyword}[^\n]*"
            matches = re.findall(keyword_pattern, content, re.IGNORECASE)
            patterns.extend([m.strip() for m in matches])

        return list(set(patterns))

    def _extract_tools(self, content: str) -> List[str]:
        """Extract tool usage from chat."""
        tools = []

        # Extract from [Tool call: ...] markers
        tool_call_pattern = r"\[Tool call:\s*(\w+)\]"
        matches = re.findall(tool_call_pattern, content)
        tools.extend(matches)

        return list(set(tools))

    def _extract_efficiency(self, content: str) -> Dict[str, Any]:
        """Extract efficiency metrics from comments."""
        efficiency = {"score": 0, "notes": []}

        # Look for efficiency comments: # Efficiency: X/Y turns (Z%)
        eff_pattern = r"# Efficiency[:\s]+(\d+)/(\d+)[^\n]*\((\d+)%\)"
        match = re.search(eff_pattern, content, re.IGNORECASE)

        if match:
            actual, expected, percentage = match.groups()
            efficiency["score"] = int(percentage)
            efficiency["actual_turns"] = int(actual)
            efficiency["expected_turns"] = int(expected)
        else:
            # Calculate from turn count
            user_turns = len(re.findall(r"^User:", content, re.MULTILINE))
            if user_turns > 0:
                # Rough estimate: assume 3-5 turns is optimal
                expected = max(3, user_turns // 2)
                efficiency["score"] = min(100, int((expected / user_turns) * 100))
                efficiency["actual_turns"] = user_turns
                efficiency["expected_turns"] = expected

        return efficiency

    def _extract_accuracy(self, content: str) -> Dict[str, Any]:
        """Extract accuracy metrics from corrections."""
        accuracy = {"score": 100, "corrections": 0, "total_turns": 0}

        # Look for accuracy comments: # Accuracy: X/Y correct (Z%)
        acc_pattern = r"# Accuracy[:\s]+(\d+)/(\d+)[^\n]*\((\d+)%\)"
        match = re.search(acc_pattern, content, re.IGNORECASE)

        if match:
            correct, total, percentage = match.groups()
            accuracy["score"] = int(percentage)
            accuracy["corrections"] = int(total) - int(correct)
            accuracy["total_turns"] = int(total)
        else:
            # Count turns and corrections
            user_turns = len(re.findall(r"^User:", content, re.MULTILINE))

            # Look for correction indicators
            correction_keywords = ["fix", "correct", "wrong", "error", "mistake", "actually"]
            corrections = sum(
                len(re.findall(rf"\b{kw}\b", content, re.IGNORECASE))
                for kw in correction_keywords
            )

            if user_turns > 0:
                accuracy["corrections"] = min(corrections, user_turns)
                accuracy["total_turns"] = user_turns
                accuracy["score"] = max(0, int(((user_turns - corrections) / user_turns) * 100))

        return accuracy

    def _extract_governance_violations(self, content: str) -> List[str]:
        """Extract CORE rule violations from chat."""
        violations = []

        # CORE-002: Markdown file generation
        core_002_patterns = [
            r"cat\s*>\s*\w+\.md",
            r"echo\s+.+>\s*\w+\.md",
            r"printf\s+.+>\s*\w+\.md",
            r"create_file.*\.md"
        ]
        for pattern in core_002_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                violations.append("CORE-002: Markdown file generation detected")
                break

        # CORE-008: TDD violation (implementation before tests)
        # Look for file creation without prior test creation
        if "[Tool call: create_file]" in content:
            # Check if test file mentioned before implementation
            lines = content.split("\n")
            found_impl_first = False
            for i, line in enumerate(lines):
                if "create_file" in line.lower():
                    # Check previous 10 lines for test mention
                    context = "\n".join(lines[max(0, i-10):i])
                    if "test" not in context.lower():
                        found_impl_first = True
                        break

            if found_impl_first:
                violations.append("CORE-008: Implementation before tests (TDD violation)")

        # CORE-028: SCREAMING_CASE file naming
        screaming_pattern = r"[A-Z_]{3,}\.py"
        if re.search(screaming_pattern, content):
            violations.append("CORE-028: SCREAMING_CASE file naming detected")

        # CORE-035: Duplication indicators
        duplication_keywords = ["duplicate", "similar.*exists", "already have"]
        for keyword in duplication_keywords:
            if re.search(keyword, content, re.IGNORECASE):
                violations.append("CORE-035: Potential duplication detected")
                break

        return violations


# AC_COMPLETE: AC-PHASE41-002, AC-PHASE41-005 ✅ Extraction engine operational
