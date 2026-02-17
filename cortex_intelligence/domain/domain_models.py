"""
Domain Models - Data structures for domain definitions.
"""

from dataclasses import dataclass


@dataclass
class DomainCapability:
    """Represents a domain capability."""
    
    name: str
    description: str
    complexity: str


@dataclass
class DomainConstraint:
    """Represents a domain constraint."""
    
    name: str
    value: str
    severity: str


@dataclass
class DomainMetadata:
    """Represents domain metadata."""
    
    domain_id: str
    name: str
    version: str
