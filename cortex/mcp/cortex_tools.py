"""
CORTEX MCP Tools - Challenge-driven interaction tools.

Exposes CORTEX orchestrators as MCP tools for Copilot integration:
- cortex_process_request: Challenge-driven request processing
- cortex_total_recall: Feature discovery
- cortex_challenge: LENS-based disagreement detection

Author: CORTEX Framework
"""

import json
import logging
from typing import Dict, Any, Optional

from cortex.mcp.server import Tool, ToolDefinition, ToolParameter

logger = logging.getLogger(__name__)


class CORTEXProcessRequestTool(Tool):
    """Process user request through challenge-driven InteractionOrchestrator."""

    @property
    def definition(self) -> ToolDefinition:
        """Get tool definition."""
        return ToolDefinition(
            name="cortex_process_request",
            description="Process user request through CORTEX challenge-driven interaction system",
            parameters=[
                ToolParameter(
                    name="user_request",
                    type="string", 
                    required=True,
                    description="User's natural language request"
                ),
                ToolParameter(
                    name="context",
                    type="object",
                    required=False,
                    description="Optional context dictionary"
                ),
                ToolParameter(
                    name="enable_challenge",
                    type="boolean",
                    required=False,
                    description="Whether to enable challenge system (default: true)"
                )
            ],
            metadata={"category": "orchestration", "version": "1.0"}
        )

    def execute(self, user_request: str, context: Optional[Dict[str, Any]] = None, enable_challenge: bool = True, **kwargs: Any) -> Dict[str, Any]:
        """Execute request processing with challenge system."""
        try:
            from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
            
            # Get MasterOrchestrator instance
            master = MasterOrchestrator.instance()
            
            # Process request through challenge-driven workflow
            try:
                if enable_challenge and hasattr(master, 'process_request_with_challenge'):
                    result = master.process_request_with_challenge(
                        user_request=user_request,
                        context=context or {}
                    )
                else:
                    # Fallback to standard processing
                    result = master.execute_operation(
                        operation_name="process_request",
                        parameters={"request": user_request, "context": context or {}}
                    )
                
                # Treat result as dict (most common case)
                if isinstance(result, dict):
                    return {
                        "status": "success",
                        "type": result.get("type", "execution"),
                        "result": result,
                        "challenge_generated": result.get("type") == "challenge"
                    }
                else:
                    # Treat as success with string representation
                    return {
                        "status": "success",
                        "type": "execution",
                        "result": {"data": str(result)},
                        "challenge_generated": False
                    }
            except Exception as exec_error:
                # Execution failed
                logger.error(f"Master orchestrator execution failed: {exec_error}", exc_info=True)
                return {
                    "status": "error",
                    "error": f"Execution failed: {str(exec_error)}"
                }
                
        except Exception as e:
            logger.error(f"CORTEX process request failed: {e}", exc_info=True)
            return {
                "status": "error", 
                "error": f"Failed to process request: {str(e)}"
            }


