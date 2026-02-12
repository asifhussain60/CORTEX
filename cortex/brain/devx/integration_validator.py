"""
ODX-002-01: Integration Validator

Validates orchestrator integrations and dependencies.
Ensures orchestrators are properly connected and communicating.

AC-ID: ODX-002-01
Phase: PHASE-18-ORCHESTRATOR-DEVX
TDD Status: GREEN phase

Features:
- Dependency validation
- Communication path verification
- Contract validation between orchestrators
- Health check integration
"""

import inspect
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
)

from cortex.models.canonical_enums import ValidationSeverity


class IntegrationStatus(Enum):
    """Status of integration point."""
    VALID = "valid"
    INVALID = "invalid"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


@dataclass
class ValidationIssue:
    """A validation issue found during integration check.

    Attributes:
        code: Issue code (e.g., "INT-001")
        message: Human-readable description
        severity: Severity level
        source: Where issue was found
        target: Target of the issue
        suggestion: How to fix
        details: Additional details
    """
    code: str = ""
    message: str = ""
    severity: ValidationSeverity = ValidationSeverity.WARNING
    source: str = ""
    target: str = ""
    suggestion: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity.value,
            "source": self.source,
            "target": self.target,
            "suggestion": self.suggestion,
            "details": self.details,
        }


@dataclass
class IntegrationPoint:
    """Definition of an integration point between components.

    Attributes:
        point_id: Unique identifier
        name: Human-readable name
        source: Source component (provider)
        target: Target component (consumer)
        contract: Expected interface contract
        required: Whether integration is required
        description: Description of the integration
    """
    point_id: str = ""
    name: str = ""
    source: str = ""
    target: str = ""
    contract: Dict[str, Any] = field(default_factory=dict)
    required: bool = True
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "point_id": self.point_id,
            "name": self.name,
            "source": self.source,
            "target": self.target,
            "contract": self.contract,
            "required": self.required,
            "description": self.description,
        }


@dataclass
class ValidationResult:
    """Result of integration validation.

    Attributes:
        valid: Whether all validations passed
        timestamp: When validation occurred
        duration_ms: Time taken in milliseconds
        integration_point: Integration point validated
        status: Overall status
        issues: List of issues found
        metadata: Additional metadata
    """
    valid: bool = False
    timestamp: datetime = field(default_factory=datetime.utcnow)
    duration_ms: float = 0.0
    integration_point: Optional[IntegrationPoint] = None
    status: IntegrationStatus = IntegrationStatus.UNKNOWN
    issues: List[ValidationIssue] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "valid": self.valid,
            "timestamp": self.timestamp.isoformat(),
            "duration_ms": self.duration_ms,
            "integration_point": self.integration_point.to_dict() if self.integration_point else None,
            "status": self.status.value,
            "issues": [i.to_dict() for i in self.issues],
            "metadata": self.metadata,
        }


@dataclass
class DependencyGraph:
    """Graph of component dependencies.

    Attributes:
        nodes: Set of component names
        edges: Dictionary mapping source to targets
        metadata: Per-node metadata
    """
    nodes: Set[str] = field(default_factory=set)
    edges: Dict[str, Set[str]] = field(default_factory=dict)
    metadata: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def add_node(self, name: str, metadata: Optional[Dict[str, Any]] = None):
        """Add a node to the graph."""
        self.nodes.add(name)
        if metadata:
            self.metadata[name] = metadata

    def add_edge(self, source: str, target: str):
        """Add an edge from source to target."""
        self.nodes.add(source)
        self.nodes.add(target)
        if source not in self.edges:
            self.edges[source] = set()
        self.edges[source].add(target)

    def get_dependencies(self, name: str) -> Set[str]:
        """Get direct dependencies of a node."""
        return self.edges.get(name, set())

    def get_all_dependencies(self, name: str) -> Set[str]:
        """Get all transitive dependencies of a node."""
        all_deps = set()
        queue = list(self.get_dependencies(name))

        while queue:
            dep = queue.pop(0)
            if dep not in all_deps:
                all_deps.add(dep)
                queue.extend(self.get_dependencies(dep))

        return all_deps

    def detect_cycles(self) -> List[List[str]]:
        """Detect circular dependencies.

        Returns:
            List of cycles found
        """
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(node: str, path: List[str]) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self.edges.get(node, set()):
                if neighbor not in visited:
                    if dfs(neighbor, path):
                        return True
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])

            path.pop()
            rec_stack.remove(node)
            return False

        for node in self.nodes:
            if node not in visited:
                dfs(node, [])

        return cycles


