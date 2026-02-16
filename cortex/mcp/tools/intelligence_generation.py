"""
CORTEX MCP v2 - Intelligence Test Generation Tool

Provides intelligent test generation via cortex_generate_tests.

ENFORCEMENT: All tools MUST validate orchestrator_context.
Only MasterOrchestrator can invoke directly (via cortex_process_request entry point).

AC_START: AC-WAVE-2-S6-002
"""

from typing import Any, Dict, List, Optional
from pathlib import Path

from cortex.mcp.mcp_tool_base import (
    ConsolidatedTool,
    ToolCategory,
    ToolParameter,
    ToolResult,
)


def validate_orchestrator_context(context: Optional[Dict[str, Any]]) -> None:
    """
    Validate request comes from MasterOrchestrator.
    
    Args:
        context: Orchestrator context with source information
        
    Raises:
        ValueError: If context missing or source is not MasterOrchestrator
    """
    if not context:
        raise ValueError(
            "BLOCKED: Missing orchestrator_context. All requests MUST route "
            "through MasterOrchestrator via cortex_process_request entry point. "
            "This ensures DoR validation, intent classification, CCL pre-warming, "
            "and governance enforcement."
        )
    
    source = context.get("source")
    if source != "MasterOrchestrator":
        raise ValueError(
            f"BLOCKED: Request from '{source}'. Only MasterOrchestrator can "
            "invoke MCP tools directly. Use cortex_process_request entry point."
        )


class CortexGenerateTests(ConsolidatedTool):
    """
    Intelligent test generation powered by multi-strategy analysis.
    
    Combines:
    - Blind spot detection (coverage gaps)
    - Edge case generation (boundary values, null checks)
    - Security testing (OWASP vulnerabilities)
    - Value-based prioritization (P0-P3)
    """
    
    @property
    def name(self) -> str:
        return "cortex_generate_tests"
    
    @property
    def description(self) -> str:
        return (
            "Generate intelligent test suites using multi-strategy analysis. "
            "Detects blind spots, edge cases, and security vulnerabilities. "
            "Prioritizes tests by value score (P0-CRITICAL to P3-LOW)."
        )
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.OPERATIONS
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="target",
                type="string",
                description="Target function name or API endpoint",
                required=True,
            ),
            ToolParameter(
                name="target_type",
                type="string",
                description="Type of target: 'function' or 'endpoint'",
                required=True,
                enum=["function", "endpoint"],
            ),
            ToolParameter(
                name="file_path",
                type="string",
                description="Path to file containing target",
                required=True,
            ),
            ToolParameter(
                name="parameters",
                type="array",
                description="List of parameter names",
                required=False,
            ),
            ToolParameter(
                name="parameter_constraints",
                type="object",
                description="Constraints for parameters (type_hint, min/max values, nullable)",
                required=False,
            ),
            ToolParameter(
                name="has_database_access",
                type="boolean",
                description="Whether target accesses database",
                required=False,
            ),
            ToolParameter(
                name="requires_authentication",
                type="boolean",
                description="Whether target requires authentication",
                required=False,
            ),
            ToolParameter(
                name="coverage_data",
                type="object",
                description="Coverage data for blind spot detection",
                required=False,
            ),
            ToolParameter(
                name="min_value_score",
                type="number",
                description="Minimum value score threshold (default: 70.0)",
                required=False,
            ),
        ]
    
    @property
    def supported_operations(self) -> List[str]:
        """Supported operations (single operation tool)."""
        return ["generate"]
    
    async def execute(self, **params) -> ToolResult:
        """Execute intelligent test generation."""
        # ENFORCEMENT: Validate orchestrator routing
        validate_orchestrator_context(params.get("orchestrator_context"))
        
        try:
            # Validate required parameters
            target = params.get("target")
            target_type = params.get("target_type")
            file_path = params.get("file_path")
            
            if not target or not target_type or not file_path:
                return ToolResult(
                    success=False,
                    data=None,
                    error="Missing required parameters: target, target_type, file_path",
                    metadata={"required_params": ["target", "target_type", "file_path"]},
                )
            
            # Validate target_type
            if target_type not in ["function", "endpoint"]:
                return ToolResult(
                    success=False,
                    data=None,
                    error=f"Invalid target_type: {target_type}. Must be 'function' or 'endpoint'.",
                    metadata={"valid_types": ["function", "endpoint"]},
                )
            
            # Import IntelligentTestGenerator
            from cortex.orchestrators.intelligence.intelligent_test_generator import (
                IntelligentTestGenerator,
                TestGenerationRequest,
            )
            
            # Build request
            request = TestGenerationRequest(
                target_type=target_type,
                target_name=target,
                file_path=Path(file_path),
                parameters=params.get("parameters", []),
                parameter_constraints=params.get("parameter_constraints"),
                has_database_access=params.get("has_database_access", False),
                requires_authentication=params.get("requires_authentication", False),
                requires_authorization=params.get("requires_authorization", []),
                returns_user_content=params.get("returns_user_content", False),
                executes_system_commands=params.get("executes_system_commands", False),
                accesses_filesystem=params.get("accesses_filesystem", False),
                coverage_data=params.get("coverage_data"),
            )
            
            # Initialize generator
            min_value_score = params.get("min_value_score", 70.0)
            generator = IntelligentTestGenerator(min_value_score=min_value_score)
            
            # Generate tests
            result = generator.generate_tests(request)
            
            # Format result
            tests_data = [
                {
                    "name": test.name,
                    "source": test.source,
                    "description": test.description,
                    "priority": test.priority,
                    "value_score": test.value_score,
                }
                for test in result.tests
            ]
            
            return ToolResult(
                success=True,
                data={
                    "tests": tests_data,
                    "total_generated": result.total_generated,
                    "high_priority_count": result.high_priority_count,
                    "target": target,
                    "target_type": target_type,
                    "file_path": file_path,
                },
                metadata={
                    "orchestrator": "IntelligentTestGenerator",
                    "min_value_score": min_value_score,
                    "strategies": ["blind_spots", "edge_cases", "security"],
                },
            )
            
        except ImportError as e:
            return ToolResult(
                success=False,
                data=None,
                error=f"IntelligentTestGenerator not available: {e}",
                metadata={"import_error": str(e)},
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                error=f"Test generation failed: {e}",
                metadata={"exception_type": type(e).__name__},
            )


# Export tool
__all__ = ["CortexGenerateTests"]

# AC_COMPLETE: AC-WAVE-2-S6-002 ✅
# Implementation: cortex_generate_tests MCP tool
