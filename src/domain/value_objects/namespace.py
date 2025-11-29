"""Namespace value object - Represents workspace isolation with priority rules"""
from dataclasses import dataclass
from typing import Tuple, Any, List
from src.domain.common.value_object import ValueObject
from src.application.common.guards import Guard


@dataclass(frozen=True)
class Namespace(ValueObject):
    """Represents a namespace with isolation and priority rules
    
    Namespaces provide workspace isolation and priority-based pattern search.
    Format: "root.project.feature" (minimum 2 segments)
    
    Root Namespaces:
    - workspace: User's application code (highest priority)
    - cortex: CORTEX internal patterns (medium priority)
    - external: Third-party libraries (lowest priority)
    
    Priority Multipliers:
    - workspace.*: 2.0x (highest relevance)
    - cortex.*: 1.5x (medium relevance)
    - external.*: 0.5x (lowest relevance)
    
    Example:
        ns = Namespace("workspace.auth.jwt")
        print(ns.root)  # "workspace"
        print(ns.is_workspace)  # True
        print(ns.priority_multiplier)  # 2.0
    """
    value: str
    
    def __post_init__(self):
        """Validate namespace format"""
        Guard.against_empty(self.value, "Namespace.value")
        if not self._is_valid_format():
            raise ValueError(
                f"Invalid namespace format: '{self.value}'. "
                f"Expected format: 'root.project.feature' (minimum 2 segments)"
            )
    
    def _is_valid_format(self) -> bool:
        """Validate namespace format (dot-separated identifiers)"""
        parts = self.value.split('.')
        
        # Must have at least 1 part (allow single-segment namespaces)
        if len(parts) < 1:
            return False
        
        # Each part must be a valid Python identifier
        return all(part.isidentifier() for part in parts)
    
    @property
    def root(self) -> str:
        """Get root namespace (first segment)"""
        return self.value.split('.')[0]
    
    @property
    def segments(self) -> List[str]:
        """Get all namespace segments"""
        return self.value.split('.')
    
    @property
    def depth(self) -> int:
        """Get namespace depth (number of segments)"""
        return len(self.segments)
    
    @property
    def is_workspace(self) -> bool:
        """Check if this is a workspace namespace (includes cortex)"""
        return self.root in ("workspace", "cortex")
    
    @property
    def is_cortex(self) -> bool:
        """Check if this is a CORTEX internal namespace"""
        return self.root == "cortex"
    
    @property
    def is_external(self) -> bool:
        """Check if this is an external library namespace"""
        return self.root == "external"
    
    @property
    def priority_multiplier(self) -> float:
        """Get priority multiplier for pattern search
        
        Returns:
            2.0 for workspace (highest priority)
            1.5 for cortex (medium priority)
            0.5 for external (lowest priority)
            1.0 for unknown roots
        """
        if self.root == "workspace":
            return 2.0
        elif self.root == "cortex":
            return 1.5
        elif self.is_external:
            return 0.5
        else:
            return 1.0  # Unknown roots get neutral priority
    
    def is_parent_of(self, other: 'Namespace') -> bool:
        """Check if this namespace is a parent of another
        
        Example:
            parent = Namespace("workspace.auth")
            child = Namespace("workspace.auth.jwt")
            parent.is_parent_of(child)  # True
        """
        return other.value.startswith(self.value + '.')
    
    def is_child_of(self, other: 'Namespace') -> bool:
        """Check if this namespace is a child of another"""
        return other.is_parent_of(self)
    
    def matches_pattern(self, pattern: str) -> bool:
        """Check if namespace matches a glob-style pattern
        
        Supports:
        - Exact match: "workspace.auth.jwt"
        - Wildcard: "workspace.auth.*"
        - Universal: "*"
        
        Example:
            ns = Namespace("workspace.auth.jwt")
            ns.matches_pattern("workspace.auth.*")  # True
            ns.matches_pattern("*")  # True
        """
        import re
        
        # Handle universal wildcard
        if pattern == "*":
            return True
        
        # Convert glob pattern to regex
        # Escape dots first, then replace * with regex pattern
        regex_pattern = re.escape(pattern).replace(r'\*', '.*')
        regex_pattern = f"^{regex_pattern}$"
        
        return bool(re.match(regex_pattern, self.value))
    
    def get_equality_components(self) -> Tuple[Any, ...]:
        """Return components used for equality comparison"""
        return (self.value,)
    
    def __str__(self) -> str:
        """String representation"""
        return self.value
    
    def __repr__(self) -> str:
        """Developer-friendly representation"""
        return f"Namespace('{self.value}')"
