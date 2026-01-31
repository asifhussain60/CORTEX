"""Integration Validator

Author: CORTEX Framework
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Callable
from datetime import datetime
import inspect

from cortex.models.canonical_enums import ValidationSeverity


class IntegrationStatus(Enum):
    """Integration status."""
    VALID = "valid"
    INVALID = "invalid"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    VALIDATING = "validating"


@dataclass
class ValidationIssue:
    """Validation issue."""
    code: str
    message: str
    severity: ValidationSeverity
    source: Optional[str] = None
    target: Optional[str] = None
    suggestion: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity.value,
            "source": self.source,
            "target": self.target,
            "suggestion": self.suggestion,
        }


@dataclass
class IntegrationPoint:
    """Integration point definition."""
    point_id: str
    name: str
    source: str
    target: str
    contract: Optional[Dict[str, Any]] = None
    required: bool = True
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "point_id": self.point_id,
            "name": self.name,
            "source": self.source,
            "target": self.target,
            "contract": self.contract,
            "required": self.required,
            "enabled": self.enabled,
        }


@dataclass
class ValidationResult:
    """Validation result."""
    valid: bool
    status: IntegrationStatus = IntegrationStatus.VALID
    issues: List[ValidationIssue] = field(default_factory=list)
    duration_ms: float = 0.0
    timestamp: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "valid": self.valid,
            "status": self.status.value,
            "issues": [i.to_dict() for i in self.issues],
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "metadata": self.metadata,
        }


class DependencyGraph:
    """Dependency graph for integration analysis."""
    
    def __init__(self):
        """Initialize dependency graph."""
        self.nodes: Set[str] = set()
        self.edges: Dict[str, Set[str]] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}
    
    def add_node(self, node: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add node to graph."""
        self.nodes.add(node)
        if metadata:
            self.metadata[node] = metadata
    
    def add_edge(self, from_node: str, to_node: str) -> None:
        """Add edge to graph."""
        self.nodes.add(from_node)
        self.nodes.add(to_node)
        
        if from_node not in self.edges:
            self.edges[from_node] = set()
        self.edges[from_node].add(to_node)
    
    def get_dependencies(self, node: str) -> Set[str]:
        """Get direct dependencies."""
        return self.edges.get(node, set()).copy()
    
    def get_all_dependencies(self, node: str) -> Set[str]:
        """Get all transitive dependencies."""
        all_deps = set()
        to_visit = [node]
        visited = set()
        
        while to_visit:
            current = to_visit.pop()
            if current in visited:
                continue
            visited.add(current)
            
            deps = self.edges.get(current, set())
            for dep in deps:
                all_deps.add(dep)
                to_visit.append(dep)
        
        return all_deps
    
    def detect_cycles(self) -> List[List[str]]:
        """Detect cycles in dependency graph."""
        cycles = []
        
        def dfs(node: str, path: List[str], visited: Set[str]) -> None:
            if node in path:
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return
            
            if node in visited:
                return
            
            path.append(node)
            
            for neighbor in self.edges.get(node, set()):
                dfs(neighbor, path.copy(), visited)
            
            visited.add(node)
        
        visited_global = set()
        for node in self.nodes:
            if node not in visited_global:
                dfs(node, [], visited_global)
        
        return cycles


