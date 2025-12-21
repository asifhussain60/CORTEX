"""
Tests for Brain Template Loader (Option 1: Symlink-Based)
==========================================================

**Test Coverage:**
- Central location priority
- Fallback to per-repo templates
- All 4 template types (YAML + JSON)
- Backwards compatibility
- Error handling
"""

import pytest
from pathlib import Path
import tempfile
import shutil
import yaml
import json

from src.tier0.brain_template_loader import (
    BrainTemplateLoader,
    get_loader,
    load_capabilities,
    load_response_templates,
    load_brain_protection_rules,
    load_config_template
)


@pytest.fixture
def temp_central_dir():
    """Create temporary central template directory."""
    temp_dir = Path(tempfile.mkdtemp()) / ".cortex" / "brain-templates"
    temp_dir.mkdir(parents=True, exist_ok=True)
    yield temp_dir
    shutil.rmtree(temp_dir.parent.parent)


@pytest.fixture
def temp_fallback_dir():
    """Create temporary fallback template directory."""
    temp_dir = Path(tempfile.mkdtemp()) / "cortex-brain"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    (temp_dir / "metadata").mkdir(exist_ok=True)
    (temp_dir / "core").mkdir(exist_ok=True)
    
    yield temp_dir
    shutil.rmtree(temp_dir.parent)


@pytest.fixture
def sample_capabilities():
    """Sample capabilities data."""
    return {
        "version": "4.0",
        "capabilities": ["planning", "tdd", "documentation"]
    }


@pytest.fixture
def sample_response_templates():
    """Sample response templates data."""
    return {
        "version": "4.0",
        "templates": {
            "success": "Operation completed successfully",
            "error": "Operation failed"
        }
    }


@pytest.fixture
def sample_brain_protection():
    """Sample brain protection rules data."""
    return {
        "version": "1.0",
        "rules": ["TDD_ENFORCEMENT", "GIT_ISOLATION_ENFORCEMENT"]
    }


@pytest.fixture
def sample_config():
    """Sample config template data."""
    return {
        "version": "4.0",
        "machines": {},
        "defaultPaths": {}
    }


