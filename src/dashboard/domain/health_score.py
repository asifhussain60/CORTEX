"""
Domain Entity: Health Score

Represents health score calculation with 7-layer breakdown.

Author: Asif Hussain
Created: 2025-11-30
CORTEX Version: 3.3.0
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class LayerScore:
    """Individual layer score with details"""
    name: str
    score: float  # 0-100
    weight: float  # 0-1 (contribution to total)
    passed: bool
    issues: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate layer score"""
        if not 0 <= self.score <= 100:
            raise ValueError(f"score must be 0-100, got {self.score}")
        if not 0 <= self.weight <= 1:
            raise ValueError(f"weight must be 0-1, got {self.weight}")


@dataclass
class HealthScore:
    """
    Domain entity representing health score with 7-layer breakdown.
    
    7 Layers (from CORTEX Integration Scoring):
    1. Discovery (25%)       - File discovery, import analysis
    2. Import (15%)          - Clean imports, no errors
    3. Instantiation (10%)   - Objects can be created
    4. Documentation (10%)   - Docstrings, comments
    5. Tests (20%)           - Test coverage, passing tests
    6. Wiring (10%)          - Integration, dependencies
    7. Optimization (10%)    - Performance, efficiency
    """
    
    # Overall score
    total_score: float = 0.0  # 0-100
    
    # 7-layer breakdown
    layers: Dict[str, LayerScore] = field(default_factory=dict)
    
    # Metadata
    component_path: Optional[str] = None
    calculated_at: Optional[str] = None
    
    def __post_init__(self):
        """Initialize default layers if not provided"""
        if not self.layers:
            self.layers = self._create_default_layers()
        
        # Calculate total if not set
        if self.total_score == 0.0 and self.layers:
            self.total_score = self.calculate_total()
    
    def _create_default_layers(self) -> Dict[str, LayerScore]:
        """Create default 7 layers with standard weights"""
        return {
            'discovery': LayerScore('Discovery', 0.0, 0.25, False),
            'import': LayerScore('Import', 0.0, 0.15, False),
            'instantiation': LayerScore('Instantiation', 0.0, 0.10, False),
            'documentation': LayerScore('Documentation', 0.0, 0.10, False),
            'tests': LayerScore('Tests', 0.0, 0.20, False),
            'wiring': LayerScore('Wiring', 0.0, 0.10, False),
            'optimization': LayerScore('Optimization', 0.0, 0.10, False)
        }
    
    def calculate_total(self) -> float:
        """Calculate weighted total score from layers"""
        total = sum(
            layer.score * layer.weight
            for layer in self.layers.values()
        )
        
        # Validate weights sum to 1.0
        weight_sum = sum(layer.weight for layer in self.layers.values())
        if not 0.99 <= weight_sum <= 1.01:
            raise ValueError(f"Layer weights must sum to 1.0, got {weight_sum}")
        
        self.total_score = round(total, 2)
        return self.total_score
    
    def update_layer(self, layer_name: str, score: float, passed: bool, issues: List[str] = None):
        """Update a specific layer score"""
        if layer_name not in self.layers:
            raise ValueError(f"Unknown layer: {layer_name}")
        
        layer = self.layers[layer_name]
        layer.score = score
        layer.passed = passed
        if issues:
            layer.issues = issues
        
        # Recalculate total
        self.calculate_total()
    
    @property
    def health_category(self) -> str:
        """Get health category"""
        if self.total_score >= 90:
            return "healthy"
        elif self.total_score >= 70:
            return "warning"
        else:
            return "critical"
    
    @property
    def health_color(self) -> str:
        """Get color code for visualization"""
        if self.total_score >= 90:
            return "#28a745"  # Green
        elif self.total_score >= 70:
            return "#ffc107"  # Yellow
        else:
            return "#dc3545"  # Red
    
    @property
    def layers_passed(self) -> int:
        """Count layers that passed"""
        return sum(1 for layer in self.layers.values() if layer.passed)
    
    @property
    def layers_failed(self) -> int:
        """Count layers that failed"""
        return len(self.layers) - self.layers_passed
    
    @property
    def total_issues(self) -> int:
        """Total issues across all layers"""
        return sum(len(layer.issues) for layer in self.layers.values())
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'total_score': self.total_score,
            'health_category': self.health_category,
            'health_color': self.health_color,
            'layers_passed': self.layers_passed,
            'layers_failed': self.layers_failed,
            'total_issues': self.total_issues,
            'layers': {
                name: {
                    'name': layer.name,
                    'score': layer.score,
                    'weight': layer.weight,
                    'passed': layer.passed,
                    'issues': layer.issues
                }
                for name, layer in self.layers.items()
            },
            'component_path': self.component_path,
            'calculated_at': self.calculated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'HealthScore':
        """Create HealthScore from dictionary"""
        layers_data = data.get('layers', {})
        layers = {
            name: LayerScore(**layer_data)
            for name, layer_data in layers_data.items()
        }
        
        return cls(
            total_score=data.get('total_score', 0.0),
            layers=layers,
            component_path=data.get('component_path'),
            calculated_at=data.get('calculated_at')
        )
