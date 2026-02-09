"""
MCP tool decorator for exposing functions as MCP-callable tools.

Authority: Phase 54 S4 - Intelligence layer decorator enhancement
Purpose: Auto-inject UnifiedIntelligenceContext for all MCP tools
"""

import logging
from typing import Any, Callable, Dict, Optional
from functools import wraps

logger = logging.getLogger(__name__)

# Global registry of MCP tools
MCP_TOOLS_REGISTRY: Dict[str, Dict[str, Any]] = {}


def mcp_tool(
    name: str,
    description: str,
    parameters: Optional[Dict[str, str]] = None,
    category: Optional[str] = None,
    inject_intelligence: bool = True,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator to register a function as an MCP-callable tool.
    
    ENHANCED (Phase 54 S4): Automatically injects UnifiedIntelligenceContext
    if 'unified_intelligence' not present in kwargs.
    
    Args:
        name: Unique name for the MCP tool.
        description: Human-readable description of the tool's purpose.
        parameters: Optional dict mapping parameter names to their types.
        category: Optional category for tool organization.
        inject_intelligence: Whether to inject UnifiedIntelligenceContext (default True).
    
    Returns:
        Decorator function that registers and returns the enhanced function.
    
    Raises:
        ValueError: If name is empty or not a valid identifier.
    
    Example:
        @mcp_tool(
            name="analyze_code",
            description="Analyze code structure",
            parameters={"code": "string", "depth": "int"},
            category="analysis"
        )
        def analyze_code(code: str, depth: int = 1, unified_intelligence=None) -> dict:
            \"\"\"Analyze code structure with intelligence context.\"\"\"
            return {"lines": len(code.split("\n")), "depth": depth}
    """
    if not name or not isinstance(name, str):
        raise ValueError("Tool name must be a non-empty string")
    
    if not description:
        raise ValueError("Tool description must be provided")
    
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        """Register function and return it enhanced."""
        # Store tool metadata
        metadata = {
            "name": name,
            "description": description,
            "func": func,
            "parameters": parameters or {},
            "category": category,
            "inject_intelligence": inject_intelligence,
        }
        MCP_TOOLS_REGISTRY[name] = metadata
        
        # Attach metadata to function for discovery
        func._mcp_tool_metadata = metadata
        
        # Return original function with intelligence injection
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            """Call original function with intelligence injection."""
            # Phase 54 S4: Inject unified intelligence context if not present
            if inject_intelligence and "unified_intelligence" not in kwargs:
                try:
                    from cortex.mcp.middleware.intelligence_gate import IntelligenceGate
                    from cortex.brain.knowledge.knowledge_synthesis_engine import get_synthesis_engine
                    
                    # Create synthesis engine if needed
                    synthesis_engine = get_synthesis_engine()
                    
                    # Create IntelligenceGate and synthesize context
                    gate = IntelligenceGate(synthesis_engine)
                    
                    # Get intent from kwargs or default to GENERIC
                    intent_type = kwargs.get("intent_type", "GENERIC")
                    file_path = kwargs.get("file_path", None)
                    
                    # Synthesize unified intelligence context
                    logger.debug(
                        f"AC_PHASE54-S4-001: Intelligence injection for tool '{name}' | "
                        f"Intent={intent_type}"
                    )
                    unified_context = synthesis_engine.synthesize_unified_context(
                        intent_type=intent_type,
                        file_path=file_path,
                    )
                    kwargs["unified_intelligence"] = unified_context
                    
                except Exception as e:
                    logger.warning(
                        f"AC_PHASE54-S4-001: Failed to inject intelligence for '{name}': {e}"
                    )
                    # Graceful degradation - proceed without intelligence
                    kwargs["unified_intelligence"] = None
            
            # Call original function
            return func(*args, **kwargs)
        
        # Also attach metadata to wrapper
        wrapper._mcp_tool_metadata = metadata
        
        return wrapper
    
    return decorator


def get_registered_tools() -> Dict[str, Dict[str, Any]]:
    """Get all registered MCP tools.

    Returns:
        Dictionary of registered tools.
    """
    return MCP_TOOLS_REGISTRY.copy()


def clear_tools() -> None:
    """Clear all registered MCP tools."""
    global MCP_TOOLS_REGISTRY
    MCP_TOOLS_REGISTRY.clear()


__all__ = ["mcp_tool", "get_registered_tools", "clear_tools", "MCP_TOOLS_REGISTRY"]
