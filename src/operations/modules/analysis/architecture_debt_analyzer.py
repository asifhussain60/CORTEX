"""
Architectural Debt Analyzer - Layer violations and circular dependencies.

Detects architectural anti-patterns that increase maintenance cost
and reduce code modularity.

Copyright © 2025 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import Dict, Any, List, Set
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ArchitectureViolation:
    """Architectural rule violation."""
    violation_type: str  # "layer_violation", "circular_dependency", "tight_coupling"
    severity: str  # "high", "medium", "low"
    description: str
    affected_modules: List[str]
    recommendation: str


class ArchitectureDebtAnalyzer:
    """Analyze architectural quality and identify debt."""
    
    def __init__(self, ast_engine):
        """
        Initialize architecture debt analyzer.
        
        Args:
            ast_engine: AST engine for dependency analysis
        """
        self.ast_engine = ast_engine
        
        # Define expected architecture layers
        self.layer_hierarchy = [
            "presentation",  # UI/API
            "application",   # Orchestrators
            "domain",        # Business logic
            "infrastructure" # Data access
        ]
        
    def analyze(self) -> Dict[str, Any]:
        """
        Analyze codebase architecture for violations and debt.
        
        Returns:
            Architecture analysis with violations and recommendations
        """
        logger.info("Analyzing architectural debt")
        
        # Use AST engine for architecture insights
        arch_data = self.ast_engine.get_architecture_insights()
        
        violations = []
        
        # Detect layer violations
        layer_violations = self._detect_layer_violations(arch_data.get('module_graph', []))
        violations.extend(layer_violations)
        
        # Detect circular dependencies
        circular_deps = self._detect_circular_dependencies(
            arch_data.get('circular_dependencies', [])
        )
        violations.extend(circular_deps)
        
        # Detect tight coupling
        tight_coupling = self._detect_tight_coupling(arch_data.get('module_graph', []))
        violations.extend(tight_coupling)
        
        return {
            'violations': violations,
            'total_violations': len(violations),
            'high_severity_count': len([v for v in violations if v.severity == 'high']),
            'debt_score': self._calculate_debt_score(violations),
            'recommended_actions': self._prioritize_actions(violations)
        }
        
    def _detect_layer_violations(self, module_graph: List[Dict]) -> List[ArchitectureViolation]:
        """Detect dependencies that violate layer hierarchy."""
        violations = []
        
        for edge in module_graph:
            from_module = edge.get('from', '')
            to_module = edge.get('to', '')
            
            from_layer = self._identify_layer(from_module)
            to_layer = self._identify_layer(to_module)
            
            if from_layer and to_layer:
                try:
                    from_idx = self.layer_hierarchy.index(from_layer)
                    to_idx = self.layer_hierarchy.index(to_layer)
                    
                    # Lower layers should not depend on higher layers
                    if from_idx > to_idx:
                        violations.append(ArchitectureViolation(
                            violation_type="layer_violation",
                            severity="high",
                            description=f"{from_layer} layer depends on {to_layer} layer",
                            affected_modules=[from_module, to_module],
                            recommendation=(
                                f"Introduce abstraction in {to_layer} layer "
                                f"or move {from_module} to appropriate layer"
                            )
                        ))
                except ValueError:
                    pass  # Layer not in hierarchy
                    
        return violations
        
    def _detect_circular_dependencies(
        self, 
        circular_deps: List[List[str]]
    ) -> List[ArchitectureViolation]:
        """Detect circular dependency cycles."""
        violations = []
        
        for cycle in circular_deps:
            if cycle:
                violations.append(ArchitectureViolation(
                    violation_type="circular_dependency",
                    severity="high",
                    description=f"Circular dependency: {' → '.join(cycle + [cycle[0]])}",
                    affected_modules=cycle,
                    recommendation=(
                        "Break cycle by introducing interface/abstraction "
                        "or inverting dependency direction"
                    )
                ))
            
        return violations
        
    def _detect_tight_coupling(self, module_graph: List[Dict]) -> List[ArchitectureViolation]:
        """Detect modules with excessive dependencies."""
        violations = []
        
        # Count incoming dependencies per module
        dependency_counts: Dict[str, int] = {}
        for edge in module_graph:
            to_module = edge.get('to', '')
            if to_module:
                dependency_counts[to_module] = dependency_counts.get(to_module, 0) + 1
            
        # Flag modules with >10 incoming dependencies
        for module, count in dependency_counts.items():
            if count > 10:
                violations.append(ArchitectureViolation(
                    violation_type="tight_coupling",
                    severity="medium",
                    description=f"{module} has {count} incoming dependencies",
                    affected_modules=[module],
                    recommendation=(
                        "Consider splitting module into smaller, focused components "
                        "or introducing facade pattern"
                    )
                ))
                
        return violations
        
    def _identify_layer(self, module_path: str) -> str:
        """Identify which architectural layer a module belongs to."""
        module_lower = module_path.lower()
        
        if 'api' in module_lower or 'ui' in module_lower or 'view' in module_lower:
            return 'presentation'
        elif 'orchestrat' in module_lower or 'service' in module_lower:
            return 'application'
        elif 'domain' in module_lower or 'model' in module_lower:
            return 'domain'
        elif 'repository' in module_lower or 'dao' in module_lower or 'db' in module_lower:
            return 'infrastructure'
        else:
            return ''
        
    def _calculate_debt_score(self, violations: List[ArchitectureViolation]) -> float:
        """Calculate overall architectural debt score (0-100)."""
        if not violations:
            return 0.0
            
        severity_weights = {"high": 3, "medium": 2, "low": 1}
        total_weight = sum(severity_weights.get(v.severity, 1) for v in violations)
        
        # Normalize to 0-100 scale (10+ violations = 100)
        return min(100.0, (total_weight / 30.0) * 100)
        
    def _prioritize_actions(self, violations: List[ArchitectureViolation]) -> List[str]:
        """Prioritize violations for remediation."""
        # Sort by severity: high > medium > low
        severity_order = {"high": 0, "medium": 1, "low": 2}
        sorted_violations = sorted(
            violations,
            key=lambda v: severity_order.get(v.severity, 3)
        )
        
        # Return top 5 actionable recommendations
        return [v.recommendation for v in sorted_violations[:5]]
