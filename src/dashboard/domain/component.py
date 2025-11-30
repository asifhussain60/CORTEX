"""
Domain Entity: Component

Represents a software component (file, class, module) in the codebase.

Author: Asif Hussain
Created: 2025-11-30
CORTEX Version: 3.3.0
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class ComponentType(Enum):
    """Types of software components"""
    FILE = "file"
    CLASS = "class"
    MODULE = "module"
    PACKAGE = "package"
    SERVICE = "service"
    LIBRARY = "library"


@dataclass
class Component:
    """
    Domain entity representing a software component with metrics.
    
    Pure business object with no external dependencies.
    """
    
    # Identity
    name: str
    path: str
    type: ComponentType
    
    # Metrics
    health_score: float = 0.0  # 0-100
    lines_of_code: int = 0
    complexity: int = 0
    test_coverage: float = 0.0  # 0-100
    
    # Quality indicators
    code_smells: int = 0
    security_issues: int = 0
    duplicate_lines: int = 0
    
    # Relationships
    dependencies: List[str] = field(default_factory=list)  # Component paths
    dependents: List[str] = field(default_factory=list)   # Component paths
    
    # Metadata
    language: Optional[str] = None
    framework: Optional[str] = None
    last_modified: Optional[str] = None
    author: Optional[str] = None
    
    # Layer breakdown (for 7-layer integration scoring)
    layer_scores: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate component data"""
        if not 0 <= self.health_score <= 100:
            raise ValueError(f"health_score must be 0-100, got {self.health_score}")
        
        if not 0 <= self.test_coverage <= 100:
            raise ValueError(f"test_coverage must be 0-100, got {self.test_coverage}")
        
        if self.lines_of_code < 0:
            raise ValueError(f"lines_of_code must be >= 0, got {self.lines_of_code}")
    
    @property
    def health_category(self) -> str:
        """Get health category (healthy/warning/critical)"""
        if self.health_score >= 90:
            return "healthy"
        elif self.health_score >= 70:
            return "warning"
        else:
            return "critical"
    
    @property
    def health_color(self) -> str:
        """Get color code for health visualization"""
        if self.health_score >= 90:
            return "#28a745"  # Green
        elif self.health_score >= 70:
            return "#ffc107"  # Yellow
        else:
            return "#dc3545"  # Red
    
    @property
    def total_issues(self) -> int:
        """Total number of quality issues"""
        return self.code_smells + self.security_issues
    
    def add_dependency(self, component_path: str):
        """Add dependency to this component"""
        if component_path not in self.dependencies:
            self.dependencies.append(component_path)
    
    def add_dependent(self, component_path: str):
        """Add component that depends on this one"""
        if component_path not in self.dependents:
            self.dependents.append(component_path)
    
    def update_health_score(self, new_score: float):
        """Update health score with validation"""
        if not 0 <= new_score <= 100:
            raise ValueError(f"health_score must be 0-100, got {new_score}")
        self.health_score = new_score
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'name': self.name,
            'path': self.path,
            'type': self.type.value,
            'health_score': self.health_score,
            'health_category': self.health_category,
            'health_color': self.health_color,
            'lines_of_code': self.lines_of_code,
            'complexity': self.complexity,
            'test_coverage': self.test_coverage,
            'code_smells': self.code_smells,
            'security_issues': self.security_issues,
            'duplicate_lines': self.duplicate_lines,
            'total_issues': self.total_issues,
            'dependencies': self.dependencies,
            'dependents': self.dependents,
            'language': self.language,
            'framework': self.framework,
            'last_modified': self.last_modified,
            'author': self.author,
            'layer_scores': self.layer_scores
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Component':
        """Create Component from dictionary"""
        # Convert type string to enum
        if isinstance(data.get('type'), str):
            data['type'] = ComponentType(data['type'])
        
        # Remove computed properties that are not constructor arguments
        filtered_data = {
            k: v for k, v in data.items()
            if k not in ['health_category', 'health_color', 'total_issues']
        }
        
        return cls(**filtered_data)
