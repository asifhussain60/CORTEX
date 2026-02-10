"""
AC-PHASE72-002: Unified Digest-Ingest MCP Tool Router

MCP tool providing intelligent routing to DIGEST or INGEST operations
through the UnifiedDigestIngestionFacade.

Enables Copilot prompts to request digest/ingest without specifying mode—
facade auto-detects and routes intelligently.

Exposed as: cortex_unified_digest_ingest
"""

from typing import Dict, Any, Optional, Literal
from cortex.orchestrators.support.unified_digest_ingest_facade import (
    UnifiedDigestIngestionFacade,
)
import logging

logger = logging.getLogger(__name__)


def cortex_unified_digest_ingest(
    source_path: str,
    source_type: Optional[Literal["chat_file", "knowledge_entry"]] = None,
    auto_process: bool = True,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Unified digest-ingest operation with intelligent routing.
    
    Processes a knowledge source (chat file or knowledge entry) through
    the appropriate orchestrator:
    - Chat files → DIGEST mode (extract enhancements)
    - Knowledge entries → INGEST mode (populate knowledge base)
    
    Auto-detection if source_type not specified:
    - Detects chat markers (User:, Assistant:, etc.) → DIGEST
    - Detects structured data (JSON, YAML, {, [, etc.) → INGEST
    
    Args:
        source_path: Path to source file to process.
        source_type: Explicit source type ('chat_file' or 'knowledge_entry').
                    If None, auto-detects based on content.
        auto_process: Enable auto-processing (auto-apply enhancements for DIGEST,
                     auto-ingest valid entries for INGEST).
        dry_run: Simulate processing without making changes.
        
    Returns:
        Dictionary with operation results:
        {
            "success": bool,
            "processing_mode": "digest" | "ingest",
            "source_file": str,
            "items_processed": int,
            "items_successful": int,
            "items_failed": int,
            "confidence_score": float,
            "error_message": str,
            "metadata": dict
        }
        
    Examples:
        # Auto-detect and process
        result = cortex_unified_digest_ingest("session.md")
        
        # Explicitly process as chat file
        result = cortex_unified_digest_ingest(
            "copilot_chat.md",
            source_type="chat_file"
        )
        
        # Explicitly process as knowledge entry
        result = cortex_unified_digest_ingest(
            "enhancements.json",
            source_type="knowledge_entry"
        )
        
        # Dry-run to preview processing
        result = cortex_unified_digest_ingest(
            "test.md",
            dry_run=True
        )
    """
    # AC_START: AC-PHASE72-002
    try:
        facade = UnifiedDigestIngestionFacade()

        if dry_run:
            logger.info(f"[DRY-RUN] Would process: {source_path}")
            # For dry-run, just return mode detection result
            from pathlib import Path

            source = Path(source_path)
            if not source.exists():
                return {
                    "success": False,
                    "processing_mode": "unknown",
                    "source_file": source_path,
                    "error_message": f"[DRY-RUN] File not found: {source_path}",
                    "items_processed": 0,
                    "items_successful": 0,
                    "items_failed": 0,
                    "confidence_score": 0.0,
                    "metadata": {"dry_run": True},
                }

            content = source.read_text(encoding="utf-8")
            mode = facade.detect_mode(content, source_type)
            return {
                "success": True,
                "processing_mode": mode.value,
                "source_file": source_path,
                "error_message": f"[DRY-RUN] Would process as {mode.value}",
                "items_processed": 0,
                "items_successful": 0,
                "items_failed": 0,
                "confidence_score": 0.0,
                "metadata": {"dry_run": True, "detected_mode": mode.value},
            }

        # Process through facade (actual execution)
        result = facade.process_knowledge_source(
            source_path=source_path,
            source_type=source_type,
            auto_process=auto_process,
        )

        # Convert to MCP response format
        return result.to_dict()

    except Exception as e:
        logger.error(f"Error in unified digest-ingest: {e}", exc_info=True)
        return {
            "success": False,
            "processing_mode": "error",
            "source_file": source_path,
            "error_message": f"Processing error: {str(e)}",
            "items_processed": 0,
            "items_successful": 0,
            "items_failed": 0,
            "confidence_score": 0.0,
            "metadata": {"error": type(e).__name__},
        }
    # AC_COMPLETE: AC-PHASE72-002 ✅


# MCP Tool Metadata Registration
__mcp_tool__ = {
    "name": "cortex_unified_digest_ingest",
    "description": "Process knowledge source (chat file or entry) with intelligent routing",
    "parameters": {
        "source_path": {
            "type": "string",
            "description": "Path to source file (chat file or knowledge entry)",
            "required": True,
        },
        "source_type": {
            "type": "string",
            "enum": ["chat_file", "knowledge_entry", None],
            "description": "Explicit source type (auto-detected if not specified)",
            "required": False,
        },
        "auto_process": {
            "type": "boolean",
            "description": "Enable auto-processing (default: true)",
            "required": False,
            "default": True,
        },
        "dry_run": {
            "type": "boolean",
            "description": "Simulate processing without making changes (default: false)",
            "required": False,
            "default": False,
        },
    },
    "response_format": {
        "success": "boolean - Operation succeeded",
        "processing_mode": "string - 'digest' or 'ingest'",
        "source_file": "string - Source file path",
        "items_processed": "integer - Total items processed",
        "items_successful": "integer - Successfully processed items",
        "items_failed": "integer - Failed items",
        "confidence_score": "float - Confidence/success rate (0.0-1.0)",
        "error_message": "string - Error message if failed",
        "metadata": "object - Additional operation metadata",
    },
    "examples": [
        {
            "description": "Auto-detect and process",
            "parameters": {"source_path": "session.md"},
        },
        {
            "description": "Process as chat file",
            "parameters": {
                "source_path": "copilot_chat.md",
                "source_type": "chat_file",
            },
        },
        {
            "description": "Dry-run preview",
            "parameters": {"source_path": "test.md", "dry_run": True},
        },
    ],
}
