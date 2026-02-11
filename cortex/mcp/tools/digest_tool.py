"""
AC-PHASE41-004: cortex_digest_session MCP tool exposes DIGEST functionality

MCP tool for DIGEST mode automation.

Exposes DigestSessionOrchestrator functionality via MCP interface.
"""

from typing import Any, Dict, Optional

from cortex.orchestrators.support.digest_session_orchestrator import (
    DigestSessionOrchestrator,
)


def cortex_digest_session(
    file_path: str,
    auto_apply: bool = False,
    min_confidence: float = 5.0
) -> Dict[str, Any]:
    """
    Auto-trigger DIGEST mode on chat file.

    Detects Copilot chat files, extracts enhancement proposals, and optionally
    auto-applies high-confidence enhancements.

    Args:
        file_path: Path to Copilot chat file or markdown document
        auto_apply: Auto-apply high-confidence enhancements (score ≥9)
        min_confidence: Minimum confidence score (5-10) to process file

    Returns:
        Dictionary with digest results:
        - success: bool
        - is_chat_file: bool
        - confidence_score: float
        - enhancements_found: int
        - enhancement_proposals: List[Dict]
        - auto_applied_count: int
        - review_queue_count: int
        - error_message: str (if failed)

    Example:
        >>> result = cortex_digest_session("/path/to/chat.md", auto_apply=True)
        >>> print(f"Found {result['enhancements_found']} enhancements")
        >>> print(f"Auto-applied {result['auto_applied_count']}")
    """
    try:
        orchestrator = DigestSessionOrchestrator()
        result = orchestrator.digest_session(
            file_path=file_path,
            auto_apply=auto_apply,
            min_confidence=min_confidence
        )
        return result.to_dict()
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "is_chat_file": False,
            "confidence_score": 0.0,
            "enhancements_found": 0,
            "enhancement_proposals": [],
            "auto_applied_count": 0,
            "review_queue_count": 0,
            "error_message": f"MCP tool error: {str(e)}"
        }


# MCP Tool Metadata for Registry
__mcp_tool__ = {
    "name": "cortex_digest_session",
    "description": "Auto-trigger DIGEST mode on chat file",
    "parameters": {
        "file_path": {
            "type": "string",
            "required": True,
            "description": "Path to Copilot chat file or markdown document"
        },
        "auto_apply": {
            "type": "boolean",
            "required": False,
            "default": False,
            "description": "Auto-apply high-confidence enhancements (score ≥9)"
        },
        "min_confidence": {
            "type": "number",
            "required": False,
            "default": 5,
            "description": "Minimum confidence score (5-10)"
        }
    },
    "returns": {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "is_chat_file": {"type": "boolean"},
            "confidence_score": {"type": "number"},
            "enhancements_found": {"type": "integer"},
            "enhancement_proposals": {"type": "array"},
            "auto_applied_count": {"type": "integer"},
            "review_queue_count": {"type": "integer"},
            "error_message": {"type": "string"}
        }
    }
}
