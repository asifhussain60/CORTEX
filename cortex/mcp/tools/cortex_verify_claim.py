"""
Phase 22 Component #10: cortex_verify_claim MCP Tool

Standalone claim verification via MCP interface.
Exposes TruthVerificationEngine for external validation.
"""

from typing import Any, Dict, Optional, Tuple

from cortex.brain.verification.truth_verification_engine import (
    ClaimType,
    TruthVerificationEngine,
)


def infer_claim_type(claim: str) -> ClaimType:
    """
    Infer claim type from natural language claim.

    Args:
        claim: Natural language claim

    Returns:
        Inferred ClaimType
    """
    claim_lower = claim.lower()

    # Check for specific orchestrator patterns (e.g., "TDDOrchestrator exists")
    import re
    orchestrator_pattern = re.search(r'(\w+orchestrator)', claim_lower)

    if orchestrator_pattern:
        if "exists" in claim_lower or "has" in claim_lower:
            return ClaimType.ORCHESTRATOR_EXISTS
        return ClaimType.ORCHESTRATOR_CAPABILITY
    elif "wiring" in claim_lower or "config" in claim_lower:
        return ClaimType.WIRING_CONFIG
    elif "test" in claim_lower and "coverage" in claim_lower:
        return ClaimType.TEST_COVERAGE
    elif "file" in claim_lower and "exists" in claim_lower:
        return ClaimType.FILE_EXISTS
    elif "function" in claim_lower:
        return ClaimType.FUNCTION_EXISTS
    elif "class" in claim_lower:
        return ClaimType.CLASS_EXISTS
    elif "mcp" in claim_lower and "tool" in claim_lower:
        return ClaimType.MCP_TOOL
    elif "git" in claim_lower:
        return ClaimType.GIT_HISTORY
    else:
        # Default to class/function exists for general "X exists" patterns
        if "exists" in claim_lower:
            return ClaimType.CLASS_EXISTS
        # Generic orchestrator check for broad claims about orchestrators
        if "orchestrator" in claim_lower:
            return ClaimType.ORCHESTRATOR_EXISTS
        return ClaimType.WIRING_CONFIG


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

        # Infer claim type from claim text
        claim_type = infer_claim_type(claim)

        # Prepare context
        context = {
            "file_path": file_path,
            "scope": scope,
            "use_ast": use_ast
        }

        # Execute verification with proper signature
        result_obj = engine.verify_claim(claim, claim_type, context)

        # Convert VerificationResult to dict for formatting
        raw_result = {
            "claim": result_obj.claim,
            "status": result_obj.status.value,
            "verdict": result_obj.status.value,  # Map status to verdict
            "confidence": result_obj.confidence,
            "evidence": [
                {
                    "source_type": e.source_type,
                    "file_path": e.file_path,
                    "line_number": e.line_number,
                    "content": getattr(e, 'content', None),
                    "description": e.description
                }
                for e in result_obj.evidence
            ],
            "explanation": result_obj.explanation,
            "recommendations": result_obj.recommendations
        }

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
