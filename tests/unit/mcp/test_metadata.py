"""
Unit tests for OrchestratorMetadata.

Tests metadata structure, validation, and pattern matching.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from src.mcp.metadata import (
    OrchestratorMetadata,
    OrchestratorType,
    OrchestratorCategory
)


class TestOrchestratorMetadata:
    """Test suite for OrchestratorMetadata."""
    
    def test_metadata_creation(self):
        """Test basic metadata creation."""
        metadata = OrchestratorMetadata(
            id="test_orchestrator",
            name="Test Orchestrator",
            version="1.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.PLANNING,
            class_name="TestOrchestrator",
            module_path="test.module",
            description="Test description"
        )
        
        assert metadata.id == "test_orchestrator"
        assert metadata.name == "Test Orchestrator"
        assert metadata.version == "1.0.0"
        assert metadata.type == OrchestratorType.AUTONOMOUS
        assert metadata.category == OrchestratorCategory.PLANNING
        assert metadata.enabled is True
    
    def test_metadata_with_patterns(self):
        """Test metadata with pattern matching."""
        metadata = OrchestratorMetadata(
            id="planning_v5",
            name="Planning v5",
            version="5.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.PLANNING,
            class_name="PlanningOrchestratorV5",
            module_path="src.orchestrators.planning",
            patterns=[r"^(plan|create a plan).*$", r"^make a plan.*$"]
        )
        
        assert len(metadata.patterns) == 2
        assert metadata.matches_pattern("plan authentication")
        assert metadata.matches_pattern("create a plan for testing")
        assert metadata.matches_pattern("make a plan")
        assert not metadata.matches_pattern("test something")
    
    def test_metadata_with_dependencies(self):
        """Test metadata with dependencies."""
        metadata = OrchestratorMetadata(
            id="execution_v1",
            name="Execution v1",
            version="1.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.EXECUTION,
            class_name="ExecutionOrchestrator",
            module_path="src.orchestrators.execution",
            dependencies=["planning_v5", "validation_v1"]
        )
        
        assert len(metadata.dependencies) == 2
        assert "planning_v5" in metadata.dependencies
        assert "validation_v1" in metadata.dependencies
    
    def test_metadata_with_capabilities(self):
        """Test metadata with capabilities."""
        metadata = OrchestratorMetadata(
            id="test_orch",
            name="Test",
            version="1.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.TESTING,
            class_name="TestOrch",
            module_path="test.module",
            capabilities=["unit_testing", "integration_testing", "e2e_testing"]
        )
        
        assert len(metadata.capabilities) == 3
        assert "unit_testing" in metadata.capabilities
    
    def test_metadata_to_dict(self):
        """Test metadata serialization to dict."""
        metadata = OrchestratorMetadata(
            id="test_id",
            name="Test Name",
            version="1.0.0",
            type=OrchestratorType.GUIDED,
            category=OrchestratorCategory.MAINTENANCE,
            class_name="TestClass",
            module_path="test.module",
            description="Test desc",
            patterns=["test.*"],
            tags={"key": "value"}
        )
        
        data = metadata.to_dict()
        
        assert data['id'] == "test_id"
        assert data['name'] == "Test Name"
        assert data['version'] == "1.0.0"
        assert data['type'] == "guided"
        assert data['category'] == "maintenance"
        assert data['class_name'] == "TestClass"
        assert data['module_path'] == "test.module"
        assert data['description'] == "Test desc"
        assert data['patterns'] == ["test.*"]
        assert data['tags'] == {"key": "value"}
        assert data['enabled'] is True
    
    def test_metadata_from_dict(self):
        """Test metadata deserialization from dict."""
        data = {
            'id': 'test_id',
            'name': 'Test Name',
            'version': '2.0.0',
            'type': 'interactive',
            'category': 'optimization',
            'class_name': 'TestClass',
            'module_path': 'test.module',
            'description': 'Test description',
            'patterns': ['test.*', 'optimize.*'],
            'dependencies': ['dep1', 'dep2'],
            'capabilities': ['cap1', 'cap2'],
            'tags': {'env': 'test'},
            'enabled': False
        }
        
        metadata = OrchestratorMetadata.from_dict(data)
        
        assert metadata.id == 'test_id'
        assert metadata.name == 'Test Name'
        assert metadata.version == '2.0.0'
        assert metadata.type == OrchestratorType.INTERACTIVE
        assert metadata.category == OrchestratorCategory.OPTIMIZATION
        assert len(metadata.patterns) == 2
        assert len(metadata.dependencies) == 2
        assert len(metadata.capabilities) == 2
        assert metadata.enabled is False
    
    def test_metadata_pattern_matching(self):
        """Test pattern matching functionality."""
        metadata = OrchestratorMetadata(
            id="test",
            name="Test",
            version="1.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.TESTING,
            class_name="Test",
            module_path="test",
            patterns=[
                r"^test\s+.*$",
                r"^run\s+tests.*$",
                r".*\btesting\b.*"
            ]
        )
        
        # Should match
        assert metadata.matches_pattern("test authentication")
        assert metadata.matches_pattern("run tests for module")
        assert metadata.matches_pattern("start testing now")
        
        # Should not match
        assert not metadata.matches_pattern("plan something")
        assert not metadata.matches_pattern("execute task")
    
    def test_metadata_enabled_flag(self):
        """Test enabled/disabled flag."""
        # Default enabled
        metadata1 = OrchestratorMetadata(
            id="test1",
            name="Test1",
            version="1.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.TESTING,
            class_name="Test1",
            module_path="test1"
        )
        assert metadata1.enabled is True
        
        # Explicitly disabled
        metadata2 = OrchestratorMetadata(
            id="test2",
            name="Test2",
            version="1.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.TESTING,
            class_name="Test2",
            module_path="test2",
            enabled=False
        )
        assert metadata2.enabled is False


class TestOrchestratorType:
    """Test suite for OrchestratorType enum."""
    
    def test_orchestrator_types(self):
        """Test orchestrator type enum values."""
        assert OrchestratorType.AUTONOMOUS.value == "autonomous"
        assert OrchestratorType.GUIDED.value == "guided"
        assert OrchestratorType.INTERACTIVE.value == "interactive"
    
    def test_type_from_string(self):
        """Test creating type from string."""
        type1 = OrchestratorType("autonomous")
        assert type1 == OrchestratorType.AUTONOMOUS
        
        type2 = OrchestratorType("guided")
        assert type2 == OrchestratorType.GUIDED


class TestOrchestratorCategory:
    """Test suite for OrchestratorCategory enum."""
    
    def test_orchestrator_categories(self):
        """Test orchestrator category enum values."""
        assert OrchestratorCategory.PLANNING.value == "planning"
        assert OrchestratorCategory.EXECUTION.value == "execution"
        assert OrchestratorCategory.TESTING.value == "testing"
        assert OrchestratorCategory.MAINTENANCE.value == "maintenance"
    
    def test_category_from_string(self):
        """Test creating category from string."""
        cat1 = OrchestratorCategory("planning")
        assert cat1 == OrchestratorCategory.PLANNING
        
        cat2 = OrchestratorCategory("testing")
        assert cat2 == OrchestratorCategory.TESTING
