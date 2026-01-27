"""Structured error context with causality chains and recovery hints.

Implements rich error context with correlation IDs, causality tracking,
recovery suggestions, and PII sanitization for safe logging.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import re
import uuid
import json


class ErrorType(str, Enum):
    """Classification of error types."""
    TRANSIENT = "TRANSIENT"  # Temporary, retry may succeed
    PERMANENT = "PERMANENT"  # Persistent, retry won't help
    CONFIGURATION = "CONFIGURATION"  # Configuration issue
    VALIDATION = "VALIDATION"  # Input validation failure


@dataclass
class RecoveryHint:
    """Hint for recovering from error.
    
    Args:
        action: Recommended action
        automated: Whether retry can be automated
        estimated_duration_seconds: Expected recovery time
        additional_context: Extra recovery information
    """
    action: str
    automated: bool
    estimated_duration_seconds: Optional[int] = None
    additional_context: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def for_error_type(cls, error_type: ErrorType) -> "RecoveryHint":
        """Generate recovery hint for error type.
        
        Args:
            error_type: Type of error
            
        Returns:
            Recovery hint
        """
        hints = {
            ErrorType.TRANSIENT: cls(
                action="Retry operation with exponential backoff",
                automated=True,
                estimated_duration_seconds=30
            ),
            ErrorType.PERMANENT: cls(
                action="Manual intervention required - check system state",
                automated=False,
                estimated_duration_seconds=None
            ),
            ErrorType.CONFIGURATION: cls(
                action="Review and update configuration settings",
                automated=False,
                estimated_duration_seconds=None
            ),
            ErrorType.VALIDATION: cls(
                action="Correct input and retry",
                automated=False,
                estimated_duration_seconds=5
            ),
        }
        return hints[error_type]


@dataclass
class CausalityNode:
    """Node in causality chain.
    
    Args:
        error_id: Error identifier
        message: Error message
        caused_by: Parent error ID
        contributing_factors: Additional contributing factors
    """
    error_id: str
    message: str
    caused_by: Optional[str] = None
    contributing_factors: List[str] = field(default_factory=list)


@dataclass
class CausalityChain:
    """Tracks error causality relationships.
    
    Attributes:
        errors: List of errors in chain
    """
    errors: List[CausalityNode] = field(default_factory=list)
    
    def add_error(
        self,
        error_id: str,
        message: str,
        caused_by: Optional[str] = None,
        contributing_factors: Optional[List[str]] = None
    ) -> None:
        """Add error to causality chain.
        
        Args:
            error_id: Error identifier
            message: Error message
            caused_by: Parent error ID
            contributing_factors: Additional factors
        """
        node = CausalityNode(
            error_id=error_id,
            message=message,
            caused_by=caused_by,
            contributing_factors=contributing_factors or []
        )
        self.errors.append(node)
    
    def root_cause(self) -> Optional[str]:
        """Get root cause error message.
        
        Returns:
            Root cause message
        """
        if not self.errors:
            return None
        
        # Find error with no parent
        error_map = {e.error_id: e for e in self.errors}
        
        for error in self.errors:
            if error.caused_by is None or error.caused_by not in error_map:
                return error.message
        
        # If all have parents (cycle), return first
        return self.errors[0].message
    
    def has_cycle(self) -> bool:
        """Detect circular causality.
        
        Returns:
            True if cycle detected
        """
        if len(self.errors) < 2:
            return False
        
        visited = set()
        error_map = {e.error_id: e for e in self.errors}
        
        for error in self.errors:
            current = error.error_id
            path = set()
            
            while current and current in error_map:
                if current in path:
                    return True  # Cycle detected
                
                path.add(current)
                current = error_map[current].caused_by
        
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize causality chain.
        
        Returns:
            Dictionary representation
        """
        return {
            "root_cause": self.root_cause(),
            "chain": [
                {
                    "error_id": e.error_id,
                    "message": e.message,
                    "caused_by": e.caused_by,
                    "contributing_factors": e.contributing_factors
                }
                for e in self.errors
            ]
        }


