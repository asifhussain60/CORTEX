"""
Phase 22 Component #9: cortex_ask MCP Tool

Educational query processing via MCP interface.
Exposes EducationalOrchestrator for truth-based learning.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from cortex.orchestrators.education.educational_orchestrator import (
    EducationalOrchestrator,
)
from cortex.orchestrators.education.truth_verification_engine import (
    TruthVerificationEngine,
)


# MCP Tool Registration (decorator added by MCP system)
def cortex_ask(
    user_query: str,
    knowledge_level: str = "beginner",
    context: Optional[Dict[str, Any]] = None,
    verify_implementation: bool = False
) -> Dict[str, Any]:
    """
    Process educational query through CORTEX ASK mode.

    Provides implementation-truth-based education about CORTEX architecture,
    with progressive disclosure and numbered next-step suggestions.

    Args:
        user_query: User's educational question
        knowledge_level: One of 'beginner', 'intermediate', 'advanced'
        context: Optional context (file paths, orchestrator names, etc.)
        verify_implementation: Whether to verify claims against live code

    Returns:
        Dict containing:
            - status: 'success' or 'error'
            - explanation: Educational response
            - next_steps: List of 3-5 numbered next-step options
            - knowledge_level: Detected/provided knowledge level
            - verification: Optional verification results
            - error: Error message if status='error'

    Examples:
        >>> result = cortex_ask("What is CORTEX?", "beginner")
        >>> result['status']
        'success'
        >>> len(result['next_steps'])
        4
    """
    # Validate input
    is_valid, error = validate_query(user_query)
    if not is_valid:
        return {
            "status": "error",
            "error": error
        }

    # Validate knowledge level
    valid_levels = ["beginner", "intermediate", "advanced"]
    if knowledge_level not in valid_levels:
        return {
            "status": "error",
            "error": f"Invalid knowledge level. Must be one of: {', '.join(valid_levels)}"
        }

    try:
        # Initialize orchestrator
        orchestrator = EducationalOrchestrator()

        # Prepare request with history that indicates knowledge level
        # The orchestrator auto-detects, but we guide it via context
        request = {
            "query": user_query,
            "history": [],
            "knowledge_level": knowledge_level  # Pass through parameter
        }

        # Execute educational processing
        result_obj = orchestrator.execute(request)

        # Unwrap Result object
        if hasattr(result_obj, 'is_ok') and result_obj.is_ok():
            result_json = result_obj.unwrap()
            # Parse JSON string
            import json
            raw_response = json.loads(result_json)
        else:
            # Result failed
            return {
                "status": "error",
                "error": str(result_obj) if hasattr(result_obj, '__str__') else "Unknown error"
            }

        # Override detected knowledge level with user-specified level
        # (orchestrator may auto-detect differently, but honor user parameter)
        raw_response["knowledge_level"] = knowledge_level

        # Format response
        formatted_response = format_educational_response(raw_response, context or {})

        # Add verification if requested
        if verify_implementation:
            verification_engine = TruthVerificationEngine()
            # Get current working directory as repo root
            repo_root = Path.cwd()

            # Extract component name from question-style query
            # "Does MasterOrchestrator exist?" → "MasterOrchestrator"
            import re
            query_for_verification = user_query
            question_match = re.search(r'(Does|Is|Has)\s+(\w+)', user_query, re.IGNORECASE)
            if question_match:
                query_for_verification = question_match.group(2)

            verification_result = verification_engine.verify_claim(
                query_for_verification,
                {"repo_root": str(repo_root)}
            )
            # Format verification result
            from cortex.orchestrators.education.truth_verification_engine import (
                VerificationStatus,
            )
            formatted_response["verification"] = {
                "verified": verification_result.status == VerificationStatus.VERIFIED,
                "confidence": verification_result.confidence,
                "evidence": verification_result.evidence,
                "refutation_reason": verification_result.refutation_reason
            }

        return formatted_response

    except Exception as e:
        return {
            "status": "error",
            "error": f"Educational processing failed: {str(e)}"
        }


def validate_query(query: str) -> Tuple[bool, Optional[str]]:
    """
    Validate user query.

    Args:
        query: User's query string

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not query or not query.strip():
        return False, "Query cannot be empty"

    if len(query) > 5000:
        return False, "Query too long (max 5000 characters)"

    return True, None


def format_educational_response(raw_response: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format raw orchestrator response for MCP output.

    Args:
        raw_response: Response from EducationalOrchestrator
        context: User-provided context dict

    Returns:
        Formatted response dict
    """
    # Format next_steps to include "query" field expected by tests
    next_steps = raw_response.get("next_steps", [])
    formatted_next_steps = []
    for step in next_steps:
        formatted_step = {
            "title": step.get("title", ""),
            "description": step.get("description", ""),
            "query": step.get("title", "")  # Use title as default query
        }
        formatted_next_steps.append(formatted_step)

    return {
        "status": "success",
        "explanation": raw_response.get("explanation", ""),
        "next_steps": formatted_next_steps,
        "knowledge_level": raw_response.get("knowledge_level", "beginner"),
        "context": context  # Pass through user context
    }


# Mark as MCP tool for registration
cortex_ask.__mcp_tool__ = True
