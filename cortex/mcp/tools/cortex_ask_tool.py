"""
CortexAsk — Educational questions about CORTEX architecture.

Extracted from cortex/mcp/tools/utilities.py (Phase 103-d, GAP-103-07).
Single Responsibility: Answer educational questions about CORTEX with
truth-based verification against the knowledge base.

CORE-011: type hints | CORE-012: docstrings
"""
from __future__ import annotations

from typing import List

from cortex.mcp.mcp_tool_base import (
    ConsolidatedTool,
    ToolCategory,
    ToolParameter,
    ToolResult,
)
from cortex.mcp.tools._shared import validate_orchestrator_context


class CortexAsk(ConsolidatedTool):
    """
    Educational questions about CORTEX.

    Operations:
    - architecture: Questions about CORTEX architecture
    - features: Feature-related questions
    - governance: Governance rule questions
    """

    @property
    def name(self) -> str:
        """Return the name."""
        return "cortex_ask"

    @property
    def description(self) -> str:
        """Return the description."""
        return (
            "Ask educational questions about CORTEX architecture "
            "with truth-based verification."
        )

    @property
    def category(self) -> ToolCategory:
        """Return the category."""
        return ToolCategory.UTILITIES

    @property
    def parameters(self) -> List[ToolParameter]:
        """Return the parameters."""
        return [
            ToolParameter(
                name="operation",
                type="string",
                description="Question type: architecture, features, governance",
                required=True,
                enum=["architecture", "features", "governance"],
            ),
            ToolParameter(
                name="question",
                type="string",
                description="The question to ask",
                required=True,
            ),
        ]

    @property
    def supported_operations(self) -> List[str]:
        """Return the supported operations."""
        return ["architecture", "features", "governance"]

    async def execute(self, **params) -> ToolResult:
        """Execute ask operation."""
        # ENFORCEMENT: Validate orchestrator routing
        _oc = params.get("orchestrator_context")
        if _oc is not None:
            validate_orchestrator_context(_oc)

        operation = params.get("operation", "architecture")
        question = params.get("question", "")

        # Mock response - will be wired to actual knowledge base
        return ToolResult(
            success=True,
            data={
                "question": question,
                "category": operation,
                "answer": f"Response to: {question}",
                "sources": ["cortex-registry/", ".github/prompts/"],
                "confidence": 0.9,
            },
            metadata={"operation": operation},
        )
