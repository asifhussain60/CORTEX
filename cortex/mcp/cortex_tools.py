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
from typing import Any, Dict, Optional

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
        """Execute feature discovery across CORTEX components."""
        try:
            results = {
                "orchestrators": [],
                "mcp_tools": [],
                "agents": [],
                "knowledge_areas": []
            }
            
            query_lower = query.lower()
            
            # Search orchestrators
            try:
                from cortex.orchestrators import get_orchestrator_count_by_category
                orch_counts = get_orchestrator_count_by_category()
                
                # Known orchestrator categories and their purposes
                orchestrator_map = {
                    "master": "Main coordination and routing",
                    "tdd": "Test-driven development workflow",
                    "lens": "Language→Examination→Navigation→Synthesis analysis",
                    "enforcement": "Governance rule enforcement (7-agent system)",
                    "challenge": "Generate AI-driven challenges to requests",
                    "planning": "Phase and task planning",
                    "refactoring": "Code improvement and restructuring",
                    "intent_router": "Intent classification and routing"
                }
                
                for orch_name, description in orchestrator_map.items():
                    if query_lower in orch_name or query_lower in description.lower():
                        results["orchestrators"].append({
                            "name": f"{orch_name.title()}Orchestrator",
                            "description": description,
                            "category": "core"
                        })
            except Exception as e:
                logger.debug(f"Orchestrator search skipped: {e}")
            
            # Search MCP tools
            try:
                from cortex.mcp.cortex_tools import get_cortex_tools
                tools = get_cortex_tools()
                
                for tool in tools:
                    tool_def = tool.definition
                    if (query_lower in tool_def.name.lower() or 
                        query_lower in tool_def.description.lower()):
                        results["mcp_tools"].append({
                            "name": tool_def.name,
                            "description": tool_def.description,
                            "category": tool_def.metadata.get("category", "unknown")
                        })
            except Exception as e:
                logger.debug(f"MCP tools search skipped: {e}")
            
            # Search governance agents
            if scope == "all" or scope == "governance":
                agent_map = {
                    "governance_enforcement": "TDD, type hints, docstrings enforcement",
                    "security_checkpoint": "Git discipline, audit trail integrity",
                    "compliance_validation": "Domain-specific compliance checks",
                    "file_naming_enforcement": "kebab-case enforcement, plan file validation",
                    "incremental_execution": "<500 LOC increments enforcement",
                    "markdown_suppression": "Block markdown report generation",
                    "architecture_integrity": "Versioned filenames, performance checks"
                }
                
                for agent_name, description in agent_map.items():
                    if query_lower in agent_name or query_lower in description.lower():
                        results["agents"].append({
                            "name": agent_name,
                            "description": description,
                            "category": "governance"
                        })
            
            # Search knowledge areas
            knowledge_areas = [
                {"name": "python", "description": "Python best practices, PEP standards"},
                {"name": "typescript", "description": "TypeScript patterns, type safety"},
                {"name": "security", "description": "OWASP Top 10, secure coding"},
                {"name": "tdd", "description": "Test-driven development patterns"},
                {"name": "architecture", "description": "System design, SOLID principles"},
                {"name": "performance", "description": "Optimization, profiling, caching"}
            ]
            
            for area in knowledge_areas:
                if query_lower in area["name"] or query_lower in area["description"].lower():
                    results["knowledge_areas"].append(area)
            
            # Calculate totals
            total_matches = sum(len(v) for v in results.values())
            
            return {
                "status": "success",
                "query": query,
                "scope": scope,
                "matches_found": total_matches,
                "results": results,
                "summary": {
                    "orchestrators": len(results["orchestrators"]),
                    "mcp_tools": len(results["mcp_tools"]),
                    "agents": len(results["agents"]),
                    "knowledge_areas": len(results["knowledge_areas"])
                }
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