class CORTEXTotalRecallTool(Tool):
    """Feature discovery through TotalRecallAgent."""

    @property
    def definition(self) -> ToolDefinition:
        """Get tool definition."""
        return ToolDefinition(
            name="cortex_total_recall",
            description="Discover and recall CORTEX features and components",
            parameters=[
                ToolParameter(
                    name="query",
                    type="string",
                    required=True,
                    description="Feature or capability to search for"
                ),
                ToolParameter(
                    name="scope",
                    type="string",
                    required=False,
                    description="Scope: all, intent_router, governance, infrastructure, state, intelligence"
                ),
                ToolParameter(
                    name="include_usage",
                    type="boolean",
                    required=False,
                    description="Whether to include usage patterns"
                )
            ],
            metadata={"category": "knowledge", "version": "1.0"}
        )

    def execute(self, query: str, scope: str = "all", include_usage: bool = False, **kwargs: Any) -> Dict[str, Any]:
        """Execute feature discovery."""
        try:
            # Simple implementation: Search for query in orchestrators and tools
            from cortex.mcp.mcp_tools_catalog import get_mcp_tools_catalog
            
            catalog = get_mcp_tools_catalog()
            # Use catalog._tools dict directly (contains MCPToolMetadata objects)
            tools_dict = catalog._tools
            
            # Filter tools matching query
            matching_tools = [
                tool for tool in tools_dict.values()
                if query.lower() in tool.name.lower() or query.lower() in tool.description.lower()
            ]
            
            return {
                "status": "success",
                "query": query,
                "scope": scope,
                "matches_found": len(matching_tools),
                "matches": [
                    {
                        "name": t.name,
                        "description": t.description,
                        "category": t.category,
                        "status": t.status.value
                    }
                    for t in matching_tools[:10]  # Limit to 10 matches
                ],
                "total_tools_searched": len(tools_dict)
            }
            
        except Exception as e:
            logger.error(f"Total recall failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": f"Feature discovery failed: {str(e)}"
            }


class CORTEXChallengeTool(Tool):
    """Generate challenge using LENS analysis."""

    @property
    def definition(self) -> ToolDefinition:
        """Get tool definition."""
        return ToolDefinition(
            name="cortex_challenge",
            description="Generate AI-driven challenge to user request using LENS analysis",
            parameters=[
                ToolParameter(
                    name="user_request",
                    type="string",
                    required=True,
                    description="User's request to analyze for potential challenges"
                ),
                ToolParameter(
                    name="search_tools",
                    type="object",
                    required=False,
                    description="Available search tools for LENS context building"
                )
            ],
            metadata={"category": "orchestration", "version": "1.0"}
        )

    def execute(self, user_request: str, search_tools: Optional[Dict[str, Any]] = None, **kwargs: Any) -> Dict[str, Any]:
        """Execute challenge generation."""
        try:
            from cortex.orchestrators.core.challenge_engine import get_challenge_engine
            
            # Get challenge engine
            engine = get_challenge_engine()
            
            # Build LENS context
            lens_context = engine.build_lens_context(
                user_request=user_request,
                search_tools=search_tools or {}
            )
            
            # Generate challenge
            challenge = engine.generate_challenge(
                user_request=user_request,
                lens_context=lens_context
            )
            
            if challenge.has_disagreement:
                formatted_response = engine.format_challenge_response(challenge)
                return {
                    "status": "success",
                    "has_disagreement": True,
                    "disagreement_type": challenge.disagreement_type.value if challenge.disagreement_type else "unknown",
                    "user_request_interpretation": challenge.user_request_interpretation,
                    "cortex_analysis": challenge.cortex_analysis,
                    "recommended_alternative": challenge.recommended_alternative,
                    "reasoning": challenge.reasoning,
                    "evidence": challenge.evidence,
                    "options": challenge.options,
                    "formatted_message": formatted_response
                }
            else:
                return {
                    "status": "success",
                    "has_disagreement": False,
                    "message": "No disagreement detected - request appears reasonable"
                }
            
        except Exception as e:
            logger.error(f"Challenge generation failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": f"Challenge generation failed: {str(e)}"
            }


def get_cortex_tools() -> list[Tool]:
    """Get all CORTEX MCP tools."""
    # Core orchestrator tools
    core_tools = [
        CORTEXProcessRequestTool(),
        CORTEXTotalRecallTool(),
        CORTEXChallengeTool()
    ]
    
    # Phase 41: Interactive approval workflow tools
    try:
        from cortex.mcp.tools.approval_mcp_tools import get_approval_tools
        approval_tools = get_approval_tools()
        logger.info(f"Loaded {len(approval_tools)} approval workflow tools")
        return core_tools + approval_tools
    except (ImportError, Exception) as e:
        logger.warning(f"Could not load approval tools: {e}")
        return core_tools