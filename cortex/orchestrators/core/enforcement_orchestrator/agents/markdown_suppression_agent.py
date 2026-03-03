"""
MarkdownSuppressionAgent and ResponseContentValidationAgent.

Extracted from enforcement_orchestrator.py (Phase 103-e god-object decomposition).
Rules: CORE-002, CORE-002-RESPONSE.

Author: Asif Hussain
AC-ID: AC-P103E-AGENT-006
"""

from __future__ import annotations

import re
from typing import Any, Dict, List

from cortex.orchestrators.core.enforcement_orchestrator.models import (
    EnforcementLevel,
    EnforcementResult,
)


class MarkdownSuppressionAgent:
    """
    Enforces CORE-002 (no markdown file generation).

    Blocks generation of:
    - *-summary.md
    - *-report.md
    - *-plan.md
    - DEPLOYMENT-*.md
    - Root directory markdown (except README.md, docs/, cortex-registry/)

    Unless user explicitly requests them (user_explicit_request=True).

    Phase 71 S1: Enhanced with root directory validation to prevent pollution.
    """

    def validate(self, context: Dict[str, Any]) -> EnforcementResult:
        """
        Validate markdown file generation restrictions.

        Args:
            context: Operation context including:
                - output_files: List of files to be generated (optional)
                - user_explicit_request: Whether user explicitly requested markdown (optional)

        Returns:
            EnforcementResult with BLOCKED (forbidden pattern) or PASS
        """
        violations: List[str] = []

        # Skip if user explicitly requested markdown files
        if context.get("user_explicit_request", False):
            return EnforcementResult(
                level=EnforcementLevel.PASS,
                violations=[],
                warnings=[],
                metadata={
                    "agent": "MarkdownSuppressionAgent",
                    "rules_checked": ["CORE-002"],
                    "explicit_request": True,
                },
            )

        output_files = context.get("output_files", [])
        forbidden_patterns = [
            ("-summary.md", "summary"),
            ("-report.md", "report"),
            ("-plan.md", "plan"),
            ("DEPLOYMENT-", "deployment guide"),
        ]

        # CORE-002 ENFORCEMENT: ONLY 3 allowed paths for .md files
        # Updated 2026-02-10: docs/ NO LONGER ALLOWED (inline only)
        allowed_md_paths = [
            ".github/prompts/",
            ".github/agents/",
            "README.md",
        ]

        for file in output_files:
            file_lower = file.lower()

            if file.endswith(".md") or file.endswith(".MD"):
                is_allowed = False

                if file.strip("/") == "README.md":
                    is_allowed = True
                else:
                    for allowed_path in allowed_md_paths:
                        if allowed_path.endswith("/") and file.startswith(allowed_path):
                            is_allowed = True
                            break

                if not is_allowed:
                    pattern_matched = False
                    for pattern, description in forbidden_patterns:
                        if pattern.lower() in file_lower:
                            violations.append(
                                f"CORE-002 VIOLATION: Cannot generate {description} markdown file: {file}. "
                                "Results must be reported inline in chat."
                            )
                            pattern_matched = True
                            break

                    if not pattern_matched:
                        violations.append(
                            f"CORE-002 VIOLATION: Cannot generate markdown file: {file}. "
                            "ONLY allowed: .github/prompts/*.md, .github/agents/*.md, README.md. "
                            "All findings must be inline in chat or stored in cortex-registry YAML files."
                        )

        level = EnforcementLevel.BLOCKED if violations else EnforcementLevel.PASS

        return EnforcementResult(
            level=level,
            violations=violations,
            warnings=[],
            metadata={
                "agent": "MarkdownSuppressionAgent",
                "rules_checked": ["CORE-002"],
                "output_files_count": len(output_files),
                "violations_count": len(violations),
            },
        )


