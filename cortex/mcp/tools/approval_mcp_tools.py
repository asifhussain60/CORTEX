"""
Interactive Approval MCP Tool Wrappers for Phase 41.

AC-ID: AC-PHASE41-S3-001
Purpose: Wrap approval_tools functions as MCP Tool instances

These tools enable the two-phase interactive approval workflow:
1. cortex_classify_request - Display DoR, await approval
2. cortex_approve_request - Execute approved request
3. cortex_reject_request - Reject request
4. cortex_modify_request - Modify and re-classify

Governance: CORE-011 (type hints), CORE-012 (docstrings)
"""

import logging
from typing import Any, Dict, Optional

from cortex.mcp.server import Tool, ToolDefinition, ToolParameter
from cortex.mcp.tools.approval_tools import (
    cortex_approve_request as approve_func,
)
from cortex.mcp.tools.approval_tools import (
    cortex_classify_request as classify_func,
)
from cortex.mcp.tools.approval_tools import (
    cortex_modify_request as modify_func,
)
from cortex.mcp.tools.approval_tools import (
    cortex_reject_request as reject_func,
)

logger = logging.getLogger(__name__)


class CORTEXClassifyRequestTool(Tool):
    """Classify request and display DoR for user approval."""

    @property
    def definition(self) -> ToolDefinition:
        """Get tool definition."""
        return ToolDefinition(
            name="cortex_classify_request",
            description="Classify user request, display Definition of Ready (DoR), and create approval session",
            parameters=[
                ToolParameter(
                    name="request",
                    type="string",
                    required=True,
                    description="User's natural language request"
                ),
                ToolParameter(
                    name="context",
                    type="object",
                    required=False,
                    description="Optional context dictionary (files, workspace info, etc.)"
                ),
                ToolParameter(
                    name="user_id",
                    type="string",
                    required=False,
                    description="User identifier for session isolation (default: 'default-user')"
                ),
                ToolParameter(
                    name="metadata",
                    type="object",
                    required=False,
                    description="Optional metadata to store with session"
                )
            ],
            metadata={"category": "approval", "version": "1.0", "phase": "41"}
        )

    def execute(
        self,
        request: str,
        context: Optional[Dict[str, Any]] = None,
        user_id: str = "default-user",
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Execute classification and DoR display."""
        try:
            return classify_func(
                request=request,
                context=context or {},
                user_id=user_id,
                metadata=metadata
            )
        except Exception as e:
            logger.error(f"Classify request failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": f"Classification failed: {str(e)}"
            }


class CORTEXApproveRequestTool(Tool):
    """Approve and execute request from stored session."""

    @property
    def definition(self) -> ToolDefinition:
        """Get tool definition."""
        return ToolDefinition(
            name="cortex_approve_request",
            description="Approve classified request and execute from stored approval session",
            parameters=[
                ToolParameter(
                    name="session_id",
                    type="string",
                    required=True,
                    description="Session UUID from cortex_classify_request"
                ),
                ToolParameter(
                    name="feedback",
                    type="string",
                    required=False,
                    description="Optional user feedback to incorporate"
                )
            ],
            metadata={"category": "approval", "version": "1.0", "phase": "41"}
        )

    def execute(
        self,
        session_id: str,
        feedback: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Execute approval and orchestrator invocation."""
        try:
            return approve_func(session_id=session_id, feedback=feedback)
        except Exception as e:
            logger.error(f"Approve request failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": f"Approval failed: {str(e)}"
            }


class CORTEXRejectRequestTool(Tool):
    """Reject request and abort execution."""

    @property
    def definition(self) -> ToolDefinition:
        """Get tool definition."""
        return ToolDefinition(
            name="cortex_reject_request",
            description="Reject classified request and close approval session",
            parameters=[
                ToolParameter(
                    name="session_id",
                    type="string",
                    required=True,
                    description="Session UUID from cortex_classify_request"
                ),
                ToolParameter(
                    name="reason",
                    type="string",
                    required=True,
                    description="Rejection reason for audit trail"
                )
            ],
            metadata={"category": "approval", "version": "1.0", "phase": "41"}
        )

    def execute(
        self,
        session_id: str,
        reason: str,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Execute rejection and session cleanup."""
        try:
            return reject_func(session_id=session_id, reason=reason)
        except Exception as e:
            logger.error(f"Reject request failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": f"Rejection failed: {str(e)}"
            }


class CORTEXModifyRequestTool(Tool):
    """Modify intent classification and re-generate DoR."""

    @property
    def definition(self) -> ToolDefinition:
        """Get tool definition."""
        return ToolDefinition(
            name="cortex_modify_request",
            description="Modify classified intent and re-generate DoR with corrections",
            parameters=[
                ToolParameter(
                    name="session_id",
                    type="string",
                    required=True,
                    description="Session UUID from cortex_classify_request"
                ),
                ToolParameter(
                    name="corrected_intent",
                    type="string",
                    required=False,
                    description="Corrected intent type (IMPLEMENT, FIX, REFACTOR, etc.)"
                ),
                ToolParameter(
                    name="feedback",
                    type="string",
                    required=False,
                    description="User feedback on why modification needed"
                )
            ],
            metadata={"category": "approval", "version": "1.0", "phase": "41"}
        )

    def execute(
        self,
        session_id: str,
        corrected_intent: Optional[str] = None,
        feedback: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Execute modification and re-classification."""
        try:
            return modify_func(
                session_id=session_id,
                corrected_intent=corrected_intent,
                feedback=feedback
            )
        except Exception as e:
            logger.error(f"Modify request failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": f"Modification failed: {str(e)}"
            }


def get_approval_tools() -> list:
    """
    Get all approval workflow tools for MCP server registration.

    Returns:
        List of Tool instances for approval workflow
    """
    return [
        CORTEXClassifyRequestTool(),
        CORTEXApproveRequestTool(),
        CORTEXRejectRequestTool(),
        CORTEXModifyRequestTool(),
    ]
