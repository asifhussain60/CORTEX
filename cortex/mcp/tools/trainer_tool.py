"""
cortex_train MCP Tool — Gap-driven template evolution for CORTEX intelligence.

AC-TRAIN-MCP-001: cortex_train tool exposed via MCP
AC-TRAIN-MCP-002: Supports scan, propose, execute operations
AC-TRAIN-MCP-003: Returns structured results for Copilot Chat rendering

Operations:
- scan: Full pipeline (inventory → analyze → detect_gaps → propose)
- propose: Generate proposal from gaps
- execute: Apply approved proposal

Author: GitHub Copilot
Date: 2026-02-26
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def cortex_train(
    op: str = "scan",
    target_path: Optional[str] = None,
    gaps: Optional[Dict[str, Any]] = None,
    proposal: Optional[Dict[str, Any]] = None,
    orchestrator_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Gap-driven template evolution for CORTEX intelligence growth.

    Analyzes external repositories, detects gaps between learned patterns
    and existing workflow templates, and proposes surgical changes
    (CREATE/ENHANCE/DELETE) — never random generation.

    Args:
        op: Operation to perform. One of:
            - "scan": Full pipeline (inventory → analyze → detect_gaps → propose)
            - "propose": Generate proposal from provided gaps
            - "execute": Apply approved proposal
        target_path: Path to repository or folder to analyze (required for scan)
        gaps: Gap analysis result (required for propose operation)
        proposal: Approved proposal to execute (required for execute operation)
        orchestrator_context: Optional MasterOrchestrator context

    Returns:
        Dict with operation results:
        - scan: {inventory, analysis, gaps, proposal}
        - propose: {proposal}
        - execute: {status, executed, skipped, errors}

    Examples:
        >>> cortex_train(op="scan", target_path="path/to/target/repo")
        >>> cortex_train(op="execute", proposal={"actions": [...], "approved": True})
    """
    # Guard for orchestrator_context validation
    if orchestrator_context is not None:
        from cortex.mcp.tools._shared import validate_orchestrator_context
        validate_orchestrator_context(orchestrator_context)

    # Import TrainerOrchestrator
    try:
        from cortex.orchestrators.intelligence.trainer_orchestrator import (
            TrainerOrchestrator,
        )
    except ImportError as e:
        return {
            "status": "error",
            "error": f"Failed to import TrainerOrchestrator: {e}",
        }

    # Create orchestrator instance
    trainer = TrainerOrchestrator()

    # Route to appropriate operation
    if op == "scan":
        if not target_path:
            return {
                "status": "error",
                "error": "target_path is required for scan operation",
            }
        return trainer.execute_operation("scan", {"target_path": target_path})

    elif op == "propose":
        if not gaps:
            return {
                "status": "error",
                "error": "gaps is required for propose operation",
            }
        return trainer.execute_operation("propose", {"gaps": gaps})

    elif op == "execute":
        if not proposal:
            return {
                "status": "error",
                "error": "proposal is required for execute operation",
            }
        return trainer.execute_operation("execute", {"proposal": proposal})

    else:
        return {
            "status": "error",
            "error": f"Unknown operation: {op}",
            "supported_operations": ["scan", "propose", "execute"],
        }


def get_tool_definition() -> Dict[str, Any]:
    """
    Return MCP tool definition for cortex_train.

    Returns:
        Tool definition dict for MCP registration.
    """
    return {
        "name": "cortex_train",
        "description": (
            "Gap-driven template evolution for CORTEX intelligence growth. "
            "Analyzes external repositories, detects gaps between learned patterns "
            "and existing workflow templates, and proposes surgical changes "
            "(CREATE/ENHANCE/DELETE). Use 'scan' to analyze a repository, "
            "'propose' to generate changes from gaps, 'execute' to apply approved changes."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "op": {
                    "type": "string",
                    "enum": ["scan", "propose", "execute"],
                    "description": (
                        "Operation: 'scan' (analyze repo → propose), "
                        "'propose' (generate proposal from gaps), "
                        "'execute' (apply approved proposal)"
                    ),
                },
                "target_path": {
                    "type": "string",
                    "description": "Path to repository or folder to analyze (required for scan)",
                },
                "gaps": {
                    "type": "object",
                    "description": "Gap analysis result (required for propose operation)",
                },
                "proposal": {
                    "type": "object",
                    "description": "Approved proposal to execute (required for execute operation)",
                },
            },
            "required": ["op"],
        },
    }
