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
            
            if result.is_ok():
                output = result.unwrap()
                return {
                    "status": "success",
                    "type": output.get("type", "execution"),
                    "result": output,
                    "challenge_generated": output.get("type") == "challenge"
                }
            else:
                return {
                    "status": "error",
                    "error": str(result.unwrap_err())
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
            from cortex.tools.total_recall_agent import TotalRecallAgent, FeatureScope
            
            # Map scope string to enum
            scope_map = {
                "all": FeatureScope.ALL,
                "intent_router": FeatureScope.INTENT_ROUTER,
                "governance": FeatureScope.GOVERNANCE,
                "infrastructure": FeatureScope.INFRASTRUCTURE, 
                "state": FeatureScope.STATE,
                "intelligence": FeatureScope.INTELLIGENCE
            }
            feature_scope = scope_map.get(scope.lower(), FeatureScope.ALL)
            
            # Initialize agent and recall
            agent = TotalRecallAgent()
            result = agent.recall(
                query=query,
                scope=feature_scope,
                include_usage=include_usage
            )
            
            return {
                "status": "success",
                "query": result.query,
                "scope": result.scope.value,
                "matches_found": len(result.matches),
                "matches": [
                    {
                        "name": match.name,
                        "entry_point": match.entry_point,
                        "test_status": match.test_status,
                        "capabilities": match.capabilities[:5],  # Limit for readability
                        "usage_pattern": match.usage_pattern
                    }
                    for match in result.matches[:10]  # Limit to 10 matches
                ],
                "related_components": result.related_components[:10]
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
                    "disagreement_type": challenge.disagreement_type.value,
                    "user_interpretation": challenge.user_interpretation,
                    "cortex_analysis": challenge.cortex_analysis,
                    "better_solution": challenge.better_solution,
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
    tools = [
        CORTEXProcessRequestTool(),
        CORTEXTotalRecallTool(),
        CORTEXChallengeTool()
    ]
    
    # Add Phase 12 capacity planning tool if available
    try:
        from cortex.mcp.tools.capacity_planning import CORTEX_CAPACITY_TOOLS
        tools.extend(CORTEX_CAPACITY_TOOLS)
    except ImportError:
        logger.warning("Phase 12 capacity planning tools not available")
    
    return tools