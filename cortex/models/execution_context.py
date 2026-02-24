"""
Canonical ExecutionContext - Single Source of Truth

Priority: P0-CRITICAL
CORE Compliance:
- CORE-035: Single canonical implementation (replaces 6 definitions)
- CORE-011: Full type hints
- CORE-012: Google-style docstrings

This module provides THE SINGLE canonical ExecutionContext for all CORTEX operations.

Replaces:
1. cortex/execution/execution_context.py
2. cortex/brain/core/execution_context.py
3. cortex/orchestrators/core/execution_context.py
4. cortex/mcp/execution_context.py
5. cortex/interaction/execution_context.py
6. cortex/lens/execution_context.py

Used by:
- MCP tools (request processing)
- Orchestrators (execution state)
- LENS analyzers (code analysis context)
- Governance enforcers (validation context)
- All CORTEX components requiring execution context

Design:
- Immutable required fields
- Mutable metadata and audit trail
- Timestamp tracking
- Type-safe via dataclass
- Audit logging integration
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import canonical IntentType (CORE-035: Single implementation)
from cortex.models.canonical_enums import IntentType

@dataclass
class ExecutionContext:
    """
    Single canonical execution context for all CORTEX operations.
    
    This class provides the execution state and metadata for any CORTEX operation,
    from MCP tool invocation to orchestrator execution to governance validation.
    
    All CORTEX components MUST use this canonical ExecutionContext to ensure:
    - Consistent state management
    - Audit trail continuity
    - Type safety across layers
    - CORE-035 compliance (single implementation)
    
    Attributes:
        orchestrator_id: Unique identifier for orchestrator handling request
        operation_id: Unique identifier for this specific operation
        intent: Type of operation (IMPLEMENT, FIX, ANALYZE, etc.)
        parameters: Operation-specific parameters
        metadata: Additional context (timestamps, user info, etc.)
        audit_trail: Chronological log of events during execution
        created_at: When context was created
        updated_at: Last update timestamp
        
    Example:
        >>> from cortex.models.execution_context import ExecutionContext, IntentType
        >>> ctx = ExecutionContext(
        ...     orchestrator_id="TDDOrchestrator",
        ...     operation_id="op-12345",
        ...     intent=IntentType.IMPLEMENT
        ... )
        >>> ctx.add_audit_event("Started TDD cycle")
        >>> ctx.add_audit_event("RED phase complete")
    """
    
    # Required fields (immutable after creation)
    orchestrator_id: str
    operation_id: str
    intent: IntentType
    
    # Optional fields (mutable)
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    audit_trail: List[str] = field(default_factory=list)
    
    # Timestamps (auto-managed)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    def add_audit_event(self, event: str) -> None:
        """
        Add audit event to trail with timestamp.
        
        Args:
            event: Description of event
            
        Example:
            >>> ctx.add_audit_event("TDD RED phase: Test written")
            >>> ctx.add_audit_event("TDD GREEN phase: Implementation complete")
        """
        timestamp = datetime.now()
        self.audit_trail.append(f"[{timestamp.isoformat()}] {event}")
        self.updated_at = timestamp
    
    def add_metadata(self, key: str, value: Any) -> None:
        """
        Add metadata to context.
        
        Args:
            key: Metadata key
            value: Metadata value
            
        Example:
            >>> ctx.add_metadata("user", "asif.hussain")
            >>> ctx.add_metadata("session_id", "sess-abc123")
        """
        self.metadata[key] = value
        self.updated_at = datetime.now()
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata value.
        
        Args:
            key: Metadata key
            default: Default value if key not found
            
        Returns:
            Metadata value or default
            
        Example:
            >>> user = ctx.get_metadata("user", "unknown")
        """
        return self.metadata.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert context to dictionary for serialization.
        
        Returns:
            Dictionary representation of context
            
        Example:
            >>> context_dict = ctx.to_dict()
            >>> import json
            >>> json.dumps(context_dict)
        """
        return {
            "orchestrator_id": self.orchestrator_id,
            "operation_id": self.operation_id,
            "intent": self.intent.value,
            "parameters": self.parameters,
            "metadata": self.metadata,
            "audit_trail": self.audit_trail,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls: object, data: Dict[str, Any]) -> ExecutionContext:
        """
        Create ExecutionContext from dictionary.
        
        Args:
            data: Dictionary with context data
            
        Returns:
            ExecutionContext instance
            
        Example:
            >>> data = {"orchestrator_id": "TDD", "operation_id": "op-1", ...}
            >>> ctx = ExecutionContext.from_dict(data)
        """
        return cls(
            orchestrator_id=data["orchestrator_id"],
            operation_id=data["operation_id"],
            intent=IntentType(data["intent"]),
            parameters=data.get("parameters", {}),
            metadata=data.get("metadata", {}),
            audit_trail=data.get("audit_trail", []),
        )
    
    def __repr__(self) -> str:
        """String representation of context."""
        return (
            f"ExecutionContext(orchestrator={self.orchestrator_id}, "
            f"operation={self.operation_id}, intent={self.intent.value}, "
            f"events={len(self.audit_trail)})"
        )

# AC_COMPLETE: AC-WAVE-P-REM-002-001 ✅ Canonical ExecutionContext created
# Next: Create migration script for 6 old definitions
