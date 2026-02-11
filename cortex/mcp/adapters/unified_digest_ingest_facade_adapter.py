"""
AC-PHASE72-003: UnifiedDigestIngestFacade MCP Adapter

MCP adapter exposing UnifiedDigestIngestionFacade capabilities.

Integrates with CORTEX MCP tool registry and orchestrator wiring system.
"""

import logging
import time
from typing import Any, Dict, List, Optional

from cortex.mcp.orchestrator_mcp_server import (
    CapabilityMetadata,
    CapabilityResponse,
    ExecutionContext,
    IOrchestratorAdapter,
)
from cortex.orchestrators.support.unified_digest_ingest_facade import (
    UnifiedDigestIngestionFacade,
)

logger = logging.getLogger(__name__)


class UnifiedDigestIngestFacadeAdapter(IOrchestratorAdapter):
    """MCP Adapter for UnifiedDigestIngestionFacade.

    Exposes capabilities:
    - process_knowledge_source: Process chat file or knowledge entry with auto-routing
    - detect_mode: Detect processing mode without processing
    - get_status: Get facade status

    CORE-035: Uses wiring system for orchestrator access (single execution path).
    """

    def __init__(self, facade: Optional[UnifiedDigestIngestionFacade] = None):
        """Initialize adapter with facade from wiring system.

        Args:
            facade: Custom facade instance (uses default if None).
        """
        self.facade = facade or UnifiedDigestIngestionFacade()

    def get_capabilities(self) -> List[CapabilityMetadata]:
        """Get all capabilities exposed by this adapter.

        Returns:
            List of CapabilityMetadata for each exposed capability.
        """
        return [
            CapabilityMetadata(
                name="process_knowledge_source",
                orchestrator="unified_digest_ingest",
                description="Process knowledge source with intelligent digest/ingest routing",
                input_schema={
                    "source_path": {
                        "type": "string",
                        "description": "Path to source file",
                    },
                    "source_type": {
                        "type": "string",
                        "enum": ["chat_file", "knowledge_entry"],
                        "description": "Optional explicit source type",
                    },
                    "auto_process": {
                        "type": "boolean",
                        "description": "Enable auto-processing",
                    },
                },
                output_schema={
                    "success": {"type": "boolean"},
                    "processing_mode": {"type": "string"},
                    "items_processed": {"type": "integer"},
                    "confidence_score": {"type": "number"},
                },
                routing_keywords=[
                    "digest",
                    "ingest",
                    "unified",
                    "process knowledge",
                ],
                tags={"phase72", "unified", "facade"},
            ),
            CapabilityMetadata(
                name="detect_mode",
                orchestrator="unified_digest_ingest",
                description="Detect processing mode from content",
                input_schema={
                    "content": {"type": "string", "description": "Content to analyze"},
                    "source_type": {
                        "type": "string",
                        "description": "Optional explicit source type",
                    },
                },
                output_schema={
                    "mode": {"type": "string", "enum": ["digest", "ingest"]},
                    "confidence": {"type": "number"},
                },
                routing_keywords=["detect", "mode", "analyze"],
                tags={"phase72", "detection"},
            ),
            CapabilityMetadata(
                name="get_status",
                orchestrator="unified_digest_ingest",
                description="Get status of digest and ingest orchestrators",
                input_schema={},
                output_schema={
                    "digest_orchestrator": {"type": "string"},
                    "ingest_pipeline": {"type": "string"},
                },
                routing_keywords=["status", "health"],
                tags={"phase72", "status"},
            ),
        ]

    def execute_capability(
        self,
        capability_name: str,
        parameters: Dict[str, Any],
        context: ExecutionContext,
    ) -> CapabilityResponse:
        """Execute a capability.

        Args:
            capability_name: Name of capability to execute.
            parameters: Parameters for capability.
            context: Execution context.

        Returns:
            CapabilityResponse with execution result.
        """
        start = time.time()
        try:
            if not self.facade:
                return CapabilityResponse(
                    request_id=context.session_id,
                    success=False,
                    error="Facade not available",
                    orchestrator="unified_digest_ingest",
                    duration_ms=(time.time() - start) * 1000,
                )

            if capability_name == "process_knowledge_source":
                source_path = parameters.get("source_path")
                if not isinstance(source_path, str):
                    return CapabilityResponse(
                        request_id=context.session_id,
                        success=False,
                        error="Invalid source_path parameter",
                        orchestrator="unified_digest_ingest",
                        duration_ms=(time.time() - start) * 1000,
                    )
                result = self.facade.process_knowledge_source(
                    source_path=source_path,
                    source_type=parameters.get("source_type"),
                    auto_process=parameters.get("auto_process", True),
                )
                return CapabilityResponse(
                    request_id=context.session_id,
                    success=result.success,
                    result=result.to_dict(),
                    orchestrator="unified_digest_ingest",
                    duration_ms=(time.time() - start) * 1000,
                )

            elif capability_name == "detect_mode":
                mode = self.facade.detect_mode(
                    content=parameters.get("content", ""),
                    source_type=parameters.get("source_type"),
                )
                return CapabilityResponse(
                    request_id=context.session_id,
                    success=True,
                    result={"mode": mode.value},
                    orchestrator="unified_digest_ingest",
                    duration_ms=(time.time() - start) * 1000,
                )

            elif capability_name == "get_status":
                status = self.facade.get_status()
                return CapabilityResponse(
                    request_id=context.session_id,
                    success=True,
                    result=status,
                    orchestrator="unified_digest_ingest",
                    duration_ms=(time.time() - start) * 1000,
                )

            else:
                return CapabilityResponse(
                    request_id=context.session_id,
                    success=False,
                    error=f"Unknown capability: {capability_name}",
                    orchestrator="unified_digest_ingest",
                    duration_ms=(time.time() - start) * 1000,
                )

        except Exception as e:
            logger.error(f"Error executing {capability_name}: {e}", exc_info=True)
            return CapabilityResponse(
                request_id=context.session_id,
                success=False,
                error=f"Execution error: {str(e)}",
                orchestrator="unified_digest_ingest",
                duration_ms=(time.time() - start) * 1000,
            )

    def validate_parameters(
        self, capability_name: str, parameters: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """Validate parameters for a capability.

        Args:
            capability_name: Name of capability.
            parameters: Parameters to validate.

        Returns:
            Tuple of (is_valid, error_message).
        """
        if capability_name == "process_knowledge_source":
            if "source_path" not in parameters:
                return False, "Missing required parameter: source_path"
            if not isinstance(parameters["source_path"], str):
                return False, "source_path must be string"
            return True, None

        elif capability_name == "detect_mode":
            if "content" not in parameters:
                return False, "Missing required parameter: content"
            if not isinstance(parameters["content"], str):
                return False, "content must be string"
            return True, None

        elif capability_name == "get_status":
            return True, None

        else:
            return False, f"Unknown capability: {capability_name}"
