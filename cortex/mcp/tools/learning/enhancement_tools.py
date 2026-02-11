"""
DIGEST Enhancement MCP Tools.

Phase 41 Stage 5 (ENH-054):
MCP tools for automated enhancement generation from DIGEST results.

AC_START: AC-PHASE41-020
Description: YAML generation MCP tools

Tools:
- cortex_digest_generate_enhancements: Generate ENH-* candidates from DigestResult
- cortex_digest_check_duplicates: Check candidate against history
- cortex_digest_apply_enhancements: Save approved candidates

Author: Asif Hussain
Date: 2026-02-07
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from mcp.server.models import Tool
from mcp.server.stdio import stdio_server

from cortex.learning.digest.models import DigestResult
from cortex.orchestrators.learning.digest_enhancement_orchestrator import (
    DigestEnhancementOrchestrator,
)

logger = logging.getLogger(__name__)


async def cortex_digest_generate_enhancements(
    arguments: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate ENH-* enhancement candidates from DIGEST result.

    AC_START: AC-PHASE41-020
    Description: Generate ENH-* YAML candidates via MCP

    Args:
        arguments: Dict with keys:
            - digest_result: DigestResult dict (serialized)
            - roi_threshold: float (optional, default 0.3)
            - similarity_threshold: float (optional, default 0.7)
            - auto_approve: bool (optional, default False)

    Returns:
        Dict with keys:
            - candidates: List[Dict] (serialized candidates)
            - unique_count: int
            - duplicate_count: int
            - approval_prompt: str
            - saved_files: List[str] (if auto_approve=True)
    """
    try:
        # Extract arguments
        digest_data = arguments.get("digest_result", {})
        roi_threshold = arguments.get("roi_threshold", 0.3)
        similarity_threshold = arguments.get("similarity_threshold", 0.7)
        auto_approve = arguments.get("auto_approve", False)

        # Reconstruct DigestResult
        digest_result = DigestResult(**digest_data)

        # Initialize orchestrator
        orchestrator = DigestEnhancementOrchestrator(
            roi_threshold=roi_threshold,
            similarity_threshold=similarity_threshold
        )

        # Run pipeline
        results = orchestrator.run_pipeline(
            digest_result,
            auto_approve=auto_approve
        )

        # Serialize candidates for response
        candidates_serialized = [
            {
                "enh_id": c.enh_id,
                "description": c.description,
                "category": c.category,
                "roi_score": c.roi_score,
                "priority": c.priority,
                "status": c.status,
                "impact": c.impact,
                "effort_days": c.effort_days
            }
            for c in results["sorted"]
        ]

        # Build response
        response = {
            "candidates": candidates_serialized,
            "unique_count": len(results["unique"]),
            "duplicate_count": len(results["duplicates"]),
            "approval_prompt": results["approval_prompt"],
            "pipeline_duration_seconds": results["pipeline_duration_seconds"]
        }

        # Include saved files if auto-approved
        if "saved_files" in results:
            response["saved_files"] = [str(p) for p in results["saved_files"]]

        logger.info(
            f"Generated {len(candidates_serialized)} enhancement candidates "
            f"({results['unique_count']} unique, {results['duplicate_count']} duplicates)"
        )

        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(response, indent=2)
                }
            ]
        }

    except Exception as e:
        logger.error(f"Failed to generate enhancements: {e}", exc_info=True)
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error: {str(e)}"
                }
            ],
            "isError": True
        }