class IntegrationValidator:
    """Validates orchestrator integrations and dependencies.

    Provides comprehensive validation of:
    - Component dependencies
    - Interface contracts
    - Communication paths
    - Health status

    Example:
        validator = IntegrationValidator()
        validator.register("MasterOrchestrator", MasterOrchestrator)
        validator.register("IntentRouter", IntentRouter)

        # Add integration point
        validator.add_integration_point(IntegrationPoint(
            point_id="master-intent",
            name="Master to Intent Router",
            source="MasterOrchestrator",
            target="IntentRouter",
            contract={"method": "route_intent"},
        ))

        # Validate
        results = validator.validate_all()
    """

    def __init__(self):
        """Initialize integration validator."""
        # Registered components
        self._components: Dict[str, Type] = {}
        self._instances: Dict[str, Any] = {}

        # Integration points
        self._integration_points: Dict[str, IntegrationPoint] = {}

        # Dependency graph
        self._dependency_graph = DependencyGraph()

        # Validation rules
        self._validators: Dict[str, Callable[[IntegrationPoint], ValidationResult]] = {}

        # Results history
        self._results_history: List[ValidationResult] = []

    def register(
        self,
        name: str,
        component_class: Type,
        instance: Optional[Any] = None,
    ) -> "IntegrationValidator":
        """Register a component for validation.

        Args:
            name: Component name
            component_class: Component class
            instance: Optional existing instance

        Returns:
            Self for method chaining
        """
        self._components[name] = component_class
        if instance:
            self._instances[name] = instance

        self._dependency_graph.add_node(name, {
            "class": component_class.__name__,
            "module": component_class.__module__,
        })

        return self

    def add_integration_point(self, point: IntegrationPoint) -> "IntegrationValidator":
        """Add an integration point definition.

        Args:
            point: Integration point definition

        Returns:
            Self for method chaining
        """
        self._integration_points[point.point_id] = point

        # Add to dependency graph
        self._dependency_graph.add_edge(point.source, point.target)

        return self

    def add_validator(
        self,
        name: str,
        validator: Callable[[IntegrationPoint], ValidationResult],
    ) -> "IntegrationValidator":
        """Add a custom validation rule.

        Args:
            name: Validator name
            validator: Function that validates an integration point

        Returns:
            Self for method chaining
        """
        self._validators[name] = validator
        return self

    def _validate_interface_contract(
        self,
        point: IntegrationPoint,
    ) -> ValidationResult:
        """Validate interface contract between components.

        Args:
            point: Integration point to validate

        Returns:
            ValidationResult
        """
        result = ValidationResult(integration_point=point)
        start_time = time.time()

        issues = []

        # Check source component exists
        if point.source not in self._components:
            issues.append(ValidationIssue(
                code="INT-001",
                message=f"Source component '{point.source}' not registered",
                severity=ValidationSeverity.CRITICAL,
                source=point.source,
                target=point.target,
            ))

        # Check target component exists
        if point.target not in self._components:
            issues.append(ValidationIssue(
                code="INT-002",
                message=f"Target component '{point.target}' not registered",
                severity=ValidationSeverity.CRITICAL,
                source=point.source,
                target=point.target,
            ))

        # Check contract methods
        if point.contract.get("method"):
            method_name = point.contract["method"]
            target_class = self._components.get(point.target)

            if target_class and not hasattr(target_class, method_name):
                issues.append(ValidationIssue(
                    code="INT-003",
                    message=f"Target '{point.target}' missing method '{method_name}'",
                    severity=ValidationSeverity.ERROR,
                    source=point.source,
                    target=point.target,
                    suggestion=f"Add method '{method_name}' to {point.target}",
                ))
            elif target_class:
                # Validate method signature if params specified
                expected_params = point.contract.get("params", [])
                if expected_params:
                    method = getattr(target_class, method_name)
                    sig = inspect.signature(method)
                    actual_params = [p for p in sig.parameters.keys() if p != "self"]

                    missing = set(expected_params) - set(actual_params)
                    if missing:
                        issues.append(ValidationIssue(
                            code="INT-004",
                            message=f"Method '{method_name}' missing parameters: {missing}",
                            severity=ValidationSeverity.WARNING,
                            source=point.source,
                            target=point.target,
                            details={"expected": expected_params, "actual": actual_params},
                        ))

        # Check contract return type
        if point.contract.get("returns") and point.target in self._components:
            target_class = self._components[point.target]
            method_name = point.contract.get("method", "")

            if method_name and hasattr(target_class, method_name):
                method = getattr(target_class, method_name)
                hints = getattr(method, "__annotations__", {})
                return_type = hints.get("return")

                expected_return = point.contract["returns"]
                if return_type and str(return_type) != expected_return:
                    issues.append(ValidationIssue(
                        code="INT-005",
                        message=f"Return type mismatch: expected {expected_return}, got {return_type}",
                        severity=ValidationSeverity.WARNING,
                        source=point.source,
                        target=point.target,
                    ))

        result.duration_ms = (time.time() - start_time) * 1000
        result.issues = issues

        # Determine status
        critical_count = sum(1 for i in issues if i.severity == ValidationSeverity.CRITICAL)
        error_count = sum(1 for i in issues if i.severity == ValidationSeverity.ERROR)

        if critical_count > 0:
            result.status = IntegrationStatus.INVALID
            result.valid = False
        elif error_count > 0:
            result.status = IntegrationStatus.DEGRADED
            result.valid = False
        elif issues:
            result.status = IntegrationStatus.DEGRADED
            result.valid = True  # Warnings don't fail
        else:
            result.status = IntegrationStatus.VALID
            result.valid = True

        return result

    def _validate_dependencies(self) -> ValidationResult:
        """Validate dependency graph for issues.

        Returns:
            ValidationResult with dependency validation
        """
        result = ValidationResult()
        start_time = time.time()
        issues = []

        # Check for circular dependencies
        cycles = self._dependency_graph.detect_cycles()
        for cycle in cycles:
            issues.append(ValidationIssue(
                code="DEP-001",
                message=f"Circular dependency detected: {' -> '.join(cycle)}",
                severity=ValidationSeverity.ERROR,
                source=cycle[0] if cycle else "",
                target=cycle[-1] if cycle else "",
                suggestion="Refactor to break circular dependency",
            ))

        # Check for missing dependencies
        for source, targets in self._dependency_graph.edges.items():
            for target in targets:
                if target not in self._components:
                    issues.append(ValidationIssue(
                        code="DEP-002",
                        message=f"Component '{source}' depends on unregistered '{target}'",
                        severity=ValidationSeverity.ERROR,
                        source=source,
                        target=target,
                        suggestion=f"Register component '{target}'",
                    ))

        result.duration_ms = (time.time() - start_time) * 1000
        result.issues = issues
        result.valid = not any(i.severity in (ValidationSeverity.ERROR, ValidationSeverity.CRITICAL) for i in issues)
        result.status = IntegrationStatus.VALID if result.valid else IntegrationStatus.INVALID
        result.metadata["cycles_detected"] = len(cycles)
        result.metadata["total_dependencies"] = sum(len(t) for t in self._dependency_graph.edges.values())

        return result

    def _validate_health(self, point: IntegrationPoint) -> ValidationResult:
        """Validate health of integration point.

        Args:
            point: Integration point to check

        Returns:
            ValidationResult with health status
        """
        result = ValidationResult(integration_point=point)
        start_time = time.time()
        issues = []

        # Check if instances are available
        source_instance = self._instances.get(point.source)
        target_instance = self._instances.get(point.target)

        if not source_instance:
            issues.append(ValidationIssue(
                code="HEALTH-001",
                message=f"No instance available for '{point.source}'",
                severity=ValidationSeverity.INFO,
                source=point.source,
                target=point.target,
            ))

        if not target_instance:
            issues.append(ValidationIssue(
                code="HEALTH-002",
                message=f"No instance available for '{point.target}'",
                severity=ValidationSeverity.INFO,
                source=point.source,
                target=point.target,
            ))

        # Check health method if available
        if target_instance and hasattr(target_instance, "health_check"):
            try:
                health = target_instance.health_check()
                if not health or (isinstance(health, dict) and not health.get("healthy", True)):
                    issues.append(ValidationIssue(
                        code="HEALTH-003",
                        message=f"Component '{point.target}' reports unhealthy",
                        severity=ValidationSeverity.WARNING,
                        source=point.source,
                        target=point.target,
                        details={"health_response": health},
                    ))
            except Exception as e:
                issues.append(ValidationIssue(
                    code="HEALTH-004",
                    message=f"Health check failed for '{point.target}': {e}",
                    severity=ValidationSeverity.WARNING,
                    source=point.source,
                    target=point.target,
                ))

        result.duration_ms = (time.time() - start_time) * 1000
        result.issues = issues
        result.valid = not any(i.severity in (ValidationSeverity.ERROR, ValidationSeverity.CRITICAL) for i in issues)
        result.status = IntegrationStatus.VALID if result.valid else IntegrationStatus.DEGRADED

        return result

    def validate(self, point_id: str) -> ValidationResult:
        """Validate a specific integration point.

        Args:
            point_id: Integration point ID

        Returns:
            ValidationResult
        """
        point = self._integration_points.get(point_id)
        if not point:
            return ValidationResult(
                valid=False,
                status=IntegrationStatus.INVALID,
                issues=[ValidationIssue(
                    code="INT-000",
                    message=f"Integration point '{point_id}' not found",
                    severity=ValidationSeverity.CRITICAL,
                )],
            )

        # Run validations
        contract_result = self._validate_interface_contract(point)
        health_result = self._validate_health(point)

        # Combine results
        all_issues = contract_result.issues + health_result.issues

        result = ValidationResult(
            integration_point=point,
            timestamp=datetime.utcnow(),
            duration_ms=contract_result.duration_ms + health_result.duration_ms,
            issues=all_issues,
        )

        # Determine overall status
        critical_count = sum(1 for i in all_issues if i.severity == ValidationSeverity.CRITICAL)
        error_count = sum(1 for i in all_issues if i.severity == ValidationSeverity.ERROR)

        if critical_count > 0:
            result.status = IntegrationStatus.INVALID
            result.valid = False
        elif error_count > 0:
            result.status = IntegrationStatus.DEGRADED
            result.valid = False
        elif all_issues:
            result.status = IntegrationStatus.DEGRADED
            result.valid = True
        else:
            result.status = IntegrationStatus.VALID
            result.valid = True

        # Run custom validators
        for validator_name, validator in self._validators.items():
            try:
                custom_result = validator(point)
                result.issues.extend(custom_result.issues)
                result.duration_ms += custom_result.duration_ms
            except Exception as e:
                result.issues.append(ValidationIssue(
                    code="CUSTOM-ERR",
                    message=f"Custom validator '{validator_name}' failed: {e}",
                    severity=ValidationSeverity.WARNING,
                ))

        self._results_history.append(result)
        return result

    def validate_all(self) -> List[ValidationResult]:
        """Validate all integration points.

        Returns:
            List of ValidationResults
        """
        results = []

        # First validate dependency graph
        dep_result = self._validate_dependencies()
        results.append(dep_result)

        # Then validate each integration point
        for point_id in self._integration_points:
            result = self.validate(point_id)
            results.append(result)

        return results

    def get_dependency_graph(self) -> DependencyGraph:
        """Get the dependency graph.

        Returns:
            DependencyGraph
        """
        return self._dependency_graph

    def get_integration_points(self) -> List[IntegrationPoint]:
        """Get all integration points.

        Returns:
            List of IntegrationPoints
        """
        return list(self._integration_points.values())

    def summary(self) -> Dict[str, Any]:
        """Get validation summary.

        Returns:
            Summary dictionary
        """
        total_points = len(self._integration_points)
        total_components = len(self._components)

        # Count issues by severity from history
        severity_counts: Dict[str, int] = {}
        valid_count = 0

        for result in self._results_history:
            if result.valid:
                valid_count += 1
            for issue in result.issues:
                sev = issue.severity.value
                severity_counts[sev] = severity_counts.get(sev, 0) + 1

        return {
            "total_components": total_components,
            "total_integration_points": total_points,
            "total_validations": len(self._results_history),
            "valid_validations": valid_count,
            "issues_by_severity": severity_counts,
            "cycles_in_dependencies": len(self._dependency_graph.detect_cycles()),
        }
