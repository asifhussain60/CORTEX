"""
Phase 22 Component #10: cortex_verify_claim MCP Tool

Standalone claim verification via MCP interface.
Exposes TruthVerificationEngine for external validation.
"""

from typing import Dict, Any, Optional, Tuple
from cortex.brain.verification.truth_verification_engine import TruthVerificationEngine


def cortex_verify_claim(
    claim: str,
    file_path: Optional[str] = None,
    scope: str = "auto",
    use_ast: bool = True
) -> Dict[str, Any]:
    """
    Verify a claim against CORTEX implementation truth.
    
    Args:
        claim: Claim to verify (e.g., "MasterOrchestrator exists")
        file_path: Optional specific file to check
        scope: Verification scope ('auto', 'file', 'all')
        use_ast: Whether to use AST analysis for verification
        
    Returns:
        Dict containing:
            - status: 'success' or 'error'
            - verdict: 'verified', 'false', or 'partial'
            - evidence: List of evidence items (file paths, line numbers, AST nodes)
            - confidence: Confidence score (0.0-1.0)
            - file_path: File path if provided
            - error: Error message if status='error'
            
    Examples:
        >>> result = cortex_verify_claim("EducationalOrchestrator exists")
        >>> result['verdict']
        'verified'
        >>> result['confidence'] > 0.9
        True
    """
    # Validate input
    is_valid, error = validate_claim(claim)
    if not is_valid:
        return {
            "status": "error",
            "error": error
        }
    
    try:
        # Initialize verification engine
        engine = TruthVerificationEngine()
        
        # Prepare verification request
        verification_request = {
            "claim": claim,
            "file_path": file_path,
            "scope": scope,
            "use_ast": use_ast
        }
        
        # Execute verification
        result_obj = engine.verify_claim(verification_request)
        
        # Unwrap Result object
        if hasattr(result_obj, 'is_ok') and result_obj.is_ok():
            raw_result = result_obj.unwrap()
        elif hasattr(result_obj, '__dict__'):
            raw_result = result_obj.__dict__
        else:
            raw_result = result_obj
        
        # Format response
        formatted_result = format_verification_result(raw_result)
        
        # Add request metadata
        if file_path:
            formatted_result["file_path"] = file_path
        formatted_result["scope"] = scope
        
        return formatted_result
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Claim verification failed: {str(e)}"
        }


def validate_claim(claim: str) -> Tuple[bool, Optional[str]]:
    """
    Validate claim input.
    
    Args:
        claim: Claim string to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not claim or not claim.strip():
        return False, "Claim cannot be empty"
    
    if len(claim) > 2000:
        return False, "Claim too long (max 2000 characters)"
    
    return True, None


def format_verification_result(raw_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format raw verification result for MCP output.
    
    Args:
        raw_result: Result from TruthVerificationEngine
        
    Returns:
        Formatted response dict
    """
    verdict = raw_result.get("verdict", "partial")
    evidence = raw_result.get("evidence", [])
    confidence = raw_result.get("confidence", 0.0)
    
    response = {
        "status": "success",
        "verdict": verdict,
        "confidence": confidence
    }
    
    if evidence:
        response["evidence"] = evidence
    
    # Add explanation if present
    if "explanation" in raw_result:
        response["explanation"] = raw_result["explanation"]
    
    return response


# Mark as MCP tool for registration
cortex_verify_claim.__mcp_tool__ = True
