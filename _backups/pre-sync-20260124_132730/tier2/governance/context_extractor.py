"""
Context Extractor for Governance Rules

AC-GOV-CTX-001: Context-aware governance with extractors
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List


@dataclass
class GovernanceContext:
    """Governance context for rule evaluation"""
    operation_id: str
    domain: str
    tier: int
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    flags: List[str] = field(default_factory=list)


class ContextExtractor:
    """Extracts governance context from operations"""

    def __init__(self):
        """Initialize context extractor"""
        pass

    def extract_context(self, operation_data: Dict[str, Any]) -> GovernanceContext:
        """Extract governance context from operation data"""
        return GovernanceContext(
            operation_id=operation_data.get("operation_id", "unknown"),
            domain=operation_data.get("domain", "default"),
            tier=operation_data.get("tier", 0),
            user_id=operation_data.get("user_id"),
            metadata=operation_data.get("metadata", {}),
            flags=operation_data.get("flags", []),
        )