class IntegrationValidator:
    """Validate integrations."""
    
    def __init__(self):
        """Initialize integration validator."""
        self._components: Dict[str, type] = {}
        self._instances: Dict[str, Any] = {}
        self._integration_points: Dict[str, IntegrationPoint] = {}
        self._dependency_graph = DependencyGraph()
        self._custom_validators: Dict[str, Callable] = {}
        self._validation_history: List[ValidationResult] = []
    
    def register(self, name: str, component: type, instance: Optional[Any] = None) -> "IntegrationValidator":
        """Register a component."""
        self._components[name] = component
        if instance is not None:
            self._instances[name] = instance
        return self
    
    def add_integration_point(self, point: IntegrationPoint) -> "IntegrationValidator":
        """Add integration point."""
        self._integration_points[point.point_id] = point
        self._dependency_graph.add_node(point.source)
        self._dependency_graph.add_node(point.target)
        self._dependency_graph.add_edge(point.source, point.target)
        return self
    
    def add_validator(self, name: str, validator: Callable) -> "IntegrationValidator":
        """Add custom validator."""
        self._custom_validators[name] = validator
        return self
    
    def validate(self, point_id: str) -> ValidationResult:
        """Validate an integration point."""
        import time
        start_time = time.time()
        
        issues = []
        
        if point_id not in self._integration_points:
            result = ValidationResult(
                valid=False,
                status=IntegrationStatus.INVALID,
                issues=[ValidationIssue(
                    code="INT-000",
                    message=f"Integration point '{point_id}' not found",
                    severity=ValidationSeverity.ERROR,
                )],
            )
            self._validation_history.append(result)
            return result
        
        point = self._integration_points[point_id]
        
        if point.source not in self._components:
            issues.append(ValidationIssue(
                code="INT-001",
                message=f"Source component '{point.source}' not registered",
                severity=ValidationSeverity.ERROR,
                source=point.source,
            ))
        
        if point.target not in self._components:
            issues.append(ValidationIssue(
                code="INT-002",
                message=f"Target component '{point.target}' not registered",
                severity=ValidationSeverity.ERROR,
                target=point.target,
            ))
        
        if point.source in self._components and point.target in self._components:
            target_class = self._components[point.target]
            
            if point.contract and "method" in point.contract:
                method_name = point.contract["method"]
                
                if not hasattr(target_class, method_name):
                    issues.append(ValidationIssue(
                        code="INT-003",
                        message=f"Target '{point.target}' missing method '{method_name}'",
                        severity=ValidationSeverity.ERROR,
                        target=point.target,
                        suggestion=f"Add {method_name} method to {point.target}",
                    ))
                else:
                    if "params" in point.contract:
                        method = getattr(target_class, method_name)
                        sig = inspect.signature(method)
                        params = list(sig.parameters.keys())
                        
                        if 'self' in params:
                            params.remove('self')
                        
                        expected_params = point.contract["params"]
                        for expected_param in expected_params:
                            if expected_param not in params:
                                issues.append(ValidationIssue(
                                    code="INT-004",
                                    message=f"Method '{method_name}' missing parameter '{expected_param}'",
                                    severity=ValidationSeverity.WARNING,
                                    target=point.target,
                                ))
            
            if point.source not in self._instances:
                issues.append(ValidationIssue(
                    code="HEALTH-001",
                    message=f"Source '{point.source}' instance not available for health check",
                    severity=ValidationSeverity.INFO,
                    source=point.source,
                ))
            
            if point.target not in self._instances:
                issues.append(ValidationIssue(
                    code="HEALTH-002",
                    message=f"Target '{point.target}' instance not available for health check",
                    severity=ValidationSeverity.INFO,
                    target=point.target,
                ))
            
            if point.target in self._instances:
                target_instance = self._instances[point.target]
                if hasattr(target_instance, 'health_check'):
                    try:
                        health = target_instance.health_check()
                        if isinstance(health, dict) and not health.get("healthy", True):
                            issues.append(ValidationIssue(
                                code="HEALTH-003",
                                message=f"Target '{point.target}' health check failed",
                                severity=ValidationSeverity.WARNING,
                                target=point.target,
                            ))
                    except Exception as e:
                        issues.append(ValidationIssue(
                            code="HEALTH-004",
                            message=f"Target '{point.target}' health check error: {e}",
                            severity=ValidationSeverity.ERROR,
                            target=point.target,
                        ))
        
        for validator_name, validator_func in self._custom_validators.items():
            try:
                custom_result = validator_func(point)
                if custom_result.issues:
                    issues.extend(custom_result.issues)
            except Exception as e:
                issues.append(ValidationIssue(
                    code="VAL-ERROR",
                    message=f"Custom validator '{validator_name}' error: {e}",
                    severity=ValidationSeverity.WARNING,
                ))
        
        has_errors = any(i.severity in (ValidationSeverity.ERROR, ValidationSeverity.CRITICAL) for i in issues)
        
        result = ValidationResult(
            valid=not has_errors,
            status=IntegrationStatus.VALID if not has_errors else IntegrationStatus.INVALID,
            issues=issues,
            duration_ms=(time.time() - start_time) * 1000,
        )
        
        self._validation_history.append(result)
        return result
    
    def validate_all(self) -> List[ValidationResult]:
        """Validate all integration points."""
        results = []
        
        cycles = self._dependency_graph.detect_cycles()
        if cycles:
            dep_issues = []
            for cycle in cycles:
                dep_issues.append(ValidationIssue(
                    code="DEP-001",
                    message=f"Circular dependency detected: {' -> '.join(cycle)}",
                    severity=ValidationSeverity.ERROR,
                ))
            
            results.append(ValidationResult(
                valid=False,
                status=IntegrationStatus.INVALID,
                issues=dep_issues,
                metadata={"validation_type": "dependencies"},
            ))
        else:
            results.append(ValidationResult(
                valid=True,
                status=IntegrationStatus.VALID,
                metadata={"validation_type": "dependencies"},
            ))
        
        for point_id in self._integration_points:
            result = self.validate(point_id)
            results.append(result)
        
        return results
    
    def get_dependency_graph(self) -> DependencyGraph:
        """Get the dependency graph."""
        return self._dependency_graph
    
    def get_integration_points(self) -> List[IntegrationPoint]:
        """Get all integration points."""
        return list(self._integration_points.values())
    
    def summary(self) -> Dict[str, Any]:
        """Get validation summary."""
        total_validations = len(self._validation_history)
        passed = len([r for r in self._validation_history if r.valid])
        failed = total_validations - passed
        
        return {
            "total_components": len(self._components),
            "total_integration_points": len(self._integration_points),
            "total_validations": total_validations,
            "passed_validations": passed,
            "failed_validations": failed,
        }


__all__ = [
    "ValidationSeverity",
    "IntegrationStatus",
    "ValidationIssue",
    "IntegrationPoint",
    "ValidationResult",
    "DependencyGraph",
    "IntegrationValidator",
]