async def cortex_digest_check_duplicates(
    arguments: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Check enhancement candidate for duplicates against history.

    AC_START: AC-PHASE41-021
    Description: Deduplication checking via MCP

    Args:
        arguments: Dict with keys:
            - description: str (candidate description)
            - history_file: str (path to enhancement-history.yaml)
            - threshold: float (optional, default 0.7)

    Returns:
        Dict with keys:
            - is_duplicate: bool
            - message: str
    """
    try:
        description = arguments.get("description", "")
        history_file = Path(arguments.get("history_file", "docs/meta/enhancement-history.yaml"))
        threshold = arguments.get("threshold", 0.7)

        if not description:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": "Error: description is required"
                    }
                ],
                "isError": True
            }

        # Initialize similarity checker
        from cortex.learning.digest.similarity_checker import SimilarityChecker
        checker = SimilarityChecker()

        # Check for duplicates
        is_duplicate = checker.check_history(
            description,
            history_file,
            threshold=threshold
        )

        message = "Duplicate detected" if is_duplicate else "No duplicates found"

        response = {
            "is_duplicate": is_duplicate,
            "message": message,
            "threshold": threshold
        }

        logger.info(f"Duplicate check: {message}")

        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(response, indent=2)
                }
            ]
        }

    except Exception as e:
        logger.error(f"Failed to check duplicates: {e}", exc_info=True)
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error: {str(e)}"
                }
            ],
            "isError": True
        }


async def cortex_digest_apply_enhancements(
    arguments: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Save approved enhancement candidates as ENH-*.yaml files.

    AC_START: AC-PHASE41-022
    Description: Save approved ENH-* candidates via MCP

    Args:
        arguments: Dict with keys:
            - candidates: List[Dict] (serialized EnhancementCandidates)
            - approved_ids: List[str] (list of ENH-XXX to save)
            - enhancement_dir: str (optional, directory to save files)

    Returns:
        Dict with keys:
            - saved_files: List[str]
            - count: int
    """
    try:
        candidates_data = arguments.get("candidates", [])
        approved_ids = arguments.get("approved_ids", [])
        enhancement_dir = Path(arguments.get("enhancement_dir", "docs/meta/enhancements"))

        if not candidates_data:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": "Error: candidates list is required"
                    }
                ],
                "isError": True
            }

        if not approved_ids:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": "Error: approved_ids list is required"
                    }
                ],
                "isError": True
            }

        # Reconstruct EnhancementCandidates
        from cortex.learning.digest.enhancement_generator import EnhancementCandidate
        candidates = [EnhancementCandidate(**c) for c in candidates_data]

        # Initialize orchestrator
        orchestrator = DigestEnhancementOrchestrator(
            enhancement_dir=enhancement_dir
        )

        # Save approved candidates
        saved_files = orchestrator.save_approved(candidates, approved_ids)

        response = {
            "saved_files": [str(p) for p in saved_files],
            "count": len(saved_files)
        }

        logger.info(f"Saved {len(saved_files)} enhancement files")

        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(response, indent=2)
                }
            ]
        }

    except Exception as e:
        logger.error(f"Failed to apply enhancements: {e}", exc_info=True)
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error: {str(e)}"
                }
            ],
            "isError": True
        }


# Tool definitions for MCP server
ENHANCEMENT_TOOLS = [
    Tool(
        name="cortex_digest_generate_enhancements",
        description=(
            "Generate ENH-* enhancement candidates from DIGEST result. "
            "Runs 5-stage pipeline: extract insights → generate candidates → "
            "deduplicate → score → present for approval."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "digest_result": {
                    "type": "object",
                    "description": "DigestResult dict (serialized)"
                },
                "roi_threshold": {
                    "type": "number",
                    "description": "Minimum ROI threshold (0.0-1.0)",
                    "default": 0.3
                },
                "similarity_threshold": {
                    "type": "number",
                    "description": "Cosine similarity threshold for duplicates",
                    "default": 0.7
                },
                "auto_approve": {
                    "type": "boolean",
                    "description": "Auto-approve all candidates (testing only)",
                    "default": False
                }
            },
            "required": ["digest_result"]
        }
    ),
    Tool(
        name="cortex_digest_check_duplicates",
        description=(
            "Check enhancement candidate for duplicates against history. "
            "Uses semantic similarity (sentence-transformers) to detect near-duplicates."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "description": {
                    "type": "string",
                    "description": "Enhancement description to check"
                },
                "history_file": {
                    "type": "string",
                    "description": "Path to enhancement-history.yaml"
                },
                "threshold": {
                    "type": "number",
                    "description": "Similarity threshold (0.0-1.0)",
                    "default": 0.7
                }
            },
            "required": ["description"]
        }
    ),
    Tool(
        name="cortex_digest_apply_enhancements",
        description=(
            "Save approved enhancement candidates as ENH-*.yaml files. "
            "Creates complete YAML files with all required metadata."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "candidates": {
                    "type": "array",
                    "description": "List of serialized EnhancementCandidate dicts",
                    "items": {"type": "object"}
                },
                "approved_ids": {
                    "type": "array",
                    "description": "List of ENH-XXX IDs to save",
                    "items": {"type": "string"}
                },
                "enhancement_dir": {
                    "type": "string",
                    "description": "Directory to save ENH-*.yaml files"
                }
            },
            "required": ["candidates", "approved_ids"]
        }
    )
]

# AC_COMPLETE: AC-PHASE41-020 ✅ Enhancement generation MCP tools
