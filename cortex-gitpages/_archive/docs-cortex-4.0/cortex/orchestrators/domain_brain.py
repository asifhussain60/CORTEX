"""Domain brain orchestrator for business knowledge operations."""

from typing import Any, Dict, List, Optional
from cortex.mcp.decorators import mcp_tool


@mcp_tool(
    name="get_relevant_business_knowledge_for_operation",
    description="Get relevant business knowledge for a specific operation",
    parameters={"operation_id": "string", "context": "dict"}
)
def get_relevant_business_knowledge_for_operation(
    operation_id: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Retrieve relevant business knowledge for a given operation.
    
    Args:
        operation_id: Unique identifier for the operation.
        context: Optional execution context containing operation metadata.
    
    Returns:
        Dictionary containing relevant knowledge, sources, and confidence scores.
    
    Example:
        knowledge = get_relevant_business_knowledge_for_operation(
            operation_id="OP-123",
            context={"domain": "finance", "urgency": "high"}
        )
    """
    if not operation_id:
        raise ValueError("operation_id must be provided")
    
    if context is None:
        context = {}
    
    # Retrieve knowledge from domain brain
    knowledge: Dict[str, Any] = {
        "operation_id": operation_id,
        "sources": [],
        "knowledge": {},
        "confidence": 0.0,
    }
    
    # Query tier 3 knowledge registry
    domain = context.get("domain", "general")
    knowledge["domain"] = domain
    
    # Fetch relevant knowledge entries
    knowledge["sources"] = _get_knowledge_sources(operation_id, domain)
    knowledge["knowledge"] = _synthesize_knowledge(operation_id, context)
    knowledge["confidence"] = _calculate_confidence(knowledge["sources"])
    
    return knowledge


def _get_knowledge_sources(operation_id: str, domain: str) -> List[str]:
    """Get list of knowledge sources for operation."""
    # This will be populated from tier 3 knowledge registry
    return [f"domain_knowledge_{domain}", f"operation_context_{operation_id}"]


def _synthesize_knowledge(
    operation_id: str,
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """Synthesize knowledge from multiple sources."""
    return {
        "operation_context": context,
        "related_operations": [],
        "best_practices": [],
        "constraints": [],
    }


def _calculate_confidence(sources: List[str]) -> float:
    """Calculate confidence score based on sources."""
    # Confidence increases with more reliable sources
    if len(sources) == 0:
        return 0.0
    return min(len(sources) * 0.5, 1.0)
