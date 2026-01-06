"""
Unit tests for OrchestratorRegistry.

Tests registration, discovery, persistence, and health checks.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import json
import tempfile
from pathlib import Path

from src.mcp.registry import OrchestratorRegistry
from src.mcp.metadata import (
    OrchestratorMetadata,
    OrchestratorType,
    OrchestratorCategory
)


class TestOrchestratorRegistry:
    """Test suite for OrchestratorRegistry."""
    
    @pytest.fixture
    def registry(self):
        """Create fresh registry for each test."""
        return OrchestratorRegistry()
    
    @pytest.fixture
    def temp_registry_file(self):
        """Create temporary registry file."""
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.json',
            delete=False
        ) as f:
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        Path(temp_path).unlink(missing_ok=True)
    
    def test_registry_initialization(self, registry):
        """Test registry initialization."""
        assert registry is not None
        assert len(registry.list_all(enabled_only=False)) == 0
    
    def test_register_orchestrator(self, registry):
        """Test basic orchestrator registration."""
        registry.register(
            id="test_orch",
            name="Test Orchestrator",
            version="1.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.TESTING,
            class_name="TestOrchestrator",
            module_path="test.module"
        )
        
        metadata = registry.get("test_orch")
        assert metadata is not None
        assert metadata.id == "test_orch"
        assert metadata.name == "Test Orchestrator"
        assert metadata.version == "1.0.0"
    
    def test_register_duplicate_fails(self, registry):
        """Test that duplicate registration fails."""
        registry.register(
            id="test_orch",
            name="Test",
            version="1.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.TESTING,
            class_name="Test",
            module_path="test"
        )
        
        with pytest.raises(ValueError, match="already registered"):
            registry.register(
                id="test_orch",
                name="Test2",
                version="2.0.0",
                type=OrchestratorType.AUTONOMOUS,
                category=OrchestratorCategory.TESTING,
                class_name="Test2",
                module_path="test2"
            )
    
    def test_register_with_overwrite(self, registry):
        """Test registration with overwrite flag."""
        registry.register(
            id="test_orch",
            name="Test v1",
            version="1.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.TESTING,
            class_name="Test",
            module_path="test"
        )
        
        # Overwrite with new version
        registry.register(
            id="test_orch",
            name="Test v2",
            version="2.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.TESTING,
            class_name="Test",
            module_path="test",
            overwrite=True
        )
        
        metadata = registry.get("test_orch")
        assert metadata.name == "Test v2"
        assert metadata.version == "2.0.0"
    
    def test_unregister_orchestrator(self, registry):
        """Test orchestrator unregistration."""
        registry.register(
            id="test_orch",
            name="Test",
            version="1.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.TESTING,
            class_name="Test",
            module_path="test"
        )
        
        assert registry.get("test_orch") is not None
        
        registry.unregister("test_orch")
        
        assert registry.get("test_orch") is None
    
    def test_unregister_nonexistent_fails(self, registry):
        """Test that unregistering nonexistent orchestrator fails."""
        with pytest.raises(KeyError, match="not found"):
            registry.unregister("nonexistent")
    
    def test_get_orchestrator(self, registry):
        """Test retrieving orchestrator metadata."""
        registry.register(
            id="test_orch",
            name="Test",
            version="1.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.TESTING,
            class_name="Test",
            module_path="test"
        )
        
        metadata = registry.get("test_orch")
        assert metadata is not None
        assert metadata.id == "test_orch"
        
        # Non-existent
        assert registry.get("nonexistent") is None
    
    def test_list_all_orchestrators(self, registry):
        """Test listing all orchestrators."""
        # Register multiple orchestrators
        registry.register(
            id="orch1",
            name="Orch1",
            version="1.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.PLANNING,
            class_name="Orch1",
            module_path="orch1"
        )
        
        registry.register(
            id="orch2",
            name="Orch2",
            version="2.0.0",
            type=OrchestratorType.GUIDED,
            category=OrchestratorCategory.EXECUTION,
            class_name="Orch2",
            module_path="orch2"
        )
        
        registry.register(
            id="orch3",
            name="Orch3",
            version="3.0.0",
            type=OrchestratorType.INTERACTIVE,
            category=OrchestratorCategory.TESTING,
            class_name="Orch3",
            module_path="orch3",
            enabled=False
        )
        
        # List all (enabled only)
        all_enabled = registry.list_all(enabled_only=True)
        assert len(all_enabled) == 2
        
        # List all (including disabled)
        all_orchestrators = registry.list_all(enabled_only=False)
        assert len(all_orchestrators) == 3
    
    def test_list_by_category(self, registry):
        """Test listing orchestrators by category."""
        registry.register(
            id="planning1",
            name="Planning1",
            version="1.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.PLANNING,
            class_name="Planning1",
            module_path="planning1"
        )
        
        registry.register(
            id="planning2",
            name="Planning2",
            version="2.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.PLANNING,
            class_name="Planning2",
            module_path="planning2"
        )
        
        registry.register(
            id="testing1",
            name="Testing1",
            version="1.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.TESTING,
            class_name="Testing1",
            module_path="testing1"
        )
        
        planning_orchs = registry.list_all(
            category=OrchestratorCategory.PLANNING
        )
        assert len(planning_orchs) == 2
        assert all(o.category == OrchestratorCategory.PLANNING for o in planning_orchs)
    
    def test_list_by_type(self, registry):
        """Test listing orchestrators by type."""
        registry.register(
            id="auto1",
            name="Auto1",
            version="1.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.PLANNING,
            class_name="Auto1",
            module_path="auto1"
        )
        
        registry.register(
            id="guided1",
            name="Guided1",
            version="1.0.0",
            type=OrchestratorType.GUIDED,
            category=OrchestratorCategory.PLANNING,
            class_name="Guided1",
            module_path="guided1"
        )
        
        autonomous_orchs = registry.list_all(
            type=OrchestratorType.AUTONOMOUS
        )
        assert len(autonomous_orchs) == 1
        assert autonomous_orchs[0].type == OrchestratorType.AUTONOMOUS
    
    def test_find_by_pattern(self, registry):
        """Test pattern-based orchestrator discovery."""
        registry.register(
            id="planning_v5",
            name="Planning v5",
            version="5.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.PLANNING,
            class_name="PlanningV5",
            module_path="planning",
            patterns=[r"^(plan|create a plan).*$"]
        )
        
        registry.register(
            id="testing_v1",
            name="Testing v1",
            version="1.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.TESTING,
            class_name="TestingV1",
            module_path="testing",
            patterns=[r"^(test|run tests).*$"]
        )
        
        # Should match planning
        matches = registry.find_by_pattern("plan authentication")
        assert len(matches) == 1
        assert matches[0].id == "planning_v5"
        
        # Should match testing
        matches = registry.find_by_pattern("test my code")
        assert len(matches) == 1
        assert matches[0].id == "testing_v1"
        
        # Should match nothing
        matches = registry.find_by_pattern("deploy application")
        assert len(matches) == 0
    
    def test_resolve_dependencies_linear(self, registry):
        """Test dependency resolution (linear chain)."""
        registry.register(
            id="base",
            name="Base",
            version="1.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.PLANNING,
            class_name="Base",
            module_path="base"
        )
        
        registry.register(
            id="middle",
            name="Middle",
            version="1.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.EXECUTION,
            class_name="Middle",
            module_path="middle",
            dependencies=["base"]
        )
        
        registry.register(
            id="top",
            name="Top",
            version="1.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.VALIDATION,
            class_name="Top",
            module_path="top",
            dependencies=["middle"]
        )
        
        resolved = registry.resolve_dependencies("top")
        assert resolved == ["base", "middle", "top"]
    
    def test_resolve_dependencies_diamond(self, registry):
        """Test dependency resolution (diamond pattern)."""
        registry.register(id="a", name="A", version="1.0.0",
                         type=OrchestratorType.AUTONOMOUS,
                         category=OrchestratorCategory.PLANNING,
                         class_name="A", module_path="a")
        
        registry.register(id="b", name="B", version="1.0.0",
                         type=OrchestratorType.AUTONOMOUS,
                         category=OrchestratorCategory.EXECUTION,
                         class_name="B", module_path="b",
                         dependencies=["a"])
        
        registry.register(id="c", name="C", version="1.0.0",
                         type=OrchestratorType.AUTONOMOUS,
                         category=OrchestratorCategory.EXECUTION,
                         class_name="C", module_path="c",
                         dependencies=["a"])
        
        registry.register(id="d", name="D", version="1.0.0",
                         type=OrchestratorType.AUTONOMOUS,
                         category=OrchestratorCategory.VALIDATION,
                         class_name="D", module_path="d",
                         dependencies=["b", "c"])
        
        resolved = registry.resolve_dependencies("d")
        # Should contain all dependencies
        assert "a" in resolved
        assert "b" in resolved
        assert "c" in resolved
        assert "d" in resolved
        # a should come before b and c
        assert resolved.index("a") < resolved.index("b")
        assert resolved.index("a") < resolved.index("c")
    
    def test_resolve_circular_dependency_fails(self, registry):
        """Test that circular dependencies are detected."""
        registry.register(id="a", name="A", version="1.0.0",
                         type=OrchestratorType.AUTONOMOUS,
                         category=OrchestratorCategory.PLANNING,
                         class_name="A", module_path="a",
                         dependencies=["b"])
        
        registry.register(id="b", name="B", version="1.0.0",
                         type=OrchestratorType.AUTONOMOUS,
                         category=OrchestratorCategory.EXECUTION,
                         class_name="B", module_path="b",
                         dependencies=["a"])
        
        with pytest.raises(ValueError, match="Circular dependency"):
            registry.resolve_dependencies("a")
    
    def test_persistence_save_and_load(self, temp_registry_file):
        """Test registry persistence to disk."""
        # Create registry with persistence
        registry = OrchestratorRegistry(registry_path=temp_registry_file)
        
        # Register orchestrators
        registry.register(
            id="orch1",
            name="Orch1",
            version="1.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.PLANNING,
            class_name="Orch1",
            module_path="orch1"
        )
        
        # Create new registry instance (should load from disk)
        registry2 = OrchestratorRegistry(registry_path=temp_registry_file)
        
        metadata = registry2.get("orch1")
        assert metadata is not None
        assert metadata.id == "orch1"
        assert metadata.name == "Orch1"
    
    def test_export_to_yaml(self, registry, tmp_path):
        """Test exporting registry to YAML."""
        registry.register(
            id="test_orch",
            name="Test",
            version="1.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.TESTING,
            class_name="Test",
            module_path="test"
        )
        
        yaml_path = tmp_path / "registry.yaml"
        registry.export_to_yaml(str(yaml_path))
        
        assert yaml_path.exists()
        
        import yaml
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        
        assert 'test_orch' in data
        assert data['test_orch']['name'] == 'Test'
    
    def test_health_check_healthy(self, registry):
        """Test health check with valid orchestrators."""
        # Register real orchestrator that exists
        registry.register(
            id="planning_v5",
            name="Planning v5",
            version="5.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.PLANNING,
            class_name="PlanningOrchestratorV5",
            module_path="src.orchestrators.planning.planning_orchestrator_v5"
        )
        
        health = registry.health_check()
        
        assert health['total'] == 1
        assert health['enabled'] == 1
        assert 'planning_v5' in health['orchestrators']
        assert health['orchestrators']['planning_v5']['status'] == 'healthy'
    
    def test_health_check_invalid_module(self, registry):
        """Test health check with invalid module."""
        registry.register(
            id="invalid",
            name="Invalid",
            version="1.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.TESTING,
            class_name="InvalidClass",
            module_path="nonexistent.module"
        )
        
        health = registry.health_check()
        
        assert health['total'] == 1
        assert 'invalid' in health['orchestrators']
        assert health['orchestrators']['invalid']['status'] == 'error'
        assert 'Import error' in health['orchestrators']['invalid']['error']
