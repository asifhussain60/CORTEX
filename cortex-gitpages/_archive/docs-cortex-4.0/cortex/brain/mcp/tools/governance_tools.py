"""
MCP Governance Tools - Runtime Enforcement via MCP

MCP-exposed tools for governance enforcement:
- check_phase_lock: Verify phase lock status
- validate_ac_id: Validate AC-ID existence
- canonicalize_intent: Normalize intent to prevent hallucination
- enforce_operation: Full operation enforcement
- get_phase_status: Get comprehensive phase status

These are thin wrappers over GovernanceEnforcer core logic.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from typing import Any, Dict, Optional

from cortex.brain.core.result import Result, Ok, Err
from cortex.brain.core.governance_enforcer import GovernanceEnforcer, IntentType
from cortex.infrastructure.database import DatabaseManager, DatabaseConfig
from cortex.brain.mcp.decorator import mcp_tool


# Module-level instances (initialized lazily)
_db: Optional[DatabaseManager] = None
_enforcer: Optional[GovernanceEnforcer] = None


# Tool registry for MCP exposure
_TOOL_REGISTRY: Dict[str, Dict[str, Any]] = {}


def _register_tool(name: str, description: str, parameters: Dict[str, Any]):
    """Register a tool in the MCP registry."""
    _TOOL_REGISTRY[name] = {
        "description": description,
        "parameters": parameters,
    }


def initialize_governance_tools(db: Optional[DatabaseManager] = None) -> None:
    """
    Initialize governance tools with database.
    
    Args:
        db: Optional pre-initialized database. Creates default if None.
    """
    global _db, _enforcer
    
    if db is not None:
        _db = db
    elif _db is None:
        _db = DatabaseManager()
        _db.initialize()
    
    _enforcer = GovernanceEnforcer(_db)


def _ensure_initialized() -> GovernanceEnforcer:
    """Ensure enforcer is initialized."""
    global _enforcer
    if _enforcer is None:
        initialize_governance_tools()
    return _enforcer


# =============================================================================
# MCP Tools
# =============================================================================

@mcp_tool(
    name="check_phase_lock",
    description="Check if a phase is locked. Locked phases cannot be modified or reimplemented.",
    parameters={
        "phase_id": {"type": "string", "description": "Phase ID (e.g., PHASE-01)"}
    }
)
def check_phase_lock(phase_id: str) -> Result[Dict[str, Any]]:
    """
    Check if a phase is locked.
    
    Args:
        phase_id: Phase identifier (e.g., "PHASE-01")
    
    Returns:
        Result containing lock status and details
    """
    if not phase_id or not phase_id.startswith("PHASE-"):
        return Err("Invalid phase_id: must be PHASE-XX format")
    
    enforcer = _ensure_initialized()
    result = enforcer.check_phase_lock(phase_id)
    
    response = {
        "phase_id": phase_id,
        "locked": not result.allowed,
    }
    
    if not result.allowed and result.metadata:
        response["locked_by"] = result.metadata.get("locked_by")
        response["locked_at"] = result.metadata.get("locked_at")
        response["git_checkpoint"] = result.metadata.get("git_checkpoint")
    
    return Ok(response)


_register_tool(
    "check_phase_lock",
    "Check if a phase is locked. Locked phases cannot be modified or reimplemented.",
    {"phase_id": {"type": "string", "description": "Phase ID (e.g., PHASE-01)"}}
)


@mcp_tool(
    name="validate_ac_id",
    description="Validate that an AC-ID exists and is properly formatted. Use before any operation targeting an AC-ID.",
    parameters={
        "ac_id": {"type": "string", "description": "Acceptance Criteria ID (e.g., AC-AR-001-01)"}
    }
)
def validate_ac_id(ac_id: str) -> Result[Dict[str, Any]]:
    """
    Validate an AC-ID exists and is properly formatted.
    
    Args:
        ac_id: Acceptance criteria ID
    
    Returns:
        Result containing validation status
    """
    enforcer = _ensure_initialized()
    result = enforcer.validate_ac_id(ac_id)
    
    return Ok({
        "ac_id": ac_id,
        "valid": result.allowed,
        "reason": result.reason,
    })


_register_tool(
    "validate_ac_id",
    "Validate that an AC-ID exists and is properly formatted. Use before any operation targeting an AC-ID.",
    {"ac_id": {"type": "string", "description": "Acceptance Criteria ID (e.g., AC-AR-001-01)"}}
)


@mcp_tool(
    name="canonicalize_intent",
    description="Normalize a raw intent string to a canonical form. Prevents hallucination by standardizing varied phrasings.",
    parameters={
        "raw_intent": {"type": "string", "description": "Raw intent string from user or agent"}
    }
)
def canonicalize_intent(raw_intent: str) -> Result[Dict[str, Any]]:
    """
    Canonicalize a raw intent string.
    
    Args:
        raw_intent: Raw intent string
    
    Returns:
        Result containing canonical intent
    """
    enforcer = _ensure_initialized()
    canonical = enforcer.canonicalize_intent(raw_intent)
    
    return Ok({
        "intent_type": canonical.intent_type.name,
        "ac_id": canonical.ac_id,
        "phase": canonical.phase,
        "confidence": canonical.confidence,
        "raw_intent": canonical.raw_intent,
    })


_register_tool(
    "canonicalize_intent",
    "Normalize a raw intent string to a canonical form. Prevents hallucination by standardizing varied phrasings.",
    {"raw_intent": {"type": "string", "description": "Raw intent string from user or agent"}}
)


@mcp_tool(
    name="enforce_operation",
    description="Enforce governance rules for an operation. Checks phase locks, AC-ID validity, and phase dependencies.",
    parameters={
        "operation": {"type": "string", "description": "Operation type (implement, review, modify)"},
        "ac_id": {"type": "string", "description": "Target AC-ID"},
        "phase": {"type": "string", "description": "Target phase"}
    }
)
def enforce_operation(
    operation: str,
    ac_id: str,
    phase: str
) -> Result[Dict[str, Any]]:
    """
    Enforce governance for a complete operation.
    
    Args:
        operation: Operation type
        ac_id: Target AC-ID
        phase: Target phase
    
    Returns:
        Result containing enforcement decision
    """
    enforcer = _ensure_initialized()
    result = enforcer.enforce_operation(operation, ac_id, phase)
    
    return Ok({
        "allowed": result.allowed,
        "reason": result.reason,
        "operation": operation,
        "ac_id": ac_id,
        "phase": phase,
        "metadata": result.metadata,
    })


_register_tool(
    "enforce_operation",
    "Enforce governance rules for an operation. Checks phase locks, AC-ID validity, and phase dependencies.",
    {
        "operation": {"type": "string", "description": "Operation type (implement, review, modify)"},
        "ac_id": {"type": "string", "description": "Target AC-ID"},
        "phase": {"type": "string", "description": "Target phase"}
    }
)


@mcp_tool(
    name="get_phase_status",
    description="Get comprehensive status for a phase including lock state, AC counts, and progress.",
    parameters={
        "phase_id": {"type": "string", "description": "Phase ID (e.g., PHASE-01)"}
    }
)
def get_phase_status(phase_id: str) -> Result[Dict[str, Any]]:
    """
    Get comprehensive phase status.
    
    Args:
        phase_id: Phase identifier
    
    Returns:
        Result containing phase status details
    """
    enforcer = _ensure_initialized()
    
    # Check lock status
    lock_result = enforcer.check_phase_lock(phase_id)
    is_locked = not lock_result.allowed
    
    # Get AC count for phase
    # Map phase to AC prefix pattern
    phase_ac_prefixes = {
        "PHASE-01": ["AC-AR-001", "AC-AR-002", "AC-AR-003", "AC-AR-004", "AC-AR-005", 
                     "AC-FR-001", "AC-FR-003", "AC-FR-004", "AC-FR-005", "AC-FR-006", "AC-AR-008"],
        "PHASE-02": ["AC-AR-006", "AC-AR-007", "AC-FR-002", "AC-AR-009", "AC-VALIDATE", "AC-METRICS"],
        "PHASE-03": ["AC-NFR-002", "AC-NFR-004"],
        "PHASE-04": ["AC-NFR-003", "AC-COHERENCE", "AC-EXPLAIN"],
        "PHASE-05": ["AC-NFR-001", "AC-BRITTLE"],
        "PHASE-PARALLEL": ["AC-AR-010"],
    }
    
    # Count ACs in database for this phase
    ac_result = _db.get_acs_by_phase(phase_id)
    ac_count = len(ac_result.unwrap()) if ac_result.is_ok() else 0
    
    # Get status breakdown
    status_counts = {"PENDING": 0, "IN_PROGRESS": 0, "COMPLETED": 0, "VERIFIED": 0}
    if ac_result.is_ok():
        for ac in ac_result.unwrap():
            status = ac.get("status", "PENDING")
            if status in status_counts:
                status_counts[status] += 1
    
    response = {
        "phase_id": phase_id,
        "locked": is_locked,
        "ac_count": ac_count,
        "status_breakdown": status_counts,
        "can_start": enforcer.can_start_phase(phase_id).allowed,
    }
    
    if is_locked and lock_result.metadata:
        response["locked_by"] = lock_result.metadata.get("locked_by")
        response["locked_at"] = lock_result.metadata.get("locked_at")
    
    return Ok(response)


_register_tool(
    "get_phase_status",
    "Get comprehensive status for a phase including lock state, AC counts, and progress.",
    {"phase_id": {"type": "string", "description": "Phase ID (e.g., PHASE-01)"}}
)


def get_tool_registry() -> Dict[str, Dict[str, Any]]:
    """
    Get the MCP tool registry.
    
    Returns:
        Dictionary of tool name -> tool info
    """
    return _TOOL_REGISTRY.copy()