class TestBrainTemplateLoader:
    """Test BrainTemplateLoader class."""
    
    def test_initialization(self, temp_fallback_dir):
        """Test loader initialization."""
        loader = BrainTemplateLoader(fallback_dir=temp_fallback_dir)
        
        assert loader.central_dir == Path.home() / ".cortex" / "brain-templates"
        assert loader.fallback_dir == temp_fallback_dir
    
    def test_central_location_priority(
        self, 
        temp_central_dir, 
        temp_fallback_dir,
        sample_capabilities
    ):
        """Test that central location takes priority over fallback."""
        # Create same file in both locations with different content
        central_file = temp_central_dir / "capabilities.yaml"
        fallback_file = temp_fallback_dir / "metadata" / "capabilities.yaml"
        
        central_data = {"source": "central"}
        fallback_data = {"source": "fallback"}
        
        with open(central_file, 'w') as f:
            yaml.dump(central_data, f)
        
        with open(fallback_file, 'w') as f:
            yaml.dump(fallback_data, f)
        
        # Monkey patch central location
        loader = BrainTemplateLoader(fallback_dir=temp_fallback_dir)
        loader.central_dir = temp_central_dir
        
        # Should load from central
        data = loader.load_capabilities()
        assert data["source"] == "central"
    
    def test_fallback_when_central_missing(
        self,
        temp_fallback_dir,
        sample_capabilities
    ):
        """Test fallback to per-repo templates when central not available."""
        # Only create fallback file
        fallback_file = temp_fallback_dir / "metadata" / "capabilities.yaml"
        
        with open(fallback_file, 'w') as f:
            yaml.dump(sample_capabilities, f)
        
        # Use non-existent central dir
        loader = BrainTemplateLoader(fallback_dir=temp_fallback_dir)
        loader.central_dir = Path("/nonexistent/central")
        
        # Should load from fallback
        data = loader.load_capabilities()
        assert data["version"] == "4.0"
    
    def test_load_capabilities_yaml(
        self,
        temp_central_dir,
        temp_fallback_dir,
        sample_capabilities
    ):
        """Test loading capabilities.yaml."""
        central_file = temp_central_dir / "capabilities.yaml"
        with open(central_file, 'w') as f:
            yaml.dump(sample_capabilities, f)
        
        loader = BrainTemplateLoader(fallback_dir=temp_fallback_dir)
        loader.central_dir = temp_central_dir
        
        data = loader.load_capabilities()
        assert data["version"] == "4.0"
        assert "planning" in data["capabilities"]
    
    def test_load_response_templates_yaml(
        self,
        temp_central_dir,
        temp_fallback_dir,
        sample_response_templates
    ):
        """Test loading response-templates-v4.yaml."""
        central_file = temp_central_dir / "response-templates-v4.yaml"
        with open(central_file, 'w') as f:
            yaml.dump(sample_response_templates, f)
        
        loader = BrainTemplateLoader(fallback_dir=temp_fallback_dir)
        loader.central_dir = temp_central_dir
        
        data = loader.load_response_templates()
        assert data["version"] == "4.0"
        assert data["templates"]["success"] == "Operation completed successfully"
    
    def test_load_brain_protection_yaml(
        self,
        temp_central_dir,
        temp_fallback_dir,
        sample_brain_protection
    ):
        """Test loading brain-protection-rules.yaml."""
        central_file = temp_central_dir / "brain-protection-rules.yaml"
        with open(central_file, 'w') as f:
            yaml.dump(sample_brain_protection, f)
        
        loader = BrainTemplateLoader(fallback_dir=temp_fallback_dir)
        loader.central_dir = temp_central_dir
        
        data = loader.load_brain_protection_rules()
        assert "TDD_ENFORCEMENT" in data["rules"]
    
    def test_load_config_template_json(
        self,
        temp_central_dir,
        temp_fallback_dir,
        sample_config
    ):
        """Test loading cortex.config.template.json."""
        central_file = temp_central_dir / "cortex.config.template.json"
        with open(central_file, 'w') as f:
            json.dump(sample_config, f)
        
        loader = BrainTemplateLoader(fallback_dir=temp_fallback_dir)
        loader.central_dir = temp_central_dir
        
        data = loader.load_config_template()
        assert data["version"] == "4.0"
    
    def test_file_not_found_error(self, temp_fallback_dir):
        """Test error when template file not found."""
        loader = BrainTemplateLoader(fallback_dir=temp_fallback_dir)
        loader.central_dir = Path("/nonexistent/central")
        
        with pytest.raises(FileNotFoundError) as exc_info:
            loader.load_capabilities()
        
        assert "capabilities.yaml" in str(exc_info.value)
    
    def test_is_central_location_available(self, temp_central_dir):
        """Test checking central location availability."""
        loader = BrainTemplateLoader()
        loader.central_dir = temp_central_dir
        
        assert loader.is_central_location_available() is True
        
        loader.central_dir = Path("/nonexistent/path")
        assert loader.is_central_location_available() is False
    
    def test_get_template_source(
        self,
        temp_central_dir,
        temp_fallback_dir,
        sample_capabilities
    ):
        """Test identifying template source location."""
        # Create files in both locations
        central_file = temp_central_dir / "capabilities.yaml"
        fallback_file = temp_fallback_dir / "metadata" / "capabilities.yaml"
        
        with open(central_file, 'w') as f:
            yaml.dump(sample_capabilities, f)
        with open(fallback_file, 'w') as f:
            yaml.dump(sample_capabilities, f)
        
        loader = BrainTemplateLoader(fallback_dir=temp_fallback_dir)
        loader.central_dir = temp_central_dir
        
        # Should report central (priority)
        source = loader.get_template_source("capabilities.yaml")
        assert source == "central"
        
        # Remove central, should report fallback
        central_file.unlink()
        source = loader.get_template_source("capabilities.yaml")
        assert source == "fallback"


