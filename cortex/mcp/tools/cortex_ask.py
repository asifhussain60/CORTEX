"""
Phase 22 Component #9: cortex_ask MCP Tool

Educational query processing via MCP interface.
Exposes EducationalOrchestrator for truth-based learning.
"""

from typing import Dict, Any, Optional, List, Tuple
from cortex.orchestrators.education.educational_orchestrator import EducationalOrchestrator
from cortex.brain.verification.truth_verification_engine import TruthVerificationEngine


# MCP Tool Registration (decorator added by MCP system)
def cortex_ask(
    user_query: str,
    knowledge_level: str = "beginner",
    context: Optional[Dict[str, Any]] = None,
    verify_implementation: bool = False
) -> Dict[str, Any]:
    """
    Process educational query through CORTEX ASK mode.
    
    Provides implementation-truth-based education about CORTEX architecture,
    with progressive disclosure and numbered next-step suggestions.
    
    Args:
        user_query: User's educational question
        knowledge_level: One of 'beginner', 'intermediate', 'advanced'
        context: Optional context (file paths, orchestrator names, etc.)
        verify_implementation: Whether to verify claims against live code
        
    Returns:
        Dict containing:
            - status: 'success' or 'error'
            - explanation: Educational response
            - next_steps: List of 3-5 numbered next-step options
            - knowledge_level: Detected/provided knowledge level
            - verification: Optional verification results
            - error: Error message if status='error'
            
    Examples:
        >>> result = cortex_ask("What is CORTEX?", "beginner")
        >>> result['status']
        'success'
        >>> len(result['next_steps'])
        4
    """
    # Validate input
    is_valid, error = validate_query(user_query)
    if not is_valid:
        return {
            "status": "error",
            "error": error
        }
    
    # Validate knowledge level
    valid_levels = ["beginner", "intermediate", "advanced"]
    if knowledge_level not in valid_levels:
        return {
            "status": "error",
            "error": f"Invalid knowledge level. Must be one of: {', '.join(valid_levels)}"
        }
    
    try:
        # Initialize orchestrator
        orchestrator = EducationalOrchestrator()
        
        # Prepare request
        request = {
            "query": user_query,
            "knowledge_level": knowledge_level,
            "context": context or {},
            "verify_implementation": verify_implementation
        }
        
        # Execute educational processing
        result_obj = orchestrator.execute(request)
        
        # Unwrap Result object
        if hasattr(result_obj, 'is_ok') and result_obj.is_ok():
            result_json = result_obj.unwrap()
            # Parse JSON string
            import json
            raw_response = json.loads(result_json)
        elif hasattr(result_obj, '__dict__'):
            raw_response = result_obj.__dict__
        else:
            raw_response = result_obj
        
        # Format response
        formatted_response = format_educational_response(raw_response)
        
        # Add verification if requested
        if verify_implementation:
            verification_engine = TruthVerificationEngine()
            verification_result = verification_engine.verify_query_claims(user_query)
            formatted_response["verification"] = verification_result
        
        return formatted_response
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Educational processing failed: {str(e)}"
        }


def validate_query(query: str) -> Tuple[bool, Optional[str]]:
    """
    Validate user query.
    
    Args:
        query: User's query string
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not query or not query.strip():
        return False, "Query cannot be empty"
    
    if len(query) > 5000:
        return False, "Query too long (max 5000 characters)"
    
    return True, None


def format_educational_response(raw_response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format raw orchestrator response for MCP output.
    
    Args:
        raw_response: Response from EducationalOrchestrator
        
    Returns:
        Formatted response dict
    """
    return {
        "status": "success",
        "explanation": raw_response.get("explanation", ""),
        "next_steps": raw_response.get("next_steps", []),
        "knowledge_level": raw_response.get("knowledge_level", "beginner"),
        "context": raw_response.get("context", {})
    }


# Mark as MCP tool for registration
cortex_ask.__mcp_tool__ = True
