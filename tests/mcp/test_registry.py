"""
Comprehensive tests for Orchestrator Registry.

Tests cover config loading, orchestrator discovery, validation,
and instantiation.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import yaml
import tempfile
from pathlib import Path
from src.mcp.registry import OrchestratorRegistry, OrchestratorDefinition


class TestOrchestratorDefinition:
    """Test OrchestratorDefinition dataclass."""
    
    def test_definition_creation(self):
        """Create orchestrator definition."""
        definition = OrchestratorDefinition(
            name="test_orch",
            class_name="TestOrchestrator",
            module_path="src.orchestrators.test",
            config_path="cortex-brain/manifests/test.yaml",
            type="autonomous"
        )
        assert definition.name == "test_orch"
        assert definition.class_name == "TestOrchestrator"
        assert definition.type == "autonomous"
    
    def test_validate_valid_definition(self, tmp_path):
        """Validate valid orchestrator definition."""
        # Create temp config file
        config_file = tmp_path / "test.yaml"
        config_file.write_text("test: config")
        
        definition = OrchestratorDefinition(
            name="test_orch",
            class_name="TestOrchestrator",
            module_path="src.test",
            config_path=str(config_file),
            type="autonomous"
        )
        
        is_valid, error = definition.validate()
        assert is_valid
        assert error is None
    
    def test_validate_invalid_type(self, tmp_path):
        """Validate with invalid type."""
        config_file = tmp_path / "test.yaml"
        config_file.write_text("test: config")
        
        definition = OrchestratorDefinition(
            name="test_orch",
            class_name="TestOrchestrator",
            module_path="src.test",
            config_path=str(config_file),
            type="invalid_type"
        )
        
        is_valid, error = definition.validate()
        assert not is_valid
        assert "Invalid type" in error
    
    def test_validate_missing_config(self):
        """Validate with missing config file."""
        definition = OrchestratorDefinition(
            name="test_orch",
            class_name="TestOrchestrator",
            module_path="src.test",
            config_path="/nonexistent/path/config.yaml",
            type="autonomous"
        )
        
        is_valid, error = definition.validate()
        assert not is_valid
        assert "Config file not found" in error


class TestOrchestratorRegistry:
    """Test OrchestratorRegistry."""
    
    @pytest.fixture
    def sample_config(self, tmp_path):
        """Create sample MCP server config."""
        # Create dummy manifest files
        manifest_dir = tmp_path / "manifests"
        manifest_dir.mkdir()
        
        planning_manifest = manifest_dir / "planning.yaml"
        planning_manifest.write_text("orchestrator: planning_system")
        
        ado_manifest = manifest_dir / "ado.yaml"
        ado_manifest.write_text("orchestrator: ado_operations")
        
        # Create config
        config = {
            "orchestrators": {
                "planning_system": {
                    "class": "PlanningOrchestratorV5",
                    "module": "src.orchestrators.planning_orchestrator_v5",
                    "config": str(planning_manifest),
                    "type": "autonomous",
                    "description": "Planning system"
                },
                "ado_operations": {
                    "class": "AdoOrchestratorV2",
                    "module": "src.orchestrators.ado_orchestrator_v2",
                    "config": str(ado_manifest),
                    "type": "autonomous",
                    "description": "ADO operations"
                }
            }
        }
        
        config_file = tmp_path / "mcp-server.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f)
        
        return config_file
    
    def test_registry_creation(self, sample_config):
        """Create registry from config."""
        registry = OrchestratorRegistry(str(sample_config))
        assert len(registry.orchestrators) == 2
        assert "planning_system" in registry.list_orchestrators()
        assert "ado_operations" in registry.list_orchestrators()
    
    def test_registry_nonexistent_config(self, tmp_path):
        """Create registry with nonexistent config."""
        config_path = tmp_path / "nonexistent.yaml"
        registry = OrchestratorRegistry(str(config_path))
        assert len(registry.orchestrators) == 0
    
    def test_get_orchestrator(self, sample_config):
        """Get orchestrator definition."""
        registry = OrchestratorRegistry(str(sample_config))
        
        definition = registry.get("planning_system")
        assert definition is not None
        assert definition.name == "planning_system"
        assert definition.type == "autonomous"
    
    def test_get_nonexistent_orchestrator(self, sample_config):
        """Get orchestrator that doesn't exist."""
        registry = OrchestratorRegistry(str(sample_config))
        
        definition = registry.get("nonexistent")
        assert definition is None
    
    def test_exists(self, sample_config):
        """Check if orchestrator exists."""
        registry = OrchestratorRegistry(str(sample_config))
        
        assert registry.exists("planning_system")
        assert registry.exists("ado_operations")
        assert not registry.exists("nonexistent")
    
    def test_list_by_type(self, sample_config):
        """List orchestrators by type."""
        registry = OrchestratorRegistry(str(sample_config))
        
        autonomous = registry.list_by_type("autonomous")
        assert len(autonomous) == 2
        assert "planning_system" in autonomous
        assert "ado_operations" in autonomous
        
        guided = registry.list_by_type("guided")
        assert len(guided) == 0
    
    def test_get_statistics(self, sample_config):
        """Get registry statistics."""
        registry = OrchestratorRegistry(str(sample_config))
        
        stats = registry.get_statistics()
        assert stats["total"] == 2
        assert stats["autonomous"] == 2
        assert stats["guided"] == 0
    
    def test_validate_all(self, sample_config):
        """Validate all orchestrators."""
        registry = OrchestratorRegistry(str(sample_config))
        
        results = registry.validate_all()
        assert len(results) == 2
        
        for name, (is_valid, error) in results.items():
            assert is_valid
            assert error is None
    
    def test_reload(self, sample_config, tmp_path):
        """Reload registry configuration."""
        registry = OrchestratorRegistry(str(sample_config))
        assert len(registry.orchestrators) == 2
        
        # Modify config (add new orchestrator)
        manifest_file = tmp_path / "vacuum.yaml"
        manifest_file.write_text("orchestrator: vacuum")
        
        config = {
            "orchestrators": {
                "planning_system": {
                    "class": "PlanningOrchestratorV5",
                    "module": "src.orchestrators.planning_orchestrator_v5",
                    "config": str(tmp_path / "manifests" / "planning.yaml"),
                    "type": "autonomous"
                },
                "vacuum": {
                    "class": "VacuumOrchestratorV2",
                    "module": "src.orchestrators.vacuum_orchestrator_v2",
                    "config": str(manifest_file),
                    "type": "autonomous"
                }
            }
        }
        
        with open(sample_config, 'w') as f:
            yaml.dump(config, f)
        
        # Reload
        registry.reload()
        
        assert len(registry.orchestrators) == 2
        assert registry.exists("vacuum")
        assert not registry.exists("ado_operations")
    
    def test_invalid_orchestrator_definition(self, tmp_path):
        """Handle invalid orchestrator definition."""
        # Create config with missing required field
        config = {
            "orchestrators": {
                "invalid_orch": {
                    "class": "InvalidOrch",
                    # Missing 'module' field
                    "config": "test.yaml",
                    "type": "autonomous"
                }
            }
        }
        
        config_file = tmp_path / "invalid-config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f)
        
        # Should not crash, just skip invalid orchestrator
        registry = OrchestratorRegistry(str(config_file))
        assert len(registry.orchestrators) == 0