@dataclass
class ErrorContext:
    """Context for error occurrence.
    
    Args:
        operation: Operation being performed
        correlation_id: Correlation ID for tracing
        user_id: User identifier
        session_id: Session identifier
        metadata: Additional context
        parent_context: Parent operation context
    """
    operation: str
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    parent_context: Optional["ErrorContext"] = None
    
    def __post_init__(self) -> None:
        """Generate correlation ID if missing."""
        if not self.correlation_id:
            # Inherit from parent or generate new
            if self.parent_context and self.parent_context.correlation_id:
                self.correlation_id = self.parent_context.correlation_id
            else:
                self.correlation_id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize context.
        
        Returns:
            Dictionary representation
        """
        return {
            "operation": self.operation,
            "correlation_id": self.correlation_id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "metadata": self.metadata
        }


def sanitize_pii(text: str) -> str:
    """Sanitize personally identifiable information.
    
    Args:
        text: Text potentially containing PII
        
    Returns:
        Sanitized text
    """
    # Email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
    
    # API keys (common patterns) - match full key including prefix
    text = re.sub(r'\b(sk|pk|api|key)[-_]?[A-Za-z0-9]{8,}\b', '[API_KEY]', text, flags=re.IGNORECASE)
    
    # Phone numbers
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
    
    # Social Security Numbers
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', text)
    
    # Credit card numbers (basic pattern)
    text = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CREDIT_CARD]', text)
    
    return text


@dataclass
class StructuredError:
    """Structured error with rich context.
    
    Args:
        error_type: Error type classification
        message: Error message
        code: Error code
        context: Error context
        causality: Causality chain
        recovery_hint: Recovery suggestion
        timestamp: When error occurred
    """
    error_type: ErrorType
    message: str
    code: str
    context: ErrorContext
    causality: Optional[CausalityChain] = None
    recovery_hint: Optional[RecoveryHint] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def correlation_id(self) -> Optional[str]:
        """Get correlation ID.
        
        Returns:
            Correlation ID
        """
        return self.context.correlation_id
    
    def sanitized_message(self) -> str:
        """Get message with PII sanitized.
        
        Returns:
            Sanitized message
        """
        return sanitize_pii(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize error to dictionary.
        
        Returns:
            Dictionary representation
        """
        result = {
            "error_type": self.error_type.value,
            "message": self.sanitized_message(),
            "code": self.code,
            "correlation_id": self.correlation_id(),
            "timestamp": self.timestamp.isoformat(),
            "context": self.context.to_dict()
        }
        
        if self.causality:
            result["causality"] = self.causality.to_dict()
        
        if self.recovery_hint:
            result["recovery_hint"] = {
                "action": self.recovery_hint.action,
                "automated": self.recovery_hint.automated,
                "estimated_duration_seconds": self.recovery_hint.estimated_duration_seconds
            }
        
        return result
    
    def to_json(self) -> str:
        """Serialize error to JSON string.
        
        Returns:
            JSON representation
        """
        return json.dumps(self.to_dict(), indent=2)
    
    def __str__(self) -> str:
        """String representation.
        
        Returns:
            Human-readable error
        """
        parts = [
            f"[{self.error_type.value}] {self.code}",
            f"Message: {self.sanitized_message()}",
            f"Correlation ID: {self.correlation_id()}",
            f"Operation: {self.context.operation}"
        ]
        
        if self.causality:
            root = self.causality.root_cause()
            if root:
                parts.append(f"Root Cause: {root}")
        
        if self.recovery_hint:
            parts.append(f"Recovery: {self.recovery_hint.action}")
        
        return "\n".join(parts)


def create_error(
    error_type: ErrorType,
    message: str,
    code: str,
    operation: str,
    correlation_id: Optional[str] = None,
    **context_kwargs: Any
) -> StructuredError:
    """Helper to create structured error.
    
    Args:
        error_type: Error type
        message: Error message
        code: Error code
        operation: Operation name
        correlation_id: Correlation ID
        **context_kwargs: Additional context fields
        
    Returns:
        Structured error
    """
    context = ErrorContext(
        operation=operation,
        correlation_id=correlation_id,
        **context_kwargs
    )
    
    recovery_hint = RecoveryHint.for_error_type(error_type)
    
    return StructuredError(
        error_type=error_type,
        message=message,
        code=code,
        context=context,
        recovery_hint=recovery_hint
    )