class ResponseContentValidationAgent:
    """
    Enforces CORE-002-RESPONSE: No markdown file suggestions in response text.

    Validates response CONTENT (not just output_files) for forbidden patterns:
    - "cat > *.md" suggestions
    - "create_file" recommendations for .md files
    - "save this as" patterns
    - "generate markdown" instructions

    Complements MarkdownSuppressionAgent (validates output_files list).

    Phase: CORTEX Inline-First (Response-Level Gate)
    Authority: CORE-002-RESPONSE (new sub-rule for chat responses)
    """

    # Forbidden patterns that suggest markdown file creation
    FORBIDDEN_PATTERNS = [
        r"cat\s*>\s*[^\s]+\.md",
        r"cat\s*>>\s*[^\s]+\.md",
        r"echo\s+.+>\s*[^\s]+\.md",
        r"printf\s+.+>\s*[^\s]+\.md",
        r"create_file\s*\(\s*['\"][^'\"]*\.md['\"]",
        r"create\s+.*\.md.*file",
        r"generate.*markdown.*report",
        r"save\s+.*as\s+.*\.md",
        r"write\s+.*to\s+.*\.md",
        r"output\s+.*to\s+.*\.md",
        r"generated?\s+.*\.md.*file",
    ]

    ALLOWED_CONTEXTS = [
        ".github/prompts/",
        ".github/agents/",
        "README.md",
    ]

    def validate(self, context: Dict[str, Any]) -> EnforcementResult:
        """
        Validate response content for markdown file suggestions.

        Args:
            context: Operation context including:
                - response_text: The response being validated (required)
                - allow_markdown_suggestions: Override to allow (optional, default False)

        Returns:
            EnforcementResult with BLOCKED if violations, PASS otherwise
        """
        violations: List[str] = []
        response_text = context.get("response_text", "")
        allow_markdown = context.get("allow_markdown_suggestions", False)

        if allow_markdown:
            return EnforcementResult(
                level=EnforcementLevel.PASS,
                violations=[],
                warnings=[],
                metadata={
                    "agent": "ResponseContentValidationAgent",
                    "rules_checked": ["CORE-002-RESPONSE"],
                    "explicit_override": True,
                },
            )

        if not response_text:
            return EnforcementResult(
                level=EnforcementLevel.PASS,
                violations=[],
                warnings=[],
                metadata={
                    "agent": "ResponseContentValidationAgent",
                    "rules_checked": ["CORE-002-RESPONSE"],
                    "response_length": 0,
                },
            )

        for pattern in self.FORBIDDEN_PATTERNS:
            matches = re.finditer(pattern, response_text, re.IGNORECASE)
            for match in matches:
                matched_text = match.group(0)

                is_allowed = False
                for allowed_ctx in self.ALLOWED_CONTEXTS:
                    if allowed_ctx in matched_text:
                        is_allowed = True
                        break

                if not is_allowed:
                    violations.append(
                        f"CORE-002-RESPONSE VIOLATION: Response suggests markdown file creation: "
                        f"'{matched_text}'. Use inline chat display instead."
                    )

        level = EnforcementLevel.BLOCKED if violations else EnforcementLevel.PASS

        return EnforcementResult(
            level=level,
            violations=violations,
            warnings=[],
            metadata={
                "agent": "ResponseContentValidationAgent",
                "rules_checked": ["CORE-002-RESPONSE"],
                "response_length": len(response_text),
                "violations_count": len(violations),
                "patterns_checked": len(self.FORBIDDEN_PATTERNS),
            },
        )

    @staticmethod
    def transform_response_to_inline(response_text: str) -> str:
        """
        Transform response that suggests file creation to inline-only alternatives.

        Args:
            response_text: Original response

        Returns:
            Transformed response suggesting inline display
        """
        transformed = response_text

        transformed = re.sub(
            r"(?i)(use\s+)?create_file\s*\(\s*['\"]([^'\"]*\.md)['\"]",
            r"Display the content inline in this chat (don't create files)",
            transformed,
        )

        transformed = re.sub(
            r"(?i)cat\s*>\s*([^\s]+\.md)",
            r"Display the content inline in this chat instead of file output",
            transformed,
        )

        transformed = re.sub(
            r"(?i)save\s+.*as\s+.*\.md",
            r"Display the result inline; user can save chat transcript if needed",
            transformed,
        )

        transformed = re.sub(
            r"(?i)generate\s+.*markdown.*report",
            r"Display findings as a markdown table inline in chat",
            transformed,
        )

        return transformed
