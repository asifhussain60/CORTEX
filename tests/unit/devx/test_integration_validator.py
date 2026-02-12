"""
Tests for ODX-002-01: Integration Validator

AC-ID: ODX-002-01
Phase: PHASE-18-ORCHESTRATOR-DEVX
"""

import pytest
from datetime import datetime
from typing import Optional

from cortex.devx.integration_validator import (
    IntegrationValidator,
    IntegrationPoint,
    ValidationResult,
    ValidationIssue,
    ValidationSeverity,
    IntegrationStatus,
    DependencyGraph,
)


class TestValidationIssue:
    """Tests for ValidationIssue dataclass."""
    
    def test_issue_creation(self):
        """Test ValidationIssue creation."""
        issue = ValidationIssue(
            code="INT-001",
            message="Test issue",
            severity=ValidationSeverity.ERROR,
            source="SourceComp",
            target="TargetComp",
        )
        
        assert issue.code == "INT-001"
        assert issue.message == "Test issue"
        assert issue.severity == ValidationSeverity.ERROR
    
    def test_issue_with_suggestion(self):
        """Test ValidationIssue with suggestion."""
        issue = ValidationIssue(
            code="INT-002",
            message="Missing method",
            severity=ValidationSeverity.WARNING,
            suggestion="Add the required method",
        )
        
        assert issue.suggestion == "Add the required method"
    
    def test_issue_to_dict(self):
        """Test ValidationIssue serialization."""
        issue = ValidationIssue(
            code="INT-001",
            message="Test",
            severity=ValidationSeverity.CRITICAL,
        )
        
        d = issue.to_dict()
        
        assert d["code"] == "INT-001"
        assert d["severity"] == "critical"


class TestIntegrationPoint:
    """Tests for IntegrationPoint dataclass."""
    
    def test_point_creation(self):
        """Test IntegrationPoint creation."""
        point = IntegrationPoint(
            point_id="master-intent",
            name="Master to Intent Router",
            source="MasterOrchestrator",
            target="IntentRouter",
        )
        
        assert point.point_id == "master-intent"
        assert point.source == "MasterOrchestrator"
        assert point.required
    
    def test_point_with_contract(self):
        """Test IntegrationPoint with contract."""
        point = IntegrationPoint(
            point_id="test",
            name="Test Point",
            source="A",
            target="B",
            contract={"method": "process", "params": ["input"]},
        )
        
        assert point.contract["method"] == "process"
        assert "input" in point.contract["params"]
    
    def test_point_to_dict(self):
        """Test IntegrationPoint serialization."""
        point = IntegrationPoint(
            point_id="test",
            name="Test",
            source="A",
            target="B",
            required=False,
        )
        
        d = point.to_dict()
        
        assert d["point_id"] == "test"
        assert d["required"] == False


class TestValidationResult:
    """Tests for ValidationResult dataclass."""
    
    def test_result_creation(self):
        """Test ValidationResult creation."""
        result = ValidationResult(
            valid=True,
            status=IntegrationStatus.VALID,
        )
        
        assert result.valid
        assert result.status == IntegrationStatus.VALID
        assert result.timestamp is not None
    
    def test_result_with_issues(self):
        """Test ValidationResult with issues."""
        issues = [
            ValidationIssue(code="I1", message="Issue 1", severity=ValidationSeverity.WARNING),
            ValidationIssue(code="I2", message="Issue 2", severity=ValidationSeverity.ERROR),
        ]
        
        result = ValidationResult(
            valid=False,
            issues=issues,
            duration_ms=50.5,
        )
        
        assert len(result.issues) == 2
        assert result.duration_ms == 50.5
    
    def test_result_to_dict(self):
        """Test ValidationResult serialization."""
        result = ValidationResult(
            valid=True,
            status=IntegrationStatus.VALID,
            metadata={"key": "value"},
        )
        
        d = result.to_dict()
        
        assert d["valid"]
        assert d["status"] == "valid"
        assert d["metadata"]["key"] == "value"


