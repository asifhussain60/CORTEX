"""
MCP Tool: cortex_ask

Educational interaction tool for CORTEX ASK mode.
Provides implementation-truth-based answers with progressive disclosure
and intelligent next-step suggestions.

Authority: AC-EDUCATIONAL-INTERACTION-001, PHASE-22-ASK-MODE-SYSTEM.yaml
"""

from typing import Dict, Any, Optional, List
from cortex.mcp.decorators import mcp_tool
from cortex.orchestrators.education.educational_orchestrator import (
    EducationalOrchestrator,
    KnowledgeLevel,
)
from cortex.brain.education.next_step_generator import NextStepContext


@mcp_tool(
    name="cortex_ask",
    description="Ask educational questions about CORTEX architecture with truth-based verification",
    parameters={
        "query": {
            "type": "string",
            "description": "Your question about CORTEX",
            "required": True
        },
        "knowledge_level": {
            "type": "string",
            "description": "Your knowledge level: beginner, intermediate, or advanced (optional, auto-detected if omitted)",
            "required": False,
            "enum": ["beginner", "intermediate", "advanced"]
        },
        "conversation_history": {
            "type": "array",
            "description": "Previous queries in this conversation (optional)",
            "required": False,
            "items": {"type": "string"}
        }
    }
)
def cortex_ask(
    query: str,
    knowledge_level: Optional[str] = None,
    conversation_history: Optional[List[str]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Ask questions about CORTEX with intelligent educational responses.
    
    Features:
    - Implementation truth verification
    - Progressive disclosure based on knowledge level
    - 3-5 intelligent next-step suggestions
    - Evidence-based answers with file paths
    - Fault detection and recommendations
    
    Args:
        query: User's question
        knowledge_level: Optional explicit knowledge level
        conversation_history: Optional previous queries
        
    Returns:
        Dict with status, answer, next_steps, evidence, faults
    """
    try:
        # Initialize orchestrator
        orchestrator = EducationalOrchestrator()
        
        # Prepare context
        context = {
            "query": query,
            "knowledge_level": knowledge_level,
            "conversation_history": conversation_history or [],
        }
        
        # Execute educational orchestration (sync version)
        result = orchestrator.execute(context)
        
        if not result.success:
            return {
                "status": "error",
                "error": result.error,
                "query": query
            }
        
        # Extract response data
        response_data = result.data
        educational_response = response_data.get("educational_response", {})
        
        # Format output
        return {
            "status": "success",
            "query": query,
            "answer": educational_response.get("answer", ""),
            "knowledge_level": educational_response.get("knowledge_level", "intermediate"),
            "confidence": educational_response.get("confidence", 0.8),
            "evidence": educational_response.get("evidence", []),
            "next_steps": educational_response.get("next_steps", []),
            "faults": educational_response.get("faults", []),
            "topic": educational_response.get("topic", "CORTEX"),
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "query": query
        }


@mcp_tool(
    name="cortex_verify_claim",
    description="Verify claims about CORTEX implementation against live code",
    parameters={
        "claim": {
            "type": "string",
            "description": "The claim to verify (e.g., 'MasterOrchestrator has 46 methods')",
            "required": True
        },
        "component": {
            "type": "string",
            "description": "Component to verify (orchestrator name, file path, or component type)",
            "required": True
        }
    }
)
def cortex_verify_claim(
    claim: str,
    component: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Verify claims about CORTEX implementation against live code.
    
    Uses TruthVerificationEngine to check:
    - File existence
    - Class/method presence
    - Implementation details
    - Wiring registration
    - Test coverage
    
    Args:
        claim: Claim to verify
        component: Component to check
        
    Returns:
        Dict with status, verified, confidence, evidence, recommendation
    """
    try:
        from cortex.brain.verification.truth_verification_engine import (
            TruthVerificationEngine,
            VerificationStrategy,
        )
        
        engine = TruthVerificationEngine()
        
        # Determine verification strategy from claim
        if "exists" in claim.lower():
            strategy = VerificationStrategy.ORCHESTRATOR_EXISTS
        elif "method" in claim.lower() or "function" in claim.lower():
            strategy = VerificationStrategy.ORCHESTRATOR_CAPABILITY
        elif "wiring" in claim.lower() or "registered" in claim.lower():
            strategy = VerificationStrategy.WIRING_CONFIG
        elif "test" in claim.lower():
            strategy = VerificationStrategy.TEST_COVERAGE
        else:
            strategy = VerificationStrategy.FILE_EXISTS
        
        # Verify claim
        result = engine.verify(
            claim=claim,
            component=component,
            strategy=strategy
        )
        
        # Format response
        verdict = "VERIFIED" if result.verified else "UNVERIFIED"
        
        return {
            "status": "success",
            "claim": claim,
            "component": component,
            "verified": result.verified,
            "verdict": verdict,
            "confidence": result.confidence,
            "evidence": result.evidence,
            "recommendation": result.recommendation if not result.verified else None,
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "claim": claim,
            "component": component
        }
