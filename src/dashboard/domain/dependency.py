"""
Domain Entity: Dependency

Represents a dependency relationship between two components.

Author: Asif Hussain
Created: 2025-11-30
CORTEX Version: 3.3.0
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class DependencyType(Enum):
    """Types of dependencies"""
    IMPORT = "import"
    INHERITANCE = "inheritance"
    COMPOSITION = "composition"
    AGGREGATION = "aggregation"
    CALL = "call"
    REFERENCE = "reference"


class DependencyStrength(Enum):
    """Coupling strength"""
    TIGHT = "tight"      # Hard to change, breaks easily
    MODERATE = "moderate"
    LOOSE = "loose"      # Easy to change, resilient


@dataclass
class Dependency:
    """
    Domain entity representing a dependency edge in the architecture graph.
    
    Pure business object with no external dependencies.
    """
    
    # Identity
    source: str      # Component path that depends ON target
    target: str      # Component path that is depended UPON
    type: DependencyType
    
    # Metrics
    usage_count: int = 1  # Number of times source uses target
    strength: DependencyStrength = DependencyStrength.MODERATE
    
    # Quality indicators
    is_circular: bool = False  # Part of circular dependency chain
    is_cross_layer: bool = False  # Violates layer separation
    
    # Metadata
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    
    def __post_init__(self):
        """Validate dependency data"""
        if self.source == self.target:
            raise ValueError("Self-dependencies not allowed")
        
        if self.usage_count < 0:
            raise ValueError(f"usage_count must be >= 0, got {self.usage_count}")
    
    @property
    def edge_id(self) -> str:
        """Unique identifier for this dependency edge"""
        return f"{self.source}→{self.target}"
    
    @property
    def has_quality_issues(self) -> bool:
        """Check if dependency has quality issues"""
        return self.is_circular or self.is_cross_layer
    
    @property
    def strength_weight(self) -> float:
        """Numeric weight for visualization (1-3)"""
        weights = {
            DependencyStrength.LOOSE: 1.0,
            DependencyStrength.MODERATE: 2.0,
            DependencyStrength.TIGHT: 3.0
        }
        return weights[self.strength]
    
    @property
    def edge_color(self) -> str:
        """Color code for visualization"""
        if self.is_circular:
            return "#dc3545"  # Red - circular dependency
        elif self.is_cross_layer:
            return "#ffc107"  # Yellow - layer violation
        else:
            return "#6c757d"  # Gray - normal
    
    def mark_circular(self):
        """Mark this dependency as part of a circular chain"""
        self.is_circular = True
        # Circular dependencies are always considered tight coupling
        self.strength = DependencyStrength.TIGHT
    
    def mark_cross_layer(self):
        """Mark this dependency as violating layer separation"""
        self.is_cross_layer = True
    
    def increment_usage(self):
        """Increment usage count (stronger coupling)"""
        self.usage_count += 1
        
        # Auto-adjust strength based on usage
        if self.usage_count > 10:
            self.strength = DependencyStrength.TIGHT
        elif self.usage_count > 3:
            self.strength = DependencyStrength.MODERATE
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'source': self.source,
            'target': self.target,
            'type': self.type.value,
            'usage_count': self.usage_count,
            'strength': self.strength.value,
            'strength_weight': self.strength_weight,
            'is_circular': self.is_circular,
            'is_cross_layer': self.is_cross_layer,
            'has_quality_issues': self.has_quality_issues,
            'edge_id': self.edge_id,
            'edge_color': self.edge_color,
            'first_seen': self.first_seen,
            'last_seen': self.last_seen
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Dependency':
        """Create Dependency from dictionary"""
        # Convert type/strength strings to enums
        if isinstance(data.get('type'), str):
            data['type'] = DependencyType(data['type'])
        if isinstance(data.get('strength'), str):
            data['strength'] = DependencyStrength(data['strength'])
        
        # Remove computed properties
        filtered_data = {
            k: v for k, v in data.items()
            if k not in ['strength_weight', 'edge_id', 'edge_color', 'has_quality_issues']
        }
        
        return cls(**filtered_data)