class TestDependencyGraph:
    """Tests for DependencyGraph."""
    
    def test_graph_creation(self):
        """Test DependencyGraph creation."""
        graph = DependencyGraph()
        
        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0
    
    def test_add_node(self):
        """Test adding nodes to graph."""
        graph = DependencyGraph()
        
        graph.add_node("A", {"type": "orchestrator"})
        graph.add_node("B")
        
        assert "A" in graph.nodes
        assert "B" in graph.nodes
        assert graph.metadata["A"]["type"] == "orchestrator"
    
    def test_add_edge(self):
        """Test adding edges to graph."""
        graph = DependencyGraph()
        
        graph.add_edge("A", "B")
        graph.add_edge("A", "C")
        
        assert "B" in graph.edges["A"]
        assert "C" in graph.edges["A"]
        # Nodes should be automatically added
        assert "A" in graph.nodes
        assert "B" in graph.nodes
    
    def test_get_dependencies(self):
        """Test getting direct dependencies."""
        graph = DependencyGraph()
        
        graph.add_edge("A", "B")
        graph.add_edge("A", "C")
        graph.add_edge("B", "D")
        
        deps = graph.get_dependencies("A")
        
        assert "B" in deps
        assert "C" in deps
        assert "D" not in deps  # Not direct
    
    def test_get_all_dependencies(self):
        """Test getting all transitive dependencies."""
        graph = DependencyGraph()
        
        graph.add_edge("A", "B")
        graph.add_edge("B", "C")
        graph.add_edge("C", "D")
        
        all_deps = graph.get_all_dependencies("A")
        
        assert "B" in all_deps
        assert "C" in all_deps
        assert "D" in all_deps
    
    def test_detect_no_cycles(self):
        """Test cycle detection with no cycles."""
        graph = DependencyGraph()
        
        graph.add_edge("A", "B")
        graph.add_edge("B", "C")
        
        cycles = graph.detect_cycles()
        
        assert len(cycles) == 0
    
    def test_detect_simple_cycle(self):
        """Test detection of simple cycle."""
        graph = DependencyGraph()
        
        graph.add_edge("A", "B")
        graph.add_edge("B", "C")
        graph.add_edge("C", "A")  # Cycle back
        
        cycles = graph.detect_cycles()
        
        assert len(cycles) >= 1
    
    def test_detect_self_cycle(self):
        """Test detection of self-referential cycle."""
        graph = DependencyGraph()
        
        graph.add_edge("A", "A")  # Self-cycle
        
        cycles = graph.detect_cycles()
        
        assert len(cycles) >= 1


class TestIntegrationValidator:
    """Tests for IntegrationValidator."""
    
    def test_validator_creation(self):
        """Test IntegrationValidator creation."""
        validator = IntegrationValidator()
        
        assert len(validator._components) == 0
        assert len(validator._integration_points) == 0
    
    def test_add_integration_point(self):
        """Test adding an integration point."""
        validator = IntegrationValidator()
        
        point = IntegrationPoint(
            point_id="test",
            name="Test Point",
            source="A",
            target="B",
        )
        
        result = validator.add_integration_point(point)
        
        assert result is validator  # Method chaining
        assert "test" in validator._integration_points
        # Should also add to dependency graph
        assert "A" in validator._dependency_graph.nodes
        assert "B" in validator._dependency_graph.nodes
    
    def test_validate_missing_integration_point(self):
        """Test validating non-existent integration point."""
        validator = IntegrationValidator()
        
        result = validator.validate("nonexistent")
        
        assert not result.valid
        assert result.status == IntegrationStatus.INVALID
        assert any(i.code == "INT-000" for i in result.issues)
    
    def test_validate_missing_source(self):
        """Test validation when source component is missing."""
        validator = IntegrationValidator()
        
        # Only register target
        class TargetComponent:
            def process(self):
                pass
        
        validator.register("Target", TargetComponent)
        
        point = IntegrationPoint(
            point_id="test",
            name="Test",
            source="Source",  # Not registered
            target="Target",
            contract={"method": "process"},
        )
        validator.add_integration_point(point)
        
        result = validator.validate("test")
        
        assert not result.valid
        assert any(i.code == "INT-001" for i in result.issues)
    
    def test_get_dependency_graph(self):
        """Test getting the dependency graph."""
        validator = IntegrationValidator()
        
        validator.add_integration_point(IntegrationPoint(
            point_id="test",
            source="A",
            target="B",
            name="Test",
        ))
        
        graph = validator.get_dependency_graph()
        
        assert "A" in graph.nodes
        assert "B" in graph.nodes
        assert "B" in graph.edges.get("A", set())
    
    def test_get_integration_points(self):
        """Test getting all integration points."""
        validator = IntegrationValidator()
        
        validator.add_integration_point(IntegrationPoint(point_id="p1", source="A", target="B", name="P1"))
        validator.add_integration_point(IntegrationPoint(point_id="p2", source="B", target="C", name="P2"))
        
        points = validator.get_integration_points()
        
        assert len(points) == 2
    
