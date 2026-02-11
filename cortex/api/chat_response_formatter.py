"""
ChatResponseFormatter - Response Header Injection Module

Wraps AI responses with standard CORTEX headers and metadata.
Ensures all responses include author, copyright, and operation context.

AC-ID: AC-REM-003-02
Issue: ISSUE-003
Governance: CORE-024 (Response Standards)
"""

import json
from datetime import datetime
from typing import Any, Dict, Optional


class ChatResponseFormatter:
    """
    Formats chat responses with CORTEX standard headers and metadata.

    Ensures:
    - All responses include required metadata (operation, phase, orchestrator, author)
    - Copyright notice is present
    - Responses remain JSON serializable
    - Original content is preserved
    - Audit trail integration
    """

    # Standard author
    AUTHOR = "Asif Hussain"

    # Standard copyright notice

    def __init__(self):
        """Initialize ChatResponseFormatter."""
        self.author = self.AUTHOR
        self.copyright = self.COPYRIGHT

    def format_response(
        self,
        content: str,
        operation: str,
        phase: str,
        orchestrator: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Format response with CORTEX headers and metadata.

        Args:
            content: The response content (plain text, markdown, etc.)
            operation: The operation being performed (e.g., "IMPLEMENTATION", "CODE_REVIEW")
            phase: The current phase (e.g., "PHASE-16", "PHASE-REMEDIATION-01")
            orchestrator: The active orchestrator (e.g., "MasterOrchestrator")
            metadata: Optional additional metadata to include

        Returns:
            Dict containing formatted response with headers

        Raises:
            ValueError: If required parameters are missing or invalid
        """
        # Validate inputs
        if not content or not isinstance(content, str):
            raise ValueError("content must be a non-empty string")
        if not operation or not isinstance(operation, str):
            raise ValueError("operation must be a non-empty string")
        if not phase or not isinstance(phase, str):
            raise ValueError("phase must be a non-empty string")
        if not orchestrator or not isinstance(orchestrator, str):
            raise ValueError("orchestrator must be a non-empty string")

        # Build response dict
        response = {
            "operation": operation,
            "phase": phase,
            "orchestrator": orchestrator,
            "author": self.author,
            "copyright": self.copyright,
            "content": content,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        # Add optional metadata if provided
        if metadata:
            if isinstance(metadata, dict):
                response["metadata"] = metadata
            else:
                raise ValueError("metadata must be a dict")

        return response

    def format_response_with_header_markdown(
        self,
        content: str,
        operation: str,
        phase: str,
        orchestrator: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Format response as markdown string with visual header.

        Useful for display purposes (not for JSON APIs).

        Args:
            content: The response content
            operation: The operation being performed
            phase: The current phase
            orchestrator: The active orchestrator
            metadata: Optional additional metadata

        Returns:
            Formatted markdown string with header
        """
        # Get the structured response
        response_dict = self.format_response(
            content=content,
            operation=operation,
            phase=phase,
            orchestrator=orchestrator,
            metadata=metadata,
        )

        # Build markdown with header
        header = (
            f"## 🧠 CORTEX {operation}\n"
            f"**Author:** {response_dict['author']} | "
            f"**Phase:** {response_dict['phase']} | "
            f"**Orchestrator:** {response_dict['orchestrator']} ✅\n\n"
            f"---\n"
            f"**{response_dict['copyright']}**\n\n"
        )

        return header + content

    def parse_formatted_response(self, response_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse a formatted response dict and extract components.

        Args:
            response_dict: A response dict from format_response()

        Returns:
            Dict with parsed components
        """
        return {
            "operation": response_dict.get("operation"),
            "phase": response_dict.get("phase"),
            "orchestrator": response_dict.get("orchestrator"),
            "author": response_dict.get("author"),
            "copyright": response_dict.get("copyright"),
            "content": response_dict.get("content"),
            "timestamp": response_dict.get("timestamp"),
            "metadata": response_dict.get("metadata"),
        }

    def validate_response_format(self, response_dict: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate that a response dict has required format.

        Args:
            response_dict: Response dict to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        required_fields = ["operation", "phase", "orchestrator", "author", "content", "copyright"]

        for field in required_fields:
            if field not in response_dict:
                return False, f"Missing required field: {field}"
            if not isinstance(response_dict[field], str):
                return False, f"Field {field} must be string, got {type(response_dict[field])}"

        # Verify copyright contains expected text
        if "Copyright © 2025-2026 Asif Hussain" not in response_dict["copyright"]:
            return False, "Copyright notice missing or incorrect"

        # Verify author is correct
        if response_dict["author"] != self.AUTHOR:
            return False, f"Author must be '{self.AUTHOR}'"

        # Verify content is not empty
        if not response_dict["content"].strip():
            return False, "Content cannot be empty"

        return True, ""

    def format_batch_responses(
        self,
        contents: list[str],
        operation: str,
        phase: str,
        orchestrator: str,
    ) -> list[Dict[str, Any]]:
        """
        Format multiple responses in batch.

        Args:
            contents: List of response contents
            operation: The operation being performed
            phase: The current phase
            orchestrator: The active orchestrator

        Returns:
            List of formatted response dicts
        """
        return [
            self.format_response(
                content=content,
                operation=operation,
                phase=phase,
                orchestrator=orchestrator,
            )
            for content in contents
        ]


def format_response_simple(
    content: str,
    operation: str,
    phase: str,
    orchestrator: str,
) -> Dict[str, Any]:
    """
    Convenience function to format a response without creating a formatter instance.

    Args:
        content: The response content
        operation: The operation being performed
        phase: The current phase
        orchestrator: The active orchestrator

    Returns:
        Formatted response dict
    """
    formatter = ChatResponseFormatter()
    return formatter.format_response(
        content=content,
        operation=operation,
        phase=phase,
        orchestrator=orchestrator,
    )