class TestConvenienceFunctions:
    """Test convenience functions for quick access."""
    
    def test_load_capabilities_convenience(
        self,
        temp_central_dir,
        sample_capabilities
    ):
        """Test load_capabilities() convenience function."""
        central_file = temp_central_dir / "capabilities.yaml"
        with open(central_file, 'w') as f:
            yaml.dump(sample_capabilities, f)
        
        # Monkey patch
        import src.tier0.brain_template_loader as module
        original_home = Path.home
        module.Path.home = lambda: temp_central_dir.parent.parent
        
        try:
            data = load_capabilities()
            assert data["version"] == "4.0"
        finally:
            module.Path.home = original_home
    
    def test_singleton_loader(self):
        """Test singleton pattern for loader instance."""
        loader1 = get_loader()
        loader2 = get_loader()
        
        assert loader1 is loader2


class TestBackwardsCompatibility:
    """Test backwards compatibility with per-repo templates."""
    
    def test_fallback_to_metadata_subdirectory(
        self,
        temp_fallback_dir,
        sample_capabilities
    ):
        """Test fallback to cortex-brain/metadata/ for capabilities."""
        metadata_file = temp_fallback_dir / "metadata" / "capabilities.yaml"
        with open(metadata_file, 'w') as f:
            yaml.dump(sample_capabilities, f)
        
        loader = BrainTemplateLoader(fallback_dir=temp_fallback_dir)
        loader.central_dir = Path("/nonexistent")
        
        data = loader.load_capabilities()
        assert data["version"] == "4.0"
    
    def test_fallback_to_core_subdirectory(
        self,
        temp_fallback_dir,
        sample_brain_protection
    ):
        """Test fallback to cortex-brain/core/ for brain protection."""
        core_file = temp_fallback_dir / "core" / "brain-protection-rules.yaml"
        with open(core_file, 'w') as f:
            yaml.dump(sample_brain_protection, f)
        
        loader = BrainTemplateLoader(fallback_dir=temp_fallback_dir)
        loader.central_dir = Path("/nonexistent")
        
        data = loader.load_brain_protection_rules()
        assert "TDD_ENFORCEMENT" in data["rules"]
    
    def test_per_repo_templates_still_work(
        self,
        temp_fallback_dir,
        sample_response_templates
    ):
        """Test that per-repo templates still work without central location."""
        # Create template directly in fallback root
        fallback_file = temp_fallback_dir / "response-templates-v4.yaml"
        with open(fallback_file, 'w') as f:
            yaml.dump(sample_response_templates, f)
        
        loader = BrainTemplateLoader(fallback_dir=temp_fallback_dir)
        loader.central_dir = Path("/nonexistent")
        
        data = loader.load_response_templates()
        assert data["version"] == "4.0"


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_invalid_yaml_handling(self, temp_central_dir, temp_fallback_dir):
        """Test handling of invalid YAML content."""
        central_file = temp_central_dir / "capabilities.yaml"
        with open(central_file, 'w') as f:
            f.write("invalid: yaml: content: [")
        
        loader = BrainTemplateLoader(fallback_dir=temp_fallback_dir)
        loader.central_dir = temp_central_dir
        
        with pytest.raises(Exception):
            loader.load_capabilities()
    
    def test_invalid_json_handling(self, temp_central_dir, temp_fallback_dir):
        """Test handling of invalid JSON content."""
        central_file = temp_central_dir / "cortex.config.template.json"
        with open(central_file, 'w') as f:
            f.write('{"invalid": json content}')
        
        loader = BrainTemplateLoader(fallback_dir=temp_fallback_dir)
        loader.central_dir = temp_central_dir
        
        with pytest.raises(Exception):
            loader.load_config_template()
    
    def test_empty_file_handling(
        self,
        temp_central_dir,
        temp_fallback_dir
    ):
        """Test handling of empty template files."""
        central_file = temp_central_dir / "capabilities.yaml"
        central_file.touch()  # Create empty file
        
        loader = BrainTemplateLoader(fallback_dir=temp_fallback_dir)
        loader.central_dir = temp_central_dir
        
        data = loader.load_capabilities()
        assert data == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
