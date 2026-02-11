"""
MCP Tool Wrapper for INTERACTIVE Mode

Purpose: Expose InteractionOrchestrator.engage_interactive_mode() as an MCP tool
for conversational guidance without TDD triggers.

Authority: ENH-034 (INTERACTIVE Mode Addition)
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def cortex_interactive_mode(
    user_question: str,
    conversation_context: Optional[Dict[str, Any]] = None,
    auto_challenge: bool = True,
) -> Dict[str, Any]:
    """
    MCP Tool: INTERACTIVE mode for exploratory conversations.

    Engages InteractionOrchestrator to provide evidence-based recommendations
    without triggering TDD or implementation workflows.

    Args:
        user_question: User's question, recommendation request, or inquiry
        conversation_context: Prior conversation history for multi-turn support
        auto_challenge: Whether to generate challenges when CORTEX disagrees

    Returns:
        {
            "status": "success" | "error",
            "recommendation": str,
            "alternatives": [
                {
                    "name": str,
                    "description": str,
                    "rationale": str,
                    "pros": [str, ...],
                    "cons": [str, ...],
                    "when_to_use": str,
                },
                ...
            ],
            "evidence": [
                {
                    "description": str,
                    "file_path": str,
                    "lines": str,
                    "snippet": str,
                },
                ...
            ],
            "tradeoffs": {
                "factor": {
                    "recommendation": float,  # 0.0-1.0
                    "alternative_1": float,
                    "alternative_2": float,
                },
                ...
            },
            "challenge_generated": bool,
            "challenge_reasoning": Optional[str],
            "next_steps": [str, ...],
            "can_transition_to_design": bool,
        }

    Examples:
        >>> result = cortex_interactive_mode(
        ...     user_question="How should I handle authentication in microservices?"
        ... )
        >>> print(result["recommendation"])
        'JWT-based token authentication with...'

        >>> result = cortex_interactive_mode(
        ...     user_question="What's your take on event-driven architecture?",
        ...     auto_challenge=True
        ... )
        >>> if result["challenge_generated"]:
        ...     print(result["challenge_reasoning"])
    """
    try:
        # Import here to avoid circular imports
        from cortex.brain.core.orchestrator.conversation_protocol import (
            ConversationProtocol,
        )
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        # Create ConversationProtocol (with default parameters)
        protocol = ConversationProtocol(
            orchestrator=None,  # Will be set by wiring system
            max_turns=10,
            token_limit=20000,
            adaptive_turn_limit=True,
            memoization_enabled=True
        )

        # Instantiate orchestrator with protocol
        orchestrator = InteractionOrchestrator(
            conversation_protocol=protocol,
            enable_challenges=auto_challenge
        )

        # Call standalone method for INTERACTIVE mode
        result = orchestrator.engage_interactive_mode(
            user_question=user_question,
            conversation_context=conversation_context or {},
            auto_challenge=auto_challenge,
        )

        logger.info(f"INTERACTIVE mode engaged for question: {user_question[:50]}...")

        # Ensure result is a dict before unpacking
        if isinstance(result, dict):
            return {
                "status": "success",
                **result,  # Orchestrator returns properly structured dict
            }
        else:
            return {
                "status": "success",
                "recommendation": str(result),
                "alternatives": [],
                "evidence": [],
                "tradeoffs": {},
                "challenge_generated": False,
                "next_steps": [],
                "can_transition_to_design": False,
            }

    except ImportError as e:
        logger.error(f"Failed to import InteractionOrchestrator: {e}")
        return {
            "status": "error",
            "message": "InteractionOrchestrator not available",
            "error": str(e),
        }

    except Exception as e:
        logger.error(f"Error in INTERACTIVE mode: {e}", exc_info=True)
        return {
            "status": "error",
            "message": "Failed to generate recommendation",
            "error": str(e),
        }


# MCP Tool Metadata (for registration in wiring.yaml)
TOOL_METADATA = {
    "name": "cortex_interactive_mode",
    "description": "Engage INTERACTIVE mode for exploratory conversations without TDD triggers",
    "parameters": {
        "user_question": {
            "type": "string",
            "description": "User's question, recommendation request, or inquiry",
            "required": True,
        },
        "conversation_context": {
            "type": "object",
            "description": "Optional prior conversation history for multi-turn support",
            "required": False,
        },
        "auto_challenge": {
            "type": "boolean",
            "description": "Whether to generate challenges when CORTEX disagrees (default: true)",
            "required": False,
        },
    },
    "returns": {
        "type": "object",
        "description": "Recommendation with alternatives, evidence, tradeoffs, and next steps",
    },
}
